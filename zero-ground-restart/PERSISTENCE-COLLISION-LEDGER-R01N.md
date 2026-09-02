# ZERO GROUND R0.1N — post-attack persistence-collision ledger

## 0. Verdict, authority, and scope

**FIRST MILESTONE: FAIL / NOT ACHIEVED.**

This ledger classifies information responsibilities discovered by attacking
the frozen R0.1N candidate. It does not select, repair, or propose an
architecture, representation, field set, layer, or physical realization.

Only these four frozen artifacts were admitted. Their hashes were verified
before semantic reading:

| Artifact | Verified SHA-256 | Role |
|---|---|---|
| `HISTORY-SEED-R01N.md` | `10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7` | Frozen candidate |
| `POSTFREEZE-BREAK-R01N.md` | `f00a9841cc9baaa349ff9300f85a8b6a68293e91af560452cf7c2d463bd9773a` | Independent break and minimized attacks |
| `r01n_history_audit.py` | `afb21585f1b9523f16f6fb4d3d647eadac5c461d30de8cda92f19ecd40f18f49` | Pinned executable falsifier |
| `EXPERIMENT-RESULT-R01N.md` | `c02d41b50c2a700d93ccfaf4f0807c18ac6e2897296763db24a566e5f1df4c41` | Pinned 6 PASS / 3 FAIL / 11 UNKNOWN run record |

No prior-round artifact, Git history, network source, or other repository file
was used.

The verdict is split into three noninterchangeable scopes:

1. **Unconditional abstract-history results** concern already-given finite
   sequences of `(direction,payload)` occurrences and finite byte strings with
   a supplied extent. They do not require C01 request execution.
2. **Conditional quotient verdicts** apply only if one fixed raw-audit future
   is adopted with exact snapshot binding, request/response capture, and
   deterministic boundary behavior. This antecedent is analysis scope, not a
   repair made by this ledger.
3. **Missing/UNKNOWN total-system capabilities** remain unclassified as
   MUST/MAY history state because the required semantics or evidence do not
   exist.

Fixed contract bytes, decoder conventions, and specification text are not
quotient-derived history information. They are separately charged external
parameters and trusted machinery.

## 1. Evidence metrics and verdict discipline

The post-freeze breaker used distinct metrics for distinct failure categories:

```text
Mpair = (total occurrences across the pair,
         total payload bytes across the pair,
         total P01 bytes across the pair,
         lexical endpoints)

Mcorr = (source P01 byte length,
         changed-bit count,
         source-history rank,
         changed byte index,
         bit mask)

Mmissing = (initial occurrence count,
            future-request count,
            explicit argument-byte count,
            lexical request description)
```

A missing transition definition is not called a pairwise collision. A
valid-to-valid corruption is not called an encoder collision. A bounded absence
of collisions is not called a global proof. UNKNOWN cannot erase a finite
FAIL, and a formal PASS cannot establish physical persistence.

The frozen experiment's pair metric omits the P01-byte coordinate and breaks
some equal-metric bucket ties by enumeration order. Its reported minima remain
exact within that disclosed bounded procedure, but not globally canonical over
all histories, request sequences, programs, crash schedules, or realizations.

## 2. Unconditional results over already-given abstract histories

### 2.1 Abstract sequence and P01 parsing

Given an already-existing finite ordered history, the abstract information is
the sequence itself. Given a finite P01 byte-string value whose total extent is
already supplied, canonical frame parsing recovers at most one such sequence:

- a direction byte is `00` or `01`;
- a shortest-form ULEB determines one payload length;
- that many payload bytes determine the next frame boundary; and
- parsing repeats until the supplied byte-string end.

This is a mathematical injectivity result for P01 over valid abstract
histories. It does not establish C01's future equivalence, physical durability,
integrity, availability, or minimality.

The bounded evidence is consistent with the parsing argument:

| Corpus/check | Exact bounded result |
|---|---:|
| Frozen public histories | 585 histories, 585 P01 encodings |
| Frozen built-in fresh histories | 157 histories, 157 P01 encodings |
| Selected P01 ULEB tiers | payload lengths `0,1,2,127,128,129,16383,16384,16385` round-trip in both directions |
| Additional breaker corpus | 343 histories, no P01 collision |
| Exhaustive raw strings of length 0 through 2 | 65,793 tested; three accepted, each canonical on re-encode |

These results establish neither an exhaustive all-history run nor a physical
subject.

### 2.2 Deterministic functions of an exact abstract sequence

