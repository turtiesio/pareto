# FEASIBILITY AUDIT R0.1E — EXHAUSTIVE FINITE QUOTIENT AND CONTRACT BOUNDARY

## 0. Frozen authorities, chronology, and verdict

This audit leaves the candidate immutable.

| artifact | commit | SHA-256 |
|---|---|---|
| `REALIZATION-CORRECTION-R01E.md` | `32059a0d014a69eca88ba014c1ad24632690ae22` | `a4c081623ccf9419ff19f3f842fff47e8631504940ee0c44038809198a15d2bf` |
| `r01e_quotient_experiment.py` | `0de9ea8df6dd6bf61d44d23dede6adff5cb7f6b1` | `68ad4142686a795ec514472984f89b480b2cc99f381766a4ba28f0ac2db033e2` |

The deterministic 52,315-byte JSON stream emitted by the instrument has
SHA-256:

```text
153e526f18b83b3daf40cafde56295afe23bafe2cc0baf7d792903c3bc3a09d4
```

The reproducible invocation is:

```text
python3 zero-ground-restart/r01e_quotient_experiment.py
```

The instrument fails closed unless the candidate has the exact frozen digest.
Its source is a nonauthorizing falsification instrument, not semantic authority
and not the architecture.

The quarantine order was:

1. an isolated builder received the boundary-history method but no repository
   or earlier ZERO GROUND material;
2. the resulting candidate was written and committed;
3. a breaker read only those frozen bytes and performed a read-only audit;
4. a separate implementer read only those frozen bytes and constructed the
   finite experiment; and
5. only after the file-only break did the breaker read the R0.1D audit and toy
   corpus as attacks.

No old proposed solution was an input to the seed.  The later archive replay
does not turn any old abstraction into an inherited primitive.

Verdict:

```text
R01E CLOSED TRANSITION LANGUAGE = TOTAL
R01E REACHABLE FINITE QUOTIENT = 10,019 CLASSES
R01E REACHABLE CANONICAL EXPORT = SOUND AND ONE-TO-ONE
R01E 30-OUTPUT / 22-REJECTION CLAIM = FALSIFIED
R01E CANONICAL IMPORT LANGUAGE = UNDERSPECIFIED
R01E SHORTEST-HISTORY REALIZATION CLAIM = INSUFFICIENT FOR HIDDEN STATE
R01E TARGET-CONTRACT ADEQUACY = FAIL / EXPLICITLY UNSUPPORTED
FIRST TARGET MILESTONE = NOT YET MET
```

The finite seed is a useful method result: its complete searched quotient is
known.  It is not the smallest total system required by the user's wider
contract because it obtains finiteness by excluding most required observation,
interpretation, authoring, querying, action, explanation, evolution, and
unlike-physical behavior.

## 1. Exhaustive experiment result

### 1.1 Reachability and future equivalence

The instrument builds the exact partial labeled transition system from the
35 input frames and every reachable exact output frame.  It retains one
shortest crossing history for each reached state, explores every legal outgoing
crossing, and refines all states together to a fixed point.  It does not use
conditioned families or handwritten future answers.

| measurement | result |
|---|---:|
| input frames | 35 |
| `(rho,kappa,omega)` quiescent combinations | 357 |
| quiescent states after `u` and `e` | 1,428 |
| distinct pending-output states | 8,591 |
| total reachable crossing states | 10,019 |
| legal crossing transitions | 58,571 |
| refinement rounds, including stable check | 6 |
| final future-equivalence classes | 10,019 |
| unique reachable 19-byte exports | 10,019 |
| same-export / unequal-class collisions | 0 |
| unequal-export / same-class pairs | 0 |

Every reachable state is distinguished by some legal future suffix.  Therefore
the candidate export is a lossless code of the finite quotient on reachable
states.  This does not make its 19-byte layout a minimum code: a dense
fixed-width index over 10,019 classes needs 14 bits, and the experiment finds
several exact reconstruction reductions below.  Index assignment, lookup, and
the transition table would themselves add semantic machinery and TCB, so the
14-bit observation is not a total-system score.

