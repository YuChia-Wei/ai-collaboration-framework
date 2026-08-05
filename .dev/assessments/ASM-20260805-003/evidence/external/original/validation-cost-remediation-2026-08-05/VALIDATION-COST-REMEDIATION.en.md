# Validation Aggregate Gate: Cost Audit And Remediation Specification

> Agent-facing version. Human-facing Traditional Chinese counterpart:
> `VALIDATION-COST-REMEDIATION.zh-TW.md`. Finding IDs, line numbers, and patch
> content are identical.

```yaml
audit_target: ".ai/scripts/check-all.sh"
target_lines: 692
subject_commit: "eaf00ae"
subject_branch: "main"
audit_date: "2026-08-05"
method:
  - "static parse of all run_*check invocations including line continuations"
  - "grep for cost-control keywords"
  - "direct execution of prerequisite paths"
related_issues: ["#75", "#96 VAL-002", "#95 EVAL-002", "#76"]
document_class: "external audit finding and implementation proposal"
authorization: "none — this document does not authorize execution"
```

## Instruction To The Implementing Agent

1. Patches 1 and 2 do not change any check's pass condition. Patch 3 changes what
   `--critical` enforces. Patch 4 is design scope only.
2. Never weaken fail-closed semantics. `blocked-by-environment` must remain a
   non-passing outcome with a non-zero exit code.
3. Do not apply Patch 3 with a global `sed`. The argument string
   `"required" "true" "true"` is identical across VALIDATOR and SELFTEST
   invocations; a global replace corrupts the classification.
4. Verify the caller inventory before Patch 3.

---

## Part 1 — Audit Findings

### V-01 — `--quick`, `--critical`, and `--full` are currently equivalent

```yaml
finding_id: V-01
severity: high
category: inert-configuration
```

Declared interface:

```
Usage: ./check-all.sh [--quick | --full | --critical]
  --quick    : Only run fast, critical checks
  --critical : Only run the most important checks
  --full     : Run all available checks (default)
```

Mode filter at lines 139–155:

```bash
select_check() {
    local description=$1
    local is_critical=$2
    local is_quick=$3
    if [ "$MODE" == "critical" ] && [ "$is_critical" != "true" ]; then
        ... return 1
    fi
    if [ "$MODE" == "quick" ] && [ "$is_quick" != "true" ]; then
        ... return 1
    fi
    return 0
}
```

Parsed inventory of every `run_check` / `run_command_check` /
`run_deferred_check` invocation, line continuations joined:

```
TOTAL invocations: 55
enforcement: {'required': 52, 'n/a': 3}
is_critical: {'true': 52, 'false': 3}
is_quick   : {'true': 52, 'false': 3}
```

All 52 `required` checks declare `is_critical="true"` and `is_quick="true"`. The
only three `false` declarations belong to `run_deferred_check`, which executes
nothing (it prints a DEFERRED line and returns).

**Conclusion:** all three modes execute the same 52 checks. The mode flags skip
nothing. `--critical` is not a fast subset.

> **Correction:** an earlier statement by this reviewer cited "27 checks". That
> number came from a line-anchored grep that missed indented invocations inside
> functions. The correct figures are 55 invocations, 52 executed. Use the figures
> in this document.

### V-02 — No cost-control mechanism exists

```yaml
finding_id: V-02
severity: high
category: missing-cost-control
```

Whole-file grep results, all zero matches:

```yaml
changed: 0
parallel: 0
cache: 0
timeout: 0
budget: 0
"git diff": 0
```

No changed-path selection, no parallelism, no cache or fingerprint, no per-check
time budget. All 52 checks execute sequentially.

### V-03 — Composition is dominated by framework self-tests

```yaml
finding_id: V-03
severity: medium
category: profile-composition
classification:
  SELFTEST: 35      # tests/test_*.py — validates the framework's own contracts
  VALIDATOR: 11     # validate-*.py — validates repository content
  DOTNET_TEST: 3    # requires restore + build
  OTHER: 6          # 3 of which are deferred no-ops
```

