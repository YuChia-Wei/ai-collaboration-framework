"""Assemble a new candidate only; never mutate an installed project or old output."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import os
from pathlib import Path
import stat
import sys
import uuid

from .data import DistributionError, json_bytes, path, require
from .git_source import GitSource
from .selection import select


# An explicit generator implementation identity, not downstream payload members.
# Adding an implementation module requires updating this list in the same change.
IMPLEMENTATION_MEMBERS = (
    "src/distribution/__init__.py",
    "src/distribution/data.py",
    "src/distribution/git_source.py",
    "src/distribution/package.py",
    "src/distribution/selection.py",
    "src/distribution/assembly.py",
    "src/distribution/codex.py",
)


def implementation_identity(source: GitSource) -> list[dict]:
    """Require the running implementation to match the selected commit's code.

    Universal newline conversion is the only tolerated checkout transformation;
    both raw execution-file and Git blob identities are recorded explicitly.
    """
    checkout = Path(__file__).resolve().parents[2]
    require(checkout == source.repository, "invoke the builder belonging to the selected source repository")
    identities = []
    for name in IMPLEMENTATION_MEMBERS:
        file_path = checkout.joinpath(*name.split("/"))
        no_links(file_path)
        raw = file_path.read_bytes()
        blob = source.read(name)
        require(raw.decode("utf-8").replace("\r\n", "\n") == blob.data.decode("utf-8").replace("\r\n", "\n"),
                f"generator implementation differs from selected commit: {name}; use its matching checkout")
        identities.append({"source": blob.identity(), "execution_file_sha256": sha256(raw).hexdigest()})
    return identities


def no_links(target: Path) -> None:
    """Reject links/reparse points in an existing path and all of its ancestors."""
    for current in (target, *target.parents):
        info = current.lstat()
        require(not stat.S_ISLNK(info.st_mode)
                and not (getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT),
                "output/input filesystem path contains a symlink or reparse point; choose a direct path")


def output_parent(value: Path, source: GitSource, label: str) -> Path:
    require(value.is_absolute() and ".." not in value.parts, f"{label}: supply an explicit absolute directory without traversal")
    no_links(value)
    require(value.is_dir(), f"{label}: prepare the explicitly chosen directory before building")
    resolved = value.resolve(strict=True)
    require(not resolved.is_relative_to(source.repository),
            f"{label}: choose a scratch/output root outside the source worktree; installed/source surfaces are not destinations")
    return resolved


class OwnedDirectory:
    """An exclusive per-invocation directory; no overwrite, reuse or cleanup."""

    def __init__(self, parent: Path, name: str):
        self.root = parent / path(name, "run directory")
        no_links(parent)
        try:
            self.root.mkdir(mode=0o700, exist_ok=False)
        except FileExistsError as exc:
            raise DistributionError("unique candidate/scratch destination already exists; leave it intact and select a new invocation") from exc
        info = self.root.lstat()
        self.identity = (info.st_dev, info.st_ino)

    def check(self) -> None:
        no_links(self.root)
        info = self.root.lstat()
        require(self.identity == (info.st_dev, info.st_ino), "owned run directory changed during assembly; stop without cleanup")

    def member_path(self, name: str) -> Path:
        self.check()
        name = path(name, "candidate member")
        target = self.root.joinpath(*name.split("/"))
        require(target.is_relative_to(self.root), "candidate member escaped its owned directory")
        return target

    def write(self, name: str, raw: bytes, mode: str = "100644") -> None:
        target = self.member_path(name)
        current = self.root
        for part in target.relative_to(self.root).parts[:-1]:
            current /= part
            try:
                current.mkdir(mode=0o700)
            except FileExistsError:
                require(current.is_dir(), f"candidate parent is occupied: {name}")
            no_links(current)
        self.check()
        with target.open("xb") as stream:
            stream.write(raw)
            stream.flush()
        if os.name == "posix":
            target.chmod(0o755 if mode == "100755" else 0o644)
        self.read(name, raw, mode)

    def read(self, name: str, expected: bytes, mode: str = "100644") -> bytes:
        target = self.member_path(name)
        no_links(target)
        require(target.is_file(), f"candidate member is not a regular file: {name}")
        raw = target.read_bytes()
        require(raw == expected, f"candidate bytes changed during assembly: {name}")
        if os.name == "posix":
            require(stat.S_IMODE(target.stat().st_mode) == (0o755 if mode == "100755" else 0o644),
                    f"candidate mode changed during assembly: {name}")
        return raw


def assemble(repository: Path, commit: str, profile: str, output_root: Path, scratch_root: Path) -> dict:
    """Return actual output locations only after complete content read-back.

    No network, archive/install lock, project settings, deletion or apply operation.
    Failed partial directories are retained. Completion metadata is written last;
    file presence alone is never admission evidence after an interrupted write.
    """
    source = GitSource(repository, commit)
    implementation = implementation_identity(source)
    selection = select(source, profile)
    output_parent_path = output_parent(output_root, source, "output-root")
    scratch_parent_path = output_parent(scratch_root, source, "scratch-root")
    # Finish all immutable source/closure/reference checks before writing anything.
    files_document = {"schema_version": 1, "files": [member.identity() for member in selection.members]}
    selection_document = {
        "schema_version": 1,
        "mode": "development",
        "release_version": None,
        "source": {"commit": source.commit, "tree": source.tree},
        "profile": selection.profile,
        "components": [{"id": package.id, "version": package.version,
                        "metadata_version": package.metadata["metadata_version"],
                        "members": sorted(package.members),
                        "required_dependencies": package.metadata["dependencies"]["required"],
                        "optional_dependencies": package.metadata["dependencies"]["optional"]}
                       for package in selection.packages],
        "adapters": list(selection.adapters),
        "build_inputs": [source.blobs[name].identity() for name in sorted(source.blobs)],
        "generator": {"id": "framework-development-assembly",
                      "implementation": [item["source"] for item in implementation]},
    }
    metadata = {"metadata/selection.json": json_bytes(selection_document),
                "metadata/files.json": json_bytes(files_document)}
    identity_inputs = {name: sha256(raw).hexdigest() for name, raw in metadata.items()}
    candidate_digest = sha256(json_bytes(identity_inputs)).hexdigest()
    run_id = uuid.uuid4().hex
    scratch = candidate = None
    try:
        scratch = OwnedDirectory(scratch_parent_path, f"scratch-{run_id}")
        for member in selection.members:
            scratch.write(member.candidate_path, member.data, member.mode)
        for name, raw in metadata.items():
            scratch.write(name, raw)
        candidate = OwnedDirectory(output_parent_path, f"candidate-{commit[:12]}-{run_id}")
        for member in selection.members:
            raw = scratch.read(member.candidate_path, member.data, member.mode)
            candidate.write(member.candidate_path, raw, member.mode)
        for name, raw in metadata.items():
            candidate.write(name, scratch.read(name, raw))
        # Re-read the entire emitted set and executing implementation immediately
        # before the completion marker; a marker never describes a planned build.
        for member in selection.members:
            candidate.read(member.candidate_path, member.data, member.mode)
        for name, raw in metadata.items():
            candidate.read(name, raw)
        require(implementation_identity(source) == implementation,
                "generator implementation changed during assembly; candidate remains incomplete")
        import yaml
        completion = {
            "schema_version": 1, "outcome": "assembled", "run_id": run_id,
            "completed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "candidate_identity": f"development:{commit}:{candidate_digest}",
            "candidate_sha256": candidate_digest, "identity_inputs": identity_inputs,
            "source_commit": commit, "profile": profile,
            "runtime": {"python": sys.version.split()[0], "pyyaml": yaml.__version__, "os": os.name},
            "executing_implementation": implementation,
            "mode_materialization": "posix-permissions" if os.name == "posix" else "inventory-only",
            "installation": "not-performed", "behavioral_validation": "not-performed",
            "publication": "not-performed",
        }
        candidate.write("metadata/build.json", json_bytes(completion))
        return {"outcome": "assembled", "candidate_root": str(candidate.root),
                "scratch_root": str(scratch.root), "candidate_identity": completion["candidate_identity"],
                "completion_metadata": str(candidate.root / "metadata/build.json")}
    except (OSError, DistributionError, UnicodeError) as exc:
        retained = [str(item.root) for item in (scratch, candidate) if item is not None]
        raise DistributionError(f"assembly failed; no installation performed; retained run directories: {retained}; {exc}") from exc
