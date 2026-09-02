# FEASIBILITY AUDIT R0.1F — CONTRACT FRONTIER, SYMBOLIC QUOTIENT, AND ORACLE FAILURE

## 0. Frozen authorities, chronology, and verdict

This audit does not modify the frozen candidate.

| artifact | commit | SHA-256 |
|---|---|---|
| `BLIND-ATTACK-PACK-R01F.md` | `da3f73e84c36a4c5a6a4a59b8c5f2b21cf706962` | `a3ad2d62a94a0b124d540165bf88e6e4174ad960fdaf3f8117eca695b096db72` |
| `CONTRACT-FRONTIER-R01F.md` | `ca05df743b38ab40fa40a2d0257544500afa617b` | `f9fce4d2f0fd43594553f06ab05403d90b088b3f2fd50b7c3f883be7f7b03445` |
| `POSTFREEZE-BREAK-R01F.md` | `05f31be76e5a905cebb87c7ef7c721d1f3fce012` | `c02942e082fd6fd304ae5fefb0f14e4fb7c8685236f8e9ab1f5ce2d4f75d0a4f` |
| `r01f_frontier_falsifier.py` | `9c4fdcc4552eebb5bf7ac465171af33c855ea5bf` | `2315e4c8152bfad801bb5eb78fda0bff8a374ff546834279bc8a23992d5c653d` |
| `ARCHIVE-REPLAY-R01F.md` | `6d90bbd729ce1bbc5712069e2c5aba2f920615cf` | `701024abd490822852352ec1e994849cb2927dac8dfcf2452d91728d3ba43487` |

The falsifier's canonical JSON output has reproducible SHA-256:

```text
5c2079c7288eba4d547b5aaf2fceb26b053fd6835a95bee0c4d3cd51c22340e5
```

The reproduced invocation took 31.13 seconds, reached 43,328 KiB maximum
resident memory, and exited 1 because findings marked `FAIL` are present.
`python3 -m py_compile` passed.  A second run produced the same output hash.
The instrument is a falsifier, not semantic authority and not an architecture.

The quarantine order was:

1. an ontology-blind breaker derived attacks without seeing a candidate or the
   repository and froze them;
2. a separate ontology-isolated builder, also without repository access,
   produced CF-1;
3. CF-1 was frozen verbatim before any defect was repaired or any old archive
   was opened;
4. the blind breaker received only its attack pack and the frozen candidate;
5. an independent implementer received only the frozen candidate and built the
   executable falsifier; and
6. only after the fresh break did a replay agent read earlier attacks.  Earlier
   proposed solutions were excluded.

Verdict:

```text
R01F EXACT CT BYTES AND NO-CRASH CORE = PASS
R01F CLOSED CLIENT CROSSING LANGUAGE = CONTRADICTORY
R01F POWER ACTION/RECOVERY ORACLE = CONTRADICTORY
R01F SUCCESS/PROVENANCE RULE = UNDERSPECIFIED
R01F CURRENT TOTAL IDENTITY = COLLIDING / UNDERSPECIFIED
R01F COMPONENTWISE PERSISTENCE VERDICTS = FALSIFIED
R01F COARSE REACHABLE DIRECT-TUPLE CUT STATES, CONDITIONAL = 165
R01F DETAILED REACHABLE DIRECT-TUPLE CUT STATES, CONDITIONAL = 34*U-67
R01F FULL POWER QUOTIENT = UNKNOWN
R01F PRACTICAL EXHAUSTIVE FIRST EXPERIMENT = FAIL
R01F UNLIKE PHYSICAL REALIZATION EVIDENCE = ABSENT / UNKNOWN
FIRST TARGET MILESTONE = NOT YET MET
NO PRODUCTION, AUTHORIZATION, OR ARCHITECTURE GATE RESULT
```

Here

```text
U = (256^256 - 1) / 255
```

is the 615-decimal-digit number of declared raw client byte strings.  The
conditional direct-state counts are useful symbolic results.  They do not cure an oracle
that gives incompatible required continuations.

## 1. What the executable experiment established

### 1.1 Reproducible result

The deterministic report contains:

| status | count |
|---|---:|
| `PASS` | 21 |
| `FAIL` | 6 |
| `UNKNOWN` | 6 |

The six machine findings marked `FAIL` cover universal framing versus malformed
crossings, the crash-after-`A0` prefix, the crash-after-`AE` old-byte outcome,
generic versus action-specific `A1` recovery, stale latest-IDENTIFY identity,
and the false componentwise MUST verdict for detailed length and offset.

