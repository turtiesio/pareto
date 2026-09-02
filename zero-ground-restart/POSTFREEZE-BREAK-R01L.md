# ZERO GROUND R0.1L — post-freeze boundary-history break

Status: **FAIL for the frozen document as a complete first-milestone
statement.** The compact accepted-effect projection has a narrow mathematical
sufficiency result for the logical ZG-1 transducer, but one advertised encoding
is not total on valid ZG-1 histories, the bounded PASS labels do not meet the
document's own evidence rule, two MAY REBUILD entries lack their required
reconstruction specifications, and several total-system capabilities remain
unsupported or UNKNOWN.

This is a breaker report, not an implementation, architecture, repair, or
storage recommendation.

## 0. Freeze gate, access boundary, and independence limitation

Before semantic reading, the supplied candidate was hashed:

| item | required SHA-256 | observed SHA-256 | result |
|---|---|---|---|
| HISTORY-SEED-R01L.md | 0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb | 0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb | PASS |

The supplied commit identity
6db0c31f096d6c93f343e920b0618b6d7c39da4b was treated only as provenance. It
was not looked up. This task read only the frozen candidate from the
filesystem. The candidate was not available to this breaker before the digest
gate and freeze.

The builder and breaker are different agents, but this breaker inherited
memory of earlier research rounds and attack shapes. It is therefore **not
memory-clean and does not claim candidate-only freshness**. The builder's
clean-room statement is self-attested provenance; the matching digest proves
the bytes examined, not the builder's cognitive or filesystem isolation.
Prior replay was permitted only after the supplied freeze.

The embedded program was executed by extracting its bytes from the candidate
itself. No other repository or Git content was read.

## 1. Verdict boundary

The following verdicts must not be merged:

1. **Frozen byte grammar for input/output frames: narrow PASS.** Complete
   frames are length-delimited, direction-tagged, and unambiguous.
2. **Mathematical ZG-1 transition on a complete request body: narrow PASS.**
   The prose and reference function give one logical result for every complete
   body.
3. **PROJECTED3 sufficiency for the logical ZG-1 state: narrow PASS as an
   induction.** The omitted actor is uniquely recoverable from the controller
   at the accepted effect's causal position.
4. **The declared finite D output: reproduced.** The printed output matched
   the frozen expected block. This is not a conforming evidence-chain PASS
   under section 4.4.
5. **ORACLE as a full-domain encoding: FAIL.** Its nested U16 item length
   overflows on a valid history well before the declared 16,000-event capacity.
6. **The frozen evidence claims and post-attack classification: FAIL /
   underdefined.** PASS is credited without the artifacts the same document
   requires, and conditional or unspecified rebuild mechanisms are placed in
   MAY REBUILD.
7. **Subject conformance, persistence across actual executions, progress,
   durability, operations, human validation, viewer-relative behavior,
   portability, and materially unlike realizations: UNKNOWN or unsupported.**

A failure of one candidate representation does not prove the causal
projection unsound. Conversely, a proof about the causal projection does not
validate the whole total system.

## 2. Exact functionality failure

### F01 — ORACLE cannot encode every valid ZG-1 history

**Type:** exact encoding/functionality FAIL, not a representation collision.

ORACLE serializes each branch as:

    four fixed bytes
    || U16BE(raw length) || raw bytes
    || SEQ(explanation events)

and then places that whole branch byte string into another SEQ item. The outer
item length is therefore restricted to 65,535. For a branch with e accepted
WA0x effects:

    branch-item length = 4 + 2 + e + 2 + 6e = 8 + 7e.

The history consisting of the root boot followed by 9,362 accepted WA0x
requests is valid: 9,362 is below the 16,000-event capacity, its raw and
explanation query responses fit the output frame, and PROJECTED3 remains
encodable. Yet:

    e = 9,361  -> branch item length 65,535 -> ORACLE succeeds
    e = 9,362  -> branch item length 65,542 -> U16BE item length is impossible

Executing the frozen definitions confirmed the boundary:

| accepted WA0x count | branch item length | ORACLE result |
|---:|---:|---|
| 9,361 | 65,535 | encoded |
| 9,362 | 65,542 | ValueError: bytes must be in range(0, 256) |

This witness is minimal within the repeated-write family. A write contributes
the maximum seven serialized branch-item bytes per accepted effect. Receipt
and fork variants first overflow at the same total accepted-effect count, not
earlier.

The finite D corpus reaches only three tail commands, so its ORACLE PASS cannot
detect this full-domain failure. The correct evidence disposition is:

- ORACLE on D: bounded PASS;
- ORACLE as a total persistent encoding for all ZG-1 histories: FAIL;
- any physical storage realization: UNKNOWN.

The failure does not imply a larger length field or any other repair or
representation.

## 3. Evidence contradiction and bounded-run scope

### F02 — the document credits PASS without its own required evidence

**Type:** evidence-semantics contradiction.

The simultaneous-dimension table says FULL, ACCEPTED4, PROJECTED3, ORACLE, and
QUOTIENT-D pass the bounded search. Section 4.4 then says a conforming evidence
run must capture all of:

- the candidate digest;
- exact extracted program bytes;
- interpreter executable digest and version;
- complete stdout and stderr;
- exit status; and
- a machine manifest.

It further says absent or unverifiable artifacts are FAIL/UNKNOWN, never PASS.
The frozen seed contains expected stdout and a builder statement about an
in-memory run, but not that evidence chain. Therefore the seed's PASS labels
are predictions/self-attestation under its own rule, not frozen run evidence.

This breaker independently piped the exact embedded block to python3 -I -.
It exited successfully and reproduced the complete expected output, including:

- 7,240 histories, 285 replay states, 655 futures, and 269 D classes;
- the five displayed lossy-candidate collisions;
- bounded no-collision results for ACCEPTED4, ORACLE, FULL, and QUOTIENT-D;
- deletion of actor byte 1; and
- the displayed survivor, order, and multiplicity witnesses.

That is a narrow output-reproduction PASS. It still lacks the interpreter
digest, machine manifest, independently captured extraction artifact, and
complete evidence chain demanded by the candidate. It cannot retroactively
make the frozen builder assertion a conforming evidence run.

### Minimizer check

The collision routine keeps the first history seen for each bounded
equivalence class within an encoding group. Because the command alphabet is
not in byte-lexicographic order, that optimization is not by itself a general
proof of the claimed lexicographic minimum. A separate exhaustive
representative check over the frozen D domain selected the same pair and first
future for every displayed failure and deletion witness. Thus:

- the displayed minima on D receive a narrow corroborating PASS;
- the routine's strategy is not a proof for D1, a hidden domain, or an altered
  alphabet; and
- global witness minimality remains UNKNOWN.

## 4. Persistence-classification audit

### F03 — two MAY REBUILD entries lack an identified reconstruction spec

**Type:** classification underdefinition.

MAY REBUILD requires deterministic reconstruction from MUST SURVIVE
information plus an identified specification. Most of section 6.2 satisfies
that rule:

- actor bytes are reconstructed by the exact ZG-1 transition;
- current branch and receipt views are reconstructed by exact replay;
- future response frames are reconstructed by the exact response grammar; and
- bounded D signatures are reconstructed by the exact 655-future list and
  oracle.

Two entries do not:

1. “Indexes, caches, query plans, navigation views” are assigned MAY REBUILD
   while the text expressly says no production algorithm is supplied.
   Different index or view definitions produce different bytes and human
   behavior. A generic intention to add an algorithm later is not an
   identified reconstruction specification.
2. A canonical ordering for a possible causal partial-order encoding is
   assigned MAY REBUILD while no partial-order representation or canonical
   topological-sort specification is selected.

These are conditional future possibilities or unsupported mechanisms, not
positive MAY REBUILD verdicts in the frozen partition. This matters because
the document calls section 6 a non-overlapping defended milestone rather than
a design-option list.

### Exact contract/specification responsibility

Every proved rebuild depends on the exact ZG-1 grammar, initial root, transition
order, capacity rule, and version binding. Section 5.5 correctly identifies
that dependence and its TCB, but section 6 excludes it from the partition
because it is not “mutable history information.” The exclusion does not make
the responsibility disappear from the total system. It is an identified
external reconstruction authority whose exact binding must remain available
between executions. No dedicated field follows, but deleting or changing the
binding makes actor reconstruction and every regenerated view undefined or
different.

The candidate does count this externalization in prose. It therefore avoids a
false zero-cost claim, but it has not classified the full between-execution
responsibility inside its advertised milestone.

### Rejected child-collision traffic

The headline says rejected traffic may be forgotten. The numbered MAY FORGET
list names missing branch, unauthorized, capacity, equal controller/mode,
invalid body, and retry cases, but does not explicitly name the valid fork
rejection N2. The adjacent complete history containing F A 0 0 returns N2 and
leaves the replay result unchanged, so the same identity-transition induction
does prove MAY FORGET. This is a finite list omission, not a new semantic
collision, but it prevents the numbered list from being literally exhaustive
without interpreting “rejected” from the headline.

