# ZERO GROUND R0.1K — Quarantined Archive Replay

## 0. Authority, quarantine chronology, and scope

This replay began only after the independent fresh break was frozen.  The two
authorities are:

| artifact | commit | SHA-256 | role |
|---|---|---|---|
| `HISTORY-SEED-R01K.md` | `c01da738b38f65868e5c8af17d4823d2bc3f07a7` | `2ae3ac8fda2a78a0b1cd4eef45a8a9d412dc6617b3fff098f4f348855c8eb678` | frozen candidate |
| `POSTFREEZE-BREAK-R01K.md` | `709faefb494f1273d7e32b6b1460ce7ce7b8b37b` | `9c78c4830db263e5e200923fc51a36edbd1f7f37b70f90d420aae1e0e3ac983b` | fresh candidate-only verdict |

The chronology is:

1. the candidate was frozen at `c01da73...`;
2. a distinct breaker read only the frozen candidate and the blind attack pack,
   recorded the candidate hash before reading, and produced the fresh **FAIL**;
3. the fresh report was committed at `709faef...` before archive access;
4. only then were the prior ZERO GROUND audit, feasibility, and archive reports
   admitted as quarantined counterexample shapes; and
5. this replay reconstructs those shapes only in K/1's boundary-history terms.

The quarantined sources were the `ARCHIVE-REPLAY*.md` reports through R0.1J,
the `FEASIBILITY-AUDIT-R01*.md` reports and run-boundary supplement, and the
prior formal, literal-spec, mathematics, unified-quotient, and realization
audits.  No prior representation, state ontology, repair, mechanism, or
proposed architecture is inherited.  The older nouns are not treated as K/1
objects; only the representation-independent collision shape is replayed.

The earlier builder-side draft advisory was also admitted only as an attack
index.  It read a pre-final candidate with SHA-256
`348ce5805d591df833810858ad1833e49e23c62511ecad8a84ea3b45420f7831`.
It was pre-freeze advice, not the mandatory fresh break and not an authority on
the final bytes.

Neither frozen authority was edited.  This report is the only replay artifact
created.

Verdicts in this report mean:

- **PASS**: the particular old formal contradiction has one answer under the
  frozen K/1 rules.  It is never an implementation or architecture verdict.
- **FAIL**: the replay reaches an exact finite K/1 contradiction or a claimed
  byte construction that is not a function.  Fresh IDs identify already-frozen
  failures.
- **UNKNOWN**: evidence, execution, closure, or an independently adjudicated
  premise needed for PASS is absent.
- **WITHDRAWN**: K/1 expressly makes no such capability claim.  Withdrawal is
  not a capability PASS; any empirical proposition behind it remains UNKNOWN.

No physical, human, or TCB obligation receives PASS in this replay.  No scalar
score, percentage, weight, or rank is used.

## 1. Fresh-break baseline

The fresh report is the verdict authority.  Archive replay does not reopen or
rename these failures:

| fresh ID | smallest frozen K/1 pressure | result |
|---|---|---|
| F01 | marker `UNBOUND` and bound opaque ASCII content `UNBOUND` both encode as `00 00 00 07 55 4e 42 4f 55 4e 44` | **FAIL** |
| F02 | `OCCURRED:R` admits at least `CUT|corpus-driver|OCCURRED|R` and `CUT|subject|OCCURRED|R`; other abbreviations lack direction fields or escaping | **FAIL** |
| F03 | `r_MAY=<DECL>` while `r_MUST=<DECL,REQ MAY,ANS TRUE>` in the written sequential transcript | **FAIL** |
| F04 | `REQ OBSERVE; REQ EVOLVE; ANS EVOLVE BUSY observation` still satisfies raw `evolution-pending`; a future AUTHOR is misrouted | **FAIL** |
| F05 | `REQ ATTEMPT; CUT OCCURRED` has no terminal ANS, so the three-step rule requires `EXPIRE:operation` that the exact script omits | **FAIL** |
| F06 | from the declared singleton cut immediately before RECOVER, `q` is reached after one delivered request, not six | **FAIL** |
| F07 | every literal post-terminal answer is `ANS|audit|s1|CAPTURE|CAPTURED|retained`, so it cannot itself contain differing retained `a` and `b` bytes | **FAIL** |
| F08 | directionless occurrences and category-only mutants prevent construction of exact `P_K`; the promised E side of the ledger is not materialized | **FAIL** |
| F09 | `depth.full="6"` routes depth seven out of envelope, while §7.3 and prediction 13 require depth-seven TRUE | **FAIL** |
| F10 | the same `(h,REQ OBSERVE)` admits CHUNK `a` and CHUNK `b`, contradicting the claim that `N(h,r)` is one unique result | **FAIL** |
| F11 | `REQ|limited|s0|OBSERVE|-` routes to `N`, but every nonempty N observation exposes a token forbidden to `limited` and no redacted constructor exists | **FAIL** |

