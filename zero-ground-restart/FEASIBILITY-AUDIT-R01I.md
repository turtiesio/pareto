# ZERO GROUND R0.1I — Feasibility audit

## 0. Decision and scope

**FIRST MILESTONE: FAIL — NOT ACHIEVED.**

R0.1I is a useful finite attack surface, but it is not one internally
consistent, independently reproducible history quotient:

1. literal same-cut-kind equivalence gives 238 PUBLIC and 415 privileged
   recovery classes, while the frozen predictions claim 139 and 315;
2. unequal clean histories have a zero-ordinary-message contractual separator,
   contrary to Prediction 3;
3. canonical cut, branch, scheduler-domain, and witness bytes are not total;
   and
4. multiple persistence, externalization, cognition, realization, and TCB
   obligations remain UNKNOWN.

One finite counterexample dominates any number of finite-model passes.  An
implementation that happens to reproduce one chosen reading would implement
that reading; it would not repair the frozen contract, select an architecture,
or establish physical persistence.  No representation is selected here.

This audit uses the R0.1I archive replay only as quarantined attack vocabulary.
It adopts no old solution, representation, ontology, or physical claim.

## 1. Frozen artifact, commit, and hash ledger

| Artifact | Commit | SHA-256 | Role |
|---|---|---|---|
| `HISTORY-SEED-R01I.md` | `c8f912b08a468dffdfb29352aaa9924aee9048ba` | `d52c083c34aa37144fa47ee8a02d9279adb75029613125f38dad5a98b0df8d9c` | Candidate authority |
| `BLIND-ATTACK-PACK-R01I.md` | `7f60816df97bed16bcfc80f837528725e1efa4b8` | `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b` | Ontology-independent attack definitions |
| `LITERAL-SPEC-AUDIT-R01I.md` | `866df82f44272d4d44ef9c28bab8c4aeec53c7da` | `e26af4a66ff1884371973a60710c5b0f556b9d4b78b5259bb50d355007262ad5` | Pre-implementation literal audit |
| `POSTFREEZE-BREAK-R01I.md` | `c8bd7f7a5cbe2fd93ddc14021761dbfa569e7fbf` | `57f007f0457595e5545eb9dd76fda210b9eea94483a1d74cb6d074230b8ac015` | Independent finite break and recount |
| `r01i_recovery_experiment.py` | `a905bedc256e138a63b15ea7db740e14021fb99b` | `770269f9a723d7a737a6a4c3c6e8e3a27952213b9b60c31b09924bc3c3888ff1` | Fail-closed executable falsifier |
| `EXPERIMENT-RESULT-R01I.md` | `89e06b920bded12df61e9d4c5d113a7e345944e5` | `6c1458f369ec6d576d7e7dd44b2fc23ae3fe8d38c5047475ece2d7915553c858` | Frozen run report |
| `PERSISTENCE-COLLISION-LEDGER-R01I.md` | `a84e156e11a075d1f27574b1ef3a38b9fb0342b2` | `9e865eec647fda9a78e9bda119f22f12cc4c33d08c3e67bded0686dc1438d6de` | Section 14 collision/derivation audit |
| `ARCHIVE-REPLAY-R01I.md` | `d2d55ba79557181a7bd3731613cb7760fcdf752f` | `921b7589a0694942531dc078ffb48d03436e78c0f32717b79e8516373b8af9cf` | Quarantined replay of earlier attacks |

The executable verifies the candidate hash before semantic work and exits
nonzero on a finite FAIL.  Its frozen run exited 1 with 97 PASS, 5 FAIL, and 7
UNKNOWN results.  Deterministic stdout had SHA-256
`5172c93e092b60837f759ea2cf7326d32124cf4f84c490394d18fc82c93e341f`.
The stdout was not retained as a second authority.

## 2. What was executed, lifted, derived, and not run

### 2.1 Direct executable enumeration

The falsifier directly generated or evaluated:

| Direct scope | Exact amount or result |
|---|---:|
| Clean histories | 157 |
| Clean unordered pairs | 12,246 |
| Distinct exact recovery prefixes | 1,208,272 |
| Total exact cuts including clean cuts | 1,208,429 |
| Normalized recovery conditions | 854 |
| Future probe bytes | Every normalized condition through its remaining allowance |
| Clean linear futures | Every no-crash and one-crash word/gap structure through depth 3 for all 14 reachable clean residuals |
| Recovery Must evaluations | 122,908 generated branch families |
| Must negative controls | 10, one targeted at each bit |

