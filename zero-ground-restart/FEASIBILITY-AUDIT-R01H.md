# FEASIBILITY AUDIT R0.1H

## Decision

**FIRST TARGET MILESTONE: NOT MET.**

R0.1H establishes a useful finite result at failure-free cuts: fourteen reachable
continuation coordinates are pairwise distinguishable in the abstract model,
every two unequal coordinates are separated by one failure-free `X`, and no
empty future separates them.  This is a fourteen-code lower bound, not an
unconditional proof that all histories within each coordinate are congruent.
It does not establish the total between-crossing/recovery contract needed to
build and compare the proposed unlike realization families.

Four frozen claims fail under the final executable audit:

1. the literal `R`-completion folds for `O`, `P`, and `G` disagree with the
   continuation required by `F:SELECT(new)` after an interrupted changing
   request;
2. exhaustive per-gap selector padding is `3,910,242`, not `3,838,493`;
3. the proposed canonical witness order does not freeze reproducible bytes; and
4. a fresh implementation requires material choices absent from the seed, so
   specification-only cognition/reproducibility fails.

The clean coordinate lower bound does not repair those defects.  Conversely, the defects do
not erase the independently checked clean arithmetic.  The result is a
partially successful mathematical seed and a failed/non-unique total contract,
not a failed proof that some future repaired design is possible.

No Family J, Family Q, or independent Harness H was built or credited.  No
software persistence realization, physical medium, or power-loss experiment was
run.

## Frozen authorities and chronology

| Stage | Frozen authority | Commit | SHA-256 | Role |
|---|---|---|---|---|
| 1 | `HISTORY-SEED-R01H.md` | `7139ab859e7e193af202cd60b8e640f8ce93086b` | `4954ed2a9612ea8a7e95041b689b549a1b9636e2d7457bf003d7d2c056958658` | Candidate specification; 31,084 bytes and 597 lines; reports no implementation or experiment. |
| 2 | `MATH-AUDIT-R01H.md` | `360945e` | `4be36240e23804b0dac6c20c62b14a07f96e8b0ff3c456af0baf02e34d9515be` | Independent finite arithmetic and quotient audit. |
| 3 | `POSTFREEZE-BREAK-R01H.md` | `bf1c698` | `c97e6ef26fbdc0084c739cf64518fd51ff1668ec8b6eb4e1e5e20cebf99d669c` | Fresh seed-only break, completed before archive access. |
| 4 | `ARCHIVE-REPLAY-R01H.md` | `b76dc7d` | `815959501ae4dd06882abf565ea4c8536293f9e3803246894479e6b12b20a2c0` | Prior ZERO GROUND attacks replayed only after the fresh break was frozen. |
| 5 | `RECOVERY-QUOTIENT-R01H.md` | `4aa32e0` | `78785ae88d0b8796d69ccf5060abe524434a8626389f757cc1b70edb6687a149` | Conditional recovery-cut quotient analysis; not a seed repair or realization. |
| 6 | `r01h_boundary_experiment.py` | `1c8bcfae4f356ab3dc8f44596b65a71342355340` | `9e263b059a5c3bd59528384c72f7af0143b17d6633af711c74956a99133053f3` | Final standard-library oracle/falsifier. |

The quarantine order matters.  The primary break was obtained without access
to any prior ZERO GROUND candidate, audit, archive, implementation, or repository
history; it received only the frozen R0.1H candidate.  Archive work was then
admitted only as an attack vocabulary; no prior primitive,
architecture, state schema, or solution was imported into the seed.

## Evidence ledger

The final executable was deterministic in two recorded runs:

| Measurement | Result |
|---|---:|
| Source size | 77,473 bytes; 1,776 lines |
| Standard output size | 47,111 bytes |
| Standard output SHA-256, run 1 | `66fae35a1046664fe88497b49e75316639d5f31f89eeec625e278ac89fdcf954` |
| Standard output SHA-256, run 2 | `66fae35a1046664fe88497b49e75316639d5f31f89eeec625e278ac89fdcf954` |
| Exit status | `1`, because FAIL findings exist |
| Result totals | 24 PASS / 4 FAIL / 16 UNKNOWN |
| Approximate wall time | 14.27 seconds per run |
| Peak resident set size | 372,304 KiB |

Those raw totals are not 24 unconditional claims.  Several PASS entries are
explicitly conditional checks of the executable's chosen scheduler, visibility,
terminal, `Must`, and selected-residual semantics.

