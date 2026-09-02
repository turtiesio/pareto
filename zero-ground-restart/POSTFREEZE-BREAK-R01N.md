# POSTFREEZE BREAK — R01N/FT-FE

Status: frozen-candidate audit; no repair proposed  
Candidate audited: `/root/pareto/zero-ground-restart/HISTORY-SEED-R01N.md`  
Expected and observed candidate SHA-256: `10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7`  
Overall result: **FAIL as a frozen total system; conditionally defensible raw-history persistence result; minimum and physical conformance remain UNKNOWN**

## 1. Pre-read gate, isolation, and contamination disclosure

Before reading candidate semantics I ran exactly:

```text
sha256sum -- /root/pareto/zero-ground-restart/HISTORY-SEED-R01N.md
```

It exited zero and returned exactly:

```text
10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7  /root/pareto/zero-ground-restart/HISTORY-SEED-R01N.md
```

The hash gate therefore passed. Semantic reading began only afterward.

This breaker is not epistemically pristine. Before this assignment, an aborted attempt to launch an R01M builder exposed me to generic prior-round instructions and attack hints, including the named DELETE/MERGE/DERIVE/RECOMPUTE/COLLIDE/FUTURE/EXTERNALIZE/REALIZE/COGNITION/TCB attacks, bounded search, capacity boundaries, corruption exercise, fresh-domain testing, physical-realization obligations, and initial-root scrutiny. That aborted attempt wrote nothing and exposed no R01N content. I used those hints only to attack the frozen R01N candidate, never as a source of solution ontology. The mechanically generated post-freeze corpus in Section 8 is independent of R01N's hand-selected payload corpus, but it is not claimed to make this breaker blind or uncontaminated.

Repository-content access was limited to the named R01N candidate and, after creation, this report for its hash/counts. I did not list or search the repository, inspect Git or history, read any other repository file or prior artifact, contact another agent, use the network, or use an external source. I invoked `sha256sum`, `awk`, and Python 3.12.3; Python standard-library modules were used for the probes. This report is the only file I created or modified, and it was created with `apply_patch`. No commit was made.

## 2. FIRST MILESTONE verdict

The first persistence statement is defensible only under a narrowed, abstract reading of C01:

- If `LENGTH` and byte-exact `AT` are total permitted observations, every unequal finite ordered boundary history is distinguishable. Enough information to reconstruct that exact history therefore **MUST SURVIVE**. This is information content, not a requirement for a field, constructor, layer, or literal P01 byte layout.
- The occurrence count, offsets, and indexes **MAY REBUILD** by a total deterministic scan from the exact history plus the frozen P01 decoding specification. The frozen redundant-bundle test exercises this claim.
- Completed-scan cursors, completed-request VM working cells, cache eviction order, host identities, and other behavior explicitly excluded from C01 **MAY FORGET**, provided none actually crossed the boundary and no crash/restart future exposes it.
- E01 traces, installed configuration/policy state, semantic evidence associations, crash-coordination metadata, and physical recovery behavior are **UNKNOWN or unsupported**, not presently established MAY-REBUILD information. Their required specifications or realization evidence are absent.

As a total system, however, the frozen candidate fails. It does not define how the typed future requests and their responses become the `(direction, payload)` occurrences that it says must capture every crossing. It also deliberately omits E01's opcode table and binary grammar, and leaves `mode` and several request edge domains undefined. Consequently an exhaustive executor cannot determine all required future-observable behavior. This is a missing-capability failure, not a P01 pairwise collision.

The final split verdict is:

```text
FIRST MILESTONE: FAIL AS A TOTAL FROZEN CANDIDATE.
RAW-HISTORY INFORMATION OBLIGATION: CONDITIONAL PASS under abstract LENGTH/AT.
P01 MINIMALITY, FULL-DOMAIN EXECUTABILITY, OPERATIONS, AND UNLIKE REALIZATIONS: UNKNOWN.
```

## 3. Quotient information versus fixed parameters and TCB

Under the abstract raw-audit observations, the quotient-derived information is just the exact finite ordered sequence of boundary occurrences. Its recoverable distinctions are sequence extent, occurrence boundaries, order, multiplicity, each direction value, and every payload byte. The least unequal index is distinguished by `AT`; unequal extent is distinguished by a suitable prefix request or current-history length observation. No argument here implies a dedicated stored count, direction field, length field, or other constructor.

