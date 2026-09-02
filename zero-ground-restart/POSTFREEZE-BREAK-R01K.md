# ZERO GROUND R0.1K — Post-Freeze Fresh Break

Status: **FAIL** for the frozen candidate. This is a fresh, boundary-history
audit of the candidate contract, not a verdict on any implementation.

## 0. Freeze gate, quarantine, and provenance

The hashes were computed before either allowed input was read.

| allowed input | required SHA-256 | observed SHA-256 | gate |
|---|---|---|---|
| `HISTORY-SEED-R01K.md` | `2ae3ac8fda2a78a0b1cd4eef45a8a9d412dc6617b3fff098f4f348855c8eb678` | `2ae3ac8fda2a78a0b1cd4eef45a8a9d412dc6617b3fff098f4f348855c8eb678` | PASS |
| `BLIND-ATTACK-PACK-R01I.md` | `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b` | `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b` | PASS |

Allowed-input statement: this audit used only those two files. It did not list
or read any other repository file, Git history, prior seed, audit, archive,
ledger, implementation, solution, or post-freeze builder explanation. The
candidate was not edited. This report is the only file created by the audit.

The requested commit identifier `c01da738b38f65868e5c8af17d4823d2bc3f07a7`
was treated only as supplied provenance. It was not looked up.

## 1. Verdict and boundary of the verdict

The candidate fails before subject execution. At least one exact information
collision exists in the seal transport, several corpus occurrences have no
unique byte expansion, the two asserted common-root quantifier requests do not
share a history root in the written scripts, and a refused request can change
the router's later phase. Each is finite. Any one is enough for **FAIL** under
the candidate's own non-masking aggregation; all are retained below.

This does **not** turn absent execution evidence into a failure of a subject.
Subject conformance, physical completion, human-local validation, operational
durability, global TCB closure, and cross-realization behavior remain
**UNKNOWN**. Passing definitions or truth-table arithmetic would not establish
an architecture.

No scalar score, percentage, weight, or rank is used.

## 2. Independent audit method

The candidate's nouns were treated as claims to attack, not as an ontology to
inherit. The primitive used here is an exact pair of finite boundary histories
plus the shortest future that forces different answer bytes. A FAIL below is
either an exact byte collision or the smallest reachable written-history
contradiction. Where the candidate does not define enough bytes to construct a
test, the result is UNKNOWN/unsupported—except when the claim being tested is
itself that those exact bytes are defined.

Minimization followed the attack pack's lexicographic order: total occurrence
nodes, differing nodes, continuation requests, viewers, realizations,
nondeterministic choices, and varied external context. Shared prefixes are
counted once. No deletion-only check is reported as a proof of global witness
minimality.

## 3. Minimized finite failures

### F01 — `UNBOUND` has an exact opaque-content collision

**Result:** FAIL — canonical seal and information-preservation claims.

`DEPENDENCIES` accepts either an influence's exact opaque bytes or the literal
marker `UNBOUND`. The transport supplies no type/presence tag that distinguishes
the marker from legitimate exact content consisting of the seven ASCII bytes
`UNBOUND`.

The complete encoded value in both cases is:

```text
00 00 00 07 55 4e 42 4f 55 4e 44
```

Hold the dependency key and every other seal byte fixed:

```text
S0: dependency k is absent/unbound; value = marker UNBOUND
S1: dependency k is bound; its exact opaque content = ASCII UNBOUND
```

`encode(S0) = encode(S1)`, while the declared rule requires the first case to
derive `UNKNOWN:UNBOUND-DEPENDENCY` and permits the second to be decided. This
is zero history-occurrence difference, one dependency value, and one
dependency-sensitive question. No future search is needed. The analogous
`MISSING`/raw-`MISSING` ambiguity exists unless the unspecified evidence tuple
adds a discriminator; because that tuple grammar is absent, it cannot repair
F01.