64% of executed checks are framework self-tests. By #75's own decomposition
these belong to a `framework-selftest` profile — selected for framework path
changes or source CI — not to every workflow handoff prerequisite.

The 3 `dotnet test` invocations (lines 297, 301, 305) are already guarded by
`source_release_context_available()` and report NOT APPLICABLE in packaged
downstream targets. That guard is correct. On the source development host they
run every time, each requiring restore and build.

### V-04 — Environment blocks are not distinguished from check failures

```yaml
finding_id: V-04
severity: high
category: agent-rework-cause
impact: "highest agent-facing impact of all findings"
```

`record_unavailable_or_failed()` at lines 176–184 collapses three distinct
conditions into one outcome:

```bash
record_unavailable_or_failed() {
    local enforcement=$1
    local description=$2
    if [ "$enforcement" == "required" ]; then
        echo -e "${RED}✗ FAILED${NC}: $description"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        REQUIRED_FAILED=$((REQUIRED_FAILED + 1))
    ...
```

Collapsed conditions:

1. the check genuinely does not pass — remediate
2. the script is missing or not executable — installation problem
3. the execution environment is unavailable: missing .NET SDK, no network,
   sandbox write denial, interpreter version mismatch — **remediate nothing**

The agent observes `✗ FAILED` in all three cases and begins remediating a
non-existent defect. This is the direct cause of rework and false-failure loops.

**The framework already owns the correct vocabulary but does not use it here.**
`software-development-orchestrator/skill.yaml` states:

> "Record each selected test level as passed, failed, **blocked-by-environment**,
> not-applicable, or deferred-with-owner. **Blocked-by-environment is never
> passed** ..."

`check-all.sh` has no `blocked-by-environment` outcome class.

### V-05 — No elapsed-time visibility

```yaml
finding_id: V-05
severity: medium
category: unmeasurable-cost
```

The summary block (lines 633–692) emits 11 counters and a completion timestamp,
but no per-check or total elapsed time. There is no way to answer which check
consumes the time. This is the concrete instance, in this script, of the
highest-severity finding `ASM-20260803-003` raised against itself.

---

## Part 2 — Remediation Specification

```yaml
patches:
  - id: 1
    name: "per-check timing instrumentation"
    behavior_risk: none
    timing: "immediately, safe before release"
  - id: 2
    name: "environment-blocked classification"
    behavior_risk: none    # adds an outcome class; does not relax fail-closed
    timing: "immediately, before or after release"
  - id: 3
    name: "make mode tiering effective"
    behavior_risk: "changes what --critical enforces"
    timing: "after v0.9.0 publication"
  - id: 4
    name: "--changed change-aware selection"
    behavior_risk: high
    timing: "VAL-002 design scope"
```

---

### Patch 1 — Per-check timing instrumentation (zero behavior risk)

Design constraints:
- does not alter any check's execution, pass condition, or exit code
- uses the bash builtin `SECONDS`; compatible with macOS bash 3.2 and Windows Git Bash
- integer-second resolution is sufficient to identify slow checks

#### 1-A: timing state — insert after line 137 (`NOT_APPLICABLE=0`)

```bash
NOT_APPLICABLE=0

# --- timing instrumentation (patch 1) ---
CHECK_TIMINGS=()
TOTAL_ELAPSED_START=$SECONDS

record_timing() {
    local elapsed=$1
    local description=$2
    local outcome=$3
    CHECK_TIMINGS+=("${elapsed}|${outcome}|${description}")
}
```

#### 1-B: `run_check()` — modify lines 185–218