The following are instead fixed contract/representation parameters or TCB, not history-derived quotient state:

- the meaning and direction convention of the one-bit boundary alphabet;
- the definition of a byte and finite sequence;
- request/response serialization and capture order — required, but missing;
- the P01 direction-byte convention, ULEB grammar, shortest-form rule, and decoder selection;
- the exact semantics of snapshots, indices, slices, comparison, rejection, and response emission;
- E01's program grammar, opcodes, integer and byte behavior, `mode`, trace, fuel, and effect rules — partly described, but not fixed completely;
- the boundary adapter, decoder, scanner, store, durability protocol, evaluator, effect driver, and conformance process.

Payload boundaries must be recoverable, but P01's literal ULEB length digits are not independently forced history information. Likewise the one history-level extent is recoverable by scanning; a persisted outer count is not forced. Canonical shortest-form validation is a P01 rule and validation mechanism, not a quotient distinction. Relaxing that rule could admit several physical words for one history without merging two histories; whether to do so is outside this audit and would be a different candidate.

The empty history has no boot occurrence. That is coherent only because C01/P01 and the decoder choice are declared as an already-existing external semantic root. C01 does not expose decoder selection or migration, so this audit does not invent a boot occurrence. If selection or evolution crosses the boundary in a broader contract, its actual bytes would have to be retained. Here the root remains incomplete because the adapter grammar and E01 grammar are absent.

## 4. Reproduction of the frozen oracle

I executed the frozen code directly from its fenced block without creating an extraction file:

```sh
awk '/^# BEGIN E-R01N-1$/{inside=1; next} /^# END E-R01N-1$/{inside=0} inside' \
  /root/pareto/zero-ground-restart/HISTORY-SEED-R01N.md | python3 -
```

Python reported version `3.12.3`. The command exited zero. Exact headline results were:

```text
public corpus: histories=585 futures=33
PASS R01N_P01: no distinguishable collision
DELETE bundle component without witness: count
DELETE bundle component without witness: last
DELETE bundle component without witness: direction_0_count
bundle deletion fixed point: ('transcript',)
fresh corpus: histories=157 futures=28
PASS R01N_P01_FRESH: no distinguishable collision
FAIL FRESH_UTF8_NFC_NORMALIZATION: classes=38; min=(0:c3a9) <> (0:65cc81); repr=b'\x00\x02\xc3\xa9'; witness=AT(0); results=(0, b'\xc3\xa9') <> (0, b'e\xcc\x81')
E-R01N-1 bounded result: PASS for P01; all listed mutants falsified
```

All twelve named whole-representation mutants and all nine position-specific mutants produced witnesses. The frozen program's exact smallest whole-mutant reports were:

| Mutant | Collision classes | Reported minimum pair | First frozen-suite witness |
|---|---:|---|---|
| `DELETE_DIRECTION` | 84 | `(0:)` / `(1:)` | `AT(0)` |
| `DELETE_PAYLOAD` | 14 | `(0:)` / `(0:00)` | `AT(0)` |
| `DELETE_FRAMING` | 156 | `(0:00)` / `(0:,0:)` | `AT(0)` |
| `MERGE_ORDER_BY_SORT` | 140 | `(0:,1:)` / `(1:,0:)` | `AT(0)` |
| `MERGE_MULTIPLICITY_BY_DEDUP` | 92 | `(0:)` / `(0:,0:)` | `LENGTH` |
| `KEEP_COUNTS_ONLY` | 9 | `(0:)` / `(0:00)` | `AT(0)` |
| `KEEP_LAST_ONLY` | 8 | `(0:)` / `(0:,0:)` | `LENGTH` |
| `KEEP_TAIL_TWO` | 64 | `(0:,0:)` / `(0:,0:,0:)` | `LENGTH` |
| `DELETE_FIRST` | 73 | `()` / `(0:)` | `AT(0)` |
| `DELETE_LAST` | 73 | `()` / `(0:)` | `AT(0)` |
| `MERGE_PAYLOAD_01_INTO_00` | 174 | `(0:00)` / `(0:01)` | `AT(0)` |
| `REPLACE_WITH_DIGEST8` | 176 | `(0:)` / `(0:00,0:01)` | `AT(0)` |

The result is a useful falsifier. It is not an architecture, a proof of total-system minimality, or an exhaustive execution of C01.

## 5. Exact minimization audit and smallest witnesses

