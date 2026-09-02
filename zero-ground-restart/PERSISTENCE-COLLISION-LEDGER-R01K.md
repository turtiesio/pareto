# ZERO GROUND R0.1K — Persistence Collision Ledger

Status: **FAIL as a frozen persistence contract; UNKNOWN for any physical
storage implementation.** This is an audit verdict over information
responsibilities. It is not a repair, a storage design, or an inference that
any responsibility needs a dedicated field, table, log, object, or type.

## 0. Provenance and boundary

Only these two frozen inputs were read:

| input | SHA-256 observed |
|---|---|
| `HISTORY-SEED-R01K.md` | `2ae3ac8fda2a78a0b1cd4eef45a8a9d412dc6617b3fff098f4f348855c8eb678` |
| `POSTFREEZE-BREAK-R01K.md` | `9c78c4830db263e5e200923fc51a36edbd1f7f37b70f90d420aae1e0e3ac983b` |

Neither input was altered. No other repository file, Git history, prior seed,
implementation, archive, solution, or builder explanation was read.

This ledger classifies only information needed by the frozen boundary claims.
It does not establish disk persistence, replication, crash consistency,
availability, latency, cost, recovery time, or physical durability.

## 1. Classification rule

The three classifications apply to logical information, not representations.

- **MUST SURVIVE** — deleting or merging the information can change a
  permitted future answer, destroy the exact evidence for a retained verdict,
  or make an older immutable verdict/lineage unverifiable. The information must
  remain exactly recoverable for as long as the relevant claim remains live.
- **MAY REBUILD(RECOMPUTE)** — a materialized result may be discarded only
  when all decisive source bytes, authority/scope associations, order and
  multiplicity survive; the reconstruction is total, deterministic,
  byte-identical, and within every applicable bound; and recomputation is not
  falsely presented as independent evidence.
- **MAY FORGET** — deletion cannot change any admitted future trace, authorized
  exact capture, retained verdict, derivation, supersession relation, or
  evidence claim. Non-influence must be established; lack of a known witness
  is not enough.

An alternate encoding, trie, delta, content-addressed blob, or shared copy can
satisfy MUST SURVIVE if it is lossless. Calling such an encoding a “rebuild”
does not make the underlying distinction disposable.

## 2. Behavioral continuation is not claim evidence

Two separate obligations are carried through this ledger.

1. **Behavioral continuation.** Information survives when a finite permitted
   future produces different answer bytes. This is the candidate's own
   future-observable criterion.
2. **Claim evidence.** Even if ordinary semantic behavior is equal, an issued
   persistent PASS, FAIL, or UNKNOWN is valid only with its exact rules, scope,
   history, evidence, dependencies, question, support, and supersession bytes.
   Losing those bytes invalidates the retained claim rather than necessarily
   changing the subject's next action.

Claim evidence can therefore require more information than an optimized
semantic state. Conversely, retaining a complete semantic state does not
recreate independently acquired evidence or its authority.

## 3. The audit-CAPTURE pressure

The candidate asserts that every distinct K/1 prefix is available to `audit`
through sealed-history CAPTURE and that one CAPTURE distinguishes different
retained occurrence bytes. Under that affirmative claim, let `p` be any valid
prefix and let `x` be one additional exact occurrence. The pair

```text
h0 = p
h1 = p · x
```

has a one-request discriminator:

```text
REQ|audit|scope|CAPTURE|-
```

The returned exact prefix must differ. No semantic summary may merge `h0` and
`h1`, even when the next action, phase label, limited-viewer projection, or
current specification would otherwise be equal. Order and multiplicity are
also observable. This remains true after `TERM-DONE`, because CAPTURE and
EXPLAIN remain admitted there.

The smallest concrete written pair is the observation-open prefix before and
after the exact answer payload:

```text
ANS|audit|s0|OBSERVE|CHUNK|a
```

