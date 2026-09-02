# FBH-12/2/3: a finite boundary-history seed

## Status and claim boundary

This document specifies a finite, closed-world experiment. It defines exact boundary histories, bounded adaptive futures, a total oracle over the declared domain, crash/recovery schedules, canonical witness minimization, and falsifiable predictions.

It reports no implementation, execution result, physical-storage fact, power-loss result, or empirical evidence.

## 1. Exact boundary histories are the primitive

A history is an exact ordered sequence of atomic boundary crossings. No internal field, record, log, event store, cache, or physical representation is assumed.

### 1.1 Channels

| Channel | Crossing | Meaning |
|---|---|---|
| `C` | client → service | One complete request frame, or typed `FIN` |
| `R` | service → client | One complete reply frame, or `STOPPED\n` |
| `A` | service → independent capture peer | One externally visible action-attempt frame |
| `L` | lifecycle observation | Typed `DOWN` and `READY` notifications |
| `F` | privileged harness control | `CRASH(gap)` and `SELECT(old\|new)` |

`C`, `R`, and `A` frames are nonempty ASCII byte strings ending in one LF. A frame crossing is all-or-nothing in this seed. Fragmentation, partial frames, and torn crossings are unsupported.

A request occurrence on `C` and its completion on `R` are separate crossings. An `A` crossing, when present, is separate from both. No pair of crossings is claimed atomic.

`F` is inaccessible to the legal client. `F:SELECT` is recorded in the run manifest but erased from observable histories. It is not a public byte crossing. `L:DOWN` and `L:READY` are observable typed lifecycle crossings, not client messages.

### 1.2 The complete nonempty client alphabet

The order shown is also the canonical message order.

| Rank | Alias | Exact request bytes |
|---:|---|---|
| 0 | `O0` | `OBSERVE 0\n` |
| 1 | `O1` | `OBSERVE 1\n` |
| 2 | `AI` | `AUTHOR ID\n` |
| 3 | `AN` | `AUTHOR NOT\n` |
| 4 | `RI` | `REPLACE ID\n` |
| 5 | `RN` | `REPLACE NOT\n` |
| 6 | `D` | `RETIRE\n` |
| 7 | `Q` | `QUERY\n` |
| 8 | `X` | `EXPLAIN\n` |
| 9 | `T` | `ATTEMPT\n` |
| 10 | `E` | `EVOLVE\n` |
| 11 | `K` | `CURRENT\n` |

These twelve messages are the entire legal input alphabet. Empty request frames are unsupported and are never counted as submissions.

Authoring and interpretation are bounded: the only authorable or replaceable programs are `ID` and `NOT`. No arbitrary source, bytecode, callback, expression, or interpreter input is legal.

### 1.3 STOP and half-close

Termination is not an empty request. It consists of two explicit crossings:

1. typed occurrence `C:FIN`;
2. completion `R:STOPPED\n`.

After `C:FIN`, no further `C` request frame is legal.

Crash precedence is exact:

- A crash before `C:FIN` completes recovery first; `C:FIN` may then occur.
- A crash after `C:FIN` but before `R:STOPPED\n` preserves the half-close responsibility. After `L:READY`, exactly one `R:STOPPED\n` must cross.
- A crash after `R:STOPPED\n` cannot produce another client reply.
- A crash cannot occur inside either atomic crossing.

STOP is not one of the twelve messages and does not consume the future-message bound.

### 1.4 Pre-cut corpus

For every word \(w\) of length zero, one, or two over the twelve-message alphabet, start a fresh service and execute \(w\) failure-free, serially, with every reply completed. The cut is immediately after the final reply crossing, or at fresh start for the empty word. There is no in-flight request at a cut.

The resulting exact history is \(H(w)\), including every `C`, `A`, and `R` crossing. Since request crossings are retained, distinct words yield distinct exact histories.

\[
|\mathcal H|=12^0+12^1+12^2=1+12+144=157.
\]