The six `UNKNOWN` findings cover the ambiguous success/provenance rule, the
inconsistent full power residual, the undefined power-versus-atomic realization
equivalence relation, incomplete global witness ordering, physically
unmaterializable dense/DAG comparison, and the absent unlike physical builds.

### 1.2 Passing byte and transition facts

The following facts passed without repairing the candidate:

- CT1 is exactly 172 bytes and ends in LF;
- CT2 is exactly 182 bytes and ends in LF;
- their UPDATE frames are exactly 177 and 187 bytes;
- all displayed fixed encodings and protocol tags match the frozen text;
- the representative validator cases produce their specified first rule and
  offset;
- the symbolic disjoint validation partition plus the 43 potentially
  successful frames sums to exactly `U`;
- immediate coarse/detailed rejection and EXPLAIN bytes match the stated
  encodings under the candidate's intended out-of-band crossing assumption;
- malformed CREATE, ACTION, UPDATE, EXPLAIN, and IDENTIFY representatives
  replace detailed provenance in the reference implementation;
- CT1 self-update, CT1-to-CT2, CT2 self-update, and CT2 downgrade rejection have
  the declared no-crash behavior;
- the direct interpreter, direct-action, and timeout-action traces match their
  declared no-crash orders;
- an atomic-scope quiescent crash preserves the tested stable state;
- the twelve unambiguous no-crash seed witnesses separate;
- the proposed direct normalization is congruent over the representative
  atomic no-crash alphabet, with an exact symbolic lemma for all other invalid
  inputs;
- retired creation/nonce distinctions and the live action bit after both
  nonces complete pass the stated deletion checks; and
- the saved detailed rule has a genuine two-history survival witness.

These are local results.  They cannot authorize the contradictory power
machine or substitute for either physical realization.

### 1.3 Exact conditional direct-state counts

Assuming that successful requests preserve saved provenance and temporarily
removing the inconsistent power oracle, the symbolic calculation obtains:

| quantity | exact result |
|---|---:|
| normalized primary configurations before provenance | 228 |
| non-none detailed rejection tuples | `U` |
| naive coarse tuple space | 456 |
| naive detailed tuple space | `228*(U+1)` |
| reachable direct-tuple cut states through two inputs, coarse | 165 |
| reachable direct-tuple cut states through two inputs, detailed | `34*U-67` |
| reachable direct states through five inputs, detailed | `228*U-324` |
| minimum whole-byte dense ID, coarse | 1 byte |
| minimum whole-byte dense ID, detailed | 256 bytes |

The conditional direct-state counts are the same for `B=atomic` and `B=power`.  The
candidate's claim that power strictly refines atomic is about realization
conformance, while its equivalence definition is about cut histories.  No
second equivalence relation is defined, and the quiescent tuple gains no `B`
responsibility.

The full residual-DAG partition and its dense identifier widths remain
`UNKNOWN`; the reported 1-byte and 256-byte widths are conditional widths for
these reachable direct-state counts, not completed proofs of the full quotient.

The recurrence `T(3)` has 1,852 decimal digits.  Enumerating every member of
`U`, sorting the residuals, and hash-consing the full DAG is mathematically
finite on an ideal machine but not a practically executable first experiment.
The falsifier therefore uses exact symbolic partitions and minimized
representatives and reports the unmaterialized comparisons as `UNKNOWN`.

## 2. Minimized blocking witnesses

### 2.1 The empty raw crossing has no declared boundary history

Section 2 says every crossing is exactly `E(P)`, hence contains at least its
two-byte length, and declares no alternative termination signal.  Sections 4,
8, and 16 require a completed empty raw crossing.

The intended comparison is STOP/no submission versus an occurrence that
submits the empty raw byte string, followed by EXPLAIN `00 01 40`.  The latter
is not a legal `E(P)` crossing and therefore has no boundary history under the
frozen rule.  If an external atomic-message or completion boundary were added,
the two occurrences would already be distinct rather than both `epsilon`.

The frozen text nevertheless assigns these intended responses:

```text
h0: 00 02 95 00
h1 coarse:   00 02 95 01
h1 detailed: 00 05 95 01 00 00 00
```

The missing boundary cannot be silently externalized.  This is a language
contradiction/undefined input occurrence, not a valid pair of equal histories.