F01 is already a zero-encoded-difference collision and therefore cannot be
improved by an archive witness under the declared minimization order.  The
archive can add a distinct failure family, or a smaller witness within F02–F11,
only if it survives reconstruction outside the rows above.

## 2. Disposition of the pre-freeze draft advice

The final candidate materially changed after the advisory hash.  The following
separates fixed draft findings from final collisions; it does not credit the
advisory as fresh evidence.

| draft pressure | final R0.1K disposition |
|---|---|
| `APPLY`/`APPLIED` spelling and epistemic predicate mismatch | **Fixed formally.** §5 now defines `Apply(R@s0)` as the semantic fact, names `APPLIED:R@s0` as positive evidence, and makes missing application capture UNKNOWN. |
| five carriers queried only after leaf divergence | **Partly fixed, then freshly broken differently.** Queries were moved before leaf-specific observation, but their two sequential requests still have different exact roots: fresh F03. |
| undefined one-step depth and overlong `a` carrier | **Partly fixed, then freshly contradicted.** Delivered requests are counted and isolated leaf lengths are stated, but the recovery-cut breaker changes the origin (F06), depth seven conflicts with the envelope (F09), and the sequential MUST request changes MAY depth (F03). |
| `a`/`ab` evolution while application was open and `u` termination while unresolved | **Fixed in the written order.** Completion expiry precedes evolution in `a/ab`, and `APPLICATION-UNRESOLVED` closes `u` before evolution.  This does not cure operation closure F05. |
| missing request-pending router rows and nonpersistent crash predicate | **Substantially fixed.** `action-requested`, zero-chunk `observation-open`, `synchronous-pending`, `recovery-pending`, and latest-crash predicates were added.  A refused request still poisons later first-match routing: F04. |
| answer cardinality without a progress bound | **Fixed as a declared driver-step bound.** Exact ATTEMPT/EVOLVE/TERMINATE scripts do not satisfy its terminal-ANS rule: F05.  Wall-clock, delivery, and subject liveness remain UNKNOWN. |
| incomplete phase labels and absent capture/response-closure families | **Expanded formally.** The final tables add the missing labels and same-label pair rule.  Exact `P_K` and the E ledger remain unconstructible: F08. |
| directionless request/answer use and prose placeholders | **Partly fixed.** Four direction-tagged forms and a literal declaration payload were added.  Missing CUT authorities, untyped `APPLICATION-UNRESOLVED`, missing ANS payloads, `|` ambiguity, and marker collisions remain F01/F02. |
| deletion-only minimality presented as global minimum | **Fixed as a criterion.** §4.3 now requires enumeration of all smaller tries.  No enumeration is supplied and F02 prevents construction of its alphabet, so actual global minimality remains UNKNOWN and the ledger claim fails through F08. |
| incorrect `ab` deletion explanation | **Fixed.** The final text distinguishes single-token candidates and says deletion from `ab` leaves the other candidate.  `NONUNIQUE` remains conditional on an unexecuted global enumeration. |
| negative physical wording such as `applied-not-completed` | **Fixed.** The final payloads say completion evidence is unavailable and §10 keeps physical completion UNKNOWN. |
| unconditional `K-CLOSE` alternatives | **Fixed at the rule level.** Bound dependencies require invariant bytes and `UNBOUND` requires UNKNOWN.  The byte transport cannot distinguish the marker from bound content: F01. |
| ambiguous “false MUST answer” wording | **Fixed.** §9 now says the failing answer is the incorrect `MUST(q)=true`; the independent physical completion UNKNOWN remains visible. |
| limited viewer mentioned without exact branch bytes | **Not fixed.** Exact explanation payloads were added, but normal limited observation/interpretation/authoring constructors remain absent: F11. |
| post-terminal `CAPTURED:retained` named but not byte-expanded | **Not fixed.** This became fresh F07. |

Thus the final candidate fixed several advisory defects rather than merely
renaming them.  F01–F11 are remaining or newly exposed collisions in the final
bytes, not recycled claims about the earlier advisory candidate.

## 3. Consolidated archive counterexample replay in K/1 terms

Duplicate old reports are consolidated by representation-independent
counterexample.  The source column is an index, not imported ontology:
`A` denotes the base archive A01–A24; `R/B/C/D/E/F/G` denote the corresponding
feasibility generations; `H01–H14` and `I01–I16` denote the consolidated H/I
archive rows; and `J` denotes the prior R0.1J archive/feasibility pressures.

### 3.1 Encoding, evidence, and exact-target attacks

