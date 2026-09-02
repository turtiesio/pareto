# ZERO GROUND R0.1K — Feasibility audit

## 0. Decision and claim boundary

FIRST MILESTONE: FAIL / NOT ACHIEVED.

R0.1K is finitely falsified before any subject execution. Its smallest decisive
byte-closure witness is fresh F01: an absent/unbound dependency and a dependency
bound to the legitimate opaque ASCII content `UNBOUND` both serialize as
`00000007554e424f554e44`, although a dependency-sensitive classification can require
`UNKNOWN:UNBOUND-DEPENDENCY` for the former and a decided answer for the latter.
This is a zero-encoded-byte-difference ambiguity between two proposed seal
dependency states. It is not literally a pair of candidate §2 boundary
histories, because dependency inputs were not first modeled as boundary
occurrences. It falsifies the affirmative canonical-seal and persistence
byte-closure claims; it does not by itself instantiate the candidate's
`encode(h1) = encode(h2)` history implication. The frozen encoding still cannot
preserve one distinction that its declared verdict contract requires.

There is also an independent process **FAIL**. The builder produced an initial
draft without prior conclusions, but before the final candidate was frozen a
builder-side advisory read the prior blind attack index, returned attacks
against draft SHA-256
`348ce5805d591df833810858ad1833e49e23c62511ecad8a84ea3b45420f7831`,
and the final candidate incorporated material fixes. The required sequence was
candidate freeze first, prior-counterexample replay second. The final
`c01da738...` bytes therefore cannot be credited as a clean-room candidate,
even though the later breaker and full archive replay are correctly ordered.

Fresh F02–F11 additionally record nonfunctional occurrence expansion,
different roots for purported common-root queries, phase poisoning after a
refusal, progress/script disagreement, inconsistent depth origins and bounds,
an exact capture payload that does not contain the promised bytes, an
unconstructible collision ledger, a nondetermined constructor called unique,
and an absent limited-viewer projection. The executable reports eleven FAIL,
four PASS, and four UNKNOWN checks under its own, differently numbered set. One
fresh depth witness is not directly executable-reproduced, while one additional
literal terminal-constructor mapping ambiguity is executable-only. Those scopes
are not silently equated below.

The verdict is about the frozen contract and corpus. No subject implementation
was supplied. Physical persistence, durability, human-local verification,
operational feasibility, global trusted-computing-base closure, and behavior of
materially unlike realizations remain **UNKNOWN**. A failed contract is not an
architecture; a repaired or passing contract would not be one either. This
audit selects no object, field, record, log, state machine, storage medium,
program, layer, or other representation.

No weighted scalar score, percentage, rank, or compensating aggregate is used.

## 1. Frozen artifacts and quarantine chronology

### 1.1 Commit and byte ledger

| Artifact | Commit | SHA-256 | Evidentiary role |
|---|---|---|---|
| `HISTORY-SEED-R01K.md` | `c01da738b38f65868e5c8af17d4823d2bc3f07a7` | `2ae3ac8fda2a78a0b1cd4eef45a8a9d412dc6617b3fff098f4f348855c8eb678` | Frozen candidate contract and finite corpus |
| `BLIND-ATTACK-PACK-R01I.md` | `7f60816df97bed16bcfc80f837528725e1efa4b8` | `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b` | Prior attack index properly admitted to the post-freeze breaker but improperly used by a builder-side pre-freeze advisory |
| `POSTFREEZE-BREAK-R01K.md` | `709faefb494f1273d7e32b6b1460ce7ce7b8b37b` | `9c78c4830db263e5e200923fc51a36edbd1f7f37b70f90d420aae1e0e3ac983b` | Independently fresh candidate-only break |
| `PERSISTENCE-COLLISION-LEDGER-R01K.md` | `019dad4ef52e748c4033cf6179d30a16aaf20c9f` | `a1237ba307a0043914887a925a66501207faeb45919d60c87f798a1f25b85793` | Audit-only information-responsibility classification |
| `r01k_history_experiment.py` | `1ea9b8bdb95c71fa6ff84aa26ecb18bbe069d762` | `52b0e3da349fbe5476dd68276992ecaa5dfb04572d4a90d3e8f02f36f07fabee` | Deterministic finite falsifier, not a subject |
| `ARCHIVE-REPLAY-R01K.md` | `095570c38afb5d8d05173112f322f11becf52e3b` | `3adb34bc1a2682f561f92978d5b4c6f6a6a9a3ac0dbd80e419d5f60962430891` | Post-break reconstruction of quarantined counterexample shapes |
| `EXPERIMENT-RESULT-R01K.md` | `4fa92f48eac392b25b1e8632f2e4a7e526788c47` | `06c729503440ca4828588992a372d94ee833d36e252c644ec7b19217b9195f90` | Corrected author and independent run record with explicit scope limits |