One audit CAPTURE is the shortest nonempty future claimed to distinguish them.
Deleting that single occurrence makes the histories equal; deleting CAPTURE
removes the claimed behavioral discriminator.

There are two limits on this conclusion.

- The fresh break's F07 shows that the literal post-terminal answer
  `ANS|audit|s1|CAPTURE|CAPTURED|retained` does not actually contain the
  promised prefix bytes. Thus exact CAPTURE is an affirmative contract pressure
  and a finite falsifier, not an executed PASS.
- “Sealed-history CAPTURE” is explicit about retained history occurrences but
  does not unambiguously say that all eight non-history seal members are
  returned. HISTORY is therefore behaviorally MUST SURVIVE under the CAPTURE
  claim. Other seal members are directly behaviorally observable only if
  CAPTURE includes them; independently, they remain MUST SURVIVE as claim
  evidence while a verdict is retained.

Because the candidate keeps audit access after terminality, there is no
declared terminal point at which exact retained history automatically becomes
MAY FORGET.

## 4. Seal-member classifications and smallest futures

No named seal member is unconditionally MAY FORGET while its persistent
verdict is retained. “Materialization” below means one produced copy or derived
view, not the logical information itself.

| seal member | behavioral continuation | claim-evidence duty | classification | smallest future witness and exact conditions | where complexity moved |
|---|---|---|---|---|---|
| `RULES` | A rule difference can change the next INTERPRET, AUTHOR, QUERY, or route. If exact seal CAPTURE includes RULES, even extensionally equal rule bytes remain distinguishable by one CAPTURE. | Derivation leaves cite exact RULES byte ranges. A name, compiler output, or version label is not the source. | **MUST SURVIVE.** Compiled/indexed materializations **MAY REBUILD(RECOMPUTE)** from the exact surviving bytes. | After a captured `CHUNK:a` and before interpretation, one `REQ|audit|s0|INTERPRET|s0:a` distinguishes a rule granting `a` from one not granting it. Exact byte comparison is conditional on an unambiguous rule encoding. | authoritative rule-byte archive, interpreter, compiler cache, proof checker |
| `DECL` | Bounds, viewers, specifications, recovery, terminal behavior, and realization scope select future constructors. Exact DECL occurrences are also part of HISTORY. | A retained verdict's scope is undefined without the exact declaration bytes. | **MUST SURVIVE.** A duplicate seal materialization **MAY REBUILD(RECOMPUTE)** from an authoritative exact `DECL:K/1` occurrence only if association and byte identity are lossless. | One request at a changed bound/viewer/version can differ. The candidate's depth-7 and limited-viewer contradictions prevent a globally exact constructor; conditional audit CAPTURE is one request. | scope registry, parser/router, permission/version adjudication |
| `HISTORY` | Exact audit CAPTURE claims to distinguish every occurrence, order, and multiplicity within one request, including refused requests and post-terminal prefixes. Phase/action futures can also differ. | C/D/E support and PD refer to exact histories and byte ranges. | **MUST SURVIVE.** It cannot be recomputed from a current semantic phase. Lossless shared-prefix/delta materialization is permitted but is still survival. | `p` versus `p·ANS|audit|s0|OBSERVE|CHUNK|a`, then one audit CAPTURE. For semantic rather than capture pressure, F04's one AUTHOR after a refused EVOLVE distinguishes raw-history lifecycle. | lossless prefix archive, request/result correlation, authorized capture service |
| `EVIDENCE` | Evidence availability can change QUERY, CAPTURE, or EXPLAIN from decided to UNKNOWN. Same raw bytes under different authority/interval may have different admissibility. | Raw inline evidence, interval, authority, and adjudication are derivation leaves; a recomputed system answer is not independent evidence. | **MUST SURVIVE** for every retained claim using it, including the exact MISSING state. Serialization may **MAY REBUILD(RECOMPUTE)** only from surviving raw bytes plus every binding. | Holding boundary history fixed, admitted apply-cut evidence versus `MISSING`, followed by `QUERY:q`, yields decided versus UNKNOWN. Exact EVD bytes are unavailable because F02 leaves its fields incomplete. | evidence capture, authority/interval binding, independent adjudicator, archive |
| `DEPENDENCIES` | An influencing dependency can change classification; an unbound one requires UNKNOWN. | Byte closure requires the exact historical dependency content, not its current recomputation or public name. | The logical bound/unbound distinction **MUST SURVIVE**, but F01 makes it **impossible under the frozen transport** for raw content `UNBOUND`. Historical ambient context is not safely recomputable. | Exact collision: both bound raw content and the marker encode as `00 00 00 07 55 4e 42 4f 55 4e 44`; a dependency-sensitive classification requires decided versus UNKNOWN but no byte future can recover which was intended. | disjoint semantic tagging absent from the contract, environment capture, TCB inventory |
| `QUESTION` | MAY, MUST, physical, application, and time-scoped questions can have different answers over the same evidence. If seal CAPTURE includes QUESTION, exact wording is directly visible. | A verdict without its exact obligation and quantifier has no retained meaning. | **MUST SURVIVE.** A materialization **MAY REBUILD(RECOMPUTE)** from a surviving exact, one-to-one bound request only if the mapping is canonical and byte-identical. | Over `{+,+,+,-,?}`, exact question bytes for MAY(q) and MUST(q) require TRUE and FALSE. The candidate's common-root F03 prevents an exact shared-root execution but not the information distinction. | request/question binder, quantifier evaluator, proof presentation |
| `SUPPORT` | Ordinary action behavior may be unchanged by deleting support, but authorized explanation or exact seal CAPTURE may differ. | Every retained verdict requires C, D, or E support with exact ranges/tree and minimization scope. Deletion makes the verdict unsupported, not silently still true. | **MUST SURVIVE** for an issued verdict. It **MAY REBUILD(RECOMPUTE)** only if the complete finite domain and all leaves survive and the rerun yields byte-identical globally minimized support; those conditions are not established for R0.1K. | The smallest claim witness needs no subject action: delete SUPPORT and validate the same seal; the verdict becomes unissued/UNKNOWN. A one-request EXPLAIN/CAPTURE witness is conditional because exact support output is not defined. | global minimizer, proof checker, canonicalizer, support archive |
| `SUPERSEDES` | No ordinary semantic discriminator is defined. If exact seal CAPTURE includes it, `NONE` versus a predecessor digest differs in one request. | It binds a new immutable seal to an older verdict, which the candidate says remains what it was. Digest text alone does not preserve the older seal. | **MUST SURVIVE** for exact seal identity and lineage. The digest materialization **MAY REBUILD(RECOMPUTE)** only from the exact older seal and a bound digest algorithm/format; neither algorithm nor durability is supplied. | Conditional one-request audit CAPTURE of otherwise equal seals with `NONE` versus predecessor digest. Without full-seal CAPTURE, the duty is claim lineage, not demonstrated behavior. | old-seal archive, digest/canonicalization authority, lineage verifier |

