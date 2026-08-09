# LESSON-ENV-001: WSL Non-Interactive .NET CLI PATH Availability

> This lesson is non-normative. It records one confirmed environment incident
> and does not change runner, classifier, release, or environment-readiness
> behavior.

| Field | Value |
| --- | --- |
| Lesson ID | `LESSON-ENV-001` |
| Category | `environment` |
| Lifecycle | `active` |
| Normative Authority | `none` |
| Origin Evidence | [Issue #163](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/163), [v0.11 completion report](../../workflows/2026-08-09-v0-11-product-boundary-delivery-evidence/reports/completion-report.md), and [V011-CLOSEOUT task](../../workflows/2026-08-09-v0-11-product-boundary-delivery-evidence/tasks/V011-CLOSEOUT.json) |
| Evidence Subject | `main@29a36934f172fa61bd3a2abf1d9d96dad2479f40`; `Ubuntu-24.04`; evidence summary `validation-v011-release-wsl-29a369-20260809/20260809T044038Z-288/evidence-summary.json` |
| Promotion Target | `none` |
| Supersedes | `none` |
| Superseded By | `none` |

## Origin Evidence

- [Issue #163](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/issues/163)
  preserves the owner-confirmed host, shell comparison, repair, and scope
  boundary for this lesson.
- The [v0.11 completion report](../../workflows/2026-08-09-v0-11-product-boundary-delivery-evidence/reports/completion-report.md)
  and [V011-CLOSEOUT task](../../workflows/2026-08-09-v0-11-product-boundary-delivery-evidence/tasks/V011-CLOSEOUT.json)
  are the current durable sources for the final fresh-login WSL release result.
- [The validation profile registry](../../../.ai/scripts/validation-profile-registry.sh)
  records the three checks as direct `dotnet test` commands. [The aggregate
  runner](../../../.ai/scripts/check-all.sh) records child-shell execution and
  environment-block classification semantics.
- [PR #158](https://github.com/YuChia-Wei/ai-collaboration-prompts-dotnet-backend/pull/158)
  separately repaired offline-uv fixture portability. Its defect and outcome
  are not evidence of the shell/PATH cause described here.

The named evidence-summary JSON is an execution artifact identity recorded by
the completed workflow; it is not copied into this lesson. Earlier failed and
blocked attempts remain truthful historical evidence.

## Context And Symptom

On the observed Windows host, WSL commands invoked inside the Codex sandbox
returned `Wsl/Service/E_ACCESSDENIED`; WSL diagnostics therefore ran outside
the sandbox. The relevant distribution was `Ubuntu-24.04`.

During v0.11 closeout, an earlier temporary-clone WSL release profile selected
52 checks and reported `passed=48`, `failed=1`, and `blocked=3`. The three
blocked checks were:

- `dotnet-analyzers`;
- `dotnet-validation`;
- `dotnet-building-blocks`.

They were reported as `blocked-by-environment` with reason
`missing-dotnet-sdk`. A separate aggregate-runner fixture portability failure
also existed and was later fixed by PR #158. The fixture failure and the three
PATH-related blocks were distinct problems.

The owner confirmed that `.NET` worked from the normal interactive WSL shell.
The diagnostic comparison then showed:

- `bash -ic 'dotnet --info'` succeeded;
- the mechanical fresh-login/non-interactive route initially could not resolve
  the same CLI.

Host installation and interactive availability therefore did not establish
availability inside the exact validation process.

## Confirmed Conditions And Root Cause

The [profile registry](../../../.ai/scripts/validation-profile-registry.sh)
registers the three checks as direct `dotnet test` text commands. The
[aggregate runner](../../../.ai/scripts/check-all.sh) executes registered text
commands through a child `bash -c` and inherits the runner environment.

The runner maps either of these output patterns to `missing-dotnet-sdk`:

```text
dotnet: command not found
No .NET SDKs were found
```

In this incident, `missing-dotnet-sdk` meant that the CLI or SDK was unavailable
to that process. It did not prove that `Ubuntu-24.04` had no SDK installed.

The confirmed root cause was different shell startup and `PATH` state. The
interactive shell could resolve `dotnet`; the fresh-login/non-interactive
validation route could not. The durable host correction created
`~/.bash_profile`, sourced `~/.profile`, and explicitly exported the directory
containing the already working `dotnet` executable.

The comparison was run from Windows PowerShell outside the sandbox:

```powershell
wsl -d Ubuntu-24.04 -- bash -lc 'echo LOGIN-NONINTERACTIVE; whoami; echo "$HOME"; command -v dotnet; type -a dotnet; dotnet --info; echo "$PATH"'
wsl -d Ubuntu-24.04 -- bash -ic 'echo INTERACTIVE; whoami; echo "$HOME"; command -v dotnet; type -a dotnet; dotnet --info; echo "$PATH"'
```

## Reusable Conclusion

Successful CLI resolution in an interactive WSL shell is evidence for that
shell only. It does not establish readiness for a child process, login shell,
non-interactive automation, service, or validation runner with different
startup files and inherited environment.

For a similar symptom, comparing `command -v`, `type -a`, `dotnet --info`,
`HOME`, and `PATH` in the working interactive shell and the exact automation
route isolates process-environment divergence without assuming that the SDK is
absent from the distribution.

Changing deterministic automation to `bash -ic` would make it depend on
interactive startup behavior. The confirmed resolution instead made the CLI
available to an explicit fresh-login/non-interactive environment.

## Non-Applicable Cases

This conclusion does not establish the cause when:

- `dotnet` fails in both interactive and non-interactive shells because no
  compatible CLI or SDK is installed;
- `dotnet` resolves but reports that no SDKs are installed;
- `dotnet` resolves and the command then fails because of project, test,
  network, permission, or repository defects;
- the failing environment is native Windows, a container, CI, or another shell
  with different startup semantics;
- WSL itself cannot be invoked because the caller is inside the Codex sandbox;
  `Wsl/Service/E_ACCESSDENIED` is a separate execution boundary;
- a synthetic fixture restricts `PATH` intentionally, as in the distinct PR
  #158 portability defect.

The runner's `missing-dotnet-sdk` reason remains a process-level classification
and is unchanged by this lesson.

## Remediation Example

The following command records the repair used from the interactive WSL shell
where `dotnet` already resolved:

```bash
dotnet_dir="$(dirname "$(type -P dotnet)")" &&
printf '%s\n' \
  'if [ -f "$HOME/.profile" ]; then' \
  '    . "$HOME/.profile"' \
  'fi' \
  "export PATH=\"$dotnet_dir:\$HOME/.dotnet/tools:\$PATH\"" \
  > "$HOME/.bash_profile"
```

This is an environment-specific evidence example, not portable repository
configuration. It overwrites `~/.bash_profile`; another host may need to review
and merge existing profile content, use a different shell startup file, or
select another installation directory. The repository does not store the
resulting personal profile.

## Verification

Fresh-login CLI verification used:

```bash
bash -lc 'command -v dotnet && dotnet --info'
```

The final fresh-login WSL release profile then reported:

```text
selected=52
executed=52
reused=0
passed=52
failed=0
blocked=0
```

The SDK was `10.0.302`, the evidence subject was
`29a36934f172fa61bd3a2abf1d9d96dad2479f40`, and the recorded summary name was:

```text
validation-v011-release-wsl-29a369-20260809/20260809T044038Z-288/evidence-summary.json
```

This terminal result superseded the earlier WSL attempts for closeout
selection. It did not relabel the earlier missing-SDK, fixture portability, or
aggregate-runner evidence as passed.

## Promotion And Supersession

The lesson remains `active` with no promotion target and no successor.

Possible future ownership changes remain outside Issue #163:

- a maintained human troubleshooting procedure would belong in an
  implementation guide;
- a mandatory release operation would belong in a runbook;
- different classifier semantics, environment-readiness behavior, or automated
  enforcement would need separately authorized policy or validator work.

This lesson is not authorization for any of those changes.

## Security And Portability Boundary

Reusable evidence is limited to the shell/process distinction, diagnostic
comparison, classifier nuance, confirmed correction shape, and final
verification. The distribution name and SDK version identify the observed
environment; they are not framework requirements.

Personal profile bytes, hostnames, credentials, private endpoints, secrets,
and mutable machine-readiness state are excluded. The host-specific
`~/.bash_profile` content remains a confirmed remediation example rather than
portable repository truth.
