# ZERO GROUND R0.1L — Persistence Collision Ledger

Status: **FAIL for the frozen first-milestone claim; partial contract-relative
logical classifications survive; physical realization remains UNKNOWN.**

This is an audit verdict about information responsibilities under exact
contract `ZG-1`. It is not a repair, representation, data model, architecture,
implementation, or recommendation for a field, log, graph, table, object,
index, or storage engine.

## 0. Input gate and quarantine

Only these two frozen files were read:

| input | required SHA-256 | observed SHA-256 | result |
|---|---|---|---|
| `HISTORY-SEED-R01L.md` | `0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb` | `0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb` | PASS |
| `POSTFREEZE-BREAK-R01L.md` | `0744f495f0a229715e1f088c99d96bbbe0b409aaef522e54fb2a8fc516461b9a` | `0744f495f0a229715e1f088c99d96bbbe0b409aaef522e54fb2a8fc516461b9a` | PASS |

Neither input was altered. No other repository file, Git history, prior
artifact, executable, implementation, archive, or builder explanation was
read.

## 1. Classification semantics

- **MUST SURVIVE** means that deleting or merging a logical distinction can
  make two completed histories with different permitted residual behavior
  collide, or can invalidate an evidence claim that remains asserted.
- **MAY REBUILD** means an output or materialized view is a total deterministic
  function of surviving logical information plus an exact, still-bound
  reconstruction specification. All sources and bindings must remain
  available; corruption must fail closed.
- **MAY FORGET** means every permitted common future remains byte-identical
  after the deletion. This requires a proof under `ZG-1`, not merely the
  absence of a finite collision.
- **UNKNOWN** means a required premise, reconstruction specification, future
  domain, evidence chain, or realization fact is absent.

These are contract-relative logical verdicts. MUST SURVIVE does not assert that
any physical medium actually preserves the distinction. MAY REBUILD does not
assert acceptable latency or that a decoder exists. MAY FORGET stops being
valid if a later contract adds transcript audit, viewer-relative output,
execution counting, rejected-attempt explanation, or stronger chronology.

## 2. Non-overlapping responsibility normalization

The frozen candidate's four MUST-SURVIVE headings overlap. The same logical
information should not be counted once as an event/placement and again as a
branch or action “correlation.” The non-overlapping normalization is:

### R1 — accepted labeled effect occurrences and multiplicity

For every accepted changing `W`, `F`, `D`, `I`, or first `A`, the fact that an
effect occurrence exists, its operation byte, target byte, final
argument/key byte, and the number of indistinguishable repeated occurrences
are **MUST SURVIVE**. Membership in this collection also carries the fact that
the request was accepted; a separate accepted flag is not an additional
responsibility.

The actor byte is excluded from R1 because it is derivable under R3 from R2's
causal prefix. Input-frame tags and length `0004` are deterministic framing,
not additional effect information.

### R2 — required causal placement relation

The relation that attaches each accepted effect to the exact causal prefix on
which its semantics depends is **MUST SURVIVE**. It retains required order on a
lineage, explanation membership/order, fork attachment, and first-action
attachment. It need not retain chronology between effects proved to commute.

This is one logical responsibility, even if a realization uses several
mechanisms.

### R3 — exact contract/version/root binding

The exact `ZG-1` grammar, initial semantic root, transition precedence,
authorization rule, interpretation rule, capacity rule, output grammar, and
contract/version identity used for reconstruction are **MUST SURVIVE as a
total-system authority**. They need not be repeated per history, but they
cannot be inferred from survivor bytes or silently replaced by ambient code.

### Double-counting disposition

| candidate heading | normalized source | independent information? | disposition |
|---|---|---|---|
| accepted effect occurrence and bytes | R1 | yes | retain once in R1 |
| multiplicity | cardinality of R1 occurrences | no separate category | part of R1; SET collision proves cardinality matters |
| required causal placement | R2 | yes | retain once in R2 |
| branch creation/snapshot correlation | `F` operation/parent/child bytes in R1 plus its parent-prefix attachment in R2 | no extra information | current parent, child surface, copied prefix, and explanation MAY REBUILD |
| completed action key/snapshot correlation | first `A` operation/branch/key bytes in R1 plus its branch-prefix attachment in R2 | no extra information | completion bitmap, receipt value, actor/mode, and receipt explanation MAY REBUILD |
| accepted/no-effect selector | R1 membership produced under R3 | not an additional survivor | selector correctness moves to ingestion/TCB |
| global sequence order | R2 plus redundant chronology between independent effects | partly overlapping | R2 MUST SURVIVE; proved-independent remainder MAY FORGET |
| frozen behavioral specification | R3 | omitted from the advertised mutable-history partition, but not from the total system | MUST SURVIVE as exact reconstruction authority |