If the exact abstract sequence and the identified algorithm are available,
the following facts are mathematical functions of that sequence:

- occurrence count;
- frame/occurrence offsets under a named encoding;
- first, last, or indexed occurrence;
- direction counts and other exactly specified folds; and
- the P01 byte string itself under the frozen P01 codec.

This establishes derivability, not persistence. It does not show that the
source sequence, codec, memory, CPU, or implementation survives a restart.

### 2.3 What is not an unconditional quotient verdict

No unconditional MUST SURVIVE or MAY FORGET verdict follows merely from naming
an abstract sequence. Necessity depends on permitted future behavior, and C01's
captured request/response transition is incomplete. Likewise, P01's literal
direction byte and ULEB digits are coding choices, not independently forced
history facts.

## 3. Conditional raw-audit quotient

### 3.1 Conditional antecedent

The following classification applies only if a clarified, fixed raw-audit
future supplies all of these properties:

- the same snapshot-bearing request can be applied to both histories;
- snapshot binding has one exact relation to request capture;
- request and response occurrences have exact deterministic bytes, directions,
  and order; and
- byte-exact extent and indexed occurrence observations are total on their
  declared domains.

Frozen C01 does not currently supply those properties. They are stated only to
make the conditional lower bound explicit.

### 3.2 Normalized MUST SURVIVE responsibility

Under that antecedent, there is one quotient-derived responsibility:

> Enough information must survive to reconstruct the exact finite ordered
> sequence of boundary occurrences.

This single responsibility entails recoverable sequence extent, occurrence
boundaries, order, multiplicity, every direction value, every payload extent,
and every payload byte. These are aspects of one sequence, not a mandate for
separate fields or duplicate state.

The minimized witness basis is:

| Distinction attacked | Exact pair | Leading `Mpair` coordinates | Conditional common raw observation |
|---|---|---|---|
| Sequence extent / one occurrence | `()` versus `((0,empty),)` | `(1,0,2)` | With pre-request snapshot binding, fixed `LENGTH(1)` gives `REJECTED` versus `1` |
| Direction value | `((0,empty),)` versus `((1,empty),)` | `(2,0,4)` | Fixed `AT(snapshot=1,index=0)` returns unequal pairs |
| Empty versus one-byte payload | `((0,empty),)` versus `((0,00),)` | `(2,1,5)` | Fixed `AT(1,0)` returns unequal payloads |
| Payload byte value | `((0,00),)` versus `((0,01),)` | `(2,2,6)` | Fixed `AT(1,0)` returns unequal payloads |
| Occurrence boundary/framing | `((0,00),)` versus `((0,empty),(0,empty))` | `(3,1,7)` | Fixed `AT(1,0)` returns `00` versus empty |
| Multiplicity | `((0,empty),)` versus `((0,empty),(0,empty))` | `(3,0,6)` | With pre-request binding, fixed `LENGTH(2)` gives `REJECTED` versus `2` |
| Order | `((0,empty),(1,empty))` versus `((1,empty),(0,empty))` | `(4,0,8)` | Fixed `AT(2,0)` returns opposite directions |

The lexical endpoint coordinate completes each metric but is omitted from the
compact table. The witnesses force information, not P01 syntax.

No successful merge of two distinct abstract histories is known under this
conditional identity quotient. The bounded P01 searches found no pairwise P01
collision; the parsing proof supplies the stronger mathematical P01 result
only when the encoded byte-string extent is already available.

### 3.3 Frozen LENGTH/AT harness futures are surrogates

The executable future named `LENGTH` is `lambda h: len(h)`. For the smallest
pair `()` and `((0,empty),)`, it returns `(0,1)`. Frozen C01 requires an explicit
snapshot argument. Before request capture, fixed requests give:

```text
LENGTH(0) -> (0,0)
LENGTH(1) -> (REJECTED,1)
LENGTH(2) -> (REJECTED,REJECTED)
```

No fixed request yields the harness pair `(0,1)`. The harness `AT(i)` likewise
omits `snapshot`, and its APPEND functions concatenate an occurrence directly
without captured CROSS/query traffic. The view, interpretation, action, and
explanation functions are Python projections, not encoded RUN programs.

Therefore harness witnesses translate into C01 persistence witnesses only
conditionally, through the fixed raw-audit antecedent above. They are not
actual frozen C01 continuation traces.

## 4. Conditional MAY REBUILD and MAY FORGET

### 4.1 MAY REBUILD

Given the conditional MUST information plus an identified exact specification,
these separately materialized results may be rebuilt:

| Derived material | Exact source | Conditional verdict and displaced cost |
|---|---|---|
| Count | Exact sequence | MAY REBUILD by scan; CPU, latency, and scanner correctness remain |
| P01 offsets/index/navigation tables | Exact P01 bytes, supplied byte extent, and frozen codec | MAY REBUILD; memory, cold-query time, and decoder TCB remain |
| Last occurrence and direction counts | Exact sequence and named fold | MAY REBUILD; no separate persistent copy is forced |
| P01 bytes or another identified encoding | Exact sequence plus that codec | MAY REBUILD as a representation form; codec availability and output extent remain |
| A deterministic view/query result | Exact sequence plus exact algorithm and version | MAY REBUILD only if the result did not itself cross and no later contract relies on its historical occurrence |

The redundant bundle `(transcript,count,last,direction-0-count)` deletes count,
last, then direction count and reaches `transcript` as its greedy fixed point.
That is a conditional component-deletion result for one supplied bundle, not a
proof that a literal transcript component is globally minimal.

Generic “hash,” “view,” “policy,” or “configuration” does not receive a blanket
MAY REBUILD verdict. The exact algorithm and version must be identified. A
fresh hash computed from corrupted bytes cannot reconstruct the earlier
integrity reference. E01 traces and installed policy state are not presently
MAY REBUILD because E01 and installation semantics are incomplete.

### 4.2 MAY FORGET

Under the same fixed contract, the following nonhistory distinctions may be
forgotten only after their stated exposure window closes:

- a completed decoder cursor after its scan;
- temporary evaluator stack/list cells after a completed request and all
  required boundary responses have crossed;
- cache eviction order;
- host object identities, allocation addresses, scheduler choices, and clocks
  that never crossed and cannot affect a permitted future; and
- abandoned author drafts that never crossed.

No occurrence, order, multiplicity, direction, or payload distinction may be
forgotten under the conditional identity quotient. Because frozen C01 does not
define capture, crash, or RUN completely, actual execution-level eligibility
for these forgettings remains conditional rather than an operational PASS.

## 5. External roots and representation-boundary responsibilities

### 5.1 Fixed specifications are not quotient history state

The following are required interpretive or operational dependencies, not
history-derived quotient information:

- the boundary alphabet and direction convention;
- C01 request/result grammar and snapshot semantics;
- request/response capture order and serialization;
- decoder selection, P01 direction convention, ULEB grammar, and canonicality
  rule;
- E01 program grammar, opcode semantics, `mode`, fuel, trace, and effect rules;
  and
- adapter, decoder, scanner, store, durability, evaluator, effect driver, and
  conformance implementations.

They belong in specification/TCB accounting. Calling them MUST SURVIVE history
would double-count a fixed semantic root; omitting their availability would
wrongly credit externalized complexity as zero.

### 5.2 P01 extent/EOF externalization

P01 frames are self-delimiting, but a complete P01 history word is terminated
by the supplied byte-string end. Exact evidence is:

```text
encode(((0,empty),))                 = 0000
encode(((0,empty),)) || encode(...) = 00000000
encode(((0,empty),(0,empty)))        = 00000000
```

Thus concatenating two one-occurrence history words is indistinguishable from
one two-occurrence history unless an external container extent/EOF identifies
the word boundary. This is not a collision between P01 encodings when each
finite byte-string value already includes its extent. It is a representation
boundary that P01 externalizes.

The extent/EOF mechanism must exist somewhere for physical decoding, but it is
not a separate C01 quotient fact and is not the same responsibility as the
recoverable number of occurrences.

## 6. Storage comparison, integrity, and capacity

### 6.1 Packed-code comparison without total dominance

The audit encodes each occurrence as
`ULEB((payload-length << 1) | direction) || payload`. Over the combined 585
public and 157 built-in fresh corpus instances:

| Measure | P01 | Packed code |
|---|---:|---:|
| Total encoded bytes | 12,566 | 10,594 |
| Histories on which packed is strictly smaller | — | 740 of 742 |
| Histories on which packed is larger | — | 0 of 742 |
| Bounded round-trip/injectivity | PASS | PASS |

This disproves any claim that P01's literal bytes are storage-minimal over the
tested domain. It does not select the packed code or establish total dominance:
corruption acceptance, canonical validation, runtime, cognition, decoder TCB,
operational behavior, EOF dependence, full-domain resources, and unlike
realizations were not jointly compared. Information necessity does not force
either code shape.

### 6.2 Valid-to-valid corruption