### 2.2 Crash immediately after `A0`

After CREATE succeeds, submit ACTION nonce `00`:

```text
C->S 00 02 30 00
S->A 00 04 41 30 00 00                  # A0
F->* 00 02 46 30                         # F0
*->F 00 02 46 31                         # F1
```

Section 12.2 permits a crash immediately after every observable crossing.
Section 12.3's receiver-pre trace puts the crash before `A0`; its receiver-post
trace requires `AE` before the crash.  The displayed prefix is neither.  An
already crossed `A0` cannot be erased during recovery.

### 2.3 Crash after `AE`, before receiver durability

The frozen normal order places the receiver's durable applied record after:

```text
S->A 00 04 41 30 00 00                  # A0
A->W 00 04 41 45 00 00                  # AE
```

A permitted crash before or during the first receiver write preserves those
two external crossings while one-byte old/new atomicity permits the old
`unseen` durable receiver state.  The reference pre outcome forbids the crossed
prefix and the post outcome requires `applied`.  This is the uncertain-effect cut that the
receiver obligation was intended, but failed, to close.

### 2.4 Post-ack recovery has two required continuations

Crash after:

```text
A->S 00 04 41 31 00 00                  # A1 applied
```

but before local pending-to-completed commitment.  Section 10.3 says every
locally pending recovery begins with `A2` and a repeated `A1`.  Section 12.3's
generic post-crossing rule resumes after `A1` and commits without the probe.
The required trace set is not unique.

### 2.5 Recovery-machine crash scope lacks a precedence rule

The horizon permits at most one `F0,F1` pair.  Section 12.2 also names crashes
during persistent writes in recovery machinery.  After the sole crash is used,
those sites may be unreachable; otherwise exercising one requires a second
pair.  The text lacks the precedence rule that decides whether this is dead
scope or a violated bound.  This is an audit-only ambiguity, not one of the
falsifier's six executable `FAIL` findings.

### 2.6 Successful provenance preservation is grammatically open

Use a success with an explicit primary transition:

```text
reject:   00 01 00
success:  00 b9 60 00 b6 || CT2            # UPDATE CT1 -> CT2
future:   00 01 40                         # EXPLAIN
```

Section 6 says success never modifies provenance “unless” its primary
transition overlaps no provenance field.  Every listed primary transition
overlaps none, so the exception swallows the rule.  Section 8 protects only
successful EXPLAIN explicitly.  Preserving versus clearing the tuple yields
different future bytes and neither choice is authorized by the frozen text.

### 2.7 “Latest IDENTIFY” is not current identity

```text
h0: IDENTIFY
h1: IDENTIFY ; UPDATE CT2
```

Both retain the same manifest and literal latest IDENTIFY response, while h0 is
at CT1 and h1 at CT2.  Future exact UPDATE CT1 succeeds after h0 and rejects as
`CT2_NO_DOWNGRADE` after h1.  Thus the stated total-identity pair collides.

### 2.8 Detailed length and offset are not independent MUST responsibilities

Smallest well-framed witness:

```text
request:  00 00                              # empty payload
reject:   00 03 83 04 02                     # rule 04, offset 02
future:   00 01 40
explain:  00 07 95 04 02 00 02 00 00
```

Given surviving `raw=00 00`, `length=u16be(len(raw))=00 02` is mechanical.
Given surviving `(rule=04, raw=00 00)` and the frozen validator, `offset=02` is
mechanical.  DELETE succeeds for both stored copies.  Their output
responsibilities survive, but their dedicated persisted components are
`MAY REBUILD`, not `MUST SURVIVE`.

## 3. Persistence classification after attacks

The following classification is conditional on a successor closing the input
boundary and selecting one noncontradictory power oracle.  It classifies
information responsibility, not fields or storage layouts.

### 3.1 MUST SURVIVE

