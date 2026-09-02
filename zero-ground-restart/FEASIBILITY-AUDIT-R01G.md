# FEASIBILITY AUDIT R0.1G — SMALL HISTORY QUOTIENT AND UNLIKE-REALIZATION BOUNDARY

## 0. Frozen authorities, chronology, and verdict

This audit leaves the H11 seed and every executable artifact immutable.

| artifact | commit | SHA-256 |
|---|---|---|
| `HISTORY-SEED-R01G.md` | `a545c845a26a1ee4ae0195f2ddc08c7a308bf42c` | `9fcf79f7544e3fe7d11f0830e224635758921f199e4478bb4180ada991629008` |
| `POSTFREEZE-BREAK-R01G.md` | `1c5a17fc2df710adf893e319343099b184c60546` | `3612139e2e3f7e2cd6c2bfeae4fa240c8204904f48bf0c4ccbede7b2be8c20f7` |
| `r01g_history_experiment.py` | `1b10120b554d00d88e68efe302e4865cc707a1c0` | `f929385020fc1ef810954b9c8bfd8263358cec3af63e76325f6f3b65cc36be52` |
| `r01g_realization_l.py` | `0f4c90737633cd28a9e9c7ebe732f38e8b722e0f` | `291aa322642d2be07d983422c054137658437c913150785e846f4a958cdd3398` |
| `r01g_realization_s.py` | `303e79ab852363596bf6cd01cc7e5ecb9c593ba5` | `e8aca5702abe926cfe9ec7e2a6c722c38d1707b0c4e95ecce8f4b695af73b761` |
| `ARCHIVE-REPLAY-R01G.md` | `6fa7366a0623c66c9f93e369006034937c6b8483` | `b4230e1262cac9d2b5335abf8c928e1e9a368b79f600f45ab66ece487518344b` |
| `r01g_unlike_compare.py` | `90d4ee509f2fdf0ba5e41b2c7072579b1026e18e` | `9e73876a98ea5a593d176f6e1e462d1e7b3c13fbc9837ee57da8f62ed414af39` |

The deterministic executable output hashes are:

| executable | canonical stdout SHA-256 | reproduced wall time | maximum RSS | exit |
|---|---|---:|---:|---:|
| reference experiment | `bf5a51cdff51499946320a3c9b970d791a55636ca514063ad2e78a7f5175612d` | 9.92 s | 74,432 KiB | 1, because three `FAIL`s exist |
| append/replay L self-test | `e4bba93ff2641d7bce67b9fcf8b781f9d153a26ae1eb761abb836b9ae0d2b9f2` | 2.73 s | 22,016 KiB | 0 |
| packed-byte S self-test | `1eb64c7eb30cd9edf6a7a83568fe0c26cbf086ec25cc02e1497f45dacc5fef85` | 0.07 s | 21,120 KiB | 0 |
| black-box unlike comparator | `0c64b93094f54e7fe5be68a79294e608d75a455a85098ed6cb7ad193f02bcd9f` | 49.33 s | 41,216 KiB | 0, with overall `UNKNOWN` |

All four pass `python3 -m py_compile`.  Repeated runs produced identical
canonical output hashes.

The quarantine and independence order was:

1. a builder with no repository or prior-candidate access received only the
   history/distinguishability method and fresh attack constraints;
2. its 616-line H11 seed was frozen verbatim;
3. a fresh breaker saw only those frozen bytes;
4. a file-scoped implementer constructed the reference experiment without
   changing the seed;
5. only after the fresh break was the adversarial archive replayed;
6. two fresh authors independently implemented L and S from the seed, sharing
   no product parser, reducer, persistence, or recovery code; and
7. a third author compared both as black-box JSONL processes against another
   independently written oracle.  Its reviewer caught an initial overclaim,
   which was removed before freeze.

No implementation is semantic authority.  Passing software over a stipulated
one-byte fault model is not physical-media evidence.

Verdict:

