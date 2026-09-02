# ZERO GROUND R0.1J — Quarantined Archive Replay

## 0. Authority, quarantine, and verdict discipline

This replay was performed only after the fresh R0.1J break was frozen at
commit `24cb91056dbcc36b021c8c1e19ccd1e7477e0273`.

The candidate and fresh verdict authorities are:

| Artifact | SHA-256 | Role |
|---|---|---|
| `HISTORY-SEED-R01J.md` | `7c9b2a742eab81f6c104b6ca3566315ddb29ecc63d216d25cff91bf1c70836dc` | Frozen candidate |
| `POSTFREEZE-BREAK-R01J.md` | `ed8675d7b2f3d53b8e35321e2361a0480665ce36e498d8ed5f8e3b15bac96d8a` | Fresh candidate-only verdict |

The following prior reports were admitted only as attack inputs:

| Quarantined report | SHA-256 |
|---|---|
| `MATH-AUDIT-R01H.md` | `4be36240e23804b0dac6c20c62b14a07f96e8b0ff3c456af0baf02e34d9515be` |
| `POSTFREEZE-BREAK-R01H.md` | `c97e6ef26fbdc0084c739cf64518fd51ff1668ec8b6eb4e1e5e20cebf99d669c` |
| `FEASIBILITY-AUDIT-R01H.md` | `37f5ab50218e2262e5d9aa0b19f4eca7559c02752d7164facef9b80487baa0de` |
| `LITERAL-SPEC-AUDIT-R01I.md` | `e26af4a66ff1884371973a60710c5b0f556b9d4b78b5259bb50d355007262ad5` |
| `POSTFREEZE-BREAK-R01I.md` | `57f007f0457595e5545eb9dd76fda210b9eea94483a1d74cb6d074230b8ac015` |
| `FEASIBILITY-AUDIT-R01I.md` | `56246649099d873d6933806ebac159d5093fdaf7260ee9ea43242956b787fbb8` |
| `UNIFIED-QUOTIENT-AUDIT-R01I.md` | `0acbfe099668368c762e11cd5c0a14821dcb682f701fd27115acf53f83b66a00` |

No prior representation, state ontology, repair, architecture, or proposed
solution is adopted. A prior report contributes only a counterexample shape.
Each shape is reconstructed in R0.1J's own alphabet, cuts, router, viewers,
and encodings.

`BLIND-ATTACK-PACK-R01I.md` is not archive evidence here: it was already an
admitted ontology-independent input to the fresh break, whose B00--B38/C1--C6
results are frozen in `POSTFREEZE-BREAK-R01J.md`.

Verdicts mean:

- **PASS:** the smallest R0.1J replay has one exact formal result and the old
  contradiction no longer applies;
- **FAIL:** the attack still produces a finite R0.1J counterexample;
- **UNKNOWN:** the test requires a capability or empirical carrier R0.1J does
  not provide, such as physical completion, external availability, human
  performance, or a realized canonicalizer.

A PASS by narrowing or deleting a claim is labeled as scope closure. It is not
capability evidence.

## 1. Replay result in one view

The archive adds **no new FAIL** beyond the five families already frozen in
`POSTFREEZE-BREAK-R01J.md`:

1. phase-router/raw-role totality;
2. partial-timeout evidence loss;
3. manifest UNKNOWN masking an independent FAIL;
4. unbound experiment-envelope context; and
5. the missing clean-active/DOWN-idle persistence obligation and incomplete
   Section 10 minimality order.

It also adds no smaller witness outside those already frozen. Two archive
attacks sharpen where the minima sit:

- the shortest router-coverage witness is `H()`, FIN crossing, then the
  reachable active FIN-pending state before STOPPED—zero ordinary C—which is
  already included in fresh F01; and
- the shortest missing persistence witness is clean `H()` versus its initial
  idle recovery cut—zero pre-cut and post-cut ordinary C—which is exactly fresh
  F05/Q7.