### 1.2 Two quarantine chronologies

The candidate-generation chronology **fails** the mandated quarantine:

1. an ontology-blind builder created an initial draft;
2. before that candidate was frozen, a builder-side advisory read the prior
   blind attack pack and the draft at SHA-256 `348ce580...`;
3. the advisory returned attack findings to the builder; and
4. the final candidate incorporated fixes that the archive replay explicitly
   traces to that advice, then froze at `c01da738...`.

Calling the pack ontology-independent does not change the timing rule. Prior
work was permitted to contribute attacks only after an independently specified
candidate had been frozen. An uncommitted draft is not that freeze, and a later
fresh breaker cannot retroactively restore it. There is no evidence that the
builder inherited an old proposed representation, but that narrower fact does
not cure the process violation.

The subsequent artifact chronology is nevertheless well ordered:

1. after `c01da738...`, the fresh breaker checked the candidate and blind-pack
   hashes before reading either, then attested that it used only those files;
2. it did not inspect Git history, prior candidates, full archives, audits,
   implementations, proposed solutions, or builder explanations;
3. the fresh report froze at `709faef...` before the full archive replay;
4. the persistence ledger read only the candidate and fresh report;
5. the full archive replay then imported prior work as counterexample shapes,
   not proposed representations; and
6. the executable pinned the candidate and fresh-report hashes, failed closed
   on a gate mismatch, and was recorded separately from the analytic audits.

This establishes a clean post-freeze breaker/replay order, not a clean
candidate-generation quarantine. Commit order and report attestations also do
not cryptographically prove cognitive or filesystem hermeticity.

## 2. What survived narrow checking

The candidate makes several useful scope choices: it starts with ordered
boundary histories, states one all-viewer future-observable equivalence, places
all declared coordinates in each leaf, separates retained evidence from
permitted continuation, retains per-obligation verdicts, refuses a weighted
score, and withholds physical and cross-realization claims without evidence.
These are constraints on a candidate, not evidence that its bytes satisfy them.

The fresh analysis found eleven narrow checks that survive at the level stated
in that report. The executable independently records only these four:

| Executable PASS | Established finite fact | Boundary that did not pass |
|---|---|---|
| `P01 written_leaf_abbreviation_counts` | The five written token scripts count `38/38/39/36/38` occurrences for `a/b/ab/n/u`. | F02 prevents promotion from abbreviation counts to exact byte histories. |
| `P02 five_carrier_quantifiers` | `{+,+,+,-,?}` gives MAY=TRUE and MUST=FALSE; deleting `n` makes MUST UNKNOWN. | The common-root execution, support, and carrier construction do not pass. |
| `P03 action_pair_arithmetic` | Eight labels have 28 unordered pairs; adding `completed` adds eight. | Arithmetic does not materialize history pairs or a collision ledger. |
| `P04 router_matrix_occupancy` | The displayed rectangle has 12 populated predicate rows and 10 operation columns. | Occupancy does not prove unique selection, reachability, lifecycle correctness, or totality. |

Other fresh narrow results include fail-dominance and empty-carrier truth-table
rules, exact longest-common-prefix mathematics for histories that are already
encoded, written CHUNK-plus-EXPIRE co-presence, and the absence of an
affirmative physical claim. None establishes a subject, persistence mechanism,
global quotient, global witness minimum, human usability, or total system.

## 3. Fresh finite failure boundary

