# ZERO GROUND R0.1J corrected persistence-collision ledger

## 0. Scope, authority, and classifications

This ledger audits frozen R0.1J without proposing any implementation
representation. It names behavioral distinctions and evidence dependencies,
not places, fields, objects, media, or architecture.

Only these frozen inputs were used:

| Input | Verified SHA-256 |
|---|---|
| `HISTORY-SEED-R01J.md` | `7c9b2a742eab81f6c104b6ca3566315ddb29ecc63d216d25cff91bf1c70836dc` |
| `POSTFREEZE-BREAK-R01J.md` | `ed8675d7b2f3d53b8e35321e2361a0480665ce36e498d8ed5f8e3b15bac96d8a` |
| `LITERAL-SPEC-AUDIT-R01J.md` | `370642e1ea148c4702a373a3e33347d3987c160db1fe41dc5e9364cb4ead3956` |

The labels are scoped:

- **MUST SURVIVE (behavioral)** means enough information to prevent the named
  all-scope continuation collision must remain somewhere in the declared total
  system across the stated boundary. It prescribes no representation.
- **MUST SURVIVE (claim evidence)** means deletion makes the corresponding
  historical, falsification, or conformance claim unauditable. It need not be
  behavioral continuation information.
- **MAY REBUILD** means a separately available derived form may be deleted and
  exactly reconstructed from the named surviving inputs and frozen function.
  This does not prove those inputs or the reconstruction machinery survive.
- **MAY FORGET** means the named distinction is within one stated continuation
  equivalence class. It does not license deletion of evidence for a claim that
  expressly refers to the distinct histories.
- **UNKNOWN** means the required deletion, cold reconstruction, severing,
  cognition, TCB, or physical experiment has not been performed.

The same semantic fact can legitimately receive two scoped labels. For
example, the active residual distinction is behavioral MUST information, while
a separately materialized residual value is MAY REBUILD from an exact prefix.

## 1. Audit-only minimization order

Section 10.1 is underdefined: it gives singular post-cut counts for pairs with
one-versus-two branch families and does not define “differing prefix
crossings” for unequal-length prefixes. Its claims of exact minimality cannot
be reproduced literally.

For this ledger only, define **audit order A1** over a candidate cut pair,
common policies, and separating scope. It is the lexicographic tuple:

1. maximum post-cut ordinary-C count over every suffix on both sides;
2. sum of those ordinary-C counts;
3. maximum post-cut full-crossing count;
4. sum of post-cut full-crossing counts;
5. total suffix count across both families;
6. total post-cut F:CRASH count;
7. total pre-cut ordinary-C count across the pair;
8. prefix-divergence count, defined as the total number of crossings remaining
   after removing the longest common crossing prefix from both exact prefixes;
9. ranked ordinary-alias sequences, compared lexicographically with an
   end-of-sequence marker below every alias;
10. separating scope code;
11. oriented `EncCut` pair bytes; and
12. controller and scheduler bytes.

A1 borrows the explicit complete-family aggregation discipline of Section
8.7 and adds a precise prefix comparison. It is an analysis convention, not
R0.1J candidate semantics and not a repair to the frozen bytes. References to
“A1-minimal” below have only that meaning. The semantic collision remains
valid even if another audit order chooses a different representative.

## 2. Exact contractual quotient ledger

Independent recounts agree on 14 clean classes, 315 recovery classes, and 329
combined all-scope classes. The continuation classes can be audited without a
storage assumption by the following mathematical partition:

| Declared-cut family | Continuation distinctions that remain contractual | Distinctions absent from the all-scope class identity |
|---|---|---|
| Clean | active residual `r` | exact clean word among histories reaching the same `r` |
| DOWN idle | directed family kind NONE, active `r`, live `d` | exact source prefix once those continuation facts agree |
| DOWN pending | directed `(pre,post)`, live `d`, OLD/NEW barrier | pending alias and T stage when they induce the same directed pair |
| DOWN FIN-pending | FIN-pending obligation | source residual, unused d, and exact source history |
| DOWN terminal | terminal obligation | source residual, unused d, and exact source history |