Complexity was moved from the declared byte grammar to an ambient semantic
type distinction. A tagged union or disjoint encoding would have to own it.

### F02 — the purported exact occurrence expansion is not a function

**Result:** FAIL — exact byte grammar, leaf set, trace counts as byte histories,
and every construction depending on `P_K`.

The four CUT fields are `CUT|authority|kind|payload`, but ordinary abbreviations
such as `OCCURRED:R`, `APPLIED:R@s0`, `CRASH:...`, `EVOLVED:s1`,
`TERM-APPLIED`, and `TERM-DONE` supply no authority and no declared default.
Only `DECL:K/1` and the completion-observer expiry receive an explicit
authority. Thus even the one-token script fragment `OCCURRED:R` has multiple
admissible payloads, for example:

```text
CUT|corpus-driver|OCCURRED|R
CUT|subject|OCCURRED|R
```

Nothing in the allowed inputs selects one.

`APPLICATION-UNRESOLVED:capture-missing` is listed among non-request words but
is omitted from the rules assigning words to ANS, CUT, or EVD. The `u` leaf
therefore stops at one directionless occurrence. Likewise
`EVIDENCE:observation-authority:MISSING` does not supply all of
`EVD|authority|kind|payload` under any stated default.

Bare observation `EXPIRE`, `COMPLETE`, and `UNAVAILABLE` abbreviations also do
not state the mandatory ANS payload field. Nor is there an escaping or
forbidden-byte rule for `|`: the delivered bytes
`REQ|audit|s0|QUERY|MAY:q:depth=6|x` can be parsed either as a malformed
six-field request or as a QUERY whose argument contains `|x`. The decoder cases
therefore do not repair the occurrence grammar.

These are the smallest possible witnesses: one abbreviation each. An exact
byte witness for downstream ledger claims cannot be demanded from an expansion
that is not defined. The FAIL is against the candidate's affirmative claim
that every abbreviation expands to one exact direction-tagged payload.

Complexity was moved to runner defaults for authority, direction, and field
placement. Those defaults would become undeclared dependencies and would
invalidate byte closure.

### F03 — the two carrier queries do not have one exact common root

**Result:** FAIL — common-root carrier quantification.

The written common prefix contains, in order, `DECL`, the MAY request and its
answer, then the MUST request and its answer. Therefore the request roots are:

```text
r_MAY  = <DECL>
r_MUST = <DECL,
          REQ|audit|s0|QUERY|MAY:q:depth=6,
          ANS|audit|s0|QUERY|TRUE|witness=a>
```

Their exact prefix difference has an empty MAY suffix and the two displayed
occurrences in the MUST suffix. They are not the same history. If the requests
were intended as two experiments cloned from `<DECL>`, they cannot also be the
five-occurrence sequential prefix used in every reported leaf count. No rule
declares query occurrences semantically erasable, and the single equivalence
explicitly preserves order and multiplicity.

There is also a depth collision. From `r_MAY`, the later MUST query is one
delivered request in every written future before observation begins. The first
positive depths for the MAY request are therefore `a=7`, `b=7`, and `ab=6`,
not `6,6,5`. Reversing the query order merely moves the extra request into the
MUST carrier. Forking both from `<DECL>` repairs depth but contradicts the one
linear transcript and P02's token counts.

Complexity was moved to an unstated branch-cloning/snapshot mechanism and to
an unstated rule that prior queries do not change the carrier domain.

### F04 — a refused request poisons the first-match router

**Result:** FAIL — reachable-prefix routing, evolution phase, and response
explainability.

Use a valid K/1 prefix whose last occurrence is:

```text
REQ|audit|s0|OBSERVE|-
```

It is `observation-open`. Deliver:

```text
REQ|audit|s0|EVOLVE|s1
ANS|audit|s0|EVOLVE|BUSY|observation
```

The matrix calls `BUSY:observation` a bounded refusal and retains the request.
Nevertheless, the next cut satisfies `evolution-pending` because it contains
an evolution request and no `EVOLVED`. That predicate precedes
`observation-open`. A following

