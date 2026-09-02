# CF-1 — finite contract-frontier candidate

## 1. Status and scope

CF-1 is a closed, finite experiment seed. It defines only byte crossings, exact retained state, and permitted future continuations. It does not posit general-purpose objects, facts, events, records, or an open-ended interpreter language.

There are exactly two independent switches:

- `A ∈ {coarse, detailed}`: rejection provenance.
- `B ∈ {atomic, power}`: crash scope.

Thus the only variants are the Cartesian product of those values. Truth-table selection, client choices, timeout scheduling, recovery branches, representations, and physical realizations are enumerated inputs or test subjects, not switches.

Everything outside the finite bounds in Section 14 is unsupported rather than implicitly rejected or generalized.

## 2. Byte notation and framing

All hexadecimal pairs denote one byte. Concatenation is written `||`.

`u16be(n)` is exactly two bytes:

- first byte: `floor(n/256)`;
- second byte: `n mod 256`.

Every crossing carries a message with exact wire encoding

```text
E(P) = u16be(|P|) || P
```

where `P` is the payload. The two-byte length is not part of `P`.

A crossing ends after exactly `2+|P|` bytes. There is no delimiter, NUL terminator, padding, implicit newline, concatenation, partial-stream interpretation, or alternative termination rule.

Client submissions are raw crossing byte strings of length `0..255`, including malformed encodings. Outbound messages may be longer than 255 bytes but must fit the `u16be` envelope.

Offsets in rejection reports are zero-based positions in the complete raw client crossing, including its two-byte envelope. A missing-byte offense uses the position at which the byte was required, which may equal the raw crossing length. Because client crossings are at most 255 bytes, every offset fits one byte.

The bit and nonce alphabets are exactly:

```text
BIT   = {00,01}
NONCE = {00,01}
```

## 3. Exact contract texts

Contract text is ASCII. Every displayed line is followed by byte `0a`, including the last line. No carriage returns, BOM, leading spaces, trailing spaces, or bytes after the final `0a` occur.

### CT1

```text
name=CF-1
version=1
create=10 o q a x i
retire=11
observe=20
query=21
action=30 n
explain=40
interpret=50
update=60 u16be(length) contract-text
identify=70
bit-bytes=00,01
```

Its exact length is 172 bytes, encoded `00 ac`.

### CT2

```text
name=CF-1
version=2
create=10 o q a x i
retire=11
observe=20
query=21
query2=22
action=30 n
explain=40
interpret=50
update=60 u16be(length) contract-text
identify=70
bit-bytes=00,01
```

Its exact length is 182 bytes, encoded `00 b6`.

CT2 differs from CT1 only in the `version` line and the insertion of `query2=22\n` immediately after `query=21\n`.

## 4. Client request grammar and finite corpus

The following are payloads; every submitted well-framed request is their `E(...)` encoding.

| Request | Exact payload |
|---|---|
| CREATE | `10 || o || q || a || x || i`, with all five fields in `BIT` |
| RETIRE | `11` |
| OBSERVE | `20` |
| QUERY | `21` |
| QUERY2 | `22` |
| ACTION | `30 || n`, with `n ∈ NONCE` |
| EXPLAIN | `40` |
| INTERPRET | `50` |
| UPDATE | `60 || u16be(|T|) || T` |
| IDENTIFY | `70` |

A syntactically formed UPDATE may contain any `T` that fits a client crossing, so `0≤|T|≤250`. Only exact CT1 and CT2 have potentially successful semantics.

Let

```text
U = ⋃(k=0..255) Bytes^k
|U| = Σ(k=0..255) 256^k = (256^256 − 1)/255.
```

`U` is the complete client-submission universe for this seed.

Let `P` be the 43 potentially successful raw frames:

- 32 CREATE frames;
- 2 ACTION frames;
- 7 fixed frames: RETIRE, OBSERVE, QUERY, QUERY2, EXPLAIN, INTERPRET, IDENTIFY;
- UPDATE with exact CT1;
- UPDATE with exact CT2.

The exact finite invalid/rejection corpus is

```text
D = U \ P.
```

Some members of `D`, such as well-framed UPDATEs containing other text, pass framing and shape validation before receiving a semantic rejection. Members of `P` may also reject because of lifecycle, version, or nonce state.

No client crossing longer than 255 bytes is in the experiment.

Useful exact encodings include:

```text
CREATE:       00 06 10 o q a x i
RETIRE:       00 01 11
ACTION n:     00 02 30 n
UPDATE CT1:   00 af 60 00 ac || CT1
UPDATE CT2:   00 b9 60 00 b6 || CT2
```

## 5. Observable crossing alphabet

A transcript is an ordered sequence of channel-labelled raw `E(P)` messages.

Channels and directions are:

- `C→S`: client to CF-1 engine;
- `S→C`: engine to client;
- `S→A`: engine to action receiver;
- `A→S`: action receiver to engine;
- `A→W`: receiver’s externally observable action crossing;
- `S→I`: engine to interpreter;
- `I→S`: interpreter to engine;
- `T→S`: timeout source to engine;
- `F→*`: fault supervisor crash crossing;
- `*→F`: completed restart crossing.

Protocol tags containing letters use literal ASCII:

```text
"A0" = 41 30
"A1" = 41 31
"A2" = 41 32
"AE" = 41 45
"I0" = 49 30
"I1" = 49 31
"F0" = 46 30
"F1" = 46 31
```

The one and only timeout-marker encoding is payload `ff`, crossed as `T→S E(ff)`.

Fault and restart crossings are exactly:

```text
F→* E("F0")
*→F E("F1")
```

No timestamps, logs, scheduler messages, physical addresses, write ordinals, or hidden transport retries are observable unless represented by one of these crossings.

## 6. Stable state

The initial stable state is:

```text
version             = 01
lifecycle           = virgin
creation bits       = undefined
used nonces         = {}
saved rejection     = none
receiver nonce 00   = unseen
receiver nonce 01   = unseen
```

Lifecycle is exactly one of:

```text
virgin
live
retired
```

CREATE is the only transition from virgin to live. RETIRE is the only transition from live to retired. There is no transition out of retired.

A successful CREATE stores the five exact bits `o,q,a,x,i`.

At a quiescent point, each nonce is either unused or completed. During an ACTION request it may additionally be pending.

Successful requests never erase or modify saved rejection provenance unless their stated primary state transition independently overlaps no provenance field. Every rejection replaces saved rejection provenance before its immediate rejection response crosses.

## 7. Successful request semantics

All response descriptions below name payloads. The wire crossing is `S→C E(payload)`.

### CREATE

Payload:

```text
10 o q a x i
```

It succeeds only in virgin state.

On success:

1. lifecycle becomes live;
2. the five bits are stored exactly;
3. used nonces becomes empty;
4. response payload is `80`.

Otherwise it rejects with `CREATE_NOT_VIRGIN`.

### RETIRE

Payload `11` succeeds only in live state.

On success lifecycle becomes retired and response payload is `80`.

Otherwise it rejects with `NOT_LIVE`.

### OBSERVE

Payload `20` succeeds only in live state and returns:

```text
90 o
```

Otherwise it rejects with `NOT_LIVE`.

### QUERY

Payload `21` succeeds only in live state and returns:

```text
91 q
```

Otherwise it rejects with `NOT_LIVE`.

### QUERY2

Payload `22` is checked first for active contract version and then for lifecycle:

- under CT1 it rejects with `QUERY2_REQUIRES_V2`;
- under CT2 but nonlive lifecycle it rejects with `NOT_LIVE`;
- under CT2 and live lifecycle it returns `93 x`.

### ACTION

Payload `30 n` is checked first for live lifecycle and then for nonce reuse.

- Nonlive rejects with `NOT_LIVE`.
- A pending or completed nonce rejects with `NONCE_USED`.
- An unused nonce executes the protocol in Section 10 and returns `80` only after exact receiver acknowledgment.

### INTERPRET

Payload `50` succeeds only in live state. It executes Section 9 and returns:

```text
92 result
```

Otherwise it rejects with `NOT_LIVE`.

### UPDATE

Payload:

```text
60 u16be(|T|) T
```

UPDATE is permitted in virgin, live, and retired lifecycle states.

Its closed behavior is:

| Current version | `T=CT1` | `T=CT2` |
|---|---|---|
| CT1 | success `80`, remain CT1 | success `80`, activate CT2 |
| CT2 | reject `CT2_NO_DOWNGRADE` | success `80`, remain CT2 |

Every other `T` rejects with `CONTRACT_TEXT`.

There is no downgrade, alternate CT2 behavior, third version, patch text, normalization, or semantically equivalent text.

### IDENTIFY

Payload `70` always succeeds.

Under CT1 it returns:

```text
94 01 00 ac || CT1
```

Under CT2 it returns:

```text
94 02 00 b6 || CT2
```

The version is one binary byte, not ASCII. The following two bytes are the exact text length. The response terminates at the end of the exact text, whose own final byte is `0a`.

### EXPLAIN

Payload `40` always succeeds and follows Section 8. It does not clear or replace saved provenance.

## 8. Rejection provenance and exact validation

### 8.1 Rule identifiers

| ID | Name |
|---|---|
| `01` | `FRAME_PREFIX` |
| `02` | `FRAME_SHORT` |
| `03` | `FRAME_EXCESS` |
| `04` | `OPCODE_MISSING` |
| `05` | `OPCODE_UNKNOWN` |
| `06` | `ARITY` |
| `07` | `BIT_VALUE` |
| `08` | `NONCE_VALUE` |
| `09` | `UPDATE_HEADER` |
| `0a` | `UPDATE_LENGTH` |
| `0b` | `CONTRACT_TEXT` |
| `20` | `CREATE_NOT_VIRGIN` |
| `21` | `NOT_LIVE` |
| `22` | `QUERY2_REQUIRES_V2` |
| `23` | `NONCE_USED` |
| `24` | `CT2_NO_DOWNGRADE` |

Rule `00` is reserved for EXPLAIN-with-none and is never a rejection rule.

### 8.2 Validation precedence and offsets

Given raw client crossing `R`, validation stops at the first applicable rule below.

