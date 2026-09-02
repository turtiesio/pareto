# ZERO GROUND R0.1L — quarantined archive replay

## 0. Authority, chronology, and use of prior work

This replay began only after both R0.1L authorities were frozen.

| artifact | commit | required SHA-256 | observed SHA-256 | role |
|---|---|---|---|---|
| HISTORY-SEED-R01L.md | 6db0c31f096d6c93f343e920b0618b6d7c39da4b | 0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb | 0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb | frozen candidate |
| POSTFREEZE-BREAK-R01L.md | a6b3289018132235f71066e8c0c8282da5e9ba54 | 0744f495f0a229715e1f088c99d96bbbe0b409aaef522e54fb2a8fc516461b9a | 0744f495f0a229715e1f088c99d96bbbe0b409aaef522e54fb2a8fc516461b9a | frozen post-freeze verdict |

The provenance sequence is materially different from the contaminated
candidate-generation sequence found in the preceding round:

1. a fork-isolated builder received only the ZERO GROUND brief and reported
   that it read no repository, Git, existing file, prior attack, archive, or
   advisor;
2. it created one candidate and reported its digest without committing;
3. the candidate was frozen before this builder was exposed to any old attack;
4. a different breaker had no pre-freeze access to the candidate, verified its
   digest before semantic reading, and froze the break;
5. that breaker explicitly disclosed that it retained earlier-round attack
   memory, so its report is independent of the builder but **not
   memory-clean**; and
6. only now was the full prior attack/audit/archive corpus opened for replay.

The builder's isolation is self-attested process evidence; the hashes prove the
bytes and chronology, not private cognition. The breaker therefore did not
claim candidate-only freshness. This full archive report makes no stronger
claim.

Prior work is used only as a source of counterexample shapes. No old state
category, representation, codec, layer, repair, program, or proposed
architecture is imported. An old pressure affects R0.1L only if it can be
restated as:

- exact ZG-1 completed input/output histories;
- one common finite ZG-1 future;
- a contradiction in the frozen ZG-1 document; or
- an explicitly missing physical, cognitive, operational, or trust premise.

The quarantined corpus includes the base A01–A24 transformation index, the
B00–B38 and C1–C6 blind attacks, prior formal/literal/mathematical/persistence
audits, feasibility and archive reports through R0.1K, and prior realization
and runtime audits. Old results are attack indexes, not transferable evidence.
In particular, a run under an older contract, codec, runtime, filesystem, or
machine cannot establish any R0.1L proposition.

No R0.1L experiment-result work was read or used.

## 1. Frozen-break baseline

The post-freeze report remains the verdict authority. It separates three
frozen-document failures from narrow positive results and empirical unknowns.

| current ID | exact R0.1L pressure | type and result |
|---|---|---|
| F01 | At 9,361 repeated accepted WA0x effects the serialized ORACLE branch item is exactly 65,535 bytes; at 9,362 it is 65,542 bytes, so its enclosing U16BE item length raises ValueError even though ZG-1 admits the history. | exact full-domain encoding/functionality **FAIL**, not a pairwise collision |
| F02 | The tables credit bounded PASS from a builder in-memory run, while section 4.4 says missing interpreter digest/version, stdout/stderr, exit status, machine manifest, or extraction artifact is never evidence PASS. | frozen evidence-semantics contradiction; output was later reproduced narrowly, but the required evidence chain remains absent |
| F03 | Generic indexes/navigation/query plans and a hypothetical canonical partial-order ordering are classified MAY REBUILD even though their required exact algorithms or representation specifications are expressly not supplied. | persistence-classification underdefinition **FAIL** |

The break also records these scope boundaries:

- exact complete-frame grammar and the mathematical complete-body transition
  receive narrow PASS;
- PROJECTED3 has a credible full-ZG-1 sufficiency induction;
- the frozen D stdout and displayed D minima were reproduced;
- response progress has no observable bound;
- actor/controller bytes do not create a viewer model;
- the exact contract/version binding remains an external reconstruction and
  TCB responsibility; and
- subject conformance, physical persistence, human validation, global
  minimality, portability, operations, TCB closure, and materially unlike
  realizations remain UNKNOWN or unsupported.