| replay | old pressure index | exact K/1 reconstruction | verdict and relation to fresh break |
|---|---|---|---|
| K-A01 — empty, malformed, truncated, and delimiter-ambiguous input | R-E1/E2; B-F1/F5/F7; C5; D1/D3; F-§2.1; G-§1.3; H malformed framing; I08; A03/A04 | Deliver `ε`, one byte, an incomplete length prefix, and `REQ|audit|s0|QUERY|MAY:q:depth=6|x`.  The last bytes admit either an extra field or an argument containing `|x`; no escape rule chooses. | **FAIL, already F02** for the affirmative exact grammar.  Behavior of a subject decoder remains UNKNOWN.  No smaller witness than F01. |
| K-A02 — presence marker versus legitimate opaque content | C16; I03/I08; J envelope-presence pressure; A04 | Hold every seal byte fixed.  In one case `DEPENDENCIES[k]` is the marker `UNBOUND`; in the other it is bound opaque ASCII `UNBOUND`.  Repeat with missing evidence versus raw ASCII `MISSING`. | **FAIL, already F01.** The `MISSING` replay is the sibling explicitly noted by the fresh break, not a new family. |
| K-A03 — authority, namespace, and association are not encoded | R-F5/E7/E8; B-F2/F3/F6/F9; C7/C9/C10/C13; D3/D14; H07/H12; I03–I05/I08 | Expand `OCCURRED:R`, `APPLIED:R@s0`, `CRASH:...`, or `EVIDENCE:observation-authority:MISSING`.  K/1 supplies no authority default for the CUTs and no complete EVD tuple.  Two authorities therefore produce different bytes for one abbreviation. | **FAIL, already F02.** Viewer authentication and external subject association remain **UNKNOWN** rather than becoming another formal PASS. |
| K-A04 — a hash, name, or label is not the selected target bytes | R-F2/F5; B-F3/F9; C9/C14; D7/D25; F provenance; H/I evidence binding; A08/A10/A11 | Ask post-terminal CAPTURE after leaf `a` and leaf `b`.  Both literal answers are `ANS|audit|s1|CAPTURE|CAPTURED|retained`, although the claimed included targets contain different CHUNK bytes.  A digest or label cannot choose or reconstruct them. | **FAIL, already F07**; missing old-seal retrieval and digest machinery remain UNKNOWN.  The candidate's general inline-evidence rule is a narrow formal safeguard, not storage evidence. |
| K-A05 — independently named byte fields must be framed | B-F8; C5/C8; D1/D3/D13; R-E1; A04 | Substitute the old `a|bc`/`ab|c` shape with two K request tuples whose raw fields contain `|`.  Without escaping, `REQ|audit|s0|QUERY|a|b` has no unique five-field parse. | **FAIL, already F02.** This is the same delimiter defect, not a new collision. |
| K-A06 — captured prefix plus timeout must not become empty | R-F2/F3; B-F8; C1/C2/C4/C8/C17; D9/D10; J timeout failure; A08 | Compare `<REQ OBSERVE, ANS CHUNK a, ANS EXPIRE>` with `<REQ OBSERVE, ANS EXPIRE>`.  The earlier HISTORY tokens differ and K/1's rule retains both CHUNK and EXPIRE, but its later literal `CAPTURED:retained` answer is unable to carry the promised earlier bytes. | **PASS** only for written prefix/expiry co-presence (fresh P08); **FAIL, already F07** for the exact later capture-answer claim.  Physical timeout authority remains UNKNOWN. |
| K-A07 — exact rule/specification content must accompany a public identity | R-E3/E5; B-F3; C11/C13/C23; D8/D25; E5; F/G/H/I specification probes; A01/A11/A12/A15 | Hold `id="ZERO-GROUND-K/1"` fixed and vary one semantic `spec.s0` byte.  The seals differ only if the literal map is actually encoded and bound; the candidate forbids name-only substitution.  Its map-entry grammar and occurrence expansion are nevertheless incomplete. | **PASS** as the narrow no-name-substitution rule; exact construction **FAILS already F02** and external bundle selection/availability remains UNKNOWN. |
| K-A08 — exact replay address and acquisition interval | R-E8; B-F9; C9/C10/C13/C14; D7; H/I manifest binding; A08/A11 | Request evidence for one byte range of `HISTORY` and one range of `EVIDENCE`.  The seal prose requires byte ranges, interval, authority, and adjudication, but supplies no exact evidence-tuple grammar or range-addressed SUPPORT instance. | **FAIL, subsumed by F02/F08** when exact constructibility is claimed; an instantiated replay archive is UNKNOWN. |

### 3.2 Lifecycle, router, continuation, and phase attacks

