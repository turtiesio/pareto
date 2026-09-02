# FEASIBILITY AUDIT R0.1D — POST-FREEZE COLLISIONS AND DELETIONS

## 0. Frozen authorities and verdict

This audit treats the following bytes as immutable:

| artifact | commit | SHA-256 |
|---|---|---|
| `REALIZATION-CORRECTION-R01D.md` | `ec1cd939d335789a9a36766492740731d7f69cbd` | `b07fd627b4d75c9c069e791139e3b8233b3b0b95a33dd642bb83353c4aa4079c` |
| `R01D-HISTORY-CORPUS.json` | `a3ebef18c2b5ee60f467d3b3e7b2cba55f8d26af` | `fc8ac76f03361f7757172df5897f0567916ad6d6e9bd608506137ef942f31d72` |
| `r01d_collision_search.py` | `a3ebef18c2b5ee60f467d3b3e7b2cba55f8d26af` | `56a4bdbad929e6c4ede397f2c159b4baf5717e5187c13323872bc769f01f7f2c` |

The candidate file is unchanged by the later corpus commit.  The breaker and
mechanical audits were read-only.  Prior conclusions are not repaired in
place.

Verdict:

```text
R01D = CONTRACT_DEFECT_UNDECIDABLE
S_READY = ABSENT
R_READY = ABSENT
P_READY = ABSENT
IMPLEMENTATION / SUBJECT / LAB TRIAL = PROHIBITED
```

R0.1D is not a fixpoint.  Some R0.1C collisions are genuinely repaired, and
the bounded corpus finds a smaller sound projection in its declared domain.
Neither fact closes the exact semantic gate: several admitted histories remain
unserializable or non-total, several required gate artifacts are not byte-
constructible, and several persisted responsibilities can still be deleted.

## 1. Bounded automatic collision search

The external research instrument enumerates 53 histories in 23 independently
conditioned families, one declared future per family, 32 candidate extractors,
four representations, and three untagged-merge attacks.  It compares every
history pair within a family, forms the future-answer quotient, searches for
representation collisions, minimizes witnesses by event difference/encoded
size, and follows a deletion path that removes rebuildable/internal extras
before retesting every survivor.

The reproducible invocation is:

```text
python3 zero-ground-restart/r01d_collision_search.py
```

At the frozen inputs it reports:

| candidate | extractors | distinguishable-history collisions |
|---|---:|---:|
| `R01D_RESPONSIBILITIES` | 17 | 0 |
| `OVERCOMPLETE` | 32 | 0 |
| `LEGACY_HASH_AND_RECOMPUTE` | 15 | 14 |
| `DERIVED_ONLY` | 12 | 14 |

The smallest legacy/derived collision is the one-event readiness witness:
absence of `S_READY` denies implementation while its occurrence authorizes it.
Both hash/derived projections encode the histories identically.

On the preferred deletion path, all 15 extras delete and the search stops at
the 17 responsibility extractors.  Deleting any one of those 17 produces a
stored minimized collision.  Twelve extras are functionally determined in the
searched rows and are classified MAY REBUILD; three internal values vary while
all declared futures stay equal and are classified MAY FORGET.  All three
untagged merges collapse a distinction: S versus R authorization, checkpoint
versus measurement, and semantic versus realization target.

This is a real bounded negative/positive result, not an architecture proof.
Family conditioning, hand-declared futures, extractor code, manually declared
derived values, greedy deletion order, and witness ordering are research TCB.
Cross-family continuations, fresh domains, physical realizations, cognition,
global minimality, and uniqueness are explicitly outside the search bound.
Sections 4 and 5 show hidden counterexamples that the passing corpus did not
contain.

## 2. Nonconstructible semantic and gate obligations

### D1 — provider request has incompatible exact schemas

The inherited exact provider request contains `run_id:text`.  R0.1D sections
8.3 and 9.3 say the provider receives `run_key`, but the selector replacement
does not replace this non-selector wire and no full provider-request
replacement is given.

Two implementations can therefore emit byte-distinct requests under the same
semantic target.  `S_D` cannot decide which is required.  A successor must
freeze one full wire, for example the profile tag plus a closed TV map of the
32-byte direct key and 32-byte source-stream check hash, and reject `run_id`
and every extra member.

### D2 — PREFLIGHT failure cannot name successor relations