```text
REQ|audit|s0|AUTHOR|R
```

is consequently assigned `BUSY:evolution`, while the still-open observation
row assigns `BUSY:observation`. The same defect occurs with refused TERMINATE
and ATTEMPT requests: the phase predicates test stale request occurrence, not
accepted/pending lifecycle.

The minimized suffix is one refused request/answer plus one future request.
Deleting the future removes the observable contradiction; deleting the refusal
removes the false phase.

Complexity was moved from explicit request/result correlation to global
existential predicates over raw history. A byte-defined acceptance/closure
relation would have to carry it.

### F05 — exact scripts and the operation-progress rule disagree

**Result:** FAIL — progress closure for the written corpus.

An ATTEMPT in each action suffix is followed by a CUT such as `OCCURRED`, not by
an ANS. EVOLVE is followed by `EVOLVED` CUT, and TERMINATE by termination CUTs.
The candidate separately distinguishes answers from controlled cuts and says
that a *terminal answer* must close a delivered operation by driver step three,
otherwise the harness appends `EXPIRE:operation`. The exact scripts contain no
such terminal ANS or expiry for these requests, and their reported occurrence
counts leave no hidden occurrence for one.

The smallest fragment is one delivered ATTEMPT, one `OCCURRED` CUT, and the
step-three close. Literal application of the progress rule requires an expiry;
literal application of the script omits it. Treating a CUT as an ANS would be a
new grammar rule and would alter the claimed direction tags.

Complexity was moved to an unstated operation-correlator in the corpus driver.
The three-step number alone does not define closure.

### F06 — the singleton depth break changes its own root

**Result:** FAIL — exact depth prediction 13 and §7.3's recovery breaker.

The singleton `a` carrier is said to be cut immediately before its RECOVER
request, but the same paragraph says its first positive witness has request
length six. From the stated cut, the continuation

```text
RECOVER, RECOVERED:captured-application-not-yet-evidenced, APPLIED:R@s0
```

contains one delivered request; answers and CUTs do not consume request depth.
It establishes `q` at depth one under the candidate's own counting rule. The
length-six number is valid only from the earlier common declaration root, not
from the stated singleton recovery cut.

Because F02 withholds the CUT authority, this is the smallest exact token-level
witness rather than an encodable history. Either the cut description or the
depth-five/six prediction is false.

Complexity was moved to an unstated absolute-depth origin rather than carried
in the query's bound and history root.

### F07 — `CAPTURED:retained` cannot contain the claimed retained bytes

**Result:** FAIL — the exact post-terminal capture prediction.

The occurrence rules say table payloads are the exact colon-separated words
shown. Consequently every branch's post-terminal answer is the same payload:

```text
ANS|audit|s1|CAPTURE|CAPTURED|retained
```

Yet §6.5 says that answer includes the original observation chunks and their
`EXPIRE` marker. The displayed answer contains neither. In particular, the
answer is byte-identical for leaves whose retained observations contain
`CHUNK:a` and `CHUNK:b`; it cannot inline both distinct originals as claimed.
The originals remain earlier in `HISTORY`, but that is not the affirmative
claim that the CAPTURE answer includes them, and no pointer-resolution rule is
declared.

Complexity was moved to a reader that is expected to chase the enclosing seal
or interpret the prose word `retained` as an undeclared macro.

### F08 — the “complete” collision ledger has no constructible carrier set

**Result:** FAIL — ledger completeness as frozen; UNKNOWN for any unexecuted
subject pair.

`P_K` requires exact expansion of every script and mutant. F02 prevents that.
The §7.3 decoder and withheld-answer mutants also specify categories, not exact
payloads, arguments, base prefixes, driver records, or resulting occurrences.
Therefore `Pairs(P_K)` is not a finite set whose members can be reproduced from
the frozen bytes.

