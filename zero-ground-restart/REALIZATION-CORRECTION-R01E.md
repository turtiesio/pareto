# REALIZATION CORRECTION R0.1E — ONTOLOGY-ISOLATED FINITE SEED

## 0. Authority, quarantine, and status

This is a new bounded candidate, not an edit to, projection of, or inheritance
from any earlier ZERO GROUND architecture.  Its builder received only the
history-equivalence method and did not inspect the repository or any earlier
candidate, conclusion, primitive, or proposed solution.  Earlier work remains
an adversarial archive.  It may be replayed against these bytes only after this
file is frozen by an external digest and commit.

The symbols below are opaque bits and positional opcodes.  Names such as
“authorization,” “run,” and “channel” are explanatory aliases for distinctions
forced by future probes; they are not asserted objects, records, fields, or
layers.  The transition relation and observable crossing bytes are the
contract.  A physical representation may have any shape that preserves its
future equivalence classes.

R0.1E is only the smallest finite experiment described here.  It is not the
target contract, a global quotient for unbounded histories, a production
architecture, or a proof about physical durability.  No earlier S, R, P, gate,
subject, LAB, store, parser, provider, or package status is inherited.  No
implementation is authorized by this document.  Only an external,
nonauthorizing enumerator and conformance instrument may be built after freeze.

Present status:

```text
R01E = SPECIFIED FINITE SEED / NOT YET EXECUTED
TARGET-CONTRACT ADEQUACY = UNKNOWN
GLOBAL MINIMALITY = UNKNOWN
PHYSICAL CONFORMANCE = UNKNOWN
AUTHORING / ACTION / PRODUCTION USE = UNSUPPORTED
```

## 1. Exact crossing alphabet

Let `U = {0,1}`.  In the displays below `10` through `22` denote one hexadecimal
octet.  Each metavariable `a`, `r`, `c`, or `x` is one octet, exactly `00` or
`01`.  Every displayed frame is one atomic boundary crossing; concatenation is
left to right.

Inputs are exactly:

```text
10 a r c       B(a,r,c)       8 frames
11 a r c x     A(a,r,c,x)    16 frames
12 a r c       Q(a,r,c)       8 frames
13             E              1 frame
14             X              1 frame
15             R              1 frame
```

There are exactly 35 input frames.  No other input byte string is contract-
permitted.

Outputs are encoded exactly:

```text
20                         OK
21 n x...                  VAL(w)
22 hi lo                   REJ(S)
```

For `VAL`, `n` is one octet in `{00,01,02}` followed by exactly `n` octets,
each `00` or `01`; those octets are the ordered word `w`.  For `REJ`, `hi lo`
is one unsigned big-endian 16-bit mask.  Bits 9 through 15 must be zero.  Bits
0 through 8 mean:

```text
0 off
1 run-missing
2 auth-disagrees
3 channel-missing
4 run-disagrees
5 policy-denies
6 full
7 final-epoch
8 already-up
```

Only masks produced by section 3 are legal.  The candidate predicts an exact
output alphabet of 30 symbols: `OK`, seven `VAL` words, and 22 reachable
rejection masks.  This count is a falsifiable construction claim; it receives
no credit until exhaustive enumeration reproduces it.

The immutable policy fixture is:

```text
P = {(0,0), (0,1), (1,1)}
```

`P` is semantic specification, not mutable hidden state or a service.  A
different table defines a different contract.

## 2. History language and future equivalence

Write `?i` for an input crossing and `!o` for an output crossing.  A history is
every such crossing that has occurred at the declared boundary.  It may end at
any legal prefix, including after an input whose output has not yet crossed.

The legal-history language is the prefix closure of:

```text
H ::= epsilon
    | Hq ?X
    | Hq ?i !o(i,Hq)       for i != X
```

Here `Hq` is any quiescent legal prefix and `o(i,Hq)` is the unique output
required by section 3.  After a non-`X` input and before its required output,
no input, `X`, wrong output, substituted output, or unsolicited output is
legal.  After `X`, the state is again quiescent, so a later legal input may
follow.  Unknown input frames and all other crossing orders are rejected by
the language rather than silently ignored.