## 5. Repeated declarations, evidence, and authorities

Repeated bytes do not imply one logical occurrence.

### 5.1 Repeated declaration content

Each leaf begins with `DECL:K/1`, and identical declaration content may recur
across seals. The common content blob may share a physical representation, but
each logical occurrence's history position, direction, authority, association
to a seal, and multiplicity MUST SURVIVE. Otherwise audit CAPTURE merges two
prefixes or D support byte ranges point at a different occurrence.

The smallest conditional future is one audit CAPTURE on histories differing by
one repeated DECL occurrence. If CAPTURE does not expose declaration
occurrences, a request whose bound/viewer/version rule differs is the semantic
future. The candidate does not supply an exact authority for ordinary CUTs and
does not establish an exact full-seal CAPTURE, so the global byte witness is
unsupported rather than PASS.

Complexity moves from repeated inline text to lossless association and
occurrence accounting. Deduplication may reduce copies; it may not erase
identity, order, authority, or multiplicity.

### 5.2 Repeated evidence content

Two acquisitions can have identical raw evidence bytes but different
authorities, intervals, adjudication rules, realization scopes, or history
positions. Those associations MUST SURVIVE separately. Merging them can turn
UNKNOWN into a false decided answer, reuse one realization's fact in another,
or invalidate a range-addressed derivation. A shared raw-byte materialization
is allowed only when every logical acquisition and binding can be reproduced
exactly.