```text
H11 ELEVEN-MESSAGE FAULT-FREE ORACLE = TOTAL
H11 CUT HISTORIES = 133
H11 CUT PARTITION, CONDITIONAL ON SET-VALUED CRASH SEMANTICS = 14 CLASSES
H11 FULL REACHABLE REDUCTIONS = 18 CLASSES
H11 REPRESENTATION INJECTIVITY = PASS FOR THREE CANDIDATES
H11 PUBLISHED CLASS MULTISET = FALSIFIED
H11 TWO PUBLISHED MINIMAL WITNESSES = FALSIFIED
H11 EMPTY-SUBMISSION CLAIM = CONTRADICTS ITS LANGUAGE
H11 CRASH EQUIVALENCE = UNDERSPECIFIED WITHOUT MAY-TRACE SET EQUALITY
H11 PUBLISHED 6,620,208-RUN CLAIM = NOT AN EXACT NONDUPLICATE COUNT
L LOCAL APPEND/REPLAY MODEL = PASS
S LOCAL PACKED-BYTE MODEL = PASS
L/S FACTORED ABSTRACT ONE-BYTE TRANSITION RELATION = PASS
COMPLETE END-TO-END UNLIKE SOFTWARE EQUIVALENCE = UNKNOWN
UNLIKE PHYSICAL MEDIA / REAL POWER-LOSS EVIDENCE = ABSENT / UNKNOWN
FIRST TARGET MILESTONE = NOT YET MET
NO PRODUCTION, AUTHORIZATION, OR ARCHITECTURE GATE RESULT
```

H11 is a materially better first corpus than CF-1: it is small enough to
enumerate and its deterministic quotient core is known.  It is not yet a
defensible total oracle because nondeterministic equivalence is unstated and
several frozen predictions are false.

## 1. Exact finite experiment result

### 1.1 Fault-free history partition

The eleven-message alphabet has ten one-byte messages and one two-byte message.
All are nonempty, and all 198 state/message combinations over the eighteen
reachable reductions have a total fault-free answer.

The exact pre-cut corpus is:

```text
M^0 union M^1 union M^2
```

and contains `1+11+121=133` histories.  Exhaustive reduction obtains fourteen
cut classes with the following corrected multiset:

```text
{45,15,15,14,14,14,2,2,2,2,2,2,2,2}
```

It sums to 133.  The seed printed four `14`s and seven `2`s, which sums to 145.
The row table itself is correct; the Section 11 multiset is not.

Across the complete five-message horizon all eighteen combinations of:

```text
current revision in {0,1}
active restricted table in {absent,I,N}
current observation in {absent,0,1}
```

are reachable and future-distinct under the intended may-trace interpretation.
The names above describe the computed partition; they do not require three
stored fields.

The reference instrument explored:

| measurement | result |
|---|---:|
| cut histories | 133 |
| unordered distinct cut-history pairs | 8,778 |
| cut classes | 14 |
| full classes | 18 |
| cut-class pair witnesses | 91 |
| full-class pair witnesses | 153 |
| future words of length 0..3 | 1,464 |
| split history/future scripts | 194,712 |
| local old/new crash cases | 83,147 |
| maximum shortest distinguishing future | 2 client messages |

Its report contains 45 `PASS`, 3 `FAIL`, and 3 `UNKNOWN` findings.  The
failures are the bad multiset, the combined minimality prediction, and the
STOP-suite claim that one of four displayed histories is an empty submission.
The unknowns are absent independent physical builds, incomplete ordering of
boundary-gap crash sites, and unstated crash behavior for terminal half-close.

### 1.2 Actual shortest witnesses

All five proposed survival pairs separate, but two proposed futures lose the
seed's own message-order tie-break:

| responsibility | histories | actual first common future | first difference |
|---|---|---|---|
| revision | `[]` / `[50]` | `[50]`, not `[60]` | `85 01` / `e0 06` |
| table absence/presence | `[]` / `[10]` | `[20]`, not `[30]` | `e0 05` / `82` |
| table I/N | `[10]` / `[11]` | `[00,30]` | `83 00` / `83 01` |
| observation absence/presence | `[]` / `[00]` | `[10,30]` | `e0 04` / `83 00` |
| observation zero/one | `[00]` / `[01]` | `[10,30]` | `83 00` / `83 01` |

The frozen order still does not totalize pair orientation, distribution of
equal-cost messages among the two histories and future, crash position within
a category, or serialization of outcome sets.  Therefore a globally unique
all-pair minimized corpus remains underspecified even though these fixed pairs
have executable separators.

### 1.3 Input completion and STOP

Atomic `C!30 00` is correctly distinct from sequential `C!30` then `C!00`.
Clean `C-down` is also structurally distinct from every nonempty client message
and returns `R!87` before halting.

The STOP/framing section nevertheless claims four displayed histories separate
STOP, an empty submission, one malformed two-byte message, and two one-byte
messages.  Its four histories are actually:

```text
C-down
C!fe
C!30 00
C!30 ; C!00
```

No empty datagram exists; the seed explicitly marks it unsupported.  It also
calls both `fe` and `30 00` malformed while its rejection taxonomy calls `fe`
an unknown opcode and only `30 00` malformed.

