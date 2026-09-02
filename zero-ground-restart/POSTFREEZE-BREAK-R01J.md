# ZERO GROUND R0.1J — Post-Freeze Blind Break

## 0. Frozen authority and audit boundary

The candidate was hashed before it was read. Its SHA-256 is exactly:

    7c9b2a742eab81f6c104b6ca3566315ddb29ecc63d216d25cff91bf1c70836dc

This audit used only:

- `HISTORY-SEED-R01J.md`, the candidate above; and
- `BLIND-ATTACK-PACK-R01I.md`, SHA-256
  `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b`.

No R0.1I candidate, archive, builder artifact, implementation, proposed
repair, or prior solution was read or used as an audit source. This report
tests a frozen finite contract. A formal PASS below is not architecture,
persistence, physical recovery, human comprehension, external-service
availability, or implementation evidence.

## 1. Executive verdict

**FAIL.** The central finite quotient is coherent: independent enumeration
reproduces 153 PUBLIC outcome functions and 329 all-scope classes. The failure
comes from five surrounding contractual defects:

1. The purported total phase router does not totalize an in-phase raw selector
   invocation, and its table omits reachable post-FIN and later post-recovery
   active-idle routes.
2. A timed-out raw observation cannot retain any crossings captured before the
   bound expired.
3. One timeout case can make a multi-case manifest return UNKNOWN even when a
   different case is a finite conformance FAIL.
4. The same EncManifest bytes can classify as UNKNOWN or FAIL according to an
   experiment envelope that is neither encoded nor cryptographically linked
   by the manifest.
5. The persistence-responsibility ledger omits the clean-active versus
   DOWN-idle recovery distinction proved necessary by the candidate's own Q7,
   and its separate “smallest” witness order is incomplete for branch families.

The first four are finite totality/evidence defects. The fifth does not falsify
the mathematical quotient; it falsifies the claim that S1–S5 form the stated
smallest mandatory deletion/merge ledger.

## 2. Independent bounded recount

### 2.1 Clean corpus

Direct enumeration of the twelve-message transition function gave:

| Quantity | Result |
|---|---:|
| Words of length 0..2 | 157 |
| Reachable residuals | 14 |
| Same-residual unordered pairs | 2,351 |
| Unequal-residual unordered pairs | 9,895 |
| Total unordered pairs | 12,246 |

The clean class multiset is exactly:

    59, 17, 17, 16, 16, 16, 2, 2, 2, 2, 2, 2, 2, 2.

The reachable residual counts after zero, one, two, and three completed future
requests are `14, 18, 18, 18`.

### 2.2 Recovery conditions and formal quotient

Folding every clean residual through every future word at the permitted depths
reproduced all 854 normalized recovery conditions:

| Family | Conditions |
|---|---:|
| Idle active | 68 |
| Changing pending non-T | 195 |
| No-op pending non-T | 355 |
| T before A | 50 |
| T after A | 50 |
| FIN-pending sources | 68 |
| Terminal sources | 68 |
| **Total** | **854** |

Their exact-prefix lift weights sum to 1,208,272. The recovery quotients are:

| Remaining condition | PUBLIC functions | All-scope classes |
|---|---:|---:|
| Active `d=3` | 14 | 14 |
| Active `d=2` | 59 | 89 |
| Active `d=1` | 63 | 105 |
| Active `d=0` | 1 | 105 |
| FIN-pending and terminal | 2 | 2 |
| **Recovery total** | **139** | **315** |

The all-scope recovery multiplicity histogram is exactly
`263×1, 9×8, 27×9, 14×10, 2×68`.

The FIN/all-zero-scheduler continuation was checked against every recovery
condition. A clean suffix has PUBLIC shape `FIN, STOPPED`; every active
recovery suffix begins with READY, FIN-pending has `READY, STOPPED`, and
terminal has `READY`. SELECTOR is empty for the clean no-crash suffix and
nonempty for every recovery suffix. There is no clean/recovery collision.