### 5.1 Frozen minimization order

Public histories are enumerated by occurrence count `0,1,2,3`; within each count, `itertools.product` follows `EVENTS`, whose exact order is directions `0,1` outside payloads `empty, 00, 01, 0001`. Fresh histories use the analogous order at maximum count two.

For a colliding pair, the frozen metric is:

```text
(
  total occurrence count across the pair,
  total payload bytes across the pair,
  history_rank(left),
  history_rank(right)
)
```

where `history_rank(h)=(occurrence count, payload-byte total, lexical tuple of (direction,payload))`, and pair endpoints are first sorted by that rank. Futures are sorted by `(declared syntactic cost, stable name)` and the first unequal result is selected. This explains, for example, why `AT(0)` precedes `LENGTH` when both cost one.

The code minimizes a pair within each representation bucket, then sorts bucket results only by the pair metric. A tie between buckets inherits deterministic insertion/enumeration order rather than an explicitly named representation-key tiebreak. It also minimizes only over the hand-enumerated histories and functions; it does not minimize program bytes, request sequences, crash schedules, resource bounds, or physical failures.

### 5.2 Breaker metric

For a pairwise representation attack I used:

```text
Mpair = (total occurrences, total payload bytes, total P01 bytes, lexical endpoints)
```

For corruption I used:

```text
Mcorr = (source P01 byte length, changed-bit count, source-history rank,
         changed byte index, bit mask)
```

For a missing semantic capability I used:

```text
Mmissing = (initial occurrence count, future-request count,
            explicit argument-byte count, lexical request description)
```

These metrics are category-specific; a missing definition is not mislabeled as a collision.

The smallest witnesses found or established are:

| Category | Smallest witness under the stated metric | Classification |
|---|---|---|
| Pairwise collision in a deletion mutant | `()` and `((0,empty),)` both map to empty under `DELETE_FIRST` or `DELETE_LAST`; `AT(0)` distinguishes | collision; mutant rejected |
| Direction merge | `((0,empty),)` and `((1,empty),)`; `AT(0)` distinguishes | collision; merge rejected |
| Framing deletion | `((0,00),)` and `((0,empty),(0,empty))`; `AT(0)` distinguishes | collision; deletion rejected |
| Successful history merge | none | impossible under abstract C01 identity quotient; no distinct pair is equivalent |
| Successful component deletion | count, last, then direction-0 count from the redundant bundle | not a history merge; deterministic work moves to scan/runtime |
| P01 pairwise collision | none in either frozen corpus or the independent corpus | bounded negative evidence plus a sound conditional parsing argument, not global total-system proof |
| Totality failure in the advertised Python encoder | none claimed or witnessed, because the executable advertises bounded use only | full C01 realization remains unsupported/UNKNOWN |
| Missing capability | empty history followed by one `LENGTH(0)` request: request and response must become occurrences, but no direction/payload serialization or capture order is defined | frozen contract has no unique required next history |
| Corruption acceptance | `0000` to `0100` by one bit; decodes from `((0,empty),)` to `((1,empty),)` | valid-to-valid corruption, not an encoder collision |
| Unknown evidence | any required unlike-realization comparison | no realization was built or run |

## 6. Contract and totality breaks

### B1 — Boundary capture is not defined (missing capability; decisive)

C01 says a history contains everything crossing the boundary and that every future request and response that actually crosses is captured as an occurrence. But its boundary alphabet contains only `(direction, payload)` while futures are typed calls such as `LENGTH(snapshot)` and `RUN(snapshot,program,fuel,mode)`. There is no mapping from those typed calls or results to direction and payload bytes, no canonical response grammar, and no rule fixing whether request capture precedes snapshot resolution or response capture.

Starting from the empty history, issue `LENGTH(0)`. The abstract answer seems to be zero, but the required new boundary history is underdetermined: the request occurrence bytes, response occurrence bytes, directions, and ordering are unspecified. Two adapters can choose different bytes, and a later `AT` observes the difference. Treating the typed call as metadata outside the pair would instead violate “everything that crossed.” Thus exhaustive future execution cannot start even at the smallest history. Complexity has been externalized to an unspecified adapter that necessarily belongs in the contract and TCB.

`CROSS(d,p)` is also ambiguous in this respect. If the typed `CROSS` call is the one occurrence it appends, that identity must be stated. If the call and a response are additional crossings, “appends exactly one” conflicts with capture. This audit does not select a repair.