This table is only a quotient description. It is not a required schema. It
accounts for all 315 recovery classes:

    68 idle + 245 directed pending + 1 FIN-pending + 1 terminal.

The 245 pending classes consist of 195 changing directed-edge classes and 50
identity-edge classes. The latter absorb 455 no-op/T-stage conditions. PUBLIC
has only 139 recovery functions because it hides F labels and direction, and
because at d=0 forced FIN hides every active residual and pending endpoint.
Those PUBLIC mergers do not authorize contractual deletion when SELECTOR or
PRIV still separates.

## 3. Exact phase witnesses omitted by Section 10

### 3.1 Minimal source cuts

Use the following exact cuts, all derived from initial clean `H()` unless a
completed RI is stated. `H()` already ends in `F:CUT REMAINING=3`.

| Name | Exact additional prefix through the cut | Derived condition |
|---|---|---|
| `J_C` | none | clean active, `(U,EMPTY,E0),d=3` |
| `J_I` | `F:CRASH GAP=0`, `L:DOWN` | DOWN idle active, same r,d |
| `J_F` | typed `C:FIN`, `F:CRASH GAP=1`, `L:DOWN` | DOWN FIN-pending, same r,d |
| `J_T` | typed `C:FIN`, typed `R:STOPPED`, `F:CRASH GAP=2`, `L:DOWN` | DOWN terminal, same source r,d |
| `J_P` | C:`REPLACE ID\n`, `F:CRASH GAP=1`, `L:DOWN` | DOWN pending no-op RI, `(pre=post=(U,EMPTY,E0)),d=2` |
| `J_I2` | C:`REPLACE ID\n`, R:`ERR EMPTY\n`, `F:CRASH GAP=2`, `L:DOWN` | DOWN idle active, same r and d as `J_P` |
| `J_PF` | C:`REPLACE ID\n`, R:`ERR EMPTY\n`, typed `C:FIN`, `F:CRASH GAP=3`, `L:DOWN` | DOWN FIN-pending, same source r,d as `J_P` |
| `J_PT` | C:`REPLACE ID\n`, R:`ERR EMPTY\n`, typed `C:FIN`, typed `R:STOPPED`, `F:CRASH GAP=4`, `L:DOWN` | DOWN terminal, same source r,d as `J_P` |

Use the controller that chooses FIN at every consulted key and the all-zero
scheduler. The complete suffix shapes are:

| Cut | Full formal suffix shape |
|---|---|
| `J_C` | `C:FIN`, `R:STOPPED` |
| `J_I` | `F:RESUME ACTIVE ...`, `F:ALLOWANCE 3`, `L:READY`, `C:FIN`, `R:STOPPED` |
| `J_F` | `F:RESUME FIN_PENDING`, `L:READY`, `R:STOPPED` |
| `J_T` | `F:RESUME TERMINAL`, `L:READY` |
| `J_P` | two OLD/NEW suffixes, each `F:SELECT`, active RESUME, ALLOWANCE 2, READY, FIN, STOPPED |
| `J_I2` | one NONE suffix with active RESUME, ALLOWANCE 2, READY, FIN, STOPPED |
| `J_PF` | the same forced shape as `J_F` |
| `J_PT` | the same forced shape as `J_T` |

Expanded exactly, the new A1-minimal suffixes are:

    J_C:
      C:FIN
      R:STOPPED

    J_I:
      F:RESUME ACTIVE O=U P=EMPTY E=E0\n
      F:ALLOWANCE 3\n
      L:READY
      C:FIN
      R:STOPPED

    J_F:
      F:RESUME FIN_PENDING\n
      L:READY
      R:STOPPED

    J_T:
      F:RESUME TERMINAL\n
      L:READY

The two exact `J_P` branches begin respectively with `F:SELECT old\n` and
`F:SELECT new\n`, followed in both cases by
`F:RESUME ACTIVE O=U P=EMPTY E=E0\n`, `F:ALLOWANCE 2\n`, `L:READY`, typed
`C:FIN`, and typed `R:STOPPED`. RI is an identity transition at EMPTY, so the
two RESUME bytes agree while the required selector labels and family
cardinality remain distinct from `J_I2`.