Archive replay does not rename those results.

## 2. Encoding, framing, and exact-target replays

| replay | prior counterexample shape | exact ZG-1 reconstruction | disposition |
|---|---|---|---|
| L-A01 — empty/content and direction collision | Untagged empty values, input/output ambiguity, delimiter concatenation, and sentinel/content collisions. | Compare an empty body, body beginning I or O, absent parent, branch bytes 0/1, and arbitrary invalid content. Input is 49 plus U16 length; output is 4f plus U16 length; absence is ff outside the branch alphabet; accepted sequences have count and per-item lengths. | **PASS for the declared logical grammar.** No marker/content or direction collision survives. This does not prove a subject parser. |
| L-A02 — malformed and future complete body | A parser silently drops, hangs on, or guesses malformed/future input. | Deliver any complete body outside the eight fixed forms, including zero, one, maximum-length, trailing, and future-tag bodies. The mathematical transition returns N5 without changing replay state. | **PASS as a total mathematical rule.** The finite D suite does not execute these edges; implementation and progress remain UNKNOWN. |
| L-A03 — partial/truncated input treated as absence | A bounded prefix plus timeout is conflated with no occurrence. | Send only a prefix of 49 || U16BE(n) || body. ZG-1 says it is outside completed history and produces no output. | **WITHDRAWN/unsupported**, not PASS: partial-frame restart, timeout, and progress observations are outside ZG-1. A physical realization still needs an external close rule if it claims one. |
| L-A04 — public name versus governing specification bytes | One version/name selects different semantics, or private source code supplies a missing wire rule. | Hold PROJECTED3 survivor bytes fixed and vary identity versus swap interpretation, initial root, capacity, or response grammar. Future Q0t or A differs. ZG-1 forbids the variation but stores no version inside PROJECTED3; the realization must bind the frozen authority externally. | Already recorded as an external reconstruction/TCB responsibility beside F03. No in-contract collision exists; cross-version persistence is UNKNOWN. |
| L-A05 — nested length boundary | A locally length-prefixed value exceeds the enclosing width although individual responses still fit. | Root boot plus 9,362 accepted WA0x effects is valid and E0c still fits a frame, but ORACLE's enclosing branch item needs length 65,542. | **FAIL, exactly current F01.** Old framing attacks corroborate the family but add no shorter threshold. |
| L-A06 — hash/label is not target content | A digest, label, or receipt name is asked to reconstruct unavailable source bytes. | PROJECTED3 retains the effect distinctions themselves and derives actors/views from them plus ZG-1. The freeze digest is not used as a decoder. QUOTIENT-D is expressly charged with an external mapping and called unusable generally. | **PASS in the narrow logical proof; UNKNOWN for artifact availability and version selection.** |
| L-A07 — response/error taxonomy mismatch | Two implementations agree on accept/reject while emitting incompatible diagnostic categories. | ZG-1 fixes N0 through N6 precedence, K, V, C, J, !, =, and T at the mathematical boundary. | Formal taxonomy **PASS**; no second implementation exists, so portable diagnostic conformance is UNKNOWN. |

The archive therefore adds no smaller exact encoding failure. F01 is minimal in
accepted-effect count for ORACLE: a write adds the maximum seven bytes to the
nested branch item, and fork or action-receipt variants first overflow at the
same total count of 9,362.

## 3. History, causality, action, and recovery replays