Exact recovery-prefix uniqueness was checked with an injective finite crossing
sequence code.  Canonical trace round trips were sampled during that 1,208,272
prefix enumeration; this was not an all-prefix canonical-witness audit.

The run took 111.38 seconds wall time, 110.96 seconds user CPU, 0.40 seconds
system CPU, and 330,196 KiB maximum resident memory.  These are falsifier-run
measurements, not service runtime, cold-start, or recovery measurements.

### 2.2 Exact symbolic lifts

Each exact recovery prefix was mapped to its enumerated normalized condition.
Future signatures were computed once per normalized condition, and exact-prefix
class sizes and pair counts were then aggregated through those exact mapping
frequencies.  Those results are exact **symbolic lifts**; they are not
1,208,272 independent future executions.

In particular, the 139/315 and 238/415 exact-history class-size histograms in
the break report are conditional lifts under their stated quotient readings.
The cross-kind 315 reading has 91,867,064,142 equivalent exact-history pairs;
the literal 415 reading has 91,247,042,949, a difference of 620,021,193 pairs
merged only by deleting the same-kind gate.

### 2.3 Mathematical derivations and conditional closures

The following are finite derivations rather than realization evidence:

- reply, A, RESUME, and ALLOWANCE **expected** bytes from residual, request,
  phase, branch, allowance, and specification;
- residual from the validated application fold;
- pre-FIN allowance from `3 - ordinary-C occurrences`;
- viewer projections and May deduplication from complete traces; and
- clean same-coordinate congruence in the finite transition model.

The independent closure recount, not the frozen falsifier, conditionally gives
`|D| = 82,224`:

| Remaining d | Decision keys |
|---:|---:|
| 3 | 3 |
| 2 | 153 |
| 1 | 3,977 |
| 0 | 78,091 |

Thus 4,133 entries are free, 78,091 entries are forced FIN, the conditional
controller count is `13^4133`, and `EncController` would occupy 82,233 bytes
before an outer wrapper.

`G` has a decisive closure fork:

| Text-consistent reading | Conditional `|G|` | Consequence |
|---|---:|---|
| Form keys only before the crash budget is used | 64,067 | `2^64067` policies; 8,009 policy bytes; 8,018-byte `EncScheduler` |
| Also include post-crash/recovery nominal keys whose bits are ignored | 519,886 | Larger canonical key list and vector |

For the 64,067 reading, proposed-next classes are 23,621 C, 25,857 R,
1,660 A, and 12,929 END keys.  The frozen text does not choose between the two
closures.  Neither conditional count is a canonical prediction PASS.

### 2.4 Work not executed

No artifact supplies a service realization, cold-start deletion, actual
reconstruction machinery, severed external carrier, unlike physical
realization, controlled human study, or one-at-a-time TCB perturbation.
Physical completion, media persistence, capture durability, authorization,
privacy, receiver effects, and exactly-once behavior remain UNKNOWN.

## 3. Finite corpus and prediction verdicts

### 3.1 Stable finite counts

| Quantity | Reproduced result |
|---|---:|
| Clean histories / classes | 157 / 14 |
| Clean class sizes | `59,17,17,16,16,16,2,2,2,2,2,2,2,2` |
| Clean same / unequal / total pairs | 2,351 / 9,895 / 12,246 |
| Reachable residuals after 0/1/2/3 future completions | `14,18,18,18` |
| Recovery prefixes: idle | 295,945 |
| Recovery prefixes: pending non-T | 271,139 |
| Recovery prefixes: T before / after A | 24,649 / 24,649 |
| Recovery prefixes: FIN-pending / terminal | 295,945 / 295,945 |
| Total recovery prefixes / total cuts | 1,208,272 / 1,208,429 |
| Normalized recovery conditions | 854 |
| Base / padded probes per clean plan | 18,965 / 24,906 |
| Base / padded slots across 157 histories | 2,977,505 / 3,910,242 |

### 3.2 Predictions 1–14