The frozen `44,268` state ceiling remains a valid loose upper bound.  The
actual state count is smaller because most output symbols are not pending from
most quiescent states.

### 1.2 The output-count claim fails

The rules reach exactly 28 output symbols:

```text
1 OK + 7 VAL + 20 REJ = 28
```

The reachable rejection masks are:

```text
0001 0004 0008 000a 000c 0010 0012 0014
0020 0024 0028 002a 002c 0030 0032 0034
0040 0060 0080 0100
```

They are not the claimed 22 masks.  In particular, `run-missing` implies
`rho(r)` is undefined.  Because `domain(rho)=image(kappa)`, `kappa(c)=r` is
then impossible: the channel is either absent or names the other run.  Thus
the lone `run-missing` mask `0002` and `run-missing|policy-denies` mask `0022`
cannot occur.

This falsifies a stated construction count and the corresponding semantic-
machinery row.  It does not make the transition function partial because
sections 1 and 3 make generated masks authoritative and label the count a
falsifiable prediction.

### 1.3 Corpus character

The experiment's history corpus is the reproducible set of 10,019 shortest
legal prefixes plus all 58,571 outgoing transitions.  Histories compose
binding, append, query, epoch, lifecycle, rejection, pending output, and
recovery behavior.  They are not empty/singleton labels.

Partition refinement covers arbitrary legal suffix length in the finite
reference machine; it is stronger than comparing only the stored one-step
answers.  The retained shortest prefixes are MAY REBUILD from the parent tree
and do not need to be separately persisted.  Section 4 explains why one
shortest path per reference state is nevertheless insufficient to establish
an implementation with hidden state.

## 2. DELETE, MERGE, DERIVE, and COLLIDE results

### 2.1 Whole-component deletion family

The declared family partitions the export, after deleting its constant marker,
into 11 groups:

```text
lifecycle_u, epoch_e, rho_0, rho_1, kappa_0, kappa_1,
omega_0, omega_1, pending_tag, pending_val, pending_rej
```

All `2^11 = 2,048` retained-group projections were tested.  Exactly three are
sound: the full set, the full set without `kappa_0`, and the full set without
`kappa_1`.  The last two are the inclusion-minimal sound projections in this
declared family.  They do not establish a unique bit- or byte-minimum.

Either one `kappa` coordinate can rebuild, but both cannot.  The total
constructor was executed against both omissions and reproduced all 10,019
original exports per coordinate, 20,038 byte-equality checks in total:

```text
omega(c) undefined -> kappa(c) undefined

omega(c) defined and domain(rho) has one endpoint
  -> kappa(c) is that endpoint

domain(rho) has two endpoints
  -> both channels are defined and bijective;
     omitted kappa(c) is the complement of retained kappa(1-c)
```

Deleting both coordinates collides.  One minimized transpose is:

```text
h0: B(0,0,0)!OK ; B(0,1,1)!OK
h1: B(0,1,0)!OK ; B(0,0,1)!OK
future: Q(0,0,0)
```

The future returns `VAL(epsilon)` in one history and
`REJ(run-disagrees)` in the other.  Equal endpoint bags are not enough;
association survives without implying two dedicated fields.

### 2.2 Pending-rejection bit deletion

A second declared family exhaustively tests all `2^9 = 512` subsets of mask
bits, zeroing only the selected bits in pending `REJ` states while retaining
every other canonical byte.  Six subsets are sound.  The two maximal sound
deleted sets are exactly:

```text
{off, final-epoch}
{off, already-up}
```

The constructors use retained state:

```text
pending REJ and u=0 -> restore off
deleted final-epoch and u=1 and e=1 and retained mask=0
  -> restore final-epoch
deleted already-up and u=1 and retained mask=0
  -> restore already-up
```