The identifiers in this section are the independently fresh report's IDs.

| Fresh ID | Minimized collision or contradiction | Contract consequence and complexity transfer |
|---|---|---|
| F01 | Hold all other proposed seal bytes fixed. Unbound marker `UNBOUND` and bound opaque ASCII `UNBOUND` both encode as `00 00 00 07 55 4e 42 4f 55 4e 44`; a dependency-sensitive question requires UNKNOWN versus a potentially decided answer. This is an ambiguous seal/dependency-state encoding, not a §2 history pair. | Canonical-seal preservation and persistence byte closure FAIL. The missing type/presence distinction has been externalized to an ambient semantic convention. |
| F02 | One abbreviation is enough: `OCCURRED:R` permits at least `CUT|corpus-driver|OCCURRED|R` and `CUT|subject|OCCURRED|R`. `APPLICATION-UNRESOLVED` lacks a direction rule; EVD and terminal observation fields and `|` escaping are also incomplete. | Exact occurrence expansion is not a function. Authority, correlation, and parsing moved to undeclared runner defaults. |
| F03 | MAY is rooted at `<DECL>`; sequential MUST is rooted at `<DECL, REQ MAY, ANS TRUE>`. Their exact prefix difference is the MAY request and answer. | The asserted common root is false, and the intervening request shifts MAY depths from `6/6/5` to `7/7/6`. Branch cloning or semantic erasure is unstated work. |
| F04 | From observation-open, retain a refused EVOLVE request and `BUSY:observation` answer, then ask AUTHOR. Raw first-match predicates return `BUSY:evolution` instead of `BUSY:observation`. | A refused request manufactures phase. Acceptance/closure correlation moved to an absent lifecycle mechanism. |
| F05 | `REQ ATTEMPT; CUT OCCURRED`—and the analogous EVOLVE and TERMINATE fragments—contains no terminal ANS. The progress rule therefore owes `EXPIRE:operation`, which the exact scripts omit. | Written histories and progress closure disagree. An unstated correlator would have to decide whether a CUT closes a request. |
| F06 | At the declared singleton cut immediately before RECOVER, the continuation has one delivered request before APPLIED establishes `q`, not six. | The depth claim changes its origin. Root identity and request counting were left to an implicit controller. |
| F07 | Leaves with retained `CHUNK:a` and `CHUNK:b` both receive literal `ANS|audit|s1|CAPTURE|CAPTURED|retained`, which contains neither original chunk nor expiry bytes. | The exact post-terminal capture claim FAILS. Retention/projection work moved to an undeclared archive lookup or macro expansion. |
| F08 | F02 prevents exact `P_K`; decoder/withheld-answer mutants are categories rather than exact members. | The affirmative “complete” ledger claim FAILS because its carrier set is not constructible from frozen bytes. The separately absent materialized E cases and global enumeration make equality/minimality results UNKNOWN or unissued, not another independent FAIL. |
| F09 | `depth.full="6"` makes depth seven `OUT-OF-ENVELOPE`, while the same depth-seven singleton query is required to return TRUE. | The router has two required results for one prefix/request. Bound normalization is unstated. |
| F10 | The same pre-observation history and the same OBSERVE request admit first answers CHUNK `a` and CHUNK `b`, although `N(h,r)` is called unique. | Result selection is not a function. Selector identity or a complete answer-tree codec is absent. |
| F11 | Authorized limited OBSERVE routes to `N`, but every nonempty declared observation exposes token identity forbidden to `limited`; no exact generic/redacted constructor exists. | The two-viewer interface is not total as frozen. Projection, authorization, and proof move outside the contract. |

F01 is lexicographically decisive for the seal/persistence byte-closure claim:
it uses zero differing encoded bytes, no candidate history occurrence, one
dependency value, and one dependency-sensitive classification.
The other failures are retained because they expose independent responsibilities
even though no additional failure is needed for the aggregate verdict.

## 4. Executable falsification boundary

### 4.1 Reproduction

The executable performs nineteen named checks over constructed byte strings,
short histories, finite arithmetic, displayed tables, and pinned-text
contradictions. Both the author's post-commit run and an independent run from
`/root/pareto` reported:

| Measure | Result |
|---|---:|
| Exit status | 1 |
| PASS / FAIL / UNKNOWN | 4 / 11 / 4 |
| Wall time | 0.04 s |
| Maximum resident set | 18,688 KiB |
| Whole-stdout SHA-256 | `c6bfaddfbc6bb18569def1f40679d82bfed8e267e28cd220fd92ae9f972721c4` |

The independent wrapper additionally reported 0.03 s user CPU and 0.00 s
system CPU. Identical hashes reproduce the deterministic sorted JSON bytes for
those two runs. They do not establish a subject trace, service latency,
completeness, physical behavior, or architecture.

### 4.2 Executable IDs are not fresh-report IDs

| Fresh finding | Executable relation |
|---|---|
| fresh F01 | executable `F01 unbound_sentinel_collision` constructs the same ambiguous seal/dependency-state bytes. |
| fresh F02 | executable `F05 direction_expansion_and_cut_authority` checks the smallest direction/authority defect; executable `F11` observes the downstream inability to construct exact `P_K`. |
| fresh F03 | executable `F02 sequential_query_common_root` constructs the unequal roots and shifted depths. |
| fresh F04 | executable `F07 refused_evolve_phase_poisoning` constructs the refused-request future. |
| fresh F05 | executable `F06 successful_request_answer_or_expiry_closure` checks the CUT/ANS mismatch; executable F09 is related to the same constructor/routing surface. |
| fresh F06 | Not separately executed; it remains the analytic one-request pre-RECOVER depth witness. |
| fresh F07 | executable `F08 literal_retained_capture_payload` checks the literal answer. |
| fresh F08 | executable `F11 p_k_and_ledger_materializability` fails because exact `P_K` is unconstructible. The missing materialized E/global enumeration remains UNKNOWN or unissued rather than supplying an independent FAIL. |
| fresh F09 | executable `F03 depth_six_envelope_vs_depth_seven` checks the two required outcomes. |
| fresh F10 | executable `F04 unique_n_observation_collision` constructs the two admitted first answers. |
| fresh F11 | executable `F10 limited_viewer_observation_constructor` checks the missing legal projection. |
| executable F09 only | `terminal_matrix_vs_terminal_refusal` finds a matrix constructor label `TERMINAL` while the exact tail names `TERMINAL-REFUSAL`. Because the mapping from the label to exact answer bytes is incomplete, this is an additional literal constructor-mapping ambiguity, not necessarily two fully specified required answer byte strings and not fresh F09. |

The fresh analytic report remains the authority for its F01–F11 minima; the
program supplies reproducible bounded falsification, not a renumbering or
exhaustive replay.

The executable's UNKNOWNs are:

- `U01 implementation_conformance`: no subject, runner output, or subject trace;
- `U02 physical_and_unlike_realization_claims`: missing independent physical
  evidence and zero materially unlike realizations;
- `U03 global_support_minimality`: no complete universe or all-smaller-trie
  enumeration; and
- `U04 tcb_and_external_context_closure`: no finite perturbation surface,
  dependency inventory, or independent oracle.

It also does not enumerate all histories, continuations, viewers, authority
states, raw payloads, candidate representations, or equivalence classes. Its
runtime and memory are properties of this falsifier run only.

## 5. Persistence classification forced by the frozen contract

### 5.1 Two distinct duties

The ledger separates:

1. **behavioral continuation**—a future request returns different bytes; and
2. **claim evidence**—an issued PASS, FAIL, or UNKNOWN remains auditable only
   with its exact scope, sources, and support.

The candidate's affirmative audit-CAPTURE promise creates unusually strong
behavioral pressure. For any valid prefix `p` and one additional occurrence
`x`, it claims that one future audit CAPTURE distinguishes `p` from `p·x`, even
after `TERM-DONE`. Therefore exact audit-visible occurrence content, order, and
multiplicity are logically required by this frozen contract. F07 shows that the
literal CAPTURE response does not discharge that promise; this pressure is a
falsifier and lower bound, not an operational PASS.

### 5.2 MUST SURVIVE