The smallest exercised coherent corruption under `Mcorr` is:

```text
source history       = ((0,empty),)
source P01            = 0000
changed byte/mask     = index 0 / 01
changed P01           = 0100
decoded changed value = ((1,empty),)
Mcorr prefix          = (2 encoded bytes, 1 changed bit, ...)
```

Both byte strings are valid canonical encodings. This is not an encoder
collision; it is a valid-to-valid storage-channel transition. Round-trip and
malformed-input rejection do not detect it. Physical integrity and recovery
remain UNKNOWN because no independently retained expected value, durability
protocol, subject, or recovery experiment exists.

### 6.3 Mathematical totality versus finite realizability

P01's mathematical encoder is total for every already-given finite abstract
history when arbitrary mathematical integers and allocation are assumed.
Shortest ULEB exists for every finite payload length, and finite concatenations
parse inductively when extent is supplied.

That fact is separate from literal physical realizability. C01 admits arbitrary
finite payloads and histories, CROSS specifies no storage/resource-exhaustion
result, and E01 admits unbounded mathematical integers and other unbounded
finite values. Any finite realization can encounter a finite payload, history,
ULEB digit sequence, program, trace, list, or buffered output beyond its
resources. Frozen C01 does not define the required boundary behavior on that
path.

Such exhaustion is a missing/UNKNOWN capability, or a failure of claimed total
physical conformance if encountered. It is not an encoder collision. No
resource bound, rejection semantics, or physical totality is invented here.

## 7. Bounded corpus and freshness evidence

### 7.1 Thirteen-history witness-union upper bound

A deterministic union of the frozen minimum pairs reduces the 585-history
public corpus to these thirteen histories while retaining witnesses for all 21
listed public attacks and the redundant-bundle fixed point:

```text
()
(0:)
(1:)
(0:00)
(0:01)
(0:,0:)
(0:,1:)
(1:,0:)
(0:,0:00)
(0:00,0:01)
(0:,0:,0:)
(0:,0:,1:)
(0:,0:,0:00)
```

The 21 attacks are twelve whole-representation mutants and nine
position-specific occurrence/direction/payload deletions. Thirteen is an upper
bound, not a proven minimum. It shows only that all 585 histories were
unnecessary for those listed witnesses; it says nothing about unlisted
representations, common C01 continuations, physical failures, or total-system
adequacy.

### 7.2 Freshness and evidence limits

- The candidate's 157-history “fresh” corpus and its expected result coexist in
  the same frozen file. Its section ordering is not an independently committed
  hidden-test protocol. Reproduction does not prove independent freshness.
- The breaker generated 343 histories mechanically from the candidate hash.
  This avoids the candidate's explicit payload choices, but the breaker had
  already read the candidate and disclosed prior generic attack hints. It is
  post-freeze evidence, not a pristine hidden suite.
- That 343-history corpus produced zero collisions for two supplied mutants
  merely because it lacked their needed structural bytes. Those zeroes are not
  PASSes; the public corpus supplies their witnesses.
- Neither corpus executes exact captured request/response transitions, RUN,
  crash/restart, a subject, or unlike realizations.

The pinned run's `6 PASS / 3 FAIL / 11 UNKNOWN` is evidence about the named
checks only. It does not establish a complete quotient, global minimum, or
physical persistence.

## 8. Missing and UNKNOWN total-system capabilities

| Capability/responsibility | Exact status and smallest pressure |
|---|---|
| Boundary capture transition | **FAIL / missing.** From empty history, one `LENGTH(0)` request must itself and its response enter history, but their bytes, directions, order, and snapshot timing are undefined. Exact argument-byte minimization is impossible because the request serializer is absent. |
| CROSS transition | **FAIL / ambiguous.** From empty history, `CROSS(0,empty)` says append one occurrence while the typed request must also be captured; identity/additional traffic and any response are undefined. |
| Common raw future | **FAIL for harness correspondence.** On `()` / `(0:)`, surrogate LENGTH gives `(0,1)`, but no fixed snapshot request gives that pair before capture. |
| RUN/E01 | **FAIL / unsupported required capability.** Opcode table, binary grammar, `mode`, exact decoder, and executable RUN are absent. |
| SLICE/COMPARE and numeric edges | **UNKNOWN/underdefined.** Negative/excessive domains, prefix-end comparison, wire encodings, and large-argument behavior are not total. |
| Complete history equivalence under captured traffic | **UNKNOWN.** Conditional identity reasoning is not an execution of frozen C01. |
| Global minimum total system | **UNKNOWN.** Only supplied mutants, one redundant bundle, and one bounded storage alternative were tested. |
| Physical durability/recovery/integrity | **UNKNOWN.** No subject; valid-to-valid corruption exists; append, flush, crash, restore, and effect coordination were not run. |
| Human cognition/authoring/explanation | **UNKNOWN/unsupported.** Raw bytes and machine offsets provide no measured human meaning or authoring protocol. |
| Query/navigation service levels | **UNKNOWN.** Derivability by scan is not a latency, memory, or availability result. |
| TCB closure | **UNKNOWN.** Adapter and E01 are incomplete; decoder, scanner, store, effect driver, specification distribution, and humans remain. |
| Evolution/migration/portability | **UNKNOWN/unsupported.** Decoder selection and migration are absent; no second implementation or evaluator conformance exists. |
| Unlike physical realizations | **UNKNOWN.** None was built or compared. |
| Finite-resource conformance | **UNKNOWN/missing.** Arbitrary finite C01/E01 values have no total physical resource or rejection behavior. |