```diff
 run_check() {
     local script_name=$1
     local description=$2
     local enforcement=$3
     local is_critical=$4
     local is_quick=$5
     shift 5
     local args=("$@")
     select_check "$description" "$is_critical" "$is_quick" || return
     record_selected "$enforcement"
+    local _t_start=$SECONDS
+    local _outcome="unknown"
 
     echo ""
     echo -e "${CYAN}▶ Running:${NC} $description"
     echo "  Script: $script_name"
     echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
 
     if [ -f "$SCRIPT_DIR/$script_name" ]; then
         if [ -x "$SCRIPT_DIR/$script_name" ]; then
             [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))
             if "$SCRIPT_DIR/$script_name" "${args[@]}" 2>&1; then
                 echo -e "${GREEN}✓ PASSED${NC}: $description"
                 PASSED_CHECKS=$((PASSED_CHECKS + 1))
+                _outcome="passed"
             else
                 record_unavailable_or_failed "$enforcement" "$description returned non-zero"
+                _outcome="failed"
             fi
         else
             record_unavailable_or_failed "$enforcement" "$script_name is not executable"
+            _outcome="unavailable"
         fi
     else
         record_unavailable_or_failed "$enforcement" "$script_name not found"
+        _outcome="unavailable"
     fi
 
+    record_timing $((SECONDS - _t_start)) "$description" "$_outcome"
     echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
 }
```

#### 1-C: `run_command_check()` — modify lines 220–244

```diff
 run_command_check() {
     local command_text=$1
     local description=$2
     local enforcement=$3
     local is_critical=$4
     local is_quick=$5
     select_check "$description" "$is_critical" "$is_quick" || return
     record_selected "$enforcement"
     [ "$enforcement" == "required" ] && REQUIRED_RUN=$((REQUIRED_RUN + 1))
+    local _t_start=$SECONDS
+    local _outcome="unknown"
 
     echo ""
     echo -e "${CYAN}▶ Running:${NC} $description"
     echo "  Command: $command_text"
     echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
 
     if (cd "$PROJECT_ROOT" && eval "$command_text"); then
         echo -e "${GREEN}✓ PASSED${NC}: $description"
         PASSED_CHECKS=$((PASSED_CHECKS + 1))
+        _outcome="passed"
     else
         record_unavailable_or_failed "$enforcement" "$description returned non-zero"
+        _outcome="failed"
     fi
 
+    record_timing $((SECONDS - _t_start)) "$description" "$_outcome"
     echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
 }
```

#### 1-D: summary — insert after line 664 (`Pass Rate`)

```bash
echo -e "Pass Rate: ${CYAN}${PASS_RATE}%${NC}"

# --- timing summary (patch 1) ---
TOTAL_ELAPSED=$((SECONDS - TOTAL_ELAPSED_START))
echo ""
echo -e "${MAGENTA}──── Elapsed By Check (slowest first) ────${NC}"
if [ ${#CHECK_TIMINGS[@]} -gt 0 ]; then
    printf '%s\n' "${CHECK_TIMINGS[@]}" \
        | sort -t'|' -k1,1nr \
        | head -15 \
        | while IFS='|' read -r secs outcome desc; do
              printf "  %5ss  %-10s %s\n" "$secs" "$outcome" "$desc"
          done
fi
echo -e "  ${CYAN}Total wall time: ${TOTAL_ELAPSED}s across $TOTAL_CHECKS selected checks${NC}"

# machine-readable line for EVAL-002 ingestion
echo "AI_CONTEXT_CHECK_TIMING total_seconds=${TOTAL_ELAPSED} checks=${TOTAL_CHECKS} failed=${FAILED_CHECKS}"
```

The final line is deliberately machine-readable so EVAL-002 can ingest it as an
`execution_record` field before its schema is finalized.

```yaml
patch_1_acceptance:
  - "./check-all.sh --full prints the 15 slowest checks with seconds"
  - "pass/fail determination and exit codes are byte-identical to pre-patch behavior"
  - "one greppable line matching AI_CONTEXT_CHECK_TIMING is emitted"
```

---

### Patch 2 — Environment-blocked classification (zero behavior risk)

**Non-negotiable design principle: fail-closed must not be relaxed.**

An environment block still fails the aggregate gate. Only two things change:

1. it is listed separately so an agent knows not to remediate code
2. exit code `3` signals "environment blocks only, no genuine failure"; exit `1`
   still signals genuine failure

CI must treat both `1` and `3` as not-passing. An agent seeing `3` prepares the
environment instead of editing code.