These verdicts concern logical information and bindings while the associated
future or retained verdict remains in scope. They do not imply dedicated
constructors or physical locations.

| Information responsibility | Smallest forcing witness | Verdict boundary |
|---|---|---|
| Bound/unbound status and exact dependency content | Fresh F01: zero encoded-byte difference between proposed seal values for marker and bound raw `UNBOUND`; one dependency-sensitive classification requires UNKNOWN versus decided. | **MUST SURVIVE** under the verdict contract, but unrepresentable by the frozen codec. This is not yet a pair of §2 boundary histories. |
| Audit-visible HISTORY content, order, and multiplicity | `h0=p`; `h1=p·ANS|audit|s0|OBSERVE|CHUNK|a`; then one audit CAPTURE, including after terminality. | **MUST SURVIVE** under the affirmative CAPTURE contract. F07 prevents an exact PASS. A phase summary cannot derive the prefix. |
| Exact RULES content and binding | After captured `CHUNK:a`, vary a decisive rule byte and ask one INTERPRET or AUTHOR. | **MUST SURVIVE** while it can affect behavior or a retained derivation. A compiled view may be rebuilt only from the exact source. |
| Exact DECL scope | Vary a bound, viewer, specification, recovery, or terminal rule and deliver one affected request. | **MUST SURVIVE** for behavior and retained claim scope. Public `K/1` is not the content. |
| EVIDENCE bytes plus authority, interval, adjudication, and missingness | Hold history fixed; admitted apply-cut evidence versus MISSING followed by QUERY:q gives decided versus UNKNOWN. | **MUST SURVIVE** for every claim using it. F02 prevents a globally exact EVD pair; reacquisition would be new evidence. |
| Exact QUESTION and quantifier | Over `{+,+,+,-,?}`, MAY(q) and MUST(q) require TRUE and FALSE. | **MUST SURVIVE** so the verdict retains meaning. F03 blocks the claimed common-root execution but not this logical distinction. |
| SUPPORT for an issued verdict | Delete SUPPORT and validate the same retained seal; the claim becomes unsupported/unissued rather than remaining justified. | **MUST SURVIVE** as claim evidence. Ordinary subject behavior need not differ; no instantiated range-addressed C/D/E artifact passes here. |
| SUPERSEDES lineage and recoverable predecessor identity | Compare otherwise equal retained claims with `NONE` versus a predecessor reference; exact seal audit can distinguish conditionally, and lineage validation requires the predecessor. | **MUST SURVIVE** while lineage is asserted. No digest algorithm, collision claim, or predecessor durability is supplied. |

Repeated identical bytes may share a physical copy only if every logical
occurrence's position, multiplicity, authority, interval, scope, and seal
association remains exactly recoverable. This is lossless representation of a
surviving distinction, not permission to forget it.

### 5.3 MAY REBUILD / MAY RECOMPUTE

Only a materialization—not its decisive source information—may receive this
verdict, and only if regeneration is total, deterministic, byte-identical,
within every bound, and based on identified surviving specifications.
No row in the following table is an achieved current MAY REBUILD
classification; each states
conditions under which a future materialization could become eligible.

| Materialization | Required surviving basis | R0.1K disposition |
|---|---|---|
| Parsed or compiled RULES/DECL view | Exact authoritative bytes plus pinned total parser/canonicalizer | Conditional; parser/codec execution is absent and the frozen grammar fails. |
| Router phase/current index | Exact HISTORY plus total deterministic request/result correlation | **FAIL as frozen** through F04; no current phase is safely rebuildable under that rule. |
| Query result | Exact rules, declaration, history, evidence, dependencies, question, carrier set, and evaluator | Conditional in principle; **FAIL/UNKNOWN here** through F03, F06, F08, and F09. |
| C/D/E SUPPORT | All exact leaves, a complete finite search domain, global minimization, and canonical result bytes | **UNKNOWN**; no such run/archive exists and F02/F08 block the domain. Recomputed agreement is not independent evidence. |
| Duplicate serialization or cache | One lossless authoritative source and every association/order/multiplicity binding | Conditional only. |
| SUPERSEDES digest | Exact predecessor plus bound digest algorithm and format | **UNKNOWN**; neither algorithm nor durable predecessor is established. |
| Captured/evidence serialization | Raw bytes plus authority, interval, adjudication, scope, occurrence identity, and order | Conditional; the exact EVD and CAPTURE grammars fail or are incomplete. |