Recomputation of the system answer is not reconstruction of independent
evidence. Repeating an acquisition creates new evidence and, under the
candidate, a superseding seal; it does not rewrite the old evidence item.

The smallest semantic future is a single evidence-dependent QUERY from two
otherwise equal seals in which the required authority is present in one and
missing in the other: decided versus UNKNOWN. F02 prevents an exact EVD byte
pair, so only the responsibility—not its frozen serialization—can be
classified.

### 5.3 Repeated or missing authority

An authority label alone is not an authority fact. Viewer authority, evidence
authority, clock authority, recovery adjudication, and physical adjudication
must remain bound to the exact occurrence/evidence they authorize whenever
they affect an answer. They cannot be derived from matching payload content.

The `u` leaf demonstrates the logical distinction: captured token text plus a
missing observation authority yields UNKNOWN rather than authorization. That
distinction is MUST SURVIVE. Its exact serialization is not constructible, and
the `MISSING` sentinel has the same untagged-domain concern identified beside
F01.

Complexity moves to authentication, acquisition provenance, and the TCB. Their
physical correctness remains UNKNOWN.

## 6. DELETE/MERGE/DERIVE/RECOMPUTE/COLLIDE audit by seal member

The cells classify the named mutation, not a proposed implementation.

| member | DELETE | MERGE | DERIVE | RECOMPUTE | COLLIDE |
|---|---|---|---|---|---|
| RULES | Removing decisive bytes makes derivation UNKNOWN or changes a future interpretation. | Extensionally different rules can share a name but diverge on one INTERPRET/AUTHOR. | A compiled result or paraphrase is not the exact source unless reversibility is proved. | Derived indexes may rebuild; historical rule bytes may not be fetched from an ambient current version. | Same version/name with different content is not identity. |
| DECL | Removing scope makes affected routing/verdict UNKNOWN. | Different bounds, viewers, or recovery rules cannot share one declaration identity. | Public `K/1` or selected fields do not derive omitted declaration bytes. | An exact duplicate may rebuild from an authoritative retained occurrence; ambient defaults may not. | Same `id` with different map bytes is a context collision. |
| HISTORY | Deleting one retained occurrence fails conditional one-request CAPTURE and may change phase. | Equal phase labels/current outputs do not merge ordered prefixes. | A current-state summary does not derive exact order, multiplicity, refusals, or expiry. | Only another lossless exact source suffices; replay is not proof of the historical occurrence. | Same phase/branch/public name can cover future-distinct histories. |
| EVIDENCE | Deleting a required item yields UNKNOWN, never negative fact. | Equal raw bytes cannot merge acquisitions with different authority/interval/scope. | Subject assertions, digests, or names do not derive independent raw evidence. | Reacquisition is new evidence/new seal, not restoration of the old item. | Untagged MISSING/raw-MISSING and shared evidence names risk collisions. |
| DEPENDENCIES | Deletion must become UNBOUND/UNKNOWN. | F01 merges bound raw `UNBOUND` with the unbound marker exactly. | Hash, label, or current value does not derive exact historical influence bytes. | Historical ambient state is not safely recomputable after context change. | F01 is zero-byte-difference semantic collision; public version collisions add others. |
| QUESTION | Deletion leaves a verdict without meaning. | MAY and MUST cannot merge even when wording/result happens to match. | A display label does not derive exact obligation/quantifier bytes. | It may rebuild only from a surviving injectively bound exact request. | Same short name `q` can denote different scopes or time bounds. |
| SUPPORT | Deletion invalidates the persistent verdict. | Two supports for one result may differ in minimality, viewer, evidence, or explanation. | Self-produced conclusion text is not support; physical claims cannot be derived without evidence. | Exact rerun is conditional on a closed domain and is not independent evidence. | Canonical-name/tie collisions require NONUNIQUE or bound tie bytes. |
| SUPERSEDES | Deletion erases declared lineage from the current seal. | Two predecessors cannot merge by a public label or unspecified digest. | A digest alone does not derive the old immutable seal. | Digest may rebuild only with exact predecessor and bound algorithm; unavailable here. | Unspecified digest algorithm/format prevents collision and identity claims. |

