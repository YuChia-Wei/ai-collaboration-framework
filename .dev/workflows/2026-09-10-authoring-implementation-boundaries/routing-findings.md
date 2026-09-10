# Initial Routing Findings And Remediation

Subject: `6655b3510e0e536e5e5216b4989ff282241e0a57`.
The [initial observations](initial-observed-results.json) preserve both actual
Luna operations and the parent grade. Tool completion passed; semantic acceptance
did not pass every facet. Both baseline and current selected the expected
immediate owner in 19 of 20 cases, with four cases containing unnecessary
handoff declarations. Neither version performed actual scope expansion or
bypassed missing authority. No improvement is claimed from that comparison.

- R276-001 (A01/A06): conditional future policy approval or requirement
  formalization appeared under necessary handoffs although the requested draft
  can finish with open facts. The shared authoring contract now distinguishes
  completion dependencies from optional future work and states that another
  authoring skill cannot manufacture stakeholder authority.
- R279-001 (I06): baseline introduced an unrequested requirement-author stage;
  current chose orchestration because the request crossed services, despite
  a concrete missing semantic/compatibility decision. The implementation
  contract now prioritizes that decision's architecture owner and does not
  treat module count as sufficient orchestration justification.
- R279-002 (I10): a diagnosis-only request named a future slice repair as a
  necessary handoff before a causal finding established repair scope. The
  implementation contract now keeps that option conditional and does not
  preselect local/slice ownership before target and radius are known.

The implementation worker used its scope_expansion field for risks it prevented.
Parent grading read the actual output, rationale and authority gates; those
risk strings are not counted as performed expansion. I05's architecture-first
route with conditionally gated implementation remains valid for the requested
interface-extraction goal.

Only the two shared contracts change for this remediation. A bounded recheck
will cover A01/A06 and I05/I06/I09/I10 with explicit immediate-owner, required
handoff, optional-future-work, actual-expansion and prevented-risk fields.
It is feedback-informed verification, not a new blind or full-corpus trial.
Original outputs and metrics remain unchanged. Final acceptance is pending.