### What was actually evaluated

- 157 clean pre-cut words and exact failure-free histories were generated and
  parsed.
- 1,884 clean cut/next-request transactions were evaluated.
- 12,246 unordered clean history pairs and 146,952 one-message pair/message
  comparisons were enumerated.
- 341,370 residual/word/schedule oracle cases were evaluated in process:
  `18 * 18,965`.
- 144 `(remaining depth, residual, crash budget)` adaptive nodes were memoized.
- Eleven deliberate negative controls were exercised.

### What was not executed

- `2,977,505 = 157 * 18,965` is a conceptual history/word/schedule product.  The
  executable did not run that many fresh history sessions.
- The 2,351 same-coordinate history pairs were mapped to one state-keyed future
  signature by construction.  Full futures were independently executed from
  **zero** such pairs.
- `2,304 = 18 * 4 * 2 * 16` is an arithmetic state/depth/budget/phase product.
  Phase is absent from the memoization key; phase-transition refinement nodes
  executed: **zero**.
- `3,838,493` and `3,910,242` are symbolic padded selector-slot counts, not run
  counts.
- No J, Q, H, DELETE, DERIVE, RECOMPUTE, EXTERNALIZE, REALIZE, physical, or TCB
  trial was executed.

## Exact finite results at failure-free cuts

The pre-cut corpus contains

```text
12^0 + 12^1 + 12^2 = 1 + 12 + 144 = 157
```

distinct words and histories.  Independent folding and the executable agree on
the fourteen reachable coordinates:

| Coordinate | Class size |
|---|---:|
| `(U,EMPTY,E0)` | 59 |
| `(0,EMPTY,E0)` | 17 |
| `(1,EMPTY,E0)` | 17 |
| `(U,ID,E0)` | 16 |
| `(U,NOT,E0)` | 16 |
| `(U,EMPTY,E1)` | 16 |
| `(0,ID,E0)` | 2 |
| `(0,NOT,E0)` | 2 |
| `(0,EMPTY,E1)` | 2 |
| `(1,ID,E0)` | 2 |
| `(1,NOT,E0)` | 2 |
| `(1,EMPTY,E1)` | 2 |
| `(U,ID,E1)` | 2 |
| `(U,NOT,E1)` | 2 |

The multiset is

```text
{59,17,17,16,16,16,2,2,2,2,2,2,2,2}.
```

It yields exactly

```text
C(157,2) = 12,246
same-coordinate pairs = 2,351
unequal-coordinate pairs = 9,895.
```

For unequal clean coordinates, `X` is an injective one-message separator because
its reply contains `O`, `P`, and `G`.  An empty future performs only
coordinate-independent FIN/STOP behavior, so one message is length-minimal.
The smallest example is `H()` versus `H(O0)`: empty futures agree and `X`
exposes `O=U` versus `O=0`.

This supplies an unconditional abstract lower bound at failure-free cuts: some
surviving total-system responsibility must distinguish the fourteen reachable
classes.  It does not identify a field, atom, byte count, file, process, owner,
or medium.

The smallest intended same-coordinate merge is `H()` versus `H(RI)`, both at
`(U,EMPTY,E0)`.  The class arithmetic is unconditional, but full adaptive/crash
congruence is not: the executable reused a state-keyed signature and performed
zero independent full-future pair executions.  Therefore no unconditional
same-class forgettability credit is issued.

## Primary contract failure: completion fold versus selected recovery

The corrected witness does **not** claim that the two exact manifests are
identical.  They differ by privileged `F:SELECT(old)` and `F:SELECT(new)`.
Their public `C/R/A/L` projections coincide because the seed erases `F` from
observable traces.

The smallest program-axis witness starts at `H()`:

1. `C:"AUTHOR ID\n"` crosses;
2. a crash occurs before its `R` completion;
3. the two exact manifests record `SELECT(old)` and `SELECT(new)` respectively;
4. recovery reaches READY; and
5. a retry or `X` exposes `P=EMPTY` versus `P=ID`.

Section 1 makes request occurrence on `C` and completion on `R` separate.
Section 3 folds `P` over completed configuration commands.  On the literal
ordinary-`R`-completion reading, neither manifest has completed the interrupted
AUTHOR command, so both folds give `P=EMPTY`.  Section 3.3 nevertheless requires
`SELECT(new)` to continue from the post-transition `P=ID` residual.  The two
requirements cannot both define the continuation without an extra rule.

