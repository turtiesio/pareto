# CONDITIONAL RECOVERY-QUOTIENT ANALYSIS R0.1H

## Scope and status

This analysis uses only:

- the frozen R0.1H seed; and
- POSTFREEZE-BREAK-R01H.md, the fresh break derived from that seed.

The seed hash was rechecked before this analysis:

    4954ed2a9612ea8a7e95041b689b549a1b9636e2d7457bf003d7d2c056958658

It matches the required SHA-256.

This document is conditional mathematical analysis. It is not a repair to the
seed, an architecture, a proposed representation, an implementation result, or
evidence about storage or recovery. It does not edit either input document.

The seed does not itself define equivalence at a recovery cut. To make the
question finite without silently choosing a storage shape, the main counts use
the following smallest explicit semantic repair and cut convention:

1. A recovery cut is immediately after the observable DOWN crossing and before
   SELECT and READY.
2. The oracle semantic condition retains the old residual, the new residual,
   and enough phase information to decide whether selection is applicable.
3. An interrupted ordinary request never completes after recovery.
4. The compared future suffix begins at this recovery cut. Crossings already in
   the prefix remain historical facts but are not emitted again.
5. No second crash is possible.
6. At least one ordinary message remains available when the maximally
   discriminating class count is stated. EXPLAIN is used as that message.

The consequences of removing item 6, including recovery after the third
message, are stated separately. The seed-wide exact count remains UNKNOWN
because the seed does not freeze this recovery-cut convention, remaining-depth
comparison, clean-gap selector behavior, or the post-STOP suffix.

## Reachable semantic-condition inventory

### Clean residuals

The residual domain is the full product:

    O in {U,0,1}
    P in {EMPTY,ID,NOT}
    G in {E0,E1}

so there are 3*3*2 = 18 clean residuals.

Four do not occur among the original fourteen prehistory-cut classes:

    (0,ID,E1)
    (0,NOT,E1)
    (1,ID,E1)
    (1,NOT,E1)

Each is nevertheless reachable in the supported future domain by starting from
the corresponding two-axis prehistory cut and changing the third axis with one
message. Thus every one of the 18 residuals can occur at a recovery cut.

Moreover, every condition counted below has a supported witness with one
ordinary message left for EXPLAIN. A missing three-axis residual costs one
future message to reach, the interrupted request costs a second, and EXPLAIN
costs the third.

### Interrupted non-ATTEMPT requests

There are eleven non-T request kinds and 18 source residuals, giving 198
source/request conditions whose input can cross before a crash.

Independent transition counting gives:

| Axis or request family | Changing | No-op |
|---|---:|---:|
| O0 and O1 | 24 | 12 |
| AI, AN, RI, RN, and D | 36 | 54 |
| E | 9 | 9 |
| Q, X, and K | 0 | 54 |
| Total | 69 | 129 |

“No-op” includes a failed precondition, an idempotent successful request, and a
read-only request. These cases have different failure-free reply bytes, but an
interrupted request is expressly forbidden from replying after recovery.
Consequently that reply distinction is not a recovery continuation.

### ATTEMPT phases

For each of the 18 residuals there are two interrupted T phases:

- pre-A: C:ATTEMPT crossed, A did not cross;
- post-A: both C:ATTEMPT and A crossed, but R did not cross.

This contributes 36 phase conditions. T changes no residual. In both phases
the interrupted transaction emits neither A nor R after recovery. The seed's
retry examples require this: the pre-A crash has only the retry's A, and the
post-A crash retains the already crossed A but emits no completion for the
interrupted transaction.

### FIN-pending and post-STOP

FIN can be pending over each of the 18 residuals, but its recovery continuation
does not use that residual: after READY it owes exactly one STOPPED completion.
All 18 source conditions therefore have one continuation class.

If a recovery cut is admitted after a crash following STOPPED, its residual is
terminal. It owes no further reply. This is one further condition/class.
Whether READY after such a crash belongs to the complete trace remains
unfrozen in the seed, so all totals including this class are conditional.

### Raw condition-type count

Using one abstract clean condition per residual, one condition per interrupted
source/request, both T phases, one FIN condition per source residual, and one
terminal condition gives:

    18 clean
    + 69 changing interrupted non-T
    + 129 no-op interrupted non-T
    + 18 pre-A T
    + 18 post-A T
    + 18 FIN-pending
    + 1 post-STOP
    = 271 condition types

This is not a count of concrete exact histories, controllers, or executions.
It is only the finite semantic-condition inventory being quotiented.

## Contract A: SELECT hidden, public May sets deduplicated