Therefore the combined normalized results are exactly:

    PUBLIC:     14 + 139 = 153
    all-scope:  14 + 315 = 329

and the predicted combined all-scope histogram is exactly:

    277×1, 9×8, 27×9, 14×10, 2×68.

### 2.3 Exact-history lift

Although the candidate leaves the exact-history multiset UNKNOWN, the finite
condition frequencies support an exact symbolic lift. No hash equality or
sampling is used: every exact prefix contributes once to its normalized
condition, and the formal continuation depends only on that condition.

The combined PUBLIC exact class-size histogram is:

    2×28, 4×6, 6×4, 12×4, 16×14, 17×6, 18×2, 19×4,
    32×1, 34×1, 50×4, 53×4, 59×9, 68×2, 71×4, 73×2,
    75×2, 100×1, 106×5, 187×6, 191×2, 216×2, 241×2,
    269×4, 282×4, 315×2, 335×1, 369×2, 374×1, 432×1,
    445×3, 632×2, 917×1, 1278×2, 1410×4, 1479×2,
    3437×2, 3792×1, 4439×2, 7049×1, 295945×2,
    565200×1.

It contains 153 classes and sums to 1,208,429 histories.

The combined all-scope exact class-size histogram is:

    2×46, 6×16, 16×20, 17×12, 18×6, 20×2, 50×10, 53×28,
    59×7, 60×4, 128×2, 144×1, 153×2, 187×12, 191×5,
    216×10, 222×16, 445×6, 450×2, 472×1, 477×4, 530×2,
    828×10, 933×20, 949×8, 1496×2, 1719×1, 1941×12,
    1944×2, 2073×5, 2220×4, 2495×10, 3489×6, 3560×1,
    5152×4, 7452×2, 8397×4, 9490×2, 11466×2, 13766×4,
    14502×2, 15528×2, 18657×1, 19017×2, 21729×1,
    22455×2, 27810×2, 27912×1, 28305×1, 295945×2.

It contains 329 classes and also sums to 1,208,429 histories. This is a formal
mathematical result, not an implementation or storage fact.

## 3. Minimized finite breaks

### F01 — The raw phase-action router is not total

The formal `Eval(H,Ctl,Sch)` interface is total over its encoded tables, but the
candidate separately claims a total raw phase-action refusal. That claim has a
hole at the smallest selector barrier.

Take clean `H()`, let `C:REPLACE ID` cross, crash before its R, and stop at the
declared pending recovery cut. Now submit the raw role invocation “force
`SELECT old`.”

- Section 4.2 says only a pending-request condition admits SELECT.
- The Section 4.4 router says that at this phase both labels are enumerated; it
  consumes no selector policy input.
- Section 5.3 likewise says the semantic result enumerates both instead of
  choosing one.
- The raw refusal covers only a forced SELECTOR **outside** the router.

This invocation is not outside the selector phase, but it is also not an
encoded policy and cannot produce the required two-branch family if accepted
as a forced OLD choice. No result or precedence rule covers it. The smallest
case uses one pre-cut ordinary C and zero post-cut ordinary C.

The supposedly total router table also omits two reachable configurations:

1. after typed FIN has crossed and before STOPPED, with crash budget still
   one; and
2. active idle after a post-recovery request has completed, with crash budget
   zero and another allowance unit remaining.

Other sections imply the intended behavior—offer STOPPED to the scheduler in
the first case and reconsult the controller without a scheduler in the
second—but those configurations have no row in the table that the evaluator
is said to follow. The initial pre-action crash text also never states in one
normative rule that the unoccurred proposal is discarded before the
post-READY controller key is consulted. These omissions need explicit router
rows; cross-section reconstruction is not the claimed total router.

**Verdict:** FAIL for B00 and for the router-totality part of B20. This does not
change the quotient arithmetic obtained under the evident intended routing.

### F02 — Timeout cannot retain a captured partial observation