In addition, `L_K`'s comprehension stores only pairs having a distinguishing
continuation. The prose says nondistinguished pairs receive E support, but no
second set or exact E entries are supplied. The phase tables are generators,
not the promised expanded collision/equality ledger.

The smallest blocking member is the one directionless
`APPLICATION-UNRESOLVED` occurrence in `u`; removing `u` does not cure the
missing CUT authorities or unspecified mutants.

Complexity was moved to a future ledger generator, router implementation, and
test-run archive. A construction recipe is not persisted coverage.

### F09 — depth seven is both admitted and outside K/1

**Result:** FAIL — decoder/envelope uniqueness.

The literal declaration fixes `depth.full="6"`, and §7.2 sends known-operation
arguments outside K/1 to `OUT-OF-ENVELOPE`. Section 7.3 and prediction 13
nevertheless require the same singleton query to return true at depths six
*and seven*. Thus, at the same prefix, the exact request

```text
REQ|audit|s0|QUERY|MAY:q:depth=7
```

has two required results: `OUT-OF-ENVELOPE` from the frozen declaration and
`TRUE` from the depth breaker. Treating seven as a saturating query bound would
be a new rule absent from `DECL:K/1`.

Complexity was moved to an unstated bound-normalization policy in the router.

### F10 — `N(h,r)` is called unique where the same input branches

**Result:** FAIL — normal-result uniqueness; UNKNOWN for any intended
nondeterministic tree constructor.

At the shared pre-observation prefix, the same request

```text
REQ|audit|s0|OBSERVE|-
```

admits at least these two first answers:

```text
ANS|audit|s0|OBSERVE|CHUNK|a
ANS|audit|s0|OBSERVE|CHUNK|b
```

No earlier selector occurrence or bound selector bytes distinguish the runs.
Section 7.2 nevertheless calls `N(h,r)` the unique result. If `N` was intended
to denote the whole seven-branch answer tree rather than the answer returned by
one delivered request, that relational/tree constructor and its branch-choice
evidence are not defined. Either reading fails the stated unique byte result.

Complexity was moved to an external nondeterministic selector and to the trace
tree serializer.

### F11 — the limited viewer has no total exact observation route

**Result:** FAIL — frozen two-viewer interface; UNKNOWN for an implementation.

The authorized request

```text
REQ|limited|s0|OBSERVE|-
```

routes to `N`. Every exact observation sequence defined for N exposes `a`,
`b`, `a+b`, or `n` when it emits a chunk, while the literal permission rule
forbids token identity to `limited`. `DENIED` is reserved for an unauthorized
viewer, and no generic/redacted limited observation sequence is defined.
INTERPRET and AUTHOR have the same missing viewer-specific constructors.

The request can therefore either leak, be refused contrary to the admitted
matrix cell, or receive an invented response. None is the claimed unique,
byte-bound total answer.

Complexity was moved to an unspecified projection/redaction engine and its
permission proof.

## 4. Finite claims that did pass

These PASS results are deliberately narrow. None is an implementation or
architecture verdict.

