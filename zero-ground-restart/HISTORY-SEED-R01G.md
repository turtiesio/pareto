# H11: a boundary-history falsification seed

## 1. Claim and limits

This seed defines a finite oracle from exact boundary histories and common future observations. No storage layout, state record, event object, graph, or implementation is part of the definition. Implementations are only falsifiers.

The seed simultaneously exercises:

- observation;
- a deliberately restricted future-authored interpreter family;
- authoring, replacement, and retirement;
- querying;
- an externally visible action attempt;
- distinct explanations of rejection;
- one contract evolution and current contract identity;
- one crash and failure-free recovery;
- two unlike proposed physical realizations.

It makes no claim about arbitrary inputs, unbounded histories, arbitrary interpreter code, concurrency, multiple clients, clocks, authentication, confidentiality, Byzantine faults, random corruption, network partitions, more than one crash, another crash during recovery, downgrade, further contract versions, receiver-side semantic effects, or capacity beyond the stated horizon. Such cases are unsupported, not implicitly accepted or rejected.

## 2. Exact boundary histories

A transcript is a totally ordered sequence of labelled crossings. There are no simultaneous crossings.

| Label | Meaning |
|---|---|
| `C!x` | The complete nonempty byte message `x` crossed from client to service. |
| `C↓` | The client-to-service stream completed by half-close. It is not a byte message. |
| `R!x` | The complete nonempty reply message `x` crossed from service to client. |
| `D!x` | The complete nonempty delivery-attempt message `x` crossed from service to the external receiver boundary. |
| `K!CRASH` | The harness removed power. |
| `K!RESTART` | The harness restarted the service. |

Each `C`, `R`, and `D` message is one atomic message crossing. A crash may occur before or after any crossing, never partway through it. No two crossings are jointly atomic.

`C↓` is observably distinct from every `C!x`. On clean `C↓`, the service emits `R!87` and halts. No later client input is legal in that run. An empty datagram is unsupported and is not `C↓`.

The client is sequential: after `C!x`, it waits for the reply, or for crash and recovery, before submitting another message. A successful action may place a `D` crossing before its `R` crossing.

### 2.1 Complete client-message alphabet

Hex bytes are written with spaces between bytes. The complete bounded alphabet has eleven messages:

| Order | Exact bytes | Name |
|---:|---|---|
| 1 | `00` | observe zero |
| 2 | `01` | observe one |
| 3 | `10` | author table I |
| 4 | `11` | author table N |
| 5 | `20` | retire the active table |
| 6 | `30` | query |
| 7 | `40` | attempt external action |
| 8 | `50` | evolve contract |
| 9 | `60` | request current contract identity |
| 10 | `fe` | deliberately unknown opcode |
| 11 | `30 00` | deliberately malformed query framing/length |

No other byte string belongs to the experiment.

The two malformed messages are deliberately finite samples:

- `fe` tests unknown-opcode explanation.
- The single two-byte message `30 00` tests that message framing is not confused with the two messages `30` followed by `00`.

No quantification over all byte strings is implied.

### 2.2 Exact replies

Successful fault-free crossings are:

| Input | Exact output |
|---|---|
| `00` | `R!80 00` |
| `01` | `R!80 01` |
| `10` | `R!81 10` |
| `11` | `R!81 11` |
| successful `20` | `R!82` |
| successful `30`, interpreted bit `b` | `R!83 b` |
| successful `40` | one `D` crossing, then `R!84` |
| successful `50` | `R!85 01` |
| `60` under revision 0 | `R!86 03 00 40 a0` |
| `60` under revision 1 | `R!86 03 01 40 a1` |
| `C↓` | `R!87` |
| completed restart | `R!88` |

Rejections are exact two-byte replies:

| Reply | Explanation |
|---|---|
| `R!e0 01` | unknown opcode |
| `R!e0 02` | malformed supported sample |
| `R!e0 03` | no active interpreter |
| `R!e0 04` | no observation |
| `R!e0 05` | no active interpreter to retire |
| `R!e0 06` | contract is already at its final supported revision |

`fe` always produces `e0 01`. The exact message `30 00` always produces `e0 02`.

There is no saved explanation, last-error register, or last-response register. A rejection is explained by its immediate reply only. Consequently every successful operation has exactly no effect on saved explanation. Later behavior never depends on the most recent reply.

### 2.3 Current contract identity

The revision-specific responsibility descriptors are:

```text
D0 = 00 40 a0
D1 = 01 40 a1
```

They mean revision byte, action opcode, and action-delivery prefix. All other rules in this document are the frozen common contract.

The identity generator is exact concatenation:

```text
identity(D) = 86 || 03 || D
```

It is injective over `D0,D1`; it is not a hash. Every `60` reply is freshly generated from the currently applicable contract responsibility. It is never copied from a previous reply.

## 3. Finite history universe

Let `M` be the ordered eleven-message alphabet above.

A cut history is generated as follows:

1. Start with the empty boundary transcript.
2. Submit a word in `M^0 ∪ M^1 ∪ M^2`.
3. Run each submitted message to quiescence before the next.
4. Permit no crash before the cut.

There are exactly:

```text
1 + 11 + 11² = 133
```

cut histories.

After the cut, a future contains zero through three additional completed `C!x` crossings. It may contain zero or one `K!CRASH`, followed by exactly one `K!RESTART` and `R!88`. If a crash is used:

- it occurs only after the cut;
- no client input is accepted between `K!RESTART` and `R!88`;
- recovery is failure-free;
- a second crash, including one during recovery, is unsupported;
- an interrupted client occurrence is never automatically replayed.

The STOP/framing suite is terminal and separate from the continuing-future product:

```text
C↓ ≺ R!87
C!fe ≺ R!e0 01
C!30 00 ≺ R!e0 02
C!30 ≺ R!e0 03 ≺ C!00 ≺ R!80 00
```

These four histories rule out equality between STOP, an empty submission, one malformed two-byte message, and two one-byte messages.

## 4. Total history oracle

The following are questions answered by replaying the exact accepted boundary history. They are mathematical history reductions, not prescribed storage fields.

- The current contract descriptor is `D1` iff a successful, crash-resolved-new `50` has occurred; otherwise it is `D0`.
- The active interpreter is determined by the last successful occurrence among `10`, `11`, and `20`. `10` selects I, `11` selects N, and `20` selects none.
- The current observation is the last successful `00` or `01`, if any.

The only authorable tables are:

| Authored table | input `0` | input `1` |
|---|---:|---:|
| I (`10`) | `0` | `1` |
| N (`11`) | `1` | `0` |

No submitted table data, predicates, bytecode, history inspection, or additional rows exist.

The fault-free oracle is:

1. `00` and `01` always succeed and replace the prior observation.
2. `10` and `11` always succeed and replace the active interpreter without changing the observation.
3. `20` succeeds only if an interpreter is active. It removes the interpreter and retains the observation. Otherwise it replies `e0 05`.
4. `30` checks for an interpreter first and an observation second:
   - no interpreter: `e0 03`;
   - interpreter but no observation: `e0 04`;
   - otherwise: `83 b`, where `b` is the table result.
5. `40` uses the same validation precedence:
   - no interpreter: `e0 03`, with no `D`;
   - interpreter but no observation: `e0 04`, with no `D`;
   - otherwise, if the result is `b`, it emits:
     - revision 0: `D!a0 b`;
     - revision 1: `D!a1 b`;
     - then `R!84`.
6. `50` succeeds once, changing `D0` to `D1`. Under `D1` it replies `e0 06`.
7. `60` emits the identity generated from the current descriptor.
8. `fe` and `30 00` behave exactly as specified above.
9. Queries, identity requests, action attempts, rejections, and replies change none of the history reductions.

This gives one executable output sequence for every fault-free legal bounded history.

### 4.1 Crash resolution

A successful mutating request is `00`, `01`, `10`, `11`, a permitted `20`, or the first permitted `50`.

Its reply is emitted only after its persistent transition has completed. Therefore:

- a visible success reply implies the new reduction survives restart;
- if crash occurs after `C!x` but before the reply, recovery may expose the old or new reduction, according to the exact old/new outcome of the physical one-byte write;
- no reply belonging to the interrupted occurrence appears after restart.

For a rejected or read-only request, a crash between `C` and `R` discards that occurrence and emits no delayed reply.

For an action request, the only fault-free order is:

```text
C!40 ≺ D!aᵣ b ≺ R!84
```

The exact crash projections are:

```text
C!40 ≺ K!CRASH
C!40 ≺ D!aᵣ b ≺ K!CRASH
C!40 ≺ D!aᵣ b ≺ R!84 ≺ K!CRASH
```

Each is followed by `K!RESTART ≺ R!88`.