One narrower exception is demonstrated outside the candidate's persistent
contract: given the pinned source documents and the identified falsifier
algorithm, the four reported transcription/arithmetic materializations—leaf
counts, the five-carrier truth table, pair counts, and displayed matrix
occupancy—are **MAY REBUILD** as experiment-report data. This says nothing
about rebuilding exact histories, support, subject state, evidence, or a
retained system verdict.

### 5.4 MAY FORGET

No named seal responsibility and no audit-visible history occurrence is
unconditionally MAY FORGET while its verdict and CAPTURE/lineage contract
remain live. Conditional MAY FORGET candidates are limited to:

- compiler, parser, search, sort, and minimizer work caches after every required
  canonical artifact and source remains recoverable;
- process-local display details, object identities, or tie preferences proved
  unable to influence any output or canonicality claim;
- redundant physical copies after all logical bytes and bindings remain
  recoverable elsewhere;
- internal details proved unable to influence any admitted answer, progress
  result, selector, recovery, explanation, evidence, or claim; and
- physical or simulator facts never admitted as evidence and unused by every
  permitted proposition.

Because the TCB and influence domain are not closed, these are conditional
classes, not evidence that any concrete system safely forgot them. Abandoning a
claim and every future audit of it could end its claim-evidence duty, but that
is outside the candidate's promise to retain and supersede verdicts.

## 6. Simultaneous total-system accounting

No row offsets another.

| Dimension | Evidence and burden | Verdict |
|---|---|---|
| Information/distinction preservation | F01 maps required proposed seal bound/unbound meanings to identical bytes; F07 cannot return promised retained history distinctions. | **FAIL** |
| Persistent state | The contract forces logical history/seal responsibilities, but its codec and exact corpus fail; no physical medium or deletion/cold-rebuild run exists. | **FAIL** as frozen logical contract; physical persistence **UNKNOWN** |
| Semantic machinery | Common-root, depth, lifecycle, progress, unique-result, and viewer rules contradict their histories; the terminal-result constructor mapping is underdefined. | **FAIL** |
| Human cognition | Exact seals, global support enumeration, cross-section routing, authority binding, and viewer projections have no measured review time, comprehension, expertise, or error rate. | **UNKNOWN** |
| Authoring burden | Inline rule text is inspectable, but limited-viewer constructors and exact authority/occurrence authoring are incomplete; no authoring study exists. | Contract **FAIL**; human burden **UNKNOWN** |
| Query/navigation burden | MAY/MUST do not share a root; depth origin and depth seven conflict; no search/navigation infrastructure or discovery study was built. | Bounded contract **FAIL**; broader burden **UNKNOWN** |
| Runtime | The falsifier takes 0.04 s and 18,688 KiB in the reported runs. CUT-only success conflicts with the contract's progress rule; subject latency and liveness were not run. | Contract **FAIL**; physical/service runtime **UNKNOWN** |
| Storage | Exact inline histories, evidence, dependencies, support, and immutable lineage would need recoverability, but volume, write amplification, replication, retention, and durability are unmeasured. | **UNKNOWN** physically |
| Operations | Refused requests create false phases; driver expiry, crash/recovery evidence, monitoring, repair, backup, corruption, and power loss are untested. | Router lifecycle **FAIL**; deployment **UNKNOWN** |
| Trusted computing base | Dependency listing is not closure; F01 loses a trust-binding distinction; no perturbation surface or independent oracle exists. | **UNKNOWN** globally, with a finite encoding **FAIL** |
| Evolution | Inline `s0`/`s1` rules avoid some silent reinterpretation, but refused EVOLVE poisons routing and no migration/rollback execution exists. | Frozen routing **FAIL**; realized evolution **UNKNOWN** |
| Portability | Big-endian lengths and inline bytes are only a partial exchange rule; the grammar is nonfunctional and no second platform or implementation exists. | Exchange contract **FAIL**; empirical portability **UNKNOWN** |
| Explainability | Short X answers are not instantiated range-addressed D support; phase and projection defects can make explanations false or impossible. | Frozen contract **FAIL**; human usefulness **UNKNOWN** |
| Information-loss risk | F01 is an exact ambiguous seal-value encoding; F07/F08 lose or fail to construct evidence obligations. Media loss, corruption, recovery, and availability are unmeasured. | Logical risk **FAIL**; physical risk **UNKNOWN** |
| External services | Driver, capture authority, archive, selector, parser, canonicalizer, permission adjudicator, and evidence observer carry required work but were not severed or failed independently. | **UNKNOWN** |
| Physical and unlike realizations | Base evidence says `MISSING`; no physical completion, durable recovery, halt, or pair of materially unlike realizations is instantiated. | **UNKNOWN** |
| Research quarantine | A builder-side advisory used the prior blind attack index and changed the draft before final freeze; later breaker/replay ordering cannot repair that sequence. | **FAIL** |