One interrupted `O0` or `O1` followed by `X` gives the same minimized defect on
`O`; one interrupted `E` followed by `E`, `K`, or `X` gives it on `G`.

The executable records:

- **FAIL** for literal `R`-completion O/P/G continuation consistency;
- **UNKNOWN** for the alternative interpretation in which `SELECT(new)` itself
  semantically applies/completes a command without an `R` crossing; and
- a conditional PASS only after adding the explicit rule
  `SELECT(old) -> pre-request residual`,
  `SELECT(new) -> post-transition residual`.

That conditional rule is a proposed semantic repair, not part of the frozen
contract.  Public-projection insufficiency and exact-manifest inconsistency must
not be conflated.

## Linear schedules and padded selectors

For a future word with `n` messages and `t` occurrences of `T`, the nominal
crossing and schedule arithmetic is exact:

```text
crossings = 2n + t + 2
gaps = 2n + t + 3
no-crash-plus-gap schedules = 2n + t + 4.
```

| Future length | Words | `T` occurrences | Word/schedule structures |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 4 |
| 1 | 12 | 1 | 73 |
| 2 | 144 | 24 | 1,176 |
| 3 | 1,728 | 432 | 17,712 |
| **Total** | **1,885** | **457** | **18,965** |

Multiplication by 157 gives the conceptual `2,977,505` clean-history product.
It is not an execution count.

Prediction 9 fails at the one-message word `[T]`.  Its nominal crossings are

```text
C:T, A:TRY, R:OK, C:FIN, R:STOPPED.
```

Six gaps plus no-crash give seven base schedules.  Both `C`-to-`A` and
`A`-to-`R` satisfy “`C` crossed and `R` did not,” so exhaustive per-gap old/new
padding adds one execution slot at each gap, even though `T` does not change the
residual and the public outcomes later collapse.  The required padded count is
nine; the frozen formula gives eight.

The corrected formula and totals are

```text
per word: 3n + 2t + 4
per prehistory: 24,906
across 157 prehistories: 3,910,242
frozen value: 3,838,493
shortfall: 71,749.
```

The executable's gap histogram also reconciles exactly:

| Phase | Gap structures per residual |
|---|---:|
| Idle | 7,369 |
| Pending request | 5,484 |
| Post-action/pre-reply | 457 |
| FIN-pending | 1,885 |
| Terminal | 1,885 |
| **Total** | **17,080** |

The count failure may instead be repaired by declaring exactly one selected
barrier per request and narrowing Section 3.3.  That would be a different
contract, not a validation of the frozen exhaustive-per-gap prose.

## Conditional recovery quotient

The seed does not define equivalence at a recovery cut.  The recovery analysis
therefore fixes a conditional cut immediately after `DOWN` and before SELECT and
READY, retains the old/new alternatives and pending phase, permits no second
crash, and begins the compared suffix at that cut.

Its raw semantic-condition inventory is

```text
18 clean residuals
+ 69 changing interrupted non-T conditions
+ 129 no-op interrupted non-T conditions
+ 18 pre-A T conditions
+ 18 post-A T conditions
+ 18 FIN-pending conditions
+ 1 post-STOP condition
= 271 condition types.
```

These are condition types, not concrete histories, controllers, or executions.
They were derived and independently checked symbolically; the executable did
not enumerate or quotient these 271 conditions and did not compute the
65/89/107/125 recovery classes.

Under Contract A—the seed's hidden-selector, deduplicated public-May
projection—and with at least one ordinary message left, one `X` exactly
fingerprints residual singleton and unordered-pair continuations.  If a
post-STOP recovery cut is included, the conditional quotient is

```text
18 singleton residual classes
+ 45 unordered changing-residual edges
+ 1 FIN-pending class
+ 1 terminal class
= 65 classes.
```

It is 64 if post-STOP does not create a recovery cut.  The headline 65 is
therefore conditional on both at least one remaining message and inclusion of
post-STOP recovery.

If old/new labels are themselves observable or required, the seed leaves the
clean-gap label protocol unfrozen.  Three conditional variants result:

| Label-preserving convention, at least one message left | Classes |
|---|---:|
| Both labels accepted and collapsed at clean gaps | 89 |
| No selector at a clean gap | 107 |
| Separate old-only and new-only clean phases | 125 |

