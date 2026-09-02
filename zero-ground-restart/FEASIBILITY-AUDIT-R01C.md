# FEASIBILITY AUDIT R0.1C — POST-FREEZE COLLISION REPORT

## 0. Authority and status

This audit attacks the exact R0.1C candidate bytes whose SHA-256 is
`ea711583b1d5911ceb759f0b91823d9609acef026a91fdf5b4e4ece1b38f84ef`,
committed in repository commit `1eca48b`.  The candidate was frozen before
the attacks below were reported.  Three read-only breakers independently
checked boundary transitions, schema constructivity, and total-system
distinction preservation.  None edited the candidate.

The result is **CONTRACT_DEFECT_UNDECIDABLE**.  R0.1C is not a deletion/merge
fixpoint and does not authorize `S_C`, `R_C`, `P_C`, an implementation, or a
trial.  A later successor may inherit its exact attacks, but may not rewrite
this file or the attacked candidate into a pass.

Each item below is a persistence or determinacy witness.  It does not by
itself require a field, record, layer, service, or named primitive.

## 1. Minimized boundary and transition collisions

### C1 — write readiness versus deadline

Let the replay-process request have one unwritten byte.  In one history its
descriptor is writable at the same poll in which the monotonic clock first
equals the deadline.  R0.1C permits one supervisor to test time first and
retain write count `L-1`, and another to write the last byte, close EOF in the
same turn, and retain `L`.  Both follow the stated prose, but their outcome
bytes differ.  The inherited PREFLIGHT write path has the same collision.

The successor must define one write turn, the observations returned by its
single poll, the order of explicit failure, time, and writable progress, and
whether final-byte acceptance and EOF commitment finish before another poll.

### C2 — provider request EOF versus deadline

Use the same one-byte history at the retained-stream provider input.  A
final-byte/EOF-close failure and the first at-deadline observation can select
either `RETAINED_STREAM_PROVIDER_FAILURE` or
`PROCESS_TIME_BOUND_EXCEEDED`.  Provider acquisition has no exact turn order
corresponding to the capture-turn order.

The provider must use a closed turn and precedence rule, including launch,
request write, EOF, capability transfer, exit, cleanup, and deadline.

### C3 — process-launch commitment

Hold request bytes and package members fixed.  Let a child be created and
then fail during executable-image replacement.  One spawn realization can
report launch failure with no exit record; another can report process exit
`127`.  R0.1C does not identify the event separating those states, so unlike
spawn implementations produce different legal-looking wires.

A successor needs an observable launch-commitment rule.  Before commitment,
all partial descendants belong to launch cleanup and no process-exit fact is
claimed; after commitment, the exact child exit is required.

### C4 — live primary scope at continuation deadline

The replay deadline begins when primary TERMINAL crosses, but replay waits for
the producer, inherited descriptors, and memory to exit.  Let that scope
remain live through the deadline.  R0.1C permits delayed request construction,
an immediate timeout, or unsupported cleanup failure because this wait is not
one of the ordered deadline phases.

The wait must either precede the timer origin or be an exact deadline-governed
phase with one outcome rule.

### C5 — corrupt provider stream

Let the provider transfer a one-bit-corrupt primary stream and exit zero.  The
replay process truthfully computes fresh hash `H'` and may emit a syntactically
well-formed inner `FAIL`, while the request names `H`.  R0.1C does not decide
whether that is a valid inner failure, a malformed outer response, or a
provider failure.  The last alternative also contradicts the rule that no
replay process exists for provider failure.

The successor must bind provider success to exact stream validation before
replay launch, or give the post-launch hash mismatch one unique outer outcome.

### C6 — provider failure with future-visible side effects

Compare (a) provider launch failure with (b) a provider that reads the complete
request, mutates database or CAS state, then fails capability transfer.  Both
produce the same provider-failure outcome.  A later acquisition can observe
the mutation or its cache/timing effect.  Closing processes and handles does
not roll back that state.

Provider acquisition must be future-observably read-only and resettable, or
the mutation and its association are MUST SURVIVE.  Moving it into a database
is EXTERNALIZE, not deletion.

### C7 — terminal association at `k=N`

`submitted_stop=false` means failure before the first unrun row, but R0.1C
allows a stop tail at `k=N`, where no unrun row exists.  A failure after all
envelopes cross and before COMPLETE terminal emission therefore has no unique
association branch.

The successor must either forbid stop completion after all `N` envelopes and
treat emitter failure as an incomplete prefix, or define one exact distinct
terminal behavior.

## 2. Lost or underdetermined information

### C8 — complete B history deleted by parser failure

Take the smallest complete `RECOVERY_ONLY` history and vary only its final
recovery byte between `00` and `01`.  After all three B events cross, fail the
locator parser on the `b_observation` root.  R0.1C calls that logical value
unaccepted, but its stop grammar allows only a *strict* B prefix.  Deleting the
last event collides the two histories; retaining full `history` contradicts
the parser-stop rule.