### B2 — E01 and several request domains are incomplete (missing capability)

E01 intentionally lacks a numeric opcode table and binary program grammar. `mode` is named but has no domain or semantics. Therefore malformed versus valid program bytes, instruction boundaries, literal length bounds, jump encodings, and the result of even an empty program cannot be determined. `RUN` is a required future, so this is a frozen total-system failure even though the candidate candidly labels portability and overall status UNKNOWN.

Other omitted exact domains include whether indices/start/count/fuel may be negative, how `SLICE` handles negative or excessive ranges, the exact prefix result of `COMPARE` when one history ends, canonical request/result encodings, and resource behavior for enormous finite arguments. Calling slicing “in that range” and byte slicing “clamped” does not fix all endpoints. These are missing definitions, not evidence of two P01 histories colliding.

The frozen oracle never implements `SLICE`, `RUN`, `COMPARE`, request/response capture, policies, buffered effects, or machine traces. Its 33 public futures and 28 built-in fresh futures are ordinary Python observation functions. They falsify selected history projections but cannot establish the promised semantic/runtime surface.

### B3 — The bounded future enumeration is exact but narrower than the boundary corpus

`make_futures` appends only `events[:4]`. In the public domain this covers the four direction-0 events and omits all four direction-1 events. In the built-in fresh domain it covers four of twelve events. Thus “one-occurrence append continuations” must be read as a selected subset, not all bounded continuation symbols. There are 33 and 28 functions exactly as printed, but no exhaustive enumeration of multi-request continuations or of C01 programs.

This does not create a missed history collision in these corpora because `AT(0..maximum-1)` already makes the base signatures injective. It does limit capability and future-composition evidence. Complexity has been moved from the oracle to unexecuted reasoning and future conformance work.

### B4 — Full-domain and nested-capacity status is UNKNOWN, not falsely proved

The mathematical P01 encoder is total over finite histories if arbitrary mathematical allocation is assumed: shortest ULEB exists for every finite payload length, and concatenated frames parse inductively. The Python program is explicitly a bounded falsifier, so its failure to cover all finite histories is not itself a broken totality claim.

The total system nevertheless has no executable full-domain resource contract. The nested boundaries are:

- occurrence count: arbitrary finite in C01; no outer encoded count; Python container, iteration, and output memory limits remain;
- payload length: unbounded ULEB in the specification; host `bytes` and total encoded-string sizes are bounded by address space and allocation;
- ULEB digit count: unbounded; the decoder has no digit/resource cap and accumulates an unbounded integer before canonicality/remainder checks;
- snapshot, index, slice start/count, and fuel: domains and wire encodings are missing;
- program and literal lengths, integer magnitude, list size/nesting, jump offsets, trace length, and buffered view/action volume: grammar or caps are missing;
- physical append size, offset width, transaction size, recovery log, and emission coordination: no realization is specified.

The breaker round-tripped payload lengths `0,1,2,126,127,128,129,255,16383,16384,16385,65535`. Observed `(payload length, ULEB bytes, frame bytes)` was exactly:

```text
(0,1,2) (1,1,3) (2,1,4) (126,1,128) (127,1,129)
(128,2,131) (129,2,132) (255,2,258) (16383,2,16386)
(16384,3,16388) (16385,3,16389) (65535,3,65539)
```

All twelve corresponding deliberately overlong ULEBs were rejected. Exhaustion over all 65,793 byte strings of length zero through two found three accepted strings, each exactly equal to `encode(decode(raw))`. These are useful boundary checks, not evidence for unbounded host execution.

### B5 — Corruption is not generally fail-closed (exercised counterexample)

The frozen four malformed-input tests passed, and the additional overlong/canonicality tests above passed. But malformed rejection is not corruption detection. The breaker searched one-bit changes in increasing encoded size and found:

```text
history=(0:) raw=0000 byte=0 mask=01 changed=0100 decoded=(1:)
```

Both strings are canonical P01 encodings. No checksum, authenticated channel, expected copy, or durability protocol exists to tell a legitimate direction change from corruption. Whole-frame truncation can likewise leave a shorter valid transcript. Therefore the assessment phrase “explicit raw retrieval makes loss detectable” is false unless an independent expected value is available. The candidate's stronger surrounding statement that corruption detection and recovery are unspecified is correct.