## 5. Narrow persistence results that survive attack

These are information responsibilities, not fields, events, logs, graphs, or
constructors.

### MUST SURVIVE under logical ZG-1

The following distinctions have finite forcing witnesses:

| responsibility | merged histories in request shorthand | shortest displayed future | differing result |
|---|---|---|---|
| an accepted effect occurred | B / B,WA0x | Q0r | empty / x |
| operation byte | B,FA01 / B,AA01 after operation deletion | WA1x | K / N0 |
| target byte | B,FA01,WA0x / B,FA01,WA1x after target deletion | Q0r | x / empty |
| final argument/key byte | B,AA00 / B,AA01 after argument deletion | AA00 | receipt / first emission |
| multiplicity | B,WA0x / B,WA0x,WA0x under set | Q0r | x / xx |
| required causal placement | B,IA01,AA00 / B,AA00,IA01 under bag | E00 | two-event / one-event receipt explanation |
| branch snapshot attachment | B,WA0x,FA01,WA0y / B,WA0x,WA0y,FA01 | Q1r | x / xy |
| completed action/key correlation | B / B,AA00 | AA00 | first emission / receipt |
| committed snapshot attachment | B,WA0x,AA00,WA0y / B,WA0x,WA0y,AA00 | AA00 | x / xy |

The complete framed histories include the deterministic outputs generated by
the oracle. The shorthand does not make the request bodies into a required
storage form.

The exact ZG-1 reconstruction authority is additionally required by every
rebuild. It may be contract-fixed rather than history-variable, but it remains
total-system state/TCB responsibility.

### MAY REBUILD with an identified rule

- The actor byte of an accepted effect rebuilds from the causal prefix's
  current controller and the exact target semantics.
- Current raw/interpreted bytes, controller, mode, parent, causal explanation,
  action bitmap, receipt value, and receipt explanation rebuild by exact
  replay.
- Future response tags, lengths, and bodies rebuild from replay state plus the
  exact frame/response grammar.
- The finite D behavior signature rebuilds from the explicitly ordered 655
  futures and the oracle.

These verdicts establish deterministic information derivability. They do not
establish acceptable latency, an available production decoder, crash-safe
recovery, or independent evidence.

### MAY FORGET under the residual-future contract

- Complete requests whose transition is identity, including boot, queries,
  explanations, invalid bodies, N0/N1/N2/N3/N4/N6 rejections, and action
  retries, may be forgotten after their response crossed B.
- Past output frames may be forgotten because ZG-1 has no transcript query and
  future policies are expressly denied implicit access to an environment-held
  old transcript.
- Redundant past framing may be forgotten when its accepted semantic body is
  losslessly reconstructible.
- The order of two accepted effects may be forgotten only under the exact
  commutation conditions stated in section 6.3: separate existing lineages and
  correlations, no snapshot/control/data dependency, and no explanation
  inclusion.

These are contract-relative results. Expanding the future contract to audit
rejected attempts, execution counts, old output bytes, or global chronology
would invalidate the corresponding MAY FORGET verdicts.

## 6. Root identity, future totality, progress, viewer, and evolution

### Root and branch correlation

The finite experiment has one exact root: the completed boot transaction from
the fixed semantic root. The program generates both input and output frames.
Fork and action correlations are attached to their precise prefix by replay.
No unstated branch selector or cloned query root is needed. This receives a
narrow PASS.

### Complete-body totality versus progress

For every complete body, the mathematical transition is total: valid requests
take the ordered cases, every other complete body returns N5, and one output
body is specified.

The physical interface has no step, elapsed-time, or externally observable
expiry bound. A realization that never emits its promised output leaves the
harness waiting forever, and the text has no timeout occurrence with which to
close that observation. Partial frames, mid-frame restart, concurrent input,
availability, and performance are expressly unsupported. Therefore:

- mathematical request/result totality: narrow PASS;
- bounded operational progress/liveness: UNKNOWN/unsupported;
- subject implementation behavior: UNKNOWN.

The absence of a progress mechanism is not zero runtime or operations
complexity.

### Viewer and authority scope

Bytes A and B implement a single-controller authorization rule, and D evolves
that rule. This is exact toy policy data. It is not authentication and it is
not a viewer model. The single harness sees all query and explanation outputs;
there is no viewer input, permission-dependent projection, redaction, or
viewer-relative explanation.