## 7. Mandatory attacks and where the complexity is now

| Attack | R0.1K result | Where the complexity is now |
|---|---|---|
| DELETE | Delete the dependency binding and the question must become UNKNOWN; delete one audit-visible CHUNK and a later exact CAPTURE must differ. Delete SUPPORT and the retained claim loses justification. | Presence/type codec, lossless archive, evidence acquisition, and claim validator. |
| MERGE | Bound raw `UNBOUND` and the marker already collide exactly. Purportedly merging the MAY/MUST roots leaves a two-occurrence prefix difference; unique `N` merges distinct a/b branches. | Disjoint value encoding, branch/root identity, selector, and answer-tree serialization. |
| DERIVE | A phase summary cannot derive exact history; `CAPTURED:retained` is an undeclared macro; no exact range-addressed support is instantiated. | Surviving source bytes, reversible proof machinery, target resolver, and independent evidence authority. |
| RECOMPUTE | Counts and truth tables recompute narrowly. Router indexes, query answers, support, and lineage are conditional on sources and complete machinery that fail or remain absent. | Parser/canonicalizer, correlator, global minimizer, cold-start work, source availability, and TCB. |
| COLLIDE | F01 is the smallest exact seal-value ambiguity, not a constructed §2 history pair. F02 also permits multiple bytes for one abbreviation; F10 permits multiple answers for one purported function input. | Tagged/disjoint bytes, exact authority namespaces, and branch-choice evidence. |
| FUTURE | One AUTHOR after a refused EVOLVE exposes F04; the intervening query exposes F03; one RECOVER exposes F06; one depth-seven QUERY exposes F09. | Lifecycle correlation, common-root experiment construction, root-bound counters, and envelope policy. |
| EXTERNALIZE | K-CLOSE can falsify a tested omitted influence, but it cannot enumerate all influences; capture, driver, selector, archive, permissions, and adjudication remain external carriers. | Hermetic environment capture, service availability, identity binding, perturbation campaigns, and organizational procedures. |
| REALIZE | The candidate correctly refuses to infer physical completion or cross-realization equality from boundary labels, but performs no realization comparison. | Independent per-realization observers, clocks, failure injection, recovery evidence, and comparison predicates. |
| COGNITION | No human-local promise is made and no study runs. Global enumeration and incomplete exact grammar leave substantial unmeasured inference work. | Reviewer tools, access, expertise, protocol, authoring workflow, and error measurement. |
| TCB | Closure is expressly withdrawn; F01 demonstrates one lost dependency distinction; classifier/validator independence is untested. | Deployment inventory, trusted capture and codecs, one-at-a-time perturbation, and an independent adjudicator. |

After every apparent simplification, the complexity remains charged:

- replacing a stored semantic summary with exact history moves cost to
  lossless capture, authorization, retrieval, and archive durability;
- deriving rather than retaining a result moves cost to exact surviving
  sources, deterministic machinery, canonicalization, runtime, and its TCB;
- making specifications inline moves trust to their grammar, authority,
  interpreter, and historical binding;