This is not a pairwise encoder collision: the histories have different encodings. It is a valid-to-valid storage-channel transition and an unsupported integrity capability. Detection complexity was omitted, not eliminated; it moves to a checksum/authentication scheme, redundant trusted copy, media protocol, or operator comparison, none of which C01/P01 specifies.

### B6 — Rebuild and evidence classifications need narrowing

Count, offsets, and direct navigation tables are genuinely deterministic from P01 and its exact decoder. The bundle fixed point exercises those deletions. A named hash or materialized view may rebuild only if its exact algorithm/version is fixed and available; generic “a digest” is not an identified specification.

E01 traces cannot presently be classified as demonstrated MAY REBUILD because E01's binary grammar and opcode table are incomplete. “Installed configuration” and policy replay are also not defined C01 capabilities, and raw payloads contain no specified tag that says which crossing installs what. Actual nondeterministic service, clock, random, model, or human results must remain in the raw history if they crossed, but the causal/semantic association needed to treat bytes as evidence is not defined. Raw bytes survive; evidentiary interpretation and human explanation remain unsupported.

Recomputing deterministic projections moves complexity into CPU time, scanner/evaluator correctness, specification retention, version control, latency, and human review. Re-running nondeterministic producers is not reconstruction.

### B7 — Freshness evidence is limited

R01N states that its Unicode corpus was selected after Sections 1–6 froze, and the normalization mutant is correctly caught. The frozen file itself contains both that corpus and its expected result, so an external breaker cannot verify when or independently how it was selected. This is not a flaw in P01, but it is UNKNOWN evidence about hidden-test independence.

Section 8 below supplies a reproducible post-freeze corpus mechanically derived from the already-gated candidate hash and a breaker-only label. It is independent of the builder's explicit payload choices. It is not claimed to erase my prior attack-hint contamination or the fact that I had read the frozen candidate before running it.

## 7. Attack ledger and complexity displacement

P01 has one persisted component: the canonical transcript byte string. The table attacks that component, its decoding mechanisms, and the external machinery needed to serve C01.

| Attack | Target and result | Classification | Where complexity moved |
|---|---|---|---|
| DELETE | Delete an occurrence, direction, payload, order boundary, or payload framing without preserving its information. Frozen minimal witnesses distinguish every such deletion. | failed simplification / collision | Any successful physical recoding must put the lost discriminator elsewhere; a sidecar is still persistence. |
| MERGE | Merge directions, byte values, order, multiplicity, or normalized Unicode. Every exercised semantic merge collides under `AT` or `LENGTH`. | failed history merge | A discriminator, reversible code, or original transcript must remain; otherwise loss is visible. |
| DERIVE | Outer count, last item, direction count, offsets, and indexes can be deleted from a redundant bundle. Literal ULEB digits are coding, not separate quotient facts. | successful component deletion for derived data | Cold scan time, memory, cache building, decoder correctness, and latency move into runtime/TCB. |
| RECOMPUTE | Deterministic indexes/views can be recomputed only with an exact retained specification. Actual crossings cannot be regenerated from changing external sources. E01 traces are not yet reproducible. | conditional success / otherwise unsupported | CPU, algorithms and their versions, replay isolation, and review replace persisted caches; nondeterministic results stay in history. |
| COLLIDE | P01 had no collision in 585 public, 157 built-in fresh, or 343 breaker histories; its parsing argument is conditionally sound. Digest and lossy mutants collide. One-bit corruption maps valid P01 to different valid P01. | no found encoder collision; definite integrity counterexample | Collision avoidance stays in exact history coding; corruption detection moves to an absent integrity/durability mechanism. |
| FUTURE | Raw `AT`/`LENGTH` force exact history. Future `RUN`, actions, policies, views, and captured requests cannot be exhaustively executed because their grammar/capture semantics are incomplete. | raw witness succeeds; total future domain fails | Semantics move to callers, programs, adapters, and humans, but those are unspecified TCB rather than removed cost. |
| EXTERNALIZE | Decoder identity, C01/P01 text, request adapter, E01, durability, and effect protocol are external to persisted history. Externalizing history bytes to a sidecar would not delete their responsibility. | large external TCB; adapter/E01 missing | Deployment configuration, code provenance, compatibility, operations, and people carry the burden. |
| REALIZE | No file, row-store, flash, optical, or other durable realization is run. Atomic append, torn writes, restart, and external-effect coordination are absent. | UNKNOWN evidence / operations unsupported | Storage engine, transaction/recovery logic, hardware, exporter, and effect driver must supply it. |
| COGNITION | Exact raw bytes preserve distinctions but supply no names, schemas, causal links, or human meaning. No author/reviewer study is executed. | capability evidence absent | Interpretation, conventions, discovery, tooling, training, and review move to humans and supplied programs. |
| TCB | Removing persisted indexes leaves adapter, canonical decoder, scanner, store, E01, and effect driver. Adapter and E01 are not completely specified. | incomplete and unmeasured TCB | State bytes shrink locally while code, tests, execution time, deployment roots, and operational procedures grow. |