For legal histories `h1` and `h2`:

```text
h1 ~=E h2
```

iff every byte-exact suffix legal from both histories has identical required
output crossings, rejection points, and successor behavior.  If a suffix is
legal from only one history, it is itself a distinguishing continuation.  The
conceptual minimum state is the set of equivalence classes under `~=E`.

The finite experiment must compute that quotient by reachability plus fixed-
point partition refinement.  Neither the derived notation below nor its
19-byte serialization is accepted as the quotient merely because it looks
plausible.

## 3. Total reference transition

### 3.1 Derived notation and invariants

The initial quiescent condition is:

```text
u=1, e=0, rho=empty, kappa=empty, omega=empty, pending=none
```

Folding a legal history derives:

```text
rho(r)=a
kappa(c)=r
omega(c) in U words of length at most 2
u in {0,1}
e in {0,1}
pending = none or one exact output symbol
```

The names are notation for a candidate code of observed distinctions.  The
reachable combinations obey:

```text
domain(rho) = image(kappa)
omega(c) is defined iff kappa(c) is defined
if rho(kappa(c))=0, omega(c) may be any word of length 0..2
if rho(kappa(c))=1, omega(c) is one of epsilon, 1, 11
```

For `A` and `Q`, absent and unequal associations map unambiguously:

```text
rho(r) undefined             -> run-missing
rho(r) defined, rho(r) != a  -> auth-disagrees
kappa(c) undefined           -> channel-missing
kappa(c) defined, kappa(c)!=r -> run-disagrees
```

### 3.2 Quiescent input rules

If `u=0`, each of `B`, `A`, `Q`, and `E` produces only
`REJ({off})`; no other predicate is evaluated and nothing mutates.

If `u=1`, `B(a,r,c)` constructs a mask containing:

- `auth-disagrees` exactly when `rho(r)` is defined and unequal to `a`; and
- `run-disagrees` exactly when `kappa(c)` is defined and unequal to `r`.

If the mask is nonempty, `B` rejects without mutation.  Otherwise it assigns
only missing pairs `rho(r):=a` and `kappa(c):=r`, initializes a newly bound
`omega(c):=epsilon`, and returns `OK`.  An already exact binding is idempotent
and still returns `OK`.

If `u=1`, `A(a,r,c,x)` constructs the union of:

- exactly one of `run-missing` or `auth-disagrees`, when applicable;
- exactly one of `channel-missing` or `run-disagrees`, when applicable;
- `policy-denies` exactly when `(a,x)` is not in `P`; and
- `full` exactly when both associations match and `length(omega(c))=2`.

If the union is nonempty, `A` rejects without mutation.  Otherwise it appends
`x` to `omega(c)` and returns `OK`.

If `u=1`, `Q(a,r,c)` applies only the four association predicates.  A
nonempty union rejects.  Otherwise it returns `VAL(omega(c))` without
mutation.

If `u=1`, `E` at `e=0` sets `e:=1`, preserves every relation and word, and
returns `OK`.  At `e=1`, it returns `REJ({final-epoch})` without mutation.

At any quiescent state, `X` sets `u:=0`, preserves `e`, `rho`, `kappa`, and
`omega`, produces no output, and remains quiescent.  Repeated `X` is legal and
has the same effect.

At quiescence, `R` with `u=0` sets `u:=1` and returns `OK`; with `u=1` it
returns `REJ({already-up})` without mutation.

### 3.3 Input/output microsteps

At `pending=none`:

```text
?X:
  durably preserve semantic data, set lifecycle condition u:=0,
  produce no output, remain quiescent

?i for i != X:
  compute post-condition d' and exact output o,
  atomically durably commit d' together with pending:=o
```

At `pending=o`, the only legal continuation is:

```text
!o:
  atomically clear pending and become quiescent
```

The pending output is durable even for a rejection, a query, or an idempotent
success.  Crash during either atomic crossing transition is outside this
contract.  `X` is permitted only as the next crossing from quiescence.  This
restriction is part of R0.1E, not evidence that in-flight crash handling costs
nothing.