#### 2-A: counters and classifier — insert after the Patch 1-A block

```bash
# --- environment-blocked classification (patch 2) ---
BLOCKED_CHECKS=0
BLOCKED_LIST=()

# Classify output as environment-blocked rather than failed.
# Signatures are deliberately conservative: only unambiguous environment
# signals match. Prefer misclassifying as failed over masking a real failure.
classify_blocked() {
    local output=$1
    case "$output" in
        *"Python prerequisite blocked"*)        echo "python-prerequisite"; return 0 ;;
        *"No module named"*)                    echo "missing-python-module"; return 0 ;;
        *"unsupported-python"*)                 echo "unsupported-python"; return 0 ;;
        *"command not found"*|*"not recognized as an internal"*)
                                                echo "missing-command"; return 0 ;;
        *"No .NET SDKs were found"*|*"MSB1003"*|*"SDK not found"*)
                                                echo "missing-dotnet-sdk"; return 0 ;;
        *"NU1301"*|*"Unable to load the service index"*|*"Could not resolve"*)
                                                echo "network-unavailable"; return 0 ;;
        *"Read-only file system"*|*"Operation not permitted"*|*"Permission denied"*)
                                                echo "sandbox-restricted"; return 0 ;;
    esac
    return 1
}

record_blocked() {
    local description=$1
    local reason=$2
    echo -e "${YELLOW}⊘ BLOCKED-BY-ENVIRONMENT${NC}: $description ($reason)"
    BLOCKED_CHECKS=$((BLOCKED_CHECKS + 1))
    BLOCKED_LIST+=("${reason}|${description}")
}
```

#### 2-B: `run_command_check()` — capture output, then classify

```diff
-    if (cd "$PROJECT_ROOT" && eval "$command_text"); then
-        echo -e "${GREEN}✓ PASSED${NC}: $description"
-        PASSED_CHECKS=$((PASSED_CHECKS + 1))
-        _outcome="passed"
-    else
-        record_unavailable_or_failed "$enforcement" "$description returned non-zero"
-        _outcome="failed"
-    fi
+    local _out _rc _reason
+    _out=$( (cd "$PROJECT_ROOT" && eval "$command_text") 2>&1 )
+    _rc=$?
+    printf '%s\n' "$_out"
+    if [ $_rc -eq 0 ]; then
+        echo -e "${GREEN}✓ PASSED${NC}: $description"
+        PASSED_CHECKS=$((PASSED_CHECKS + 1))
+        _outcome="passed"
+    elif _reason=$(classify_blocked "$_out"); then
+        record_blocked "$description" "$_reason"
+        _outcome="blocked"
+    else
+        record_unavailable_or_failed "$enforcement" "$description returned non-zero"
+        _outcome="failed"
+    fi
```

> Capturing output defers progress display until the check completes. If live
> output must be preserved, use `tee` instead:
> ```bash
> _tmp=$(mktemp)
> (cd "$PROJECT_ROOT" && eval "$command_text") 2>&1 | tee "$_tmp"
> _rc=${PIPESTATUS[0]}
> _out=$(cat "$_tmp"); rm -f "$_tmp"
> ```
> `PIPESTATUS` is available in bash 3.2.

#### 2-C: `run_check()` — same structure

Apply the same capture-and-classify structure to the branch where the script
exists and is executable. Missing or non-executable scripts continue through
`record_unavailable_or_failed` — that is an installation problem, not an
environment block.

#### 2-D: summary and exit codes

Add to the counter block:

```bash
echo -e "Blocked By Environment: ${YELLOW}$BLOCKED_CHECKS${NC}"
```

Add after the timing table:

```bash
if [ ${#BLOCKED_LIST[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}──── Blocked By Environment (do NOT remediate code) ────${NC}"
    printf '%s\n' "${BLOCKED_LIST[@]}" | while IFS='|' read -r reason desc; do
        printf "  %-24s %s\n" "$reason" "$desc"
    done
    echo -e "  ${CYAN}These are host/runtime conditions. Prepare the environment, then re-run.${NC}"
fi
```