| replay | prior counterexample shape | exact ZG-1 reconstruction | disposition |
|---|---|---|---|
| L-A08 — occurrence versus absence | A current surface deletes whether an accepted effect happened. | Compare B with B,WA0x; future Q0r returns empty versus x. Compare B with B,AA00; future AA00 returns ! versus =. | **PASS as MUST-survive witnesses.** No storage field follows. |
| L-A09 — multiplicity and order | SET loses duplicates; BAG loses causal placement. | WA0x versus WA0x,WA0x then Q0r; and IA01,AA00 versus AA00,IA01 then E00. | **PASS as the frozen bounded collisions.** Global order between proved-independent lineages remains forgettable only under the exact commute premise. |
| L-A10 — request, application, and completion conflation | A requested or acknowledged action is presented as applied or physically completed. | A first authorized AA00 creates a logical receipt and emits !; a later authorized AA00 emits = with the committed bytes. The action body attaches to the exact causal prefix. No physical target fact is claimed. | Logical !/= distinction **PASS**. Physical delivery, exactly-once effect, and durability remain **UNKNOWN**. |
| L-A11 — denied, failed, no-op, and success collide later | A superficial response erases a future-relevant attempt class. | N0–N6 and retries are exact immediate answers but identity transitions. ZG-1 has no past-attempt query; a common future begins from the unchanged replay state. | **PASS only under the residual-future contract.** The traffic is MAY FORGET because audit of rejected attempts is not a capability. Expanding explanation scope would invalidate the verdict. |
| L-A12 — action snapshot floats after evolution | A later interpretation change rewrites an earlier applied action or retry. | Compare WA0x,AA00,IA01 with WA0x,IA01,AA00. AA00 retry and E00 retain the first action's committed value and exact prefix; action receipts do not follow current mode. | **PASS for the exact logical snapshots.** Cross-version physical obligations remain UNKNOWN. |
| L-A13 — branch copy loses its attachment point | A child inherits a later rather than exact fork-time snapshot. | WA0x,FA01,WA0y versus WA0x,WA0y,FA01; future Q1r returns x versus xy. | **PASS as a branch-correlation witness.** Copy-on-write, sharing, or graph storage is not inferred. |
| L-A14 — restart erases accepted action/effect | A completed transaction survives or disappears depending on recovery placement. | Insert any number of completed B transactions after accepted W/F/D/I/A effects; B is an identity transition and PROJECTED3 ignores it. Replay still answers Q/E/retry from the accepted causal distinction. | Formal between-transaction semantics **PASS by induction**. There is no physical restart or durable substrate evidence. |
| L-A15 — crash before/after commit and second crash | Equal caller prefixes hide a physical effect or recovery capability. | Mid-transaction crash, power loss, torn persistence, and recovery requests do not exist in ZG-1. | **UNSUPPORTED/UNKNOWN**, not a capability PASS. Prior physical or recovery results cannot transfer. |
| L-A16 — graceful or irreversible terminal cuts | Request, applied termination, physical halt, and post-terminal behavior differ. | ZG-1 has no terminal request or terminal history. B is a logical boot transaction, not a halt or recovery proof. | **UNSUPPORTED.** No old termination result is imported. |

R0.1L genuinely avoids the prior semantic error of treating application as
physical completion. It does so by defining only a logical boundary emission
and receipt. That precision narrows the claim; it does not supply the omitted
physical capability.

## 4. Viewer, scheduler, query, and witness replays

| replay | prior counterexample shape | exact ZG-1 reconstruction | disposition |
|---|---|---|---|
| L-A17 — one projection mistaken for full history | A limited viewer's equal outputs are used as full-history identity. | ZG-1 has one harness and no viewer input or projection. Bytes A/B control mutations but do not constrain who observes Q/E outputs. | No false projection equivalence is claimed, but multi-viewer behavior is **unsupported**. This is the current break's viewer gap, not a new archive FAIL. |
| L-A18 — hidden nondeterminism or selector | One history/request admits incompatible outputs or an ambient selector chooses a branch. | The complete-body transition is deterministic; F explicitly creates child 1 at its exact prefix. No branch selector, clock, scheduler, or random choice is permitted. | **PASS for mathematical determinism.** Runtime common-mode error remains TCB UNKNOWN. |
| L-A19 — adaptive controller context | An external controller remembers an observation and chooses a different next request while the system calls both choices determined by one history. | A permitted future policy may adapt to future output bytes; the candidate does not claim its authored inputs are history-determined. Its private policy state starts equal and past transcripts are unavailable unless future input carries them. | **PASS by exact scope.** Human/controller rationale and old-transcript audit are not supported. |
| L-A20 — MAY/MUST, hidden carriers, vacuity, and depth | Existential, universal, empty-carrier, and remaining-depth queries are merged or miscounted. | ZG-1 has no modal carrier query or depth/capability counter. Q asks only current raw/interpreted/controller/mode/parent/action bitmap. | **WITHDRAWN/unsupported.** Old MAY/MUST results do not transfer and the absence is not zero query complexity. |
| L-A21 — two canonical witnesses | Equal minimal witnesses alternate under an unbound tie rule. | No boundary operation asks for a canonical causal witness. The D falsifier has a fixed diagnostic pair order; it is not a system capability. | **PASS by claim withdrawal; capability unsupported.** F03 separately catches an unselected future partial-order canonicalizer. |
| L-A22 — bounded quotient label mistaken for decoder | A small class number is treated as sufficient without the transition/evidence mapping. | QUOTIENT-D is explicitly only the 655-future behavior vector; the text charges the 7,240-history table, decoder, invalidation, trust, and opacity. | **PASS as scope discipline.** It does not construct the full quotient. |
| L-A23 — observation truncation becomes historical absence | Empty bounded output is called proof that no matching history exists. | Q0r returns the complete current raw bytes because ZG-1 effect capacity bounds them; there is no observation window or capture omission result. | Logical current-query semantics **PASS**. Physical boundary completeness and response progress are UNKNOWN. |