The clean STOP suite is declared separate, while the global crossing rule says
a crash may occur before or after any crossing.  L exposes two conditional
STOP crash schedules, whereas S and the seed expose clean STOP only.  The
comparator exercises the L schedules but excludes them from equality and marks
the scope `UNKNOWN`; it does not invent a precedence rule.

### 1.4 Crash nondeterminism is not yet an equivalence

After the same public prefix:

```text
C!10 ; K!CRASH ; K!RESTART ; R!88 ; C!30
```

an interrupted one-byte write with the old outcome leads to `R!e0 03`, while
the new outcome leads to `R!e0 04`.  Old/new is not a public crossing label.

Section 5 says histories are equivalent when every common future “produces
identical” projections, but never says to compare complete may-trace sets.  A
pointwise reading can compare different nondeterministic samples and make even
`H ~ H` fail.  The executable experiments conditionally use exact set equality
or an instrumented old/new directive.  That interpretation is coherent and
produces the 14/18 result, but it is not authorized uniquely by the frozen
text.

No probability, fairness, must-trace, or liveness distribution is declared.

## 2. Representation and deletion results

### 2.1 Information lower bound

Fourteen cut classes require at least four fixed information bits at the cut.
All eighteen full-horizon classes require at least five.  This is a quotient
cardinality statement, not a prescription for five named bits.

The three post-partition candidates are injective over all eighteen classes:

- one packed byte `00..11` hexadecimal;
- a four-byte length-plus-three-slot canonical representative; and
- a three-byte discriminator/probe signature.

The executable experiment checked all 153 candidate class merges and all three
encodings.  A hash alone is neither used nor credited.

### 2.2 MUST SURVIVE

Conditional on exact may-trace-set semantics, only the following past
information responsibilities survive at quiescent execution boundaries:

| responsibility | smallest fixed-pair witness |
|---|---|
| current contract revision | `[]` / `[50]`, future `[50]` or identity `[60]` |
| restricted table absence versus presence | `[]` / `[10]`, future `[20]` |
| restricted table I versus N | `[10]` / `[11]`, future `[00,30]` |
| observation absence versus presence | `[]` / `[00]`, future `[10,30]` |
| observation zero versus one | `[00]` / `[01]`, future `[10,30]` |
| actual old/new durable resolution after an interrupted mutator | same public crash prefix, then a probe whose result depends on recovered reduction; the public contract must compare the two-result set |

The channel/message/half-close boundary and ordered `C/R/D/K` crossing
machinery are also total-system responsibilities.  Their deletion changes
same-turn transcripts even when they are not semantic state persisted between
clean requests.

### 2.3 MAY REBUILD

Given a lossless representation of the eighteen-class responsibility and the
frozen seed specification, the following are deterministic reconstructions:

- current identity bytes;
- query result;
- action-attempt payload;
- immediate rejection code;
- every success/restart reply;
- interpreted bit;
- packed class number, canonical representative, and probe signature when a
  different lossless representation survives;
- L's log length from its contiguous non-`ff` prefix; and
- every behaviorally necessary derived value after discarding a nonpersistent
  cache; the cache's exact irrelevant contents need not be reconstructable.

The decoder, specification, mapping, and recomputation code are TCB and are
charged.  Behavioral equality cannot establish that an implementation
physically recomputes rather than uses a correct hidden cache.

### 2.4 MAY FORGET

Under the bounded future language and intended set semantics, exhaustive
congruence supports forgetting:

- multiplicity and order before the latest surviving reduction;
- overwritten observation values and replaced table selections;
- successful or rejected queries and action attempts after their crossings;
- immediate rejection explanations after delivery;
- prior identities and replies;
- any latest-error or latest-response responsibility; and
- whether `D` crossed for an interrupted action, from the engine after restart,
  because the occurrence is never replayed automatically.

An external client may remember an observed `D` and choose to submit a new
action occurrence.  That policy memory is outside engine state but remains
part of the future continuation; it is not proof that the earlier crossing did
not occur.

L deliberately retains more past mutation order than the semantic quotient.
That over-preservation is a storage/operations tradeoff, not a new semantic
MUST verdict.

## 3. Unlike realization experiment

### 3.1 Independent local results

Realization L uses a five-byte `ff`-initialized append/replay image.  Its
independent self-test reports:

| L measurement | count |
|---|---:|
| reachable images | 4,754 |
| reachable images by length 0..5 | `1,5,26,138,732,3852` |
| image/message pairs | 52,294 |
| successful mutations | 24,841 |
| semantic no-ops among them | 7,708 |
| rejections | 16,523 |
| read-only successes | 7,842 |
| successful actions | 3,088 |
| action schedules | 12,352 |
| scanner-alphabet images | 16,807 |
| invalid scanner images | 12,053 |