Exit block (lines 668–691):

```diff
-if [ $FAILED_CHECKS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
+if [ $FAILED_CHECKS -eq 0 ] && [ $WARNINGS -eq 0 ] && [ $BLOCKED_CHECKS -eq 0 ]; then
     ... All Checks Passed ...
     exit 0
-elif [ $FAILED_CHECKS -eq 0 ]; then
+elif [ $FAILED_CHECKS -eq 0 ] && [ $BLOCKED_CHECKS -eq 0 ]; then
     ... Passed with Advisory Warnings ...
     exit 0
+elif [ $FAILED_CHECKS -eq 0 ]; then
+    echo -e "${YELLOW}╔════════════════════════════════════════╗${NC}"
+    echo -e "${YELLOW}║  ⊘ $BLOCKED_CHECKS check(s) blocked by environment  ║${NC}"
+    echo -e "${YELLOW}╚════════════════════════════════════════╝${NC}"
+    echo ""
+    echo -e "${YELLOW}Next Steps:${NC}"
+    echo "1. Do NOT modify repository code for these."
+    echo "2. Prepare the host prerequisite listed above."
+    echo "3. Re-run. Exit code 3 means unverified, never passed."
+    exit 3
 else
     ... Checks Failed ...
     exit 1
 fi
```

```yaml
patch_2_acceptance:
  - "on a host without the .NET SDK, the 3 dotnet test checks report BLOCKED-BY-ENVIRONMENT (missing-dotnet-sdk), not FAILED"
  - "exit code is 3 and the summary states blocked is never passed"
  - "genuine check failures still report FAILED with exit code 1"
  - "CI configuration treats both 1 and 3 as not-passing (verify this separately)"
```

---

### Patch 3 — Make mode tiering effective (after v0.9.0)

```yaml
risk: "changes what --critical enforces"
prerequisite: "caller inventory"
```

#### 3-A: caller inventory (prerequisite)

```bash
git grep -n 'check-all\.sh' -- ':!.dev/workflows' ':!.dev/assessments'
```

Confirm that source CI and the release gate use `--full`, and only interactive
or handoff prerequisites use `--critical`. If source CI currently uses
`--critical`, change it to `--full` before applying this patch.

#### 3-B: proposed classification

| Class | Count | `is_critical` | `is_quick` | Rationale |
| --- | ---: | --- | --- | --- |
| VALIDATOR (`validate-*.py`) | 11 | `true` | `true` | validates actual repository content |
| Spec / Coding Standards (lines 276, 575) | 2 | `true` | `false` | content validation but slower |
| Git commit message (line 504) | 1 | `true` | `true` | fast and relevant to every commit |
| **SELFTEST** (`tests/test_*.py`) | 35 | **`false`** | **`false`** | framework's own contracts; needed for framework-path changes and source CI |
| **DOTNET_TEST** (lines 297, 301, 305) | 3 | **`false`** | **`false`** | requires restore+build; already source-context guarded |
| deferred no-op | 3 | unchanged | unchanged | executes nothing |

Post-patch, `--critical` executes roughly 14 checks instead of 52.

#### 3-C: judgment calls requiring owner confirmation

| Line | Check | Consideration |
| ---: | --- | --- |
| 471 | Workflow Handoff Fail-Closed Tests | cross-session handoff correctness; keep critical if handoffs are frequent |
| 467 | Git Commit Policy Fail-Closed Tests | relevant to every commit |
| 520 | AI Context Language And Bilingual Parity | relevant when documentation changes often |

#### 3-D: application method

Modify the 4th and 5th positional arguments per invocation. Example at line 451:

```diff
 run_command_check "python .ai/scripts/tests/test_assessment_artifacts.py -v" \
     "Assessment Artifact Fail-Closed Tests" \
-    "required" "true" "true"
+    "required" "false" "false"
```

**Do not use a global `sed`.** The string `"required" "true" "true"` is identical
across VALIDATOR and SELFTEST invocations. Apply line by line against the table
in 3-B.