| Prediction | Verdict | Evidence and qualification |
|---:|---|---|
| 1 | PASS | 157 histories, 14 clean coordinates, and the stated class multiset reproduce. |
| 2 | PASS | 2,351 same and 9,895 unequal clean pairs reproduce. |
| 3 | **FAIL** | X separates publicly, but FIN plus an initial-gap crash exposes unequal RESUME values to SELECTOR/Priv with zero ordinary C. |
| 4 | PASS at finite-model scope | Exhaustive modeled futures found no split of equal clean coordinates. No implementation/path/cache claim follows. |
| 5 | PASS | All six recovery-prefix phase totals and 1,208,429 total cuts reproduce. |
| 6 | PASS | The normalized corpus has 854 conditions. |
| 7 | **FAIL** | Relaxed 139/315 reproduces; literal contractual equivalence gives 238/415. |
| 8 | **FAIL** | Literal histogram is `363x1,9x6,27x7,14x8,2x68`, not the printed 315-class histogram. |
| 9 | PASS at finite-model scope | Interrupted AI OLD/NEW applies exactly as specified and invents no interrupted R. |
| 10 | PASS at crossing-model scope | CLIENT-blind retry yields one A from pre-A and two from post-A; no receiver effect follows. |
| 11 | PASS at finite-model scope | FIN-pending emits one STOPPED; terminal recovery emits none. |
| 12 | PASS | All base and padded linear arithmetic reproduces, including 3,910,242. |
| 13 | **FAIL** | EncCut/branch presence, derived-field mismatch handling, G closure, and viewer eligibility do not determine one canonical byte string. |
| 14 | PASS for generated grammar; UNKNOWN as a total verifier | All 122,908 generated families satisfy the ten implications and all ten mutations are detected under the experiment's disclosed scope. Recovery-cut prefix-versus-suffix Must scope is not frozen independently. |

## 4. Literal and relaxed recovery quotients

Section 7.3 permits comparison only between equal cut kinds and equal live
allowance contracts.  Sections 9 and 11 merge PENDING_NON_T, T_PRE_A, and
T_POST_A behaviors across that gate.  Both relations were evaluated from
exact future signatures, not from predicted class labels.

| Reading | PUBLIC classes | Privileged classes | Privileged normalized histogram |
|---|---:|---:|---|
| Relaxed suffix behavior, deleting the kind gate | 139 | 315 | `263x1,9x8,27x9,14x10,2x68` |
| Literal same-cut-kind contract | **238** | **415** | `363x1,9x6,27x7,14x8,2x68` |

Allowance decomposition is:

| d/phase | Relaxed PUBLIC | Literal PUBLIC | Relaxed Priv | Literal Priv |
|---|---:|---:|---:|---:|
| d=3 | 14 | 14 | 14 | 14 |
| d=2 | 59 | 101 | 89 | 117 |
| d=1 | 63 | 117 | 105 | 141 |
| d=0 | 1 | 4 | 105 | 141 |
| FIN-pending + terminal | 2 | 2 | 2 | 2 |

At normalized-pair level:

| Domain | Comparable pairs | PUBLIC same / separate | Priv same / separate |
|---|---:|---:|---:|
| Cross-kind active domains used by printed counts | 87,799 | 37,688 / 50,111 | 6,410 / 81,389 |
| Literal same-kind domains | 56,687 | 25,250 / 31,437 | 5,650 / 51,037 |

The relaxed quotients are coherent observational suffix partitions.  They are
not the equivalence relation frozen in Section 7.3 and cannot be called the
contractual quotient without changing the candidate.

## 5. Smallest collisions, separators, and mergers

| Finding | Smallest pair and permitted future | Result |
|---|---|---|
| Zero-ordinary clean separator | `H()` versus `H(O0)`; choose FIN and crash at the initial pre-FIN gap | SELECTOR/Priv sees `RESUME O=U` versus `O=0`; Prediction 3 fails. |
| Cross-kind merger used by 315 | From `H()`, interrupt no-op RI after C; compare T interrupted after C/before A at the same `r=(U,EMPTY,E0),d=2` | Recovery suffixes match, but kinds PENDING_NON_T and T_PRE_A are not comparable. |
| T-phase merger | T interrupted before A versus after A at fixed r,d | Suffix behavior matches, but kinds T_PRE_A/T_POST_A differ; Section 11.4 conflicts with Section 7.3. |
| Privileged orientation | Interrupted AI `EMPTY->ID` versus interrupted D `ID->EMPTY`, both PENDING_NON_T at d=2 | PUBLIC endpoint sets agree; SELECTOR/Priv OLD/NEW orientation differs with zero ordinary C. |
| Clean permitted merger | `H()` versus `H(RI)` | Same CLEAN kind, d=3, residual, and exhaustive modeled future; exact prefix is omitted. |
| Request-identity merger | Interrupt RI versus RN from `(U,EMPTY,E0)`, then apply the same SELECT | Same-kind OLD/NEW recovery futures are byte-identical; identity may be forgotten after SELECT. |
| FIN allowance merger | FIN immediately versus one completed O0 then FIN, each crashing before STOPPED | Same FIN_PENDING future; unused allowance is dead and rebuildable from the retained prefix. |
| Selected-branch merger | Interrupt AI versus AN from EMPTY and realize OLD | Selected OLD futures agree; unlike NEW alternatives must remain in the complete manifest family. |
| EncCut collision of readings | Encode CLEAN/T/FIN/terminal cuts with different text-consistent optional residual/alias presence maps | Different bytes, lengths, pair orientation, and witness order. |
| Witness-viewer collision | Interrupted AI/D orientation pair | CLIENT code 0 and SELECTOR code 3 are both text-consistent because viewer admissibility is absent. |
| Vacuity evidence collision | No-crash family versus lifecycle-correct crash family | Must bit 1 is true vacuously versus non-vacuously, but the mask records the same truth. |