Parser failure cannot retract a B crossing.  The full accepted B value, or an
equivalent lossless source fact, is MUST SURVIVE.

### C9 — provisional locator input differs from final input

An early locator call can read candidate record `R` and raw prefix `P` and
return `L` twice.  Later capture or stop completion changes another record
leaf or extends raw input to `P || s`; the retained query input is now `R'` and
the same deterministic parser returns `L'`.  R0.1C deletes `L` while requiring
future byte-identical reproduction.

Validation and replay must use the identical frozen input, or accepted locator
results must survive.  Merely running a parser twice is not a reconstruction
specification.

### C10 — uncaptured locator execution state

Keep parser member bytes, path, mode, record, and raw packs equal.  Run the two
initial invocations under stable runtime state `e1` and another pair under
stable state `e2`; each pair agrees but returns a different otherwise valid
list.  Because launch/runtime state is not a parser input or captured member,
the envelopes collide while a historical locator query must answer
differently.

The choices are to persist the accepted result, or to specify a total pure
function and retain every input affecting it.  Code identity plus two-sample
agreement is insufficient.

### C11 — locator adequacy is self-referential

Except for checkpoints, an always-empty deterministic parser satisfies
“all-and-only spans reported by the parser.”  It links no observation to raw
evidence while passing the stated structural checks.  Therefore R0.1C's
explainability/linkage claim is unsupported even if determinism is repaired.

An independent semantic coverage rule or an explicit UNKNOWN/UNSUPPORTED
locator result is required; parser self-report cannot establish adequacy.

### C12 — S_C and R_C success occurrences have no carrier

Let two histories contain identical C0 bytes, equal decoder projections,
semantic members, and realization manifest.  In the first, the required
decoder and inventory-verifier executions occurred; in the second, they did
not.  A future implementation or `P_C` action is authorized only in the first,
but R0.1C calls closure records rebuildable and retains no occurrence bit.

The conjunction of successful executions is MUST SURVIVE until consumed.  An
exact compact occurrence or an indivisible check-and-consume transition can
carry it; deterministic output bytes alone cannot.

### C13 — mutable retained-run registry is externalized

In history H1 a tuple `(semantic ID, realization ID, run_nonce)` has already
been reserved; in H2 it has not.  Submission of the same tuple must be rejected
only in H1.  Likewise the provider needs a mutable run-to-stream association.
Captured store code and configuration are equal in both histories.

The reservation and retained-target association are MUST SURVIVE, or must be
reconstructed by an exact enumeration of retained runs.  An ambient store is
not zero state.

### C14 — finite hashes are not exact unique selectors

R0.1C states that unequal member bytes create a new `A_real` and uses hash IDs
as selectors.  Conceptually choose unequal legal targets with equal exposed
digest.  INVENTORY or raw replay still distinguishes the full targets, but a
hash-only lookup does not.

Every ID binding must reject equal ID with unequal full target bytes, or the
contract must explicitly make collision resistance an unsupported assumption.
No practical collision construction is needed for this exactness attack.

### C15 — MAY REBUILD hides nonderivable canonical leaves

Only thirteen native measurement cells have total constructors.  Other native
cells, operation outcomes, process observations, constituent-check outcomes,
and accepted raw values may be actual observations.  Calling the entire
canonical record rebuildable from unspecified “source facts” is circular if
those facts are the deleted values themselves.

Every nonmechanical source fact is MUST SURVIVE.  Only the canonical container,
position-derived names, and values with an identified total constructor are
MAY REBUILD.

## 3. Schema and constructivity defects

### C16 — inactive raw source has two encodings

Sections 5.1 and 7 say an inactive source is absent; section 5.2 says it is
empty and COMPLETE.  The same manifest and row therefore permit different pack
cardinalities and bytes.  One rule must survive.  Absence is the smaller rule
already used by the stop projection.

### C17 — unknown producer has no completion realization

`producer_path` may name an unknown external or physical slot, while pipe and
run-file branches require waiting for and reaping the exact producer.  No
executable, process identity, launch association, or terminal protocol exists
for an unknown slot.  Restrict these branches to captured members or define and
charge a separate external-producer protocol.

### C18 — source preflight base depends on future bytes

The source row requires its two semantic fixtures but a legal manifest may add
another pipe or file source active on that row.  `SOURCE_PAYLOAD_BASE` is the
entire source envelope and must be constructed during preflight, before the
extra producer runs.  Some R_C-valid manifests therefore can never close P_C.

The two fixture streams must be all-and-only sources active for the source row,
or the attack base must be a closed subcarrier independent of future streams.

### C19 — raw-prefix negative has no independent witness

`RAW_PREFIX_BASE` contains byte `52`, a stop execution, and its completion
marker.  Deleting the marker also describes a legal history in which EOF/reap
completed before an unrelated apparatus failure.  The validator cannot reject
that mutation without inventing a source-terminal observation.