Transfer summary: DELETE moves work to evidence reacquisition or makes the
claim UNKNOWN; MERGE moves it to proof of future equivalence; DERIVE moves it
to a reversible proof checker; RECOMPUTE moves it to exact surviving sources
and a bound canonicalizer; COLLIDE moves it to disjoint identities and
authority/context binding. None deletes the information responsibility.

## 7. FUTURE/EXTERNALIZE/REALIZE/COGNITION/TCB audit by seal member

| member | FUTURE | EXTERNALIZE | REALIZE | COGNITION | TCB | where complexity moved |
|---|---|---|---|---|---|---|
| RULES | One INTERPRET/AUTHOR can expose changed semantics; conditional CAPTURE exposes changed bytes. | Ambient interpreter/spec lookup that changes a result belongs in dependencies. | Same rule bytes do not establish physical equivalence. | Human validation bound is withdrawn. | Interpreter, canonicalizer, and rule authority are unclosed. | rule archive, interpreter, proof checker |
| DECL | One bound/viewer/version-sensitive request can expose a change. | Locale, search path, selector, or permission default cannot override the seal. | Realization scope text does not prove a realization. | Scope comprehension is unmeasured. | Boundary/permission/clock authorities are unclosed. | scope binder, router, authorization service |
| HISTORY | One audit CAPTURE is the claimed universal local discriminator; semantic futures also exist. | Capture omission must become unavailable/UNKNOWN, not a shorter history. | A boundary history does not transfer physical facts. | Reviewing arbitrary exact prefixes has no burden claim. | Capture source and prefix encoder remain trusted. | lossless archive, capture authority, correlator |
| EVIDENCE | One dependent QUERY/EXPLAIN changes decided/UNKNOWN. | Removing capture or adjudicator context cannot become absence. | Evidence is realization-specific; reuse is forbidden. | Human adjudication accuracy/time is UNKNOWN. | Observer, clock, permission, and adjudication are unclosed. | independent evidence pipeline and archive |
| DEPENDENCIES | One classification/K-CLOSE run can expose a changed influence, except F01 destroys the encoded distinction. | This is the dependency duty itself; unknown influences prevent closure. | Influences can differ per realization. | Discovering all influences has no bound. | Global perturbation surface is expressly UNKNOWN. | hermetic environment capture and TCB inventory |
| QUESTION | One evaluation can separate MAY/MUST/time/physical scope. | Controller/selector context cannot silently change the quantifier or carrier set. | Physical questions require per-realization predicates/evidence. | Quantifier/vacuity comprehension is unmeasured. | Parser, carrier generator, and adjudicator are unclosed. | exact query binding and evaluator |
| SUPPORT | One authorized explanation or full-seal CAPTURE may expose support; claim validation needs no subject future. | Canonicalizer/tie/search context must be bound or result UNKNOWN. | Physical support cannot cross realization. | Local proof-checking burden is withdrawn. | Minimizer, range checker, canonicalizer, and oracle are unclosed. | proof engine, artifact archive, reviewer tooling |
| SUPERSEDES | Conditional full-seal CAPTURE exposes NONE/digest; no ordinary semantic query is defined. | Hash/canonicalization/archive context can change lineage. | One machine's predecessor does not prove another's state. | Lineage verification burden is unmeasured. | Digest algorithm, canonicalizer, and archive are unclosed. | predecessor retention and lineage verifier |