The canonical witness order cannot repair these collisions because the bytes
and viewer eligibility to be ordered are themselves incomplete.

## 6. Section 14 persistence correction

The collision ledger separates retained experiment evidence from information
that history-equivalence forces across executions.  The corrected grouping is:

| Scope | MUST SURVIVE | MAY REBUILD | MAY FORGET | UNKNOWN |
|---|---|---|---|---|
| Manifest evidence | Controller table; selector association; complete branch records; crossed-A fact; actually observed reply/A/recovery bytes; exact pre-cut/request/T-phase distinctions; complete alternative family | Clean class label; FIN/terminal phase; residual; d; absence of interrupted R; post-FIN d | — | Claimed 315 recovery classification; specification/application identity; canonical codec/domain identity; combined May/Must |
| Between executions | Fourteen-way clean distinction; selector association; owed FIN-pending STOPPED; terminal no-more-C/R | Expected output bytes; residual fold; pre-FIN d | Complete branch records after external retention; proved clean same-class prefix; interrupted R debt; post-SELECT no-op identity; unused post-FIN d; unselected alternative after family retention | Claimed recovery-class responsibility; specification identity; controller policy; crossed-A fact; canonical codec/domain; combined May/Must; literal pre-A/post-A forgetting |

This is not a representation prescription.  In particular:

- an exact prefix can be indispensable evidence while being irrelevant to the
  selected service continuation;
- a phase coordinate can be rebuilt from a retained full prefix while its
  behavioral obligation still must survive somewhere;
- generated expected bytes are not proof that those bytes crossed an
  independently observed boundary; and
- moving a responsibility to controller, selector, capture peer, manifest,
  specification, or canonicalizer is EXTERNALIZE, not DELETE.

Rows lacking a same-kind permitted future or a total named derivation remain
UNKNOWN.  The equal T-before/T-after suffix does not justify MAY FORGET under
literal R0.1I because the cut kinds are incomparable.

## 7. Simultaneous total-system accounting

| Dimension | Current evidence | Feasibility status |
|---|---|---|
| Boundary behavior | Exact C/R/A/L/F grammar and projections; finite model enumerated | PASS at mathematical boundary only |
| Clean continuation | Counts, pair partition, and modeled congruence reproduce | PASS in model; Prediction 3's claimed minimum FAILS contractually |
| Recovery | Prefix inventory and transition behavior reproduce | FAIL as one contractual quotient: 238/415 literal versus 139/315 printed |
| Controller | CLIENT-only total-table grammar; conditional D recount | UNKNOWN availability, restart, unused-key identity, and realization |
| Scheduler | PUBLIC-prefix/next-crossing grammar and linear counts | FAIL for canonical identity because G has two closures; runtime UNKNOWN |
| Selector | OLD/NEW semantic association and branch order are exact | PASS in model; external selector/authority/availability UNKNOWN |
| Capture | A is an exact isolated crossing and scheduler-visible | Availability, durability, authenticity, and receiver effects UNKNOWN |
| Manifest | Complete F interleaving and branch evidence are required | No writer, subject binding, retention, replay, or severing evidence: UNKNOWN |
| Termination | FIN_PENDING and TERMINAL suffixes are distinct and exact | PASS in model; physical terminality/recovery UNKNOWN |
| Specification | Candidate bytes and hash are frozen | Identity does not cure internal contradiction or underdetermined algorithms: FAIL for reproduction |
| Canonicalizer | Primitive codecs mostly round-trip; malformed controls work | EncCut, branch population, G scope, mismatch result, and viewer eligibility incomplete: FAIL |
| Evolution | One E0-to-E1 transition and interrupted SELECT behavior are finite | PASS for bounded model; arbitrary/cross-version evolution UNKNOWN |
| Runtime/operations | One falsifier run has measured cost | Service runtime, cold start, resource bounds, fault injection, and monitoring UNKNOWN |
| Externalization | Influencing carriers are named | None was severed; all availability claims UNKNOWN |
| Cognition | Literal forks are documented | No controlled human trial; independent exact reproduction already fails |
| TCB | Influence inventory is named | Nothing was independently perturbed: UNKNOWN |
| Physical system | Candidate explicitly makes no media/power/corruption claim | UNKNOWN; exclusions receive no capability credit |