Use the candidate's own smallest nonempty complete suffix: clean `H()`,
controller FIN, scheduler pass. The formal family is one trace containing
typed FIN followed by typed STOPPED.

Let a candidate realization expose FIN, then fail to expose STOPPED before the
declared observation bound expires. The evidence must record both facts:

1. raw FIN was captured; and
2. the family was incomplete when the bound expired.

`result-kind=0` can carry the one-crossing partial raw family, but the
classifier treats it as complete and returns `FAIL(CONFORMANCE)`. Conversely,
`result-kind=1` records expiry but requires an empty body, discarding the FIN
that was captured. No EncEvidenceObservation carries partial bytes plus the
expiry marker.

The candidate says raw evidence records what was captured and must carry a
nonterminating observation. The smallest one-crossing partial case disproves
that claim.

**Verdict:** FAIL for B08 and the evidence side of B00.

### F03 — UNKNOWN masks an independent finite FAIL

Construct a sorted, duplicate-free two-case manifest using any one valid cut,
controller, and scheduler:

- case A has `origin=1`, `result-kind=0`, and a finite raw family unequal to
  the formal family, so it is a `FAIL(CONFORMANCE)` case;
- case B has `origin=1`, `result-kind=1`, with no envelope evidence that the
  expiry violated a contract-authorized bound, so it is
  `UNKNOWN(OBSERVATION_BOUND)`.

The cases have different bytes and are not duplicates. The manifest
classifier checks UNKNOWN/FAIL(NON_TOTAL) before FAIL(CONFORMANCE), so this
manifest returns UNKNOWN and suppresses case A's finite counterexample.

That contradicts the blind pack's mandatory verdict discipline: one finite
FAIL dominates any number of UNKNOWN cases. It also contradicts the useful
meaning of a multi-case falsification manifest.

**Verdict:** FAIL. The minimal repair is to return a per-case verdict vector or
to place every finite FAIL category before UNKNOWN.

### F04 — Manifest classification depends on an unbound envelope

Use a one-case valid manifest whose sole evidence observation has
`result-kind=1`. Hold every manifest byte fixed and present two separately
signed experiment envelopes:

- one does not establish a contract-authorized observation bound, yielding
  `UNKNOWN(OBSERVATION_BOUND)`; and
- one establishes that expiry violated such a bound, yielding
  `FAIL(NON_TOTAL)`.

EncManifest contains neither an envelope identifier nor a digest of the
governing envelope. Section 8.8 nevertheless dispatches an EncManifest as a
top-level binary object to a “total evidence classifier.” Thus the same
top-level bytes have two results, and nothing selects which of multiple signed
envelopes governs.

Charging envelope context externally is sound accounting; leaving it unbound
to an allegedly total manifest classification is not. The classifier must be
defined over an encoded `(manifest,envelope)` pair or the manifest must commit
to the envelope identity.

**Verdict:** FAIL for the manifest-identity pressure in B31. TCB trust in the
signer remains separately UNKNOWN.

### F05 — The mandatory persistence ledger omits Q7's distinction

Compare:

- the clean `H()` cut; and
- its initial idle recovery cut after
  `F:CRASH GAP=0; L:DOWN`.

Both derive `(U,EMPTY,E0), d=3`. Choose FIN everywhere and use the all-zero
scheduler. The clean PUBLIC suffix is `FIN, STOPPED`; the recovery PUBLIC
suffix is `READY, FIN, STOPPED`. SELECTOR is empty on the clean side and begins
`RESUME ACTIVE ...; ALLOWANCE 3` on the recovery side. This is Q7 and uses zero
post-cut ordinary C.

Therefore enough information to distinguish clean active from DOWN-idle
recovery—equivalently, whether mandatory recovery closure is owed—must survive
somewhere in the declared total system. S1 preserves O/P/G, S2 preserves d,
S3 preserves idle versus interrupted recovery, S4 preserves direction, and S5
preserves FIN-pending versus terminal. None preserves clean active versus DOWN
idle when r and d agree.