FIN is typed and therefore is not an ordinary C for minimization. Every phase
pair below separates with zero post-cut ordinary C.

### 3.2 Complete phase-pair matrix

Section 10 lists only idle-versus-pending (S3) and FIN-pending-versus-terminal
(S5). All ten unordered phase-family pairs are contractually unequal:

| Phase pair | Exact direct witness | Smallest separating evidence | Correct classification |
|---|---|---|---|
| clean / DOWN idle | `J_C` / `J_I` | PUBLIC has `FIN,STOPPED` versus `READY,FIN,STOPPED`; SELECTOR empty versus RESUME/ALLOWANCE | **MUST SURVIVE**; A1-minimal omitted Q7 witness |
| clean / DOWN pending | `J_C` / `J_P` | PUBLIC lacks versus has READY; SELECTOR also has two labeled branches | **MUST SURVIVE**, covered semantically by Q7 but absent from S1-S5 |
| clean / FIN-pending | `J_C` / `J_F` | PUBLIC `FIN,STOPPED` versus `READY,STOPPED` | **MUST SURVIVE**, Q7 corollary |
| clean / terminal | `J_C` / `J_T` | PUBLIC `FIN,STOPPED` versus `READY` | **MUST SURVIVE**, Q7 corollary |
| DOWN idle / DOWN pending | `J_I2` / `J_P` | PUBLIC may agree after projection; SELECTOR/PRIV distinguish one NONE suffix from OLD/NEW | **MUST SURVIVE**, existing S3 |
| DOWN idle / FIN-pending | `J_I` / `J_F` | PUBLIC `READY,FIN,STOPPED` versus `READY,STOPPED` | **MUST SURVIVE**; A1-minimal active/FIN omission |
| DOWN idle / terminal | `J_I` / `J_T` | PUBLIC `READY,FIN,STOPPED` versus `READY` | **MUST SURVIVE**; A1-minimal active/terminal omission |
| DOWN pending / FIN-pending | `J_P` / `J_PF` | PUBLIC `READY,FIN,STOPPED` versus `READY,STOPPED`; SELECTOR branch family also differs | **MUST SURVIVE**, active/FIN direct corollary |
| DOWN pending / terminal | `J_P` / `J_PT` | PUBLIC `READY,FIN,STOPPED` versus `READY`; SELECTOR branch family also differs | **MUST SURVIVE**, active/terminal direct corollary |
| FIN-pending / terminal | `J_F` / `J_T` | first F:RESUME differs; PUBLIC owes STOPPED only on FIN-pending side | **MUST SURVIVE**, existing S5 |

`J_C/J_I` is A1-minimal for clean versus any recovery: it has no pre-cut
ordinary C, and idle recovery is the shortest recovery prefix. `J_I/J_F` and
`J_I/J_T` are A1-minimal active-versus-special pairs for the same reason.
`J_P/J_PF` and `J_P/J_PT` isolate pending-active from the special phases at
equal r and d; RI is the lowest-ranked identity transition at EMPTY.

The phase matrix is a behavioral lower bound only. The phase distinction may
be recomputed from an exact prefix and frozen fold; this does not make the
distinction MAY FORGET.

## 4. Audit of every frozen MUST entry

The semantic pairs below are valid. Their frozen claims of candidate-exact
smallestness remain underdefined; A1 supplies an audit-only check.