Remaining depth changes all these results.  After the third allowed message,
when no ordinary message remains, the conditional counts are:

| Convention | Zero-message classes |
|---|---:|
| Contract A, post-STOP included | 3 |
| Contract A, post-STOP excluded | 2 |
| Label-preserving 89-class variant | 3 |
| Label-preserving 107-class variant | 4 |
| Label-preserving 125-class variant | 5 |

Cut placement before or after SELECT, inherited versus reset future depth,
clean-gap selector semantics, client visibility of capture-peer `A`, and
post-STOP trace completion are all unfrozen.  Therefore the total recovery
quotient is **UNKNOWN**.  The 65, 89, 107, and 125 values must not be summed,
mixed, or presented as seed-wide counts.

Useful minimized conditional mergers are:

- clean `(U,EMPTY,E0)` versus an interrupted failed-precondition `RI`: the same
  singleton continuation under Contract A;
- interrupted `AI` from `EMPTY -> ID` versus interrupted `D` from
  `ID -> EMPTY`: the same unordered edge under Contract A, but reversed old/new
  maps under a label-preserving contract;
- `T` interrupted before `A` versus after `A`: the future service continuation
  may merge, although the already crossed `A` remains a different historical
  fact; and
- FIN-pending versus post-STOP: separated with no ordinary message because the
  former owes exactly one STOPPED and the latter owes no reply.

## Prediction verdicts

| # | Unconditional verdict | Aggregate finding |
|---:|---|---|
| 1 | PASS | Exactly 157 clean pre-cut histories. |
| 2 | PASS | Exactly fourteen clean coordinate blocks with the frozen size multiset.  `X` makes them a pairwise-distinguishable lower bound; same-block total-future congruence remains conditional, so this is not an unconditional total quotient or a persistence layout. |
| 3 | PASS | Exactly 2,351 same-coordinate and 9,895 unequal unordered pairs.  These are arithmetic counts, not full-future pair executions. |
| 4 | PASS | At clean cuts, `X` separates every unequal coordinate in one message and an empty future separates none.  Canonical bytewise witness ordering is a separate failed claim. |
| 5 | UNKNOWN | A 144-node state/depth/budget model conditionally preserves 14/18 classes, but scheduler identity, `A` visibility, `Must`, terminal projection, selected-residual semantics, and phase refinement are not frozen. |
| 6 | FAIL | The two operational AUTHOR crash/retry traces can be generated under the selected-residual repair, but literal completed-command `P` and `SELECT(new)` continuation disagree. |
| 7 | PASS | Abstract post-`A` crash/retry yields two crossed `A` frames.  It proves no downstream receiver effects or exactly-once behavior. |
| 8 | PASS | The syntactic totals are 18,965 and conceptual 2,977,505. |
| 9 | FAIL | Exhaustive per-gap padding is 3,910,242, not 3,838,493. |
| 10 | UNKNOWN | J, Q, and independent H were not supplied or executed. |
| 11 | PASS | Software-boundary results do not entail the expressly excluded physical, security, authority, or downstream-effect claims.  This is a correct non-inference, not evidence about those properties. |

One false finite prediction rejects the frozen prediction set as a whole.  It
does not refute predictions 1 through 4 at clean cuts.

## Adaptive and canonical limits

The executable conditionally evaluated all 18 residuals against all 18,965
linear word/schedule structures, with maximum May cardinality two.  It also
memoized 144 `(depth,state,budget)` nodes.  Under its chosen policy encoding,
the fourteen clean coordinates map to fourteen node classes and the full
modeled residual domain maps to eighteen.

This is not the seed's promised 2,304-node phase refinement.  The executable
only multiplies 144 by sixteen invented phase labels; it executes zero
phase-keyed transition nodes.  Nor does it independently run full futures on
the 2,351 same-coordinate history pairs.  Its same-class result is a symbolic
lift through `state = (O,P,G)` and is conditional on exactly the factoring at
issue.

A common adaptive scheduler remains undefined when observed branches have
different shapes.  The minimized probe compares `H()` and `H(AI)`, sends `X`,
then sends `T` only if the reply contains `P=EMPTY`; “crash after the second
request's A” exists on one run and not the other.  The seed also does not say
whether a legal client controller observes `A` at the independent capture peer.

