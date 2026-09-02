# R01N — frozen history seed and first collision experiment

Status: independently specified seed; frozen before exposure to any prior archive  
Candidate identifier: `R01N/FT-FE`  
Decision: `UNKNOWN` as a smallest total system; bounded falsification is specified below  
Freeze rule: changing the contract, encoding, or evaluator after running the tests creates a new candidate identifier

## 1. Scope and non-claims

This seed begins with a declared boundary and finite histories. It does not assume a domain ontology. Words such as “frame,” “direction,” and “payload” below name pieces of the boundary alphabet, not universal primitives. Each is retained only because this seed's declared contract exposes a continuation that distinguishes it.

The candidate is a complete proposal for one narrow contract, not a claim that every useful system should expose that contract. In particular:

- It does not claim byte-optimal storage, minimal runtime code, operational durability, pleasant authoring, or universal human comprehensibility.
- It does not equate a passing program with an architecture proof.
- It does not treat a filesystem, database, virtual machine, operating system, durability protocol, boundary adapter, or human convention as free.
- It does not claim that a bounded search establishes unbounded correctness or global minimality.
- It does not silently promise clocks, identities, authentication, authorization, confidentiality, exactly-once external effects, distributed consensus, or recovery from arbitrary corruption.

The purpose of `R01N` is to make one candidate precise enough to break.

## 2. Declared external contract C01

### 2.1 Boundary alphabet and history

A boundary occurrence is a pair `(d, p)` where:

- `d` is exactly one bit. `0` means the occurrence crossed in the declared left-to-right direction; `1` means it crossed right-to-left.
- `p` is a finite, possibly empty, byte string.

A history is a finite ordered sequence of boundary occurrences:

`h = ((d0,p0), (d1,p1), ..., (dn-1,pn-1))`.

Order is crossing order. Simultaneous crossings are outside C01: an adapter must expose an order or reject the input. There is no implicit timestamp, identifier, actor, type, encoding, fact, event identity, or semantic label. If a caller needs one, its bytes must cross the boundary and therefore occur in `p`.

The empty history is permitted. Empty payloads, repeated occurrences, and identical payloads in opposite directions are distinct cases.

### 2.2 Permitted future continuations

C01 permits any finite continuation composed from these requests:

1. `CROSS(d,p)` appends exactly one occurrence.
2. `LENGTH(snapshot)` returns the exact number of occurrences at the named snapshot.
3. `AT(snapshot,i)` returns the exact pair at zero-based index `i`, or the distinguished result `ABSENT`.
4. `SLICE(snapshot,start,count)` returns the exact ordered subsequence in that range.
5. `RUN(snapshot,program,fuel,mode)` runs the frozen evaluator E01 described below. It returns either a deterministic result and trace, `REJECTED`, or `EXHAUSTED`.
6. `COMPARE(snapshot-a,snapshot-b)` returns the first differing occurrence, or reports equality.

Every request and response that actually crosses the declared boundary is itself captured by the boundary adapter as an occurrence. “What actually crossed” is authoritative; an intended or recomputed response is not substituted for an observed crossing.

A snapshot is a logical prefix length, not a persisted identifier. A request referring to prefix length `k` refers to the first `k` occurrences. A missing prefix is `REJECTED`. Thus snapshot names add no independent persistent information.

The raw observations `LENGTH`, `AT`, and `SLICE` are deliberately in the contract. This is a strong audit contract. It means a future is allowed to distinguish any two different histories. A later candidate may weaken this contract, but must receive a new identifier and explicitly state which observations disappear.

### 2.3 Evaluator E01

E01 is semantic machinery and part of the total-system cost. It is not persistent history. Its specification is frozen by C01.

E01 is a deterministic, fuel-bounded stack machine over the value domain:

- arbitrary integers;
- finite byte strings;
- boundary occurrences;
- finite lists of values;
- booleans;
- `ABSENT`.