Branch and action witnesses remain essential: they force R1 or R2. They do not
force a dedicated third or fourth store of the same correlation.

## 3. Smallest forcing futures and exact conditions

Request shorthand below expands uniquely under the frozen frame grammar. For
example, future `Q0r` is the exact input frame:

```text
49 00 03 51 30 72
```

For empty versus one raw `x`, its exact output frames are:

```text
4f 00 03 56 00 00       ; V, zero bytes
4f 00 04 56 00 01 78    ; V, one byte x
```

| surviving distinction | minimized history pair or condition | shortest future | forced output distinction | class |
|---|---|---|---|---|
| accepted occurrence | `B` / `B,WA0x` | `Q0r` | empty / `x` | R1 MUST SURVIVE |
| operation | `B,FA01` / `B,AA01` after deleting byte 0 | `WA1x` | `K` / `N0` | R1 MUST SURVIVE |
| target | `B,FA01,WA0x` / `B,FA01,WA1x` after deleting byte 2 | `Q0r` | `x` / empty | R1 MUST SURVIVE |
| final argument/key | `B,AA00` / `B,AA01` after deleting byte 3 | `AA00` | receipt `=` / first emission `!` | R1 MUST SURVIVE |
| multiplicity | `B,WA0x` / `B,WA0x,WA0x` under SET | `Q0r` | `x` / `xx` | R1 MUST SURVIVE |
| same-lineage order | `B,WA0x,WA0y` / `B,WA0y,WA0x` | `Q0r` | `xy` / `yx` | R2 MUST SURVIVE |
| action causal placement | `B,IA01,AA00` / `B,AA00,IA01` under BAG | `E00` | receipt explanation has two events / one | R2 MUST SURVIVE |
| fork snapshot attachment | `B,WA0x,FA01,WA0y` / `B,WA0x,WA0y,FA01` | `Q1r` | `x` / `xy` | R2 MUST SURVIVE |
| first-action snapshot attachment | `B,WA0x,AA00,WA0y` / `B,WA0x,WA0y,AA00` | `AA00` | committed `x` / `xy` | R2 MUST SURVIVE |
| completed action fact | `B` / `B,AA00` | `AA00` | first emission / receipt | R1 occurrence plus R2 attachment; not a separate responsibility |
| branch existence/parent | `B` / `B,FA01` | `Q1p` | `N0` / `C0` | R1 fork occurrence plus R2 attachment |
| exact contract/version binding | same completed history `B,WA0x,IA01`, interpreted by frozen swap semantics versus an unbound identity interpretation | `Q0t` | `y` / `x` | R3 MUST SURVIVE |

The last row is a binding witness, not a comparison between two valid `ZG-1`
contracts. It shows that survivor bytes alone do not select their
interpretation; deleting the exact contract binding leaves two possible
futures.

## 4. Corrected logical classification ledger

### 4.1 MUST SURVIVE

| responsibility | exact scope and condition | what is not additionally required |
|---|---|---|
| R1 labeled accepted-effect occurrences and multiplicity | Every accepted changing body contributes operation, target, argument/key, and one occurrence. Identical repeats remain separate in cardinality. | actor byte, old input envelope, old success output, a dedicated acceptance field |
| R2 required causal placement | Enough relation to replay controller/mode/data evolution, per-branch explanations, fork snapshots, and first-action committed prefixes exactly. | total chronology between proved-independent effects; copied current surfaces; dedicated parent/receipt records |
| R3 exact contract/version/root binding | Exact frozen source of grammar, semantic root, transitions, capacity, actor derivation, output framing, corruption policy, and version identity for every rebuild. | repeated per-history copy, provided an exact authoritative binding remains available |
| bounded-run claim evidence, if the run is presented as evidence | Candidate digest, extracted code bytes, interpreter identity/digest/version, stdout, stderr, exit status, manifest, and binding to the declared domain. | nothing physical is inferred merely from retaining artifacts |