These missing capabilities are not silently reclassified as persistent fields.

## 9. Mandatory attack ledger and complexity displacement

| Attack | Evidence-bounded verdict | Where complexity moved |
|---|---|---|
| DELETE | Deleting an occurrence, direction, payload content, boundary, order, or multiplicity creates the minimized conditional collisions in Section 3. Count/last/direction-count delete successfully from the redundant bundle. | Lost history information must exist in some reversible carrier; successful derived-data deletion moves scan time, memory, latency, and correctness to runtime/TCB. |
| MERGE | Direction, byte-value, order, multiplicity, digest, and Unicode normalization mergers collide under surrogate AT/LENGTH and translate only conditionally to fixed raw observations. No distinct-history merger is permitted by the conditional identity quotient. | Original discriminators or a reversible code remain; semantic normalization is not deletion under byte-exact audit. |
| DERIVE | Count, offsets, indexes, and named folds are exact functions of the sequence/codec. | Source availability, fixed algorithm/version, CPU, memory, and verification replace a persisted copy. |
| RECOMPUTE | Deterministic named projections may recompute conditionally. E01 traces, installed policies, evidence associations, and nondeterministic external results do not have established regenerators. | Work moves to evaluator/scanner code, replay isolation, version retention, latency, and human review; actual nondeterministic crossings remain history. |
| COLLIDE | No P01 collision was found in 585, 157, or 343 histories; lossy/digest mutants collide. `0000 -> 0100` is valid-to-valid corruption, not encoding collision. P01 also depends on external EOF. | Injectivity remains in codec logic; integrity and history-word extent move to external container/media/TCB responsibilities. |
| FUTURE | Conditional fixed raw LENGTH/AT forces exact sequence information. Frozen surrogate functions are not common captured C01 futures; RUN and other futures are incomplete. | Semantics and capture move to unspecified adapter, request grammar, evaluator, callers, programs, and humans. |
| EXTERNALIZE | C01/P01 specification, decoder choice, EOF, adapter, E01, durability, and effect protocol sit outside quotient history. | Distribution, identity, compatibility, availability, trust, and operations remain real total-system costs. |
| REALIZE | No durable realization, crash schedule, restart, or unlike pair was exercised. Mathematical P01 totality does not supply finite-resource physical behavior. | Media, container extent, transactions, recovery, resource rejection, exporter, and effect coordination remain UNKNOWN. |
| COGNITION | Exact raw history preserves bytes but supplies no measured names, schemas, causal links, authoring safety, discovery, or explanation. | Interpretation, conventions, tooling, training, and verification move to people and programs. |
| TCB | Removing redundant persisted values leaves the adapter, codec, EOF/container, scanner, store, evaluator, effect driver, specs, build/runtime, and adjudication. | Smaller local bytes increase reliance on code, configuration, external roots, tests, execution resources, and operators. |

After each apparent simplification, complexity is located rather than erased:

- deleting count or indexes moves work to scanning and cold-query resources;
- retaining only raw bytes moves semantic discovery and authoring to programs
  and humans;
- omitting a history header moves word extent to EOF/container framing;
- omitting an integrity reference leaves valid-to-valid changes undetectable;
- omitting request/RUN grammar moves required semantics into an unspecified
  adapter/evaluator;
- changing P01 to a packed code changes storage and decoder/integrity burdens
  without settling the other dimensions; and
- ideal unbounded mathematics moves finite-capacity behavior outside the
  realized contract rather than making it free.