Programs are finite instruction sequences carried as bytes in a `RUN` request. The normative decoder must reject malformed or non-canonical programs. Each decoded instruction consumes one fuel unit before execution. A backward jump consumes fuel on every visit. Exhausting fuel discards buffered effects and returns `EXHAUSTED` with the executed-prefix trace.

The instruction responsibilities are:

- push a literal integer or byte string;
- obtain history length;
- obtain an occurrence at an index;
- extract direction or payload;
- integer arithmetic and comparison;
- byte concatenation, length, slicing, and equality;
- list construction, indexing, and length;
- conditional and unconditional absolute jumps;
- append a view byte string to a buffered view result;
- append an action byte string to a buffered action result;
- halt with a value;
- reject.

Arithmetic is over unbounded mathematical integers. Byte slicing clamps to the available range. Type mismatch, stack underflow, an invalid jump target, malformed code, or a non-canonical literal returns `REJECTED`; none may depend on host-language accidents. Views and actions are buffered and cross the boundary only after normal halt. The explanation returned on halt contains the program bytes, snapshot prefix length, final value, buffered outputs, and an ordered trace of `(instruction-offset, opcode, stack-depth-before)` tuples. This trace is machine explanation, not a guarantee of human meaning.

This instruction set can express observation, finite interpretation, queries, conditional actions, and renderings; looping plus indexed access permits programs to traverse an arbitrary finite history subject to supplied fuel. Authors evolve behavior by supplying new programs rather than changing the history encoding. Installed programs or policies, if C01 later gives them continuing force, must themselves have crossed the boundary; replay can rediscover them.

The exact numeric opcode table and program binary grammar are intentionally not claimed complete in this seed. Therefore portability and cross-implementation conformance of `RUN` remain `UNKNOWN`, and the total-system candidate cannot pass overall yet. Crediting E01 as zero code would be invalid.

### 2.4 Required observable equality

For C01, histories `h1` and `h2` are equivalent only if every permitted future continuation produces identical required boundary behavior.

For any `h1 != h2`, either their lengths differ or there is a least index `i` at which their occurrences differ. `LENGTH` distinguishes the first case and `AT(i)` distinguishes the second. Therefore:

`h1 ≡C01 h2` if and only if `h1 = h2`.

This is a proof about C01, not about all possible contracts. Under C01, the history quotient is the identity partition. Any valid persistent representation must be injective over valid histories. Compression is allowed; collision is not.

## 3. Candidate persistent representation P01

P01 persists one canonical byte string and no index, count, checksum, cache, semantic projection, materialized view, or installed in-memory state.

### 3.1 Canonical encoding

Let `ULEB(n)` be the shortest unsigned little-endian base-128 encoding of the non-negative integer `n`. Non-shortest encodings are invalid.

Encode one occurrence `(d,p)` as:

`BYTE(d) || ULEB(LENGTH(p)) || p`

where `BYTE(0)` is `00` and `BYTE(1)` is `01`. Encode a history by concatenating its occurrence encodings in order. The empty history encodes as the empty byte string. There is no persisted magic number, outer count, checksum, schema identifier, or version.

The decoder reads one direction byte, one canonical ULEB length, and exactly that many payload bytes, then repeats until end of input. It rejects a direction other than `00` or `01`, truncated data, and non-canonical ULEB.

This encoding is injective: the decoder has exactly one next boundary at every byte position and recovers the original sequence. It is appendable: a new occurrence's encoding is concatenated without rewriting prior bytes.

The absence of a persisted decoder identifier is not free. P01 binds to the externally frozen C01/P01 specification. If a deployment may select among decoders, the decoder selection becomes a contract-visible distinction and must survive somewhere. That broader contract is not claimed here.

### 3.2 Restart behavior

On restart, an implementation scans P01 from byte zero and reconstructs occurrence offsets, count, indexes, cached interpretations, and any policy state deterministically required by replay. Replay must not re-emit historical external actions. Only a newly accepted continuation may emit a new action.