1. If `|R|<2`, reject `FRAME_PREFIX`, offset `|R|`.
2. Decode declared payload length `N` from `R[0:2]`. Let actual payload length be `|R|-2`.
   - If actual length is less than `N`, reject `FRAME_SHORT`, offset `|R|`.
   - If actual length is greater than `N`, reject `FRAME_EXCESS`, offset `2+N`.
3. If `N=0`, reject `OPCODE_MISSING`, offset `02`.
4. If payload byte zero is not one of `10,11,20,21,22,30,40,50,60,70`, reject `OPCODE_UNKNOWN`, offset `02`.
5. For fixed-size opcodes other than UPDATE:
   - required payload size is 6 for CREATE;
   - required payload size is 2 for ACTION;
   - required payload size is 1 for all other fixed opcodes.
   A short payload receives `ARITY` at offset `|R|`. A long payload receives `ARITY` at offset `2+required-size`.
6. For CREATE, scan `o,q,a,x,i` left to right. The first byte outside `BIT` receives `BIT_VALUE` at offset `3+j`, where `j` is its zero-based field index.
7. For ACTION, a nonce outside `NONCE` receives `NONCE_VALUE` at offset `03`.
8. For UPDATE:
   - if `N<3`, reject `UPDATE_HEADER`, offset `|R|`;
   - otherwise decode embedded length `L` at raw positions 3 and 4;
   - let actual text length be `N-3`;
   - if actual text is shorter than `L`, reject `UPDATE_LENGTH`, offset `|R|`;
   - if actual text is longer than `L`, reject `UPDATE_LENGTH`, offset `5+L`;
   - if lengths agree but text is neither exact CT1 nor exact CT2, reject `CONTRACT_TEXT` at the text offense defined below.
9. For a syntactically valid QUERY2, check version before lifecycle:
   - CT1 gives `QUERY2_REQUIRES_V2`, offset `02`;
   - otherwise apply the live check.
10. CREATE outside virgin gives `CREATE_NOT_VIRGIN`, offset `02`.
11. RETIRE, OBSERVE, QUERY, ACTION, and INTERPRET outside live give `NOT_LIVE`, offset `02`.
12. A syntactically valid ACTION in live state whose nonce is pending or completed gives `NONCE_USED`, offset `03`.
13. Exact CT1 UPDATE while CT2 is active gives `CT2_NO_DOWNGRADE`, offset `05`.

For unsupported UPDATE text, append a conceptual end marker to the submitted text and to CT1 and CT2. Scan from text position zero while retaining contract texts that matched the entire preceding prefix. The offense is the first position where the submitted next byte or end marker matches no retained candidate’s next byte or end marker. The reported raw offset is `5+position`. The end marker is used only to locate the offset and is never encoded.

### 8.3 Profile A: coarse

An immediate rejection response has payload exactly:

```text
82
```

Saved provenance is exactly one Boolean: none or some. Every rejection sets it to some.

EXPLAIN returns exactly:

```text
95 00    if none
95 01    if some
```

### 8.4 Profile A: detailed

An immediate rejection response has payload exactly:

```text
83 rule offset
```

Saved provenance is exactly:

```text
(rule, offset, u16be(|R|), R)
```

where `R` is the complete raw rejected client crossing, including a malformed or absent envelope.

EXPLAIN returns:

```text
95 00
```

when none exists, and otherwise:

```text
95 rule offset u16be(|R|) R
```

Every rejection replaces the complete saved tuple. This includes malformed CREATE, ACTION, UPDATE, EXPLAIN, and IDENTIFY submissions and state-dependent rejections. A successful EXPLAIN does not replace it.

## 9. Interpreter protocol

All four unary Boolean truth tables are available. A table is encoded by the pair:

```text
t0 t1 ∈ BIT × BIT
```

meaning `f(00)=t0` and `f(01)=t1`.

For every accepted INTERPRET:

1. `S→I E("I0" || i)` crosses.
2. Only after that crossing, the interpreter policy selects one of the four pairs.
3. `I→S E("I1" || t0 || t1)` crosses.
4. The engine computes `result = t0` if `i=00`, otherwise `result=t1`.
5. `S→C E(92 || result)` crosses.

The selected table is independent for each invocation. It may depend on the post-cut transcript already observed by the interpreter policy. No other input, prior-history lookup, code loading, table size, or interpretation result is permitted.

During power recovery, an already-crossed interpreter response remains replayable internally until the client response crosses. It is not crossed a second time. After client completion, the selected table and result have no retained semantic role.

## 10. Action receiver protocol

### 10.1 Exact crossings

An accepted action uses:

```text
Action request:   S→A E("A0" || a || n)
Action crossing:  A→W E("AE" || a || n)
Status probe:     S→A E("A2" || n)
Applied response: A→S E("A1" || n || 00)
Absent response:  A→S E("A1" || n || 01)
```

`A1 n 00` is the exact acknowledgment required before client success.

### 10.2 Normal order

For a previously unused nonce:

1. The engine durably reserves `n` as pending with the current `a`.
2. The receiver acceptance transition crosses the ordered block:
   - `A0 a n`;
   - `AE a n`.
3. The receiver durably records that `n` was applied with `a`.
4. The acknowledgment schedule chooses exactly one of:
   - direct: cross `A1 n 00`;
   - timeout: cross the sole marker `ff`, then the engine crosses `A2 n`, then the receiver crosses `A1 n 00`.