- calling branches a single `N(h,r)` moves choice and tree identity to an
  external selector unless the contract carries them;
- retaining only a label or digest moves target selection and availability to
  a resolver and predecessor archive;
- using an external driver for progress moves liveness, expiry evidence, and
  request/result correlation to that driver; and
- withdrawing physical, human, portability, or TCB claims prevents a false
  PASS but leaves the required total-system responsibility unfulfilled.

## 8. Quarantined archive replay and pre-freeze contamination

The full archive replay against the final bytes was opened only after the
post-freeze fresh FAIL was frozen. It reconstructed prior counterexamples in
K/1's boundary-history terms and found **no new final-candidate failure family
and no smaller witness** than fresh F01–F11. In particular, no replayed archive
byte-closure attack can use fewer differing encoded bytes than F01; that
statement does not convert F01 into a §2 history pair.

That correctly ordered replay also discloses the earlier, distinct quarantine
failure: a builder-side advisory had already read the blind prior-attack index
before the final candidate freeze and its recommendations materially changed
the final bytes. Thus “no new post-freeze archive failure” is not evidence that
candidate generation was quarantined. The later replay cannot erase this
process FAIL.

The replay also records real improvements over earlier attack shapes,
including the pre-freeze advisory, without evidence that an old proposed
solution was imported: the application proposition is explicitly separated
from physical completion; unresolved application is placed before later
evolution; pending router rows and a driver-step progress bound are named;
global rather than deletion-only minimization is required as a criterion; the
K-CLOSE rule is conditional on bound content; physical-negative wording is
withdrawn; and the incorrect-MUST example is corrected. Several were only
partial repairs:
progress is not reconciled with CUT-only scripts, the exact alphabet and global
enumeration remain unavailable, and a refused request still poisons routing.

The record shows no imported old proposed representation, but prior work did
contribute attacks at the wrong pre-freeze time as well as during the allowed
post-freeze replay. The exposed work resides in byte typing/framing, authority
association, request/result correlation, branch identity, viewer projection,
root/depth accounting, evidence retention, ledger enumeration, and context
binding. Neither replay supplies subject, physical, cognitive, operational,
portability, storage, or trust evidence.

## 9. Final feasibility verdict

R0.1K is a useful bounded falsification target, but it is neither a valid
clean-room candidate nor the defensible first-milestone statement requested by
ZERO GROUND. Its final bytes incorporated prior attack advice before freeze.
Conditional on its own affirmative contract, the ledger can still identify
logical information that would have to survive: exact dependency
presence/content, audit-visible history occurrences and their ordering,
governing rules and scope, evidence and authority bindings, the question,
support for retained claims, and lineage. It can also identify conditions
under which materializations could become rebuildable and a narrow conditional
set of non-influencing intermediates that could be forgotten.

That is not yet the quotient or a valid representation of it. One required
distinction is unrepresentable by the frozen bytes; multiple required histories
are not uniquely encodable; the common experiment roots, router, progress rule,
viewer projection, and exact capture contract contradict themselves; and the
finite collision/equality domain cannot be materialized. Consequently the
audit cannot prove that every retained responsibility has an exact witness or
that every omitted item is future-inert.

Subject conformance, physical storage and survival between executions,
deterministic cold reconstruction, operational recovery, human authoring and
verification, global TCB closure, portability, and materially unlike physical
realizations remain UNKNOWN. None may be credited as zero complexity or as
implicitly supplied by a runtime, service, prompt, convention, or organization.

FIRST MILESTONE: FAIL / NOT ACHIEVED.

R0.1K is finitely inconsistent and its final candidate violates the mandatory
pre-freeze research quarantine. It yields conditional information
responsibilities and bounded falsifiers, not a defensible total-system quotient
or architecture. Physical, unlike-realization, cognitive, operational,
storage, and TCB capabilities remain UNKNOWN.

No representation, primitive, constructor, layer, package, storage mechanism,
program, or architecture survives merely because this audit names an
information responsibility. A future candidate must be frozen under a new
identifier and re-attacked from histories; this audit does not prescribe its
shape.