| ID | finite tested claim | evidence and scope |
|---|---|---|
| P01 | freeze gate | Both allowed inputs matched their required SHA-256 before read. |
| P02 | token-level leaf counts | Recounting the written abbreviations, including two common query request/answer pairs, gives `a=38`, `b=38`, `ab=39`, `n=36`, `u=38`. F02 prevents promotion to exact-byte histories. |
| P03 | fixed-carrier quantifier arithmetic | For the declared vector `{+,+,+,-,?}`, MAY is true and MUST is false. Removing `n` makes MUST unknown while `u` remains. |
| P04 | fail dominance truth table | The stated finite aggregation orders FAIL before UNKNOWN before PASS and retains the per-member vector. An unrelated unknown cannot mask a known counterexample in that definition. |
| P05 | empty-carrier labels | The written rules make MAY false and label formal universal vacuity `VACUOUS`; they do not fabricate a carrier. No UI/comprehension claim follows. |
| P06 | exact-prefix mathematics | For two already-encoded finite sequences, longest common prefix and the two ordered suffixes are unique. This does not cure the non-encoding in F02. |
| P07 | local pair arithmetic | Eight action labels have `8 choose 2 = 28` unordered label pairs; adding `completed` creates eight new pairs. This is not proof that history pairs were enumerated. |
| P08 | written prefix/expiry co-presence | Each of the five leaf scripts retains a CHUNK and EXPIRE token (with `ab` retaining two chunks), and the no-chunk mutant does not derive a token. F07 separately defeats the exact capture-answer claim. |
| P09 | physical claim boundary | The base corpus does not affirm positive or negative physical completion, physical halt, or cross-realization equivalence. Boundary `APPLIED`, `CRASH`, and `TERM-DONE` are expressly scoped as boundary cuts. |
| P10 | matrix occupancy only | The displayed router rectangle has 12 predicate rows and all 10 named operation columns populated. F04/F05 show that occupancy is not reachable-prefix totality. |
| P11 | no scalar masking | The candidate contains no weighted conformance score and preserves coordinate/verdict vectors in its declared aggregation. |

## 5. UNKNOWN or unsupported claims

| obligation | result | why PASS is unavailable | where the burden now lives |
|---|---|---|---|
| subject conformance | UNKNOWN | The candidate expressly contains no subject execution evidence. | implementation and runner |
| all delivered-byte decoder cases | UNKNOWN | One specimen at lengths 0, 1, 256, and 257 plus one malformed case is not exhaustive over all payload bytes; no executable decoder/proof is supplied. | parser implementation and exhaustive test/proof |
| global C/D/E support minimality | UNKNOWN | The document declares global enumeration but supplies neither the enumeration nor a fully defined alphabet; the cited dependency/realization bounds are not enumerated in §5. | minimizer and evidence archive |
| `NONUNIQUE` on `ab` | UNKNOWN | The candidate itself makes it conditional on enumerating every smaller admissible trie; no such run is present. | global witness search |
| byte closure beyond F01 | UNKNOWN | `K-CLOSE` is a test schema, not perturbation evidence, and hidden influences are not finitely closed. | dependency discovery and TCB |
| viewer authentication | UNKNOWN | Viewer names occur in request bytes, but the authority fact, credential binding, and its exact occurrence grammar are absent. | authorization service and seal producer |
| full two-viewer routing in a subject | UNKNOWN | F11 fails the frozen exact constructor, and no implementation execution is available. | projection engine and permission adjudicator |
| versioned execution | UNKNOWN | Inline `s0`/`s1` text is finite, but no subject run or exhaustive old/future-version parser evidence exists. | interpreter and migration runner |
| response progress in a subject | UNKNOWN | The driver can emit expiry, but delivery, driver progress authority, wall-clock liveness, and subject availability are not established. | external harness and clock authority |
| immutable retention and supersession durability | UNKNOWN | No storage, availability, garbage-collection, digest algorithm, or old-seal retrieval evidence is supplied. | external append-only archive |
| explanations as replayable D support | UNKNOWN | The short X payloads are not the required range-addressed derivations, and exact SUPPORT bytes are not instantiated. | proof producer and authorized viewer tooling |
| human-local verification | UNKNOWN | The candidate expressly withdraws time, expertise, cognition, and access claims. | reviewer, tools, and organizational process |
| physical completion/recovery/termination | UNKNOWN | Required independent physical evidence is `MISSING` in the base corpus. | physical observer and adjudicator |
| materially unlike realizations | UNKNOWN | None are instantiated, so no portability or cross-realization evidence exists. | per-realization harnesses and observers |
| TCB closure | UNKNOWN | The candidate expressly withdraws closure and gives no finite perturbation surface. | deployment inventory and independent oracle |
| storage/runtime/operational feasibility | UNKNOWN | Seal size, proof-search work, write amplification, latency, recovery cost, and archive growth are not bounded as an architecture. | implementation architecture and operations |