| ID | Behavioral information lower bound | Exact collision and continuation | Corrected disposition |
|---|---|---|---|
| S1-O | Active O across recovery | Idle recovery from clean `H()` versus matching idle recovery from clean `H(O0)`, both d=3; first active RESUME says `O=U` versus `O=0` | **MUST SURVIVE**; O0 is A1-minimal changing O |
| S1-P | Active P across recovery | Same construction with `H()` versus `H(AI)`; first RESUME says EMPTY versus ID | **MUST SURVIVE**; AI is A1-minimal changing P |
| S1-G | Active G across recovery | Same construction with `H()` versus `H(E)`; first RESUME says E0 versus E1 | **MUST SURVIVE**; E is the only G-changing request |
| S2 | Remaining live allowance | `J_I` at d=3 versus `J_I2` at d=2, with the same residual; ALLOWANCE differs before any ordinary post-cut C | **MUST SURVIVE**; separately available d is MAY REBUILD under R3 |
| S3 | NONE versus interrupted OLD/NEW obligation | `J_I2` versus `J_P`; r and d agree, PUBLIC can agree, SELECTOR/PRIV cannot | **MUST SURVIVE**; existing smallest semantic pair, A1 rather than Section 10.1 supplies reproducible aggregation |
| S4 | Directed pre/post association | Interrupt AI from EMPTY to ID versus D from ID to EMPTY at equal d; PUBLIC endpoint sets agree but OLD/NEW RESUME association reverses | **MUST SURVIVE** contractually; PUBLIC alone MAY FORGET direction |
| S5 | FIN-pending versus terminal | `J_F` versus `J_T`; one owes exactly one STOPPED and the other forbids later C/R | **MUST SURVIVE** |

The corrected MUST ledger adds the phase rows in Section 3. S1-S5 alone are
not complete: preserving r, d, pending-kind, direction, and FIN/terminal still
allows `J_C` to collide with `J_I`, or active recovery to collide with a
special recovery phase.

For clean cuts, unequal active residuals are also contractual distinctions:
the initial crash exposes them to SELECTOR/PRIV with zero ordinary C, and X
exposes them to PUBLIC with one ordinary C. S1's recovery frames are the
smallest deletion witnesses for the coordinate values, not a license to erase
the same values at clean cuts.

## 5. Audit of every frozen MAY REBUILD entry

Every R entry is a valid formal conditional. None is evidence of a cold-start,
availability, work, or physical-recovery experiment.

| ID | Separately deletable derived material | Exact surviving inputs and reconstruction | Corrected disposition |
|---|---|---|---|
| R1 | Pre-serialized RESUME and ALLOWANCE bytes | Exact cut prefix plus frozen fold yields `(r,d)`; Section 4 templates reproduce bytes | **MAY REBUILD** formally; input/spec/machinery survival **UNKNOWN** |
| R2 | A separately available nondefault residual value | Exact clean prefix `H(O0)`, initial residual, and transition fold reproduce r and X bytes | **MAY REBUILD** formally; exact-prefix availability **UNKNOWN** operationally |
| R3 | A separately available noninitial d value | Exact prefix counts ordinary C occurrences after CUT; initial 3 and the allowance rule reproduce d | **MAY REBUILD** formally; cold reconstruction **UNKNOWN** |
| R4 | Cached viewer projections and trace-set order | Generated full suffix family plus frozen projection/codec/sort rules reproduce four projected values | **MAY REBUILD** formally; generator/canonicalizer availability **UNKNOWN** |

The quotient audit exposes additional derived material with the same
conditional classification:

| Added ID | Derived fact or result | Exact reconstruction basis | Disposition |
|---|---|---|---|
| R5 | Clean/DOWN/pending/FIN-pending/terminal condition and any pending pre/post association | Exact cut prefix plus Sections 2-4 fold; occurrence captures pre/post and any crossed R determines completed application | **MAY REBUILD** as a separate form; the underlying behavioral distinction remains **MUST SURVIVE** |
| R6 | D and G key universes, ordering, and table lengths | Frozen cut corpus, transition semantics, projections, exploration rules, and codecs | **MAY RECOMPUTE** formally; independent operational agreement remains **UNKNOWN**. One audit obtained `N=82,224`, `M=64,067` |
| R7 | Formal viewer outcomes for fixed cut and policy bytes | Exact cut, legal controller, legal scheduler, and frozen evaluator | **MAY RECOMPUTE** formally; router-interface defects and independent implementation evidence remain unresolved |
| R8 | A Section 8.7 canonical witness | Fixed cut pair, complete finite policy universes, evaluator, scope rule, and byte order | **MAY RECOMPUTE** in the finite formal model; emitted exact bytes, cost, and independent canonicalizer agreement are **UNKNOWN** |