Section 10 then says no other responsibility receives a label, and Section 12
defines DELETE/MERGE only over S1–S5. A realization could erase Q7's phase
obligation without exercising any listed deletion witness, despite violating
the 329-class relation.

The persistence witness order has a second reproducibility gap: unlike Section
8.7, Section 10.1 does not say whether post-cut counts over two branch families
are maxima, sums, deduplicated-viewer counts, or selected-branch counts, and it
does not define “number of differing prefix crossings” for unequal-length
sequences. Thus the word **exact** in the S3/S4 smallest-witness claims is not
algorithmically justified.

**Verdict:** FAIL for the claimed S1–S5 mandatory ledger and its exact
minimality. Add the Q7 phase obligation and reuse Section 8.7's explicit
family aggregation plus an exact prefix-distance definition.

## 4. Formal/raw and canonical checks that did hold

The finite failures above should not obscure four successful repairs:

1. EncCut carries one exact prefix authority and no optional semantic fields.
2. A formal Obs_PRIV is derived and strictly validated, while malformed finite
   realization output is representable through EncRawFamily. Wrong tags,
   payloads, branch order, duplicates, and empty families therefore reach a
   falsification verdict instead of being rejected as formal outcomes. F02 is
   specifically the remaining partial-timeout hole.
3. EncWitness requires the named scope itself to separate. Q4 therefore cannot
   select CLIENT merely because its code sorts before SELECTOR.
4. Section 8.7's witness order explicitly aggregates maxima and sums over both
   complete families, includes scope admissibility, and ends in exact bytes.
   Given fixed D/G, it is a finite well-order and selects a unique formal
   witness. No finite Section 8.7 ambiguity was found.

The exact D/G lists and witness bytes were not independently emitted in this
audit, so cross-implementation byte agreement remains UNKNOWN rather than
receiving PASS from this static review.

## 5. Frozen-prediction audit

| Prediction | Verdict | Independent result |
|---:|---|---|
| 1 | PASS | Recounted 157 clean, 1,208,272 recovery, and 1,208,429 total cuts. |
| 2 | PASS | Recounted fourteen clean classes and the 2,351/9,895 pair split. |
| 3 | PASS (formal) | Initial pre-FIN crash exposes the injective residual in SELECTOR/PRIV with zero ordinary C. |
| 4 | PASS (formal) | Every zero-ordinary-C PUBLIC schedule is residual-blind; one X reply is injective. |
| 5 | PASS (formal) | Exact induction on `(r,d,crash budget,phase)` preserves every same-residual clean pair. |
| 6 | PASS | Recounted 139 recovery PUBLIC functions and 315 all-scope classes. |
| 7 | PASS | Recounted 153/329 over the all-cut relation; no clean/recovery collision. |
| 8 | PASS | Recounted `277×1,9×8,27×9,14×10,2×68`. |
| 9 | PASS (formal) | OLD applies nothing, NEW applies delta exactly once, and neither emits the interrupted R. |
| 10 | PASS (formal) | Prefix plus blind retry has one A in the pre-A case and two in the post-A case; suffix observations alone remain equal. |
| 11 | PASS (formal) | FIN-pending recovery emits one STOPPED; terminal recovery emits none. |
| 12 | UNKNOWN | Primitive codecs and witness well-order are exact, but D/G lists, canonical bytes, independent implementations, and the router gaps in F01 were not resolved by an emitted closure. |

Predictions 1–11 are finite formal statements only. They supply no realization
or persistence evidence.

## 6. Mandatory individual attack verdicts

`PASS (formal)` below means the frozen transition system itself supplies the
finite result. It does not credit an implementation or physical system.