Consequently authority-transition arithmetic is supported in ZG-1, while
future behavior for multiple viewers is unsupported. Human cognition and
access control cannot receive PASS from the presence of actor bytes.

### Evolution

Mode changes and controller delegation give exact in-contract semantic and
policy evolution. A later contract version, conversion, rollback, unknown
future input meaning, and cross-version persistence are not instantiated.
Version binding is externalized to the realization TCB. Those wider evolution
claims remain UNKNOWN.

## 7. Finite-domain and global-minimality boundary

The D corpus is reproducible and useful for falsification, but it omits:

- complete invalid-body specimens and frame-length edges;
- partial-frame and response-progress behavior;
- capacity and maximum response boundaries;
- long explanations and nested-encoding length boundaries;
- any viewer projection;
- any physical restart/fault evidence; and
- histories deeper than three commands.

F01 is exactly the kind of valid long-history failure D cannot see.

D1 is precisely specified at a useful high level but has no executable block
or evidence run in the seed. Its result remains UNKNOWN. The hidden-bundle
protocol has no committed/revealed bundle or independently rooted identity
evidence, so it is also UNKNOWN.

PROJECTED3's full-contract induction is stronger than a finite D pass for
soundness: replaying the causal projection reconstructs the exact oracle state.
It is still not a minimality proof. The candidate itself establishes that
some retained global order is unnecessary, selects no encoding of the causal
quotient, and does not enumerate all representations or all smaller witnesses.
Neither the conceptual quotient, the five responsibility names, nor the
PROJECTED3 sequence is the smallest total system established by this evidence.

## 8. Mandatory transformation attacks

| attack | disposition | where the complexity is now |
|---|---|---|
| DELETE | Deleting effect occurrence, operation, target, argument, multiplicity, fork placement, or action attachment has the minimized futures in section 5 and FAILS. Deleting actor passes derivation. | accepted/no-effect selection, causal correlation, replay |
| MERGE | EMPTY, LAST, SET, BAG, and SURFACE each merge D-distinguishable histories. Independent cross-lineage order can merge only under the exact commute predicate. | equivalence proof and causal-relation machinery |
| DERIVE | Actor and materialized semantic views derive exactly. Unspecified indexes and canonical partial-order orderings do not yet have a derivation specification. | frozen transition, parser, renderer, verifier |
| RECOMPUTE | Logical answers reproduce from surviving distinctions plus ZG-1. Repetition is not independent evidence, and physical restart recovery is untested. | replay runtime, version binding, durable substrate |
| COLLIDE | The finite suite finds the stated lossy representation collisions. No PROJECTED3 collision is known; ORACLE instead fails total encoding at F01. | collision enumerator, full-domain proof obligations |
| FUTURE | Queries, writes, retries, and explanations expose every retained local witness. Wider viewer, progress, version, and realization futures are absent or UNKNOWN. | future-domain authority and contract evolution |
| EXTERNALIZE | Dropped actor bytes move work into replay; omitted global order would move work into causal relation/canonicalization; the contract specification and version binding remain external reconstruction authorities. | implementation TCB, deployment binding, operators/tools |
| REALIZE | No actual realization, physical fault set, or unlike pair is evidenced. | persistent media, boundary instrumentation, independent observers |
| COGNITION | Byte counts and qualitative burden observations are not a human study. Viewer-specific comprehension is absent. | renderers, reviewers, access, expertise, navigation |
| TCB | Logical correctness depends on parsing, filtering, causal projection, replay, version binding, formatting, corruption handling, and comparison. Physical durability adds unmeasured layers. | code, build/runtime, storage, evidence capture, independent adjudication |

After every apparent simplification, the responsibility remains in the named
location; none is credited as zero complexity.

## 9. Simultaneous total-system disposition

No row is a scalar score and no PASS masks a FAIL or UNKNOWN.