R5-R8 do not imply that controller or scheduler choices can be derived from a
cut. Those choices are external quantified inputs. Recomputing the domains in
which they are encoded is not reconstructing their chosen values.

Under A1, the frozen R examples also remain the least conditional examples of
their kind: `H()` for pre-serialized recovery frames, O0 for a nondefault
residual, RI for a noninitial d without changing the residual, and clean
`H()`/FIN for a nonempty complete projected suffix. This is audit analysis,
not restoration of Section 10.1's missing order.

## 6. Audit of every frozen MAY FORGET entry

These are all-scope continuation mergers. The evidence column prevents a
behavioral merger from being inflated into a claim that the full histories
were identical.

| ID | Exact merger | Continuation disposition | Evidence/claim boundary |
|---|---|---|---|
| F1 | Clean `H()` versus `H(RI)` | **MAY FORGET** the exact clean prehistory for continuation; both are in one clean residual class | Exact prefix must survive if the claim concerns which history occurred |
| F2 | Pending no-op RI versus RN from `H()` at equal d | **MAY FORGET** pending alias for all-scope continuation | Their distinct C frames remain different prefix evidence |
| F3 | T interrupted before A versus after A | **MAY FORGET** the T stage for post-cut continuation | The crossed A on the post-A side is a full-history/capture evidence distinction and must survive for that historical claim |
| F4-r | FIN-pending from `H()` versus from `H(O0)` | **MAY FORGET** source residual after FIN | Exact source history remains claim evidence if asserted |
| F4-d | FIN-pending from `H()` versus after completed no-op RI | **MAY FORGET** unused d after FIN | Same evidence caveat |
| F5-r/d | Append STOPPED and crash at END to the F4 sources | **MAY FORGET** source residual and unused d after terminal completion | Same evidence caveat |

The quotient entails two useful closures of these rows:

| Added ID | Merger family | Disposition |
|---|---|---|
| F6 | Any clean exact histories reaching the same residual | **MAY FORGET** their exact-word distinction for all-scope continuation; F1 is the A1-smallest distinct pair |
| F7 | Any pending aliases/T stages with equal directed `(pre,post)` and d | **MAY FORGET** alias and T stage for all-scope continuation; do not forget OLD/NEW direction |
| F8 | Any exact recovery prefixes normalizing to the same idle or directed-pending condition | **MAY FORGET** source-prefix multiplicity for continuation; exact-prefix claims remain separate |
| F9 | Any FIN-pending sources, respectively any terminal sources | **MAY FORGET** all source r/d/history distinctions for continuation; FIN-pending and terminal may not merge with each other |
| F10-PUBLIC | Reversed changing edges such as S4, idle/no-op branch-count differences whose projected traces deduplicate, and all active/pending conditions at d=0 | **MAY FORGET only in PUBLIC's projected function**; SELECTOR/PRIV contractual distinctions still **MUST SURVIVE** |

No F row licenses forgetting the frozen specification needed to interpret the
remaining information, the exact policies requested for a future, or evidence
for an independently asserted historical claim.

Under A1, the frozen exemplars remain least within their stated merger kinds:
RI is the first identity transition at EMPTY, RI/RN are the first two distinct
pending identity aliases there, T supplies the only pre-A/post-A pair, O0 is
the first source-residual change, and one completed RI is the first unchanged
residual with reduced d. Again, this does not make the candidate's own
minimization order complete.

## 7. Between-execution information versus manifest evidence

### 7.1 Behavioral continuation ledger

For R0.1J continuation, enough information to identify the appropriate
all-scope quotient class must remain available across a relevant execution or
recovery boundary. That is the combined content of:

- active r where active futures can expose it;
- live d while active;
- clean versus every DOWN recovery family;
- idle NONE versus pending OLD/NEW;
- directed pre/post association while selection is owed; and
- active, FIN-pending, and terminal obligations.