| replay | old pressure index | exact K/1 reconstruction | verdict and relation to fresh break |
|---|---|---|---|
| K-A09 — request occurrence is not accepted application | R-F1; C18/C20; D13/D14; E2; F action cuts; H01/H02; I01/I11; A16/A17 | Start with `REQ|audit|s0|OBSERVE|-`; deliver `REQ|audit|s0|EVOLVE|s1` and its `BUSY|observation` refusal.  The raw request occurred but evolution was not accepted.  K/1 nevertheless labels the next cut `evolution-pending`. | **FAIL, already F04.** The old request/application distinction was named but not carried by the first-match predicates. |
| K-A10 — output/cut/progress closure is a separate occurrence | C1–C4/C17/C21; D9/D10/D15; E2; F-§2.2–2.5; G STOP; H03; I11; J router | Use `REQ|audit|s0|ATTEMPT|R@s0; CUT|?|OCCURRED|R`.  No terminal ANS closes ATTEMPT under §7.2, so driver step three owes `EXPIRE:operation`; the leaf omits it.  EVOLVE and TERMINATE have the same form. | **FAIL, already F05**, with the CUT authority also F02.  Atomic delivery, durable commit, process launch, and wall-clock completion remain UNKNOWN. |
| K-A11 — refused work must not poison a later phase | C20/C21; D14/D15; H10; I11; J F01; A09 | After the K-A09 refusal, append `REQ|audit|s0|AUTHOR|R`.  The still-open observation row requires `BUSY:observation`; raw `evolution-pending` instead requires `BUSY:evolution`. | **FAIL, already F04.** The archive adds no shorter future; one later request is necessary to expose the wrong phase. |
| K-A12 — terminal request, applied boundary, and boundary-terminal cut | C7/C21; D9/D15; F recovery precedence; G/H terminal crash; I terminal rows; A09/A13 | Compare prefixes ending after `REQ TERMINATE`, after `CUT TERM-APPLIED`, and after `CUT TERM-DONE`; append ATTEMPT.  The table intends TERMINATING, TERMINATING, and TERMINAL-REFUSAL respectively.  The written termination operation itself has no terminal ANS under the progress rule. | **FAIL, already F05** for the exact script.  Boundary phase labels are formally distinct.  Irrecoverable crash, process halt, and physical terminality are **WITHDRAWN/UNKNOWN**, never PASS. |
| K-A13 — occurrence, application, and external completion are different | F action lifecycle; G/H action capture; I13; A16 | Compare a prefix ending at `CUT ... OCCURRED|R`, one ending at `CUT ... APPLIED|R@s0`, and one with only `CUT|completion-observer|EXPIRE|completion-observation`.  Query `q` and the physical completion proposition separately. | **PASS** for the stated semantic separation `OCCURRED`/`APPLIED`/completion-UNKNOWN; exact CUT bytes still **FAIL through F02/F05**.  Physical completion is UNKNOWN. |
| K-A14 — crash/recovery phase identity and remaining work | C6/C7/C21; D10/D14; E2/E4; F-§2.2–2.5; G crash nondeterminism; H09/H13; I01/I12/I13/I16; A08/A09 | Replay K/1 leaves `a`, `b`, `ab`, `n`, and `u` at their CRASH cuts and append RECOVER/QUERY.  Their intended answers differ by captured, applied, denied, and missing-application evidence.  Exact scripts use unspecified CUT authorities, and the singleton depth query changes its root. | **FAIL, already F02/F06/F08.** Additional recovery crashes and corrupt recovery images are WITHDRAWN; physical recovery is UNKNOWN. |
| K-A15 — a hidden path or cache may not change a sealed verdict | C6/C10/C13; D11/D12; E4; F/G hidden-state probes; H/I path-cache; A01/A08/A12 | Run the same byte-identical seal after changing one omitted cache, locale, selector order, or recovery environment.  K-CLOSE requires identical bytes if bound and UNKNOWN if `UNBOUND`. | **PASS** as a conditional rule, but **FAIL already F01** at the bound/unbound transport and UNKNOWN for global dependency closure or any implementation. |
| K-A16 — unsupported future input still needs a bounded classification | R-E5/E10; C5/C17/C20; D31; G malformed/unknown; H/I future grammar; A02/A21 | Deliver a well-formed unknown operation, a known operation under version `s2`, and a 257-octet request.  The prose names `UNSUPPORTED`, `UNSUPPORTED-VERSION`, and `OVERSIZE`; the exact parser/escaping grammar is not a function and no subject run exists. | **FAIL, already F02** for exact bytes; subject decoder behavior is UNKNOWN.  Semantics outside the ten named operations are WITHDRAWN after bounded refusal. |

### 3.3 Viewer, nondeterminism, quantifier, depth, and witness attacks