Realization S uses one packed byte and independently reports:

| S measurement | count |
|---|---:|
| valid images | 18 |
| invalid byte images | 238 |
| image/message pairs | 198 |
| state changes | 69 |
| semantic no-ops | 24 |
| rejections | 71 |
| read-only successes | 34 |
| old/new write outcomes | 138 |
| no-write cases | 129 |

Both self-tests pass.  They share the frozen semantics, Python runtime, OS, and
underlying machine; those dependencies remain common TCB.

### 3.2 Third-harness result

The comparator does not import either product implementation.  It drives their
different JSONL protocols as black-box subprocesses and compares both with its
own history oracle.

| comparison measurement | result |
|---|---:|
| factored history/future state cases | 46,848 |
| expanded scripts | 194,712 |
| L expanded symbolic schedule obligations | 1,790,701 |
| S expanded symbolic schedule obligations | 1,748,699 |
| expanded per-script canonical outcome obligations, including recovered/final quotient metadata | 1,748,699 |
| actual L JSONL protocol calls | 32,749 |
| actual S JSONL protocol calls | 29,445 |
| logical S reset/boot congruence cycles inside one subprocess | 6,864 |
| full/cut/handler/rejection merge attacks | `153 / 91 / 55 / 15` |
| characteristic-interpreter evaluations | 17,689 |
| action-retry cases | 32 |
| deliberate local sensitivity controls caught | `10 / 10` |

The exact result is:

```text
FACTORED ABSTRACT ONE-BYTE TRANSITION RELATION = PASS
COMPLETE END-TO-END UNLIKE SOFTWARE EQUIVALENCE = UNKNOWN
PHYSICAL MEDIA / REAL POWER LOSS = NOT CLAIMED
```

The 1.79/1.75 million figures are expanded symbolic obligations, not subprocess
runs.  The first harness draft mislabeled such multiplicities; an independent
reviewer caught the error.  The frozen version separates actual requests from
symbolic factoring and explicitly leaves the end-to-end claim unknown.

### 3.3 Schedule-count falsification

The seed's `17` schedules per script is a loose sum of incompatible maxima:

```text
1 + 2*maximum_writes + maximum_crossing_gaps
```

Three actions can yield ten gaps and zero writes.  Three mutators can yield
three writes but fewer gaps.  Under its rule that write-adjacent boundary gaps
are replaced by old/new outcomes rather than duplicated, the per-script
maximum is eleven.  Exact expanded conditional counts are:

```text
L = 1,790,701
S = 1,748,699
total = 3,539,400
```

The frozen `6,620,208` is a conservative arithmetic upper bound only.  Its
later statement that both realizations must “complete all 6,620,208 bounded
runs” incorrectly treats the bound as an exact executable run set.

## 4. Mandatory attacks and complexity location

| attack | evidence-backed result |
|---|---|
| DELETE | oracle/model-level deletion checks support revision/table/observation witnesses and conditional removal of derived outputs/old history; the complete implementation attack matrix is unknown |
| MERGE | all 91 cut and 153 full oracle class pairs separate under intended set semantics; model-level handler/rejection merges were exercised |
| DERIVE | oracle/model checks rebuild identity, query/action/rejection outputs and representation transforms from quotient responsibility plus spec; implementation-wide derivation remains unknown |
| RECOMPUTE | L replay and S decoding pass local tests; full fresh-session recomputation over every expanded schedule remains unknown |
| COLLIDE | three candidate encodings are injective; false empty-history prose and ambiguous crash relation are specification failures rather than encoding collisions |
| FUTURE | oracle depth-three residual search proves the conditional 14/18 partition; two printed fixed-pair minima are false and global ordering remains incomplete |
| EXTERNALIZE | receiver effect, policy memory, one-byte adapter, atomic framing, Python/runtime, and oracle stay charged |
| REALIZE | two independent programs and a third harness exist; factored model passes, end-to-end and physical evidence remain unknown |
| COGNITION | eleven messages are manageable, but 616 lines, false counts, and unstated set semantics still force invention |
| TCB | parser/reducer/recovery/output ordering are independent; OS, Python, filesystem, seed, harness, byte axiom, and human procedure remain shared/untested |

The compact five-bit information lower bound moves rather than deletes
complexity.  Current locations include:

- the 28,021-byte frozen specification;
- 52,193 bytes of reference experiment code;
- 43,249 bytes of L code and 41,734 bytes of S code;
- 76,509 bytes of third-harness code;
- Python and its standard library;
- atomic message framing and half-close semantics;
- old/new nondeterministic-set handling;
- the stipulated one-byte durability adapter;
- external client memory and receiver-side action risk;
- independent build/recovery procedures; and
- evidence capture, source association, and human review.

No one-byte semantic image makes those responsibilities zero.

## 5. Simultaneous total-system evaluation

No scalar score is computed and no measurement is borrowed from a different
build to create a synthetic winner.

| dimension | evidence-backed H11 result |
|---|---|
| information preservation | conditional 14/18-class partition with all-pair witnesses; total crash equivalence still underspecified |
| persistent state | abstract L=5 bytes, S=1 byte; actual physical byte atomicity and durability are axioms, not evidence |
| semantic machinery | three independently authored reducers/harnesses agree on the factored relation; false frozen predictions remain |
| human cognition | small alphabet, but action-attempt/effect and old/new sets require careful distinction; text defects caused real disagreement |
| authoring burden | `10/11` replace two frozen table choices; no authored table bytes or arbitrary interpreter language exist |
| query/navigation burden | one fixed query and identity request; discovery, selection, aggregation, and navigation are unsupported |
| runtime | reproducible local/reference/harness measurements recorded above; no real device fault campaign |
| storage | logical image capacities and code sizes measured; runtime, filesystem, reserved space, metadata, and evidence storage remain charged |
| operations | deterministic self-tests and JSONL protocols exist; deployment, cold device recovery, cleanup/reset, and operator dossier do not |
| trusted computing base | code independence improved; shared spec, Python, OS, hardware, harness, and one-byte axiom remain |
| evolution | one irreversible revision and exact current identity; migrations, further versions, downgrade, and reinterpretation unsupported |
| portability | standard-library software is portable only conditionally; no second physical medium or durability adapter is demonstrated |
| explainability | six immediate coded rejection distinctions; no later explanation query, saved provenance, or physical proof of cache absence |
| information-loss risk | acknowledged mutators survive under the axiom; unacknowledged old/new and action-attempt uncertainty are explicit; other faults unsupported |

## 6. Archive replay and unsupported surface

The old archive was opened only after the fresh H11 break.  It added no new
exact H11 counterexample.  It kept these claims at `UNKNOWN`:

- actual transport completion and durability-before-reply ordering;
- physical absence of hidden caches, latest responses, timers, processes, or
  background retry;
- receiver attempt-adapter behavior and any receiver semantic effect;
- implementation-specific malformed/counterfeit/replayed recovery images;
- cleanup/reset equivalence and cold bootstrap;
- exact artifact/build/run evidence binding and replay packs;
- toolchain/dependency inventory, TCB mutation, and cognition measurements;
- complete end-to-end unlike execution; and
- real power-loss behavior and physical byte cost.

Arbitrary inputs, interpreters, versions, histories beyond five occurrences,
multiple/recovery crashes, concurrency, clocks, authority, privacy, erasure,
randomness, partitions, Byzantine behavior, corruption, and rollback are
explicitly unsupported.  They are not passed capabilities.

The exact-history separator is likewise outside the eleven-message language.
Its theorem is valid only after specifying which pre-install history snapshot
the hypothetical interpreter receives; query-time history includes the
author/install crossing and does not literally match the seed's informal proof.

## 7. Boundary of the result

H11 establishes the first practically enumerated, all-capability finite core in
this restart:

- a small end-to-end corpus exists;
- its deterministic reduction and conditional quotient are known;
- conditional survival/rebuild/forget responsibilities have fixed-pair minimal
  separators;
- two unlike representation programs exist independently; and
- a third harness identifies precisely what its factoring proves and does not
  prove.

It does not yet establish the requested first milestone as a total result.  A
defensible successor must, without inheriting H11 as an ontology:

1. state may-trace-set equality explicitly;
2. totalize half-close/crash precedence;
3. remove the nonexistent empty-submission claim;
4. freeze a complete minimization order and corrected witnesses;
5. publish exact schedule sets rather than incompatible-maxima products; and
6. either execute complete end-to-end unlike sessions and physical faults or
   keep those dimensions explicitly unknown.

The smallest defended persistent responsibility in this searched domain is the
eighteen-way future-behavior class, not H11's packed byte, L's five cells, or
three named coordinates.  Which representation minimizes the total system
remains a Pareto question because code, recovery, storage, cognition,
operations, evolution, portability, and trust do not order the candidates the
same way.