The relation carrier must retain an independent “terminal not observed” fact;
the persistent representation still needs only the smallest completion
discriminator.

### C20 — inherited oracle conversion is branch-partial

The frozen base has 3,028 subject literals whose reason/evidence lists are
inside string-labelled `status_coordinates`, and 3,288 retained LAB literals
whose lists are at the expected-value root and whose coordinates are
`{namespace,code,label}` maps.  `R01B-TO-R01C-ORACLE-1` describes only insertion
of root lists and no branch-specific enum conversion.

The successor must select the branch from its closed row kind, validate all
three label/code/namespace representations where present, take lists from the
branch's actual location, and emit one exact eight-coordinate value.

### C21 — stop completion is not a total constructor

`pending_frames`, `stop_frames`, and the phrase “c-selected registered
unknowns” do not determine exact bytes for every unfinished check, edge,
checkpoint, B/process observation, measurement phase, and raw-source phase.
`empty-nonderivable-prefix` is referenced but never defined.  Consequently
closure bounds and `TERMINAL_ASSOCIATION_BASE` are not materializable.

The global 1,057-text set prevents new strings but does not decide which legal
string belongs to a check.  A successor needs a positional, phase-total fill
function that preserves every accepted value and gives every unaccepted slot
one exact result.

### C22 — ordinary LAB process observations are author-selected

The source row fixes `NO_EXECUTION`, but the other 3,288 LAB rows may choose any
inherited terminal and wait-order text.  If LAB processes are intentionally
not subject processes, their process observation must be the one global
`NO_EXECUTION` pair; otherwise actual LAB process facts need a closed capture
protocol and must survive.

### C23 — launch-relevant realization context is outside A_real

Two systems can expose equal member bytes/path/mode while differing in uid/gid,
directory search authority, ACL, file capability, interpreter state, or a
`noexec` mount.  The next role launch can succeed in one and fail in the other.
R0.1C may consistently call A_real only a reported content-bundle identity,
but it may not claim that the digest fixes launch behavior or the full
realization.

## 4. Mandatory DELETE/DERIVE results not yet applied

The following R0.1C logical-L members contain values already determined by
smaller surviving information:

- `operation_fact.unknown_detail` is fixed by `fact=UNKNOWN` plus stop cause;
- `b_observation.unknown` is fixed by the prefix branch plus stop cause;
- the structured value inside nonempty `missing_suffix` is fixed by its one-bit
  incompleteness discriminator plus stop cause;
- structured unknown process-observation payloads are fixed by absence plus
  stop cause;
- a fixture binding's `fixture_recipe` is fixed by its active LAB trial;
- each edge result copied into both endpoints can at least be owned once and
  rebuilt for the other endpoint from the scan; and
- semantic-member paths are fixed by the exact seventeen-path positional list.

Deleting these values does not permit deleting their discriminators, source
facts, constructors, scan work, or TCB.  A successor must attack each proposed
deletion again; in particular, actual check, process, operation, native-cell,
and locator outputs are not automatically derivable merely because their
container is canonical.

## 5. Verified facts that survived this audit

The following mechanical claims recomputed exactly and are not defects:

- the source TV value, case ID, trial ID, 19-byte selected trace, and trace hash;
- 6,317 effective rows: 3,028 subject and 3,289 LAB, with source ordinal 6,316;
- 1,041 base needed-evidence strings, consisting of 1,027 constructed path
  strings and fourteen direct strings;
- the disjoint union with sixteen C strings, totaling 1,057;
- 1,027 policy-admitted UNKNOWN paths, nine UNSUPPORTED paths, and thirteen
  `NATIVE_ONLY` paths;
- 26 unique attack IDs in unsigned byte order; and
- 110 balanced code fences with no stale namespace-11, namespace-9 value,
  old timeout label, raw-locator member, or persisted terminal-stop map.

The terminal cause plus `submitted_stop` bit survived MERGE: a completed row
followed by a prelaunch stop and the same row stopped after its accepted
observations can share envelope count, unrun suffix, and cause while a per-row
execution query differs.  The compact PREFLIGHT success occurrence likewise
survived DELETE.  These results do not rescue the defects above.

## 6. Successor discipline

Before a successor is frozen it must, in one simultaneous round:

1. close every boundary turn and launch/acquisition commitment;
2. preserve gate, run-registry, B, raw, and nonderivable canonical occurrences;
3. reject unequal targets under an equal finite ID;
4. make stop completion and both inherited-oracle branches byte-constructive;
5. remove every still-derived payload or give it a minimized witness;
6. state which locator semantics are actually supported, including failure and
   semantic adequacy rather than treating a parser as its own oracle;
7. charge the authorization controller, store registry, provider reset path,
   scanner, comparator, and launch context in operations and TCB; and
8. report physical independence, human cognition, complete realization
   identity, malicious coherent replacement, and global future completeness as
   UNKNOWN unless independently observed.

No passing implementation can substitute for these contract obligations.