```yaml
patch_3_acceptance:
  - "./check-all.sh --critical reports Skipped By Mode > 0"
  - "--critical and --full report different Total Checks Run"
  - "--full still executes all 52 checks; source CI and release gate use --full"
  - "the caller inventory result is recorded in the commit message or workflow evidence"
```

---

### Patch 4 — `--changed` change-aware selection (VAL-002 design scope)

**Design outline, not a directly applicable patch.** The real work is declaring
input paths per check.

#### 4-A: declare input paths

Store as data rather than hard-coding in shell:

```yaml
# .ai/scripts/check-input-paths.yaml
checks:
  - description: "Assessment Artifact Metadata"
    command: "python .ai/scripts/validate-assessment-artifacts.py"
    input_paths:
      - ".dev/assessments/**"
      - ".ai/assets/skills/ai-context-auditor/templates/**"
  - description: "Workflow Artifact Metadata"
    command: "python .ai/scripts/validate-workflow-artifacts.py"
    input_paths:
      - ".dev/workflows/**"
      - ".dev/standards/WORKFLOW-ARTIFACT-POLICY.md"
  - description: "Dotnet Backend Analyzer Template Tests"
    command: "dotnet test tools/DotnetBackendAnalyzers.Tests/..."
    input_paths:
      - "tools/DotnetBackendAnalyzers/**"
      - "tools/DotnetBackendAnalyzers.Tests/**"
```

#### 4-B: selection logic

```
--changed [<base>]     # base defaults to origin/main
```

1. `CHANGED=$(git diff --name-only <base>...HEAD)`
2. select a check when any of its `input_paths` intersects `CHANGED`
3. a check with **no** declared `input_paths` is **always selected** — failing
   open would break fail-closed, so undeclared means always relevant
4. the summary must print the list skipped as unchanged — silent truncation
   reads as full coverage when it is not

#### 4-C: inviolable constraints

- `--changed` must not be used by source CI or the release gate; those are always `--full`
- checks without declared input paths must never be skipped
- the skipped list must be visible and exit-code semantics unchanged

#### 4-D: relationship to VAL-002

VAL-002's `handoff_condition` currently reads:

> "Design profiles and changed-path semantics before editing check-all"

That constraint is correct for Patch 4 but **over-broad for Patches 1–3**:
timing output and environment classification change no check's pass condition,
and mode tiering repairs existing design rather than introducing new semantics.
Recommend recording an exception on VAL-002 so Patches 1 and 2 can proceed.

---

## Part 3 — Mapping To Online Issues

| This document | Issue | Relationship |
| --- | --- | --- |
| V-01, V-03, Patch 3 | #75 / VAL-002 (#96) | #75 identified the composition problem; V-01 supplies the concrete mechanism explaining why the mode flag is inert |
| V-05, Patch 1 | EVAL-002 (#95) | Patch 1's machine-readable line is the lowest-cost `execution_record` pilot |
| V-04, Patch 2 | #76 (environment readiness profiles) | Patch 2 is #76's runtime counterpart: #76 assesses the environment beforehand, Patch 2 classifies correctly afterwards |
| Patch 4 | VAL-002 (#96) | fully within VAL-002 design scope |

## Part 4 — Recommended Schedule

```yaml
before_v0_9_0_publication:
  - "apply Patch 1 — zero risk, and immediately yields real timing data from the v0.9.0 release gate run"
before_or_after_v0_9_0:
  - "apply Patch 2 — zero risk; verify CI handling of exit code 3 in the same change"
first_action_after_v0_9_0:
  - "run caller inventory, then apply Patch 3"
after_VAL_002_design:
  - "implement Patch 4"
sequencing_note: >
  Run Patch 1 before deciding the Patch 3 classification. The current
  classification is inferred from category. With real timing data the split can
  be ordered by measured cost, which may reveal that a VALIDATOR — not a
  self-test — is the slowest check.
```

---

*Audit target: `.ai/scripts/check-all.sh` @ `eaf00ae`. Date: 2026-08-05.*