The last row is claim evidence, not residual ZG-1 behavior. The frozen candidate
does not contain the complete evidence chain it demands, so its evidence status
is FAIL/UNKNOWN even though the logical responsibility is conditional MUST
SURVIVE whenever that PASS claim is retained.

### 4.2 MAY REBUILD

| responsibility | exact surviving sources | total reconstruction rule and conditions |
|---|---|---|
| actor byte of each accepted effect | R1 operation/target/argument, R2 causal prefix, R3 controller semantics | take the then-current controller of the target (parent for `F`), insert it at byte 1, validate acceptance, fail closed on mismatch |
| branch existence, raw/interpreted bytes, controller, mode, parent, and causal explanation | R1, R2, and R3 initial root/transitions | deterministic replay in causal order; explanation rendering follows exact accepted bodies |
| action completion bitmap, committed value/mode/actor, and receipt explanation | first `A` in R1, its R2 attachment, and R3 action semantics | evaluate the attached branch prefix once; later identity retries do not add state |
| future response body, tag, count, and frame length | reconstructed logical state, future request, and R3 response/frame grammar | execute the total complete-body transition and frame its exact output |
| accepted input envelope when needed for a generated explanation or validation | rebuilt four-byte body plus R3 input-frame grammar | prefix with `I` and exact U16 length four; this does not recreate forgotten rejected traffic |
| finite D behavior signature as a test artifact | reconstructed state, exact ordered 655-future list, and exact oracle | rerun all futures in order; this is not a general quotient or independent evidence |

These are derivability verdicts, not performance or availability verdicts.

### 4.3 MAY FORGET

| information | proof condition | invalidating contract extension |
|---|---|---|
| completed identity-transition inputs: boot, query, explanation, invalid body, N0/N1/N2/N3/N4/N6 rejection, and action retry | after its output crosses B, the transition leaves the replay result byte-identical; induction gives identical output for every common future | transcript query, rejected-attempt explanation, execution-count query, audit of invalid traffic |
| old output-frame bytes | future policies may remember outputs privately but cannot ask the candidate for the old transcript; future results derive from R1–R3 | transcript/audit/replay-byte endpoint |
| old framing around forgotten identity traffic | frame bytes have no residual semantic effect after the completed transaction | past-frame query or forensic obligation |
| redundant input frame around an accepted four-byte body | `I` and U16 length four rebuild from R1/R3 | preserving exact past transcript rather than residual behavior |
| relative chronology of two accepted effects | only if their transition functions commute: separate existing lineages/correlations, no create/control/mode/data/snapshot dependency, distinct required action correlation, and neither explanation includes the other | global chronology query, cross-lineage explanation, or any failed commutation premise |
| ephemeral replay/index caches that are not boundary-visible and carry no evidence claim | exact R1–R3 survive and cache loss changes only performance | promised performance, navigation bytes, availability, or cache identity |

The valid fork rejection `N2` is explicitly included; its omission from the
candidate's numbered forget list was a list-completeness defect, not a semantic
survivor.

### 4.4 UNKNOWN

| proposed responsibility/mechanism | why no positive class is available |
|---|---|
| exact production index, cache, query plan, or navigation view | No artifact grammar, algorithm, output contract, or correctness relation is frozen. An internal unobserved cache may forget, but a named view cannot be credited MAY REBUILD without a specification. |
| canonical ordering for a causal partial-order encoding | R2 is necessary and independent chronology can forget, but no relation encoding or canonical topological-sort rule is selected. |
| global quotient/minimum responsibility set | The induction proves sufficiency, not minimality; D is finite, D1/hidden evidence is absent, and no representation universe is closed. |
| partial frames, mid-frame restart, concurrent input, progress, and availability | Unsupported by `ZG-1`; no future/result or timeout rule exists. |
| later contract conversion/version evolution | No `ZG-2`, total conversion, rollback, or cross-version witnesses exist. |
| actual subject conformance and between-execution preservation | No subject or persistence run is evidenced. |
| physical storage, crash durability, recovery, and persist-before-ack | No medium, fault set, atomicity experiment, or durability evidence exists. |
| human comprehension, workload, access, and error | No reviewer task, population, time, expertise, or outcome evidence exists. |
| TCB closure and size | Parser, selector, replay, version binder, codec, runtime, storage, and evidence chain are identified but not closed. |
| portability and materially unlike realizations | There are no instantiated realizations or independent evidence roots. |