The core all-cut quotient remains independently reproduced at 153 PUBLIC
functions and 329 contractual classes. Complexity was not removed; it was
made explicit in the router, F-bearing branch family, controller/scheduler
domains, evidence carrier, canonicalizer, specification, and external
experiment envelope.

## 2. R0.1H counterexample replay

Duplicate H-era reports are consolidated by counterexample, not counted as
independent evidence.

| ID | Prior counterexample | Smallest R0.1J replay | Verdict | Fixed behavior or moved complexity |
|---|---|---|---|---|
| H01 | Completed-R residual fold contradicted SELECT-new after interrupted AI/O0/E. | From `H()`, let `C:AUTHOR ID` cross and crash before R. OLD resumes EMPTY; NEW atomically applies delta and resumes ID; neither invents R. | **PASS** | Section 4.1 makes SELECT-new a semantic application. Responsibility moves to the exact application fold, F label, and selector family. |
| H02 | One public post-crash prefix was incorrectly treated as one full-history residual key. | Use H01 and compare CLIENT/PUBLIC with SELECTOR/PRIV. Public suffixes may coincide before a probe; exact labeled branches do not. | **PASS** | Full prefix, viewer projection, selected residual, and future suffix are separate authorities. Public equality is not full-history identity. |
| H03 | The post-STOP crash trace was ambiguous or erased by “complete at STOPPED.” | `H()`, FIN, STOPPED, crash in END. Recovery is exactly `RESUME TERMINAL; READY` and then ends. | **PASS (formal)** | Terminal lifecycle behavior is frozen; physical terminality remains UNKNOWN. |
| H04 | Adaptive schedules lacked one identity when paths had different crossing shapes. | Send X; choose T only on the EMPTY reply and FIN otherwise. A global G bit is keyed by exact PUBLIC suffix plus proposed crossing; absent keys are inert. | **PASS (formal)** | Complexity moves to the external scheduler vector, G closure, PUBLIC observation, and canonicalizer. Availability/restart is UNKNOWN. |
| H05 | It was unclear whether a client controller saw capture A or could be random. | Crash after T's A and before R, then use the fixed retry-on-READY controller. CLIENT excludes A/F; scheduler PUBLIC includes A; controllers are deterministic. | **PASS (formal)** | The visibility split is exact. Capture/scheduler survival and authenticity remain external UNKNOWNs. |
| H06 | May dedup erased the carrier needed for old/new Must; vacuity and inapplicability were ambiguous. | Interrupt no-op RI. The formal family has ordered OLD/NEW full suffixes even when PUBLIC deduplicates them. R0.1J exposes no arbitrary Must mask. | **PASS by scope closure** | Branch carrier moves to PRIV/raw evidence. Arbitrary MAY/MUST and human “guaranteed” queries remain UNKNOWN rather than becoming vacuous PASSes. |
| H07 | Canonical witnesses lacked tags, widths, controller/scheduler grammar, and viewer admissibility. | Use the AI/D reversed-edge pair. EncCut, tables, scope admissibility, and the Section 8.7 order are exact; SELECTOR must actually separate. | **PASS (formal)** | Byte production moves to D/G closure and the canonicalizer. Exact emitted lists, bytes, and implementation agreement remain UNKNOWN. |
| H08 | `[T]` has two interrupted gaps, so old padding omitted one branch slot. | One-message future T has distinct pre-A and post-A crash cuts; both produce OLD/NEW families. | **PASS** | Both phases are in the declared corpus (`24,649` each). R0.1J makes no obsolete 3,838,493 prediction. Enumeration cost remains charged. |
| H09 | Recovery cut placement, inherited d, label behavior, and terminal inclusion yielded incompatible conditional quotients. | Every recovery cut is after DOWN/before recovery; d is folded from ordinary C; no recovery crash exists; FIN-pending and terminal are explicit. | **PASS** | The single router/condition fold replaces conditional quotient families. Router exactness is now the fresh F01 pressure. |
| H10 | Meta-classifier input grammar and refusal precedence were absent. | Standalone top-level magics and witness precedence are explicit; raw operational reasons have an order. Force SELECT old at a pending cut to exercise fresh F01's remaining raw-role hole. | **FAIL**, already F01 | Old absence is largely fixed, but the last complexity sits in exact router membership and raw-role classification. |
| H11 | A claimed 2,304 phase-state bound was only multiplication, not an executed phase closure. | R0.1J makes no 2,304 claim and leaves numeric D/G sizes UNKNOWN. | **PASS by withdrawal** | No closure-size credit is issued. The finite algorithms, evaluator work, and memory remain charged. |
| H12 | Exact-history interpretation needed an injective encoding that was not supplied. | EncCut is magic plus a length-delimited exact trace, validates membership, and has no repeated semantic fields. Arbitrary interpreter requests remain unsupported. | **PASS for supported EncCut; UNKNOWN outside scope** | Injectivity is formal. General interpretation/version behavior is not claimed. |
| H13 | Recovery responsibilities and MAY FORGET claims lacked exhaustive cut classes and deletion witnesses. | Replay Q7: clean `H()` versus its initial DOWN-idle recovery cut at the same r,d. | **FAIL**, already F05 | R0.1J supplies S1–S5/R1–R4/F1–F5, but omits the recovery-closure-owed responsibility and leaves its separate minimal order incomplete. |
| H14 | Physical completion, power loss, externalization, human cognition, TCB closure, and unlike realizations were unevidenced. | No finite FORMAL suffix can instantiate the missing physical or human premise. | **UNKNOWN** | R0.1J explicitly admits FORMAL only and accounts for these influences without claiming success. |

