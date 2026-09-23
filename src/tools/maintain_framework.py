"""Fixed development entry: isolated Python, one JSON stdin request/result.

Host prerequisites: Python 3.10+ and provisioned PyYAML 6.x. No installer,
network action, runtime selection, skill launcher or arbitrary command options.
Use: python -I -B /explicit/checkout/src/tools/maintain_framework.py
"""
import sys
sys.dont_write_bytecode = True  # Before any local product or dependency import.

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat

# Bootstrap knows the exact local closure BEFORE importing it. The state owner
# checks the same closed list and actual loaded origins again at dispatch.
ENGINE_FILES = (
    "src/distribution/__init__.py",
    "src/distribution/data.py",
    "src/distribution/git_source.py",
    "src/distribution/installation.py",
    "src/distribution/installation_io.py",
    "src/distribution/installation_plan.py",
    "src/distribution/installation_state.py",
    "src/distribution/maintenance_coordination.py",
    "src/distribution/package.py",
    "src/tools/maintain_framework.py",
)
DOCUMENT_LIMIT = 4 * 1024 * 1024
FILE_LIMIT = 16 * 1024 * 1024
TOTAL_LIMIT = 128 * 1024 * 1024
_framework_bootstrap = None
_framework_bootstrap_bytes = 0


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _reject_number(value):
    raise ValueError("unsupported JSON number")


def _direct_identity(target: Path, directory: bool) -> list:
    """Observe plain ancestors and the selected file/directory before imports."""
    result = []
    for item in reversed((target, *target.parents)):
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("linked bootstrap path")
        if item != target or directory:
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError("invalid bootstrap directory")
        elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > FILE_LIMIT:
            raise ValueError("invalid bootstrap member")
        result.append((info.st_dev, info.st_ino))
    return result


def _windows_canonical(target: Path) -> Path:
    """Only _direct's error-1 path calls this stdlib-only pre-pin predicate."""
    import ctypes
    from ctypes import wintypes as w

    if (not target.is_absolute() or str(target).startswith(("\\\\", "//"))
            or ".." in target.parts):
        raise ValueError("invalid bootstrap local path")
    for part in target.parts[1:]:
        if (part.endswith((".", " ")) or re.search(r'[<>:"|?*\x00-\x1f]', part)
                or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³])(?:\..*)?", part)):
            raise ValueError("ambiguous bootstrap path")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.QueryDosDeviceW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
    kernel.QueryDosDeviceW.restype = w.DWORD
    device = ctypes.create_unicode_buffer(32768)
    length = kernel.QueryDosDeviceW(target.drive, device, len(device))
    kernel.GetDriveTypeW.argtypes = [w.LPCWSTR]
    kernel.GetDriveTypeW.restype = w.UINT
    if (not 0 < length < len(device) or re.fullmatch(r"\\Device\\[^\\]+", device.value) is None
            or kernel.GetDriveTypeW(target.anchor) not in {2, 3, 5, 6}):
        raise ValueError("direct bootstrap drive unavailable")
    kernel.GetLongPathNameW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
    kernel.GetLongPathNameW.restype = w.DWORD
    canonical = ctypes.create_unicode_buffer(32768)
    length = kernel.GetLongPathNameW(str(target), canonical, len(canonical))
    if not 0 < length < len(canonical):
        raise ValueError("canonical bootstrap name unavailable")
    return Path(canonical.value)


def _direct(target: Path, *, directory: bool = False) -> None:
    if len(str(target).encode("utf-16-le")) // 2 > 240 or any(len(part.encode("utf-16-le")) // 2 > 255 for part in target.parts):
        raise ValueError("bootstrap path budget")
    before = _direct_identity(target, directory)
    try:
        canonical = target.resolve(strict=True)
    except OSError as exc:
        if os.name != "nt" or getattr(exc, "winerror", None) != 1:
            raise
        # ERROR_INVALID_FUNCTION only. The native long-name query cannot by
        # itself prove direct ancestry, usable identity or absence of DOS aliases.
        if not all(device and inode for device, inode in before):
            raise ValueError("bootstrap identity unavailable")
        canonical = _windows_canonical(target)
    if canonical != target:
        raise ValueError("noncanonical bootstrap path")
    if _direct_identity(target, directory) != before:
        raise ValueError("bootstrap path identity changed")


class _VerifiedSourceFinder:
    """Load only the local closure, from bytes retained after pin verification."""

    def __init__(self, sources):
        self.sources = sources

    def find_spec(self, fullname, path=None, target=None):
        if fullname != "distribution" and not fullname.startswith("distribution."):
            return None  # Host stdlib/PyYAML retain their existing import boundary.
        if fullname not in self.sources:
            raise ImportError("module outside fixed engine closure")
        filename, _ = self.sources[fullname]
        locations = [str(filename.parent)] if fullname == "distribution" else None
        return importlib.util.spec_from_file_location(fullname, filename, loader=self,
                                                     submodule_search_locations=locations)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        filename, content = self.sources[module.__spec__.name]
        # Never ask a SourceLoader for code: even -B can read a valid old .pyc.
        exec(compile(content, str(filename), "exec", dont_inherit=True), module.__dict__)


