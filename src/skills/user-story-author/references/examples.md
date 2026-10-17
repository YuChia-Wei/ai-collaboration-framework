# Fictional local examples

These are illustrative supplied facts/decisions for this page, not online work
items, executed acceptance or real project requirements. Local labels have no
provider identity. Each example separates fields and carries its own handoff.

## Functional user-value

Supplied accepted input: warehouse staff need to find a shipment using its supplied
reference; no matching shipment must show a no-match message. Data-entry rules are
not settled. Local source: example brief V1, accepted fictional intent.

**Title:** Find a shipment by reference

**Description:**
- **User Story:** As warehouse staff, I want to find a shipment by its reference so
  I can answer a shipment-status enquiry.
- **Background (As-Is / Why):** Staff receive enquiries containing references;
  current lookup method is unknown. The supplied goal is answering the enquiry.
- **User Scenarios:** Staff start a lookup when receiving an enquiry, enter its
  reference and see matching shipment status; no match produces a no-match message.
- **Functional Requirements:** Show status for a matching reference; show a
  no-match message otherwise. No FR ID was supplied.
- **Scope:** Reference lookup and its two supplied outcomes; editing shipments excluded.
- **Open Questions:** Permitted reference format is unknown; input validation wording
  depends on that decision.

**Acceptance Criteria:**
- AC-A (supplied local label): Given a matching reference, when staff search,
  then the matching shipment status is displayed.
- AC-B (supplied local label): Searching an unmatched reference displays a no-match message.

**Handoff:** Source example brief V1; accepted fictional scope above. No parent or
external dependency is established. Next: owner resolves reference format; current
authority is drafting only. Existing GWT and prose AC remain in their supplied forms.

## Business-rule

Supplied accepted input: a room booking is checked on submission; overlapping
bookings are rejected, non-overlapping bookings continue through the existing flow.
BR-A is a supplied local label. Source: fictional booking rules V1, accepted.

**Title:** Prevent overlapping room bookings

**Description:**
- **Objective:** Help booking staff avoid allocating the same room twice.
- **Background:** The brief identifies overlapping requests as the problem;
  current incident frequency is unknown.
- **Expected Behavior:** Check on submission; reject overlap with an overlap message;
  non-overlap continues through the existing booking flow.
- **Business Rules:** BR-A applies to requests for the same room with overlapping
  intervals. Effective period and touching-endpoint semantics are unknown;
  no priority or exceptions were supplied.
- **Scope:** Overlap decision and message; changing the rest of booking flow excluded.
- **Open Questions:** Owner must decide whether adjacent intervals overlap; boundary
  AC cannot be finalized before that decision.

**Acceptance Criteria:** A request overlapping an existing booking for the same
room is rejected with an overlap message. A non-overlapping request continues
through the existing booking flow. Endpoint-boundary acceptance remains unresolved.

**Handoff:** Booking rules V1, accepted fictional input; no provider/parent ID.
Dependency: existing booking records (source states their use, interface unknown).
Next: booking-rule owner decides endpoint semantics; authority is draft only.

## Technical

Supplied accepted input: file-export owners need streaming so an export does not
require buffering the complete file; output bytes and supported callers stay the
same. Source: fictional export constraint V1. No performance threshold supplied.

**Title:** Stream exports while preserving the exported content

**Description:**
- **Technical Objective:** Let export owners process files without complete-file buffering.
- **Current State and Problem:** The brief states complete-file buffering is required
  today; no measured memory profile is supplied.
- **Expected Outcome:** Complete-file buffering is unnecessary; outward bytes and
  supported calling behavior are preserved. Peak-memory threshold is unknown.
- **Technical Requirements and Constraints:** Preserve export content and callers;
  no TR ID, version, architecture or deployment choice was supplied. Incremental
  streaming is a proposed approach, not an accepted implementation.
- **Scope:** Export buffering behavior; content-format changes excluded.
- **Open Questions:** Owner selects any required memory threshold and comparison evidence.

**Acceptance Criteria:** Export content is byte-for-byte equal for the same accepted
input. Supported callers retain their existing observable behavior. Export processing
does not require the complete file in memory. These are supplied prose technical AC;
no forced Gherkin conversion or test-level selection occurs.

**Handoff:** Export constraint V1, accepted fictional input. Dependency: existing
export contract, exact version unknown. Next: owner supplies that contract before
dependent implementation. Authority is draft only; no implementation/test execution claim.

## Bounded research using the technical template

Supplied accepted input: the search owner wants evidence on whether prefix indexing
is suitable. Investigation is limited to one provided synthetic corpus; no timebox
was supplied. Source: fictional investigation brief V1, accepted research scope.

**Title:** Establish evidence for a prefix-index decision

**Description:**
- **Technical Objective:** Answer whether prefix indexing meets the search owner's
  needs for the supplied synthetic corpus; benefit is an informed decision.
- **Current State and Problem:** No comparison evidence is supplied; production
  suitability cannot yet be concluded.
- **Expected Outcome:** A comparison report with observations, limitations and a
  recommendation; no production deployment promised.
- **Technical Requirements and Constraints:** Use the one provided corpus; measurement
  method is proposed for owner confirmation. Time bound is unknown. Proposed stopping
  criterion: report the selected comparison and its limits, or a documented blocker.
- **Scope:** One corpus and comparison; production rollout and generalization excluded.
- **Open Questions:** Search owner confirms measurement method/stopping criterion and
  any timebox before dependent experimentation.

**Acceptance Criteria:** Report answers the learning question with evidence references
and limits, or explains why it remains unanswered. Observations and recommendations
are distinguished. This is proposed acceptance for owner decision, not research success.

**Handoff:** Investigation brief V1; proposed acceptance/stopping criterion explicitly
unaccepted. Corpus delivery is a dependency. Next: search owner confirms method and
criteria; current authority is research planning only.

## Overlarge counterexample and slicing

“Improve all booking operations, make everything fast and deploy it” leaves the
beneficiary, observable outcome, scope, thresholds and authority unresolved.
Creating Epic/Feature/Story/Task shells or separate Issues for design/code/test does
not resolve those gaps. Ask which booking outcome matters and what evidence exists.

If the supplied priority is preventing room overlap, propose the independently
observable overlap-decision Story above first. A separate cancellation outcome
can be another proposed Story only when its beneficiary, rules and acceptance are
supplied. Shared booking-data dependencies determine sequencing. Implementing a
check and its UI message are Tasks within the overlap Story when they have no
independent delivery value. If speed is still an open question, propose bounded
measurement research with an owner-confirmed question and stopping criterion;
do not fabricate a latency target, deadline or deployment approval.