Contract A follows the seed's public projection. The labels old and new are
erased, equal traces are deduplicated, and only complete public continuation
sets matter.

### Active singleton classes

For a clean residual r, the post-cut continuation is the continuation from r.
An interrupted no-op has branches {r,r}, which deduplicate to {r}. Pre-A and
post-A T also have {r,r}, emit no interrupted completion, and have the same
future continuation.

Therefore all of the following merge for each r:

- clean recovery at r;
- every interrupted no-op non-T request at r;
- T interrupted before A at r;
- T interrupted after A at r.

There are exactly 18 such singleton classes.

### Active changing classes

For an interrupted changing request from r to s, with r not equal to s, the
public May continuation is the unordered set {K(r),K(s)}, where K is the
failure-free continuation behavior after READY. Request identity and branch
orientation disappear because the interrupted request never replies and
SELECT is erased.

The 69 directed changing conditions collapse to 45 distinct unordered residual
edges:

| Changed axis | Distinct unordered edges |
|---|---:|
| Observation | 18 |
| Program | 18 |
| Engine | 9 |
| Total | 45 |

There are 24 bidirectional edges represented by two directed request
conditions, and 21 one-way edges:

- six bidirectional 0-to-1 observation edges, one for each P,G;
- eighteen bidirectional program edges, the three edges of the program
  triangle for each O,G;
- twelve one-way U-to-0 or U-to-1 observation edges;
- nine one-way E0-to-E1 engine edges.

No pair changed on different axes can coincide.

### FIN and terminal classes

FIN-pending is one class because its future contains the owed STOPPED crossing
without another FIN crossing. Post-STOP is a separate terminal class because
it must not emit another reply.

### Conditional Contract-A count

With one ordinary message available and with the post-STOP recovery cut
included:

    18 singleton residual classes
    + 45 unordered changing-edge classes
    + 1 FIN-pending class
    + 1 post-STOP terminal class
    = 65 classes

The quotient of the 271 raw condition types has this multiplicity check:

| Class family | Number of classes | Raw-condition multiplicity |
|---|---:|---:|
| Singleton residual | 3 | 9 each |
| Singleton residual | 9 | 10 each |
| Singleton residual | 6 | 11 each |
| Bidirectional changing edge | 24 | 2 each |
| One-way changing edge | 21 | 1 each |
| FIN-pending | 1 | 18 |
| Post-STOP | 1 | 1 |

The raw total is:

    3*9 + 9*10 + 6*11 + 24*2 + 21 + 18 + 1 = 271

If the post-STOP crash does not create a recovery cut, the conditional total is
64 rather than 65.

### Why one EXPLAIN is complete

The exact EXPLAIN reply is injective in r=(O,P,G). For a singleton it returns
one residual-specific trace. For a changing condition it returns the two
residual-specific traces in an unordered deduplicated set.

Consequently:

- two different singleton residuals are separated by one X;
- a singleton and a doubleton are separated by one X;
- two different unordered residual pairs are separated by one X;
- no one-message or longer public future can recover orientation from the same
  unordered pair, because after hidden selection the future depends only on
  the selected endpoint.

Thus the 18+45 active count is exact under Contract A and the stated cut
convention, not merely an upper bound.

## Contract B: old/new label behavior is observable or required

Contract B is not the seed's public contract. The following is the smallest
label-preserving comparison: compare the label-indexed continuation map rather
than its deduplicated range.

For an interrupted request, this preserves:

    old -> K(r)
    new -> K(s)

including two distinct label obligations when r=s. It does not preserve request
identity, request reply bytes, or phase unless those change label behavior.

### Minimal label-interface variant

If a clean recovery has no selector obligation, the active classes are:

- 18 clean residual classes with no selector;
- 18 no-op classes with old and new both mapping to the same residual;
- 69 ordered changing-edge classes;
- one FIN-pending class;
- one post-STOP class.

With one X available:

    18 + 18 + 69 + 1 + 1 = 107 classes

The 271 raw condition types then check as follows:

| Class family | Number of classes | Raw-condition multiplicity |
|---|---:|---:|
| Clean residual | 18 | 1 each |
| Equal old/new residual | 3 | 8 each |
| Equal old/new residual | 9 | 9 each |
| Equal old/new residual | 6 | 10 each |
| Directed changing edge | 69 | 1 each |
| FIN-pending | 1 | 18 |
| Post-STOP | 1 | 1 |

The raw total is:

    18 + 3*8 + 9*9 + 6*10 + 69 + 18 + 1 = 271