def main() -> int:
    global _framework_bootstrap, _framework_bootstrap_bytes
    operation = "inspect"
    finder = None
    try:
        if len(sys.argv) != 1 or not sys.flags.isolated or not sys.flags.dont_write_bytecode or sys.version_info < (3, 10):
            raise ValueError("requires isolated Python 3.10+ with -B and no options")
        raw = sys.stdin.buffer.read(DOCUMENT_LIMIT + 1)
        if len(raw) > DOCUMENT_LIMIT:
            raise ValueError("request limit")
        request = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs, parse_constant=_reject_number)
        if type(request) is not dict:
            raise ValueError("request object")
        if request.get("operation") in {"inspect", "plan", "apply", "recover"}:
            operation = request["operation"]
        pin = request.get("engine")
        if type(pin) is not dict or set(pin) != {"id", "version", "source_commit", "files"}:
            raise ValueError("closed engine pin")
        if pin["id"] != "framework-managed-installation" or pin["version"] != "1.0.0" or type(pin["source_commit"]) is not str or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", pin["source_commit"]):
            raise ValueError("engine identity")
        rows = pin["files"]
        if type(rows) is not list or len(rows) != len(ENGINE_FILES):
            raise ValueError("engine closure")
        launch = Path(__file__).absolute()
        _direct(launch)
        root = launch.parents[2]
        if type(request.get("engine_root")) is not str or Path(request["engine_root"]) != root:
            raise ValueError("executing root")
        _direct(root, directory=True)
        total = len(raw)
        sources = {}
        for expected, row in zip(ENGINE_FILES, rows):
            if type(row) is not dict or set(row) != {"path", "sha256"} or row["path"] != expected or type(row["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"]):
                raise ValueError("engine file binding")
            target = root / expected
            _direct(target)
            before = target.stat()
            with target.open("rb") as stream:
                content = stream.read(FILE_LIMIT + 1)
            after = target.stat()
            total += len(content)
            signature = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
            if len(content) > FILE_LIMIT or total > TOTAL_LIMIT or signature(before) != signature(after) or hashlib.sha256(content).hexdigest() != row["sha256"]:
                raise ValueError("engine bytes")
            if expected.startswith("src/distribution/"):
                name = "distribution" if expected.endswith("/__init__.py") else "distribution." + target.stem
                sources[name] = (target, content)
        if any(name == "distribution" or name.startswith("distribution.") for name in sys.modules):
            raise ValueError("preloaded product modules")
        # -I excludes cwd/PYTHONPATH/user site. Explicit host Python/venv and
        # PyYAML are prerequisites, outside the local source pin.
        import yaml
        if str(getattr(yaml, "__version__", "")).split(".")[0] != "6":
            raise ValueError("PyYAML 6 required")
        # Intercept package initialization and every transitive/lazy local import.
        # Keep the checkout off sys.path so host dependencies cannot be shadowed.
        finder = _VerifiedSourceFinder(sources)
        sys.meta_path.insert(0, finder)
        import distribution
        _framework_bootstrap = (str(root), pin)
        _framework_bootstrap_bytes = total
        from distribution.installation import execute
    except (OSError, ValueError, TypeError, KeyError, ImportError, UnicodeError, RecursionError, OverflowError):
        if finder is not None:
            sys.meta_path.remove(finder)
        details = None
        if operation in {"apply", "recover"}:
            details = {"managed_state": "unsupported", "project_readiness": "not-assessed", "lock_sha256": None,
                       "operation_root": None, "counts": None, "protected_input_state": "unresolved"}
        elif operation == "inspect":
            details = {"managed_state": "unsupported", "project_readiness": "not-assessed", "owned": None,
                       "unknown": None, "drift": None, "mode_policy": None}
        result = {"api_version": 1, "operation": operation, "outcome": "unsupported", "changed": False, "details": details,
                  "diagnostics": [{"code": "source-bootstrap", "path": None,
                                   "reason": "Fixed engine bootstrap or host prerequisites could not be established before dispatch.",
                                   "next_action": "Provide isolated Python 3.10+ with -B, existing PyYAML 6, exact external source checkout/pin and one bounded JSON request."}]}
        sys.stdout.buffer.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8"))
        return 1
    try:
        result = execute(raw)
        sys.stdout.buffer.write((json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8"))
        return 0 if result["outcome"] in {"inspected", "planned", "applied", "unchanged", "recovered", "already-matching"} else 1
    except (Exception, KeyboardInterrupt):
        # Never turn a dispatch/output failure into a fabricated unchanged result.
        sys.stderr.write("Maintenance dispatch or result delivery was interrupted. Preserve operation storage and inspect current state; no success/unchanged result is established.\n")
        return 2
    finally:
        sys.meta_path.remove(finder)


if __name__ == "__main__":
    raise SystemExit(main())