## 5. ORACLE totality and logical state

The logical replay state is MAY REBUILD from R1–R3. The candidate named
`ORACLE` serialization is not the logical responsibility and cannot inherit
that verdict automatically.

For one root branch with `e` accepted `WA0x` effects, its nested ORACLE item has
length:

```text
8 + 7e
```

The outer SEQ item length uses U16. Thus:

```text
e = 9,361  -> 65,535 bytes, encodable
e = 9,362  -> 65,542 bytes, not encodable
```

`B` followed by 9,362 accepted `WA0x` requests is a valid `ZG-1` history below
the 16,000-event capacity. This is the smallest repeated-write totality witness
reported by the fresh break. Therefore:

- logical replay state: **MAY REBUILD** from R1–R3;
- ORACLE on finite D: only a bounded predicted/reproduced result, not the
  candidate's required evidence-chain PASS;
- ORACLE as a total all-`ZG-1` encoder: **FAIL**;
- any alternative total serialization or physical persistence: **UNKNOWN**.

The failure moves complexity to codec-domain proof, length accounting,
corruption rejection, and version binding. It does not imply a replacement
encoding.

## 6. Overlap-sensitive partial-order and navigation audit

R2 is a causal relation responsibility. A global accepted-event sequence
contains R2 plus order that may be irrelevant. The audit must not count both
the sequence and a second branch/action correlation graph as separate minimum
information.

| case | logical disposition | conditions |
|---|---|---|
| same-lineage effects | R2 MUST SURVIVE order/attachment | writes, delegation, mode, fork, or action attachment can change data, authority, snapshots, or explanation |
| fork versus parent/child effect | R2 MUST SURVIVE unless exact commutation is proved | fork snapshots the parent at its causal position |
| first action versus branch mutation | R2 MUST SURVIVE unless exact commutation is proved | action commits interpreted bytes and explanation at its attachment |
| effects on proved-independent lineages/action correlations | relative chronology MAY FORGET | both transitions commute and produce identical per-branch explanations/receipts for all futures |
| chosen serialization of R2 | UNKNOWN | no representation is selected by the logical duty |
| canonical topological ordering | UNKNOWN | no frozen canonicalizer; it is not automatically derivable |
| internal index over R2 | MAY FORGET if unobservable; otherwise UNKNOWN | performance-only cache versus promised navigation artifact must be separated |
| query/navigation results already in ZG-1 | MAY REBUILD | exact Q/E outputs follow replay; discovery/search is unsupported |

Removing redundant global chronology moves complexity to independence proof,
causal-relation maintenance, topological rendering, concurrency reasoning,
recovery, and reviewer navigation. The bytes may shrink; the total-system work
does not disappear.

## 7. Mandatory attacks per responsibility

Each responsibility below is subjected to DELETE, MERGE, DERIVE, RECOMPUTE,
COLLIDE, FUTURE, EXTERNALIZE, REALIZE, COGNITION, and TCB. “Where now” records
the mandatory complexity transfer.

### R1 — accepted labeled occurrences and multiplicity: MUST SURVIVE

- **DELETE / MERGE / COLLIDE:** the occurrence, operation, target, argument,
  and SET multiplicity witnesses in §3 all yield different one-request futures.
- **DERIVE / RECOMPUTE:** actor and framing derive; operation, target, argument,
  occurrence, and count do not derive from the remaining projection.
- **FUTURE:** `Q0r`, `WA1x`, or `AA00` is sufficient for the minimized pairs.
- **EXTERNALIZE:** caller memory, a queue, rejected transcript, or operator log
  would move the missing label/count outside B and change the contract.
- **REALIZE:** no physical substrate or unlike realization is evidenced:
  UNKNOWN.
- **COGNITION:** compact projection increases replay burden; no human result is
  measured: UNKNOWN.
- **TCB:** accepted/no-effect filtering, capacity, authorization, framing, and
  acknowledgement ordering remain trusted and unclosed.
- **Where now:** ingestion selector, exact effect collection, replay validator,
  and contract binder.

### R2 — causal placement relation: MUST SURVIVE

- **DELETE / MERGE / COLLIDE:** BAG, same-lineage, fork-placement, and
  action-placement pairs in §3 distinguish loss of required attachment.