One label choice followed by X distinguishes every two different ordered
pairs: choose a label on which the endpoints differ, then X identifies the
selected residual.

### Why the exact Contract-B count is UNKNOWN from the seed

The seed says that before an input only old is permitted and after a reply only
new is permitted. At a clean gap between one reply and the next input, both
descriptions apply relative to different requests. It also says SELECT may be
forced only at the “corresponding” fault barrier without defining a clean-gap
selector protocol.

At least three label-preserving clean-gap conventions are consistent with
parts of the text:

1. No selector at a clean gap. This gives the 107-class variant above.
2. Separate old-only and new-only clean phases. This gives:

       18 old-only + 18 new-only + 18 both-label no-op
       + 69 changing + FIN + terminal = 125

3. Both labels are accepted and collapse at a clean gap. Clean and interrupted
   no-op states then merge, giving:

       18 equal-pair + 69 changing + FIN + terminal = 89

The seed's deduplicated public Contract A makes these choices observationally
irrelevant. Contract B exposes exactly the distinction that the seed leaves
undefined. Therefore 107 is a useful minimal conditional count, not an exact
count licensed by the frozen seed; the unconditional Contract-B count is
UNKNOWN.

If Contract B additionally exposes request identity, crash-gap identity, or an
A-phase label from the manifest, further splits occur. None of those are
specified by the hypothetical label-only contract in the task.

## Minimized merger and collision search

### Clean versus interrupted no-op

At r=(U,EMPTY,E0), compare:

- a clean crash; and
- REPLACE ID interrupted after C and before R.

The latter is a failed-precondition no-op. Under Contract A both have the
singleton continuation {r}; X and every longer public future coincide. Under
the minimal Contract B variant, zero ordinary messages suffice to distinguish
the selector domain: no selector versus two required labels with equal
continuations.

All failed, idempotent, and read-only interrupted requests at the same residual
merge this way. No pending reply may be used to recover their identity.

### Reverse changing edges

Compare:

- AUTHOR ID interrupted from (U,EMPTY,E0), producing the hidden set
  {EMPTY,ID}; and
- RETIRE interrupted from (U,ID,E0), producing the hidden set {ID,EMPTY}.

Under Contract A these are the same class. One X produces the same two-element
May set, and no longer future can orient it.

Under Contract B the maps are reversed:

    first:  old -> EMPTY, new -> ID
    second: old -> ID,    new -> EMPTY

Selecting old and issuing X separates them in one ordinary message.

The same merger occurs for O1 from O=0 versus O0 from O=1, for AUTHOR NOT
versus RETIRE on EMPTY/NOT, and for REPLACE NOT versus REPLACE ID on ID/NOT.
There are exactly 24 such orientation mergers in Contract A.

### Same source, different new residual

AUTHOR ID and AUTHOR NOT interrupted from an empty-program residual have the
same old endpoint but different new endpoints. Contract A separates their
different unordered sets with one X. Contract B selects new and separates them
with one X. Hence no unintended merger remains once the endpoint set/map
differs.

### ATTEMPT before A versus after A

At a fixed r:

    pre-A:  C:ATTEMPT, crash
    post-A: C:ATTEMPT, A:TRY..., crash

From the recovery cut forward, both have old and new mapping to r, neither
emits an A or R for the interrupted transaction, and one X is identical.
They merge under Contract A and under the minimal label-only Contract B.

This is not a claim that their full histories are equal. The post-A prefix
already contains an immutable A crossing and the pre-A prefix does not.
Future-observable equivalence can merge their service continuations while the
capture/history responsibility retains the past difference.

### FIN-pending versus post-STOP

These do not merge. After READY, FIN-pending emits exactly one STOPPED and
post-STOP emits none. No ordinary message is needed to separate them. They also
do not merge with an active residual class: an active controller must itself
cross FIN before receiving STOPPED.

## What must survive a recovery boundary

“Survive” here is behavioral responsibility only. It says nothing about fields,
records, bytes, files, or ownership.

| Condition | Required continuation information |
|---|---|
| Clean active | The selected clean residual behavior. |
| Interrupted changing, before SELECT, Contract A | The unordered set of two possible residual continuations; orientation and request identity are irrelevant. |
| Interrupted changing, before SELECT, Contract B | The old/new-indexed residual continuation map; orientation is required. |
| Interrupted no-op, Contract A | No pending-request distinction beyond the singleton residual. It merges with clean recovery. |
| Interrupted no-op, minimal Contract B | The fact that both old and new labels are required survives until selection, even though both lead to the same residual. |
| Any interrupted ordinary request, after SELECT | Only the selected residual continuation remains relevant. The ordinary request identity and reply completion do not. |
| T before A | No A and no R obligation survives for the interrupted T. |
| T after A | No new A and no R obligation survives for the interrupted T. The already crossed A remains in the historical capture trace. |
| FIN-pending | The exactly-one STOPPED obligation survives until discharged. |
| Post-STOP | The terminal/no-more-reply condition must remain distinct from FIN-pending if recovery continues. |