REALIZE, COGNITION, and TCB columns intentionally do not produce PASS. The
candidate instantiates no materially unlike realizations, makes no human-local
burden claim, and withdraws TCB closure.

## 8. MAY REBUILD(RECOMPUTE) boundary

The following materializations may be discarded and rebuilt only under all
listed conditions:

| materialization | conditions for MAY REBUILD(RECOMPUTE) | current R0.1K disposition |
|---|---|---|
| parsed/canonical view of RULES or DECL | exact authoritative source bytes, pinned total parser/canonicalizer, byte-identical result | UNKNOWN because grammar/canonicalizer execution is absent |
| router phase or current semantic index | exact HISTORY survives; predicate/result matching is total and deterministic | FAIL as frozen because F04 phase predicates disagree after a refusal |
| query result | RULES, DECL, HISTORY, EVIDENCE, DEPENDENCIES, and QUESTION survive; finite carrier set is constructible; no new evidence is claimed | UNKNOWN/FAIL because `P_K`, common roots, and depths are not constructible consistently |
| SUPPORT | all exact leaves and complete finite search domain survive; global minimum is rerun; result bytes are canonical | UNKNOWN; no enumeration evidence and F02/F08 block the domain |
| duplicate DECL/QUESTION serialization | one authoritative exact source and its seal/history association survive; mapping is injective | conditional only; no implemented proof |
| SUPERSEDES digest | exact predecessor seal plus bound digest algorithm/format survive | UNKNOWN; algorithm/format and old-seal durability are absent |
| captured/evidence serialization | raw bytes plus authority, interval, adjudication, order, occurrence identity, and scope survive | conditional; EVD grammar is incomplete |

Recomputing a verdict is not independent evidence. Repeating an observation or
physical acquisition creates a later fact and, if admitted, a superseding seal;
it cannot reconstruct the earlier acquisition interval or authority.

## 9. MAY FORGET boundary

Within a retained R0.1K seal and the claimed audit-CAPTURE interface, none of
RULES, DECL, HISTORY, EVIDENCE, DEPENDENCIES, QUESTION, SUPPORT, or SUPERSEDES
is unconditionally MAY FORGET.

The following information may be forgotten only when it is outside every seal,
retained prefix, support range, authority association, and dependency, and is
proved not to influence any admitted answer:

- compiled-rule caches, parsed indexes, sort caches, search queues, and global
  minimizer worklists after any required canonical artifact is retained;
- process-local display formatting, object identities, and tie preferences
  that do not influence output bytes or claimed canonicality;
- redundant physical copies after exact logical bytes, associations, order,
  and multiplicity remain recoverable elsewhere;
- internal implementation detail that never crosses the boundary and cannot
  influence a verdict, progress result, selector, recovery, or explanation;
- silence that was never converted into an occurrence, and raw timing detail
  not used by an expiry/evidence/dependency claim;
- physical/simulator facts not admitted as evidence and not used for any
  physical proposition.

Proving non-influence may itself require TCB knowledge. Because TCB closure is
UNKNOWN, these are conditional MAY FORGET classes, not evidence that a concrete
system safely forgot them.

Abandoning a verdict and every future audit/lineage claim about it could remove
its claim-evidence duty, but that is outside the candidate's retained-verdict
claim and cannot be used to justify forgetting while still presenting the
verdict.

## 10. What cannot be classified from the frozen bytes

The following remain impossible to close rather than presumed safe:

1. **All-prefix minimization.** F02 makes ordinary CUT/EVD expansions and
   `APPLICATION-UNRESOLVED` nonfunctional. The §7.3 mutants are not exact.
   Therefore `P_K`, `Pairs(P_K)`, exact PDs, and the claimed C/E ledger cannot
   be generated.
2. **A global MAY FORGET quotient.** Without constructible `P_K` and its exact
   futures, no audit can prove that an unlisted pair of prefixes is safe to
   merge or forget. Local witnesses prove MUST SURVIVE; missing witnesses do
   not prove MAY FORGET.
3. **Exact CAPTURE outputs.** F07's literal `CAPTURED:retained` conflicts with
   the claim to return original bytes. It is unknown whether non-HISTORY seal
   members are behaviorally exposed.
4. **Bound/unbound dependency recovery.** F01 maps two logical states to the
   same exact bytes. The logical distinction is MUST SURVIVE, but no byte-only
   persistence mechanism can recover it under the frozen transport.
5. **Exact authority/multiplicity witnesses.** Missing CUT authorities,
   incomplete EVD fields, and absent delimiter rules prevent exact global
   histories for repeated declaration/evidence cases.
6. **Recompute closure.** Global witness minimality, canonicalization, parser
   totality, and dependency perturbation were not executed. A recomputed match
   would not by itself prove correctness.
7. **Physical storage and durability.** No crash-consistent medium,
   availability boundary, retention period, replica rule, or recovery-time
   evidence is supplied.
8. **Physical and unlike realizations.** Completion, physical recovery,
   physical termination, portability, and cross-realization evidence remain
   UNKNOWN.
9. **Human verification.** Time, expertise, access, comprehension, and review
   reliability remain UNKNOWN.
10. **TCB closure.** Capture, authority, interpreter, canonicalizer,
    minimizer, digest, clock, storage, and adjudication trust remain UNKNOWN.

## 11. First-milestone consequence

The first persistence milestone cannot be “recover the current semantic phase”
or “recompute the current answer.” The earliest claimed milestone must retain
or losslessly reconstitute the exact audit-visible prefix across expiry, crash,
evolution, recovery, and `TERM-DONE`, and must retain the exact seal evidence
needed for every verdict it continues to present.

The minimal milestone breaker is:

```text
h0 = p
h1 = p · ANS|audit|s0|OBSERVE|CHUNK|a
future = one audit CAPTURE, repeated after TERM-DONE
```

A milestone that recovers both as merely “observation expired/terminal” merges
an exact retained occurrence and fails the candidate's CAPTURE pressure. A
milestone that returns the same literal `CAPTURED:retained` for both also fails
F07.

The milestone cannot currently receive PASS: the exact occurrence grammar and
`P_K` are not constructible, F01 loses a required dependency distinction, and
the exact CAPTURE payload is contradictory. That is a specification-level
**FAIL** and an implementation-level **UNKNOWN**, not a recommendation for a
particular representation.

## 12. Final persistence verdict

- The logical content and binding of every named seal member is **MUST
  SURVIVE** while its persistent verdict remains issued.
- Derived indexes, duplicate materializations, a support rerun, and a
  supersession digest are **MAY REBUILD(RECOMPUTE)** only under the explicit
  exact-source, canonicality, completeness, authority, and bound conditions in
  this ledger. The frozen candidate does not establish most of them.
- Only non-influencing, non-evidentiary, non-captured intermediates and
  redundant copies are conditionally **MAY FORGET**. No named seal member and
  no audit-visible history occurrence is unconditionally forgettable.
- F01 makes one MUST-SURVIVE distinction unrepresentable, while F02/F07/F08
  prevent complete prefix/capture enumeration. The frozen persistence contract
  therefore **FAILS**.
- Physical storage, durability, operational feasibility, unlike realizations,
  human cognition, and TCB closure remain **UNKNOWN**. Passing this logical
  ledger would not establish any of them.