R0.1D claims 39 P relations: the 26 lifted archive rows followed by 13
successor P rows.  The inherited failure payload restricts
`failed_relation_index` to `0..25`.  A first failure in positions `26..38`
has no legal frame even though the success frame claims all 39 passed.

The replacement must define range `0..38`, exact index-to-ID order, and the
closure reserve over every failure carrier.  The successor P suffix in byte
order is C01, C02, C03, C04, C05, C06, C08, C09, C10, C12, C13, C14, C23.

### D3 — the derived semantic projection is not byte-constructible

`D_D.measurement_registry_delta` gives conceptual edits rather than the exact
ordered RFC-6901 pointer/value operations.  It does not freeze the full JSON
value of `replay_selector_record`, whether `run_key` is inline or referenced,
or the exact ordered replay-consistency string list.  Multiple canonical JSON
byte strings satisfy the prose.

Because two decoders are required to reproduce byte-identical `D_D`, `S_D`
cannot close.  The honest current value is UNSPECIFIED until a complete literal
operation list, selector schema, and rule-string list are frozen.

### D4 — successor attacks are descriptions, not executable relations

The 23 rows provide small natural-language pairs, but not closed base values,
candidate mutations, exact serialized requests, injection controls, expected
response bytes/reasons, or cleanup transitions.  The digest double does not
even select its fixed 32 bytes.  C01, C06, C12, C14, C21, and the behavioral
rows admit many incompatible implementations.

They are valid attack obligations but cannot count as S/R/P executions.  The
external research corpus cannot fill the gap because R0.1D correctly excludes
it from semantic identity and gate closure.  Until each relation receives a
frozen carrier and invocation semantics, the claimed 39-relation PREFLIGHT is
UNSUPPORTED.

### D5 — one lifted archive base uses an undefined carrier member

The lifted raw-prefix attack introduces `source_terminal_observed` only in the
prose lift.  Its base shape and relation to the candidate record are not
defined.  At minimum the carrier must independently contain byte `52`,
`missing_suffix=true`, stop execution, and
`source_terminal_observed=false`; the mutation may then change only the
Boolean.  Without the independent fact, rejection invents the very terminal
observation the attack is meant to test.

The lifted semantic-member-duplication base likewise needs to say that its
repeated path is derived from position zero of the effective path list before
the old `{bytes,mode,path}` mutation is built.

### D6 — postlaunch corrupt-provider outcome is unreachable

R0.1D requires the controller to exact-compare the acquired view with sealed
bytes before replay launch.  Any corrupt provider view therefore fails
prelaunch.  The same contract requires a postlaunch branch in which replay
reads corrupt bytes, returns well-formed `FAIL(H')`, and produces code 6 with
exit zero.  Both cannot occur under one provider path.

The smallest corrupt byte is classified before launch by the first rule and
after launch by the second.  A successor must choose: validate only capability
association before launch and let replay perform the sole content read, or
retain full prelaunch comparison and delete the postlaunch branch/C05.

### D7 — promised equal-digest rejection evidence has no carrier

Section 1.2 says the existing binding, unequal new target, and attempted
association remain distinguishable attack evidence.  The logical store keeps
successful target rows/runs only, while failed S/R attempt internals may be
forgotten.

```text
h0: exact target A exists
h1: A exists; unequal B with the same digest is attempted and rejected
```

Both leave identical persistent state, contrary to the promised later attack
evidence.  Either a rejection crossing/record with exact B and association is
MUST SURVIVE, or the contract must narrow the future interface so an ordinary
reset rejection has no later query and only frozen collision-test carriers
remain evidence.

### D8 — the S bootstrap exception omits machinery S requires

The pre-S exception authorizes two decoders and a minimal membership writer.
`S_D` itself requires closed-scope launching, codecs, exact comparisons,
cleanup, atomic durable insertion, recovery, and authorization control.  If
those components cannot be authored, the gate deadlocks; if ambient machinery
supplies them, its state/authority and TCB are externalized.

A successor must enumerate the complete bootstrap S apparatus and constrain it
to nonauthorizing gate work, while continuing to prohibit target realization
implementation until the occurrence exists.

## 3. Boundary-totality and externalization collisions

### D9 — cleanup and result emission have no deadline transition