`Must` lacks a frozen vacuity rule for no-crash runs and needs an internal
branch carrier for the old/new-residual proposition after public trace
deduplication.  The counted crash gap after STOPPED likewise does not say
whether the completed trace ends at STOPPED or appends `DOWN,READY`.

Finally, the minimization order does not freeze crossing tag bytes, integer
width/endianness, complete controller and scheduler grammars, typed lifecycle
encoding, or all length meanings.  One-message `X` length minimality survives;
reproducible bytewise canonical witness identity fails.

## Mandatory attack battery

| Attack | Aggregate verdict | Evidence and limit |
|---|---|---|
| DELETE | UNKNOWN | No named implementation responsibility was removed and cold-started. |
| MERGE | UNKNOWN overall | `X` rejects a forced unequal-coordinate merge in the abstract clean model.  Same-coordinate total-future congruence is conditional and no realization labels were forced together. |
| DERIVE | UNKNOWN empirically | Clean exact output bytes are mathematically derivable from continuation responsibility, request, and specification; no target bytes were deleted and cold-rebuilt. |
| RECOMPUTE | UNKNOWN | No replay/table recovery machinery or reconstruction cost was measured. |
| COLLIDE | FAIL at the contract level; realization UNKNOWN | Distinct SELECT manifests fold to the same old O/P/G value under literal `R` completion while `SELECT(new)` requires a distinguishable continuation.  The executable's injective 288-string Cartesian product is only a local smoke test; no candidate phase encoding or forced implementation hash collision was tested. |
| FUTURE | UNKNOWN unconditionally | The chosen state-only model conditionally passes 341,370 linear evaluations and 144 adaptive nodes; scheduler, visibility, `Must`, terminal, selected-residual, phase, and independent pair evidence remain open. |
| EXTERNALIZE | UNKNOWN | No client, capture peer, token, build artifact, or specification service was introduced and then severed. |
| REALIZE | UNKNOWN | J, Q, and H do not exist as tested independent realizations. |
| COGNITION | FAIL for specification reproducibility; human performance UNKNOWN | Fresh work required choices about SELECT completion, padding, terminal traces, `Must`, adaptive schedules, `A` visibility, and serialization.  No controlled human study measured time, recall, or error. |
| TCB | UNKNOWN | Runtime, OS, transport, serializer, compiler, cache, fault hook, capture peer, oracle, canonicalizer, filesystem, and build inputs were not independently perturbed. |

## Archive replay disposition

Archive replay found no genuinely new FAIL and no smaller counterexample than
the frozen fresh break.  It independently re-exposed the recovery, scheduler,
`Must`, terminal, canonicalization, and padding problems and prevented scoped
exclusions from being mistaken for capabilities.

The following are coherent scope closures, not implementation successes:

- malformed, partial, empty, non-LF, and arbitrary request frames are outside
  the twelve-frame atomic alphabet and return typed UNSUPPORTED;
- empty input is not FIN; FIN is an explicit typed crossing;
- corruption, rollback, counterfeit recovery images, concurrency, clocks,
  unbounded resources, privacy, authority, and downstream exactly-once effects
  are excluded; and
- the hypothetical exact-history interpreter request is outside the supported
  alphabet.

The replay kept selector completeness and trace binding, hidden cache/path
state, recovery-image validation, external specification identity, capture-peer
availability/authenticity, DELETE/DERIVE/RECOMPUTE evidence, TCB perturbation,
fresh-human measurement, and unlike software/physical realization UNKNOWN.

Where the fresh and archive reports described one equal “exact observable
prefix,” this aggregate adopts the final executable's more precise statement:
the exact F-bearing manifests are distinct; their public `C/R/A/L` projections
are equal; the frozen literal `R`-completion fold conflicts with the selected-new
continuation.

## Cautious responsibility classification

These labels classify behavioral responsibilities only.  They do not classify
fields, records, files, storage locations, physical bytes, or owners.