The archive adds no selector, common-root, or modal-query collision because
ZG-1 does not contain those claims. It also cannot credit their absence as
support for the requested broader viewer/navigation/query system.

## 5. Evolution, derivation, and externalization replays

| replay | prior counterexample shape | exact ZG-1 reconstruction | disposition |
|---|---|---|---|
| L-A24 — silent reinterpretation | New semantics rewrite prior raw/action meaning. | I changes only current mode; raw bytes remain; an action stores its interpreted value and causal prefix; later I does not change the receipt. | **PASS inside ZG-1.** A ZG-2 conversion and rollback remain UNKNOWN. |
| L-A25 — old encoding cannot support a splitting new observer | Evolution asks for a distinction already forgotten. | The seed states that a later contract needs a total conversion and may not merge histories distinguished by its future. No conversion is instantiated. | Correct criterion, empirical result **UNKNOWN**. |
| L-A26 — actor/authority deletion | Removing actor spelling loses authorization or causal evidence. | For every accepted W/F/D/I/A effect, the actor is uniquely the target's then-current controller; replay reconstructs the exact four-byte body and validates acceptance. Rejected attempts are outside later audit. | **PASS as a full-contract derivation.** Parser, replay, and exact version binding carry the work. |
| L-A27 — derivation from current surface | A current state is used to recreate multiplicity, cause, or receipt attachment. | SURFACE fails on B versus DA0B,DB0A under future E0c. PROJECTED3 retains causal effects instead of deriving them from the surface. | **PASS as a bounded falsification and induction premise.** |
| L-A28 — unspecified compiler/index/canonicalizer called rebuildable | A future algorithm is credited as zero or deterministic without exact bytes. | Section 6.2 labels generic indexes/navigation and a possible canonical partial-order ordering MAY REBUILD without supplying the algorithms. | **FAIL, exactly current F03.** Archive adds no smaller history witness because this is a specification/classification defect. |
| L-A29 — hidden manifest/specification/context | Same persisted bytes are interpreted under a different rule, locale, prompt, service, or runtime default. | ZG-1 forbids ambient semantic inputs. PROJECTED3 nevertheless depends on an externally bound exact ZG-1 authority. The candidate identifies the binding and TCB but does not realize or perturb it. | No in-contract collision; external closure **UNKNOWN**. |
| L-A30 — recomputation presented as independent evidence | The same code emits an answer and validates itself. | The builder's embedded program, expected output, and self-report share the candidate authority. Section 4.4 demands a stronger evidence chain but does not contain it. | **FAIL/UNKNOWN, exactly current F02.** A later matching rerun is bounded corroboration, not independence. |
| L-A31 — false mechanism attestation | A stage or success byte is emitted even though the named persistent operation was skipped. | K and ! are logical oracle results, not claims that fsync, power-safe publication, or physical delivery occurred. A realization would need persist-before-success evidence, which is absent. | The old false physical claim is avoided; durable acknowledgement remains **UNKNOWN**. |
| L-A32 — corruption, rollback, and coherent substitution | Invalid stored bytes are rejected but a different valid history is silently accepted. | PROJECTED3 requires invalid triples to fail closed, but has no physical integrity, freshness, writer authority, or rollback evidence. A bit change that forms another valid accepted sequence is outside the logical equality proof. | **UNKNOWN/unsupported** under any physical fault claim. |