| replay | old pressure index | exact K/1 reconstruction | verdict and relation to fresh break |
|---|---|---|---|
| K-A17 — one viewer projection is not full-history identity | R-F3; H02/H05; I02/I05/I09/I13; A02/A16 | Compare leaf `a` with leaf `b`.  `limited` explanations may both hide the token, while `audit` CAPTURE or exact histories distinguish `CHUNK:a` from `CHUNK:b`.  The single equivalence quantifies over every viewer. | **PASS** for the abstract non-conflation rule.  The actual `limited` OBSERVE/INTERPRET/AUTHOR routes have no legal exact constructor: **FAIL already F11**. |
| K-A18 — nondeterministic branches need one correlated carrier | G-§1.4; H01/H04/H06; I01/I04/I06/I07/I10; A02/A04/A10 | At the same pre-observation `(h,r)`, compare first answers `ANS ... CHUNK|a` and `ANS ... CHUNK|b`.  There is no preceding selector byte.  Calling `N(h,r)` one unique result merges the two branches; calling it a tree would require an unstated tree codec and branch evidence. | **FAIL, already F10.** Scheduler, replay, and determinism identity are expressly WITHDRAWN; their empirical carriers remain UNKNOWN. |
| K-A19 — MAY, MUST, hidden UNKNOWN, and fail dominance | R-F4/E2; H06; I06; J mixed-manifest; A02/A07 | Over the declared vector `{a:+,b:+,ab:+,n:-,u:?}`, ask `MAY(q)` and `MUST(q)`.  Arithmetic gives TRUE and FALSE.  Separately, an incorrect `MUST(q)=true` is a suite FAIL even while physical completion is UNKNOWN. | **PASS** as finite truth-table arithmetic and fail-dominance rule (fresh P03/P04).  Exact common-root execution **FAILS already F03**; subject support is UNKNOWN. |
| K-A20 — empty-carrier vacuity is not an operational witness | H06; I06; J empty carrier; A07/A20 | Use selector `empty`; ask MAY(q), MUST(q), MUST(not-q), and for a carrier.  The written results are FALSE, VACUOUS, VACUOUS, and no carrier. | **PASS** only for the frozen labels (fresh P05).  Human comprehension is UNKNOWN and the capability is not an operational guarantee. |
| K-A21 — two purported common-root queries must have identical prefixes | H04/H06; I06/I07; J policy-root pressure; A02/A04 | Expand the written common prefix.  MAY is rooted at `<DECL>`; MUST is rooted after the MAY request and TRUE answer.  Their `PD` contains those two occurrences. | **FAIL, already F03.** This is the K/1 reconstruction of older common-policy/domain attacks. |
| K-A22 — depth is relative to the named cut | F/G remaining-horizon probes; H09/H13; I12/I16; J Q7/depth; A02/A06 | From the singleton `a` cut immediately before RECOVER, append `REQ RECOVER`, its answer, then `CUT APPLIED`.  Only one delivered request occurs.  Also submit `QUERY ... depth=7` against `depth.full="6"`. | **FAIL, already F06/F09.** A consumable capability or crash-counted quota is expressly WITHDRAWN; no such capability receives PASS. |
| K-A23 — canonical witnesses require exact alphabet, scope, and global order | R-E1/E6; B-F7; D22–D30; E1/E3; F/G minimization; H07; I03–I08/I15; J canonical order; A04/A06/A10/A23 | Use the two candidate leaves `<CHUNK:a,OCCURRED:R>` and `<CHUNK:b,OCCURRED:R>` for `why-admitted(ab)`.  §4.3 now requires every smaller trie, but F02 leaves the alphabet nonfunctional and no enumeration/support artifact is present. | **FAIL, already F02/F08** for frozen exact-ledger claims; global `NONUNIQUE` and minimality results remain UNKNOWN.  Local pair arithmetic alone passes. |
| K-A24 — ledger generation is not the ledger | R-E5/E6/E9; B-F8; C12/C20; D4–D7/D22/D24/D27/D30; E1/E3; H13; I12/I16; J persistence ledger; A06/A10/A24 | Attempt to materialize `P_K` from five scripts, decoder mutants, withheld-answer cases, and every prefix.  `APPLICATION-UNRESOLVED` lacks a direction rule, CUT authorities are missing, decoder mutants lack exact payload/result bytes, and no set stores nondistinguished E pairs. | **FAIL, already F08.** The archive adds no missing exact member smaller than the directionless one retained by the fresh report. |
| K-A25 — exact prefix difference does not cure an unencoded history | H12; I03; J EncCut; A04/A05 | For already encoded histories, compute their longest common prefix and two ordered suffixes.  The mathematics is unique.  Then try it on `OCCURRED:R`; F02 prevents choosing its bytes. | **PASS** for sequence mathematics (fresh P06); exact corpus application **FAILS already F02**. |

### 3.4 Evolution, derivation, externalization, and realization attacks

