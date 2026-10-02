"""Offline adapter state tests; every process transport result is synthetic.

The local Git-rebind response below is an explicit transport fixture, not Git or
native acceptance. Renderer/record behavior is tested with real APIs elsewhere.
"""
import json
import sys
from unittest.mock import patch

from .tool_fixtures import ToolCase, encoded, source_tool


class ProviderTransportTests(ToolCase):
    def test_unavailable_conflict_and_uncertain_write_are_not_success(self):
        family = "pr-author"
        local, _, value, _ = self.persist(family)
        inspected = local.execute(self.request(family, "inspect", reference=local.reference(value)))
        rendered = local.execute(self.request(family, "render", reference=local.reference(value)))
        self.assertFalse(rendered["subject_verified"])
        adapter = source_tool(family, "github.py")
        target, subject = value["provider_target"], value["subject"]
        request = self.request(family, "provider-create", reference=local.reference(value), repository_root=str(self.project),
            expected_record_sha256=inspected["sha256"], expected_template_sha256=rendered["template_sha256"],
            expected_body_sha256=rendered["body_sha256"], write_mode="coordinated-single-writer", grant={
                "source": "synthetic fixture only", "operation": "provider-create", "target": target,
                "body_sha256": rendered["body_sha256"]})
        expected_results = {
            "unverified-local-subject": ("blocked", "none", 0),
            "unavailable-gh": ("unavailable", "none", 0),
            "preflight-conflict": ("conflict", "none", 0),
            "post-write-read-failure": ("failed", "committed", 1),
            "lost-write-response": ("failed", "unknown", 1),
        }
        for scenario, expected in expected_results.items():
            with self.subTest(scenario=scenario):
                transport = []

                def fake_transport(argv, env, cwd, input_data=None, timeout=30):
                    if argv[0] == sys.executable:
                        operation = json.loads(input_data)["operation"]
                        synthetic_render = {**rendered, "subject_verified": scenario != "unverified-local-subject"}
                        response = {"explain": {"outcome": "succeeded"}, "inspect": inspected, "render": synthetic_render}[operation]
                        return 0, encoded({**response, "operation": operation, "mutation_state": "none"}), b""
                    self.assertEqual(argv[0], "gh")
                    method = argv[argv.index("--method") + 1]
                    endpoint = argv[-3] if argv[-2:] == ["--input", "-"] else argv[-1]
                    transport.append((method, endpoint))
                    if scenario == "unavailable-gh":
                        adapter.fail("executable", "Synthetic missing executable", "unavailable")
                    if "/git/ref/heads/" in endpoint:
                        name = endpoint.rsplit("/", 1)[-1]
                        oid = subject["base_commit" if name == target["base_ref"] else "head_commit"]
                        response = {"ref": "refs/heads/" + name, "object": {"type": "commit", "sha": oid}}
                        if scenario == "preflight-conflict":
                            response["object"]["sha"] = "0" * 40
                    elif "/compare/" in endpoint:
                        response = {"merge_base_commit": {"sha": subject["merge_base"]}}
                    elif "/pulls?" in endpoint:
                        response = []
                    elif method == "POST":
                        body = json.loads(input_data)
                        self.assertEqual(body["body"], rendered["view"]["markdown"])
                        self.assertTrue(body["draft"])
                        if scenario == "lost-write-response":
                            raise TimeoutError("Synthetic uncertain write result")
                        response = {"number": 1}
                    elif method == "GET" and endpoint.endswith("/pulls/1"):
                        return 1, b"", b"synthetic read failure"
                    else:
                        raise AssertionError("Unexpected transport shape")
                    return 0, encoded(response), b""

                with patch.object(adapter, "run_bounded", fake_transport), patch.object(
                        adapter.subprocess, "Popen", side_effect=AssertionError("Live process forbidden")):
                    result = adapter.execute(request)
                self.assertEqual((result["outcome"], result["mutation_state"], sum(method == "POST" for method, _ in transport)), expected)
                if scenario == "unverified-local-subject":
                    self.assertEqual(transport, [])
