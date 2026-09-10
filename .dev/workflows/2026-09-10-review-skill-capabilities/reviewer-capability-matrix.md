# Reviewer Responsibility And Applicability

Issue: #289. Stable entry: `code-reviewer`.

| Responsibility | Authority and applicability | Coverage and conflict handling |
| --- | --- | --- |
| Common review | Supplied intent/contracts and common review method; every file partition | Correctness, failure, dependencies, relevant security and regression risk, test evidence, actionable findings. State unknown intent and unavailable specialist checks. |
| Architecture methods | Target-adopted DDD, CA, CQRS, event sourcing or other recorded decisions for the selected scope | Do not impose methods from the source framework or role name. Contradictory authority stops affected judgments pending owner resolution. |
| .NET extension | Explicitly selected and installed dotnet-backend; per-file technology and finding predicates | Retains 14 route IDs and applicable standards. Missing installation or rule authority blocks required .NET acceptance; common review cannot discharge it. |
| Target policy | Current target requirements, decisions and freshness-verified effective rules within their scope | Apply exact effective semantics. Never substitute defaults or another route when resolution fails; preserve customization reconciliation and source/target boundaries. |
| Other technologies | Common reasoning plus any explicitly supplied target-owned specialist extension | Report exactly which checks were performed. An unknown language or missing extension is not evidence of a clean specialist review. |

In mixed scope, partition by technology and apply only matching extensions.
Missing required coverage remains blocked even if common review finds no defects.
Review findings are separate from implementation, architecture revision and
formal compliance. Independent acceptance retains fixed-subject, author/reviewer
identity and applicable evidence requirements.