The deadline covers replay cleanup/reset, outcome crossing/EOF, and PREFLIGHT
result crossing.  The one-turn failure/deadline/action rule covers none of
those phases.  Inherited prose also permits precharged serialization to finish
after the deadline.

Minimal cleanup witness: identical valid response, stderr EOF, and exit zero,
with cleanup ready when the clock first equals the deadline.  Cleanup-first
yields valid response; clock-first yields time bound.  With one result byte or
only result EOF remaining, the same ambiguity becomes success, timeout, or an
unsupported prefix.  For PREFLIGHT, that changes whether primary launch is
authorized even though all invocations already passed.

### D10 — ready-token EOF races child exit

```text
h0: child exits 127 without a ready token
h1: child writes the complete token, closes it, then exits 127 before poll
```

The generic turn prioritizes an already-observed failure over the readiness
action, merging both as precommit launch failure with no exit.  Validating the
buffered token/EOF first makes `h1` postcommit and requires a truthful exit
record.  No clause orders these simultaneously ready observations.

A two-way acknowledged commitment or a phase-specific drain/exit precedence
is needed; merely naming the token does not totalize the race.

### D11 — successful provider reads may leave hidden persistent state

Reset-equivalence, including timing, is exact for a completed provider-
**failure**.  “Cleanup and reset” is merely named for success.

```text
h0: exact provider read leaves a cold shared cache
h1: same exact view and PASS, but a persistent DB/CAS cache becomes warm
future: a later run with a deadline between cold and warm latency
```

The future fails after `h0` and succeeds after `h1`.  Either all completed
provider invocations must restore future-equivalent state, or the cache fact is
additional MUST SURVIVE information.

### D12 — failed parser and S activity can externalize state

A failed locator invocation or failed S attempt may append no locator or
membership while mutating a cache, file, service, authorization state, or
deadline-relevant resource.  A later allowed invocation can distinguish the
mutation.  Unlike provider failure, these paths have no general transactional
reset-equivalence requirement.

The rule must apply to every closed apparatus invocation, success and failure,
or its future-visible side effects must cross and survive.

### D13 — channel begin is not atomic with the stored empty crossing

Absent crossing position means “never began”; a present empty crossing means
“began, no byte accepted.”  No `RUN_BEGIN` operation requires insertion of
positions 1 or 2 before the corresponding endpoint or side effect is opened.

Crash immediately before open and crash immediately after open/before append
can therefore leave the same durable run row while later endpoint/cleanup
observation distinguishes them.  Successful atomic insertion of the empty
crossing must itself be the begin occurrence and precede every channel side
effect.

### D14 — crossings do not derive every live phase

After a closed replay request and before outcome start, one run may be before
provider acquisition while another is postcommit with process-request bytes
written.  Both can have identical closed crossings 0/1 and absent crossing 2.
A deadline/cleanup future requires zero count/no exit in the first and actual
count/truthful exit in the second.

R0.1D honestly calls incomplete-run resumption UNKNOWN; that prevents an
invented completed result but contradicts the broader claim that parsing the
crossings derives every phase.  Crash-resume totality remains unsupported, and
any external effect of the live phase must be isolated or retained.

### D15 — terminal-byte acceptance and primary EOF lack turn precedence

The deadline begins at the terminal's last byte.  The primary EOF transition
then occurs before phase 1 but outside the one-turn ordering.  A clock/failure
poll can therefore interpose despite the intended same-turn close rule.

The last terminal-byte action must include its EOF attempt with no intervening
clock sample; EOF success/failure fixes in that turn, and the next sample begins
replay-request crossing.

## 4. Successful DELETE and DERIVE attacks

These are reductions, not missing data.  They show that R0.1D's MUST ledger and
nineteen-member semantic target are still too coarse.

### D16 — `R01B-S1.json` may rebuild

The inherited semantic contract explicitly defines S1 as a mechanical result
of frozen S0 plus `D_sem`.  Its 28,549,230 canonical JSON bytes can therefore
be regenerated by the identified compiler/specification.  Deleting the S1
materialization from `semantic_members` does not merge a permitted future so
long as its exact sources and constructor survive.

The compiler, CPU, canonicalizer, and validation remain charged.  The target
association and actual S authorization occurrence do not become derivable.

### D17 — checkpoint bytes become rebuildable after a valid locator