The main complexity transfer is explicit rather than erased:

- dropping actor bytes moves work to replay, controller derivation, version
  binding, validation, and reviewer tooling;
- dropping no-effect traffic moves capability scope to the absence of a
  transcript/rejected-attempt query;
- dropping independent global order would move work to causal-relation
  construction and canonical rendering;
- filtering to accepted effects moves trust to exact ingestion and
  persist-before-success ordering;
- rebuilding views moves time and trust to replay;
- omitting indexes moves cost to linear query/navigation and human waiting;
- keeping ZG-1 outside the history moves its exact selection and availability
  to realization/deployment TCB; and
- stopping action semantics at !/= moves every physical delivery fact outside
  the logical claim rather than deleting the physical work.

## 6. Physical, unlike-realization, human, operational, and TCB replay

Prior bounded filesystem, process-kill, corruption, and cross-runtime results
were produced for different contracts and artifacts. They are not R0.1L
evidence.

| pressure | R0.1L status | why no old PASS transfers |
|---|---|---|
| physical persistence and power loss | **UNKNOWN** | no persistent substrate, fault set, cold start, or media observation is instantiated |
| crash atomicity and durable K/! | **UNKNOWN** | ZG-1 excludes mid-transaction crash and supplies no persist-before-output run |
| boundary capture completeness | **UNKNOWN** | BOUNDARY-COMPLETE is only a proposed predicate; no instrumentation artifacts exist |
| execution separation | **UNKNOWN** | boot B is a logical identity transition; volatile-destruction evidence is absent |
| software portability | **UNKNOWN** | no second R0.1L implementation/runtime exchanges PROJECTED3 bytes |
| materially unlike physical realization | **UNKNOWN** | zero realization pairs and no independent physical evidence roots exist |
| human cognition and authoring | **UNKNOWN** | no participants, tasks, time, error, expertise, access, or controlled adjacent case |
| query/navigation usability | **UNKNOWN/unsupported** | fixed Q/E exist, but search/discovery and measured replay latency do not |
| operations | **UNKNOWN/unsupported** | no backup, restore, monitoring, corruption repair, migration execution, availability, or rollback |
| TCB closure | **UNKNOWN** | parser, selector, replay, interpreter, formatter, runtime, storage, evidence capture, and version binding are not independently perturbed |

The R0.1L realization checklist correctly prevents scope transfer, but terms
such as independent root, non-overlapping primary mechanism, independent team,
and evaluator identity are not instantiated as executable evidence. Withdrawal
prevents false PASS; it does not satisfy the unlike-realization, cognitive, or
operational goals.

## 7. Mandatory transformation replay