## 6. Mandatory formal-check disposition

| required check | disposition | independent finding |
|---|---|---|
| exact byte grammar | FAIL | F01 sentinel collision and F02 nonfunctional expansion. Map entry schema, duplicate-key rule, request escaping, and evidence tuple framing are also unsupported. |
| every reachable prefix/router phase | FAIL | F04 gives a reachable refused-request phase collision. Raw-existential predicates do not correlate request acceptance and closure. |
| progress bounds | FAIL for written scripts; UNKNOWN for a subject | F05. The three-step rule is finite but not reconciled with CUT-only operation suffixes. |
| depth counts | FAIL | F03 adds the intervening MUST request to the MAY futures; F06 makes the stated pre-RECOVER root depth one; F09 conflicts at depth seven. The isolated branch request counts `a=6`, `b=6`, `ab=5`, `n=6` pass only after an unstated fork from `<DECL>`. |
| common-root carrier quantification | FAIL | F03. Sequential MAY and MUST requests have different exact histories. |
| MAY/MUST/UNKNOWN aggregation | PASS as a finite truth table | P03–P05. Exact support and common-root execution remain UNKNOWN/FAIL separately. |
| fail dominance | PASS as a rule | P04; it makes this report's final verdict FAIL despite unrelated unknowns. |
| partial-prefix plus expiry retention | PASS in the earlier leaf history; FAIL at exact post-terminal answer | P08 and F07. Retained history is not the same as the claimed capture payload. |
| context binding | FAIL at transport; UNKNOWN globally | F01; K-CLOSE cannot prove an unknown influence absent. |
| viewer/authority/version behavior | FAIL as frozen; UNKNOWN in a subject | F11 has no legal exact limited OBSERVE result. Authority binding and execution are also absent. |
| ledger completeness | FAIL as frozen | F08. The intensional recipe cannot yield exact `P_K`, and no E-ledger is materialized. |
| true global versus local minimization | PASS as stated criterion; UNKNOWN as result | §4.3 correctly rejects deletion-only minimality, but no global enumeration evidence exists. |
| physical-negative claims | PASS only as a nonclaim | The base does not infer physical non-completion from expiry or silence. No physical proposition passes. |
| unlike realization boundaries | PASS as a scope withdrawal; UNKNOWN empirically | Evidence transfer is prohibited, but there are no two unlike runs. |

## 7. Simultaneous total-system dimensions

The dimensions are kept together; this table is not a score and no row can
average away another.

| dimension | disposition | joint consequence and complexity transfer |
|---|---|---|
| information preservation | FAIL | `UNBOUND` collides with valid opaque content, and exact capture bytes do not carry the promised retained data. A tagged transport and archive must own the distinction. |
| persistent state | UNKNOWN | Immutable seals are a requirement, not storage. Durability, retrieval, supersession, and old-seal preservation move to an external archive. |
| semantic machinery | FAIL | Common-root and phase semantics contradict their written histories. Correctness moves to an unstated experiment cloner and lifecycle correlator. |
| cognition | UNKNOWN | Human validation burden is withdrawn; global support enumeration may be enormous. Burden moves to reviewers and proof tooling. |
| authoring | FAIL/UNKNOWN | Inline authorization rules are inspectable, but F11 leaves limited author/interpret constructors undefined; authority and executed transitions are absent. Burden moves to interpreter, projection, and authorization evidence. |
| query/navigation | FAIL | MAY/MUST are not rooted together, the sequential query changes depth, the recovery breaker changes origin, and depth seven is both admitted and out of envelope. Branch cloning, carrier identity, and search move to the runner. |
| runtime | FAIL for contract consistency; UNKNOWN physically | CUTs do not close operations under the stated ANS rule. Actual delivery/liveness is externalized to the driver. |
| storage | UNKNOWN | Inline rules/history/evidence/dependencies/support and immutable superseding seals imply replication and archive growth with no resource claim. Cost moves to the corpus store. |
| operations | FAIL for router lifecycle; UNKNOWN for deployment | Refused requests can manufacture phases. Monitoring, expiry, crash evidence, and repair remain harness/operations work. |
| TCB | UNKNOWN | Dependency listing is not closure, and sentinel encoding loses a trust distinction. Discovery and independent validation stay outside the formalism. |
| evolution | FAIL for reachable routing; UNKNOWN in a subject | `s0`/`s1` bytes are finite, but a refused EVOLVE creates false pending state and no implementation run exists. Migration machinery owns the rest. |
| portability | UNKNOWN | Canonical endianness helps only after grammar repair; no unlike realization or external-authority portability is demonstrated. Per-realization adapters own it. |
| explainability | UNKNOWN/FAIL | X prose is not instantiated D support; F04 can make phase explanations false. Proof serialization and viewer projection own validity. |
| loss risk | FAIL for representational distinction; UNKNOWN operationally | A bound dependency can be indistinguishable from unbound, and old seals can be unavailable without contradicting any tested runtime claim. Risk is transferred to encoding and archive operations. |