Locator validation requires selected raw spans to concatenate to the exact
40-byte checkpoint.  Once that locator, raw targets, checkpoint position, and
order survive, a second checkpoint byte copy can be deleted.  Before a
successful locator exists, an accepted checkpoint remains MUST SURVIVE.

Thus checkpoint responsibility is conditional, not the blanket R0.1D row.

### D18 — raw completion is branch- and terminal-dependent

The completion Boolean is forced false for every active source in a COMPLETE
run.  Under the candidate's fixture rule, accepting the exact recipe's last
byte also supplies fixture completion.  Those bits rebuild from terminal,
branch, bytes, and recipe.  The Boolean remains independent for a stopped
nonfixture source when equal bytes may exist before versus after EOF/reap.

### D19 — native and stop-filled measurement cells rebuild

The thirteen `NATIVE_ONLY` values are exact submission constructors from the
descriptor, semantic/realization/run targets, and fixed registry.  Stop-filled
cells derive from row, path, and cause.  For ordinary structured status values,
the registered reason/evidence payload derives from path/policy once the
actual tag choice survives.

Only genuinely observed native values and nondeducible variant choices are
MUST.  Storing all 1,040 materialized cells is not the quotient.

### D20 — forced `registered_errno="NONE"` rebuilds

For every non-error operation fact and stop-filled `UNKNOWN`, the exact NONE
value follows from `fact` plus the grammar.  Only an admitted error fact's
registered literal or numeric errno is independent.  A branch-shaped union can
remove the repeated NONE text without weakening the later errno query.

### D21 — parts of check triples rebuild

The empty failure-reason list is forced for non-FAIL status.  Entire stop-filled
triples derive from row position and cause.  An actual verifier status and any
nonderivable selected reason/evidence values remain MUST.  The full uniform
three-member materialization need not survive for every branch.

## 5. Post-freeze attacks on the bounded search

The frozen corpus's positive result remains exactly reproducible.  These
attacks bound what that result means and prevent it from being promoted into a
minimum or gate result.

### D22 — family conditioning suppresses most candidate collisions

All 53 histories yield 1,378 unordered pairs.  The search compares only the 39
pairs within a shared family, of which 36 have unequal future answers.  It
never asks whether two histories from different families receive the same
encoding but are separated by a composed continuation.

On the corpus's own handwritten answers, 44 unequal-answer cross-family pairs
already collide under the 17 extractors.  The smallest displayed example is
the two empty histories `semantic_not_ready` and `raw_inactive`: their encodings
are identical while their answers are `IMPLEMENTATION_DENIED` and `INACTIVE`.
This does not refute the explicitly conditioned per-family test; it shows that
family/future context is trusted external state rather than part of the tested
representation.

A fresh hidden pair exposes a real missing association:

```text
h0: exact semantic targets A and B cross; S_READY occurs for A
h1: exact semantic targets A and B cross; S_READY occurs for B
future: attempt authoring under A, then under B
```

The corpus extractors retain the same ordered target bytes and the same bare
`S_READY="READY"` value for both.  They omit which target owns the occurrence,
so the claimed 17-responsibility encoding collides.  The R0.1D nested store
does carry this association; the corpus fails to model it and therefore cannot
validate the total candidate representation.

### D23 — the reported 17-extractor endpoint is not a bounded minimum

Starting with the claimed 17, delete both `check_result` and
`owned_edge_result`, then add the supposedly rebuildable `derived_status`.
The resulting 16-extractor representation has zero collisions on every pair
the script checks.  Within the disjoint check and edge families, PASS/FAIL
happens to encode their two exact future answers.

The 17 result is therefore a consequence of deleting declared-derived fields
before event fields.  “No further deletion succeeds” is true only at that
chosen greedy endpoint; neither minimum cardinality, minimum bytes, nor a
unique quotient representation was searched.  Extractor count is not itself
an information measure.

### D24 — derivation specifications are not executed

The script never reads `derivation_specifications`.  `declared_derived` values
are copied from each history.  Removing the specifications or changing the
failed-check status to arbitrary `MANUALLY_WRONG` bytes still passes and still
classifies `derived_status` MAY REBUILD.