- **DERIVE / RECOMPUTE:** current surfaces cannot recover a past fork/action
  prefix; materialized parent, child, and receipt views do derive from R2.
- **FUTURE:** `E00`, `Q1r`, and `AA00` expose the smallest written collisions.
- **EXTERNALIZE:** timestamps, source-file order, VCS lineage, or operator
  convention merely relocate the relation outside B.
- **REALIZE:** copy, sharing, and pointer mechanisms are unevidenced: UNKNOWN.
- **COGNITION:** a partial relation needs navigation and canonical rendering;
  burden is unmeasured.
- **TCB:** relation construction, snapshot attachment, topological replay, and
  corruption detection are unclosed.
- **Where now:** causal-relation authority, renderer, replay, concurrency and
  recovery reasoning.

### R3 — exact contract/version/root binding: MUST SURVIVE

- **DELETE / MERGE / COLLIDE:** the same survivor bytes under swap versus
  identity interpretation yield `y` versus `x`; a shared name cannot merge
  different semantic bytes.
- **DERIVE / RECOMPUTE:** history does not derive its grammar/root/transition;
  it can only reference an exact surviving authority.
- **FUTURE:** one `Q0t`, invalid request, capacity edge, or action can expose a
  changed rule.
- **EXTERNALIZE:** embedding semantics in code, firmware, prompt, service, or
  operator memory moves the responsibility into deployment/TCB.
- **REALIZE:** no two realizations bind the same exact contract under
  independent evidence: UNKNOWN.
- **COGNITION:** compact events make reviewers consult more specification;
  burden is unmeasured.
- **TCB:** version selector, parser, transition engine, build, and corruption
  policy are unclosed.
- **Where now:** immutable contract authority, deployment binding, verifier,
  and evolution/conversion gate.

### R4 — actor byte: MAY REBUILD

- **DELETE / MERGE / COLLIDE:** bounded deletion of byte 1 found no collision,
  and the full-domain induction reconstructs it from the then-controller.
- **DERIVE / RECOMPUTE:** insert current controller at the event's causal
  position and validate exact acceptance; failure must not be skipped.
- **FUTURE:** all ZG-1 futures are preserved only if R1–R3 remain exact; the
  finite D pass alone is insufficient.
- **EXTERNALIZE:** dropping the byte moves work to replay and R3, not to an
  ambient identity provider.
- **REALIZE / COGNITION:** physical implementations and reviewer cost are
  UNKNOWN.
- **TCB:** actor reconstruction and prior-controller replay enter the trusted
  path.
- **Where now:** deterministic replay, validation, renderer, and exact version
  binding.

### R5 — replay-derived semantic views and future frames: MAY REBUILD

- **DELETE / MERGE / COLLIDE:** deleting a cache/view is safe only because R1–R3
  uniquely reconstruct its semantics; merging caches across different sources
  is unsafe.
- **DERIVE / RECOMPUTE:** exact replay yields branch/action views and Q/E/A
  outputs; tags and lengths follow the frame grammar.
- **FUTURE:** queries, explanations, and retry exercise the reconstruction.
- **EXTERNALIZE:** a materializer or service becomes part of the replay path
  and version TCB; it is not free.
- **REALIZE / COGNITION:** latency, availability, physical behavior, and human
  usability are UNKNOWN.
- **TCB:** replay, formatter, capacity, corruption handling, and caches remain
  unclosed.
- **Where now:** boot/query compute, formatter, cache invalidation, and
  operational latency.

### R6 — identity traffic, old outputs, and redundant framing: MAY FORGET

- **DELETE / MERGE / COLLIDE:** identity transitions start and end in the same
  replay state; old outputs are not queryable. Valid `N2` is included.
- **DERIVE / RECOMPUTE:** old output bytes need not be regenerated; future
  outputs rebuild from R1–R3. Accepted framing is deterministic.
- **FUTURE:** the universal residual-future induction, not a sampled future,
  establishes equality under current ZG-1.
- **EXTERNALIZE:** environment memory is permitted private future-policy state
  but cannot be queried implicitly by the candidate.
- **REALIZE / COGNITION:** forensic, privacy, and operational consequences are
  outside the logical contract and UNKNOWN.
- **TCB:** the identity-transition selector must be correct; a false deletion
  loses R1/R2.