| replay | old pressure index | exact K/1 reconstruction | verdict and relation to fresh break |
|---|---|---|---|
| K-A26 — evolution must not reinterpret an authored request silently | R-E3/E5; C18/C23; E5; F latest identity; G stale revision; H01; I old/new fold; A02/A11 | Compare `R@s0` applied before and after `CUT ... EVOLVED|s1`; request an unqualified interpretation.  The rule keeps `R@s0` meaning and returns `TIME-SCOPE-REQUIRED` for the unqualified request. | **PASS** as a bounded semantic rule.  Exact occurrence construction fails through F02/F05 and execution is UNKNOWN.  General migration, rollback, and future versions are WITHDRAWN. |
| K-A27 — DERIVE/RECOMPUTE must retain every source and its machinery | R-F2/F3/E3; B persistence; C15; D16–D21/D24/D28/D29; E4/E5; F over-preservation; G/H/I/J derivation rows; A05/A08/A11/A12/A17/A18 | Delete one D-support range, one exact rule byte, or the retained target of CAPTURE; rerun from the remaining seal.  K/1 says a missing required leaf yields UNKNOWN and a digest/name cannot replace content.  No cold rebuild or range-addressed support instance exists. | **PASS** only as the conservative rule “missing required leaf ⇒ UNKNOWN”; actual derivation, recomputation, and minimum retained information are UNKNOWN.  F07/F08 already cover affirmative byte claims. |
| K-A28 — over-preservation is not proved necessary by a preferred decomposition | D16–D23/D28; F-§2.8; G representation results; A05/A16/A17 | Ask whether any named K/1 occurrence, seal field copy, or implementation field must physically persist merely because the prose names it.  K/1 claims information responsibilities and sealed evidence, not a subject layout, and supplies no implementation deletion experiment. | **WITHDRAWN** as a storage-shape claim; minimal physical storage and deletion remain UNKNOWN.  Passing formalism is not architecture. |
| K-A29 — causal/provenance explanation needs evidence, not a status label | R-F2/E8; C6/C19/C22; D2/D7/D29/D30; F provenance; G/H/I explanation; A03/A08/A14 | Ask `limited` and `audit` why `q` holds after hidden token `a`.  The short X answer says `support=APPLIED` or `basis=HIDDEN`, but no instantiated D support names rule nodes and byte ranges. | **UNKNOWN** for replayable explanation; exact limited routing **FAILS already F11**.  Arbitrary lineage/counterfactual explanation is WITHDRAWN. |
| K-A30 — external controller, capture, selector, manifest, canonicalizer, or environment | R-E3/E4; B-F3; C10/C13/C23; D8/D11/D12/D25; E5; F/G/H/I/J externalization; A01/A09/A11/A12/A15/A20/A21 | Hold a seal fixed; vary one external influence.  If it is bound, verdict/support bytes must remain equal; if unbound, both must be UNKNOWN.  No finite inventory proves all influences found. | **FAIL, already F01** for the marker distinction; otherwise global closure and severing are UNKNOWN.  Determinism/selector identity beyond bound bytes is WITHDRAWN. |
| K-A31 — malformed, counterfeit, replayed, rollback, and second-crash recovery inputs | C5/C6; D6/D10/D12; F recovery-machine crash; G/H/I corruption/replay; A02/A08/A13 | Present a corrupt recovery image, a coherent rollback, or a second crash.  None is a K/1 routed request or admitted leaf under the one-crash abstract envelope. | **WITHDRAWN** from K/1.  Robustness, import validation, rollback protection, and physical recovery remain UNKNOWN, not PASS. |
| K-A32 — physical completion, halt, delivery, power loss, and unlike realizations | R realization limits; C3/C6/C23; D9/D13; E/F/G/H/I/J realization rows; A03/A13/A19/A20 | Replace `completion.evidence="MISSING"` with no new physical observer bytes and ask whether completion, halt, durable delivery, or cross-realization equality occurred. | **UNKNOWN** by §10.  The base abstract boundary makes no such claim.  Scope is **WITHDRAWN**, and no physical proposition receives PASS. |
| K-A33 — human-local verification and authoring burden | R-E9; C11/C22; D3/D4/D23/D24; E/G/H/I/J cognition; A07/A14/A18/A20 | Give a reviewer only the frozen seal, short X text, and the claimed global-minimality duty; ask for bounded time, error, or independent reproduction.  No population, protocol, resource bound, or measurement exists. | **UNKNOWN**.  K/1 expressly withdraws human-burden claims; withdrawal is not a human capability PASS. |
| K-A34 — TCB closure and circular self-validation | R-E3; B-F3; C11/C22/C23; D8/D24/D25; E5; F/G/H/I/J TCB; A03/A09/A11/A12/A15/A19/A21 | Perturb the classifier and validator's shared parser, rule bytes, authority binding, canonicalizer, or driver-progress source while keeping their mutually produced answer/support matched.  No independent oracle or finite perturbation surface is present. | **UNKNOWN** globally; K/1 withdraws TCB closure.  F01 independently FAILS one trust-binding byte distinction.  No TCB PASS is issued. |
| K-A35 — resource counts, search cost, and implementation feasibility | B run-boundary size; D/E/F/G/H/I/J cost and count probes; A07/A20/A23 | Materialize all smaller tries and every `Pairs(P_K)` member, retain inline evidence/support, and measure storage/runtime.  The candidate supplies bounds on leaf/request counts but no executed enumerator, archive volume, latency, or implementation. | **UNKNOWN**.  Finite syntax is not operational feasibility or architecture. |