All six sound deletion sets were reconstructed and byte-compared for all
6,637 reachable pending-rejection states, 39,822 executed checks.  Deleting
both `final-epoch` and `already-up` fails:

```text
hF: ?E !OK ?E
hR: ?E !OK ?R
```

Both have `u=1`, `e=1`, and a pending rejection after deletion, but the only
legal next outputs are respectively `REJ(0080)` and `REJ(0100)`.

Thus “exact pending output” means its future class or a lossless code, not
every redundant mask bit.

### 2.3 Merge attacks

All eight declared lossy merges collide:

```text
rho endpoint bag
kappa endpoint bag
omega channel bag
omega bit bag
pending kind only
generic rejection
VAL length only
lifecycle/epoch OR
```

Representative minimized witnesses include:

- appending `0,1` versus `1,0` to one bound position, followed by `Q`, defeats
  unordered word storage;
- appending one value to position zero versus position one, followed by a
  query of position zero, defeats a word bag;
- pending `REJ(000a)` versus `REJ(002a)` requires unequal immediate output
  bytes and defeats a generic rejection; and
- `epsilon` versus `?X`, followed by `B(0,0,0)`, defeats deletion of lifecycle
  state.

The deterministic report contains 37 shortest collision witnesses and a
shortest distinguishing suffix for each declared projection boundary and
merge attack.  Passing the candidate export means only that no invalid
collision exists in this exact finite quotient.

## 3. Corrected persistence verdict for the finite language

These are responsibility verdicts, not primitive or field declarations.

### MUST SURVIVE

| dynamic responsibility | forcing future |
|---|---|
| the lossless topology and values of accepted positional associations | the two-binding transpose followed by exact `B`, `A`, or `Q` distinguishes it |
| each word's content, order, and selecting position | `Q` returns unequal exact `VAL` bytes for swapped positions or `01` versus `10` |
| the up/down distinction | `epsilon` versus `?X`, then `B`, requires `OK` versus `off` |
| the consumed-epoch distinction | `epsilon` versus `?E !OK`, then `E`, requires `OK` versus `final-epoch` |
| a pending output's future-equivalence class until it crosses | at the same semantic condition, `?R` versus an invalid `?A` requires different sole next output bytes |

The exact representation may combine these responsibilities.  One `kappa`
coordinate and some pending bits are reconstructible, so this table does not
license a uniform field list.

### MAY REBUILD

- either one, but not both, of the two `kappa` coordinates using the executed
  constructor in section 2.1;
- `off` plus either `final-epoch` or `already-up` in pending rejections using
  the executed branch constructors in section 2.2;
- the constant format marker, canonical padding, lengths, frame bytes, sorted
  presentation, state numbers, class numbers, and shortest witnesses;
- the 19-byte reachable export from the bounded mutation log, fixed lifecycle
  byte, fixed pending cell, and frozen fold; and
- a canonical representative log from a reachable snapshot.

The two representation constructors each reproduced all 10,019 reachable
states.  Rebuild cost resides in the codec, invariants, fold, scans, lookup,
and CPU.

### MAY FORGET

Within this exact closed contract, executed convergent histories establish that
the following may be forgotten after any pending output crosses:

- rejected input operands and rejection-attempt count/timing;
- counts of repeated exact `B` and repeated `X`;
- the original order of independent successful bindings; and
- the raw path history whenever only the derived finite condition is queried.

For example, `epsilon` and `?Q(0,0,0)!REJ(000a)` reach the same condition, as
do `?X` and `?X ?X`.

### NOT CLASSIFIED AS DYNAMIC HISTORY

The transition specification, immutable policy, codec, and version must be
available and correct, but changing them changes the contract rather than
continuing two histories under one contract.  They are external specification
and TCB responsibility, not a dynamic `~=E` MUST-SURVIVE result.  Their storage,
distribution, selection, and recovery are still nonzero total-system costs.