There is never an automatic retry. One received `40` occurrence produces at most one `D` crossing. A client retry is a new occurrence and may produce another attempt.

`D!x` means only that one complete delivery attempt crossed the declared receiver boundary. Receiver application, durable acceptance, status lookup, deduplication, and semantic effect are unsupported. Thus the contract honestly exposes loss and possible duplicate attempts after client retry. It makes no exactly-once claim and has no hidden resolving receiver.

## 5. Common-future equivalence

For cut histories `H` and `H′`, define:

```text
H ~ H′
```

iff every legal common adaptive future of at most three client messages, with zero or one permitted crash/restart, produces identical ordered `R` and `D` projections.

A common adaptive future chooses the same next harness action while observations remain equal. Once observations differ, a witness is complete.

Shortest witnesses are found by breadth-first search with this order:

1. minimize the total client occurrences in `H`, `H′`, and the common future;
2. then minimize common-future length;
3. then use the declared message order;
4. then order crash choices as no crash, boundary gap, byte-old, byte-new.

Intermediate action crossings are compared before replies. Pair states with identical observed prefixes are memoized. Fixed future words cover every adaptive branch path; adaptivity does not introduce an unenumerated byte message.

### 5.1 Computed partition at the cut

For reporting only, write:

- `r ∈ {0,1}` for the current descriptor;
- `t ∈ {–,I,N}` for interpreter status;
- `o ∈ {–,0,1}` for observation status;
- `c = 9r + 3t + o`, where `–,I,N` encode as `0,1,2` and `–,0,1` encode as `0,1,2`.

These names are derived after the history partition; they are not required fields.

The 133 cut histories form exactly fourteen classes:

| `r` | `t` | `o` | `c` | Histories |
|---:|---|---|---:|---:|
| 0 | – | – | 0 | 45 |
| 0 | – | 0 | 1 | 15 |
| 0 | – | 1 | 2 | 15 |
| 0 | I | – | 3 | 14 |
| 0 | I | 0 | 4 | 2 |
| 0 | I | 1 | 5 | 2 |
| 0 | N | – | 6 | 14 |
| 0 | N | 0 | 7 | 2 |
| 0 | N | 1 | 8 | 2 |
| 1 | – | – | 9 | 14 |
| 1 | – | 0 | 10 | 2 |
| 1 | – | 1 | 11 | 2 |
| 1 | I | – | 12 | 2 |
| 1 | N | – | 15 | 2 |

The four missing cut classes are `13,14,16,17`; each needs revision, interpreter, and observation and therefore at least three mutating messages. All eighteen classes `0..17` are reachable within the complete five-message horizon.

The partition is separated by three probes:

- `60` separates `r`.
- `00,30` separates `t`: replies end in `e0 03`, `83 00`, or `83 01`.
- `10,30` separates `o`: replies end in `e0 04`, `83 00`, or `83 01`.

Thus any two unequal full-horizon classes have a common future of at most two messages unless revision alone separates them in one.

### 5.2 Surviving information responsibilities and minimized witnesses

Exactly three kinds of past information survive: contract responsibility, active-interpreter status/identity, and observation status/value. Multiplicity, earlier values, queries, actions, rejection explanations, and latest replies do not survive.

| Responsibility | `H` | `H′` | Common future | First differing output |
|---|---|---|---|---|
| contract revision | `[]` | `[50]` | `[60]` | `86 03 00 40 a0` / `86 03 01 40 a1` |
| interpreter absence/presence | `[]` | `[10]` | `[30]` | `e0 03` / `e0 04` |
| interpreter I/N | `[10]` | `[11]` | `[00,30]` | `83 00` / `83 01` |
| observation absence/presence | `[]` | `[00]` | `[10,30]` | `e0 04` / `83 00` |
| observation zero/one | `[00]` | `[01]` | `[10,30]` | `83 00` / `83 01` |

The breadth-first ordering above predicts these witnesses are minimal.

Operational capability witnesses are:

| Capability | `H` | `H′` | Common future | Difference |
|---|---|---|---|---|
| successful retirement | `[10]` | `[10,20]` | `[30]` | `e0 04` / `e0 03` |
| query | `[10]` | `[11]` | `[00,30]` | query bit differs |
| external action | `[10]` | `[11]` | `[00,40]` | `D!a0 00` / `D!a0 01` |
| evolved action contract | `[]` | `[50]` | `[10,00,40]` | `D!a0 00` / `D!a1 00` |
| rejection explanation | `[]` | `[10]` | `[30]` | `e0 03` / `e0 04` |
| stable crash recovery | `[]` | `[10]` | `CRASH,RESTART,[30]` | `e0 03` / `e0 04` |
| in-flight old/new recovery | write-old history for `10` | write-new history for `10` | `RESTART,[30]` | `e0 03` / `e0 04` |

For the last row, the public histories through `K!CRASH` are equal, while their instrumented one-byte fault histories differ by the declared old/new outcome.

### 5.3 Restriction theorem

If future authors could submit unrestricted interpreters that test exact prior-history equality, the quotient would be the identity relation.

Proof: for unequal exact histories `H` and `H′`, submit in both worlds the characteristic interpreter “return one exactly when the prior history equals `H`,” then query it. The outputs differ. Therefore no two unequal histories could merge.

This seed prevents that collapse by permitting exactly I and N, both defined only on the latest one-bit observation.

## 6. Representation candidates, introduced only after the partition

Across the complete horizon there are eighteen distinguishable classes, so a fixed-width exact class identifier needs at least five information bits. This is an information obligation, not a mandate to store five particular bits.

Three quotient representations are candidates:

1. **Packed class byte**

   Store the one byte `c = 9r + 3t + o`, restricted to `00..11` hexadecimal.

2. **Canonical representative word**

   Construct the unique word:

   ```text
   [50 if r=1] ||
   [10 if t=I; 11 if t=N] ||
   [00 if o=0; 01 if o=1]
   ```

   Encode it as one length byte followed by three slots padded with `ff`. This uses four bytes and replays to exactly one quotient class.

3. **Probe signature**

   Store three bytes `[r,u,v]`, where:

   - `u=02,00,01` for `t=–,I,N`, matching the virtual `00,30` discriminator;
   - `v=02,00,01` for `o=–,0,1`, matching the virtual `10,30` discriminator.

All three must be exhaustively checked for injectivity across eighteen classes.

No component is separately `MUST STORE`. The requirement is only to preserve future distinctions. Current identity bytes, query results, action payloads, explanations, class numbers, indices, checks, and cached interpretations are mechanically derivable from surviving exact bytes plus this frozen specification and therefore are `MAY REBUILD`.

## 7. Architecture-neutral persistence fault model

Persistent storage exposes individual one-byte writes.

For a write changing byte `x` to byte `y`:

- without crash, the durable result is `y`;
- at the single permitted crash during that write, the durable result is exactly `x` or exactly `y`;
- earlier completed byte writes retain their new values;
- later unissued writes retain their old values.

No multi-byte write is atomic. A crash immediately before a write is equivalent to that write’s old outcome; a crash immediately after it is equivalent to its new outcome. These equivalent schedules are canonicalized rather than duplicated.

The model excludes reordering after reported durable completion, random bit corruption, lost writes reported durable, and a second crash. A real adapter that cannot substantiate this one-byte interface does not realize the seed and must introduce, charge, and fault-test its own markers, checks, or redundancy.

## 8. Two unlike proposed physical realizations

These are experiment obligations, not evidence. No unlike-realization claim survives until two independent builds pass exhaustive comparison.

### 8.1 Realization L: append-only mutation history

Persistent image: five one-byte cells, initially:

```text
ff ff ff ff ff
```

On every successful mutating occurrence, including a semantic no-op, write its one-byte opcode into the first `ff` cell. Valid persisted opcodes are:

```text
00 01 10 11 20 50
```

The position supplies order. Recovery scans the contiguous non-`ff` prefix and replays it through the oracle. A replay-invalid opcode sequence is a test failure; it is not assigned new product behavior.

Properties:

- persistent capacity: 5 bytes;
- write cost: one byte per successful mutator;
- recovery: at most five reads and five replay steps;
- an interrupted write resolves to an absent or present final opcode;
- queries, actions, identities, and rejections write nothing;
- no marker or checksum is needed under the exact one-byte old/new model.

### 8.2 Realization S: overwrite the packed quotient

Persistent image: one rewritable byte, initially:

```text
00
```

For a successful mutation that changes the quotient class, compute the new packed class byte and perform one one-byte write. Emit the success reply only after the write reports durable completion.

For a successful semantic no-op, perform no write: the already durable byte is the promised result.

Recovery reads the byte and requires it to lie in `00..11` hexadecimal.