- **Where now:** ingestion classification and the explicit decision to provide
  no transcript/rejected-attempt audit.

### R7 — independent relative chronology: conditional MAY FORGET

- **DELETE / MERGE / COLLIDE:** deletion is sound only under the exact commute
  predicate. Same-lineage writes and fork/action placements give immediate
  counterexamples when premises fail.
- **DERIVE / RECOMPUTE:** required causal order is R2; no canonical total order
  derives without an additional specification.
- **FUTURE:** all futures must agree by transition commutation, not merely the
  finite 655-future domain.
- **EXTERNALIZE:** timestamps or source order would reintroduce chronology as
  an external dependency.
- **REALIZE / COGNITION:** concurrent realization and human navigation are
  UNKNOWN.
- **TCB:** independence checker, causal maintenance, renderer, and recovery are
  unclosed.
- **Where now:** commutation proof, partial-order machinery, canonical output
  if later required, and reviewer navigation.

### R8 — index/navigation/canonical partial-order artifacts: UNKNOWN

- **DELETE / MERGE / COLLIDE:** no ZG-1 future observes an internal index, but
  no exact promised artifact exists whose deletion/merge can be classified.
- **DERIVE / RECOMPUTE:** “an algorithm could be added” is not an identified
  reconstruction specification; positive MAY REBUILD is unsupported.
- **FUTURE:** Q/E outputs rebuild, while discovery, search, and navigation
  futures are absent.
- **EXTERNALIZE:** database/search service or human convention moves the
  unspecified behavior and trust elsewhere.
- **REALIZE / COGNITION:** no system, latency, reviewer, or task evidence:
  UNKNOWN.
- **TCB:** any later indexer/canonicalizer/verifier would add an unmeasured
  trusted path.
- **Where now:** future specification authority, indexing algorithm, verifier,
  cache invalidation, performance, and UX.

### R9 — bounded signature and conforming evidence chain: mixed

- **DELETE / MERGE / COLLIDE:** deleting one ordered future can merge D classes;
  deleting required artifact identity invalidates the claimed evidence chain.
- **DERIVE / RECOMPUTE:** the D signature MAY REBUILD from R1–R3 plus the exact
  655-future list; rerun agreement is not independent evidence.
- **FUTURE:** D proves only its declared futures; D1, hidden, and universal
  domains remain UNKNOWN.
- **EXTERNALIZE:** interpreter, extractor, manifest, and artifact capture are
  part of the experiment TCB.
- **REALIZE / COGNITION:** no subject or human validation follows from a code
  run.
- **TCB:** runtime, code extraction, ordering, comparison, and evidence custody
  are unclosed.
- **Where now:** test-domain authority, runner, evidence archive, independent
  capture, and global proof obligations.

### R10 — logical replay state versus ORACLE serialization

- **DELETE / MERGE / COLLIDE:** logical state distinctions reduce to R1/R2
  witnesses; ORACLE's problem is totality, not a pairwise collision.
- **DERIVE / RECOMPUTE:** logical state MAY REBUILD from R1–R3; the named codec
  throws at the valid 9,362-write history and is not a total reconstruction.
- **FUTURE:** the totality witness needs no future request; construction itself
  is undefined beyond U16 item length.
- **EXTERNALIZE:** a different codec would be a different, separately trusted
  mechanism, not evidence for the frozen ORACLE.
- **REALIZE / COGNITION:** no physical codec deployment or usability evidence:
  UNKNOWN.
- **TCB:** length arithmetic, canonicalization, decoder, and corruption checks
  remain unclosed.
- **Where now:** full-domain codec proof and version binding; no representation
  is selected by this audit.

## 8. Complexity-movement ledger