## 4. Candidate code and quotient test

Every reachable reference condition has this canonical 19-byte export:

```text
offset  bytes  meaning
0       5a     format marker
1       u      00 or 01
2       e      00 or 01
3       rho(0) 00, 01, or 02=undefined
4       rho(1) 00, 01, or 02=undefined
5       kappa(0) 00, 01, or 02=undefined
6       kappa(1) 00, 01, or 02=undefined
7       length omega(0), 00..02 or 03=undefined
8..9    omega(0), one octet per bit, zero-padded
10      length omega(1), 00..02 or 03=undefined
11..12  omega(1), one octet per bit, zero-padded
13      pending tag: 00=none, 01=OK, 02=VAL, 03=REJ
14      pending VAL length; otherwise 00
15..16  pending VAL bits, zero-padded; otherwise 00 00
17..18  pending REJ mask, unsigned big-endian; otherwise 00 00
```

All unused octets must be zero.  Invalid invariants, noncanonical padding,
unknown tags, impossible words, and impossible masks are rejected.  The marker
is framing, not a candidate future distinction, and may be supplied by the
containing specification rather than persisted per state.

The candidate claim is only:

```text
same 19-byte export => same ~=E class
```

The experiment must additionally determine whether unequal exports ever fall
in one class.  If so, the export is overcomplete and must be reduced.  A class
index assigned after fixed-point refinement is the finite conceptual quotient;
no field layout is implied by that index.

### 4.1 Exhaustive bound

There are exactly 357 predicted quiescent `(rho,kappa,omega)` combinations:

```text
no bound c:                         1
one bound c:        2*2*(7+3)      = 40
two c, one r:       2*(7^2+3^2)    = 116
two c, two r:       2*(7+3)^2      = 200
total                               357
```

Including `u` and `e` predicts exactly `357*2*2 = 1,428` quiescent states.
With no more than 30 pending output symbols, the crossing-machine search has
the hard bound `1,428*(1+30) = 44,268` states.  Both the 1,428 count and the
30-symbol claim must be checked, not assumed.

The external experiment shall:

1. start from the exact initial export;
2. breadth-first enumerate every legal crossing transition;
3. explore all 35 inputs at quiescent states and only the exact output at a
   pending state;
4. reject every unknown frame and illegal ordering;
5. partition-refine the deterministic labeled transition system to a fixed
   point;
6. compare every reachable-state pair through its final class rather than
   conditioning comparisons by a hand-authored family;
7. retain one shortest history per reached state and compute a shortest
   distinguishing suffix for every reported collision;
8. test the canonical export and every DELETE/MERGE projection declared by
   the instrument; and
9. report all inclusion-minimal sound projections within that declared
   projection family, not one greedy endpoint or a claim of byte minimality.

Future answers come only from the transition function.  Handwritten answer
labels are forbidden.  Any reconstruction classified MAY REBUILD must execute
and byte-compare its constructor.  The instrument must require the externally
frozen SHA-256 of this file and fail closed on mismatch.

## 5. Unlike realizations used only as falsification instruments

Two deliberately unlike candidate encodings may be tested after freeze.

### 5.1 Bounded folded log

The logical mutation log contains at most two state-changing `B` entries, four
successful `A` entries, and one successful `E` entry.  A separate fixed cell
holds the exact pending output.  Every non-`X` input atomically appends any
semantic mutation and writes the pending cell.  Rejected, queried, and
idempotent inputs write only the pending cell.  The matching output atomically
clears the cell.  Recovery folds the bounded mutation log and restores the
pending cell.

### 5.2 Canonical snapshot

The snapshot stores the current derived relations, words, epoch, lifecycle
condition, and exact pending output directly.  Each input atomically replaces
the snapshot; each output atomically clears its pending portion.