After repeated component deletion in the frozen bundle, none of its remaining single component (`transcript`) can be deleted within the searched domain. This is only a greedy fixed point for that supplied bundle. It says nothing about a radically different injective coding or total-system optimum. No weighted scalar can turn the simultaneous deficits into a pass.

## 8. Independently generated post-freeze protocol

### 8.1 Generation and metric

After the hash gate, I set `seed` to the 32 candidate-hash bytes. Payload lengths were:

```python
lengths = tuple(sorted({0, *(b % 65 for b in seed[:8])}))
```

This yielded exactly `(0, 7, 16, 28, 42, 46, 51, 52, 57)`. Payload `i` of length `n` was generated as:

```python
shake_256(b"R01N-postfreeze-independent:" + bytes((i,)) + seed).digest(n)
```

Both directions were paired with all nine payloads, producing 18 occurrences. Histories were exhaustively enumerated at lengths zero through two, producing `1 + 18 + 18^2 = 343`. Futures were exactly `LENGTH`, `AT(0)`, and `AT(1)`, in that stated order. They are sufficient to distinguish all histories in this bounded domain. Pair minimization used the frozen `history_rank`/`pair_rank` functions.

The reproducible core of the probe was:

```python
from hashlib import shake_256

seed = bytes.fromhex(
    "10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7"
)
lengths = tuple(sorted({0, *(b % 65 for b in seed[:8])}))
payloads = tuple(
    shake_256(b"R01N-postfreeze-independent:" + bytes((i,)) + seed).digest(n)
    for i, n in enumerate(lengths)
)
events = tuple((d, p) for d in (0, 1) for p in payloads)
histories = enumerate_histories(events, 2)
futures = (
    (1, "LENGTH", lambda h: len(h)),
    (2, "AT(0)", lambda h: at(h, 0)),
    (3, "AT(1)", lambda h: at(h, 1)),
)
assert len(histories) == 343
assert len({encode_full(h) for h in histories}) == len(histories)
assert all(decode_full(encode_full(h)) == h for h in histories)
assert not minimized_collisions(encode_full, histories, futures)
```

Here the named functions are loaded unchanged from frozen `E-R01N-1`; no extracted file is created.

### 8.2 Exact results

```text
independent lengths= (0, 7, 16, 28, 42, 46, 51, 52, 57)
independent domain: events=18 histories=343 futures=3 P01_collisions=0
DELETE_DIRECTION collisions=90 min=(0:) <> (1:) witness=AT(0)
DELETE_PAYLOAD collisions=6 min=(0:) <> (0:24121b73022172) witness=AT(0)
DELETE_FRAMING collisions=0
MERGE_ORDER_BY_SORT collisions=153 min=(0:,1:) <> (1:,0:) witness=AT(0)
MERGE_MULTIPLICITY_BY_DEDUP collisions=171 min=(0:) <> (0:,0:) witness=LENGTH
DELETE_FIRST collisions=19 min=() <> (0:) witness=LENGTH
DELETE_LAST collisions=19 min=() <> (0:) witness=LENGTH
MERGE_PAYLOAD_01_INTO_00 collisions=0
```

The two zeroes are retained rather than spun as passes. This corpus happens not to contain the structural bytes needed to collide under the supplied no-framing mutant or a relevant `01`-to-`00` replacement. The frozen public corpus supplies witnesses for both. This demonstrates why one fresh corpus is a falsification instrument, not an adequacy proof.

## 9. Required unlike-realization obligations

No physical realization evidence exists in the candidate or this audit. At minimum, two materially unlike obligations remain:

1. **Append byte stream versus transactional rows.** Independently implement the adapter/exporter/decoder for an append-only byte medium and a transactional row store, without sharing parsing code. Run the same generated histories and all exactly specified C01 futures, restart after each accepted continuation, and compare exported histories and boundary outputs byte for byte. Inject interruption at every byte-write/transaction phase and at response/action emission. The test must report whether each outcome is old history, new history, or explicit rejection; a silently different valid history fails.
2. **Electronic store versus printed optical marks.** Persist the same histories in a conventional electronic durable store and in printed/optically scanned marks with an independently implemented reader. Exercise empty/repeated frames, arbitrary binary payloads, ULEB transitions, reorder/duplication/drop, mark damage, rescans, and export. Compare decoded history and every raw observation. Undetected valid-to-valid alteration fails any advertised integrity claim; if integrity is outside the contract, the result must remain explicitly unsupported.

These are obligations, not proposed architecture. Both are `NOT RUN`; portability, durability, and unlike-realization conformance remain UNKNOWN.

## 10. Simultaneous total-system assessment

| Dimension | Breaker result | Evidence or forcing distinction |
|---|---|---|
| information preservation | conditional bounded PASS for P01; no found collision | frozen 585 + 157 and breaker 343 histories; inductive frame parsing; abstract `AT`/`LENGTH` |
| persistent state | exact-history information MUST; literal P01 minimum UNKNOWN | deletion mutants fail; redundant derived bundle deletes; no alternative-space proof |
| semantics | FAIL / missing | E01 opcodes, binary grammar, `mode`, request capture absent |
| cognition | unsupported/high burden | raw bytes and machine-offset traces do not provide human concepts or evidence links |
| authoring | unsupported | arbitrary program bytes are asserted possible; no valid grammar/tooling/review task exists |
| query/navigation | abstract exact access specified; realized path incomplete | scan can derive offsets; actual request wire and physical snapshot behavior absent |
| runtime | bounded Python falsifier passes; total runtime UNKNOWN | no resource envelope for ULEB, history, VM, buffers, or replay |
| storage | logical encoding precise; durable storage unsupported | no atomicity, flush, integrity, repair, backup, or concurrent writer protocol |
| operations | FAIL for advertised total-system readiness | crash, response/effect coordination, restore, migration, and concurrency unresolved |
| TCB | incomplete and unmeasured | adapter/E01 missing; decoder/scanner/store/effect driver remain required |
| evolution | unsupported beyond changing caller bytes | no decoder selection/migration; installed-policy semantics absent |
| portability | P01 mathematical bytes plausible; total portability UNKNOWN | E01 nonconformable; no independent decoder or physical realizations |
| explainability | raw audit possible; semantic explanation unsupported | no complete evaluator, human semantics, or retained causal grammar |
| loss risk | definite undetected corruption witness | canonical `0000` flips to canonical `0100` in one bit |
| unlike physical realizations | UNKNOWN | both obligations in Section 9 are unexecuted |

No dimension is traded into a weighted score. The preservation result does not cancel the missing semantic, operational, cognitive, or realization capabilities.

## 11. Final disposition

R01N correctly avoids calling its bounded candidate the minimum and correctly labels many operational gaps. Its strongest defensible result is narrow: assuming abstract byte-exact `AT` and suitable `LENGTH` observations, exact ordered history information must survive, and the P01 frame grammar is injective in the searched domains and by ordinary inductive parsing.

The frozen candidate is nevertheless not a total executable contract. The smallest decisive witness is the empty history plus one typed query: the contract requires its request and response crossings to enter history but supplies no occurrence encoding or ordering for them. E01 then independently blocks interpretation, action, and explanation conformance. A one-bit valid-to-valid corruption disproves the claim that raw retrieval alone makes information loss detectable. None of these findings is repaired here.

Final classification:

```text
MUST SURVIVE — exact raw ordered boundary-history information, conditional on a fixed
               capture grammar; forced by byte-exact AT and extent observation.
MAY REBUILD  — count, offsets, indexes, and only projections with an identified exact
               deterministic specification; work moves to runtime/TCB.
MAY FORGET   — completed transient machinery and excluded host behavior that neither
               crossed nor can be exposed by a permitted future.
UNKNOWN      — E01 traces/configuration, semantic evidence, crash/effect state,
               full-domain resource behavior, human authoring/explanation,
               minimality, integrity/recovery, and unlike realizations.
FAIL         — frozen total-system claim, because boundary capture and required RUN
               behavior are not defined sufficiently for exhaustive execution.
```
