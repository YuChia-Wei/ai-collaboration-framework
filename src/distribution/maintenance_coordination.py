"""Participating maintenance writers only; caller quiescence is an assertion."""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import stat

from . import installation_state as state
from .installation_io import IO


def declaration(value: dict, scope: list[str]) -> dict:
    state._shape(value, {"declared_by", "declaration_reference", "affected_capabilities",
                         "sessions_stopped", "tools_stopped", "external_writers_stopped"})
    state._text(value["declared_by"])
    state._text(value["declaration_reference"])
    capabilities = state._array(value["affected_capabilities"], state.LIMITS["components"] * 2)
    for name in capabilities:
        state._id(name)
    state._check(capabilities == scope, "maintenance-scope", "Fresh declaration must name the exact sorted affected capability union.")
    state._check(all(value[key] is True for key in ("sessions_stopped", "tools_stopped", "external_writers_stopped")),
                 "maintenance-declaration", "Caller must explicitly declare affected sessions, tools and external writers stopped.")
    return value


class WriterLock:
    """Nonblocking OS-held exclusion; never unlink, replace or truncate the guard."""

    def __init__(self, io: IO, project: Path, *, allow_create: bool):
        self.io, self.project, self.allow_create = io, project, allow_create
        self.descriptor = None
        self.held = False
        self.created = False

    def __enter__(self):
        target = self.io.locate(self.project, state.GUARD_PATH)
        if target is None:
            state._check(self.allow_create, "missing-guard", "This operation cannot create missing writer coordination.", state.GUARD_PATH)
            self.io.create(self.project, state.GUARD_PATH, b"", "project")
            self.created = True
            target = self.project / state.GUARD_PATH
        before = target.lstat()
        state._plain(before, state.GUARD_PATH)
        state._check(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size == 0,
                     "guard-conflict", "Coordination must be the reserved empty direct file.", state.GUARD_PATH, "conflict")
        self.descriptor = os.open(target, os.O_RDWR | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0))
        try:
            opened = os.fstat(self.descriptor)
            state._check((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                         "guard-drift", "Guard changed while opening.", state.GUARD_PATH, "conflict")
            if self.io.backend.windows:
                from ctypes import wintypes as w
                import msvcrt

                class Overlapped(ctypes.Structure):
                    _fields_ = [("Internal", ctypes.c_size_t), ("InternalHigh", ctypes.c_size_t),
                                ("Offset", w.DWORD), ("OffsetHigh", w.DWORD), ("hEvent", w.HANDLE)]

                self.overlapped = Overlapped()
                self.handle = w.HANDLE(msvcrt.get_osfhandle(self.descriptor))
                native = self.io.backend.native
                native.LockFileEx.argtypes = [w.HANDLE, w.DWORD, w.DWORD, w.DWORD, w.DWORD, ctypes.POINTER(Overlapped)]
                native.LockFileEx.restype = w.BOOL
                native.UnlockFileEx.argtypes = [w.HANDLE, w.DWORD, w.DWORD, w.DWORD, ctypes.POINTER(Overlapped)]
                native.UnlockFileEx.restype = w.BOOL
                state._check(bool(native.LockFileEx(self.handle, 3, 0, 1, 0, ctypes.byref(self.overlapped))),
                             "writer-lock-unavailable", "Native exclusive writer lock is held or inaccessible.", state.GUARD_PATH)
            else:
                import fcntl
                try:
                    fcntl.flock(self.descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    raise state.InstallationError("writer-lock-unavailable", "Native exclusive writer lock is held or inaccessible.", state.GUARD_PATH) from None
            self.held = True
            self.verify()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def verify(self) -> None:
        state._check(self.held and self.descriptor is not None, "writer-lock-required", "An acquired native writer handle is required.")
        target = self.io.locate(self.project, state.GUARD_PATH)
        state._check(target is not None, "guard-drift", "Held guard pathname disappeared.", state.GUARD_PATH)
        opened, current = os.fstat(self.descriptor), target.lstat()
        state._plain(current, state.GUARD_PATH)
        state._check((opened.st_dev, opened.st_ino) == (current.st_dev, current.st_ino)
                     and current.st_nlink == 1 and current.st_size == 0 and stat.S_ISREG(current.st_mode),
                     "guard-drift", "Held guard was altered/replaced; external concurrent writers are unsupported.", state.GUARD_PATH, "conflict")

    def __exit__(self, exc_type, exc, traceback):
        try:
            if self.held:
                if self.io.backend.windows:
                    if not self.io.backend.native.UnlockFileEx(self.handle, 0, 1, 0, ctypes.byref(self.overlapped)):
                        raise state.InstallationError("writer-unlock-failed", "Native writer unlock failed; verify OS handle release before retry.", state.GUARD_PATH)
                else:
                    import fcntl
                    fcntl.flock(self.descriptor, fcntl.LOCK_UN)
        finally:
            self.held = False
            if self.descriptor is not None:
                os.close(self.descriptor)
                self.descriptor = None