| Attack | Verdict | Evidence |
|---|---|---|
| B00 Totality envelope | **FAIL** | F01 leaves an in-phase raw selector invocation and reachable router states without one total routing rule; F02 also prevents faithful timeout evidence. |
| B01 Full history vs projection | PASS (formal) | T pre-A/post-A cuts preserve their exact-prefix A difference while equal suffix projections do not assert equal full histories. |
| B02 Viewer-relative explanation | UNKNOWN | X explains current residual state, not the pack's hidden causal prerequisite and counterfactual; no authorized causal-explanation adjudicator exists. |
| B03 Attempt/deny/apply/complete | UNKNOWN | C/A/R/SELECT are formal, but denied-before-occurrence and independently completed physical effects are unsupported. |
| B04 Permission change | UNKNOWN | Authentication, authorization, and permission-time semantics are unsupported. |
| B05 Occurrence/application/completion | UNKNOWN | Occurrence and formal application are exact; external completion and a physical crash cut are absent. |
| B06 Crash after physical completion | UNKNOWN | Physical completion, effect counting, and retry guarantees are outside the admitted realization. |
| B07 Rejected/failed/no-op/success | UNKNOWN | Ordinary ERR/no-op/success replies exist, but the four action-effect classes and physical completion evidence do not. |
| B08 Truncation vs absence | **FAIL** | F02 cannot encode a captured partial family together with observation-bound expiry. |
| B09 Labeled nondeterminism | PASS (formal) | OLD/NEW remain ordered and labeled in SELECTOR/PRIV before projected trace-set deduplication. |
| B10 Repetition vs determinism | PASS (formal) | The only admitted realization has a finite exact branch generator; the candidate explicitly refuses to generalize this to implementations. |
| B11 Scheduler identity | PASS (formal) | One global PUBLIC-suffix/next-crossing vector fixes every reached adaptive scheduling choice. |
| B12 Scheduler context loss | UNKNOWN | Controller/scheduler severing and recovery availability have not been exercised. |
| B13 MAY vs MUST | UNKNOWN | R0.1J deliberately exposes no arbitrary predicate or MAY/MUST query interface, so the executable two-carrier test is absent. |
| B14 Empty-carrier vacuity | UNKNOWN | The candidate avoids a Must truth mask but supplies no q/¬q carrier-query interface or human guarantee response to execute. |
| B15 Carrier projection collision | PASS (formal) | Q4 preserves both full branches; PUBLIC forgets only orientation whose PUBLIC futures agree, while SELECTOR/PRIV retains it. |
| B16 Exact depth | PASS (formal) | d decrements on ordinary C, FIN is forced at zero, and beyond-bound descriptions receive the allowance refusal. |
| B17 Phase-specific capability | UNKNOWN | The formal C-occurrence rule is exact, but external controller preservation/severing is untested. |
| B18 Empty recovery drift | PASS (formal) | The one permitted empty recovery consumes no ordinary allowance; a second crash is explicitly refused. No physical repetition claim follows. |
| B19 Exhausted recovery | PASS (formal) | d=0 forces FIN and the raw ordinary-action boundary returns the allowance refusal. |
| B20 Graceful termination cuts | **FAIL** | FIN-pending and terminal traces are declared, but the claimed total router omits the reachable active post-FIN/pre-STOPPED row identified in F01. |
| B21 Crash as physical terminal | UNKNOWN | No physical or irrecoverable crash is admitted. |
| B22 Post-terminal continuation | PASS (formal) | C/R cannot continue; raw post-terminal role actions terminate with the phase refusal and add no crossing. |
| B23 Canonical diamond | PASS (formal) | Scope admissibility and the nine-part Section 8.7 well-order select one witness for every finite separable pair. |
| B24 External canonicalizer context | UNKNOWN | The formal order is fixed, but no independent canonicalizer or context perturbation was run. |
| B25 Evolution reinterpretation | UNKNOWN | E0→E1 is residual evolution, not a two-specification meaning change. |
| B26 Cross-version author/apply | UNKNOWN | Cross-version authored actions are unsupported. |
| B27 Unknown future extension | UNKNOWN | Future-version requests are explicitly outside the claimed semantic domain. |
| B28 External controller | UNKNOWN | Ctl is in the formal determination scope, but independent context variation/severing was not run. |
| B29 Capture omission | UNKNOWN | Capture availability, completeness, and physical history are untested. |
| B30 External selector | UNKNOWN | Both formal labels are enumerated; no external selector realization or perturbation exists. |
| B31 Manifest/spec identity | **FAIL** | F04 gives the same EncManifest identity two classifier results because its governing envelope is unbound. Signer trust remains UNKNOWN. |
| B32 Human-local burden | UNKNOWN | No human resource bound or controlled review exists. |
| B33 Quantifier/vacuity cognition | UNKNOWN | No MAY/MUST presentation or human trial exists. |
| B34 TCB closure | UNKNOWN | Influences are listed but not independently perturbed; F04 shows that envelope binding must join that surface. |
| B35 Circular validation | UNKNOWN | The candidate correctly says origin-0 agreement is not an independent verifier test, but no independent oracle was run. |
| B36 Unlike realizations | UNKNOWN | FORMAL is the only admitted realization and has no physical evidence. |
| B37 Simulated vs physical completion | UNKNOWN | Physical completion is excluded and unevidenced. |
| B38 Cross-realization canonicality | UNKNOWN | No cross-realization canonical or physical-witness claim is made or tested. |