Provisional atomic-abort state, caches, cursors, processes, physical location,
and scheduling effects were not in the finite machine and were not executed.
They remain NOT ESTABLISHED, not MAY FORGET.

## 4. Fresh breaker findings

### E1 — the output prediction is false

Section 1.2 supplies the exhaustive result and proof.  This is a frozen
construction error, not edited away.

### E2 — the prose folded log omits a bounded lifecycle choice

If the log contains only the stated `B/A/E` mutations and pending cell:

```text
h0 = epsilon
h1 = ?X
```

produce identical durable bytes, yet future `B(0,0,0)` requires `OK` versus
`off`.  If every lifecycle transition is appended instead, the equivalent
cycle `(?X ?R !OK)^n` makes the append-only log unbounded.

The experiment chooses and charges a concrete completion: one fixed durable
`u` byte, updated by `X` and by `R` while down, atomically associated with the
five-byte pending cell.  Under that additional choice, its folded log uses
8–37 bytes, at most two state-changing `B` entries, four successful `A`
entries, and one successful `E` entry, and agrees with the reference on all
58,571 tested edges.

That pass belongs to the explicit instrument realization.  It does not turn
the frozen prose omission into zero complexity.

### E3 — local canonical validation accepts an unreachable state

The candidate describes local invariants and padding rules but no total
accepted-byte language for snapshot recovery.  This 19-byte string passes the
local decoder and re-encodes identically:

```text
5a010002020202030000030000020000000000
```

It denotes empty associations with pending `VAL(epsilon)`.  It is absent from
all 10,019 reachable exports: a successful `Q` requires a bound position and
does not remove that binding.

Therefore the export is proved sound only on reachable states.  Recovery must
either add a whole-state reachability/pending-coherence rule, or declare import
of arbitrary durable bytes unsupported.  The instrument reports the defect
and does not silently strengthen the frozen decoder.

### E4 — shortest reference histories cannot exclude path-sensitive state

The reference histories:

```text
h0 = epsilon
h1 = ?R !REJ(0100)
```

converge to the exact same reference condition.  Only `h0` is its shortest
representative.  A defective realization can retain “a rejected R occurred”
and misbehave later.  Testing all outgoing edges once from the canonical state
does not expose that path if the checker assumes the realization also
converged.

Full realization conformance therefore needs either a trusted premise that
the declared durable bytes are the complete deterministic state, or an
inductive relational congruence check over alternate paths and physical
effects.  The current logical-adapter pass cannot establish absence of hidden
state.

### E5 — specification availability is TCB, not a history witness

Changing `P` changes the answer to a future `A`, but it defines a different
contract.  There is no same-contract pair in which “the specification
survived” is a dynamic state.  Section 3 moves this responsibility out of the
history quotient without crediting its storage or code as free.

## 5. Unlike-realization result and limit

The instrument implements two unlike logical encodings:

- a bounded mutation log plus a fixed lifecycle byte and pending cell; and
- the 19-byte canonical snapshot.

It independently codes their transition functions, reconstructs from durable
bytes at every shortest state, performs 1,428 quiescent `X` recoveries, checks
all 58,571 permitted outgoing edges, and converts every snapshot to a
canonical representative log.  All checked logical conditions agree byte for
byte.

This is evidence for two encodings, not two unlike physical systems.  They
share one Python process, host, codec contract, filesystem assumptions, and
reference model.  There is no torn-write, power-loss, corruption, replication,
independent-failure-domain, or cross-machine experiment.  Snapshot import is
also underspecified by E3, and alternate-history hidden state survives E4.
Physical interchangeability therefore remains UNKNOWN.

## 6. Quarantined R0.1D attack replay

The archive authorities were read only after the file-only break:

| archive artifact | SHA-256 |
|---|---|
| `REALIZATION-CORRECTION-R01D.md` | `b07fd627b4d75c9c069e791139e3b8233b3b0b95a33dd642bb83353c4aa4079c` |
| `FEASIBILITY-AUDIT-R01D.md` | `5d217612e5b62a0628fcff47282ef3cdc1ad119293dc9bbaa089e6987978194b` |
| `R01D-HISTORY-CORPUS.json` | `fc8ac76f03361f7757172df5897f0567916ad6d6e9bd608506137ef942f31d72` |
| `r01d_collision_search.py` | `56a4bdbad929e6c4ede397f2c159b4baf5717e5187c13323872bc769f01f7f2c` |

Classification below means:

- **DIRECT**: the attack exposes an R0.1E overclaim;
- **CLOSED**: R0.1E's finite method closes that attack or the old material is
  not inherited; and
- **WIDER**: the attack names a target capability R0.1E explicitly leaves
  unsupported.  This is not a pass toward the target contract.

| attack | result | disposition |
|---|---|---|
| D1 | WIDER | provider request and schema behavior are absent |
| D2 | WIDER | PREFLIGHT and multi-relation gate failure are absent |
| D3 | WIDER | semantic projection and authoring targets are unsupported; its constructibility lesson applies to E3 |
| D4 | WIDER | executable S/R/P relations and gate closure are absent |
| D5 | WIDER | raw-source and locator carriers are absent |
| D6 | WIDER | provider acquisition, launch, and corrupt outcomes are absent |
| D7 | WIDER | historical rejection query is explicitly excluded, so provenance forgets only under that narrower contract |
| D8 | WIDER | bootstrap authoring/authorization machinery is unsupported |
| D9 | WIDER | deadline, cleanup, and result-emission races are unsupported |
| D10 | WIDER | processes, ready tokens, EOF, and launch commitment are unsupported |
| D11 | WIDER | provider/cache behavior is absent; hidden physical state remains UNKNOWN |
| D12 | WIDER | parser/gate side effects are absent; the pattern reinforces E4 |
| D13 | WIDER | physical begin/open/crash behavior is unsupported; “channel” is only an alias here |
| D14 | WIDER | live replay and crash resumption are unsupported; only durable pending output exists logically |
| D15 | WIDER | terminal byte, EOF, clock, and replay phase are absent |
| D16 | CLOSED | no inherited S1 materialization exists |
| D17 | CLOSED | no checkpoint/locator duplication exists |
| D18 | WIDER | raw completion and EOF queries are absent |
| D19 | WIDER | measurements, aggregation, and structured status are absent |
| D20 | WIDER | operation/errno queries are absent |
| D21 | WIDER | constituent checks and gate explanation are absent |
| D22 | CLOSED | one LTS and fixed-point refinement replace conditioned family comparisons |
| D23 | CLOSED | all inclusion-minimal projections in each declared family are reported |
| D24 | CLOSED | every claimed reconstruction in this audit executes and byte-compares |
| D25 | CLOSED | the exact candidate digest is enforced and mismatch fails closed |
| D26 | CLOSED | transforms operate on actual canonical bytes, not handwritten merge tokens |
| D27 | **DIRECT** | shortest representatives do not test alternate path-sensitive physical state; E4 is the minimized witness |
| D28 | CLOSED | deletion results are limited to two explicitly frozen granularities; no whole-extractor global claim is made |
| D29 | CLOSED | all future answers come from the executable transition function |
| D30 | CLOSED | literal positions and associations are exhaustively exercised; transpose merges fail |
| D31 | CLOSED | the input codec is closed and unknown frames/orders reject |

The replay's dominant result is not that the legacy runtime attacks vanished.
It is that R0.1E put them outside its contract.  That accurately bounds the
finite theorem but is exactly why R0.1E cannot satisfy the target goal.

## 7. Simultaneous total-system account

No weighted scalar score is used.