## 2. Future-observable equivalence

A legal adaptive client controller:

- starts at a cut;
- issues at most three nonempty client messages, counting retries;
- waits for a reply or for `L:READY` following an interrupted request before issuing another message;
- may choose its next message from the entire observed suffix;
- cannot observe or choose `F:SELECT`;
- eventually performs the explicit FIN/STOPPED handshake.

A legal scheduler chooses either no crash or exactly one crash at a gap between nominal atomic crossings. Recovery is failure-free: after `DOWN`, it reaches `READY`; no second crash occurs.

For a history \(H\), controller \(C\), and scheduler \(S\), define:

\[
\operatorname{May}(H,C,S)
\]

as the set of all complete observable suffix traces produced by every valid hidden `old`/`new` recovery selection. Traces include `C`, `R`, `A`, `L:DOWN`, `L:READY`, FIN, and STOPPED. They exclude `F:CRASH` and `F:SELECT`. Equal traces are deduplicated.

A trace is complete only when the controller has terminated and the FIN obligation has completed. An interrupted ordinary request need not receive a reply; it remains visible through its input crossing and lifecycle interruption.

Let the fixed must-vocabulary be:

- recovery reaches `READY`;
- a legal controller eventually reaches exactly one STOPPED completion;
- no ordinary completion is invented for an interrupted request;
- an `A` crossing occurs only for `T`;
- within a failure-free `T` transaction, `A` precedes its `R` completion;
- every recovery residual is one of the oracle’s old/new alternatives.

\(\operatorname{Must}(H,C,S)\) is the subset of these propositions true for every internal choice represented by the complete may-trace set.

The bounded future-observable equivalence is:

\[
H\equiv_3 H'
\iff
\forall C,S:
\begin{cases}
\operatorname{May}(H,C,S)=\operatorname{May}(H',C,S),\\
\operatorname{Must}(H,C,S)=\operatorname{Must}(H',C,S).
\end{cases}
\]

Comparing one harness-selected outcome is not equivalence. Equality of complete may-trace sets makes the relation reflexive even when old/new recovery is nondeterministic.

## 3. Total history oracle

The following are mathematical functions of the exact completed prefix. They are not claims about stored fields.

- `O(prefix)` is `U` if neither observation has completed; otherwise it is the value of the last completed `O0` or `O1`.
- `P(prefix)` starts as `EMPTY` and is folded over completed configuration commands:

  - `AI` or `AN` changes `EMPTY` to the named program; when nonempty it has no effect.
  - `RI` or `RN` changes a nonempty program to the named program; when empty it has no effect.
  - `D` changes a nonempty program to `EMPTY`; when empty it has no effect.

- `G(prefix)` is `E0` until the first completed successful evolution and `E1` thereafter.

The restricted program result is:

| Program | Observation | Value |
|---|---|---|
| `EMPTY` | any | `NONE` |
| `ID` | `U` | `UNKNOWN` |
| `ID` | `0` | `DENY` |
| `ID` | `1` | `ALLOW` |
| `NOT` | `U` | `UNKNOWN` |
| `NOT` | `0` | `ALLOW` |
| `NOT` | `1` | `DENY` |

These history functions cover every legal prefix. No hidden default is left unspecified.

### 3.1 Exact failure-free completions

For a pre-request completed prefix:

| Request | Exact crossings after its `C` occurrence |
|---|---|
| `O0` | `R:OK OBSERVE 0\n` |
| `O1` | `R:OK OBSERVE 1\n` |
| `AI`, when `P=EMPTY` | `R:OK AUTHOR ID\n` |
| `AI`, otherwise | `R:ERR ACTIVE\n` |
| `AN`, when `P=EMPTY` | `R:OK AUTHOR NOT\n` |
| `AN`, otherwise | `R:ERR ACTIVE\n` |
| `RI`, when `P≠EMPTY` | `R:OK REPLACE ID\n` |
| `RI`, otherwise | `R:ERR EMPTY\n` |
| `RN`, when `P≠EMPTY` | `R:OK REPLACE NOT\n` |
| `RN`, otherwise | `R:ERR EMPTY\n` |
| `D`, when `P≠EMPTY` | `R:OK RETIRE\n` |
| `D`, otherwise | `R:ERR EMPTY\n` |
| `Q` | `R:VALUE <V>\n` |
| `X` | `R:WHY O=<O> P=<P> E=<G> V=<V>\n` |
| `T` | `A:TRY O=<O> P=<P> E=<G> V=<V>\n`, then `R:OK ATTEMPTED\n` |
| `E`, when `G=E0` | `R:OK ENGINE E1\n` |
| `E`, when `G=E1` | `R:OK ENGINE E1 ALREADY\n` |
| `K` | `R:ENGINE <G>\n` |

Angle-bracket substitutions select one of the finite uppercase tokens already defined. They are not literal angle brackets in output.

`X` is immediate in the boundary sense: its explanation crosses as that transaction’s completion before any next input can be accepted. No wall-clock latency claim is made.

`E` permits exactly one identity transition, `E0 → E1`; later evolution requests are idempotent and observable as already evolved. Policy values are identical across engines, while `K`, `X`, and `T` expose current engine identity.

### 3.2 Externally visible action attempt

An `A` crossing means only that the exact `TRY ...\n` frame was observed and atomically recorded by the independent capture peer at the defined boundary.

It does not claim:

- an application receiver effect;
- durable receiver storage;
- success of a downstream action;
- atomicity with the request or reply;
- exactly-once behavior.

`OK ATTEMPTED\n` asserts only that the preceding `A` crossing occurred for that transaction.

### 3.3 Crash and old/new recovery

A crash may occur only between atomic crossings.

For an ordinary request whose `C` occurrence crossed but whose `R` completion did not:

- `old` continues from the residual behavior immediately before that request occurrence;
- `new` continues from the residual behavior obtained by applying that request’s specified transition;
- the interrupted request receives no reply after recovery;
- already crossed `A` frames remain in the trace and cannot be retracted.

For requests that do not change residual behavior, or whose precondition failed, old and new collapse to one outcome. Once the reply crosses, only new is permitted. Before the input crosses, only old is permitted.

The privileged harness may force a branch only while the service is stopped at the corresponding fault barrier. The authority belongs to the test launcher through `F:SELECT(old|new)`, not to the client. The selector is absent from `C`, `R`, `A`, and observable trace projection. An implementation without a forceable selector cannot establish completeness of its may set; that result remains unknown.

### 3.4 Totality and closed-world handling

For every valid tuple `(prehistory, adaptive controller, scheduler, selector assignment)`, the oracle terminates because the bounds are finite.

For any description outside that domain, the meta-oracle returns `UNSUPPORTED(reason)` rather than inventing a boundary trace. Thus the oracle is total as a classifier while making behavioral predictions only inside the declared domain.

## 4. Exact separating and crash witnesses

Aliases below denote the exact bytes in Section 1.2. These examples are exact witnesses but are not claimed to be the canonical minimal witness for their subject.

| Obligation | Histories and future | Exact differing observation |
|---|---|---|
| Observation | `H(O0)` vs. `H(O1)`; future `X` | `WHY O=0 P=EMPTY E=E0 V=NONE\n` vs. `WHY O=1 P=EMPTY E=E0 V=NONE\n` |
| Restricted interpretation | `H(O0,AI)` vs. `H(O0,AN)`; future `Q` | `VALUE DENY\n` vs. `VALUE ALLOW\n` |
| Authorability | `H()` vs. `H(AI)`; future `AI` | `OK AUTHOR ID\n` vs. `ERR ACTIVE\n` |
| Replacement | `H(AI)` vs. `H(AI,RN)`; future `X` | `P=ID` vs. `P=NOT` in the exact explanation |
| Retirement | `H(AI)` vs. `H(AI,D)`; future `X` | `P=ID` vs. `P=EMPTY` |
| Query | `H(O1,AI)`; future `Q` | `R:VALUE ALLOW\n` |
| Immediate explanation | `H(O1,AI)`; future `X` | Same-transaction `R:WHY O=1 P=ID E=E0 V=ALLOW\n` |
| Evolution/current identity | `H()` vs. `H(E)`; future `K` | `ENGINE E0\n` vs. `ENGINE E1\n` |
| Action attempt | `H(O1,AI)`; future `T` | `A:TRY O=1 P=ID E=E0 V=ALLOW\n` before `R:OK ATTEMPTED\n` |

### 4.1 Exact author-crash may set

From `H()`, use a controller that sends `AI`, retries `AI` once after recovery if no reply crossed, and then half-closes. Crash in the gap after the first input and before its reply.

The complete may-trace set is exactly:

```text
{
  C:"AUTHOR ID\n",
  L:DOWN,
  L:READY,
  C:"AUTHOR ID\n",
  R:"OK AUTHOR ID\n",
  C:FIN,
  R:"STOPPED\n"
}
```

and

```text
{
  C:"AUTHOR ID\n",
  L:DOWN,
  L:READY,
  C:"AUTHOR ID\n",
  R:"ERR ACTIVE\n",
  C:FIN,
  R:"STOPPED\n"
}
```

The first is the old branch; the second is the new branch. `F:SELECT` appears in neither observable trace. Both branches must recover and terminate.

### 4.2 Exact action retry traces

From `H(O1,AI)`, let the controller retry `T` once only if its reply did not cross.

Crash before the first `A` crossing produces one externally visible attempt:

```text
C:"ATTEMPT\n",
L:DOWN,
L:READY,
C:"ATTEMPT\n",
A:"TRY O=1 P=ID E=E0 V=ALLOW\n",
R:"OK ATTEMPTED\n",
C:FIN,
R:"STOPPED\n"
```

Crash after the first `A` crossing but before its reply produces two externally visible attempts:

```text
C:"ATTEMPT\n",
A:"TRY O=1 P=ID E=E0 V=ALLOW\n",
L:DOWN,
L:READY,
C:"ATTEMPT\n",
A:"TRY O=1 P=ID E=E0 V=ALLOW\n",
R:"OK ATTEMPTED\n",
C:FIN,
R:"STOPPED\n"
```

Crash after the reply produces one attempt and no retry under this controller. These are crossing counts only, never receiver-effect counts.

### 4.3 Exact STOP crash witness

With no future request, a crash between FIN and STOPPED yields:

```text
C:FIN,
L:DOWN,
L:READY,
R:"STOPPED\n"
```

There is one FIN occurrence and one completion. It is not an empty submission.

### 4.4 Exact-history interpreter theorem outside the seed

Let \(H_a\neq H_b\) be distinct exact histories. In a hypothetical extended language, bind in each run:

\[
pre := \operatorname{Encode}(\text{exact history ending immediately before the install request occurrence}).
\]

Only after that snapshot is bound, send the same hypothetical request:

```text
INSTALL EQ <literal Encode(H_a)>
```

The hypothetical interpreter returns `ALLOW` exactly when `pre` equals the literal. A later query therefore separates \(H_a\) from \(H_b\). The snapshot excludes the install crossing itself, so the separator proof is literal and non-self-referential.

`INSTALL EQ ...` is outside the twelve-message alphabet. It is unsupported, is never enumerated, and provides no lower bound or equivalence claim for this seed’s restricted interpreter.

## 5. Canonical minimization and attack battery

### 5.1 Complete witness order

Every generated minimal witness uses this total order:

1. **Unordered history-pair orientation.** Order histories by `(message count, message-rank word, exact history encoding)` and place the lesser history first.
2. **Distribution across histories and future.** Compare  
   \[
   (|H|+|H'|+|F|,\ |H|,\ |H'|,\ |F|)
   \]
   lexicographically after orientation.
3. **Message order.** Compare history words and adaptive controller nodes by the twelve-message rank order. Controller branches are ordered by exact observed-block encoding.
4. **Crash position and ordinal.** `no-crash` ranks first. Otherwise, number nominal crossing gaps from zero before the first crossing through the gap after the last crossing. Compare gap ordinal, then request ordinal and phase. Hidden branch order is `old < new`.
5. **Outcome-set serialization.** Encode each crossing as tag, direction, byte length, and bytes; sort complete traces lexicographically; encode set cardinality followed by length-prefixed traces. Compare the two oriented outcome sets lexicographically.
6. **Final tie-breaker.** Compare the complete length-prefixed controller and scheduler serializations bytewise.

This order covers pair orientation, message distribution, message ordering, crash placement, branch ordering, and unordered outcome sets. No wall-clock timing participates.

### 5.2 Required attacks

Each attack records `PASS`, `FAIL`, or `UNKNOWN`; no omitted attack is silently treated as a pass.

| Attack | Exact operation and criterion |
|---|---|
| **DELETE** | Remove one named candidate responsibility, cold-start, and rerun the corpus. Equality shows only corpus-level behavioral redundancy; it does not prove physical absence. |
| **MERGE** | Force two tentative continuation labels to share one realization. Run their canonical separator. Any differing may set or must set rejects the merge. |
| **DERIVE** | Delete target bytes and rebuild them solely from an explicitly named surviving responsibility plus the frozen specification. Success permits only the label `MAY REBUILD from <responsibility> + <specification>`. |
| **RECOMPUTE** | Restart without the target representation and reconstruct behavior by replay or table evaluation from named surviving inputs. Record replay cost and recovery machinery rather than calling the work free. |
| **COLLIDE** | Exhaustively compare encodings of distinct reachable residual and pending conditions. Force or synthesize equal hashes where hashing is used; a distinguishable collision is a failure. |
| **FUTURE** | Apply bounded adaptive partition refinement through depth three with every legal message, schedule, complete may set, and must verdict. Linear examples alone are insufficient. |
| **EXTERNALIZE** | Move a responsibility to a client, capture peer, build artifact, or service. Then sever that source during recovery. Passing behavior means the responsibility moved; it was not eliminated. |
| **REALIZE** | Build two unlike realization families and compare each independently with the oracle and harness. A design sketch is not a pass. |
| **COGNITION** | Give a fresh implementer only the frozen specification and manifests. Undocumented human knowledge needed to reproduce behavior is a surviving responsibility and a failure of the claimed factoring. |
| **TCB** | Enumerate and perturb trusted runtime, OS, transport, serializer, compiler, caches, fault hook, capture peer, oracle, canonicalizer, and build inputs. Untested hidden state remains `UNKNOWN`. |

## 6. Predicted quotient

Only after the exact witnesses and attack definitions do we classify histories.

The predicted continuation coordinate is:

\[
(O,P,G)\in\{U,0,1\}\times\{EMPTY,ID,NOT\}\times\{E0,E1\}.
\]

This is a quotient label derived from histories, not a proposed storage record.

Histories with the same coordinate have identical future transitions, replies, action frames, old/new alternatives, and STOP behavior by induction on remaining controller depth and crash budget. Histories with different coordinates are separated by the one-message future `X`, whose exact reply includes all three coordinates. Empty future produces only coordinate-independent STOP behavior, so every distinct-class separator needs at least one future message.

### 6.1 Predicted class counts

| Predicted coordinate | Length 0 | Length 1 | Length 2 | Class size |
|---|---:|---:|---:|---:|
| `(U,EMPTY,E0)` | 1 | 7 | 51 | 59 |
| `(0,EMPTY,E0)` | 0 | 1 | 16 | 17 |
| `(1,EMPTY,E0)` | 0 | 1 | 16 | 17 |
| `(U,ID,E0)` | 0 | 1 | 15 | 16 |
| `(U,NOT,E0)` | 0 | 1 | 15 | 16 |
| `(U,EMPTY,E1)` | 0 | 1 | 15 | 16 |
| `(0,ID,E0)` | 0 | 0 | 2 | 2 |
| `(0,NOT,E0)` | 0 | 0 | 2 | 2 |
| `(0,EMPTY,E1)` | 0 | 0 | 2 | 2 |
| `(1,ID,E0)` | 0 | 0 | 2 | 2 |
| `(1,NOT,E0)` | 0 | 0 | 2 | 2 |
| `(1,EMPTY,E1)` | 0 | 0 | 2 | 2 |
| `(U,ID,E1)` | 0 | 0 | 2 | 2 |
| `(U,NOT,E1)` | 0 | 0 | 2 | 2 |
| **Sum** | **1** | **12** | **144** | **157** |

The predicted class-size multiset is:

\[
\{59,17,17,16,16,16,2,2,2,2,2,2,2,2\},
\]

which sums to 157.

Among the \(\binom{157}{2}=12{,}246\) distinct unordered history pairs:

- predicted same-class pairs:

  \[
  \binom{59}{2}+2\binom{17}{2}+3\binom{16}{2}+8\binom{2}{2}
  =1711+272+360+8
  =2351;
  \]

- predicted unequal pairs:

  \[
  12{,}246-2351=9895.
  \]

The 157 diagonal pairs are separately reflexive by exact equality of their complete may and must results.

## 7. Representation candidates and cautious classifications

### 7.1 Candidate representations

These candidates follow the quotient calculation; none is reported as implemented.

1. **Exact transcript/replay.** Retain accepted boundary commands and fold them under the frozen specification after restart. This preserves distinctions beyond the predicted quotient.

2. **Quotient atom/table.** Represent one canonical continuation label and use a generated transition/output table. Fourteen labels occur at the cut; the full future transition domain can reach all eighteen `(O,P,G)` combinations.

3. **Factored finite realization.** Maintain separate finite responsibilities corresponding to the three quotient axes and interpret them through direct conditionals.

4. **Externalized continuation token.** Require a client-supplied authenticated continuation token on each request. Authentication and authority are outside this seed, so this candidate is useful only for the EXTERNALIZE attack and is not presently conforming.

During an interrupted operation, every family also needs a realization of pending completion, old/new recovery authority, and durable FIN responsibility. Comparing cut labels alone is not a total-system comparison.

### 7.2 Permitted classifications

| Subject | Classification |
|---|---|
| Distinguishing the fourteen predicted cut classes | Boundary-required responsibility under this closed finite model; no storage location or physical byte count follows |
| Distinctions between histories in one predicted class | Predicted behaviorally irrelevant within the seed only |
| Exact reply and action bytes | `MAY REBUILD from continuation responsibility + current legal request + frozen specification` |
| Exact pre-cut transcript | Predicted deletable only if another surviving responsibility preserves all continuation behavior |
| Pending FIN after its crossing | Boundary-required until exactly one STOPPED completion |
| Externalized state | Responsibility moved to the named external dependency |
| Caches, allocator state, filesystem metadata, runtime state, and hidden tables | `UNKNOWN` until DELETE, EXTERNALIZE, and TCB attacks exercise them |
| Power-loss or media persistence | `UNKNOWN` and unsupported |

No derived byte component is classified as physically MUST. “Behaviorally irrelevant” never means “physically absent.”

## 8. Total-system, non-scalar evaluation

No single scalar such as byte count, field count, or source-line count decides superiority.

| Dimension | Transcript/replay | Quotient atom/table | Factored finite |
|---|---|---|---|
| Cut representation | Potentially grows with history | One finite label | Three finite responsibilities |
| Transition complexity | Mostly in replay fold | Moves into generated table and generator | Moves into conditional interpreter |
| Recovery | Journal framing and replay boundary | Snapshot/commit protocol and pending phase | Component commit protocol and pending phase |
| Exact output construction | Serializer plus replay result | Table/serializer | Interpreter/serializer |
| Extra historical distinctions | Retained | Intentionally merged | Usually merged |
| Proof burden | Replay correctness | Quotient and generator correctness | Component interaction correctness |
| Corruption surface | Journal and framing | Code, snapshot, table | Components, code, snapshot |
| Cognitive burden | History model | Generation pipeline | Conditional semantics |
| TCB | Runtime, journal, serializer, spec | Runtime, generator, table, serializer, spec | Runtime, interpreter, serializer, spec |

Reducing one runtime representation may move complexity into code, generated tables, recovery metadata, specifications, test manifests, external dependencies, or human knowledge. Software factoring alone provides no evidence about physical power interruption, storage media, controller caches, or hardware independence.

## 9. Operational enumeration and realization obligations

### 9.1 Terminating oracle algorithm

1. Enumerate prehistory words by length and canonical message order.
2. Produce each exact failure-free `H(w)` and validate every crossing byte.
3. Enumerate linear future paths of length zero through three, always appending FIN/STOPPED.
4. For each path, construct its nominal crossing sequence.
5. Enumerate no crash and one crash at every nominal gap.
6. At an interrupted request gap, symbolically evaluate old and new; deduplicate equal complete traces.
7. Compute must propositions over each complete outcome set.
8. Use memoized depth-bounded partition refinement on `(residual behavior, remaining depth, crash budget, phase)`.
9. Orient every unequal history pair and perform breadth-first separator search using the complete minimization order.
10. Emit the quotient, class membership, pair witnesses, may sets, must sets, and a run manifest.

A conservative symbolic-configuration bound is:

\[
18\text{ residual labels}\times4\text{ depths}\times2\text{ crash budgets}\times16\text{ phases}=2304.
\]

The sixteen-phase bound comprises idle, twelve possible pending requests, post-action/pre-reply, FIN-pending, and terminal. Many combinations are unreachable; 2304 is not an execution count.

Adaptive controllers need not be enumerated as enormous whole trees. Partition refinement examines every possible next message and every output branch at each memoized node. Induction on remaining depth establishes equivalence for all deterministic adaptive controllers.

### 9.2 Exact schedule counts

For a fixed linear future with \(n\) messages and \(t\) occurrences of `T`:

- ordinary requests contribute two nominal crossings;
- each `T` contributes one extra `A` crossing;
- FIN and STOPPED contribute two crossings.

The nominal crossing count is \(2n+t+2\). There are \(2n+t+3\) distinct gaps, plus the no-crash schedule:

\[
\text{schedule cases}=2n+t+4.
\]

Aggregating without multiplying incompatible maxima:

| Future length \(n\) | Words \(12^n\) | Total `T` occurrences \(n12^{n-1}\) | Exact word/schedule cases |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 4 |
| 1 | 12 | 1 | 73 |
| 2 | 144 | 24 | 1,176 |
| 3 | 1,728 | 432 | 17,712 |
| **Total** | **1,885** | **457** | **18,965** |

Across all 157 prehistories, the exact number of linear history/word/schedule cases is:

\[
157\times18{,}965=2{,}977{,}505.
\]

For padded symbolic old/new obligations, allocate one extra branch slot for the interrupted-request gap of each future message, even when the branches later collapse. Per word this is \(3n+t+4\). The exact padded total is:

\[
157\times24{,}449=3{,}838{,}493.
\]

This is a conservative per-realization execution upper bound if every nonapplicable or collapsing selector slot is nevertheless exercised. It is not an actual execution count.

Actual executions must be read from the harness manifest. The seed reports none. Counts from different realization families, adaptive-tree maxima, schedule maxima, and selector maxima must not be multiplied and presented as executed runs.

### 9.3 Unlike realization obligations

The following remain obligations:

- **Family J:** an append-only transcript/replay realization with explicit completion and FIN markers.
- **Family Q:** a generated quotient-atom transition-table realization with explicit pending-operation and FIN phases.
- **Harness H:** an independently implemented exact-history oracle, capture peer, canonicalizer, fault-gap injector, branch selector, and manifest writer.

J and Q must be independently implemented without sharing transition or recovery code. H must not import either realization’s transition implementation. The exact byte specification may be shared as the frozen authority.

Each case starts from a fresh namespace, replays its prehistory failure-free, verifies the exact cut, applies the future and schedule, forces every available recovery branch, completes STOP, and compares canonical complete may sets and must verdicts.

Until J, Q, and H exist independently and pass the attacks, they are proposed families and a proposed harness—not evidence. Even successful process-crash tests would establish only behavior at the defined software boundary, not power-loss, controller, or media behavior.

## 10. Unsupported space

The supported domain is exactly the histories, messages, controller bounds, schedules, crossings, and oracle rules stated above. Its set-theoretic complement is unsupported; no behavior is implied there.

Explicitly unsupported are:

- empty client messages and every byte string outside the twelve exact frames;
- partial, fragmented, duplicated, reordered, or concurrently delivered frames;
- more than two pre-cut or three post-cut client messages;
- more than one client, concurrent requests, races, weak memory, or distributed ordering;
- more than one crash, crash during recovery, unavailable recovery, or arbitrary process failure points inside atomic crossings;
- power interruption, torn media writes, storage-controller behavior, bit corruption, checksums, silent corruption, or rollback;
- snapshots, backup restore, downgrade, replay attacks, or forked histories;
- evolution other than `E0 → E1`, arbitrary migrations, or semantic changes between engines;
- arbitrary observations, sensors, analog values, provenance, or physical-world truth;
- arbitrary programs, interpreters, plugins, callbacks, expressions, code loading, or side effects;
- downstream receiver behavior, delivery, execution, durability, idempotence, or exactly-once effects;
- authentication, authorization, ownership, delegation, tenancy, quotas, billing, or administrative authority;
- confidentiality, privacy, erasure law, traffic analysis, metadata leakage, or access isolation;
- clocks, timeouts, deadlines, expiration, leases, randomness, or real-time liveness;
- resource exhaustion, throughput, latency, fairness beyond the stated finite recovery progress, or denial of service;
- OS, compiler, runtime, filesystem, network, cache, or hardware trust beyond what a recorded TCB attack actually establishes;
- human interpretation not frozen into the specification;
- any external service, storage, or client-held token not explicitly introduced by an EXTERNALIZE experiment.

## 11. Falsifiable predictions

1. Enumeration will produce exactly 157 pre-cut histories.
2. The bounded quotient will contain exactly fourteen classes with size multiset  
   \(\{59,17,17,16,16,16,2,2,2,2,2,2,2,2\}\).
3. There will be exactly 2,351 same-class and 9,895 unequal distinct unordered history pairs.
4. Every unequal pair will have a one-message failure-free separator using `X`; no empty future will separate any pair.
5. No adaptive future of depth at most three and no defined crash schedule will split histories sharing a predicted coordinate.
6. The author-crash/retry witness will have exactly the two complete may traces specified above.
7. A crash after an `A` crossing and before its reply, followed by the defined retry, will expose two attempt crossings without implying two receiver effects.
8. Linear future enumeration will yield exactly 18,965 word/schedule cases and 2,977,505 history/word/schedule cases.
9. The padded old/new symbolic expansion will contain exactly 3,838,493 slots per realization plan.
10. If independently implemented J and Q conform, their complete may sets and must verdicts will match the independent harness for every executed case.
11. Passing software tests will not establish physical absence of hidden state, media durability, power-failure safety, privacy, authority correctness, or downstream exactly-once behavior.