## 8. Mandatory transformation-attack ledger

All ten mutations were considered against every persisted responsibility:
seal/encoding, history and prefix difference, retained evidence, support,
aggregation, carrier/depth query, viewer/version/authority, router/progress,
collision ledger, supersession/storage, explanation/cognition, and physical or
cross-realization claims. The first table records mechanism coverage; the
second retains the operator-specific minimized result. “Moved to” is mandatory
because deleting a noun does not delete its work.

### 8.1 Persisted-mechanism coverage

| persisted responsibility | decisive disposition | where complexity moved |
|---|---|---|
| canonical seal and dependency binding | FAIL (F01) | tagged serialization, dependency inventory, canonicalizer, TCB |
| exact occurrences and finite histories | FAIL (F02) | runner defaults, authority assignment, request/answer correlator |
| prefix difference and future equivalence | PASS only after histories are encoded | unbounded experiment quantification and bounded witness runner |
| retained evidence versus continuation | FAIL/UNKNOWN (F07) | external archive, capture projection, post-terminal audit service |
| C/D/E support and minimization | UNKNOWN | proof engine, range-addressed artifacts, global enumerator |
| three-valued verdict/aggregation | PASS as finite logic | carrier adjudication and complete evidence acquisition |
| K/1 carrier set and depth | FAIL (F03, F06, F09) | experiment cloning, root identity, bound normalization, depth counter |
| viewer, authority, and version | FAIL/UNKNOWN (F11) | authentication, permission projection, interpreter/migration TCB |
| router, decoder, and progress | FAIL/UNKNOWN (F04, F05, F09–F11) | explicit lifecycle machine, parser proof, selector, driver/clock |
| phase-collision ledger | FAIL as persisted artifact (F08) | generator, exhaustive execution, result archive |
| immutable supersession and storage | UNKNOWN | content-addressed durable storage and retention operations |
| physical and unlike realization | UNKNOWN by scope | independent observers and realization-specific adjudicators |
| explanation and cognition | UNKNOWN | proof presentation, reviewer access, expertise, and measurement |

### 8.2 Operator-specific results