The lifecycle condition cannot disappear from the total system.  If a test
harness rather than a realization stores `u`, that harness state, its durable
write, and the atomic relation between `u` and the pending cell are part of the
candidate's persistent state, operations, and TCB.  A realization may instead
store `u` in its log or snapshot.  Crediting harness storage as zero would be
EXTERNALIZE, not DELETE.

The conformance instrument drives both encodings through every shortest
reachable history, discards all volatile reconstruction state at each
quiescent `X`, recovers from only the declared durable bytes, and compares
every permitted future transition with the reference quotient.  This tests
two unlike logical/storage encodings.  It does not establish independent
failure domains, torn-write safety, power-loss durability, or physical
interchangeability; those remain UNKNOWN.

## 6. Persistence classification at the seed boundary

These are verdicts about information responsibility.  They do not require a
dedicated field, item, constructor, or storage layer.

### MUST SURVIVE

| responsibility | smallest forcing continuation |
|---|---|
| the two positional associations made by an accepted `B`, including which endpoints are associated | transpose two equal flat endpoint sets; `A` or `Q` for one exact triple accepts in one history and rejects in the other |
| each ordered word and the positional association selecting it | `Q(a,r,c)` returns unequal `VAL` bytes; swapping two words between `c=0` and `c=1` defeats a flat bag |
| the up/down distinction | after `X`, `B` returns `off`; before `X` the same `B` can return `OK` |
| the consumed-evolution distinction | `E` returns `OK` before consumption and `final-epoch` afterward |
| an exact pending output, or lossless information that reconstructs it | the only legal next crossing is its exact `!o`; replacing a rejection mask or query value changes legality and observable bytes |
| the immutable transition specification, policy table, and codec version | changing `P`, a mask bit, or a frame meaning changes a future while retained dynamic bytes can remain equal |

Every row is conditional on the exact seed contract.  The experiment must
minimize the stated transpose or probe; the row is not a proof for any larger
domain.

### MAY REBUILD

- the 19-byte export from a surviving exact mutation log, pending cell,
  lifecycle condition, and this specification;
- a bounded log view from a surviving canonical condition plus a canonical
  representative-history constructor, if the contract never queries the
  original raw history;
- sorted association order, lengths, padding, format marker, reachable-state
  numbers, quotient class numbers, and shortest distinguishing witnesses; and
- rejection or value frame bytes while the exact pending symbol and codec
  specification survive.

The fold, serializer, canonical representative constructor, partition
refiner, and CPU are nonzero runtime and TCB.  If their specification is not
available, their outputs return to MUST SURVIVE or the query is unsupported.

### MAY FORGET

- a rejected input's exact operands after its pending rejection has crossed,
  because this seed has no rejection-history query;
- the count and timing of repeated exact `B`, `X`, and rejected attempts;
- the original order of independent successful bindings when all later
  crossings depend only on the derived associations;
- provisional computation that never crossed and is erased by an atomic
  abort; and
- cache, cursor, process, location, or scheduling details only after the total
  system has restored future-equivalent state.

No failed reset, hidden timing effect, lifecycle bit, incomplete pending
output, or physical delta is licensed by this list.  If a permitted future can
observe one, it becomes MUST SURVIVE or that completion is unsupported.

## 7. Mandatory attacks and where the complexity moved

| attack | seed disposition | complexity now located in |
|---|---|---|
| DELETE / RECOMPUTE | only quotient-irrelevant raw history is deleted; log replay is tested | exact fold, persistent log/cell, recovery CPU |
| MERGE / COLLIDE | only fixed-point-equivalent reachable states may merge | full reachability graph, partition checker, minimized suffix search |
| DERIVE | associations and words derive only from accepted crossings | total transition interpreter and versioned specification |
| FUTURE | all legal suffixes of the closed alphabet participate | exhaustive finite state search; broader futures are unsupported |
| EXTERNALIZE | policy is immutable specification; lifecycle/harness state is charged | harness durability, atomicity, configuration, and TCB |
| REALIZE | folded log and canonical snapshot must match one oracle | two adapters, recovery paths, comparison, fault limits |
| COGNITION | stable masks and shortest distinguishing suffixes explain finite decisions | learning nine bits, positional notation, witness tooling |
| TCB | no compiler/verifier/storage work is credited free | codec, reference fold, serializer, partition checker, durable adapters, harness |