The information may be present directly or reconstructed from exact named
inputs. This ledger does not infer where or how. Exact within-class source
history distinctions in F1-F10 may be forgotten if, and only if, the claim is
limited to continuation behavior at the stated observation scope.

A falsification manifest is not among these behavioral prerequisites. Holding
cut and policies fixed while deleting only manifest retention leaves every
formal `Obs_v` unchanged. Therefore manifest bytes are **MAY FORGET between
service executions for continuation alone**.

### 7.2 Claim-evidence retention ledger

Evidence retention answers a different question:

| Evidence dependency | If the corresponding claim must remain auditable | Effect on continuation | Current evidence status |
|---|---|---|---|
| Exact cut prefix | **MUST SURVIVE (claim evidence)** for exact-history, cut-membership, crash-ordinal, or witness validation claims | Within-class prefix differences may be forgotten behaviorally | Physical retention/location **UNKNOWN** |
| Manifest bytes | **MUST SURVIVE (claim evidence)** for the particular manifest-backed claim | MAY FORGET for continuation | No R0.1J manifest exists; operational retention **UNKNOWN** |
| Captured raw family | **MUST SURVIVE (claim evidence)** for what was actually observed | Not continuation state by itself | Capture durability/completeness **UNKNOWN** |
| Partial raw prefix before timeout | Should distinguish two evidence histories, but kind 1 deletes it | No behavioral effect | **FAIL**: the frozen carrier cannot retain prefix plus expiry |
| Experiment envelope governing a timeout verdict | Necessary for a bound-violation claim | No behavioral effect | **UNDERDEFINED/FAIL**: no frozen codec or manifest binding; identical manifest bytes can be UNKNOWN or FAIL |
| Frozen specification bytes/digest | Necessary to interpret cuts, policies, generator results, and manifest digest | Also a named input to formal rebuilding | Availability, distribution, and independent identity adjudication **UNKNOWN** |
| Crossed A evidence | **MUST SURVIVE (claim evidence)** if claiming the T attempt was captured before the cut | F3 permits stage deletion for continuation | Capture durability **UNKNOWN** |
| Origin-0 generated family | May evidence generator self-consistency if retained | No extra continuation information | Explicitly not an independent verifier test |

Retention is necessary but not sufficient for a valid evidence claim. A
retained timeout case still loses its captured prefix; a retained multi-case
manifest can let UNKNOWN precede a finite conformance FAIL; and a retained
manifest has no bound envelope identity. A zero-case 57-byte manifest or only
matching origin-0 cases cannot establish conformance merely because the
classifier says `SUPPORTED_EVIDENCE`.

Deleting manifest evidence should change the corresponding claim to UNKNOWN,
not rewrite history to “nothing happened” and not alter continuation behavior.

## 8. Externalized influences and UNKNOWN persistence

Formal inputs or charged external influences are not thereby proven durable.

| Influence | Formal role | Correct persistence classification |
|---|---|---|
| Controller table | Same total CLIENT-visible choice function is applied to both compared cuts | If a claim requires the same future policy, its identity/value is a necessary input; survival or severing is **UNKNOWN** |
| Scheduler vector | Same global PUBLIC/next-crossing vector governs divergent clean paths | Domain is MAY RECOMPUTE; selected bits, availability, and recovery across severing are **UNKNOWN** |
| Selector | Formal semantics enumerates both labels rather than retaining one chosen branch | Any external selector realization, choice durability, or severing is **UNKNOWN** |
| Capture peer | Supplies A-boundary evidence and no client feedback during a run | Omission, availability, and durability are **UNKNOWN** |
| Manifest and envelope context | Supports later evidence adjudication only | Claim-scoped retention is necessary; binding is defective and operational survival **UNKNOWN** |
| Frozen specification | Supplies fold, grammar, codecs, and reconstruction authority | Named formal input; distribution, collision resistance in use, and availability **UNKNOWN** |
| Canonicalizer | Executes finite closure, projection, ordering, and witness search | Results MAY RECOMPUTE formally; availability, cost, independent agreement, and context perturbation are **UNKNOWN** |