The functional-dependence test is also vacuous whenever every responsibility
encoding in a family is unique.  MAY REBUILD requires an identified total
mechanical constructor, not an arbitrary finite lookup that happens not to
conflict.  It also resets its lookup per family: `semantic_target_a` and
`merge_semantic_target` have the same responsibility encoding but different
declared digest/frame/path extras, yet no inconsistency is seen.  A successor
instrument must execute each constructor and compare its output to
independently supplied expected bytes across the full declared domain.

### D25 — the contract hash is reported but not enforced

The tool hashes the selected `--contract` path for output only.  Running it
against `/dev/null` still exits successfully with the same collision verdicts.
It therefore does not establish that its extractor/future semantics agree with
the frozen R0.1D bytes.

This is acceptable for a self-described external toy search, but not for a
semantic gate.  A successor audit instrument should require the expected
contract digest and fail closed on mismatch; semantic adequacy still requires
independent review beyond a matching hash.

### D26 — merge tokens bake in more deletion than “merge”

Each merge attack ignores the actual two extractor payloads and substitutes a
handwritten common `merge_token`.  For authorization, the S payload is text
while the R payload contains its exact S/R association.  Replacing both by
`"READY"` deletes association bytes as well as the type tag.

The resulting collision proves that this particular lossy normalization is
invalid.  It does not prove that combining responsibilities in one lossless
tagged or otherwise uniquely decodable carrier is invalid.  A surviving
distinction still does not imply a dedicated field or constructor.

### D27 — the histories are not end-to-end sequences

Ten corpus rows are empty histories and the other 43 contain exactly one
event.  No row composes authorization, reservation, channel begin, PREFLIGHT,
row observations, terminal, provider, and later continuation.  Deadline races,
parser-after-B failure, accepted-prefix preservation, reset, crash, evolution,
and cross-run effects are represented only by isolated labels or not at all.

The artifact is a useful one-step distinction table, not yet the requested
smallest end-to-end history corpus.

### D28 — coarse extractors hide the successful branch-local deletions

`measurement_value`, `checkpoint_value`, `check_result`,
`operation_fact`, and `raw_activity_bytes_terminal` each treat a whole family
as one indivisible responsibility.  The search can show that some information
inside each family matters, but it cannot test deletion of derived native
cells, locator-backed checkpoint copies, forced check members, NONE errno, or
complete-run/fixture terminal bits.  D16--D21 are therefore fresh-domain
successful deletions despite the corpus's 17 MUST labels.

The next corpus must split actual choices from deterministic branch outputs and
must test representations, not field names, at the byte/responsibility level.

### D29 — MAY FORGET depends on handwritten future answers

The search does not execute `future_contract`; it reads each history's
handwritten `answer` and skips pairs whose answers are equal.  Cursor values 7
and 9 are classified forgettable only because both empty histories say
`SAME_RESET_STATE`.  Provisional locator and launch-token variants similarly
omit pre-completion and crash continuations by declaration.

Changing an answer exposes or suppresses a collision without changing the
history.  The three MAY FORGET verdicts are therefore conditional hypotheses
about successful cleanup/reset, not observations that reset occurred.  They
must be tested by a future interpreter or kept UNKNOWN.

### D30 — whole-extractor witnesses do not preserve all coordinates

A coarsened form of the same 17 extractor names remains sound on the frozen
pairs while keeping only such fragments as R-ready's semantic parent,
run-reservation primary bytes, channel bytes/EOF, B wire, check status,
operation errno, process terminal/wait, raw bytes/terminal, outcome code, and
external-effect presence.  The alleged delete witnesses therefore do not
establish the omitted key, parent, channel, address, source, response, count,
or explanation coordinates.

One missing pair is enough:

```text
h0: K0 under S0/R0 is reserved to primary P
h1: K1 under S1/R1 is reserved to the same primary P
future: acquire by the reserved key under the selected parent
```

The corpus varies P versus Q while keeping key/parents fixed, so a primary-only
projection passes.  Equivalent gaps exist for request/outcome run association,
locator row/address association, and channel indices other than zero.

### D31 — unrecognized-event extension collides by construction

Corpus validation accepts arbitrary event kinds.  A held-out same-family pair
with unequal future answers and a one-event difference using a fresh kind is
ignored by all 17 extractors and collides.  This does not show that an arbitrary
kind is contract-permitted; it shows that the PASS has no closed event grammar
or fresh-domain guarantee.  A future corpus must derive its event alphabet from
the frozen boundary contract and reject or explicitly classify every other
crossing.