### Pending ordinary completion

Pending ordinary completion must not survive as an owed R crossing. The seed is
explicit that an interrupted ordinary request receives no reply after recovery.
Emitting the old completion would violate the defined trace.

Before selection, a changing request still creates an old/new residual
responsibility. Under Contract B, even a no-op request creates label-availability
responsibility. Neither is an ordinary reply obligation. Once selection is
resolved, request identity can merge whenever the selected residual and the
special FIN/terminal phase agree.

### Crossed A

A crossed before the crash must survive as an immutable fact in the complete
boundary history used to count attempts. It need not survive as a service
continuation distinction: no future service output depends on pre-A versus
post-A, and replaying A would be wrong.

Thus the capture/history responsibility survives somewhere in the experiment,
while the recovery continuation quotient may merge the two T phases. If a
controller is allowed to inherit and branch on pre-cut capture-peer observations,
then its own state can distinguish the phases; the seed does not specify that
visibility. That is a controller-domain issue, not a service residual
requirement.

## Pre-selection versus post-selection cuts

The 65 and conditional 107 counts classify the fault barrier before SELECT.
After a branch has been selected but before READY:

- under Contract A, active continuation depends only on the selected residual,
  giving 18 active classes when X remains;
- under Contract B, it gives 36 active (label,residual) classes only if the
  selected old/new label remains part of the compared contract at that cut;
- if the label crossing is already in the excluded prefix, Contract B also
  reduces to the same 18 selected-residual continuations.

FIN-pending and terminal add two classes if both recovery-cut kinds exist.
The seed does not identify which side of SELECT “between-execution recovery
cut” denotes, another reason not to present one unconditional number.

## Remaining-depth effect

The one-message counts classify cuts with at least one ordinary submission
left. A recovery after the third allowed message has depth zero. Then residual
identity cannot be exposed before the mandatory FIN handshake:

- Contract A: all active singleton and doubleton conditions merge, leaving
  active, FIN-pending, and post-STOP: 3 conditional classes.
- Minimal Contract B: all no-selector clean residuals merge; all two-label
  interrupted maps have the same label-indexed STOP continuation; with FIN and
  post-STOP this gives 4 conditional classes.
- With phase-explicit old-only, new-only, and both-label domains, Contract B
  gives 5 conditional classes.

If Contract B treats an unobservable selected residual identity as an
intensional requirement, it is no longer future-observable equivalence and
these depth-zero mergers need not occur. The task's “observable/required”
wording does not choose between extensional and intensional comparison.

The original seed equivalence always starts at a clean prehistory cut with a
fresh bound of three; it does not say whether a newly defined recovery-cut
equivalence resets the bound or inherits the remaining allowance. Therefore
classes at different remaining depths cannot be summed into one exact seed
quotient.

## Conditional counts and final verdict

| Recovery-cut contract | At least one message remains | Zero messages remain | Seed-wide exact verdict |
|---|---:|---:|---|
| A, hidden labels, pre-SELECT, post-STOP included | 65 | 3 | UNKNOWN |
| A, same but no post-STOP recovery cut | 64 | 2 | UNKNOWN |
| B, minimal no-selector clean convention | 107 | 4 | UNKNOWN |
| B, old-only/new-only clean phases | 125 | 5 | UNKNOWN |
| B, both labels collapse at clean gaps | 89 | 3 | UNKNOWN |

The robust results independent of representation shape are:

1. all 18 clean residual behaviors are reachable;
2. interrupted non-T conditions divide into 69 changing and 129 no-op cases;
3. hidden deduplicated May semantics turns the 69 directed transitions into 45
   unordered edges;
4. preserving old/new mapping retains all 69 directed edges;
5. pending ordinary R completion must not survive recovery;
6. FIN's STOPPED obligation must survive;
7. pre-A and post-A T have the same future service continuation, while the
   already crossed A must remain in the historical capture trace;
8. one X is a complete fingerprint of every residual singleton, unordered
   pair, or label-indexed pair when one message remains;
9. no single exact recovery-quotient count follows from the seed until cut
   placement, remaining depth, clean-gap selector behavior, controller access
   to A, and post-STOP trace completion are frozen.