| operator | minimized attack and result | where complexity moved |
|---|---|---|
| DELETE | Delete one dependency binding: the intended result becomes UNKNOWN, but F01 shows raw `UNBOUND` cannot be distinguished from that deletion. Delete a CHUNK and the written rule correctly withholds token derivation. | presence tags, evidence acquisition, archive retention |
| MERGE | Merge bound raw `UNBOUND` with the marker: exact seal collision (FAIL). Merge the two query roots: their two-occurrence PD remains (FAIL). F10 merges distinct a/b answers under one allegedly unique N. | disjoint encoding, branch identity, selector, projection engine |
| DERIVE | C/D/E rules prohibit self-assertion and physical derivation on paper (PASS criterion), but no range-addressed support bytes exist (UNKNOWN), and `CAPTURED:retained` derives content from a label (F07). | proof producer, evidence resolver, independent oracle |
| RECOMPUTE | Immutable old seals prevent in-place promotion by rule, but recomputation has no execution/TCB evidence and supersession depends on an external old-seal archive (UNKNOWN). | content-addressed store, dependency capture, replay runner |
| COLLIDE | F01 is an exact sentinel collision; F02 permits authority/default collisions; `NONUNIQUE` correctly avoids claiming a canonical a/b winner but remains unexecuted. | tagged bytes, authority namespace, global minimizer |
| FUTURE | One AUTHOR after a refused EVOLVE exposes F04. The later common query exposes F03's off-by-one. One RECOVER exposes F06, and the depth-seven request exposes F09. | lifecycle correlator, root-bound depth accounting, bound policy |
| EXTERNALIZE | K-CLOSE makes a useful falsifier, but no finite set of all external influences exists in the evidence; hidden context remains UNKNOWN. | hermetic runner, environment capture, perturbation campaign |
| REALIZE | The base correctly refuses physical and cross-realization conclusions, so no false PASS is issued; all realization obligations remain UNKNOWN. | per-realization physical observers, clocks, failure injectors |
| COGNITION | No local-verification promise is made. The seal and global-minimization duties therefore provide no bounded human answer (UNKNOWN rather than PASS). | reviewer tooling, access, expertise, study design |
| TCB | The candidate expressly withdraws closure; F01 additionally loses a trust-binding distinction. Tested perturbations could falsify but cannot close the surface. | deployment inventory, trusted measurement, independent adjudicator |

## 9. Independent small-collision summary

| order | pair | differing material | shortest discriminator | result |
|---|---|---|---|---|
| 1 | bound dependency bytes `UNBOUND` / unbound marker | zero encoded bytes | dependency-sensitive classification | exact collision; FAIL |
| 2 | MAY root / asserted common MUST root | two exact query occurrences | direct PD | roots unequal; FAIL |
| 3 | observation-open / same history after refused EVOLVE | refused request+answer | AUTHOR | `BUSY:observation` versus `BUSY:evolution`; FAIL |
| 4 | retained `a` / retained `b` post-terminal histories | at least CHUNK byte | CAPTURE | identical literal `CAPTURED:retained` cannot include both originals; FAIL |
| 5 | pre-RECOVER singleton at claimed depth five / its one-request recovery future | RECOVER request | APPLIED CUT | q is reachable at request depth one; FAIL |
| 6 | K/1 depth-six envelope / depth-seven breaker | one argument byte | QUERY at depth seven | OUT-OF-ENVELOPE versus TRUE; FAIL |
| 7 | common pre-observation `(h,r)` / same `(h,r)` | zero prefix/request bytes | first observation answer | CHUNK a versus CHUNK b despite unique N; FAIL |

No claim is made that this is the globally smallest set across an undefined
`P_K`. Each row is individually deletion-reduced at the level the candidate
actually encodes. F01 is the smallest decisive exact-byte witness.

## 10. Final verdict

**FAIL.** F01 alone falsifies information-preserving canonical transport.
F02–F11 independently falsify exact corpus, common-root/depth, routing and
progress, retention-answer, ledger, normal-result uniqueness, envelope, or
viewer-totality claims. Under the declared fail-dominant aggregation, the
simultaneous UNKNOWN obligations do not mask these failures.

The frozen candidate's own freeze rule says that repairing an occurrence
grammar, semantic rule, reachable phase, bound, or dependency requires a new
candidate identifier and audit. A passing revision would still be a formal
contract and breaker corpus—not evidence of a feasible runtime, storage,
operational, cognitive, physical, or portable architecture.