P01 does not specify atomic append, torn-write detection, fsync behavior, media failure, concurrent writers, snapshot isolation, or external-effect coordination. Those are operational responsibilities, not zero complexity. Until a realization specifies them, crash consistency and exactly-once effects are `UNKNOWN` or unsupported.

### 3.3 Unlike physical realizations

Two unlike realizations conform if, for every accepted continuation, they preserve a byte string decoding to the same history and return the same C01 observations. Examples could include an append-only file and transactional rows, or durable flash and printed optical marks. Their physical layouts need not match P01 bytes if their exported decode is identical.

This is a conformance condition, not evidence that such implementations have been built. Each realization must account for its decoder, adapter, durability mechanism, and E01 implementation in its trusted computing base.

## 4. Attack ledger before experiment

The following witnesses are minimal at the level claimed. `I(x)` abbreviates `(0,x)` and `O(x)` abbreviates `(1,x)` only in this table.

| Attack | Proposed simplification | Small collision | Distinguishing continuation | Verdict |
|---|---|---|---|---|
| DELETE | delete the only occurrence | `()` vs `(I(""),)` | `LENGTH` | occurrence responsibility survives |
| DELETE | delete a payload byte | `(I(00),)` vs `(I(""),)` | `AT(0)` | payload content survives |
| MERGE | merge direction values | `(I(""),)` vs `(O(""),)` | `AT(0)` | direction survives |
| MERGE | merge payload byte values | `(I(00),)` vs `(I(01),)` | `AT(0)` | byte value survives |
| DERIVE | persist an outer count | same P01 bytes determine count | deterministic scan | count may rebuild |
| DERIVE | persist offsets or an index | same P01 bytes determine them | deterministic scan | offsets/index may rebuild |
| RECOMPUTE | persist a digest, view, or query cache | P01 plus frozen algorithm determines it | deterministic replay | may rebuild unless its actual crossing is itself history |
| COLLIDE | remove length framing | `(I(""),I(""))` vs `(I(00),)` | `LENGTH`, then `AT` | framing responsibility survives |
| COLLIDE | sort occurrences | `(I(00),O(01))` vs `(O(01),I(00))` | `AT(0)` | order survives |
| COLLIDE | deduplicate | `(I(00),)` vs `(I(00),I(00))` | `LENGTH` | multiplicity survives |
| FUTURE | normalize text today | composed and decomposed UTF-8 spellings | a later byte-exact `AT` | normalization forbidden by C01 |
| EXTERNALIZE | omit the decoder specification | identical bytes can acquire different histories | cross-realization conformance test | spec remains external TCB |
| EXTERNALIZE | omit semantics from state | authors must supply E01 programs | program review and authoring effort | complexity moved to programs/humans |
| REALIZE | change physical storage | file and rows decode differently after a torn append | restart observation | durability protocol must be specified |
| COGNITION | retain only raw bytes | humans must discover structure and meaning repeatedly | author/reviewer task | high cognition burden; not a win |
| TCB | remove indexes from persistence | scanner and cache builder must be correct | rebuild-vs-direct comparison | code moved to runtime TCB |

After the apparent state simplification, complexity is located in the boundary adapter, canonical decoder, durable append mechanism, rebuild scanner, evaluator, supplied programs, effect driver, conformance tests, and human interpretation. P01 claims none of these as zero.

## 5. Persistent-state classification

These verdicts apply only to C01.

### MUST SURVIVE

The information content of the complete finite ordered sequence must survive between executions:

- sequence length and occurrence boundaries;
- order and multiplicity;
- each direction bit;
- each payload length and payload byte value.

This does not require literal P01 bytes if a different injective physical coding is used. It requires enough information to reconstruct exactly the same sequence. Each responsibility has a `LENGTH` or `AT` witness above.

Actual nondeterministic boundary results must survive. Re-running a model, clock, random source, service, or human does not reconstruct what actually crossed.

### MAY REBUILD

Given MUST SURVIVE information and the identified frozen specification, an implementation may deterministically rebuild:

- outer count, offsets, indexes, reverse indexes, and navigation tables;
- hashes, checksums used only for acceleration, caches, and materialized views;
- deterministic query results and E01 traces that have not themselves crossed the boundary;
- replay-derived installed configuration whose defining bytes occur in history;
- encoding blocks in a different conforming physical realization.

Whether rebuilding is tolerable in time, memory, and operations is a separate total-system measurement. “May rebuild” does not mean “costs nothing.”

### MAY FORGET

C01 permits forgetting:

- transient decoder cursor positions after a completed scan;
- temporary E01 stack cells after the request and any required response have crossed;
- cache eviction history;
- host object identities, allocation addresses, scheduler choices, and wall-clock time that never crossed the boundary;
- abandoned author drafts that never crossed the declared boundary.

Changing the contract to expose any of these changes its verdict.

## 6. Simultaneous total-system assessment

No scalar score is assigned.

| Dimension | R01N assessment | Present falsifier or unresolved burden |
|---|---|---|
| distinction preservation | P01 is injective by canonical decoding | malformed decoder or an omitted boundary occurrence |
| persistent state | one self-delimiting history word | not proven shortest; compression alternatives remain |
| semantic machinery | fuel-bounded E01 plus caller programs | opcode grammar incomplete; overall `UNKNOWN` |
| human cognition | raw history is locally simple but semantically opaque | reviewers must reconstruct conventions and program intent |
| authoring burden | arbitrary bytes/programs are possible | safe tooling, names, schemas, linting, and discovery are absent |
| query/navigation | exact scan is possible; indexes rebuild | cold query is linear and index construction is real work |
| runtime | append and scan decoder are small in concept | validation, replay, VM, and effect buffering are not measured |
| storage | P01 has one direction byte and ULEB overhead per occurrence | no compression or compaction proof; raw audit forbids lossy merge |
| operations | single-writer logical append is described | concurrency, torn writes, backup, repair, and migration unresolved |
| trusted computing base | adapter, decoder, store, rebuild, E01, effect driver | no component may be credited as absent |
| evolution | new meanings may arrive as E01 programs | decoder evolution and migration are unsupported in C01 |
| portability | canonical bytes are host-neutral in intent | E01 binary/opcode semantics and conformance suite incomplete |
| explainability | raw `AT` plus deterministic machine trace | human-semantic explanation is not guaranteed |
| information-loss risk | explicit raw retrieval makes loss detectable | corruption detection and recovery are unspecified |

The candidate therefore has a proved local preservation property, severe cognition and operations costs, and an incomplete evaluator specification. It remains `UNKNOWN`, not accepted.

---

## 7. Freeze boundary

Sections 1–6 are the frozen candidate. The experiment and counterexamples below may reject it but may not edit it. Any repair is a new candidate.

---

## 8. First experiment E-R01N-1

### 8.1 Bounded domain

The public corpus contains every history of zero through three occurrences over:

- directions `{0,1}`;
- payloads `{empty, 00, 01, 0001}`.

There are eight possible occurrences and `1 + 8 + 8^2 + 8^3 = 585` histories.

The bounded future suite includes length, exact indexed observation, last occurrence, direction count, payload concatenation, a viewer, an interpretation, a conditional action, an explanation-like render, pattern tests, and one-occurrence append continuations followed by observations. Exact indexed observation makes every different corpus history contract-distinguishable; the other futures exercise non-audit behavior and catch implementation mistakes.

### 8.2 Representations attacked

The experiment evaluates P01 and these simplifications in the same run:

- erase direction;
- erase payload;
- erase length framing;
- sort order;
- deduplicate;
- keep only counts, the last occurrence, or a two-occurrence tail;
- drop first or last occurrence;
- merge payload byte values;
- replace the representation with an eight-bit digest;
- erase an occurrence, direction, or payload at every position in the bounded domain.

It also starts with an instrumented redundant bundle `(P01, count, last, incoming-count)`, deletes any component with no surviving witness, and repeats to a fixed point. The expected fixed point is P01 alone. This greedy deletion is not a proof that no radically different injective coding exists.