## 4. Coverage index for prior counterexample IDs

The table below records where each older report's distinct findings were
replayed.  It prevents a duplicate old noun from being counted as a new attack
while making omissions visible.

| quarantined source | K/1 replay rows |
|---|---|
| Base `ARCHIVE-REPLAY.md` A01–A24 | K-A01–K-A35 collectively: context/externalization K-A15/K-A30; collision/exactness K-A01–K-A08/K-A23–K-A25; deletion/rebuild K-A27/K-A28; total dimensions and realization K-A31–K-A35 |
| `FEASIBILITY-AUDIT-R01.md` F1–F5, E1–E10 | F1 K-A07/K-A17; F2–F3 K-A04/K-A06/K-A08; F4 K-A02/K-A19; F5 K-A03; E1–E2 K-A01–K-A03/K-A19; E3–E10 K-A06–K-A08/K-A16/K-A24/K-A30/K-A33 |
| `FEASIBILITY-AUDIT-R01B.md` F1–F7 and run-boundary F8–F9 | K-A01–K-A08, K-A23, K-A35 |
| `FEASIBILITY-AUDIT-R01C.md` C1–C23 | C1–C4/C17/C21 K-A10; C5/C16 K-A01/K-A02; C6/C8 K-A06/K-A14; C7/C20 K-A09/K-A12; C9–C15/C18/C19/C22/C23 K-A03/K-A04/K-A07/K-A08/K-A27/K-A30/K-A32–K-A34 |
| `FEASIBILITY-AUDIT-R01D.md` D1–D31 | D1–D8 K-A01–K-A08/K-A24; D9–D15 K-A09–K-A14; D16–D21 K-A27/K-A28; D22–D31 K-A16/K-A23–K-A25/K-A27/K-A35 |
| `FEASIBILITY-AUDIT-R01E.md` E1–E5 | K-A10/K-A14/K-A15/K-A23/K-A24/K-A30/K-A34/K-A35 |
| `FEASIBILITY-AUDIT-R01F.md` §2.1–§2.8 and R01F archive replay | K-A01, K-A03/K-A04, K-A10/K-A13/K-A14, K-A23, K-A26–K-A30 |
| `FEASIBILITY-AUDIT-R01G.md` and R01G archive replay | framing/STOP K-A01/K-A12; nondeterminism K-A18; minimization/counts K-A23/K-A24/K-A35; action/recovery K-A13/K-A14; external/physical K-A30–K-A34 |
| R0.1H H01–H14, mathematics and feasibility audits | H01/H02 K-A09/K-A17; H03 K-A12; H04/H05 K-A18/K-A30; H06 K-A19–K-A21; H07/H08 K-A23/K-A24/K-A35; H09/H10/H13 K-A09–K-A14/K-A24; H11 K-A35; H12 K-A25; H14 K-A32–K-A34 |
| R0.1I I01–I16, literal/unified/feasibility audits | I01/I11/I12/I13/I16 K-A09/K-A14/K-A24; I02/I05/I09 K-A17/K-A29; I03/I04/I08 K-A01–K-A03/K-A23–K-A25; I06 K-A19–K-A21; I07 K-A18/K-A30; I10/I14 K-A06/K-A08; I15 K-A23/K-A35 |
| R0.1J archive, literal, and feasibility audits | partial timeout K-A06; UNKNOWN masking K-A19; unbound envelope K-A15/K-A30; phase/router K-A09–K-A12/K-A14; incomplete persistence/minimality K-A23/K-A24/K-A27 |
| `FORMAL-AUDIT-B2.md` | union-domain totality K-A09/K-A16/K-A18; exact merge witnesses K-A23–K-A25; deletion/derive limits K-A27/K-A28; evolution fiber pressure K-A26; realization/TCB limits K-A32–K-A35 |
| `REALIZATION-AUDIT-R1.md` | false attestation K-A10/K-A29/K-A34; error-taxonomy mismatch K-A01/K-A16; target/hash and external bundle K-A04/K-A07/K-A27/K-A30; unlike software versus physical scope K-A32; operational/resource claims K-A35 |

This is consolidation, not erasure: every prior finite collision shape has a
K/1 history/request/evidence reconstruction above, while purely empirical
probes remain UNKNOWN and out-of-scope capabilities are marked WITHDRAWN.

## 5. Does the archive add a new or smaller failure?

**No.** The archive adds neither a new final-candidate failure family beyond
F01–F11 nor a smaller witness.

- Old sentinel/presence attacks are exactly F01.  The raw-`MISSING` sibling was
  already recorded by the fresh break.
- Old framing, namespace, association, delimiter, and exact-address attacks are
  instances of F02, with downstream ledger impact already F08.