No scalar compression discharges another row.  The mathematical boundary can
pass while persistence, externalization, cognition, or physical realization
remains UNKNOWN.

## 8. Mandatory blind-attack verdicts

### 8.1 Individual attacks

| Attack | Verdict | Minimal reason |
|---|---|---|
| B00 Totality envelope | **FAIL** | Canonical input/output is not uniquely determined. |
| B01 Full history vs projection | PASS | Full traces, four projections, May, and Priv are distinct in the finite model. |
| B02 Viewer-relative explanation | **FAIL** | X exposes current coordinate, not viewer-valid causal/counterfactual lineage. |
| B03 Attempt/deny/apply/complete | UNKNOWN | No complete physical four-cut action experiment. |
| B04 Permission change | UNKNOWN | Authorization/privacy excluded and untested. |
| B05 Occurrence/application/completion | UNKNOWN | Abstract cuts exist; physical completion is not established. |
| B06 Crash after physical completion | UNKNOWN | Physical completion and receiver effects unobservable. |
| B07 Rejected/failed/no-op/success | UNKNOWN | No executable four-class attempt/evidence run. |
| B08 Truncation vs absence | UNKNOWN | No controllable window or capture-loss experiment. |
| B09 Labeled nondeterminism | PASS | Ordered OLD/NEW survives in Priv before projection dedup. |
| B10 Repetition/determinism | UNKNOWN | Model closure is finite; realization/TCB proof absent. |
| B11 Adaptive scheduler identity | PASS at model scope | One total controller/scheduler domain covers divergent paths. |
| B12 Lost adaptive context | UNKNOWN | No controller/scheduler severing or restart run. |
| B13 MAY vs MUST carriers | UNKNOWN | Fixed ten-proposition Must is not the arbitrary two-carrier query required. |
| B14 Empty-carrier vacuity | **FAIL** | Truth mask conflates vacuous truth with operational support. |
| B15 Projection carrier collision | PASS | Priv/SELECTOR retains hidden orientation before public merge. |
| B16 Exact depth boundary | PASS | d=3..0 accounting and forced FIN reproduce. |
| B17 Capability across crash phase | UNKNOWN | Consumption rule is formal; controller/manifest survival untested. |
| B18 Empty recovery drift | UNKNOWN | One crash only; zero/one/two-cycle experiment unavailable. |
| B19 Exhausted recovery | PASS in model | d=0 forces FIN and cannot resurrect ordinary allowance. |
| B20 Termination cuts | PASS in model | FIN-pending and terminal futures are exact. |
| B21 Crash as physical terminal | UNKNOWN | Irrecoverability and external observation untested. |
| B22 Post-terminal continuation | PASS in model | No later semantic C/R is generated. |
| B23 Canonical witness diamond | **FAIL** | Optional fields and viewer eligibility do not select one witness. |
| B24 External canonicalizer context | **FAIL** | Multiple frozen-text readings change bytes under one history. |
| B25 Evolution reinterpretation | UNKNOWN | Only fixed E0-to-E1 state evolution exists. |
| B26 Cross-version author/apply | UNKNOWN | No cross-version authored action experiment. |
| B27 Unknown future extension | UNKNOWN | Future extensions are unsupported, not handled. |
| B28 External controller context | UNKNOWN | Named but not held apart or severed. |
| B29 External capture omission | UNKNOWN | No independent physical history/capture-loss trial. |
| B30 External selector choice | UNKNOWN | Formal alternatives exist; selector perturbation did not run. |
| B31 Manifest/spec collision | UNKNOWN | No two independently distinguished governing bundles or TCB check. |
| B32 Human-local burden | UNKNOWN | No bound or controlled reviewer trial. |
| B33 Quantifier/vacuity cognition | UNKNOWN | Static vacuity failure exists; human study absent. |
| B34 TCB closure | UNKNOWN | No one-at-a-time perturbation. |
| B35 Circular validation | UNKNOWN | No independent realization oracle/shared-influence perturbation. |
| B36 Unlike realizations | UNKNOWN | No realization was built. |
| B37 Simulated vs physical completion | UNKNOWN | Physical completion is outside the evidence. |
| B38 Cross-realization witness | UNKNOWN | No unlike physical witnesses or context swap. |