5. The engine durably changes local nonce state from pending to completed.
6. The engine returns client success `80`.

In the timeout schedule, the original acknowledgment is withheld; it does not cross later. There is at most one timeout marker per accepted ACTION.

### 10.3 Recovery of pending action

After restart, a locally pending action always begins with a status probe; it never blindly retransmits `A0`.

- If the receiver answers `A1 n 00`, the engine commits completed state and returns `80`.
- If the receiver answers `A1 n 01`, no accepted `A0` crossing occurred. The engine then crosses `A0 a n` once, the receiver crosses `AE a n` once, and normal acknowledgment scheduling resumes.

A probe response is immediate except that the single permitted crash may occur at its crossing boundary. It does not independently time out.

Across every permitted execution:

- accepted `A0 a n` crosses at most once for each nonce;
- `AE a n` crosses at most once for each nonce;
- probes and acknowledgment crossings may repeat only where the recovery rules explicitly require them;
- client reuse of a pending or completed nonce rejects.

The receiver retains enough durable nonce state for the bounded run to answer recovery probes and suppress a second action crossing.

### 10.4 Feasibility boundary

Exactly-once observable `AE` and single accepted `A0` cannot be guaranteed under the power scope using only sender-local state and an ordinary non-deduplicating receiver. A crash after receiver application but before sender completion makes “not applied” and “applied but unacknowledged” indistinguishable to the sender.

CF-1 therefore includes the receiver’s durable nonce deduplication, atomic acceptance/application state, and status-probe behavior in the total system and TCB. If that receiver obligation is removed, the CF-1 power variant has no conforming realization; it is not weakened to at-least-once or at-most-once behavior.

## 11. Legal microsteps and quiescent cuts

Only one client request may be active. A client policy may submit the next crossing only after the prior request’s client response has crossed.

For every request, the legal order is:

1. client crossing;
2. pure framing and validation;
3. if rejected, durable provenance replacement;
4. any required primary state commitment;
5. any interpreter or action protocol crossings in their specified order;
6. client response crossing;
7. return to quiescence.

Pure validation has no lasting state. The transport retains a crossed client request until its client response crosses, so recovery does not require a second observable client submission.

A quiescent condition holds exactly when:

- no client request is active or retained;
- the most recent client response, if any, has completely crossed;
- no interpreter invocation or response is pending;
- no action is pending;
- no acknowledgment, probe response, or timeout is scheduled;
- no fault or restart transition is active;
- all durable commitments required before the last response are complete.

A cut may occur only in the gap after a completed request and before the next client submission. The initial state is a quiescent cut.

Before the chosen cut there are zero, one, or two completed client submissions and no crash. After the cut there are zero through three sequential client submissions and zero or one crash/restart pair.

## 12. Crash switch B

### 12.1 Atomic scope

A crash may occur only at a quiescent gap:

1. `F→* E("F0")` crosses;
2. the stable state remains exact;
3. restart completes;
4. `*→F E("F1")` crosses.

There is no mid-request crash in this scope.

### 12.2 Power scope

The power scope includes every atomic-scope site and additionally permits a crash:

- immediately before or after any observable crossing;
- during any one-byte persistent write in the engine, transport retention machinery, receiver, or recovery machinery;
- at action acceptance/application and acknowledgment boundaries.

CPU-only work with no persistent or boundary effect is equivalent to an adjacent permitted site and adds no distinct outcome.

A single physical byte write has exactly old-or-new atomicity. No assumption is made about multi-byte atomicity, layout, addresses, sectors, append order, checksums, or recovery implementation.

### 12.3 Reference pre/post semantics

The reference machine represents every durable transition by exact full configurations `Γpre→Γpost`. A configuration includes stable fields, active-request phase, retained channel material, receiver nonce state, and the next legal microstep.

A crash during a durable transition produces exactly the set:

```text
{recover(Γpre), recover(Γpost)}
```

with duplicates collapsed if the configurations are equivalent. No hybrid configuration is permitted.

Recovery from `Γpre` repeats or resumes the transition. Recovery from `Γpost` proceeds with its next microstep. Previously crossed boundary bytes remain in the transcript.

For an ordinary observable crossing `X`, the exact fault outcome set is:

```text
F0,F1, then X and continuation
X, then F0,F1 and continuation from post-X
```

For the receiver acceptance block, pre/post outcomes are atomic at the contract boundary:

- pre: neither `A0` nor `AE` has crossed and receiver status is absent;
- post: both have crossed in order and receiver status is applied.

Thus no allowed recovery has `A0` without the corresponding durable receiver state and `AE`, or `AE` without `A0`.

If a crash leaves local action state pending:

- receiver-pre recovery probes absent before the first and only `A0`;
- receiver-post recovery probes applied and emits no second `A0` or `AE`.

For an interpreter response crossing:

- pre recovery permits the not-yet-selected response to be selected and crossed later;
- post recovery retains the already selected pair internally and does not cross `I1` again.

A client response crossing moves to completed/quiescent state atomically at the boundary: pre recovery crosses it after restart; post recovery does not duplicate it.

