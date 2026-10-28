"""Current-record directory export with real SQLite/file IO and strict preflight."""
from __future__ import annotations

import base64
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "src/skills/workflow-records"
sys.path.insert(0, str(PACKAGE / "tools"))
from workflow_records.service import WorkflowRecords
from workflow_records.contracts import VERSION, digest, encoded
from workflow_records.group_service import LocalGroup, CONFIG
from workflow_records import group_model as model
from workflow_records import file_export as files

SCRATCH = Path(os.environ.get("WORKFLOW_EXPORT_TEST_ROOT", tempfile.gettempdir()))


class FileExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_temp = tempfile.TemporaryDirectory(prefix="file-export-base-", dir=SCRATCH)
        cls.baseline = Path(cls.base_temp.name)
        (cls.baseline / "fixture.txt").write_text("Synthetic source identity", encoding="utf-8")
        for args in (("init", "--initial-branch=fixture"), ("add", "."),
                     ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "-c", "commit.gpgsign=false", "-c", "core.hooksPath=empty-hooks", "commit", "-m", "fixture")):
            subprocess.run(["git", "-C", str(cls.baseline), *args], capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.base_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="file-export-case-", dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.project = self.directory / "project"
        shutil.copytree(self.baseline, self.project)
        self.ref = {"provider_id": "local", "store_id": "fixture", "workflow_id": "workflow"}
        self.database = self.directory / "native.db"
        config = {"contract_version": VERSION, "default_provider": "local", "stores": {"local": {
            "kind": "local", "store_id": "fixture", "repository_id": "fixture", "database": str(self.database)}}}
        self.native = WorkflowRecords(self.project, config)
        self.ok(self.nrequest("init", store_ref={"provider_id": "local", "store_id": "fixture"}, operation_id="init"))
        self.record = {"metadata": {"title": "完整原始資料", "status": "active", "owner_skill": "fixture",
                         "authority": "Fixture owner", "schema_version": "0.6", "custom": {"nested": [1, True, None]}},
                       "tasks": [{"task_id": "T2", "status": "planned", "title": "第二項", "extra": ["yes", "2026-01-01"]},
                                 {"task_id": "T1", "status": "active", "title": "First", "future": {"value": 1.25}}],
                       "entrypoint": "plan.md", "documents": {"plan.md": "# 計畫\r\n下一步\r\n", "nested/empty": ""},
                       "attachments": {"binary.bin": base64.b64encode(b"\x00\xff\r\n").decode("ascii")}}
        self.ok(self.nrequest("create", operation_id="create", record=self.record))
        self.group_ref = {"group_id": "fixture", "project_id": "fixture", "workflow_id": "workflow"}
        self.control = self.directory / "control"
        self.control.mkdir()
        self.carrier = self.directory / "group.json"
        self.group = LocalGroup(self.project, {"contract_version": CONFIG, "group_ref": self.group_ref,
                                 "control_directory": str(self.control), "file_path": str(self.carrier)})
        self.counter = 0
        self.gok("group-init", operation_id="init")
        record = copy.deepcopy(self.record)
        record["tasks"][1]["future"]["value"] = 1  # Group canonical numbers are safe integers.
        record["documents"] = {name: {"encoding": "utf-8", "content": value} for name, value in record["documents"].items()}
        record["attachments"] = {name: {"encoding": "base64", "content": value} for name, value in record["attachments"].items()}
        self.gok("group-create", record=record)

    def nrequest(self, operation, **extra):
        request = {"contract_version": VERSION, "operation": operation, **extra}
        if "store_ref" not in request:
            request["workflow_ref"] = self.ref
        return self.native.execute(request)

    def ok(self, response):
        self.assertEqual(response["status"], "ok", response)
        return response["result"]

    def error(self, response, code):
        self.assertEqual(response["status"], "error", response)
        self.assertEqual(response["error"]["code"], code, response)

    def grequest(self, operation, **extra):
        self.counter += 1
        request = {"contract_version": model.PROFILE, "operation": operation, "group_ref": self.group_ref}
        reads = {"group-configuration", "group-sync-status", "group-preflight-files"}
        if operation not in reads | {"group-export-files"}:
            request["operation_id"] = "op-" + str(self.counter)
        if operation not in reads | {"group-init"}:
            status = self.ok(self.group.execute({"contract_version": model.PROFILE, "operation": "group-configuration", "group_ref": self.group_ref}))
            for key in ("configuration_revision", "authority_epoch", "revision"):
                request["expected_" + key] = status[key]
        request.update(extra)
        return self.group.execute(request)

    def gok(self, operation, **extra):
        return self.ok(self.grequest(operation, **extra))

    def export_native(self, name="export", **extra):
        revision = self.ok(self.nrequest("context"))["revision"]
        return self.ok(self.nrequest("export-files", destination=str(self.directory / name), expected_revision=revision, **extra))

    def preflight_native(self, result, **extra):
        return self.nrequest("preflight-files", directory=result["destination"], manifest_digest=result["manifest_digest"], **extra)

    def rehash(self, result, changed):
        directory = Path(result["destination"])
        manifest_path = directory / files.MANIFEST
        manifest = json.loads(manifest_path.read_bytes())
        for name in changed:
            raw = (directory / name).read_bytes()
            manifest["files"][name] = {"sha256": digest(raw), "size": len(raw)}
        raw = encoded(manifest)
        manifest_path.write_bytes(raw)
        result["manifest_digest"] = digest(raw)

    def selection(self):
        destination = self.project / ".ai/project/workflow-records"
        destination.mkdir(parents=True)
        for source, target in (("schemas/file-workflow-v1.schema.json", "workflow.schema.json"),
                               ("schemas/file-task-v1.schema.json", "task.schema.json"),
                               ("templates/file-workflow.yaml", "workflow-template.yaml"),
                               ("templates/file-task.yaml", "task-template.yaml"),
                               ("templates/file-schema-selection.json", "selection.json")):
            shutil.copyfile(PACKAGE / source, destination / target)
        selected = destination / "selection.json"
        return {"path": selected.relative_to(self.project).as_posix(), "sha256": digest(selected.read_bytes())}

    def test_native_complete_projection_and_checkpoint_preserve_source(self):
        checkpoint = {"summary": "Complete", "authority": "Fixture", "completed": ["one"], "pending": [],
                      "blockers": [], "evidence": [], "next_action": "Review"}
        context = self.ok(self.nrequest("context"))
        self.ok(self.nrequest("checkpoint", operation_id="checkpoint", checkpoint=checkpoint,
                             expected_revision=context["revision"], expected_source_head=context["source_head"]))
        before = self.database.read_bytes()
        result = self.export_native()
        self.assertEqual(self.database.read_bytes(), before)
        directory = Path(result["destination"])
        self.assertEqual(yaml.safe_load((directory / "workflow.yaml").read_bytes()), self.record["metadata"])
        self.assertEqual(yaml.safe_load((directory / "tasks/T1.yaml").read_bytes()), self.record["tasks"][1])
        self.assertEqual((directory / "documents/plan.md").read_bytes(), self.record["documents"]["plan.md"].encode("utf-8"))
        self.assertEqual((directory / "documents/nested/empty").read_bytes(), b"")
        self.assertEqual((directory / "attachments/binary.bin").read_bytes(), b"\x00\xff\r\n")
        raw = json.loads((directory / files.CURRENT).read_bytes())
        self.assertEqual(raw["checkpoint"]["value"], checkpoint)
        self.assertEqual(raw["event"]["operation_id"], "checkpoint")
        self.assertEqual(self.ok(self.preflight_native(result))["reassembly"], "exact")
        archive = self.ok(self.nrequest("export", store_ref={"provider_id": "local", "store_id": "fixture"},
                                       destination=str(self.directory / "full-backup.json")))
        self.assertIn("snapshot_digest", archive)

    def test_group_file_and_sqlite_authority_export_exact_current_body(self):
        before = self.carrier.read_bytes()
        first = self.gok("group-export-files", destination=str(self.directory / "file-cut"))
        self.assertEqual(self.carrier.read_bytes(), before)
        self.gok("member-add", member_id="sqlite", kind="sqlite", path=str(self.directory / "group.db"))
        for row in self.gok("group-sync-status")["targets"]:
            if row["target"]["kind"] == "local" and row["delivery"]["state"] != "accepted":
                self.gok("group-sync", intent_id=row["intent_id"])
        generation = self.gok("group-configuration")["members"]["sqlite"]["generation"]
        self.gok("select-authority", member_id="sqlite", expected_generation=generation)
        second = self.gok("group-export-files", destination=str(self.directory / "sqlite-cut"))
        for name in ("workflow.yaml", "tasks/T1.yaml", "documents/plan.md", "attachments/binary.bin", files.CURRENT):
            self.assertEqual((Path(first["destination"]) / name).read_bytes(), (Path(second["destination"]) / name).read_bytes())
        self.assertEqual(self.gok("group-preflight-files", directory=second["destination"], manifest_digest=second["manifest_digest"])["reassembly"], "exact")

    def test_missing_selected_group_authority_never_falls_back(self):
        self.carrier.unlink()
        response = self.group.execute({"contract_version": model.PROFILE, "group_ref": self.group_ref,
                                      "operation": "group-export-files", "destination": str(self.directory / "missing"),
                                      "expected_configuration_revision": 0, "expected_authority_epoch": 1, "expected_revision": "missing"})
        self.error(response, "provider_unavailable")
        self.assertFalse((self.directory / "missing").exists())

    def test_native_revision_and_group_cas_refuse_stale_cut(self):
        response = self.nrequest("export-files", destination=str(self.directory / "stale"), expected_revision="old")
        self.error(response, "revision_conflict")
        for key in ("expected_revision", "expected_configuration_revision", "expected_authority_epoch"):
            with self.subTest(key=key):
                response = self.grequest("group-export-files", destination=str(self.directory / "stale"), **{key: "old" if key.endswith("revision") and key == "expected_revision" else 999})
                self.assertEqual(response["status"], "error", response)
        self.assertFalse((self.directory / "stale").exists())

    def test_project_copy_selection_templates_validate_without_inserting_defaults(self):
        selected = self.selection()
        result = self.export_native(schema_selection=selected)
        self.assertEqual(yaml.safe_load((Path(result["destination"]) / "workflow.yaml").read_bytes()), self.record["metadata"])
        self.ok(self.preflight_native(result, schema_selection=selected))
        self.error(self.preflight_native(result), "integrity_error")
        template = self.project / ".ai/project/workflow-records/workflow-template.yaml"
        template.write_text("title: Changed\nstatus: planned\n", encoding="utf-8")
        revision = self.ok(self.nrequest("context"))["revision"]
        self.error(self.nrequest("export-files", destination=str(self.directory / "changed"), expected_revision=revision,
                                 schema_selection=selected), "integrity_error")
        self.assertFalse((self.directory / "changed").exists())

    def test_incompatible_project_schema_fails_before_publication(self):
        selected = self.selection()
        path = self.project / selected["path"]
        selection = json.loads(path.read_bytes())
        schema_path = self.project / selection["schemas"]["workflow"]["path"]
        schema_path.write_bytes(encoded({"type": "object", "required": ["owner_custom_field"]}))
        selection["schemas"]["workflow"]["sha256"] = digest(schema_path.read_bytes())
        path.write_bytes(encoded(selection))
        selected["sha256"] = digest(path.read_bytes())
        revision = self.ok(self.nrequest("context"))["revision"]
        self.error(self.nrequest("export-files", destination=str(self.directory / "conflict"), expected_revision=revision,
                                 schema_selection=selected), "schema_conflict")
        self.assertFalse((self.directory / "conflict").exists())

    def test_managed_missing_and_external_schema_resources_fail_closed(self):
        revision = self.ok(self.nrequest("context"))["revision"]
        for path, code in ((".ai/core/schema.json", "unsafe_path"), (".agents/schema.json", "unsafe_path"),
                           ("../schema.json", "unsafe_path"), (".ai/project/missing.json", "not_found")):
            with self.subTest(path=path):
                self.error(self.nrequest("export-files", destination=str(self.directory / "blocked"), expected_revision=revision,
                                         schema_selection={"path": path, "sha256": "sha256:missing"}), code)
        selected = self.selection()
        path = self.project / selected["path"]
        selection = json.loads(path.read_bytes())
        schema = self.project / selection["schemas"]["workflow"]["path"]
        schema.write_bytes(encoded({"$ref": "https://example.invalid/forbidden.json"}))
        selection["schemas"]["workflow"]["sha256"] = digest(schema.read_bytes())
        path.write_bytes(encoded(selection))
        selected["sha256"] = digest(path.read_bytes())
        self.error(self.nrequest("export-files", destination=str(self.directory / "blocked"), expected_revision=revision,
                                 schema_selection=selected), "unsupported_format")
        schema.write_bytes(encoded({"$schema": "http://json-schema.org/draft-07/schema#", "type": "object"}))
        selection["schemas"]["workflow"]["sha256"] = digest(schema.read_bytes())
        path.write_bytes(encoded(selection))
        selected["sha256"] = digest(path.read_bytes())
        self.error(self.nrequest("export-files", destination=str(self.directory / "blocked"), expected_revision=revision,
                                 schema_selection=selected), "unsupported_version")

    def test_case_and_file_directory_collisions_are_preflighted(self):
        self.gok("group-create-task", task={"task_id": "t1"})
        self.error(self.grequest("group-export-files", destination=str(self.directory / "task-collision")), "unsafe_path")
        for paths in (("same", "SAME"), ("prefix", "prefix/child"), ("A/one", "a/two")):
            with self.subTest(paths=paths):
                self.assertRaises(files.RecordError, files.check_paths, ["documents/" + name for name in paths])

    def test_document_prefix_collision_refuses_entire_export(self):
        self.gok("group-revise-workflow", metadata_patch={}, task_patches={}, attachments={},
                 documents={name: {"encoding": "utf-8", "content": name} for name in ("prefix", "prefix/child")})
        self.error(self.grequest("group-export-files", destination=str(self.directory / "collision")), "unsafe_path")
        self.assertFalse((self.directory / "collision").exists())

    def test_group_long_task_identity_preserves_group_contract(self):
        task_id = "T" + "x" * 159
        self.gok("group-create-task", task={"task_id": task_id, "extra": "preserved"})
        selected = self.selection()
        result = self.gok("group-export-files", destination=str(self.directory / "long-id"), schema_selection=selected)
        self.assertEqual(yaml.safe_load((Path(result["destination"]) / ("tasks/" + task_id + ".yaml")).read_bytes()),
                         {"task_id": task_id, "extra": "preserved"})
        self.gok("group-preflight-files", directory=result["destination"], manifest_digest=result["manifest_digest"], schema_selection=selected)

    def test_existing_destination_live_overlap_and_write_failure_preserve_source(self):
        existing = self.directory / "existing"
        existing.mkdir()
        (existing / "keep").write_bytes(b"user")
        revision = self.ok(self.nrequest("context"))["revision"]
        self.error(self.nrequest("export-files", destination=str(existing), expected_revision=revision), "already_exists")
        self.assertEqual((existing / "keep").read_bytes(), b"user")
        self.error(self.nrequest("export-files", destination=str(self.database), expected_revision=revision), "unsafe_path")
        self.error(self.nrequest("export-files", destination=str(self.database) + "-journal", expected_revision=revision), "unsafe_path")
        self.error(self.grequest("group-export-files", destination=str(self.control / "export")), "unsafe_path")
        before = self.database.read_bytes()
        with patch.object(files.os, "fsync", side_effect=OSError("injected flush failure")):
            self.error(self.nrequest("export-files", destination=str(self.directory / "failed"), expected_revision=revision), "io_error")
        self.assertFalse((self.directory / "failed").exists())
        self.assertEqual(self.database.read_bytes(), before)

    def test_preflight_detects_byte_semantic_and_current_record_tampering(self):
        for changed in ("workflow.yaml", files.CURRENT, "attachments/binary.bin"):
            with self.subTest(changed=changed):
                result = self.export_native(name="tamper-" + str(len(changed)))
                path = Path(result["destination"]) / changed
                if changed == "workflow.yaml":
                    metadata = yaml.safe_load(path.read_bytes())
                    metadata["custom"] = "changed"
                    path.write_bytes(files.yaml_bytes(metadata))
                elif changed == files.CURRENT:
                    current = json.loads(path.read_bytes())
                    current["event"]["operation_id"] = "changed"
                    path.write_bytes(encoded(current))
                else:
                    path.write_bytes(b"changed")
                self.rehash(result, [changed])
                self.error(self.preflight_native(result), "integrity_error")

    def test_preflight_requires_exact_file_directory_and_identity_closure(self):
        result = self.export_native()
        directory = Path(result["destination"])
        (directory / "unlisted").write_bytes(b"extra")
        self.error(self.preflight_native(result), "integrity_error")
        (directory / "unlisted").unlink()
        (directory / "extra-directory").mkdir()
        self.error(self.preflight_native(result), "integrity_error")
        (directory / "extra-directory").rmdir()
        (directory / "tasks/T1.yaml").unlink()
        self.error(self.preflight_native(result), "integrity_error")
        self.error(self.grequest("group-preflight-files", directory=result["destination"], manifest_digest=result["manifest_digest"]), "binding_mismatch")

    def test_malformed_manifest_returns_stable_error(self):
        result = self.export_native()
        path = Path(result["destination"]) / files.MANIFEST
        manifest = json.loads(path.read_bytes())
        manifest["source"] = "not-a-source-object"
        raw = encoded(manifest)
        path.write_bytes(raw)
        result["manifest_digest"] = digest(raw)
        self.error(self.preflight_native(result), "malformed_record")

    def test_copied_cli_closure_exports_and_missing_module_is_unavailable(self):
        runtime = self.directory / "isolated-package"
        shutil.copytree(PACKAGE, runtime)
        native_config = self.directory / "native-config.json"
        native_config.write_bytes(encoded(self.native.config))
        group_config = self.directory / "group-config.json"
        group_config.write_bytes(encoded({"contract_version": CONFIG, "group_ref": self.group_ref,
                                          "control_directory": str(self.control), "file_path": str(self.carrier)}))
        status = self.gok("group-configuration")
        requests = [
            ("workflow-records.py", native_config, {"contract_version": VERSION, "operation": "export-files",
                "workflow_ref": self.ref, "destination": str(self.directory / "native-cli"),
                "expected_revision": self.ok(self.nrequest("context"))["revision"]}),
            ("local-group.py", group_config, {"contract_version": model.PROFILE, "operation": "group-export-files",
                "group_ref": self.group_ref, "destination": str(self.directory / "group-cli"),
                **{"expected_" + key: status[key] for key in ("configuration_revision", "authority_epoch", "revision")}}),
        ]
        for script, config, request in requests:
            with self.subTest(script=script):
                request_path = self.directory / "cli-request.json"
                request_path.write_bytes(encoded(request))
                command = [sys.executable, "-I", "-B", str(runtime / "tools" / script), "--root", str(self.project),
                           "--config", str(config), "--request", str(request_path)]
                response = subprocess.run(command, capture_output=True, check=True)
                self.ok(json.loads(response.stdout))
        (runtime / "tools/workflow_records/file_export.py").unlink()
        for script, config, request in requests:
            request_path.write_bytes(encoded(request))
            response = subprocess.run([sys.executable, "-I", "-B", str(runtime / "tools" / script), "--root", str(self.project),
                                       "--config", str(config), "--request", str(request_path)], capture_output=True)
            self.assertEqual(response.returncode, 1, response.stderr)
            self.assertEqual(json.loads(response.stdout)["error"]["code"], "provider_unavailable")

    def test_unsafe_and_link_paths_are_refused(self):
        revision = self.ok(self.nrequest("context"))["revision"]
        self.error(self.nrequest("export-files", destination=str(self.directory / "bad:ads"), expected_revision=revision), "unsafe_path")
        target = self.directory / "linked"
        target.mkdir()
        link = self.directory / "link"
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError:
            # Windows directory junctions exercise the same reparse prohibition
            # without developer-mode symlink privileges.
            if os.name != "nt":
                raise
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, check=True)
        try:
            self.error(self.nrequest("export-files", destination=str(link / "export"), expected_revision=revision), "unsafe_path")
        finally:
            if link.is_symlink():
                link.unlink()
            else:
                link.rmdir()


if __name__ == "__main__":
    unittest.main(verbosity=2)