### 8.2 Composite attacks

| Composite | Verdict | Reason |
|---|---|---|
| C1 Projection × action × crash | UNKNOWN | Projection is modeled; physical action completion/recovery evidence is absent. |
| C2 Nondeterminism × scheduler × evolution | UNKNOWN | Branch grammar exists; external recovery context and meaning-changing evolution do not. |
| C3 MAY/MUST × depth × recovery | UNKNOWN | Depth is exact, but required arbitrary predicate carriers and recovery run are absent. |
| C4 Terminal × physical realization | UNKNOWN | Formal terminal traces cannot establish physical terminality. |
| C5 Canonical × viewer × external context | **FAIL** | Orientation pair plus optional fields and viewer ambiguity is a finite counterexample. |
| C6 Human × TCB × vacuity | UNKNOWN | Vacuity evidence fails statically; human and TCB trials are absent. |

## 9. Section 13 simultaneous attack gate

| Attack | Verdict | Accounting |
|---|---|---|
| DELETE | UNKNOWN | No named implementation responsibility was removed and cold-started. |
| MERGE | **FAIL** | Printed 315 performs 100 class mergers forbidden by the same-kind relation. |
| DERIVE | UNKNOWN as an executed attack | D1-D3-style functions are mathematical; no target form was deleted and rebuilt. |
| RECOMPUTE | UNKNOWN | No restart without target state, dependency capture, or work measurement. |
| COLLIDE | **FAIL** | Canonical optional-field, G-scope, and witness-viewer readings collide. |
| FUTURE | **FAIL** | Zero-C privileged clean separator and literal 415 recovery future contradict predictions. |
| EXTERNALIZE | UNKNOWN | Named carriers were not severed; movement is not deletion. |
| REALIZE | UNKNOWN | No unlike realization or independent physical oracle. |
| COGNITION | **FAIL for exact reproduction; UNKNOWN for measured humans** | Two text-consistent quotient/canonical readings exist; no controlled study ran. |
| TCB | UNKNOWN | Inventory unperturbed. |

The persistence ledger further shows that expected-byte DERIVE, residual fold,
and allowance fold are mechanically total given named inputs.  That narrows
what a future attack must delete, but it is not RECOMPUTE, availability, cost,
or independence evidence.

## 10. Archive replay disposition

The quarantined replay finds genuine R0.1I repairs at the abstract boundary:

- SELECT-new is an application, so changing interrupted requests have one
  full-history fold per branch;
- public projection no longer stands in for full exact history;
- controller visibility excludes A/F while scheduler visibility includes A;
- one common truth-table grammar covers adaptive paths;
- FIN-pending and terminal suffixes are exact;
- both ATTEMPT gaps receive selector coverage; and
- branch records precede May dedup and carry a fixed Boolean Must vocabulary.

Those repairs move responsibility to F-bearing history, selector, branch
manifest, controller, scheduler, canonicalizer, capture peer, and exact
specification.  No movement is deletion, availability, unlike-realization, or
TCB evidence.  The archive adds no counterexample smaller than the fresh
same-kind, zero-C, and canonical-byte breaks.

## 11. Final feasibility verdict

R0.1I does not establish the first milestone.  It has a reproducible finite
corpus and several reusable semantic tests, but its claimed contractual
quotient is not its literal quotient, its claimed minimal clean separator is
not minimal, and its canonical witness algorithm cannot emit one uniquely
specified byte string.  Its persistence table also conflates manifest evidence
with information forced across executions.

The next candidate must, before any representation receives credit:

1. choose one cut comparability relation and recount every quotient under it;
2. make EncCut, branch population, repeated-field mismatch handling, G closure,
   Must history scope, and witness-viewer eligibility total;
3. retain the exact direct-versus-symbolic evidence boundary;
4. attach a permitted same-domain collision or total named derivation to every
   persistence verdict; and
5. run the still-UNKNOWN deletion, recomputation, externalization, realization,
   cognition, and TCB work before making physical or architectural claims.

Passing a corrected executable falsifier would establish only its bounded
contract behavior.  It would not by itself be an architecture, a persistence
mechanism, or a physical-system result.