### 12.4 Architecture-neutral physical fault comparison

For a fixed client/environment continuation, the reference outcome set is the union of:

- the no-crash trace;
- each permitted crash site;
- each exact pre/post recovery outcome at that site.

A physical realization is run with crashes:

- before its first persistent byte write in an interval;
- after every persistent byte write;
- after the interval’s final write;
- immediately before and after every action, acknowledgment, interpreter, timeout, client, and fault-relevant crossing.

Physical write addresses and write counts are not included in the observable transcript. Multiple physical fault points producing the same boundary transcript collapse to one set member. The resulting exact transcript set must equal the reference set. A subset is insufficient, and an extra hybrid trace is a failure.

This comparison does not require two realizations to share layouts or to map corresponding addresses.

## 13. Future-observable equivalence

A boundary history is a legal completed pre-cut transcript and its resulting quiescent configuration.

For equivalence, the pre-cut transcript is not replayed to a fresh future policy. A future policy begins with an empty post-cut observation and may adapt only to crossings observed after the cut. Otherwise an external policy could distinguish histories merely by remembering which past it was handed, independently of CF-1.

A permitted future policy may choose:

- STOP or one of the finite client crossings in `U`;
- up to three client submissions;
- one of four truth-table responses after each `I0`;
- direct acknowledgment or the exact timeout schedule after an eligible `A0`;
- no crash or one crash at a permitted site;
- its next choice as a deterministic function of the post-cut transcript so far.

A viewer sees channel, direction, complete raw bytes, and total order for every post-cut crossing.

For nondeterministic recovery, behavior is an exact set of complete post-cut transcripts.

Two histories `h` and `h′` merge iff, for every permitted future adaptive policy, viewer, interpreter selection, action schedule, fault directive, contract query, update, retirement, and physical realization satisfying the reference contract, their required post-cut transcript sets are identical.

No state-field equality, storage-layout equality, implementation type, or informal semantic similarity may substitute for that test.

## 14. Exact terminating enumeration

### 14.1 Ordering

Bytes are ordered `00..ff`. Raw client crossings are ordered first by length and then lexicographically. Histories are ordered by completed-frame count and then by raw crossings. Truth tables are ordered:

```text
00 00
00 01
01 00
01 01
```

Direct acknowledgment precedes timeout. No-crash precedes crash sites in microstep order; pre recovery precedes post recovery.

### 14.2 Reference exploration

For each of the four `(A,B)` variants:

1. Enumerate every raw client crossing in `U`.
2. From the initial state, enumerate all legal sequences of zero through two completed submissions, including all interpreter and action choices, with no crash.
3. Retain every resulting quiescent cut history.
4. From each cut, construct a depth-three alternating residual tree:
   - at a client-choice node, branch to STOP and every raw crossing in `U`;
   - execute validation and exact microsteps;
   - at `I0`, branch over all four tables;
   - after an eligible receiver acceptance, branch direct/timeout;
   - when crash remains available, branch at every permitted reference site into no-crash continuation and exact pre/post crash outcomes;
   - after a client response, recurse with depth reduced by one.
5. Record channel-labelled raw transcript bytes on edges.
6. Canonicalize sets by exact byte equality, sort by the ordering above, and hash-cons only after full structural equality.
7. Histories with identical canonical residual roots are one quotient class.
8. For each unequal pair, breadth-first search the paired residual trees for the first separating future.

This explores adaptive policies directly; it need not materialize every policy function.

### 14.3 Hard bounds

Let:

```text
Ucount = (256^256 − 1)/255.
```

Then:

- pre-cut client sequences are bounded by `1+Ucount+Ucount²`;
- post-cut open-loop client sequences are bounded by `1+Ucount+Ucount²+Ucount³`;
- at most five client submissions occur in a complete pre-plus-post run;
- at most five INTERPRET choices occur, giving at most `4^5` truth-table combinations;
- only two nonces exist, so at most two accepted actions occur;
- at most one timeout occurs per accepted action;
- at most one `F0,F1` pair occurs, and only after the cut;
- a reference request has fewer than 32 persistent/crossing fault sites;
- at most `3×32+4=100` post-cut sites exist, including quiescent gaps;
- the crash branch factor is therefore at most `1+2×100=201`;
- a safe open-loop run-count bound is:

```text
(1+Ucount+Ucount²)
× (1+Ucount+Ucount²+Ucount³)
× 4^5
× 201.
```

A safe residual-node recurrence is:

```text
T(0)=1
T(d+1)=1 + Ucount×804×T(d), for d≤2.
```

The bound deliberately overcounts mutually exclusive action and interpreter branches but is finite and computable.

Every eligible concrete realization must be finite-state over the bounded run or provide a computable terminating execution bound. A cycle that produces neither an allowed crossing nor required progress is nonconforming.

## 15. Shortest separating witnesses

Witness minimization uses this key:

```text
(
  max pre-cut frame count,
  sum of the two pre-cut frame counts,
  future client frame count,
  total raw bytes,
  lexicographic encoding
)
```

The enumerator must confirm the first witness for each pair. The following are required seeds and are shortest in completed-frame count. `C(oqaxi)` means CREATE with those five bits; `U1` and `U2` mean UPDATE with exact CT1 and CT2.

