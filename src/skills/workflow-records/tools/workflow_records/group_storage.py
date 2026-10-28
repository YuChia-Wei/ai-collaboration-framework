"""Local-group persistence: one OS lock and bounded atomic carrier envelopes."""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import stat
import tempfile

from . import source_contract as c
from .contracts import RecordError, require

MAX_BYTES = 32 * 1024 * 1024
FORMAT = "workflow-local-group-envelope/1"
SCHEMA = "workflow-local-group-sqlite/1"


def local_path(value):
    require(isinstance(value, str) and Path(value).is_absolute(), "unsafe_path", "An explicit absolute local path is required.")
    path = Path(value)
    require(not str(path).startswith(("\\\\", "//")), "unsupported_topology", "Network paths are unsupported.")
    for item in [*reversed(path.parents), path]:
        if item.exists() or item.is_symlink():
            info = item.lstat()
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
                    "unsafe_path", "Links and reparse points are unsupported.")
            if item.is_file():
                require(info.st_nlink == 1, "unsafe_path", "Hard-linked storage is unsupported.")
    if os.name == "nt":
        import ctypes
        require(ctypes.windll.kernel32.GetDriveTypeW(str(path.anchor)) != 4,
                "unsupported_topology", "Mapped network storage is unsupported.")
    return path.resolve()


def bounded(value):
    raw = c.canonical(value)
    require(len(raw) <= MAX_BYTES, "limit_exceeded", "The complete retained envelope exceeds 32 MiB; nothing was pruned.")
    return raw


def read_json(path):
    path = local_path(str(path))
    require(path.is_file(), "provider_unavailable", "Selected storage is unavailable; no fallback was attempted.")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, "limit_exceeded", "Stored object exceeds the complete-object bound.")
    return c.parse(raw)


def atomic_json(path, value, *, fresh=False):
    path = local_path(str(path))
    raw = bounded(value)
    require(path.parent.is_dir(), "not_found", "Storage parent must already exist.")
    if fresh:
        require(not path.exists(), "already_exists", "Fresh storage cannot replace existing bytes.")
    fd, temporary = tempfile.mkstemp(prefix=".group-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if fresh:
            publish_fresh(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def publish_fresh(temporary, path):
    """Publish complete initial bytes without replacing another initializer."""
    if os.name == "nt":
        os.rename(temporary, path)  # Windows rename refuses an existing destination.
    else:
        os.link(temporary, path)
        os.unlink(temporary)


@contextmanager
def group_lock(directory):
    """Keep the lock inode stable. Kernel ownership ends on process exit."""
    directory = local_path(str(directory))
    require(directory.is_dir(), "not_found", "Explicit control directory must already exist.")
    path = local_path(str(directory / "group.lock"))
    stream = path.open("a+b")
    locked = False
    try:
        if os.name == "nt":
            import msvcrt
            stream.seek(0, 2)
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                locked = True
            except OSError:
                require(False, "writer_busy", "Another group operation holds the OS lock.")
        else:
            import fcntl
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
            except BlockingIOError:
                require(False, "writer_busy", "Another group operation holds the OS lock.")
        yield
    finally:
        if locked:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


def envelope_digest(value):
    return c.digest(bounded(value))


def sqlite_runtime():
    try:
        import sqlite3
        return sqlite3
    except ImportError:
        require(False, "provider_unavailable", "Selected SQLite runtime is unavailable; file authority was not replaced.")


def load_member(member):
    if member["kind"] == "file":
        return read_json(local_path(member["path"]))
    sqlite3 = sqlite_runtime()
    try:
        return _load_member(member)
    except sqlite3.Error as exc:
        raise RecordError("storage_error", "SQLite carrier is unavailable or malformed; reconcile its original operation.") from exc


def _load_member(member):
    path = local_path(member["path"])
    if member["kind"] == "file":
        return read_json(path)
    require(path.is_file(), "provider_unavailable", "Selected SQLite carrier is missing.")
    sqlite3 = sqlite_runtime()
    connection = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True, timeout=0, isolation_level=None)
    try:
        connection.execute("PRAGMA trusted_schema=OFF")
        row = connection.execute("SELECT schema_version,payload FROM group_envelope WHERE id=1").fetchone()
        require(row and row[0] == SCHEMA, "unsupported_version", "Not a local-group SQLite carrier; native databases are never adopted.")
        require(len(row[1]) <= MAX_BYTES, "limit_exceeded", "SQLite envelope exceeds the retained bound.")
        return c.parse(bytes(row[1]))
    finally:
        connection.close()


def save_member(member, value, expected=None, *, fresh=False):
    if member["kind"] == "file":
        return _save_member(member, value, expected, fresh=fresh)
    sqlite3 = sqlite_runtime()
    try:
        return _save_member(member, value, expected, fresh=fresh)
    except sqlite3.Error as exc:
        raise RecordError("storage_error", "SQLite commit is unavailable; reconcile the original operation before retry.") from exc


def _save_member(member, value, expected=None, *, fresh=False):
    path = local_path(member["path"])
    raw = bounded(value)
    if member["kind"] == "file":
        if not fresh:
            require(envelope_digest(load_member(member)) == expected, "replica_conflict", "File carrier changed outside the selected commit.")
        return atomic_json(path, value, fresh=fresh)
    sqlite3 = sqlite_runtime()
    temporary = None
    database = path
    if fresh:
        require(not path.exists(), "already_exists", "SQLite initialization requires a fresh path.")
        fd, name = tempfile.mkstemp(prefix=".group-sqlite-", dir=path.parent)
        os.close(fd)
        temporary = Path(name)
        database = temporary
    connection = sqlite3.connect(database.as_uri() + "?mode=rw", uri=True, timeout=0, isolation_level=None)
    committed = False
    try:
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.execute("PRAGMA synchronous=FULL")
        if fresh:
            connection.execute("PRAGMA journal_mode=DELETE")
        require(connection.execute("PRAGMA journal_mode").fetchone()[0] == "delete", "unsupported_topology", "SQLite requires DELETE journal.")
        connection.execute("BEGIN IMMEDIATE")
        if fresh:
            connection.execute("CREATE TABLE group_envelope(id INTEGER PRIMARY KEY CHECK(id=1),schema_version TEXT NOT NULL,payload BLOB NOT NULL)")
            connection.execute("INSERT INTO group_envelope VALUES(1,?,?)", (SCHEMA, raw))
        else:
            row = connection.execute("SELECT schema_version,payload FROM group_envelope WHERE id=1").fetchone()
            require(row and row[0] == SCHEMA, "unsupported_version", "Not a local-group carrier.")
            require(c.digest(bytes(row[1])) == expected, "replica_conflict", "SQLite carrier changed before commit.")
            connection.execute("UPDATE group_envelope SET payload=? WHERE id=1", (raw,))
        connection.commit()
        committed = True
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()
        if temporary is not None:
            try:
                if committed:
                    publish_fresh(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