## 10. Simultaneous total-system assessment

No scalar score is defined, and no row compensates for another.

| Dimension | Current evidence | Verdict |
|---|---|---|
| Information/distinction preservation | P01 is mathematically injective for supplied finite byte strings with extent; bounded corpora agree; conditional raw audit forces exact sequence | Conditional PASS for abstract history only; captured-traffic quotient UNKNOWN |
| Persistent state | One normalized information responsibility: exact sequence recoverability; no P01 field assumption | Conditional MUST; literal minimum and physical carrier UNKNOWN |
| Semantic machinery | Abstract frame codec is exact; capture and E01 are incomplete | FAIL / missing required semantics |
| Human cognition | Raw transcript is byte-exact but semantically opaque; no study | UNKNOWN/high unmeasured burden |
| Authoring burden | No complete E01 grammar, tooling, schema, linting, or review protocol | Unsupported/UNKNOWN |
| Query/navigation | Count and offsets derive by scan; frozen futures are surrogates | Mathematical derivability only; realized requests and service levels UNKNOWN |
| Runtime | Pinned falsifier ran twice in about 3 seconds with about 18.8 MiB RSS | Experiment-only measurement; unbounded scan/VM/replay/resource behavior UNKNOWN |
| Storage | P01 uses direction byte plus ULEB; packed code saves 1,972 bytes over 742 tested instances | Bounded packed storage advantage; no total-system dominance or global minimum |
| Operations | No atomic append, concurrency, flush, crash, backup, repair, restore, or effect protocol | UNKNOWN/unsupported; total operational system fails |
| Trusted computing base | External spec, adapter, decoder, EOF/container, scanner, store, E01, effect driver, runtime, and humans remain | Incomplete and unperturbed: UNKNOWN |
| Evolution | New caller bytes are possible, but decoder selection, installed-policy meaning, migration, and rollback are absent | Unsupported/UNKNOWN |
| Portability | P01 mathematics is host-neutral in intent; E01 and capture are not conformable | No independent implementation or unlike realization: UNKNOWN |
| Explainability | AT-like raw inspection and direct Python results exist; machine/human semantics do not | Raw audit conditional; human explanation unsupported |
| Information-loss risk | One-bit `0000 -> 0100` silently changes valid history; whole-frame truncation can leave a shorter valid word | Definite integrity pressure; detection/recovery UNKNOWN |
| Evidence/freshness | Frozen and hash-derived corpora reproduce named checks | No independently committed hidden suite or adequacy proof: UNKNOWN |
| Physical capacity | Mathematical finite encoding has no matching total finite-resource contract | Missing/UNKNOWN; exhaustion is not an encoder collision |
| Unlike realizations | None exists | UNKNOWN |

## 11. Final normalized ledger

### Unconditional abstract-history results

- P01 is injective over valid finite abstract histories when the complete
  finite input byte-string extent and frozen codec are supplied.
- Count, offsets, and named deterministic folds are functions of the exact
  sequence and identified specification.
- P01's complete history word depends on external extent/EOF.
- Bounded tests find no P01 collision, but do not establish a total system.

### Conditional MUST SURVIVE

If a fixed exact common raw-audit future is adopted, enough information must
survive to reconstruct the exact ordered occurrence sequence. Section 3's
minimized witnesses force its extent, boundaries, order, multiplicity,
directions, and payload bytes. This is one information responsibility, not a
P01 schema.

### Conditional MAY REBUILD

Count, offsets, indexes, last occurrence, direction counts, encoding bytes,
and deterministic projections may rebuild only from the exact sequence plus a
named exact specification. Source/specification availability, work, and TCB
remain charged. E01 traces, generic evidence, and nondeterministic results do
not presently qualify.

### Conditional MAY FORGET

Only transient machinery and excluded host distinctions that never crossed,
cannot affect a permitted future, and are past their exposure window may be
forgotten. No distinction within the exact history may be merged under the
conditional identity quotient.

### Separate external dependencies and UNKNOWNs

Specification bytes and decoder conventions are external semantic roots, not
quotient-derived history state. EOF/container extent, capture grammar,
integrity, durability, finite-resource behavior, E01/RUN, human cognition,
query service levels, TCB closure, evolution, portability, and unlike
realizations remain missing or UNKNOWN.

R0.1N therefore does not establish what information survives in a complete
physical system, even though its abstract encoding and conditional raw-history
lower bound are locally defensible. No representation or architecture is
selected by this ledger.