| operator | archive disposition in ZG-1 terms | where complexity remains |
|---|---|---|
| DELETE | Effect occurrence/operation/target/argument, multiplicity, fork placement, and action attachment have the frozen one-future witnesses. Actor deletion derives successfully. ORACLE totality fails without any deletion. | causal survivor bytes, exact selector, replay |
| MERGE | EMPTY, LAST, SET, BAG, and SURFACE have exact D collisions. Independent cross-lineage order merges only under the stated commute relation. | equivalence proof, causal dependency relation |
| DERIVE | Actor, current views, explanations, and future outputs derive from survivor distinctions plus ZG-1. Generic indexes and canonical partial-order bytes do not. | exact specification, parser, replay, renderer, verifier |
| RECOMPUTE | Logical outputs reproduce; old run results and self-agreement are not independent evidence. Physical cold rebuild is absent. | runtime, source availability, durable medium, evidence chain |
| COLLIDE | Old framing/sentinel collisions are closed by tags and lengths. Current lossy-candidate collisions remain; no PROJECTED3 collision is reconstructed. F01 is a total-function failure. | full-domain encoder proof and finite collision search |
| FUTURE | Q, W, A retry, and E expose all retained local witnesses. Viewer, progress, recovery, modal, terminal, and physical futures are absent or unsupported. | future-contract scope and later evolution |
| EXTERNALIZE | ZG-1 removes ambient semantic inputs but remains an external rebuild authority; filtering, persistence ordering, evidence, and physical effects remain outside the mathematical state. | deployment/version TCB, ingestion, observers, organizations |
| REALIZE | Old realization evidence is contract-specific and cannot transfer. R0.1L supplies zero realizations. | media, runtimes, fault injectors, independent comparators |
| COGNITION | Qualitative byte/burden claims are not a study. Uniform harness visibility avoids one projection bug by omitting viewers. | people, access, renderers, navigation, measurement |
| TCB | Exact code identifies many dependencies but does not close or independently perturb them. F02 demonstrates common-authority evidence risk. | build/runtime/storage/evidence roots and adjudicator |

No simplification is credited without its moved work.

## 8. Persistence-verdict replay

Archive attacks corroborate the following contract-relative information
verdicts without implying a representation.

### MUST SURVIVE

- enough distinction to recover each accepted effect occurrence, its operation,
  target, final argument, multiplicity, and required causal attachment;
- branch-fork snapshot correlation where future child behavior depends on the
  attachment point;
- first-action key and committed-prefix correlation where retry or E can
  observe it; and
- the exact ZG-1 reconstruction authority and version binding somewhere in the
  total system, even if contract-fixed rather than history-variable.

The smallest behavioral witnesses remain those in the fresh break: B versus
B,WA0x followed by Q0r; B versus B,AA00 followed by AA00; the operation,
target, and argument projection pairs; the SET/BAG pairs; and the fork/action
attachment pairs.

### MAY REBUILD

- actor bytes from the then-current controller under exact ZG-1;
- current branch/receipt state and causal explanations by deterministic replay;
- future response framing and bodies from replay state and the exact grammar;
  and
- the bounded D signature from the exact ordered future list and oracle.

These are information derivations, not latency, availability, independent
evidence, or physical recovery results.

### MAY FORGET

- all completed identity-transition traffic, including B, Q/E, invalid input,
  N0–N6 rejections, and action retries, after its immediate response crossed B;
- old output frames under the residual-future rule and absence of a transcript
  query;
- redundant framing whose semantic accepted body is reconstructible; and
- only the global order proved irrelevant by the exact cross-lineage commute
  conditions.

Generic future indexes, query plans, navigation views, and an unselected
canonical partial-order serialization do **not** receive MAY REBUILD. They
remain unspecified/unsupported as frozen in F03.

Changing the contract to expose execution counts, rejected attempts, old
outputs, viewer projections, global chronology, physical delivery, or
cross-version meaning reopens these classifications.

## 9. What R0.1L genuinely avoids

The archive confirms real, independently stated improvements in the frozen
candidate:

1. one exact direction-tagged length grammar replaces delimiter and sentinel
   ambiguity;
2. every complete body has a deterministic mathematical answer, including
   invalid/future bodies;
3. branch and action choices are correlated to exact prefixes rather than an
   ambient selector;
4. actor deletion has a full-contract derivation and validation rule;
5. raw, interpreted, controller, mode, parent, action, and causal explanation
   outputs are distinct;
6. action first emission and retry receipt are distinct, while physical
   completion is expressly withheld;
7. fork-time and action-time snapshots remain observable after later changes;
8. current surface, SET, and BAG are attacked rather than presumed sufficient;
9. bounded D equivalence is not presented as the unbounded quotient;
10. global minimality, physical realization, cognition, operations, and TCB
    closure remain UNKNOWN rather than silently passing;
11. externalized compilers, selectors, replay, indexing, recovery, and trust
    are charged in the total-system table; and
12. the candidate was frozen under a genuine pre-archive builder quarantine.

These improvements do not cure F01–F03 and do not create missing viewer,
progress, recovery, search, physical, or unlike-realization capabilities.

