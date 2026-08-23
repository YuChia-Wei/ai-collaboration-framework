#!/usr/bin/env python3
"""Given-When-Then tests for evidence-bound read-only upgrade routing."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))

import ai_context_upgrade_routes as ROUTES  # noqa: E402


class RouteFixture:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="upgrade-routes-")
        self.root = Path(self._temporary.name)
        self.serial = 0
        self.target = "v0.14.0"
        self.package_identity = {
            "package_id": "ai-context-dotnet-backend-v0.14.0",
            "release_id": "REL-v0.14.0",
            "payload_fingerprint": hashlib.sha256(b"canonical-target-payload").hexdigest(),
        }
        self.matrix = {
            "template_metadata": {
                "template_id": "upgrade-route-matrix",
                "template_version": "1.1.0",
                "created_at": "2026-08-20T00:00:00+08:00",
                "updated_at": "2026-08-20T00:00:00+08:00",
            },
            "schema_version": ROUTES.SCHEMA_VERSION,
            "matrix_id": "v0.14.0-supported-upgrades",
            "target": {
                "version": self.target,
                "release_id": "REL-v0.14.0",
                "commit": "e" * 40,
                "manifest": self.asset("target/manifest.yaml", b"target-manifest"),
                "package_identity": self.package_identity,
            },
            "retained_origins": [
                self.origin("immediate-predecessor", "v0.13.0", "a"),
                self.origin("v0.9.0", "v0.9.0", "b"),
                self.origin("v0.6.0", "v0.6.0", "c"),
            ],
            "semantic_cutovers": [
                {
                    "cutover_id": "remediation-packet-v1",
                    "required": True,
                    "description": "Prospective remediation packet adoption",
                }
            ],
            "routes": [],
            "deprecations": [],
        }

    def close(self) -> None:
        self._temporary.cleanup()

    def asset(self, path: str, content: bytes) -> dict[str, str]:
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return {
            "asset_id": path.replace("/", "-"),
            "path": path,
            "sha256": hashlib.sha256(content).hexdigest(),
        }

    def canonical_json_asset(self, path: str, value: dict) -> dict[str, str]:
        return self.asset(path, ROUTES.canonical_json(value).encode("utf-8"))

    def rewrite_asset(self, identity: dict[str, str], content: bytes) -> None:
        destination = self.root / identity["path"]
        destination.write_bytes(content)
        identity["sha256"] = hashlib.sha256(content).hexdigest()

    def origin(self, role: str, version: str, commit_character: str) -> dict:
        return {
            "role": role,
            "version": version,
            "release_id": f"REL-{version}",
            "commit": commit_character * 40,
            "manifest": self.asset(f"origins/{version}/manifest.yaml", version.encode()),
        }

    def edge(
        self,
        from_version: str,
        to_version: str,
        *,
        validation_state: str = "passed",
        covers_cutover: bool = True,
    ) -> dict:
        self.serial += 1
        edge_id = f"{from_version}-to-{to_version}-{self.serial}"
        prefix = f"edges/{self.serial}"
        archive = f"archive:{edge_id}".encode()
        artifacts = {
            "archive": self.asset(f"{prefix}/package.tar.gz", archive),
            "checksum": self.asset(
                f"{prefix}/package.tar.gz.sha256",
                f"{hashlib.sha256(archive).hexdigest()}  package.tar.gz\n".encode(),
            ),
            "manifest": self.asset(f"{prefix}/migration.yaml", f"edge: {edge_id}\n".encode()),
            "validator": self.asset(f"{prefix}/validator.py", b"print('validated')\n"),
        }
        validator_argv = ["python", artifacts["validator"]["path"], "--edge-id", edge_id]
        output = self.asset(f"{prefix}/validation-output.log", f"validated {edge_id}\n".encode())
        semantic_cutovers = (
            [{"cutover_id": "remediation-packet-v1", "state": "passed"}]
            if covers_cutover
            else []
        )
        edge_package_identity = (
            deepcopy(self.package_identity)
            if to_version == self.target
            else {
                "package_id": f"ai-context-dotnet-backend-{to_version}",
                "release_id": f"REL-{to_version}",
                "payload_fingerprint": hashlib.sha256(
                    f"canonical-payload:{to_version}".encode()
                ).hexdigest(),
            }
        )
        report = {
            "schema_version": ROUTES.EDGE_VALIDATION_RECEIPT_SCHEMA_VERSION,
            "edge_id": edge_id,
            "from_version": from_version,
            "to_version": to_version,
            "artifacts": artifacts,
            "validator_argv": validator_argv,
            "semantic_cutovers": [
                {
                    "cutover_id": cutover["cutover_id"],
                    "required": True,
                    "state": cutover["state"],
                }
                for cutover in semantic_cutovers
            ],
            "portable_validation": {
                "schema_version": ROUTES.PORTABLE_VALIDATION_SCHEMA_VERSION,
                "authority": {
                    "kind": "incoming-candidate",
                    "manifest": {
                        "path": "metadata/validation.json",
                        "sha256": hashlib.sha256(b"validation-manifest").hexdigest(),
                    },
                    "validator": {
                        "path": ".ai/scripts/validate-ai-context-payload.py",
                        "sha256": hashlib.sha256(b"portable-validator").hexdigest(),
                        "argv": [
                            "python",
                            "payload/.ai/scripts/validate-ai-context-payload.py",
                            "--package-root",
                            ".",
                        ],
                    },
                },
                "package_identity": deepcopy(edge_package_identity),
                "execution": {
                    "outcome": "passed",
                    "exit_code": 0,
                    "output_sha256": hashlib.sha256(b"portable-validation-output").hexdigest(),
                },
            },
            "outcome": validation_state,
            "exit_code": 0 if validation_state == "passed" else 1,
            "output_sha256": output["sha256"],
        }
        return {
            "edge_id": edge_id,
            "order": 1,
            "from_version": from_version,
            "to_version": to_version,
            "package_identity": edge_package_identity,
            "artifacts": artifacts,
            "semantic_cutovers": semantic_cutovers,
            "validation": {
                "state": validation_state,
                "validator_argv": validator_argv,
                "report": self.canonical_json_asset(f"{prefix}/validation.json", report),
                "output": output,
            },
        }

    def route(self, route_id: str, origin: str, edges: list[dict]) -> dict:
        for order, edge in enumerate(edges, 1):
            edge["order"] = order
        return {
            "route_id": route_id,
            "origin": origin,
            "target": self.target,
            "edges": edges,
        }

    def resolve(self, origin: str) -> dict:
        raw = yaml.safe_dump(self.matrix, sort_keys=True).encode()
        return ROUTES.resolve_upgrade_route(
            self.matrix,
            origin=origin,
            target=self.target,
            matrix_bytes=raw,
            asset_root=self.root,
            matrix_reference="upgrade-route-matrix.yaml",
        )

    def complete_deprecation(self, role: str, origin: str) -> dict:
        deprecation_id = f"deprecate-{origin}"
        reason = "Owner-approved support retirement"
        notice = self.canonical_json_asset(
            f"deprecations/{origin}/notice.json",
            {
                "schema_version": ROUTES.DEPRECATION_NOTICE_SCHEMA_VERSION,
                "deprecation_id": deprecation_id,
                "role": role,
                "origin": origin,
                "target": self.target,
                "disposition": "unsupported",
                "reason": reason,
            },
        )
        decision = self.canonical_json_asset(
            f"deprecations/{origin}/owner-decision.json",
            {
                "schema_version": ROUTES.DEPRECATION_DECISION_SCHEMA_VERSION,
                "deprecation_id": deprecation_id,
                "role": role,
                "origin": origin,
                "target": self.target,
                "status": "approved",
                "approved": True,
                "owner": "framework-governance-owner",
                "decided_at": "2026-08-20T00:00:00+08:00",
            },
        )
        output = self.asset(
            f"deprecations/{origin}/validation-output.log", b"deprecation evidence validated\n"
        )
        receipt = self.canonical_json_asset(
            f"deprecations/{origin}/validation.json",
            {
                "schema_version": ROUTES.DEPRECATION_VALIDATION_RECEIPT_SCHEMA_VERSION,
                "deprecation_id": deprecation_id,
                "role": role,
                "origin": origin,
                "target": self.target,
                "deprecation_notice": notice,
                "owner_decision": decision,
                "outcome": "passed",
                "exit_code": 0,
                "output_sha256": output["sha256"],
            },
        )
        return {
            "deprecation_id": deprecation_id,
            "role": role,
            "origin": origin,
            "target": self.target,
            "disposition": "unsupported",
            "complete": True,
            "reason": reason,
            "evidence": {
                "deprecation_notice": notice,
                "owner_decision": decision,
                "validator": receipt,
                "output": output,
            },
        }


class UpgradeRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = RouteFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_gwt_001_given_valid_identity_when_resolved_then_direct_contains_exact_edge_assets(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("direct", result["route_kind"])
        self.assertEqual(edge["artifacts"], result["selected_route"]["edges"][0]["artifacts"])
        self.assertRegex(result["matrix"]["sha256"], r"^[0-9a-f]{64}$")

    def test_gwt_001a_given_all_retained_origins_when_portable_proof_matches_then_each_route_is_direct(self) -> None:
        origins = ("v0.13.0", "v0.9.0", "v0.6.0")
        self.fixture.matrix["routes"] = [
            self.fixture.route(
                f"{origin}-direct",
                origin,
                [self.fixture.edge(origin, self.fixture.target)],
            )
            for origin in origins
        ]

        for origin in origins:
            with self.subTest(origin=origin):
                result = self.fixture.resolve(origin)
                self.assertEqual("direct", result["route_kind"])
                self.assertEqual([], result["diagnostics"])

    def test_gwt_002_given_unique_v06_chain_when_resolved_then_order_is_immutable(self) -> None:
        edges = [
            self.fixture.edge("v0.6.0", "v0.9.0", covers_cutover=False),
            self.fixture.edge("v0.9.0", "v0.13.0", covers_cutover=False),
            self.fixture.edge("v0.13.0", self.fixture.target),
        ]
        self.fixture.matrix["routes"] = [self.fixture.route("v06-chain", "v0.6.0", edges)]

        result = self.fixture.resolve("v0.6.0")

        self.assertEqual("orchestrated-multi-hop", result["route_kind"])
        self.assertEqual([1, 2, 3], [edge["order"] for edge in result["selected_route"]["edges"]])
        self.assertEqual(
            ["REL-v0.9.0", "REL-v0.13.0", "REL-v0.14.0"],
            [
                edge["package_identity"]["release_id"]
                for edge in result["selected_route"]["edges"]
            ],
        )

    def test_gwt_003_given_deferred_edge_when_resolved_then_reconciliation_is_required(self) -> None:
        edges = [
            self.fixture.edge("v0.9.0", "v0.10.0", covers_cutover=False),
            self.fixture.edge(
                "v0.10.0",
                "v0.11.0",
                validation_state="deferred-with-owner",
                covers_cutover=False,
            ),
            self.fixture.edge("v0.11.0", self.fixture.target),
        ]
        self.fixture.matrix["routes"] = [self.fixture.route("deferred", "v0.9.0", edges)]

        result = self.fixture.resolve("v0.9.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn("edge-validation-not-passed", {item["code"] for item in result["diagnostics"]})

    def test_gwt_004_given_origin_outside_matrix_when_resolved_then_unsupported(self) -> None:
        result = self.fixture.resolve("v0.5.0")

        self.assertEqual("unsupported", result["route_kind"])
        self.assertEqual("origin-outside-matrix", result["diagnostics"][0]["code"])

    def test_gwt_005_given_two_safe_direct_routes_when_resolved_then_ambiguity_fails_closed(self) -> None:
        self.fixture.matrix["routes"] = [
            self.fixture.route(
                "direct-a", "v0.13.0", [self.fixture.edge("v0.13.0", self.fixture.target)]
            ),
            self.fixture.route(
                "direct-b", "v0.13.0", [self.fixture.edge("v0.13.0", self.fixture.target)]
            ),
        ]

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertEqual("ambiguous-safe-chain", result["diagnostics"][0]["code"])

    def test_gwt_006a_given_missing_intermediate_asset_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        (self.fixture.root / edge["artifacts"]["archive"]["path"]).unlink()

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn("missing-asset", {item["code"] for item in result["diagnostics"]})

    def test_gwt_006b_given_tampered_intermediate_asset_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        (self.fixture.root / edge["artifacts"]["validator"]["path"]).write_bytes(b"tampered")

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn("tampered-asset", {item["code"] for item in result["diagnostics"]})

    def test_gwt_007_given_direct_cutover_bypass_when_safe_chain_exists_then_selects_multi_hop(self) -> None:
        direct = self.fixture.route(
            "unsafe-direct",
            "v0.13.0",
            [self.fixture.edge("v0.13.0", self.fixture.target, covers_cutover=False)],
        )
        multi = self.fixture.route(
            "safe-multi",
            "v0.13.0",
            [
                self.fixture.edge("v0.13.0", "v0.13.1", covers_cutover=False),
                self.fixture.edge("v0.13.1", self.fixture.target),
            ],
        )
        self.fixture.matrix["routes"] = [direct, multi]

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("orchestrated-multi-hop", result["route_kind"])
        self.assertEqual("safe-multi", result["selected_route"]["route_id"])

    def test_gwt_008_given_cutover_bypass_without_safe_chain_then_reconciliation_is_required(self) -> None:
        self.fixture.matrix["routes"] = [
            self.fixture.route(
                "unsafe-direct",
                "v0.13.0",
                [self.fixture.edge("v0.13.0", self.fixture.target, covers_cutover=False)],
            )
        ]

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "direct-route-bypasses-required-cutover",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_009_given_complete_owner_deprecation_when_resolved_then_unsupported(self) -> None:
        self.fixture.matrix["retained_origins"] = [
            item for item in self.fixture.matrix["retained_origins"] if item["role"] != "v0.6.0"
        ]
        self.fixture.matrix["deprecations"] = [
            self.fixture.complete_deprecation("v0.6.0", "v0.6.0")
        ]

        result = self.fixture.resolve("v0.6.0")

        self.assertEqual("unsupported", result["route_kind"])
        self.assertEqual("fully-explicitly-deprecated", result["diagnostics"][0]["code"])

    def test_gwt_010_given_tampered_deprecation_evidence_when_validated_then_matrix_is_rejected(self) -> None:
        self.fixture.matrix["retained_origins"] = [
            item for item in self.fixture.matrix["retained_origins"] if item["role"] != "v0.6.0"
        ]
        deprecation = self.fixture.complete_deprecation("v0.6.0", "v0.6.0")
        self.fixture.matrix["deprecations"] = [deprecation]
        (self.fixture.root / deprecation["evidence"]["owner_decision"]["path"]).write_text(
            "changed", encoding="utf-8"
        )

        with self.assertRaisesRegex(ROUTES.MatrixValidationError, "incomplete deprecation evidence"):
            self.fixture.resolve("v0.6.0")

    def test_gwt_010a_given_wrong_checksum_sidecar_with_updated_self_hash_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        self.fixture.rewrite_asset(
            edge["artifacts"]["checksum"],
            f"{'0' * 64}  package.tar.gz\n".encode("utf-8"),
        )

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "checksum-archive-digest-mismatch",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_010b_given_failed_validation_report_with_updated_self_hash_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        report_path = self.fixture.root / edge["validation"]["report"]["path"]
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["outcome"] = "failed"
        report["exit_code"] = 1
        self.fixture.rewrite_asset(
            edge["validation"]["report"], ROUTES.canonical_json(report).encode("utf-8")
        )

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "edge-validation-report-outcome-not-passed",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_010l_given_same_package_and_release_with_different_payload_when_resolved_then_it_fails_closed(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        report_path = self.fixture.root / edge["validation"]["report"]["path"]
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["portable_validation"]["package_identity"]["payload_fingerprint"] = "f" * 64
        self.fixture.rewrite_asset(
            edge["validation"]["report"], ROUTES.canonical_json(report).encode("utf-8")
        )

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "edge-package-payload-identity-conflict",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_010m_given_boolean_portable_exit_code_when_resolved_then_it_fails_closed(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        report_path = self.fixture.root / edge["validation"]["report"]["path"]
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["portable_validation"]["execution"]["exit_code"] = False
        self.fixture.rewrite_asset(
            edge["validation"]["report"], ROUTES.canonical_json(report).encode("utf-8")
        )

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "edge-validation-report-invalid-shape",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_010c_given_missing_or_mismatched_validator_argv_when_checked_then_the_contract_fails_closed(self) -> None:
        missing = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [missing])]
        del missing["validation"]["validator_argv"]

        with self.assertRaisesRegex(ROUTES.MatrixValidationError, "validator_argv"):
            self.fixture.resolve("v0.13.0")

        mismatched = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [mismatched])]
        mismatched["validation"]["validator_argv"] = [
            mismatched["artifacts"]["validator"]["path"],
            "--different-contract",
        ]

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "edge-validation-report-validator-argv-mismatch",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_010d_given_absent_or_cross_mismatched_output_bytes_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        output_path = self.fixture.root / edge["validation"]["output"]["path"]
        output_path.unlink()

        absent = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", absent["route_kind"])
        self.assertIn("missing-asset", {item["code"] for item in absent["diagnostics"]})

        self.fixture.rewrite_asset(
            edge["validation"]["output"], b"other validation output bytes\n"
        )
        mismatched = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", mismatched["route_kind"])
        self.assertIn(
            "edge-validation-report-output-digest-mismatch",
            {item["code"] for item in mismatched["diagnostics"]},
        )

    def test_gwt_010e_given_approved_false_owner_decision_when_resolved_then_deprecation_invalidates_the_matrix(self) -> None:
        self.fixture.matrix["retained_origins"] = [
            item for item in self.fixture.matrix["retained_origins"] if item["role"] != "v0.6.0"
        ]
        deprecation = self.fixture.complete_deprecation("v0.6.0", "v0.6.0")
        self.fixture.matrix["deprecations"] = [deprecation]
        decision_path = self.fixture.root / deprecation["evidence"]["owner_decision"]["path"]
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        decision["approved"] = False
        self.fixture.rewrite_asset(
            deprecation["evidence"]["owner_decision"],
            ROUTES.canonical_json(decision).encode("utf-8"),
        )

        with self.assertRaisesRegex(ROUTES.MatrixValidationError, "not-approved"):
            self.fixture.resolve("v0.6.0")

    def test_gwt_010f_given_edge_asset_symlink_escape_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        archive_path = self.fixture.root / edge["artifacts"]["archive"]["path"]
        archive_path.unlink()
        with tempfile.TemporaryDirectory(prefix="upgrade-route-outside-") as outside_directory:
            outside_path = Path(outside_directory) / "archive.tar.gz"
            outside_path.write_bytes(b"outside route asset\n")
            try:
                archive_path.symlink_to(outside_path)
            except OSError:
                original_resolve = ROUTES.Path.resolve

                def simulated_resolve(path: Path, *args: object, **kwargs: object) -> Path:
                    if path == archive_path:
                        return outside_path
                    return original_resolve(path, *args, **kwargs)

                with mock.patch.object(
                    ROUTES.Path, "resolve", autospec=True, side_effect=simulated_resolve
                ):
                    result = self.fixture.resolve("v0.13.0")
            else:
                result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn("unsafe-asset-path", {item["code"] for item in result["diagnostics"]})

    def test_gwt_010g_given_matrix_and_receipt_states_disagree_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        edge["validation"]["state"] = "failed"

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn("edge-validation-state-mismatch", {item["code"] for item in result["diagnostics"]})

    def test_gwt_010h_given_raw_matrix_path_aliases_when_validated_then_each_fails_before_normalization(self) -> None:
        for alias in ("./dot", "a/./b", "a//b"):
            with self.subTest(alias=alias):
                candidate = deepcopy(self.fixture.matrix)
                candidate["target"]["manifest"]["path"] = alias

                with self.assertRaisesRegex(
                    ROUTES.MatrixValidationError, "safe matrix-relative path"
                ):
                    ROUTES.validate_matrix(candidate)

    def test_gwt_010i_given_matrix_added_cutover_with_unchanged_receipt_when_resolved_then_reconciliation_is_required(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target, covers_cutover=False)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        edge["semantic_cutovers"] = [
            {"cutover_id": "remediation-packet-v1", "state": "passed"}
        ]

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "edge-validation-report-cutover-mismatch",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_010j_given_relabelled_edge_with_unchanged_receipt_when_resolved_then_reconciliation_is_required(self) -> None:
        relabelled = self.fixture.edge("v0.13.0", self.fixture.target)
        relabelled["to_version"] = "v0.9.0"
        relabelled["package_identity"] = {
            "package_id": "ai-context-dotnet-backend-v0.9.0",
            "release_id": "REL-v0.9.0",
            "payload_fingerprint": hashlib.sha256(
                b"canonical-payload:v0.9.0"
            ).hexdigest(),
        }
        successor = self.fixture.edge("v0.9.0", self.fixture.target)
        self.fixture.matrix["routes"] = [
            self.fixture.route("relabelled-chain", "v0.13.0", [relabelled, successor])
        ]

        result = self.fixture.resolve("v0.13.0")

        self.assertEqual("reconciliation-required", result["route_kind"])
        self.assertIn(
            "edge-validation-report-route-mismatch",
            {item["code"] for item in result["diagnostics"]},
        )

    def test_gwt_010k_given_duplicate_matrix_keys_when_loaded_then_the_matrix_fails_closed(self) -> None:
        for label, content in (
            (
                "top-level",
                "schema_version: '1.0'\nschema_version: '9.9'\n",
            ),
            (
                "nested",
                "target:\n  version: v0.14.0\n  version: v0.9.0\n",
            ),
        ):
            with self.subTest(label=label):
                matrix_path = self.fixture.root / f"duplicate-{label}.yaml"
                matrix_path.write_text(content, encoding="utf-8", newline="\n")

                with self.assertRaisesRegex(ROUTES.MatrixValidationError, "unique string keys"):
                    ROUTES.load_route_matrix(matrix_path)

    def test_gwt_011_given_explicit_matrix_cli_when_run_then_output_is_canonical_and_read_only(self) -> None:
        edge = self.fixture.edge("v0.13.0", self.fixture.target)
        self.fixture.matrix["routes"] = [self.fixture.route("direct", "v0.13.0", [edge])]
        matrix_path = self.fixture.root / "upgrade-route-matrix.yaml"
        matrix_bytes = yaml.safe_dump(self.fixture.matrix, sort_keys=True).encode()
        matrix_path.write_bytes(matrix_bytes)
        before = {
            path.relative_to(self.fixture.root): path.read_bytes()
            for path in self.fixture.root.rglob("*")
            if path.is_file()
        }

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".ai/scripts/plan-ai-context-upgrade.py"),
                "--matrix",
                str(matrix_path),
                "--origin",
                "v0.13.0",
                "--target",
                self.fixture.target,
            ],
            check=False,
            capture_output=True,
        )

        self.assertEqual(0, result.returncode, result.stderr.decode("utf-8"))
        self.assertEqual(b"", result.stderr)
        self.assertNotIn(b"\r", result.stdout)
        parsed = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(hashlib.sha256(matrix_bytes).hexdigest(), parsed["matrix"]["sha256"])
        self.assertEqual(ROUTES.canonical_json(parsed).encode("utf-8"), result.stdout)
        after = {
            path.relative_to(self.fixture.root): path.read_bytes()
            for path in self.fixture.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_gwt_011a_given_invalid_matrix_cli_when_run_then_error_is_canonical_utf8_lf(self) -> None:
        missing_matrix = self.fixture.root / "missing-upgrade-route-matrix.yaml"

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / ".ai/scripts/plan-ai-context-upgrade.py"),
                "--matrix",
                str(missing_matrix),
                "--origin",
                "v0.13.0",
                "--target",
                self.fixture.target,
            ],
            check=False,
            capture_output=True,
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual(b"", result.stdout)
        self.assertNotIn(b"\r", result.stderr)
        parsed = json.loads(result.stderr.decode("utf-8"))
        self.assertEqual(ROUTES.canonical_json(parsed).encode("utf-8"), result.stderr)

    def test_gwt_012_given_governed_role_omitted_without_deprecation_then_matrix_fails_closed(self) -> None:
        candidate = deepcopy(self.fixture.matrix)
        candidate["retained_origins"] = [
            item for item in candidate["retained_origins"] if item["role"] != "v0.9.0"
        ]

        with self.assertRaisesRegex(ROUTES.MatrixValidationError, "account for exactly"):
            ROUTES.validate_matrix(candidate)

    def test_gwt_013_given_self_inconsistent_v014_archive_when_each_retained_edge_runs_then_none_can_pass(self) -> None:
        release_dir = ROOT / ".dev/releases/v0.14.0"
        script = release_dir / "route-assets/validate-direct-edge.py"
        for origin in ("v0.13.0", "v0.9.0", "v0.6.0"):
            with self.subTest(origin=origin):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(script),
                        "--edge-id",
                        f"{origin}-to-v0.14.0",
                        "--origin-version",
                        origin,
                        "--archive",
                        "route-assets/v0.14.0/ai-context-dotnet-backend-v0.14.0.zip",
                        "--checksum",
                        "route-assets/v0.14.0/ai-context-dotnet-backend-v0.14.0.zip.sha256",
                        "--target-manifest",
                        "route-assets/v0.14.0/metadata/files.yaml",
                        "--origin-manifest",
                        f"route-assets/origins/{origin}/metadata/files.yaml",
                        "--migration",
                        "route-assets/v0.14.0/metadata/migration.yaml",
                        "--cutover-id",
                        "remediation-packet-v1",
                    ],
                    cwd=release_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                self.assertEqual(1, result.returncode)
                self.assertIn("incoming portable validation failed", result.stderr)

    def test_gwt_014_given_legacy_v014_matrix_when_each_retained_origin_is_resolved_then_portable_proof_is_required(self) -> None:
        matrix_path = ROOT / ".dev/releases/v0.14.0/support-matrix.yaml"
        matrix, matrix_bytes = ROUTES.load_route_matrix(matrix_path)
        current_validator_sha256 = hashlib.sha256(
            (matrix_path.parent / "route-assets/validate-direct-edge.py").read_bytes()
        ).hexdigest()
        for route in matrix["routes"]:
            for edge in route["edges"]:
                edge["artifacts"]["validator"]["sha256"] = current_validator_sha256
        for origin in ("v0.13.0", "v0.9.0", "v0.6.0"):
            with self.subTest(origin=origin):
                result = ROUTES.resolve_upgrade_route(
                    matrix,
                    origin=origin,
                    target="v0.14.0",
                    matrix_bytes=matrix_bytes,
                    asset_root=matrix_path.parent,
                    matrix_reference=matrix_path.as_posix(),
                )
                self.assertEqual("reconciliation-required", result["route_kind"])
                self.assertIn(
                    "edge-portable-validation-proof-missing",
                    {diagnostic["code"] for diagnostic in result["diagnostics"]},
                )


if __name__ == "__main__":
    unittest.main()