Properties:

- persistent capacity: 1 byte;
- write cost: zero or one byte per successful mutator;
- recovery: one read and a range check;
- an interrupted write resolves exactly to the old or new class;
- current identity and every other derived output are rebuilt.

### 8.3 Independence and comparison obligation

The two builds must be independently authored from this document. They may share corpus files, but may not share parser, history-fold, persistence, recovery, output-ordering, or action-adapter product code. The comparison harness is a third implementation.

For every client/control skeleton:

1. enumerate every issued one-byte write;
2. inject the sole crash with both old and new outcomes;
3. enumerate every non-duplicate boundary gap;
4. restart without another fault;
5. compare the complete ordered `R` and `D` projection with the reference oracle;
6. compare the sets of public projections reachable from L and S.

Write ordinals need not correspond between L and S. Their reachable public trace sets must correspond.

Until this experiment is executed, “two unlike realizations agree” is explicitly unproven.

## 9. Exhaustive attack program

The finite proposal universe below must be searched, not argued away informally.

### DELETE

Search deletion of:

- each of the eleven input handlers;
- each successful reply form;
- each of the six rejection distinctions;
- the `D` crossing;
- current contract responsibility;
- interpreter absence and identity;
- observation absence and value;
- persistence across restart;
- each persistent byte position in L and the single byte in S;
- any proposed cache, stored explanation, stored identity, latest response, counter, index, checksum, or marker.

Expected outcome:

- deletion of a surviving responsibility or contracted crossing has a listed shortest witness;
- deletion of cached identity, cached interpretation, latest reply, saved explanation, counters, and indices succeeds, so those items remain absent;
- L’s later cells are necessary only for histories long enough to reach them;
- S’s byte is necessary;
- proposed multi-byte markers and checks are unnecessary under this seed’s one-byte realizations and therefore are not included.

### MERGE

Search:

- all `18 choose 2 = 153` full-horizon class merges;
- all `14 choose 2 = 91` cut-class merges;
- all `11 choose 2 = 55` input-handler merges;
- all `6 choose 2 = 15` rejection-code merges;
- merging `D0` with `D1`;
- merging `C`, `R`, `D`, STOP, crash, or restart labels;
- merging `D` and `R` into one atomic action result;
- merging old and new in-flight recovery outcomes.

Every class merge is expected to fail under one of the three discriminator probes. Every rejection merge is expected to lose an exact explanation trace. Channel and action-crossing merges are expected to fail on framing or crash placement.

### DERIVE

For every candidate stored datum, remove it and attempt derivation from the remaining exact persistent bytes and frozen specification.

Expected derivable data include identity bytes, interpreted result, error text/code selection, active probe signatures, class-code names, log length, and response bytes. Derivable data are never promoted to componentwise `MUST`.

### RECOMPUTE

Erase every nonpersistent cache before every request and restart. Recompute from L’s log or S’s class byte. The complete transcript must remain unchanged.

### COLLIDE

Exhaustively compare:

- all eighteen packed bytes;
- all eighteen canonical representative encodings;
- all eighteen probe signatures;
- `D0` and `D1`;
- `ff` against every valid L opcode;
- every reachable old/new crash image.

Any equal encoding for distinguishable classes, stale identity, replay ambiguity, or reachable invalid S byte falsifies the candidate.

### FUTURE

Run breadth-first common-future search to depth three, retaining the shortest witness for every distinguishable pair. Also run a deliberately unrestricted exact-history interpreter model and confirm that its quotient becomes exact-history identity.

### EXTERNALIZE

For every successful action class, inject crash:

- before `D`;
- after `D` and before `R`;
- after `R`;
- after an uncertain outcome followed by a client retry.

Require zero or one attempt for each received occurrence, preserve exact crossing order, and record that receiver semantic effect is unknown. Any automatic replay, hidden status claim, or exactly-once assertion fails.

### REALIZE

Execute both independent builds across every physical fault schedule. Until this completes, unlike-realization evidence is absent.

### COGNITION

Charge the human-facing burden explicitly:

- eleven message forms;
- two authorable tables containing four table cells total;
- one retirement operation;
- one query operation;
- six rejection explanations;
- two contract descriptors;
- four ordinary channel labels plus crash/restart controls;
- the old/new uncertainty rule;
- the action-attempt-versus-effect distinction.