| responsibility | minimized distinguishing future |
|---|---|
| input occurrence/completion when bytes alone are empty or incomplete | STOP versus empty submission; future EXPLAIN |
| active CT version | `[]` versus `[UPDATE CT2]`; future IDENTIFY or UPDATE CT1 |
| lifecycle | live versus retired after the same CREATE; future OBSERVE |
| live `o` | two CREATE histories differing only in `o`; future OBSERVE |
| live `q` | two CREATE histories differing only in `q`; future QUERY |
| live `x` | differing `x`; future UPDATE CT2 then QUERY2 |
| live `i` | differing `i`; future INTERPRET with table `00,01` |
| live `a` while a nonce remains unused | differing `a`; future ACTION carries different `A0/AE` bytes |
| used-nonce distinction | CREATE versus CREATE/ACTION-00; future ACTION-00 |
| coarse no-rejection versus some-rejection | empty history versus one rejection; future EXPLAIN |
| detailed rejected raw bytes | reject `00 01 00` versus `00 01 01`; future EXPLAIN echoes different bytes |
| detailed rejection rule responsibility | QUERY2 then UPDATE-CT2 versus UPDATE-CT2 then QUERY2; same CT2/virgin/raw/offset, future EXPLAIN differs in rule |
| current A/B run identity outside IDENTIFY | same CT response under different manifest; next invalid request or fault context differs |
| active request/phase during power recovery | deleting it selects a different resume/replay trace; exact verdict awaits a consistent oracle |
| receiver resolution/dedup information while action is pending | applied versus unseen receiver world; recovery probe returns applied versus absent |

The last two are total-system responsibilities.  Moving them into retained
transport or a receiver does not make them disappear; that component, its
protocol, storage, recovery, and trust are charged.

### 3.2 MAY REBUILD

| information or representation | exact source of reconstruction |
|---|---|
| CT text copy | active version plus the exact immutable CT mapping specification |
| detailed rejected length | `u16be(len(raw))` |
| detailed rejection offset | exact `(rule,raw)` plus the frozen validator |
| local active-frame copy | exact retained transport bytes, if that transport contract is supplied and tested |
| shortest history representatives | deterministic parent pointers only after the incomplete byte-count, pair-orientation, and serialization order is frozen; until then this rebuild claim is `UNKNOWN` |
| residual DAG cache | frozen oracle plus exhaustive enumerator, conceptually; operational rebuilding is not demonstrated |
| dense-ID mapping | exact quotient ordering plus residual structures; a bare ID is insufficient |

The immutable mapping, validator, enumerator, and retained transport are
identified specifications/TCB.  Reconstruction complexity is not credited as
zero, and the full residual/DAG rebuild is physically unestablished.

### 3.3 MAY FORGET

Within CF-1's explicitly restricted future language, executable congruence or
the frozen transition rules support forgetting:

- creation bits and nonce distinctions after retirement;
- live `a` after both nonces have completed;
- an interpreter table and result after its client response completes;
- completed request order older than the one saved rejection responsibility;
- the pre-cut transcript itself, because future policies are explicitly denied
  prior-history access;
- settled timeout scheduling information; and
- receiver dedup state after local durable completion and all channels settle,
  provided no permitted receiver query or replay can reach it.

These verdicts do not generalize to a longer horizon, arbitrary history-aware
interpreters, rollback, or a wider receiver contract.

## 4. Mandatory attacks and where the complexity moved

| attack | result |
|---|---|
| DELETE | succeeds for stored detailed length/offset, retired data, exhausted action bit, completed interpreter data |
| MERGE | the conditional direct tuple has 165 coarse or `34*U-67` detailed reachable cut states; full residual and power merge results are unknown |
| DERIVE | rebuilds CT text, detailed length/offset, and proposed caches only with named specification/apparatus |
| RECOMPUTE | symbolic validation avoids materializing `U`; full dense/DAG regeneration remains physically unsupported |
| COLLIDE | the empty crossing is undefined under universal framing; stale latest-IDENTIFY supplies a minimized actual collision |
| FUTURE | twelve no-crash witnesses pass; contradictory crash futures prevent a total power comparison |
| EXTERNALIZE | receiver, retained transport, manifest, CT mapping, timeout source, drivers, and oracle remain charged |
| REALIZE | two unlike families are prescribed but absent; no realization evidence exists |
| COGNITION | a 1,109-line seed still required discretionary interpretation at seven points; the frozen artifacts do not support independent execution without invention |
| TCB | the candidate identifies a broad TCB but supplies no corruption/removal dossier or cold rebuild |

After the apparent compact direct tuple, complexity is located in:

- the boundary that declares an input complete;
- exact raw rejection retention, which makes the detailed quotient enormous;
- the receiver's uncertain external-effect cut;
- request/response retention and deduplication;
- current run-manifest and contract mapping integrity;
- crash-site and recovery-set semantics;
- symbolic validation and residual-generation code;
- comparison/oracle code shared by both proposed builds;
- physical serializers, recovery paths, drivers, and fault harnesses; and
- human procedures needed to resolve text that the machine cannot decide.

