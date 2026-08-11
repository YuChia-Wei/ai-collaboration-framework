#!/usr/bin/env python3
"""Focused fail-closed tests for the selected-payload user-view contract."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / ".ai/scripts"))
import ai_context_package as PACKAGE  # noqa: E402


def payload_file(
    path: str,
    content: str,
    component_id: str = "software-development-core",
) -> PACKAGE.PayloadFile:
    return PACKAGE.PayloadFile(
        path=path,
        source_path=path,
        content=content.encode("utf-8"),
        mode=0o644,
        ownership="framework-managed",
        install_behavior="managed",
        entry_id="fixture",
        component_id=component_id,
    )


def user_view_contract(*, code_reviewer: bool = False) -> dict:
    capabilities = []
    if code_reviewer:
        capabilities.append(
            {
                "capability_id": "code-reviewer",
                "owner_component": "dotnet-backend",
                "path_patterns": [
                    ".ai/assets/skills/code-reviewer/**",
                    ".ai/assets/sub-agent-role-prompts/*code-review-sub-agent/**",
                ],
                "availability": {
                    "core-only": "unavailable-not-selected",
                    "dotnet-selected": "available",
                },
            }
        )
    return {
        "schema_version": "1.0.0",
        "classifications": dict(PACKAGE.PAYLOAD_USER_VIEW_CLASSIFICATIONS),
        "reference_integrity": {
            "text_extensions": [".md", ".yaml", ".sh"],
            "forbidden_source_lifecycle_patterns": [
                ".dev/workflows/20*/**",
                ".dev/assessments/ASM-*/**",
                ".dev/releases/v*/**",
                ".dev/backlog/items/**",
            ],
        },
        "components": [
            {
                "component_id": "software-development-core",
                "classification": "mandatory-core",
                "required": True,
                "requires": [],
            },
            {
                "component_id": "ai-context-lifecycle-core",
                "classification": "mandatory-core",
                "required": True,
                "requires": [],
            },
            {
                "component_id": "dotnet-backend",
                "classification": "technology-profile",
                "required": False,
                "requires": ["software-development-core"],
            },
        ],
        "supported_selections": [
            {
                "selection_id": "core-only",
                "components": [
                    "software-development-core",
                    "ai-context-lifecycle-core",
                ],
            },
            {
                "selection_id": "dotnet-selected",
                "components": [
                    "software-development-core",
                    "ai-context-lifecycle-core",
                    "dotnet-backend",
                ],
            },
        ],
        "capabilities": capabilities,
    }


class PayloadUserViewContractTests(unittest.TestCase):
    def test_given_navigation_classes_when_targets_exist_then_contract_passes(self) -> None:
        files = [
            payload_file(
                "docs/index.md",
                "\n".join(
                    [
                        "# Index",
                        "[directory](guide/)",
                        "[anchor](guide/page.md#section)",
                        "[external](https://example.invalid/missing)",
                        "[template](guide/{page}.md)",
                        "`[inline example](missing-inline.md)`",
                        "```markdown",
                        "[fenced example](missing-fenced.md)",
                        "```",
                    ]
                ),
            ),
            payload_file("docs/guide/page.md", "# Guide\n\n## Section\n"),
        ]

        PACKAGE.validate_payload_user_view(files, user_view_contract())

    def test_given_missing_navigation_or_anchor_when_validated_then_it_fails_closed(self) -> None:
        with self.subTest("missing local target"):
            with self.assertRaisesRegex(PACKAGE.PackageError, "navigation targets are missing"):
                PACKAGE.validate_payload_user_view(
                    [payload_file("docs/index.md", "[missing](missing.md)\n")],
                    user_view_contract(),
                )
        with self.subTest("missing local anchor"):
            with self.assertRaisesRegex(PACKAGE.PackageError, "anchors are missing"):
                PACKAGE.validate_payload_user_view(
                    [
                        payload_file("docs/index.md", "[missing anchor](guide.md#missing)\n"),
                        payload_file("docs/guide.md", "# Present\n"),
                    ],
                    user_view_contract(),
                )

    def test_given_unsatisfied_actionable_command_when_validated_then_it_fails_closed(self) -> None:
        files = [
            payload_file(
                "docs/commands.md",
                "```powershell\npython .ai/scripts/missing.py\n```\n",
            )
        ]
        with self.assertRaisesRegex(PACKAGE.PackageError, "actionable command targets are missing"):
            PACKAGE.validate_payload_user_view(files, user_view_contract())

    def test_given_non_command_code_and_placeholder_when_validated_then_they_are_non_actionable(self) -> None:
        files = [
            payload_file(
                "docs/examples.md",
                "```python\nprint('.ai/scripts/missing.py')\n```\n"
                "`python .ai/scripts/<target>.py`\n",
            )
        ]

        PACKAGE.validate_payload_user_view(files, user_view_contract())

    def test_given_code_reviewer_component_split_when_validated_then_core_leak_fails(self) -> None:
        split = [
            payload_file(
                ".ai/assets/skills/code-reviewer/skill.yaml",
                'references: [".ai/assets/tech-stacks/dotnet-backend/standard.md"]\n',
            ),
            payload_file(
                ".ai/assets/tech-stacks/dotnet-backend/standard.md",
                "# Standard\n",
                "dotnet-backend",
            ),
        ]
        with self.assertRaisesRegex(PACKAGE.PackageError, "not owned entirely"):
            PACKAGE.validate_payload_user_view(split, user_view_contract(code_reviewer=True))

    def test_given_code_reviewer_owned_by_dotnet_when_validated_then_both_dispositions_close(self) -> None:
        closed = [
            payload_file(
                ".ai/assets/skills/code-reviewer/skill.yaml",
                'references: [".ai/assets/tech-stacks/dotnet-backend/standard.md"]\n',
                "dotnet-backend",
            ),
            payload_file(
                ".ai/assets/sub-agent-role-prompts/code-review-sub-agent/sub-agent.yaml",
                'references: [".ai/assets/skills/code-reviewer/skill.yaml"]\n',
                "dotnet-backend",
            ),
            payload_file(
                ".ai/assets/tech-stacks/dotnet-backend/standard.md",
                "# Standard\n",
                "dotnet-backend",
            ),
        ]

        PACKAGE.validate_payload_user_view(closed, user_view_contract(code_reviewer=True))


if __name__ == "__main__":
    unittest.main()