## 7. Mandatory composite verdicts

| Composite | Verdict | Evidence |
|---|---|---|
| C1 Projection × action × crash | UNKNOWN | Projection and formal application are exact, but hidden-cause explanation and physical completion are unavailable. |
| C2 Nondeterminism × scheduler × evolution | UNKNOWN | Branch and scheduler semantics are finite; specification evolution and recovered external scheduler context are unsupported/untested. |
| C3 MAY/MUST × depth × recovery | UNKNOWN | Depth/recovery are formalized, but there is no executable MAY/MUST predicate interface or external recovery evidence. |
| C4 Terminal × physical realization | UNKNOWN | Formal terminal traces cannot supply irrecoverable-crash or unlike physical-realization evidence. |
| C5 Canonical × viewer × external context | UNKNOWN | The formal witness order passes static review, but no external canonicalizer perturbation exists. F04 separately fails manifest-envelope identity, not Section 8.7 witness choice. |
| C6 Human × TCB × vacuity | UNKNOWN | No q/¬q carrier presentation, human study, independent oracle, or TCB perturbation exists. |

## 8. Persistence and claim separation

The candidate is correct that a falsification manifest is evidence for a claim
and is not automatically service continuation state. Deleting the manifest
can destroy auditability without changing FORMAL `Obs_v`; that conditional
separation is mathematically sound.

It does not follow that any physical responsibility has been deleted,
externalized safely, reconstructed after failure, or realized. In particular:

- F05 requires adding the clean-active/DOWN-idle recovery obligation to the
  behavioral lower-bound ledger;
- F02–F04 require a lossless, context-bound evidence carrier before manifest
  retention claims can be tested operationally; and
- DELETE, DERIVE, RECOMPUTE, EXTERNALIZE, REALIZE, COGNITION, and TCB remain
  UNKNOWN exactly as the candidate states.

## 9. Final classification

R0.1J successfully freezes a coherent one-relation formal quotient and repairs
the principal formal/raw and canonical-scope confusions: the independently
recounted answer is 153 PUBLIC functions and 329 contractual classes.

It does not pass the blind pack. The raw router is not total at every role
boundary, partial timeout evidence is unrepresentable, the manifest can mask a
finite FAIL and has an unbound envelope-dependent verdict, and the mandatory
persistence ledger omits a smallest Q7 obligation. One finite counterexample
dominates the valid formal predictions.

All architecture, implementation, physical persistence, power-loss,
completion, external-service, human, and TCB conclusions remain UNKNOWN.