## 10. Does the archive add a new or smaller failure?

**No new frozen failure family and no smaller witness is established.**

- Old nested-length attacks reproduce current F01. Repeated writes maximize
  ORACLE item growth, and fork/action variants overflow at the same 9,362
  accepted-effect count.
- Old self-validation, incomplete evidence, and false-attestation attacks
  reproduce current F02's evidence boundary. They do not create a smaller
  history collision because F02 is a document/evidence contradiction.
- Old missing-canonicalizer, external-index, and derivation-specification
  attacks reproduce current F03. They do not create an exact ZG-1 history pair
  because the claimed future mechanisms were never specified as ZG-1 outputs.
- Old framing, marker, namespace, result-selection, phase, and branch-root
  failures are genuinely blocked by the exact deterministic ZG-1 grammar.
- Old viewer, progress, crash/recovery, terminal, MAY/MUST, physical, human,
  operations, and unlike-realization pressures land in explicit
  UNKNOWN/unsupported scope already recorded by the fresh break.
- No prior representation or old execution supplies a collision in
  PROJECTED3, a physical persistence result, or a global quotient proof.

The archive does sharpen one evidence statement: prior finite realization and
cross-runtime passes are non-transferable because their boundary contracts and
artifacts differ. This is scope discipline, not a new candidate failure.

## 11. Simultaneous total-system archive disposition

| dimension | replay result |
|---|---|
| information preservation | PROJECTED3 logical proof survives; ORACLE full-domain F01 remains; global quotient UNKNOWN |
| persistent state | logical causal responsibilities survive; physical persistence and minimum storage UNKNOWN |
| semantic machinery | exact toy transition survives; parser/filter/replay/version machinery remains charged |
| human cognition | UNKNOWN; no viewer or human protocol |
| authoring | four-byte wire operations are exact; human workflow and error burden UNKNOWN |
| query/navigation | fixed Q/E semantics survive; modal query, search, discovery, and measured latency unsupported |
| runtime | deterministic diagnostic execution exists; response progress and production performance UNKNOWN |
| storage | byte formulas for ACCEPTED4/PROJECTED3 survive; ORACLE codec fails; media/durability UNKNOWN |
| operations | restart semantics are formal only; crash, restore, repair, availability, rollback, and monitoring unsupported |
| TCB | dependencies are named but not closed or independently perturbed |
| evolution | I/D behavior survives; ZG-2 conversion, rollback, and cross-version persistence UNKNOWN |
| portability | exact syntax is not empirical portability; no R0.1L second realization |
| explainability | accepted causal traces survive; rejected-attempt and viewer-relative explanation unsupported |
| information-loss risk | local collision witnesses survive; corruption, coherent substitution, and unseen futures UNKNOWN |
| research process | builder quarantine PASS as attested and ordered; breaker independence qualified by prior-memory disclosure; full archive replay correctly post-freeze |

No row offsets another and no weighted score is used.

## 12. Final archive disposition

The quarantined archive confirms the frozen R0.1L **FAIL** without adding a new
or smaller failure family. It also confirms that R0.1L is a materially cleaner
history experiment than its predecessors: exact frames, deterministic complete
body handling, causal branch/action snapshots, derivable actor bytes, explicit
lossy candidates, and disciplined physical nonclaims avoid many old formal
collisions.

Those successes are contract-relative. The frozen document still overstates
ORACLE's full-domain encoding, credits bounded PASS without its own complete
evidence chain, and assigns MAY REBUILD to mechanisms without identified
specifications. The compact causal projection remains sufficient by a
mathematical ZG-1 induction, but it retains known redundant global order and is
not the quotient or the smallest total system.

Viewer-relative behavior, bounded progress, physical survival between
executions, crash recovery, human verification, operations, portable
execution, global TCB closure, and materially unlike realizations remain
UNKNOWN or unsupported. Old physical and software evidence cannot be borrowed
across contracts.

**FIRST MILESTONE: FAIL / NOT ACHIEVED.**

The surviving information responsibilities and their finite witnesses do not
select a field, record, event, log, graph, object, state machine, storage
medium, program, layer, package, or architecture.