For each attacked representation, histories are grouped by representation value. Within every colliding group the program chooses a minimum pair by total occurrence count, total payload bytes, and lexical order. It then selects the lowest-cost future that distinguishes the pair. Thus every reported collision class has a deterministic minimized witness.

### 8.3 Executable falsification code

Run with Python 3.11 or later. It uses only the standard library. A nonzero exit or failed assertion rejects the expected bounded result.

```python
# BEGIN E-R01N-1
from collections import defaultdict
from hashlib import sha256
from itertools import product
import unicodedata

DIRS = (0, 1)
PAYLOADS = (b"", b"\x00", b"\x01", b"\x00\x01")
EVENTS = tuple((d, p) for d in DIRS for p in PAYLOADS)
MAX_HISTORY = 3


def enumerate_histories(events, maximum):
    result = []
    for n in range(maximum + 1):
        result.extend(tuple(xs) for xs in product(events, repeat=n))
    return tuple(result)


HISTORIES = enumerate_histories(EVENTS, MAX_HISTORY)


def uleb(n):
    assert isinstance(n, int) and n >= 0
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def read_uleb(data, offset):
    start = offset
    value = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ValueError("truncated ULEB")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            if data[start:offset] != uleb(value):
                raise ValueError("non-canonical ULEB")
            return value, offset
        shift += 7


def encode_frame(event):
    direction, payload = event
    assert direction in DIRS and isinstance(payload, bytes)
    return bytes((direction,)) + uleb(len(payload)) + payload


def encode_full(history):
    return b"".join(encode_frame(event) for event in history)


def encode_full_alternate(history):
    # Deliberately different construction path for a small conformance check.
    out = bytearray()
    for direction, payload in history:
        out.append(direction)
        out.extend(uleb(len(payload)))
        out.extend(payload)
    return bytes(out)


def decode_full(data):
    offset = 0
    result = []
    while offset < len(data):
        direction = data[offset]
        offset += 1
        if direction not in DIRS:
            raise ValueError("invalid direction")
        length, offset = read_uleb(data, offset)
        end = offset + length
        if end > len(data):
            raise ValueError("truncated payload")
        result.append((direction, data[offset:end]))
        offset = end
    return tuple(result)


ABSENT = ("ABSENT",)


def at(history, index):
    return history[index] if 0 <= index < len(history) else ABSENT


def render(history):
    return "|".join(f"{d}:{p.hex()}" for d, p in history)


def make_futures(events, maximum):
    # Each entry is (syntactic-cost, stable-name, observation-function).
    futures = [
        (1, "LENGTH", lambda h: len(h)),
        (2, "LAST", lambda h: at(h, len(h) - 1)),
        (3, "COUNT_DIRECTION_0", lambda h: sum(d == 0 for d, _ in h)),
        (3, "CONCAT_PAYLOADS", lambda h: b"".join(p for _, p in h)),
        (4, "VIEW_HEX", render),
        (4, "INTERPRET_U8_SUM", lambda h: sum(sum(p) for _, p in h)),
        (
            4,
            "ACTION_IF_LAST_IS_0:00",
            lambda h: b"ACT" if at(h, len(h) - 1) == (0, b"\x00") else b"NOACT",
        ),
        (
            5,
            "EXPLAIN_DIRECTIONS",
            lambda h: tuple((i, d) for i, (d, _) in enumerate(h)),
        ),
        (5, "HAS_0:0001", lambda h: (0, b"\x00\x01") in h),
        (5, "HAS_ADJACENT_REPEAT", lambda h: any(a == b for a, b in zip(h, h[1:]))),
    ]
    for index in range(maximum):
        futures.append((1 + index, f"AT({index})", lambda h, i=index: at(h, i)))
    for event_number, event in enumerate(events[:4]):
        event_name = f"{event[0]}:{event[1].hex()}"
        futures.append(
            (
                5 + event_number,
                f"APPEND({event_name});LENGTH",
                lambda h, e=event: len(h + (e,)),
            )
        )
        for index in range(maximum + 1):
            futures.append(
                (
                    6 + event_number + index,
                    f"APPEND({event_name});AT({index})",
                    lambda h, e=event, i=index: at(h + (e,), i),
                )
            )
    return tuple(sorted(futures, key=lambda item: (item[0], item[1])))


FUTURES = make_futures(EVENTS, MAX_HISTORY)


def signature(history, futures=FUTURES):
    return tuple(fn(history) for _, _, fn in futures)


def history_rank(history):
    return (
        len(history),
        sum(len(payload) for _, payload in history),
        tuple((direction, payload) for direction, payload in history),
    )


def pair_rank(a, b):
    a, b = sorted((a, b), key=history_rank)
    return (
        len(a) + len(b),
        sum(len(payload) for h in (a, b) for _, payload in h),
        history_rank(a),
        history_rank(b),
    )


def first_witness(a, b, futures=FUTURES):
    for cost, name, fn in futures:
        left, right = fn(a), fn(b)
        if left != right:
            return cost, name, left, right
    return None


def minimized_collisions(encoder, histories=HISTORIES, futures=FUTURES):
    groups = defaultdict(list)
    signatures = {history: signature(history, futures) for history in histories}
    for history in histories:
        groups[encoder(history)].append(history)

    minimized = []
    for representation, bucket in groups.items():
        if len(bucket) < 2:
            continue
        best = None
        for i, left in enumerate(bucket):
            for right in bucket[i + 1 :]:
                if signatures[left] == signatures[right]:
                    continue
                candidate = (pair_rank(left, right), left, right)
                if best is None or candidate[0] < best[0]:
                    best = candidate
        if best is not None:
            _, left, right = best
            minimized.append(
                (pair_rank(left, right), representation, left, right,
                 first_witness(left, right, futures))
            )
    minimized.sort(key=lambda item: item[0])
    return minimized


def show(history):
    return "(" + ",".join(f"{d}:{p.hex()}" for d, p in history) + ")"


def report(name, encoder, histories=HISTORIES, futures=FUTURES):
    collisions = minimized_collisions(encoder, histories, futures)
    if not collisions:
        print(f"PASS {name}: no distinguishable collision")
        return collisions
    _, representation, left, right, witness = collisions[0]
    _, future_name, left_result, right_result = witness
    print(
        f"FAIL {name}: classes={len(collisions)}; "
        f"min={show(left)} <> {show(right)}; "
        f"repr={representation!r}; witness={future_name}; "
        f"results={left_result!r} <> {right_result!r}"
    )
    return collisions


def no_direction(history):
    return b"".join(uleb(len(p)) + p for _, p in history)


def no_payload(history):
    return bytes(direction for direction, _ in history)


def no_framing(history):
    return b"".join(bytes((direction,)) + payload for direction, payload in history)


def sorted_order(history):
    return b"".join(sorted(encode_frame(event) for event in history))


def deduplicated(history):
    return b"".join(sorted(set(encode_frame(event) for event in history)))


def counts_only(history):
    return (len(history), sum(direction == 0 for direction, _ in history))


def last_only(history):
    return at(history, len(history) - 1)


def tail_two(history):
    return encode_full(history[-2:])


def drop_first(history):
    return encode_full(history[1:])


def drop_last(history):
    return encode_full(history[:-1])


def merge_payload_01_into_00(history):
    changed = tuple((d, p.replace(b"\x01", b"\x00")) for d, p in history)
    return encode_full(changed)


def tiny_digest(history):
    return sha256(encode_full(history)).digest()[:1]


MUTANTS = (
    ("DELETE_DIRECTION", no_direction),
    ("DELETE_PAYLOAD", no_payload),
    ("DELETE_FRAMING", no_framing),
    ("MERGE_ORDER_BY_SORT", sorted_order),
    ("MERGE_MULTIPLICITY_BY_DEDUP", deduplicated),
    ("KEEP_COUNTS_ONLY", counts_only),
    ("KEEP_LAST_ONLY", last_only),
    ("KEEP_TAIL_TWO", tail_two),
    ("DELETE_FIRST", drop_first),
    ("DELETE_LAST", drop_last),
    ("MERGE_PAYLOAD_01_INTO_00", merge_payload_01_into_00),
    ("REPLACE_WITH_DIGEST8", tiny_digest),
)


def erase_event_at(index):
    def encoder(history):
        if index >= len(history):
            return encode_full(history)
        return encode_full(history[:index] + history[index + 1 :])
    return encoder


def erase_direction_at(index):
    def encoder(history):
        if index >= len(history):
            return encode_full(history)
        changed = list(history)
        changed[index] = (0, changed[index][1])
        return encode_full(tuple(changed))
    return encoder


def erase_payload_at(index):
    def encoder(history):
        if index >= len(history):
            return encode_full(history)
        changed = list(history)
        changed[index] = (changed[index][0], b"")
        return encode_full(tuple(changed))
    return encoder


def redundant_bundle(active):
    def encoder(history):
        values = []
        for component in active:
            if component == "transcript":
                values.append(encode_full(history))
            elif component == "count":
                values.append(len(history))
            elif component == "last":
                values.append(at(history, len(history) - 1))
            elif component == "direction_0_count":
                values.append(sum(d == 0 for d, _ in history))
            else:
                raise AssertionError(component)
        return tuple(values)
    return encoder


def deletion_fixed_point():
    active = ["transcript", "count", "last", "direction_0_count"]
    deletion_order = ("count", "last", "direction_0_count", "transcript")
    while True:
        deleted = False
        for component in deletion_order:
            if component not in active:
                continue
            trial = [x for x in active if x != component]
            if not minimized_collisions(redundant_bundle(trial)):
                active = trial
                print(f"DELETE bundle component without witness: {component}")
                deleted = True
                break
        if not deleted:
            return tuple(active)


assert len(EVENTS) == 8
assert len(HISTORIES) == 585
assert len({signature(history) for history in HISTORIES}) == len(HISTORIES)
for history in HISTORIES:
    assert decode_full(encode_full(history)) == history
    assert encode_full_alternate(history) == encode_full(history)

print(f"public corpus: histories={len(HISTORIES)} futures={len(FUTURES)}")
assert not report("R01N_P01", encode_full)

for mutant_name, mutant in MUTANTS:
    assert report(mutant_name, mutant), f"mutant unexpectedly survived: {mutant_name}"

for position in range(MAX_HISTORY):
    assert report(f"DELETE_EVENT_AT_{position}", erase_event_at(position))
    assert report(f"DELETE_DIRECTION_AT_{position}", erase_direction_at(position))
    assert report(f"DELETE_PAYLOAD_AT_{position}", erase_payload_at(position))

fixed_point = deletion_fixed_point()
print(f"bundle deletion fixed point: {fixed_point}")
assert fixed_point == ("transcript",)


# Fresh domain sealed from the public payload set above.
FRESH_PAYLOADS = (
    b"\xff",
    b"\x00\x00",
    b"\x01\x00",
    "é".encode("utf-8"),
    "e\u0301".encode("utf-8"),
    bytes(range(128)),
)
FRESH_EVENTS = tuple((d, p) for d in DIRS for p in FRESH_PAYLOADS)
FRESH_HISTORIES = enumerate_histories(FRESH_EVENTS, 2)
FRESH_FUTURES = make_futures(FRESH_EVENTS, 2)


def normalize_utf8_nfc(history):
    changed = []
    for direction, payload in history:
        try:
            payload = unicodedata.normalize("NFC", payload.decode("utf-8")).encode("utf-8")
        except UnicodeError:
            pass
        changed.append((direction, payload))
    return encode_full(tuple(changed))


for history in FRESH_HISTORIES:
    assert decode_full(encode_full(history)) == history
    assert encode_full_alternate(history) == encode_full(history)

print(
    f"fresh corpus: histories={len(FRESH_HISTORIES)} "
    f"futures={len(FRESH_FUTURES)}"
)
assert not report("R01N_P01_FRESH", encode_full, FRESH_HISTORIES, FRESH_FUTURES)
assert report(
    "FRESH_UTF8_NFC_NORMALIZATION",
    normalize_utf8_nfc,
    FRESH_HISTORIES,
    FRESH_FUTURES,
)


# Decoder rejection tests are observations of the identified specification.
for invalid in (b"\x02\x00", b"\x00", b"\x00\x80\x00", b"\x00\x02\xff"):
    try:
        decode_full(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"accepted malformed representation: {invalid!r}")

print("E-R01N-1 bounded result: PASS for P01; all listed mutants falsified")
# END E-R01N-1
```