### H-era stable results

The clean counts, one-X PUBLIC separator, H()/H(RI) intended merger,
failure-free reply table, A crossing count, and 3,910,242 corrected padded-slot
arithmetic all survive. They are mathematical boundary results only.

## 3. R0.1I counterexample replay

| ID | Prior counterexample | Smallest R0.1J replay | Verdict | Fixed behavior or moved complexity |
|---|---|---|---|---|
| I01 | Same-cut-kind comparability forbade the T/no-op mergers used by 139/315; literal counts were 238/415. | At `(U,EMPTY,E0),d=2`, compare interrupted no-op RI with T interrupted before A; also compare T pre-A/post-A. | **PASS** | `==J` has no kind gate. Equal suffix functions merge; the recounted recovery result is 139/315. Complexity moves to one total phase router. |
| I02 | “No empty separator” was false contractually because an initial idle crash exposed residual through F. | Clean `H()` versus `H(O0)`; choose FIN and crash before it. SELECTOR/PRIV separates with zero ordinary C; PUBLIC still needs X. | **PASS** | R0.1J states the viewer-relative minima explicitly and encodes separate PUBLIC/contractual witness searches. |
| I03 | EncCut optional residual/alias fields lacked a presence map and could disagree with the trace. | Encode any clean or recovery cut. EncCut contains only its exact prefix; every residual, alias, d, and phase is derived. | **PASS** | The repeated-authority fork is deleted. Work moves to exact prefix validation and fold logic. |
| I04 | Conceptual branch fields and EncBranchRecord disagreed about residual/phase/fold population. | Use interrupted AI. Obs_PRIV is only the ordered exact full suffix sequence; SELECT, RESUME, ALLOWANCE, and READY are in the trace. | **PASS** | Redundant record fields are removed. Validation moves to the formal generator and raw-evidence comparison. |
| I05 | A lower viewer code could canonicalize a witness that did not separate; Priv had no scope code. | Use AI EMPTY→ID versus D ID→EMPTY. EncWitness rejects CLIENT/CAPTURE/PUBLIC and admits SELECTOR or PRIV only. | **PASS** | Scope eligibility is contractual and PRIV has code 4. Canonicalizer complexity remains charged. |
| I06 | Must could inspect suffix only or prefix+suffix; its Boolean mask conflated vacuous and operational truth. | Interrupt no-op RI and inspect the full ordered family; no Must mask is encoded or used by `==J`. | **PASS by scope closure** | Validation evidence is separate. Arbitrary quantifier/vacuity capability remains UNKNOWN. |
| I07 | G could include only pre-crash keys or also ignored post-crash keys, changing scheduler bytes. | R0.1J records a G key iff crash budget is one; after crash the scheduler is not invoked and recovery cuts add none. | **PASS** | The closure choice is exact. Numeric G, runtime, and an independent emitted list remain UNKNOWN. |
| I08 | Canonical object dispatch, wrong repeated-field handling, and witness viewer precedence were incomplete. | Present a standalone object or malformed witness under its distinct magic; EncCut has no repeated fields and scope is checked for separation. | **PASS for Section 8** | The old parser forks are closed. Manifest classification has the different fresh F02–F04 failures. |
| I09 | X was used as if it supplied viewer-relative causal/counterfactual explanation. | Ask X after any hidden selector cause. It returns only the current residual/value. | **PASS by narrower claim; capability UNKNOWN** | R0.1J claims immediate state explanation, not arbitrary causal lineage. It receives no B02 capability credit. |
| I10 | Generated formal outcomes could not represent wrong/malformed observations for negative verification. | Encode an origin-1 raw family with a wrong tag, payload, order, duplicate, or empty family. | **PASS for finite completed evidence** | Formal and raw carriers are separated. A partial trace plus timeout remains unrepresentable: fresh F02. |
| I11 | A same input description could lack total semantics at mismatched phases; the unified quotient needed a common router. | At a pending cut force raw SELECT old; or reach active FIN-pending after typed FIN. | **FAIL**, already F01 | Globally legal Ctl/Sch evaluation is substantially fixed; raw-role and literal router coverage remain incomplete. |
| I12 | Clean and recovery cuts had not been compared; a merger was assumed or counts were merely added. | Choose FIN/pass from every clean and recovery condition. Clean begins FIN; recovery begins READY and has nonempty selector evidence. | **PASS** | Exhaustive collision check finds none. Combined formal counts are 153 PUBLIC and 329 contractual. The owed-recovery distinction becomes the missing F05 responsibility. |
| I13 | Pre-A/post-A service continuation was conflated with the already crossed A historical fact. | Compare T recovery cuts immediately before and after A. All suffix functions agree; the latter exact prefix alone contains A. | **PASS (formal)** | Service continuation phase may merge while exact evidence retains A. Capture durability and manifest availability remain UNKNOWN. |
| I14 | Manifest evidence and between-execution necessity were conflated. | Delete/retain an external manifest while holding the cut and policies fixed; FORMAL Obs values do not change. | **PASS as a mathematical separation** | Evidence retention moves to an external ledger. F02–F04 show that the new evidence carrier/classifier is not yet sufficient operationally. |
| I15 | D/G sizes, exact recovery class histograms, and canonical bytes were asserted without independent closure. | R0.1J leaves D/G and witness bytes UNKNOWN. Independent symbolic lifting supplies exact 153/329 history histograms but not canonical policy bytes. | **PASS by claim discipline; byte agreement UNKNOWN** | Closure computation and canonicalizer remain explicit work, not hidden constants. |
| I16 | Persistence labels lacked one permitted collision or named total derivation per responsibility. | Clean `H()` versus its initial idle recovery cut replays the unclassified recovery-closure obligation; S3/S4 also expose the incomplete Section 10 family-count order. | **FAIL**, already F05 | Several old overclaims are now deliberately unclassified, but the claimed S1–S5 deletion gate is still incomplete. |