Moving any one of these responsibilities outside a service is
`EXTERNALIZE`, not DELETE. A severing experiment must show what remains
available before an operational MUST/MAY claim can receive PASS.

The post-freeze reports differ in phrasing about the encoded router: the
cross-section transition rules suffice to reproduce the 329-class quotient,
while the router table itself omits explicit reachable configurations and the
raw in-phase selector invocation has no exact result. This ledger uses the
reproduced formal suffixes for collision lower bounds. It does not convert
that reconstruction into a total raw-interface or implementation PASS.

## 9. Transformation and evidence matrix

| Operator | Exact R0.1J use | Ledger verdict |
|---|---|---|
| DELETE | Remove enough information to collapse one S row or one phase-matrix pair; separately delete one claim's manifest/prefix evidence | Behavioral collision is formal **FAIL**; evidence deletion makes that claim unauditable. No physical deletion run exists |
| MERGE | Force two cuts from different contractual rows to share one future behavior, or merge evidence histories such as timeout-before versus timeout-after-FIN | Quotient-crossing merge is **FAIL**; within F1-F10 scope is **MAY FORGET**; timeout carrier already **FAILS** |
| DERIVE | Delete a separately available R1-R5 form and apply the exact named fold/template | Formal **MAY REBUILD**; surviving inputs and cold machinery **UNKNOWN** |
| RECOMPUTE | Recreate R4 and R6-R8 projections, closures, outcomes, or witnesses | Finite algorithm exists; operational bytes, work, availability, and independent agreement **UNKNOWN** |
| EXTERNALIZE | Sever controller, scheduler, selector, capture, manifest/envelope, specification, or canonicalizer one at a time | **UNKNOWN**; external placement is charged, not evidence of lossless deletion |
| COGNITION | Give fresh reviewers only the claimed sufficient artifacts for S/R/F, scope, and manifest verdict decisions | **UNKNOWN**; no bounded time, error, expertise, or access study exists |
| TCB | Perturb runtime, codec, capture, selector, scheduler/controller, spec, canonicalizer, envelope signer, and human adjudication one at a time | **UNKNOWN**; origin-0 agreement is explicitly non-independent and no perturbation campaign exists |

`REALIZE` remains UNKNOWN as well: FORMAL is the only admitted realization and
there is no physical persistence, crash/recovery, completion, or unlike-media
evidence.

## 10. Corrected collision ledger summary

### Behavioral MUST SURVIVE

Enough information must preserve:

1. active O, P, and G distinctions;
2. live allowance d;
3. all clean-versus-DOWN distinctions;
4. idle NONE versus pending OLD/NEW;
5. directed pre/post association;
6. active recovery versus FIN-pending and terminal; and
7. FIN-pending versus terminal.

Items 3 and 6 are the missing Section 10 quotient responsibilities. The exact
A1-minimal additions are `J_C/J_I`, `J_I/J_F`, and `J_I/J_T`; direct pending
corollaries are `J_P/J_PF` and `J_P/J_PT`.

### Formal MAY REBUILD / MAY RECOMPUTE

Derived residual, allowance, phase, pending association, frames, projections,
D/G closures, formal outcomes, and canonical search results may be rebuilt or
recomputed only from their exact named surviving inputs and frozen machinery.
This is conditional mathematics, not persistence evidence.

### Behavioral MAY FORGET

Exact histories within one clean residual, aliases/stages within one directed
pending class, normalized-source multiplicity, and source r/d after FIN or
terminal may be forgotten for all-scope continuation. Additional PUBLIC-only
mergers may not be promoted to contractual mergers.

### Claim-scoped MUST and operational UNKNOWN

Exact prefix, captured observations, manifest, governing experiment context,
and specification must remain available if their particular audit claim is to
remain checkable. They are not automatically between-execution behavioral
state. No physical retention, severing, cognition, TCB, or unlike-realization
experiment exists, and R0.1J's timeout/envelope defects mean that merely
retaining its present manifest bytes is not sufficient evidence.