| apparent simplification | logical bytes/distinction removed | where complexity is now |
|---|---|---|
| omit identity traffic and old outputs | transcript detail with no residual ZG-1 future | exact accepted/no-effect ingestion selector; no forensic/audit capability |
| omit actor byte | one derivable byte per accepted effect | causal replay, controller reconstruction, validation, reviewer renderer |
| replace materialized views with replay | duplicated branch/receipt values | boot/query latency, replay engine, formatter, cache strategy, version TCB |
| collapse branch snapshot as a separate category | duplicate accounting, not the F event or attachment | R1 event label plus R2 causal placement; replay derives parent/snapshot |
| collapse action correlation as a separate category | duplicate accounting, not first A/key/attachment | R1 action label plus R2 placement; replay derives receipt/value/explanation |
| remove independent global chronology | order proved not to affect futures | commutation proof, causal relation, topological rendering, concurrency/recovery |
| omit index/navigation artifact | no defined boundary capability | linear replay/scan, latency, missing discovery UX; exact rebuild stays UNKNOWN |
| rebuild finite signature | stored 655-future vector | future-list authority, oracle runtime, comparison, evidence custody |
| rely on frozen contract | per-history rule duplication | exact contract/version availability, deployment binding, parser/verifier TCB |
| use ORACLE materialization | copied replay surfaces/traces | nested codec, update consistency, length proof; frozen codec fails totality |

Nothing in this table makes storage, runtime, operators, humans, or trust cost
zero.

## 9. Contract-relative verdict versus external UNKNOWNs

| layer | verdict | limit |
|---|---|---|
| exact complete-frame grammar | narrow logical PASS | partial frames/restart/progress unsupported |
| complete-body mathematical transition | narrow logical PASS | no subject execution or liveness evidence |
| R1/R2/R3 responsibility necessity | finite witnesses plus derivation boundary | no global minimal representation proof |
| actor and replay-view derivability | narrow logical MAY REBUILD | requires exact R1–R3 and fail-closed replay |
| identity traffic/past-output forgetting | logical MAY FORGET | valid only because ZG-1 has no past-transcript future |
| independent chronology forgetting | conditional MAY FORGET | only after exact all-future commutation proof |
| indexes/navigation/canonical partial order | UNKNOWN | specification missing |
| ORACLE total encoding | FAIL | valid 9,362-write history is unencodable |
| bounded D evidence | predicted/reproduced output, but conforming evidence chain absent | cannot establish subject or universal conformance |
| physical storage/durability/recovery | UNKNOWN | no medium, fault set, or run |
| materially unlike realizations/portability | UNKNOWN | zero instantiated pairs |
| cognition/operations/TCB | UNKNOWN | no measurements or closure |

## 10. First-milestone consequence

The first logical milestone cannot add four independent persistence charges for
event bytes, multiplicity/order, branch snapshots, and action snapshots. The
smallest defended responsibility statement is instead:

```text
R1: accepted labeled effect occurrences, including multiplicity
R2: their required causal placement relation
R3: the exact ZG-1 contract/version/root binding
```

Branch snapshot and completed-action snapshot behavior are forced, but their
information is the relevant `F`/first-`A` label in R1 plus its attachment in
R2. Actor bytes and semantic views may rebuild. Identity traffic, old output,
and proved-independent chronology may forget under the stated conditions.

The frozen document still does not achieve its advertised first milestone:

- it excludes R3 from the partition while relying on it for every rebuild;
- it labels unspecified index/navigation and canonical partial-order artifacts
  MAY REBUILD rather than UNKNOWN;
- its ORACLE candidate is not total on valid ZG-1 histories; and
- its bounded PASS labels lack the evidence chain its own rule requires.

This is a correction to the logical accounting only. It does not select a
representation or prove that any implementation persists R1–R3.

## 11. Final verdict

**FROZEN FIRST MILESTONE: FAIL / NOT ACHIEVED.**

- **MUST SURVIVE:** R1 accepted labeled occurrences/multiplicity; R2 required
  causal placement; R3 exact contract/version/root binding; and, conditionally,
  complete artifacts for any bounded-run evidence claim that remains asserted.
- **MAY REBUILD:** actor bytes; branch/action semantic views; future response
  bodies/frames; and the finite D signature, each only from exact named sources.
- **MAY FORGET:** completed identity-transition traffic, old outputs, redundant
  framing, and relative order of effects proved independent under ZG-1.
- **UNKNOWN:** index/navigation artifacts, canonical partial-order ordering,
  global quotient/minimality, cross-version conversion, subject conformance,
  physical storage/durability/recovery, operations, humans, TCB closure,
  portability, and unlike realizations.
- **ORACLE:** underlying logical state may rebuild, but the frozen ORACLE
  serialization fails totality at the valid 9,362-write witness.

These are logical obligations and omissions, not constructors. Passing them
would still not establish a durable, usable, operational, portable, or
physically realized system.
