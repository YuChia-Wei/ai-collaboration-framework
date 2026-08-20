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
        self.matrix = {
            "template_metadata": {
                "template_id": "upgrade-route-matrix",
                "template_version": "1.0.0",
                "created_at": "2026-08-20T00:00:00+08:00",
                "updated_at": "2026-08-20T00:00:00+08:00",
            },
            "schema_version": "1.0",
            "matrix_id": "v0.14.0-supported-upgrades",
            "target": {
                "version": self.target,
                "release_id": "REL-v0.14.0",
                "commit": "e" * 40,
                "manifest": self.asset("target/manifest.yaml", b"target-manifest"),
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
        return {
            "edge_id": edge_id,
            "order": 1,
            "from_version": from_version,
            "to_version": to_version,
            "artifacts": artifacts,
            "semantic_cutovers": (
                [{"cutover_id": "remediation-packet-v1", "state": "passed"}]
                if covers_cutover
                else []
            ),
            "validation": {
                "state": validation_state,
                "report": self.asset(
                    f"{prefix}/validation.json",
                    json.dumps({"state": validation_state}, sort_keys=True).encode(),
                ),
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
        return {
            "deprecation_id": f"deprecate-{origin}",
            "role": role,
            "origin": origin,
            "target": self.target,
            "disposition": "unsupported",
            "complete": True,
            "reason": "Owner-approved support retirement",
            "evidence": {
                "deprecation_notice": self.asset(
                    f"deprecations/{origin}/release-notes.md", b"support retired\n"
                ),
                "owner_decision": self.asset(
                    f"deprecations/{origin}/owner-decision.json", b'{"approved":true}\n'
                ),
                "validator": self.asset(
                    f"deprecations/{origin}/validation.json", b'{"state":"passed"}\n'
                ),
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
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        parsed = json.loads(result.stdout)
        self.assertEqual(hashlib.sha256(matrix_bytes).hexdigest(), parsed["matrix"]["sha256"])
        self.assertEqual(ROUTES.canonical_json(parsed), result.stdout)
        after = {
            path.relative_to(self.fixture.root): path.read_bytes()
            for path in self.fixture.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_gwt_012_given_governed_role_omitted_without_deprecation_then_matrix_fails_closed(self) -> None:
        candidate = deepcopy(self.fixture.matrix)
        candidate["retained_origins"] = [
            item for item in candidate["retained_origins"] if item["role"] != "v0.9.0"
        ]

        with self.assertRaisesRegex(ROUTES.MatrixValidationError, "account for exactly"):
            ROUTES.validate_matrix(candidate)


if __name__ == "__main__":
    unittest.main()