## 4. Replay of the five frozen R0.1J failures

| Fresh failure | Nearest archive pressure | Archive disposition | Smaller R0.1J witness added? |
|---|---|---|---|
| F01 raw phase/router totality | H03/H04/H10 and I11 | Confirms that exact phase routing and common policy identity are the right boundary. | **No new witness.** The zero-ordinary active-FIN state after `H(); FIN` is already named in F01 and is smaller than the one-ordinary forced-selector illustration. |
| F02 partial timeout evidence | R0.1I B08 was UNKNOWN; old reports had no raw timeout carrier | New J-specific evidence-encoding defect. | **No.** One captured FIN before expiry is the minimum nonempty partial observation. |
| F03 UNKNOWN masks conformance FAIL | Old reports required “one FAIL dominates,” but had no multi-case manifest codec | New J-specific classifier-composition defect. | **No.** Two cases are necessary: one UNKNOWN and one independent FAIL. |
| F04 unbound envelope-dependent verdict | Old EXTERNALIZE/manifest/TCB pressures were UNKNOWN | New J-specific binding defect. | **No.** One timeout case and two external envelope contexts are minimal. |
| F05 missing recovery-owed responsibility/minimal order | H13 and I12/I16; Q7 already supplied the pair | Archive independently corroborates the omitted behavioral lower bound. | **No.** Clean `H()` and its initial idle recovery cut use zero ordinary C on both sides. |