### 8.4 Acceptance and rejection conditions

The bounded P01 result passes only if:

1. every public and fresh history round-trips through both encoder construction paths;
2. no two future-distinguishable histories collide under P01;
3. every listed simplification produces at least one minimized witness;
4. all position-level deletions produce a witness;
5. redundant persisted bundle components are deleted until only P01 remains;
6. the fresh byte domain passes unchanged;
7. the previously hidden Unicode-normalization attack collides and is caught;
8. malformed/non-canonical inputs are rejected.

Failure of an assertion rejects P01 or the experiment. Success establishes only the enumerated result.

## 9. Hidden and fresh attacks after freeze

The fresh corpus was selected after the P01 specification freeze. It attacks assumptions that small public bytes are text, that equivalent-looking Unicode may merge, that NUL is a terminator, that payload length is tiny, and that all bytes are valid UTF-8. P01 predicts exact preservation in each case. NFC normalization predicts a collision between composed and decomposed spellings, which `AT` distinguishes.

Additional attacks not resolved by this bounded program are mandatory before acceptance:

- payloads whose ULEB length crosses 127/128 and larger boundaries;
- histories large enough to expose counter overflow, memory exhaustion, and rebuild time;
- concurrent crossings and the adapter's ordering rule;
- a crash at every byte of append, flush, index rebuild, and response emission;
- malicious ULEB and program encodings with resource limits;
- corruption, backup, restore, and replica divergence;
- two independently written decoders and, after E01 completion, two evaluators;
- semantic authoring and review tasks with humans unfamiliar with prior conventions;
- policy evolution that needs information never allowed to cross the original boundary;
- an external service whose response changes between replay and actuality;
- a physical realization that cannot provide atomic variable-length append;
- previously archived counterexamples, replayed by a breaker without importing archived solutions.

The prior adversarial archive is intentionally not consulted in this seed. Archive replay begins only after this freeze and contributes attacks, not ontology.

## 10. Current conclusion

For the exact raw-audit contract C01, every difference in finite boundary history is future-observable, so the conceptual quotient contains one class per distinct history. P01 is an injective, self-delimiting candidate representation of those classes. The first experiment can falsify common deletion, merge, framing, ordering, multiplicity, digest, and normalization shortcuts over a small corpus.

This does not establish the smallest total system. P01 may lose on compression, cognition, authoring, query cost, runtime, operations, and TCB even while preserving distinctions. E01's binary grammar is incomplete, durability is unspecified, and no unlike physical realizations have passed conformance. The correct overall verdict is therefore:

`UNKNOWN — persistence distinction claim locally defensible; total-system minimality and operational realization unproved.`

The first milestone statement is:

- MUST SURVIVE: enough information to reconstruct exact ordered boundary occurrences, forced by `LENGTH` and `AT`.
- MAY REBUILD: every deterministic projection named in Section 5, with its specification and runtime counted.
- MAY FORGET: only behavior excluded by C01 and transient machinery with no permitted future witness.
- FORCING DISTINCTION: for unequal histories, the least unequal index or unequal length is the explicit smallest observable witness.