| Subject | Label | Scope and condition |
|---|---|---|
| Distinction among fourteen failure-free clean coordinates | **MUST SURVIVE** | Unconditional within the closed clean-cut model.  `X` provides the direct lower bound.  The distinction may survive in any total-system component. |
| Machinery/specification sufficient to construct exact clean replies and action frames | **MUST SURVIVE** | Some responsibility for exact byte construction is required; the seed does not require pre-materialized output bytes. |
| Exact clean reply and action bytes | **MAY REBUILD** | Model-level derivation from surviving continuation responsibility, current request, and frozen specification is valid.  Actual cold DERIVE evidence is absent, and reconstruction machinery/cost remains charged. |
| Exact pre-cut transcript and distinctions between histories in one clean coordinate | **MAY FORGET** | Conditional only on a repaired, common future contract and a surviving continuation responsibility.  Zero independent full-future same-pair executions means this is not unconditional credit. |
| Pre-SELECT alternatives for an interrupted changing request | **MUST SURVIVE** | Conditional pre-SELECT quotient with at least one ordinary message left: an unordered endpoint set under public Contract A, or an old/new-indexed map under label Contract B.  At zero remaining depth these residual distinctions may merge extensionally. |
| Selected residual after SELECT | **MUST SURVIVE** | Conditional when a remaining future can observe it: the continuation must behave as the chosen old or new residual.  At zero remaining depth it may merge under extensional equivalence; an intensional label contract may retain `(label,residual)`.  The frozen rule connecting this to the completed-prefix fold is defective. |
| Pending ordinary `R` completion after interruption | **MAY FORGET** | More strongly, it must not survive as an owed reply: the interrupted ordinary request receives no completion after recovery. |
| Interrupted ordinary request identity after selection | **MAY FORGET** | Conditional when selected residual and special phase agree; request identity is not itself a later reply obligation. |
| Pre-A versus post-A `T` service-continuation distinction | **MAY FORGET** | Conditional recovery quotient: neither phase emits a new `A` or `R` for the interrupted transaction. |
| An `A` frame that already crossed | **MUST SURVIVE** | It remains an immutable fact in external capture/history and must not be replayed.  This need not imply a distinct future service residual. |
| FIN-pending exactly-one STOPPED obligation | **MUST SURVIVE** | Unconditional until discharged; it is distinct from an active residual and from terminal/no-more-reply behavior. |
| Post-STOP terminal/no-more-reply condition | **MUST SURVIVE** | Conditional on admitting post-STOP recovery; it must remain distinct from FIN-pending.  Inclusion of later lifecycle crossings is still UNKNOWN. |
| Old/new orientation under the seed's deduplicated public projection | **MAY FORGET** | Conditional Contract A only.  With at least one message left, a label-preserving Contract B instead makes orientation **MUST SURVIVE** and yields the 89/107/125 ambiguity; zero-depth extensional classes collapse further. |

No `MAY FORGET` label means physical deletion.  No `MAY REBUILD` label makes
reconstruction free.  Caches, allocator/runtime state, generated tables,
filesystem metadata, recovery images, and physical persistence receive no
definitive classification without realization attacks.

## Simultaneous total-system dimensions and where complexity moved

Feasibility cannot be ranked by one scalar such as state labels, stored bytes,
source lines, or test cases.  Every candidate must be assessed simultaneously
on the following dimensions:

| Dimension | Required accounting | Present evidence |
|---|---|---|
| Clean continuation behavior | Fourteen pairwise-distinguishable reachable coordinates; exact C/R/A outputs | Finite clean lower bound PASS; within-coordinate total congruence conditional |
| Recovery behavior | Pending phase, selector authority, selected residual, READY, no invented ordinary reply | Contract defective; conditional quotient only |
| Termination | Durable FIN responsibility and exactly one STOPPED; terminal no-more-reply | FIN-pending witness PASS; post-STOP projection UNKNOWN |
| External action history | Atomic captured `A` crossing and no receiver-effect inference | Abstract crossing counts PASS; capture implementation UNKNOWN |
| Information-loss risk | Reject cross-coordinate merges; justify every same-coordinate deletion and recovery merge | `X` rejects cross-coordinate merges; same-coordinate deletion and recovery orientation loss remain conditional |
| Representation | Transcript, quotient label, or factored responsibilities | Proposals only; no layout receives credit |
| Persistent state and storage | Cardinality, bytes, framing, write protocol, recovery image, retention | Behavioral responsibilities only; physical bytes, storage volume, and media behavior UNKNOWN |
| Transition/output machinery | Replay fold, generated table, or conditional interpreter plus serializer | Mathematical possibilities only |
| Authoring burden | Exact `ID`/`NOT` authoring, replacement, retirement; human effort and broader language | Bounded command behavior checked; arbitrary authoring unsupported; effort/error unmeasured |
| Query/navigation burden | Exact `Q`, `X`, and `K`; discovery and navigation beyond current finite state | Direct finite queries checked; no search/navigation infrastructure built; burden unmeasured |
| Explainability | Immediate exact current-state `X`; recovery/lineage/evidence explanation | Current-coordinate bytes checked; branch provenance, lineage, and canonical evidence remain absent or unsupported |
| Evolution | Failure-free `E0 -> E1`, repeated evolution, recovery during evolution, broader migration | Clean identity behavior PASS; interrupted fold is defective; arbitrary migration unsupported |
| Runtime | Execution cost of candidate behavior and recovery | Only the falsifier was measured (about 14.27 s and 372,304 KiB); candidate runtime/latency UNKNOWN |
| Operations | Deployment, cold start, recovery, monitoring, backup, rollback, fault handling | No candidate operational trial; rollback/backup outside seed; operations UNKNOWN |
| Canonicalization/build | Exact tags, lengths, tree/scheduler grammar, generator/spec identity | Reproducibility FAIL/TCB UNKNOWN |
| Corruption and rollback | Framing, validation, freshness, counterfeit/old images | Coherently out of seed scope; no robustness evidence |
| External dependencies | Client token, capture peer, specification/build service, authority | EXTERNALIZE UNKNOWN |
| Cognitive burden | Reproducible contract plus implementation/reconciliation work | Specification reproduction FAIL; human measurement UNKNOWN |
| Portability | Independent language/runtime/OS/architecture and unlike physical realization | One Python/standard-library falsifier in one environment; portability and physical independence UNKNOWN |
| TCB | Runtime through media, compiler, hook, peer, oracle, and build inputs | UNKNOWN |
| Physical realization | Media durability, power interruption, controller caches, physical independence | UNKNOWN and unsupported |

The clean-coordinate factoring moves complexity; it does not eliminate it:

- Forgetting a transcript moves continuation responsibility into some surviving
  label, components, code path, or external source.
- A quotient atom moves transition/output complexity into its table, generator,
  serializer, snapshot/commit protocol, and build/specification identity.
- Factoring `(O,P,G)` moves interaction correctness into conditionals plus the
  recovery representation of phase and selected residual.
- Transcript/replay moves recovery cost into journal framing, completion
  markers, replay logic, and retained historical distinctions.
- Rebuilding reply/action bytes moves responsibility into the frozen byte table,
  serializer, and surviving continuation state.
- Erasing SELECT from public traces moves branch association into privileged
  manifest/harness state; it does not remove selector authority.
- Merging pre-A and post-A service continuations leaves the crossed `A` fact at
  the capture/history boundary.
- Externalization moves responsibility and failure modes to the named client,
  peer, token, build artifact, or service; it is not deletion.

## Why realizations were not credited

The seed makes J, Q, and H obligations depend on one exact total oracle,
canonicalizer, scheduler domain, and recovery branch protocol.  The fresh and
executable audits found those inputs contradictory or underdetermined before a
realization gate could be meaningful.  Building J or Q at that point would
silently select a repair and show conformance only to that local interpretation;
building H would embed the same choice in the judge.  The work therefore stopped
at falsification and conditional model checking rather than crediting an
arbitrary repair as the frozen result.

This is not evidence that unlike implementations cannot be built after a new
freeze.  It is evidence that none was built or compared here.  In particular,
there is no unlike software-realization equivalence result, no independent
capture/selector manifest dossier, no cold-restart or persistent-image result,
and no unlike physical-media or real power-loss evidence.

## Required next gate

Before another realization attempt, a replacement freeze must at least:

1. reconcile literal `R` completion with `SELECT(new)` and define the semantic
   state on both sides of SELECT;
2. fix recovery-cut placement and inherited remaining depth;
3. choose public versus label-preserving selector equivalence and clean-gap
   selector behavior;
4. define one common adaptive scheduler domain and controller access to `A`;
5. define the `Must` carrier and vacuity/inapplicability rules;
6. freeze the post-STOP trace projection;
7. correct per-gap selector padding or explicitly narrow the barrier plan; and
8. freeze complete canonical crossing, controller, scheduler, and outcome-set
   bytes.

Only then can independent J, Q, and H work begin without silently changing the
contract.  Those realizations would still need actual DELETE, MERGE, DERIVE,
RECOMPUTE, COLLIDE, FUTURE, EXTERNALIZE, REALIZE, COGNITION, and TCB evidence,
with physical and power-loss claims kept separate from abstract software-boundary
results.