| Capability | Pre-cut histories | Shared future | Required separation |
|---|---|---|---|
| CREATE authoring | `[]` vs `[C(00000)]` | `C(00000)` | success `80` vs `CREATE_NOT_VIRGIN` |
| retirement | `[C(00000)]` vs `[C(00000),RETIRE]` | OBSERVE | `90 00` vs rejection |
| observation | `[C(00000)]` vs `[C(10000)]` | OBSERVE | `90 00` vs `90 01` |
| query | `[C(00000)]` vs `[C(01000)]` | QUERY | `91 00` vs `91 01` |
| action value | `[C(00000)]` vs `[C(00100)]` | ACTION `00` | `A0` and `AE` carry different `a` |
| QUERY2 value | `[U2,C(00000)]` vs `[U2,C(00010)]` | QUERY2 | `93 00` vs `93 01` |
| interpretation | `[C(00000)]` vs `[C(00001)]` | INTERPRET with table `00 01` | different `I0` and `92` result |
| nonce use | `[C(00000)]` vs `[C(00000),ACTION 00]` | ACTION `00` | action protocol vs `NONCE_USED` |
| explanation existence | `[]` vs `[raw empty crossing]` | EXPLAIN | `95 00` vs some |
| evolution/identity | `[]` vs `[U2]` | IDENTIFY | exact CT1 vs CT2 response |
| CT2 closure | `[]` vs `[U2]` | `U1` | CT1 self-update success vs CT2 downgrade rejection |
| CT1 QUERY2 | `[C(00000)]` vs `[U2,C(00000)]` | QUERY2 | CT1 rejection vs `93 00` |
| crash/recovery | `[C(00000)]` | ACTION `00`, crash at receiver acceptance | exact pre/post trace set in Section 16 |
| unlike realization | same cut and future on both build families | exhaustive suite | identical reference transcript sets |

These witnesses cover observation, interpretation, authoring, retirement, querying/navigation, action, explanation, evolution, contract identity, crash/recovery, and unlike realization.

## 16. Strict inclusion witnesses for both switches

### 16.1 Rejection profile

Let:

- `h0` be one completed rejection of the empty raw crossing;
- `h1` be one completed rejection of the one-byte raw crossing `00`.

Under coarse provenance, both save only some and a future EXPLAIN returns:

```text
95 01
```

Under detailed provenance:

```text
h0 → 95 01 00 00 00
h1 → 95 01 01 00 01 00
```

The fields are `95,rule,offset,length,raw`.

Therefore detailed future equivalence strictly refines coarse equivalence:

```text
≈detailed ⊊ ≈coarse.
```

### 16.2 Crash scope

Atomic contexts are a strict subset of power contexts because power permits every quiescent crash and also mid-request faults.

Use cut `[C(00000)]`, future ACTION `00`, direct acknowledgment, and crash at receiver acceptance.

The power reference has these two core payload orders.

Receiver-pre recovery:

```text
C→S  30 00
F→*  "F0"
*→F  "F1"
S→A  "A2" 00
A→S  "A1" 00 01
S→A  "A0" 00 00
A→W  "AE" 00 00
A→S  "A1" 00 00
S→C  80
```

Receiver-post recovery:

```text
C→S  30 00
S→A  "A0" 00 00
A→W  "AE" 00 00
F→*  "F0"
*→F  "F1"
S→A  "A2" 00
A→S  "A1" 00 00
S→C  80
```

Every payload above is enveloped with `E`.

A realization that keeps pending action state only in volatile memory can match every atomic continuation but, after the post case, may resend `A0` or duplicate `AE`. The power context separates it.

Thus conformance/equivalence over realizations satisfies:

```text
≈power ⊊ ≈atomic.
```

The reference semantic state quotient at quiescent cuts need not gain a new field; the strict refinement arises from the larger future fault-context set.

## 17. Quotient representations

The following three representations are mandatory comparison candidates for the same computed quotient. None is declared an implementation architecture.

### 17.1 Direct canonical information

At a quiescent state, canonicalize:

```text
(
  active version,
  lifecycle,
  future-relevant creation bits,
  future-relevant used-nonce set,
  profile-specific saved provenance
)
```

Normalization rules are:

- virgin has no creation bits and an empty used set;
- retired discards all creation bits and used-nonce distinctions because no permitted continuation can return to live;
- live retains `o,q,x,i`;
- live retains `a` while at least one nonce is unused;
- live with both nonces completed normalizes `a` away because no future ACTION can expose it;
- coarse provenance is none/some;
- detailed provenance is none or the exact `(rule,offset,length,raw)` tuple.

The enumerator, not this proposed tuple, is authoritative. Any counterexample residual makes the tuple invalid.

### 17.2 Dense class identifier

Enumerate quiescent cut histories, sort their canonical residual structures, and assign consecutive unsigned integers starting at zero. The identifier width is the minimum whole number of bytes capable of representing every class in that variant.

The table mapping ID to complete residual structure is charged storage or rebuild apparatus. A bare dense ID without the exact mapping is not meaningful.

### 17.3 Residual/future behavior structure

Store the canonical depth-three alternating residual DAG itself:

- client-choice branches;
- interpreter and timeout branches;
- fault pre/post set branches;
- exact crossing bytes;
- exact terminal conditions.

Structural equality is full recursive equality. A hash may index the DAG but cannot establish equality without collision resolution against the full structure.

The direct tuple, dense ID, and residual DAG must induce exactly the same partition. Disagreement is a minimized `COLLIDE` witness and rejects the candidate representation; it does not create another switch.

## 18. Probe discipline and preservation verdicts

Classifications are verdicts produced only after the probes below.

- `DELETE`: remove the selected information from every claimed copy and run all residuals.
- `MERGE`: force two proposed representation states to share one encoding and compare residuals.
- `DERIVE`: reconstruct bytes solely as a deterministic function of named surviving bytes.
- `RECOMPUTE`: remove a cache, restart the specified algorithm, and compare transcripts.
- `COLLIDE`: search pairs of non-equivalent histories mapped to one representation and minimize the separating witness.
- `FUTURE`: compare the complete adaptive depth-three residual structures.
- `EXTERNALIZE`: move information to a receiver, interpreter, transport, operator procedure, or verifier and charge that component rather than treating the information as absent.
- `REALIZE`: execute both unlike physical families against the same reference.
- `COGNITION`: remove undocumented human knowledge; any required invention or discretionary repair is a failure and human procedures are charged.
- `TCB`: remove or corrupt each trusted component and record the first separating continuation.

Verdicts mean:

- `MUST SURVIVE`: deleting all copies changes a required future transcript set and exact reconstruction from named surviving information is impossible.
- `MAY REBUILD`: the particular representation may be deleted because an exact terminating derivation from named surviving information restores it before its next required crossing.
- `MAY FORGET`: deletion causes no difference in any permitted residual.
  
For CF-1, exhaustive probes must confirm at least:

| Information at the stated condition | Verdict |
|---|---|
| active CT version | MUST SURVIVE |
| lifecycle | MUST SURVIVE |
| live `o,q,x,i` | MUST SURVIVE |
| live `a` with an unused nonce | MUST SURVIVE |
| live used-nonce distinctions | MUST SURVIVE |
| all creation bits and nonce distinctions after retirement | MAY FORGET |
| live `a` after both nonces complete | MAY FORGET |
| coarse none/some provenance | MUST SURVIVE |
| detailed rule, offset, length, and raw rejection | MUST SURVIVE |
| a local copy of contract text when version and immutable CT mapping survive | MAY REBUILD |
| dense-ID table when the residual enumerator and frozen inputs survive | MAY REBUILD |
| residual DAG cache when the exact enumerator survives | MAY REBUILD |
| active client frame and phase during power recovery | MUST SURVIVE somewhere in the charged total system |
| a local active-frame copy backed by exact retained transport | MAY REBUILD |
| interpreter table/result after client completion | MAY FORGET |
| completed request order older than saved provenance | MAY FORGET |
| receiver dedup state while an ACTION is pending | MUST SURVIVE |
| receiver dedup state after local durable completion and all channels settle | MAY FORGET from the contract quotient, though a realization may retain it |

“Some other copy probably exists” is not a derivation. An externalized copy is part of the total system, TCB, storage charge, and loss analysis.

## 19. Contract identity boundary

IDENTIFY `70` identifies exactly the active CT version and text. It intentionally does not add bytes for switches A or B.

The exact run manifest is therefore separately retained as ASCII:

```text
CF-1|A=coarse|B=atomic\n
CF-1|A=coarse|B=power\n
CF-1|A=detailed|B=atomic\n
CF-1|A=detailed|B=power\n
```

Exactly one line applies to a run. It is configuration, not a third switch and not a client-protocol crossing.

The total experiment identity is:

```text
(exact manifest line, exact latest IDENTIFY response)
```

If the manifest is omitted, IDENTIFY collides across variants that have different rejection or crash behavior. That collision is a required `EXTERNALIZE`/`COLLIDE` finding; the missing identity must not be silently inferred.

## 20. Unlike physical realization experiment

Two complete realizations are required.

### Fixed-address overwrite family

Its persistent engine state uses a bounded set of predetermined addresses and updates reusable locations in place. Shadow copies, generations, and checks are allowed only at predetermined addresses. It may not represent each semantic transition by consuming the next append position.

### Append-only journal/fold family

Its persistent engine state appends transition material to previously unused positions for the bounded run and reconstructs current behavior by an independent fold. It may not update a fixed canonical state tuple in place after each transition.

The families must not share:

- state reducer or fold implementation;
- persistence serializer/deserializer;
- recovery implementation;
- commit protocol;
- generated state-transition tables.

Each total build includes its own engine, decoder, receiver integration, interpreter integration, recovery path, and persistence code. Shared operating-system or device drivers, if any, are explicitly charged as shared TCB. The frozen reference vectors and comparison harness may be shared because they are the oracle, not a realization reducer.

For every variant, both builds are run over:

- every pre-cut history;
- every post-cut adaptive residual;
- all four future truth tables;
- both action acknowledgment schedules;
- every permitted crash site;
- every exact pre/post recovery result;
- every invalid raw crossing in `D`.

Acceptance requires:

```text
fixed transcript set
= append/fold transcript set
= reference transcript set
```

for every indexed case. Agreement between the two builds without agreement with the reference is insufficient.

Neither physical family is endorsed by the three quotient representations. A realization may encode a quotient in any collision-free way consistent with its family constraint.

## 21. Whole-system accounting

Each physical build is reported as one indivisible dossier. Measurements from different builds may not be combined into a synthetic best score.

For each build, report:

- total live bytes at every quiescent cut;
- peak live bytes at every request phase;
- engine persistent bytes;
- engine volatile bytes;
- receiver persistent and volatile bytes;
- interpreter bytes;
- retained client, action, interpreter, timeout, and fault-channel buffers;
- unused but exclusively reserved fixed slots or journal capacity;
- executable code bytes;
- source, generated code, and build metadata bytes;
- CT text, specification, configuration, and manifest bytes;
- decoder/encoder bytes;
- persistence and recovery bytes;
- device and transport driver bytes;
- verification oracle, enumeration tables, traces, and fault-harness bytes;
- operations scripts and documentation bytes;
- human setup, recovery, explanation, evolution, and verification time;
- every manual decision and prerequisite expertise.

Within one build, total live bytes are the sum across all simultaneously resident or exclusively reserved components. There is no scalar score combining bytes, time, risk, or cognition. It is forbidden to combine, for example, the fixed build’s smallest RAM result with the journal build’s smallest recovery burden.

### Required total-system evaluations

| Area | Required evaluation |
|---|---|
| Preservation | DELETE/MERGE/FUTURE verdicts for every quotient field |
| Persistent state | all byte-write crash points and pre/post recovery sets |
| Semantic machinery | independent decoder and transition conformance |
| Cognition | independent execution from frozen artifacts without invented rules |
| Authoring | CREATE, UPDATE CT1/CT2, and RETIRE witnesses |
| Query/navigation | OBSERVE, QUERY, QUERY2, EXPLAIN, IDENTIFY residuals |
| Runtime | exact microstep order, buffer lifetime, timeout, and completion |
| Storage | complete byte ledger, including slack and externalized receiver state |
| Operations | cold restart and deterministic trace reproduction |
| TCB | component-removal and corruption inventory |
| Evolution | CT1 self-update, CT1→CT2, CT2 self-update, rejected downgrade |
| Portability | dependencies and driver assumptions stated and charged |
| Explainability | coarse/detailed outputs and saved-provenance loss probes |
| Loss risk | first separating witness for each deleted or corrupted component |

Portability is established only for the explicitly tested one-byte-atomic persistent interface and supplied channel drivers. Portability to different atomicity, ordering, endianness, transport, hardware, compiler, or operator environment is unsupported until separately realized and exhaustively compared.

Loss probabilities are unsupported unless independently measured. The seed reports consequence witnesses, not invented probabilities.

## 22. Trusted computing base

The TCB includes every component whose failure can change a required transcript set:

- frozen CF-1 specification and exact CT bytes;
- run manifest;
- framing encoder and decoder;
- semantic transition machinery;
- persistence ordering and recovery machinery;
- retained-request and retained-response transport behavior;
- one-byte atomicity assumption;
- action receiver nonce store, status protocol, and action crossing;
- interpreter table selector and response retention;
- timeout source;
- client-response completion boundary;
- fault injector and transcript recorder;
- reference enumerator and equality checker;
- build configuration and drivers;
- any human procedure required to build, restore, inspect, or evolve the system.

Moving functionality into a database, device, receiver, operator, library, generated table, or verification service does not remove it from the TCB or accounting.

## 23. Exact-history interpreter theorem

Let `h` and `h′` be two distinct finite prior boundary histories. Suppose a future-authored interpreter is allowed to read the exact prior history and may implement arbitrary equality tests.

Author an interpreter `J_h` that returns `01` exactly when its prior-history input equals `h`, and `00` otherwise. A future invocation of `J_h` returns different results after `h` and `h′`. Therefore every pair of distinct histories is future-distinguishable, and the quotient is identity:

```text
h ≈ h′  iff  h = h′.
```

Consequently, any summary smaller than exact history is sound only if the contract restricts every future interpreter, update, viewer, policy, and continuation to quotient-respecting observations.

CF-1 obtains a non-identity quotient solely because:

- INTERPRET is restricted to the four unary tables over stored `i`;
- UPDATE accepts only exact CT1 and CT2;
- no continuation can inspect arbitrary prior transcript bytes;
- EXPLAIN exposes only the specified latest rejection profile;
- the future horizon and crash count are bounded exactly.

Allowing arbitrary authored interpreters, additional contract texts, longer histories, another crash, concurrency, new opcodes, receiver behavior outside the stated obligation, or any input outside the finite seed invalidates the smaller quotient unless a new proof is performed.

## 24. Experimental boundary

The finite reference enumeration is the definition of the candidate frontier. Implementations are falsifiers only: a failed realization refutes that realization or exposes an inconsistency; two passing realizations do not establish correctness beyond the enumerated seed.

All generalization beyond the exact byte corpus, two-before/three-after horizon, one restart, two bits, two nonces, two contract texts, four unary truth tables, two provenance profiles, and two crash scopes is unsupported.