| dimension | disposition | evidence boundary and consequence |
|---|---|---|
| information/distinction preservation | mixed: PROJECTED3 logical soundness PASS; ORACLE totality FAIL; global quotient UNKNOWN | induction versus F01 and unsearched representations |
| persistent state | logical responsibilities partly defended; physical persistence UNKNOWN | no durable implementation or fault run |
| semantic machinery | exact toy transition PASS | replay, filtering, version binding, and corruption handling remain TCB |
| human cognition | UNKNOWN | no population, task, time, error, expertise, or access evidence |
| authoring burden | fixed four-byte W body is measurable; usable authoring UNKNOWN | wire brevity is not human usability |
| query/navigation burden | fixed Q/E behavior exists; discovery/search unsupported | replay is linear; no measured latency or navigation system |
| runtime | asymptotic replay claims are plausible; bounded progress and measured performance UNKNOWN | no response deadline or subject |
| storage | PROJECTED3 byte formula is exact; durability, growth operations, and minimum storage UNKNOWN | full-domain causal count is bounded, no physical substrate |
| operations | UNKNOWN/unsupported | no crash atomicity, recovery run, monitoring, availability, or rollback |
| TCB | identified but not closed or measured | interpreter/build/storage/evidence roots uninstantiated |
| evolution | D/I narrow PASS; contract-version evolution UNKNOWN | conversion and version binding not executed |
| portability | UNKNOWN | byte grammar is portable syntax, not cross-realization evidence |
| explainability | accepted causal traces are derivable; rejected-attempt and viewer-relative explanation unsupported | explanation scope is intentionally narrow |
| information-loss risk | local loss witnesses PASS; corruption and unseen-future risk UNKNOWN | finite D plus proof, no physical integrity or global search |

The toy contract simultaneously touches observation, interpretation, authoring,
query, action, explanation, branch continuation, and authority evolution. It
does not thereby satisfy the broader viewer, physical, operational, cognitive,
or application-semantic objectives.

## 10. Physical and materially unlike realizations

The candidate correctly refuses to infer physical completion, durability,
portable recovery, or unlike-realization equivalence from logical byte traces.
Its proposed evidence checklist is useful as a set of obligations, but terms
such as independent root, non-overlapping primary mechanism, independent team,
and evaluator identity are not reduced to an executable ZG-1 grammar.

There are zero instantiated realizations, zero published fault-set runs, zero
volatile-destruction demonstrations, and zero unlike pairs. Therefore:

- BOUNDARY-COMPLETE: UNKNOWN;
- EXECUTION-SEPARATED: UNKNOWN;
- DURABLE-ACK: UNKNOWN;
- universal TRACE-CONFORMANT: UNKNOWN;
- PORTABLE: UNKNOWN; and
- MATERIALLY-UNLIKE: UNKNOWN.

Scope withdrawal prevents a false physical PASS. It does not satisfy the
requested unlike-realization capability, and it does not make the omitted
observer, storage, fault injector, or organization free.

## 11. Small-witness summary

| order | witness | type | result |
|---:|---|---|---|
| 1 | B / B,WA0x; future Q0r | one accepted occurrence | MUST-survive distinction |
| 2 | B / B,AA00; future AA00 | action receipt | MUST-survive distinction |
| 3 | B,FA01 / B,AA01 under deleted operation; future WA1x | projected-byte collision | FAIL for deletion |
| 4 | B,AA00 / B,AA01 under deleted argument; future AA00 | projected-byte collision | FAIL for deletion |
| 5 | one / two WA0x under SET; future Q0r | multiplicity collision | FAIL for SET |
| 6 | IA01,AA00 / AA00,IA01 under BAG; future E00 | causal-placement collision | FAIL for BAG |
| 7 | 9,362 accepted WA0x | codec totality, no second history required | FAIL for full-domain ORACLE |

F01 is not claimed to be a pairwise representation collision. It is the
smallest established total-function failure in its repeated-write family.
No PROJECTED3 collision was found, and no global smallest witness or total
quotient was established.

## 12. Final result

**FROZEN DOCUMENT: FAIL.**

R0.1L makes meaningful progress: it declares one exact logical boundary,
defines a total mathematical transition for complete request bodies, supplies
small future-distinguishing witnesses, gives a credible induction for dropping
actor bytes, distinguishes bounded search from global equivalence, and keeps
physical and unlike-realization claims UNKNOWN.

It nevertheless cannot receive the first milestone:

- ORACLE is not a total encoding on valid ZG-1 histories;
- bounded PASS labels lack the frozen evidence chain the document itself
  requires;
- two MAY REBUILD entries are only conditional and lack identified
  reconstruction specifications;
- the exact contract/version binding remains an external total-system
  responsibility;
- operational progress and viewer-relative behavior are unsupported; and
- global minimality, cognition, durability, operations, portability, TCB
  closure, and unlike realization remain UNKNOWN.

**FIRST MILESTONE: FAIL / NOT ACHIEVED.**

The surviving result is a contract-relative information-responsibility
statement and a falsification seed. It is not a persistent representation
selection, kernel, architecture, implementation conformance result, physical
system, or proof of the smallest total system.