- Old partial-output and exact-target attacks split exactly as fresh P08/F07:
  CHUNK plus EXPIRE co-presence survives in HISTORY, while the asserted capture
  answer does not carry the retained bytes.
- Old request/application, lifecycle, completion, and phase-router attacks are
  F04/F05; the archive supplies no continuation shorter than the retained
  refusal plus one next request used in F04.
- Old adaptive/common-domain and depth-origin attacks are F03/F06/F09/F10.
- Old projection/authorization attacks reach F11.
- Old exhaustive-ledger and global-minimality attacks reach F02/F08 plus the
  fresh UNKNOWN for an unexecuted global enumeration.
- Physical, human, cross-realization, storage, operational, and TCB probes do
  not become formal counterexamples merely because K/1 withdraws the claims;
  they remain UNKNOWN.

F01 has zero encoded-byte difference and no history occurrences, so no replay
can be lexicographically smaller.  Several archive rows are independent
corroborations, but none changes the fresh verdict or its minimum.

## 6. Where the complexity moved

The candidate avoids prescribing a representation, but the work exposed by old
attacks remains somewhere in the total experiment.  This table records the
responsibility location without proposing an architecture.

| attacked responsibility | where K/1 places the work | replay status |
|---|---|---|
| exact type/presence distinction | seal transport, map/value grammar, marker discrimination | F01/F02 FAIL |
| occurrence direction and authority | direction-tagged occurrence encoder and authority bytes | F02 FAIL; authority realization UNKNOWN |
| retained evidence and exact target selection | inline `HISTORY`/`EVIDENCE`, CAPTURE projection, immutable superseding-seal archive | F07 FAIL for capture payload; archive/durability UNKNOWN |
| request acceptance, pending state, and refusal closure | first-match history predicates and request/result correlation | F04/F05 FAIL |
| bounded progress | external corpus driver, progress evidence, operation-closing ANS | F05 FAIL; wall-clock/network behavior UNKNOWN |
| branch correlation and normal results | branch policy, answer-tree construction, selector evidence | F10 FAIL; scheduler/determinism claims withdrawn |
| viewer projection and authority | viewer-scoped constructors, permission adjudication, projection evidence | F11 FAIL; authentication UNKNOWN |
| carrier root and request depth | experiment root identity, request counter, branch cloning if used | F03/F06/F09 FAIL |
| exact future-collision ledger | expansion of `P_K`, all pair continuations, C/E artifact retention | F08 FAIL |
| witness minimality and nonuniqueness | finite global enumeration, exact alphabet, scope and tie bytes | criterion stated; result UNKNOWN, blocked by F02/F08 |
| versioned meaning | inline specification bytes, interpreter, time-scoped request/answer | formal rule PASS; exact execution/TCB UNKNOWN |
| derivation and recomputation | retained source ranges, rule identity, proof machinery, cold reconstruction work | rule conservative; execution/cost UNKNOWN |
| external context closure | `DEPENDENCIES`/`EVIDENCE`, seal producer, perturbation surface | F01 FAIL; global closure UNKNOWN |
| physical completion/recovery/termination | independent observer, clock, adjudication and per-realization evidence | UNKNOWN; base claim withdrawn |
| human validation and authoring | reviewer access, tools, expertise, protocol and measurements | UNKNOWN; burden claim withdrawn |
| TCB and circular validation | dependency inventory and an independent adjudicator | UNKNOWN; closure withdrawn |
| storage/runtime/operations | seal/evidence retention, enumerator, decoder, driver and subject realization | UNKNOWN; no architecture selected |

Moving a responsibility is not deleting it.  In particular, making a rule
inline moves trust to the exact byte grammar and interpreter; making evidence
external moves availability, identity, and binding to the seal producer and
archive; making a witness derivable moves work to retained source ranges and
proof machinery; and withdrawing physical or human claims leaves those goals
undischarged rather than cost-free.

## 7. Final archive disposition

The quarantined archive confirms the fresh **FAIL** without adding a new or
smaller final-candidate counterexample.  It also confirms that the final R0.1K
fixed several pre-freeze advisory defects: the application predicate, leaf
ordering around unresolved actions, pending-state inventory, conditional
K-CLOSE rule, global-minimality criterion, physical-negative wording, and the
incorrect-MUST example were materially corrected.

The remaining exact collisions are the fresh F01–F11.  The archive principally
shows where the deleted old nouns' work now resides: byte typing and framing,
authority association, request/result correlation, branch identity, viewer
projection, root/depth accounting, evidence retention, global ledger
enumeration, and external context binding.

Subject conformance, physical completion, durable recovery, terminal halt,
human-local validation, global TCB closure, storage/runtime feasibility, and
cross-realization behavior remain **UNKNOWN**.  A passing formal definition or
finite truth table would still not establish an implementation or architecture.