## 6. Mechanically verified nondefects

- The source TV is exactly 290 bytes and reproduces its displayed case/trial
  IDs.  Trace and measurement lengths, hex, and hashes recompute exactly.
- Removing the two historical source rows and adding the replacement yields
  6,317 rows: 3,028 SUBJECT plus 3,289 LAB.  The source ordinal is 6,316.
- The displayed nineteen paths are unique, byte-sorted, and present.  This is
  a construction fact; D16 still permits deleting derived S1 bytes.
- Exhaustive frozen-input checking found zero conversion errors across all
  3,028 SUBJECT and 3,288 retained LAB layouts, including coordinate shapes,
  namespaces/codes/labels, 64,680 subject check positions, 2,010 edges/4,020
  incident references, aggregates, and LAB reason/evidence unions.
- The 23 successor IDs are unique and byte-sorted with 8 S, 2 R, and 13 P;
  the 26 archive IDs are unique and sorted.  The defect is executability and
  failure serialization, not arithmetic.
- The final-request-byte/deadline rule, independent boundary EOF occurrence,
  `k=N` unassigned terminal branch, full-B preservation, frozen locator input,
  locator result retention, single edge ownership, direct nonrebindable run
  key, and exact-target-over-hash rule repair their named bounded attacks.
- Exact provider mismatch has disjoint prelaunch/postlaunch *shapes* and
  request/outcome association by run nesting is unambiguous after crossing;
  D6 concerns reachability of the postlaunch shape.
- Physical durability, unlike-realization evidence, locator causal adequacy,
  cognition, incomplete-run resumption, global quotient completeness, and
  target-contract adequacy remain explicitly UNKNOWN.

## 7. Corrected persistence verdict at this audit boundary

### MUST SURVIVE

- Exact S/R target information or lossless sources, their successful
  authorization occurrences, and their parent association while actions depend
  on them.
- Each permanently reserved direct key, exact parent association, and every
  nonderivable accepted boundary prefix/EOF needed by a permitted continuation.
- Actual nonderivable B, raw, process, operation-error, measurement, check,
  owner-edge, locator, and outcome choices only in the branches where the
  semantic rules and other survivors do not determine them.
- Future-visible external side effects of any apparatus invocation unless
  exact reset-equivalence is established before completion.
- Rejected unequal targets/attempted associations if the promised later
  collision-evidence query is retained.
- Live phase/channel-begin information if crash resumption or later cleanup is
  permitted; otherwise that capability must stay explicitly unsupported.

### MAY REBUILD

- `R01B-S1.json`; semantic paths; IDs/digests; TV/frame bytes; status and
  aggregate views; nonowner edge views; source/status/check fields fixed by
  their branch; checkpoint bytes after a validated locator; complete-run and
  eligible fixture completion; native/stop-filled measurement values; forced
  NONE errno; locator response framing; replay indexes; and parsed completed
  phases.
- Every rebuild depends on the exact surviving source and an identified frozen
  specification.  Compiler, scanner, parser, comparator, and CPU/TCB are
  charged.

### MAY FORGET

- Only noncrossed provisional/internal state after a universally applied
  future-equivalent reset and after no permitted crash/resumption query can
  observe it.
- Duplicate materializations that the surviving source plus exact constructor
  regenerates.

No broader MAY FORGET verdict survives D7, D11, D12, or D14.

## 8. Where the complexity is now

Deleting S1, checkpoint copies, native cells, completion bits, NONE errno, and
forced check members moves work into the semantic compiler, raw/locator
scanner, branch parser, aggregation logic, and query-time regeneration.  Adding
missing occurrence/rejection/channel/live-phase distinctions moves bytes into
the authorization/run evidence carrier and adds atomic append/recovery work.
Totalizing deadlines and launch requires a larger supervisor state machine.
Closing P requires 23 exact relation carriers and a 39-position failure wire.
None of these costs is credited as zero.

The automatic search itself adds corpus design, future declarations,
extractors, canonical comparison, enumeration, minimization, and audit burden.
Its bounded pass reduced uncertainty only inside its 23 conditioned families;
the post-freeze breakers supply the fresh-domain attacks that keep the global
answer UNKNOWN.