The apparent deletion of raw histories moves complexity into canonical folding
and the frozen interpreter.  The deletion of rejection provenance narrows the
future interface.  The deletion of in-flight recovery moves that entire
capability outside the contract.  The use of two-bit domains makes exhaustive
search possible but moves generality outside the experiment.  None of those
moves is described as a free simplification.

## 8. Simultaneous total-system account

No weighted scalar score is defined.

| dimension | R0.1E seed result and charged cost |
|---|---|
| information/distinction preservation | decidable by exhaustive suffix equivalence inside the closed finite language; everything outside it is unsupported |
| persistent state | conceptual quotient class; candidate 19-byte export or bounded log plus pending/lifecycle responsibility |
| semantic machinery | 35 input frames, total transition function, 30 predicted outputs, policy fixture, codec, legality checker |
| human cognition | small finite tables and nine stable mask bits, but positional aliases and microstep rules remain; comprehension is unmeasured |
| authoring burden | one closed interpreter, two adapters, exhaustive checker, and exact specification/digest maintenance |
| query/navigation burden | `Q` is direct and bounded; aggregation, discovery, free-form query, and search are unsupported |
| runtime | constant-size fold per crossing plus exhaustive offline exploration/refinement; exact measurements not yet taken |
| storage | fixed bounded state; log and snapshot byte totals must be reported by the experiment rather than inferred |
| operations | atomic input commit, atomic output clear, recovery, corruption detection, backup, and harness lifecycle coordination are required |
| trusted computing base | codec, interpreter, persistent adapter, recovery, lifecycle harness, comparator, partition refiner, and host durability assumptions |
| evolution | one observable irreversible `E` bit only; semantic upgrade, rollback, mixed versions, and migration are unsupported |
| portability | two unlike encodings are specified for comparison; physical and power-loss equivalence remain UNKNOWN |
| explainability | exact rejection masks and minimized distinguishing suffixes explain bounded decisions; historical/free-form explanations are unsupported |
| information-loss risk | exhaustive finite collision search can find model-level loss; implementation bugs, corruption, hidden state, and omitted futures remain UNKNOWN |

## 9. Contract forks and explicit unsupported surface

Changing any of these choices changes the future equivalence and may change
the minimum:

- one generic rejection instead of the nine-bit witness mask;
- crash permitted while an input or output is pending;
- an unobservable or repeatable `E` instead of the observable final epoch;
- alpha-renamable tokens instead of literal future frames addressing `0` and
  `1`;
- dynamic authority, revocation, expiry, delegation, or oracle failure instead
  of fixed `P`; and
- unordered observations instead of ordered words.

Unsupported capabilities are: domains larger than two tokens; more than two
observations per channel position; deletion; cancellation; concurrent or
pipelined inputs; mid-transition or pending-output crash; idempotent retry of
`A`; dynamic authorization; aggregation; discovery; general querying;
semantic-changing upgrade; downgrade; mixed-version operation; migration;
replication; timing guarantees; confidentiality; cryptographic identity;
historical rejection queries; free-form explanation; arbitrary authoring or
action; and arbitrary unlike physical realizations.

These are reported as unsupported, not silently assumed.  Prior-archive replay
must determine which omissions conflict with the wider target contract; it may
not reinterpret this finite seed as having supplied them.

## 10. Freeze and next allowed work

After this file receives an external SHA-256 and repository commit, the only
allowed next steps are:

1. build the bounded external reachability/partition instrument;
2. run its deletion, merge, collision, constructor, and two-encoding checks;
3. give a breaker only these frozen bytes and the boundary method;
4. minimize every new collision;
5. replay prior counterexamples as attacks, without importing their proposed
   representations; and
6. publish a post-freeze audit without editing this file.

A passing finite run will establish only the quotient of this exact 35-input
language.  The first target milestone remains a defensible classification for
the wider declared contract, which R0.1E does not yet supply.