None of those responsibilities is zero because it is outside an engine tuple.

## 5. Simultaneous total-system evaluation

No row is a weighted score, and measurements from imaginary different builds
are not combined.

| dimension | R0.1F evidence-backed result |
|---|---|
| distinction preservation | conditional atomic direct-state partition and witnesses are useful; the total oracle fails before a full quotient result exists |
| persistent state | symbolic responsibilities identified; no physical byte ledger or sound power recovery exists |
| semantic machinery | exact validator/no-crash reducer implemented; power reducer is contradictory |
| human cognition | exact bytes help, but seven defects require invention; corpus and 1,109-line contract impose high verification burden |
| authoring burden | fixed CREATE, UPDATE CT1/CT2, and RETIRE exist; arbitrary authoring is unsupported |
| query/navigation burden | five fixed queries exist; discovery, search, aggregation, and general selectors are unsupported |
| runtime | no-crash traces execute; full crash trace set has no unique oracle |
| storage | conceptual direct/dense/DAG candidates only; detailed dense ID alone is 256 bytes and mapping/apparatus is charged |
| operations | no cold restart, rebuild, deployment, cleanup/reset, or trace-reproduction dossier |
| trusted computing base | receiver, transport, mappings, timeout, drivers, oracle, harness, configuration, and humans are identified but untested |
| evolution | exact CT1/CT2 cases pass; additional versions, migrations, undo, and reinterpretation are unsupported |
| portability | only an abstract one-byte-atomic interface is named; no physical family exists |
| explainability | exact coarse/detailed bytes pass conditionally; preservation rule ambiguous and two stored components are redundant |
| information-loss risk | minimized consequence witnesses exist; probabilities and physical corruption behavior are unsupported |

## 6. Archive replay

The old archive was opened only after CF-1 and its fresh audit were frozen.
The replay changed no top-level verdict.  It added the independent DERIVE
failure in Section 2.8 and classified older attacks as follows:

- malformed stream/completion, action recovery, crash count, provenance, and
  path-sensitive identity attacks were already found freshly;
- exact CT bytes, representative validation precedence, the symbolic `U`
  partition, and unambiguous atomic no-crash distinctions have executable
  discharge evidence;
- adaptive correlation is represented by complete ordered transcript sets,
  but full power comparison remains unknown;
- arbitrary authoring, discovery/navigation, processes/providers/EOF, clocks,
  authority/privacy/erasure, randomness, concurrency, and ambient modes are
  explicitly unsupported rather than passed;
- arbitrary counterfeit/rollback recovery images are outside semantic crash
  inputs and remain TCB loss attacks for a future physical build;
- exact binding of evidence to physical subjects, cleanup/reset equivalence,
  hidden service state, timeout-source behavior, bootstrap/offline dependency
  closure, and human/TCB evidence remain unknown; and
- no fixed-overwrite or append/fold build, fault dossier, storage ledger, or
  operations dossier exists.

Old named abstractions receive no authority from this mapping.  The replay is
only an adversarial classification.

## 7. Boundary of the result

CF-1 correctly states the exact-history interpreter theorem: if a future
interpreter may compare its input with any exact prior history, every distinct
history has a separating future and the quotient is identity.  Its smaller
candidate partition is possible only because INTERPRET is limited to four unary
tables, UPDATE to CT1/CT2, the past transcript is hidden from future policy,
and the horizon is bounded.

CF-1 also demonstrates a second boundary: finite does not mean experimentally
tractable.  Detailed echo of arbitrary raw rejection bytes makes even the
reachable direct-state count nearly as large as the input universe.  The first experiment must begin with a
small explicit corpus that can actually be exhaustively crossed, minimized,
and independently realized.

The defensible result is therefore not a kernel or total architecture.  It is:

1. a set of exact or explicitly conditional survival/rebuild/forget verdicts;
2. seven minimized specification failures showing why the total CF-1 oracle
   cannot be executed uniquely;
3. an exact symbolic scale result showing where explanation detail moves
   information responsibility;
4. a list of externalized TCB and cognition costs; and
5. a sharper requirement for the next seed: a small explicit boundary alphabet,
   a realizable action/crash trace contract, and two actual unlike builds.

Until those exist and agree against one total oracle, the first target
milestone remains open.