An independent implementer must predict the anchor traces and class table from the frozen document without supplementary rules. Disagreement is a specification failure, not permission to invent behavior.

### TCB

Inventory and independently attack:

- atomic message framing;
- the eleven-message parser;
- rejection precedence;
- history reduction or quotient encoder;
- one-byte durability adapter;
- recovery;
- `C/D/R` ordering;
- current-identity generation;
- the external-attempt adapter;
- the fault harness and comparison oracle.

The external receiver beyond the `D` crossing is not in the TCB because no semantic receiver effect is claimed. Hashing, clocks, transactions spanning external output and storage, background retry, and a durable deduplication service are absent.

## 10. Joint, non-scalar evaluation

No scalar score, weighting, or winner is permitted. Comparison is componentwise.

| Dimension | Realization L | Realization S |
|---|---|---|
| preserved information | successful mutation history, more than quotient | exact quotient class |
| persistent bytes | 5 | 1 |
| writes | 1 per successful mutator | 0 or 1 per successful mutator |
| recovery runtime | up to 5 reads and replay steps | 1 read and range check |
| semantics | reference oracle | reference oracle |
| author/query burden | same public two-table authoring and one-message query | same |
| human cognition | replay and acceptance ordering | packed-class formula and migration |
| operations | append capacity must be respected | overwrite endurance must be respected |
| storage risk | partial final cell is old/new | entire class byte is old/new |
| TCB | scanner, replay, byte adapter | encoder, range check, byte adapter |
| evolution | old opcodes aid diagnosis but freeze replay meaning | new classes require explicit code migration |
| portability | favors append/write-once media | requires safe rewritable-byte interface |
| explainability | successful mutator provenance remains physically inspectable | only current quotient remains |
| loss risk for acknowledged mutation | none under stated model | none under stated model |
| loss risk for unacknowledged mutation | old or new | old or new |
| external action risk | attempt may be absent; retry may duplicate | identical |
| current identity | rebuilt from replayed revision | rebuilt from class revision |
| capacity beyond horizon | unsupported | unsupported |

Neither realization dominates on every dimension: S minimizes bytes and recovery work; L retains provenance and offers different evolution/debugging properties. Action uncertainty is unchanged by either representation.

## 11. Predicted quantities and independent falsification checks

- Client byte-message alphabet: exactly **11**, all nonempty.
- Malformed/rejected framing samples: exactly **2** (`fe`, `30 00`).
- Pre-cut message histories: exactly **133**.
- Pre-cut future-equivalence classes: exactly **14**.
- Class-size multiset: **`{45,15,15,14,14,14,14,2,2,2,2,2,2,2}`**.
- Full-horizon reachable quotient classes: exactly **18**.
- Maximum no-crash distinguishing future for unequal classes: **2 client messages**.
- Revision-0 identity replies over the 133 cut histories: **111**.
- Revision-1 identity replies over the 133 cut histories: **22**.
- Future words of length zero through three: **1,464**.
- Split prehistory/future scripts: **133 × 1,464 = 194,712**.
- Maximum post-cut persistent writes per realization: **3**.
- Maximum public crossing gaps before the sole crash: **10**.
- Conservative schedules per script: **1 + 2·3 + 10 = 17**.
- Conservative exhaustive runs per realization: **3,310,104**.
- Conservative exhaustive runs for both realizations: **6,620,208**.
- Recovered L images before semantic filtering: at most **`1+6+6²+6³+6⁴+6⁵ = 9,331`**.
- Recovered S images: exactly **18**.
- Quiescent adaptive pair-search nodes, including depth and crash-used flag: at most **1,368**.
- L persistent storage: exactly **5 bytes**; recovery reads at most **5**.
- S persistent storage: exactly **1 byte**; recovery reads exactly **1**.
- Successful action without crash: exactly one `D` followed by exactly one `R!84`.
- Successful action interrupted after `D`: exactly one attempt, no success reply, and no recovery retry.
- Successful action interrupted before `D`: no attempt, no success reply, and no recovery retry.
- Second crash or crash during recovery: **unsupported**, never silently generalized.
- Empirical unlike-realization evidence: **absent until two independent builds complete all 6,620,208 bounded runs and all attack checks**.

Any different count, longer supposedly minimal witness, stale identity, stored derived field presented as mandatory, unexplained rejection merge, hidden receiver guarantee, hybrid torn state, automatic action retry, second-crash behavior, or unequal L/S public trace set falsifies this frozen candidate.