| dimension | audited R0.1E result and charged cost |
|---|---|
| information/distinction preservation | complete for the exact 10,019-state reference quotient; omitted target futures dominate remaining loss risk |
| persistent state | every dynamic quotient class is distinct; candidate snapshot is 19 bytes, tested folded log 8–37 bytes, and one `kappa` coordinate plus selected rejection bits rebuild |
| semantic machinery | closed codec, 35 inputs, 28 actual outputs, transition function, policy table, legality, serializer, 58,571-edge graph, refinement, and constructors |
| human cognition | nine diagnostic meanings and short witnesses aid inspection; positional opcodes, microsteps, projection families, and unsupported boundaries still require learning; no participant study exists |
| authoring burden | exact candidate, reference fold, two adapter folds, projection definitions, constructors, breaker cases, digest maintenance, and audit |
| query/navigation burden | exact `Q` is constant and tiny; discovery, aggregation, general query, and navigation are unsupported rather than cheap |
| runtime | one observed full run used about 7.8 seconds and 54,056 KiB maximum RSS on this host; no portability claim follows |
| storage | logical snapshots are 19 bytes and tested logs 8–37 bytes; interpreter, script, specification, and result reproduction are additional storage |
| operations | atomic input commit, pending-output clear, lifecycle coordination, recovery, integrity checking, and experiment execution remain |
| trusted computing base | candidate reader/hash check, Python/runtime/host, reference fold, two adapters, codec, serializer, graph builder, partition refiner, constructor checks, and audit logic |
| evolution | only one observable epoch bit exists; semantic-changing upgrade, migration, rollback, downgrade, and mixed versions are unsupported |
| portability | two unlike logical encodings agree in one process; physical portability and power-loss behavior remain UNKNOWN |
| explainability | exact masks and minimized suffixes explain finite decisions; historical provenance and free-form explanation are unsupported |
| information-loss risk | exhaustive model checking removes finite model collisions; hidden paths, counterfeit imports, implementation faults, contract shrinkage, and all omitted futures remain |

### Where the complexity is now

| apparent simplification | complexity now located in |
|---|---|
| delete raw histories | total fold, convergence proof, hidden-state premise, and recovery |
| delete one association coordinate | invariant-aware constructor and retained other coordinates |
| delete pending mask bits | branch-aware reconstruction from `u`, `e`, tag, and retained mask |
| use a dense class code | quotient table/version, encoder/decoder, lookup, migration, and corruption handling |
| bounded folded log | fixed lifecycle and pending cells, canonical compaction, atomic updates, and recovery validation |
| omit rejection provenance | narrower future interface with no historical rejection explanation |
| omit in-flight crash | unsupported continuation, not zero recovery state |
| omit broad semantics/query/action | target-contract work deferred outside this experiment |
| use one host for unlike encodings | shared-failure and physical equivalence remain untested |

## 8. Target boundary and next successor constraints

R0.1E proves a bounded methodological point: once the external contract and
alphabet are truly closed, exhaustive histories and futures can compute their
quotient and expose both collisions and successful reconstruction.  It also
shows how easily a small quotient can be purchased by shrinking the contract.

The next candidate must not silently select one minimum across contract forks.
At minimum it must expose separate future-equivalence relations for:

- synchronous-only rejection versus later rejection-history explanation;
- quiescent-only restart versus pending/in-flight crash and resume;
- a fixed semantic version versus upgrade, migration, rollback, and mixed
  versions;
- fixed policy versus externally authored, revoked, delegated, or evolved
  authority;
- positional `Q` versus discovery, aggregation, general query, navigation, and
  explanation; and
- unlike logical encodings versus unlike physical durability and capability
  placement.

These variants are Pareto-incomparable until their external contracts are
fixed; no weighted scalar may hide the difference.  Each newly permitted
future needs exact crossing carriers and an executable interpreter before it
can force persistence.  Prior archives may supply attacks, not structures.

R0.1E therefore remains a completed finite experiment but an inadequate target
candidate.  No authoring, action, production implementation, or target gate is
authorized, and the requested first target milestone remains open.