Thus archive replay changes no fresh verdict. It prevents the valid formal
repairs from being mistaken for deletion of the work now carried by router,
selector, controller, evidence, canonicalizer, or external context.

## 5. Complexity-movement ledger

| Old ambiguity or conflation | R0.1J location of the responsibility | Replay status |
|---|---|---|
| Interrupted application versus R completion | F:SELECT rule and exact application fold | Formal behavior fixed; selector/fold implementation UNKNOWN |
| Public prefix versus full history | EncCut, suffix projections, SELECTOR, PRIV | Formal distinction fixed; evidence retention external |
| Adaptive schedule identity | D/G union closures and total Ctl/Sch tables | Formal grammar fixed; availability, emitted closure, and runtime UNKNOWN |
| Client versus capture visibility | CLIENT/PUBLIC/CAPTURE projections | Formal permissions fixed; capture authenticity/durability UNKNOWN |
| Hidden branch carrier and Must | Ordered full family plus separate evidence | Formal family fixed; arbitrary quantifier capability withdrawn |
| Phase comparability | One all-cut relation and router | Quotient fixed; raw/router gaps remain F01 |
| Canonical authority | Prefix-only EncCut and Section 8 well-order | Formal algorithm fixed; independent bytes/TCB UNKNOWN |
| Malformed implementation output | EncRawFamily and manifest classifier | Completed malformed evidence fixed; F02–F04 remain |
| Persistence versus falsification evidence | Sections 9 and 10 separate ledgers | Separation fixed; F05 ledger completeness fails |
| Physical/human/external guarantees | Explicitly outside FORMAL and charged in accounting | UNKNOWN; no scope exclusion becomes PASS evidence |

Moving a responsibility is not deleting it. In particular, dropping repeated
cut fields increases reliance on exact prefix validation; dropping Must moves
branch truth work to evidence/adjudication; one global scheduler moves replay
identity into G and its external availability; and externalizing manifests and
envelopes creates binding, retention, and TCB obligations.

## 6. Final archive disposition

The archive confirms that R0.1J materially fixes the earlier finite semantic
failures:

- selected application is distinct from ordinary R completion;
- one exact all-cut relation replaces the kind gate;
- public and privileged minima are viewer-correct;
- recovery cut, allowance, T stages, FIN-pending, and terminal behavior are
  explicit;
- EncCut has one authority;
- formal outcomes and completed raw observations are separate; and
- Section 8 canonical witness scope and ordering are complete as a formal
  algorithm.

Those repairs do not reverse the frozen fresh FAIL. The archive adds no new or
smaller counterexample beyond the zero-ordinary router and Q7 subwitnesses
already present there. Partial-timeout loss, manifest verdict masking, unbound
envelope context, and the incomplete mandatory persistence ledger remain
decisive.

All implementation, architecture, storage, physical persistence, power-loss,
external availability, human cognition, cross-realization, and TCB claims stay
UNKNOWN.
