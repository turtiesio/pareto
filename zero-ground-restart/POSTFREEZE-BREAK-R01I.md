# ZERO GROUND R0.1I — Post-Freeze Blind Break

## 0. Frozen authority and audit boundary

This report evaluates the immutable R0.1I candidate using only:

- `BLIND-ATTACK-PACK-R01I.md`, SHA-256 `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b`;
- `HISTORY-SEED-R01I.md`, SHA-256 `d52c083c34aa37144fa47ee8a02d9279adb75029613125f38dad5a98b0df8d9c`.

Both hashes were independently verified before analysis. No earlier candidate, history, archive, implementation, other report, or git history was inspected.

The candidate is a finite specification, not an implementation or run (`HISTORY-SEED-R01I.md:5-7`). Consequently:

- finite claims implied by its frozen transition rules can receive PASS or FAIL from independent exhaustive enumeration;
- a finite internal counterexample is a FAIL even without an implementation;
- physical, runtime, recovery-severing, human, realization, and TCB claims remain UNKNOWN without the required experiments;
- an explicit scope exclusion is never counted as capability evidence.

## 1. Executive verdict

**FAIL.** The frozen candidate has four independent finite defects:

1. Its 315-class “contractual” recovery quotient merges cut kinds that its equivalence rule forbids comparing. Literal application produces **415**, not 315, contractual classes.
2. Its “no empty separator” prediction is false. A pre-FIN idle crash distinguishes unequal clean coordinates in SELECTOR/Priv with zero ordinary client messages.
3. Its supposedly exact canonical encoding omits normative choices needed to produce one byte string.
4. Its canonical witness format does not define which viewer code is admissible; a SELECTOR-only distinction can therefore canonicalize either as SELECTOR or, by raw byte order, CLIENT.

The candidate also supplies no PASS evidence for its explicitly unexecuted DELETE, DERIVE, RECOMPUTE, EXTERNALIZE, REALIZE, COGNITION, or TCB gates (`HISTORY-SEED-R01I.md:850-852`). Those dimensions remain UNKNOWN rather than inheriting this finite-model FAIL.

## 2. Independent exact recount

### 2.1 Clean corpus

An independent transition enumerator reproduced:

| Quantity | Exact result |
|---|---:|
| Words of length 0..2 over 12 messages | 157 |
| Reachable clean coordinates | 14 |
| Class sizes | `59, 17, 17, 16, 16, 16, 2, 2, 2, 2, 2, 2, 2, 2` |
| Same-coordinate unordered pairs | 2,351 |
| Unequal-coordinate unordered pairs | 9,895 |
| All unordered pairs | 12,246 |

The reachable-coordinate counts after zero, one, two, and three completed future messages are respectively `14, 18, 18, 18`.

### 2.2 Exact recovery-prefix corpus

| Phase | Per clean history | Across 157 clean histories |
|---|---:|---:|
| Idle | 1,885 | 295,945 |
| Pending non-T | 1,727 | 271,139 |
| T before A | 157 | 24,649 |
| T after A | 157 | 24,649 |
| FIN-pending | 1,885 | 295,945 |
| Terminal | 1,885 | 295,945 |
| **Total recovery prefixes** | **7,696** | **1,208,272** |

Adding the 157 clean cuts gives exactly **1,208,429** cut histories.

### 2.3 Normalized conditions

The normalized recount is:

| Family | Exact conditions |
|---|---:|
| Idle active | 68 |
| Changing pending non-T | 195 |
| No-op pending non-T | 355 |
| T before A | 50 |
| T after A | 50 |
| FIN-pending sources | 68 |
| Terminal sources | 68 |
| **Total** | **854** |

The no-op non-T classes have 6, 7, or 8 request identities. Across the 50 `(residual,d)` sources their distribution is `9×6, 27×7, 14×8`.

### 2.4 Public and privileged quotients

The frozen text defines equivalence only for equal cut kinds and equal live-allowance contracts (`HISTORY-SEED-R01I.md:454-465`). It separately assigns distinct codes to IDLE, PENDING_NON_T, T_PRE_A, and T_POST_A (`HISTORY-SEED-R01I.md:663-666`). The reported 139/315 counts instead collapse active conditions across those kinds.

Both readings were enumerated:

| Reading | PUBLIC classes | Priv classes | Priv normalized multiplicity histogram |
|---|---:|---:|---|
| Cross-kind observational/behavioral collapse used by the printed counts | 139 | 315 | `263×1, 9×8, 27×9, 14×10, 2×68` |
| Literal same-cut-kind rule | **238** | **415** | `363×1, 9×6, 27×7, 14×8, 2×68` |

The 139 count remains a useful **observational PUBLIC continuation quotient** because the candidate expressly labels it non-contractual (`HISTORY-SEED-R01I.md:567-580`). It cannot repair the contractual 315 count.

The literal 415 decomposition is:

    68 idle
  + 195 directed changing non-T
  + 50 no-op non-T
  + 50 T-before-A
  + 50 T-after-A
  + 1 FIN-pending
  + 1 terminal
  = 415.

The printed 315 merges each no-op non-T class and the corresponding T-before/T-after conditions into a single selector-no-op class. That is exactly 100 forbidden class mergers. At normalized-pair level it introduces 760 extra equivalent pairs.

#### Normalized comparable-pair inventory

| Reading | Comparable pairs | PUBLIC same / separate | Priv same / separate |
|---|---:|---:|---:|
| Printed cross-kind active domains | 87,799 | 37,688 / 50,111 | 6,410 / 81,389 |
| Literal same-kind domains | 56,687 | 25,250 / 31,437 | 5,650 / 51,037 |

Under the literal rule, privileged evidence separates 19,600 normalized pairs that PUBLIC continuation alone merges.

### 2.5 Full exact-recovery class-size recount

The candidate leaves the exact-history class-size multiset UNKNOWN (`HISTORY-SEED-R01I.md:621-625`). Independent enumeration produced the following conditional results. Notation `s×n` means `n` classes containing `s` exact histories.

#### PUBLIC observational 139-class reading

    2×20, 4×6, 6×4, 12×4, 16×11, 17×4, 18×2, 19×4,
    32×1, 34×1, 50×4, 53×4, 59×8, 68×2, 71×4, 73×2,
    75×2, 100×1, 106×5, 187×6, 191×2, 216×2, 241×2,
    269×4, 282×4, 315×2, 335×1, 369×2, 374×1, 432×1,
    445×3, 632×2, 917×1, 1278×2, 1410×4, 1479×2, 3437×2,
    3792×1, 4439×2, 7049×1, 295945×2, 565200×1.

#### Cross-kind privileged 315-class reading

    2×38, 6×16, 16×17, 17×10, 18×6, 20×2, 50×10, 53×28,
    59×6, 60×4, 128×2, 144×1, 153×2, 187×12, 191×5,
    216×10, 222×16, 445×6, 450×2, 472×1, 477×4, 530×2,
    828×10, 933×20, 949×8, 1496×2, 1719×1, 1941×12,
    1944×2, 2073×5, 2220×4, 2495×10, 3489×6, 3560×1,
    5152×4, 7452×2, 8397×4, 9490×2, 11466×2, 13766×4,
    14502×2, 15528×2, 18657×1, 19017×2, 21729×1,
    22455×2, 27810×2, 27912×1, 28305×1, 295945×2.

#### Literal same-kind PUBLIC 238-class reading

    2×36, 4×6, 6×12, 12×4, 14×6, 16×19, 17×8, 18×2,
    19×4, 32×1, 34×1, 48×4, 50×10, 53×22, 59×10, 75×2,
    96×2, 100×1, 106×5, 112×1, 119×2, 187×12, 191×5,
    216×8, 222×4, 241×2, 269×4, 350×2, 354×1, 371×4,
    374×1, 424×2, 432×1, 445×6, 632×2, 828×2, 933×4,
    949×2, 1122×2, 1337×1, 1512×2, 1941×2, 2073×1,
    2495×2, 2670×1, 3489×1, 22608×2, 248688×1,
    271296×1, 295945×2.

#### Literal contractual Priv 415-class reading

    2×54, 6×24, 14×6, 16×25, 17×14, 48×4, 50×14, 53×40,
    59×8, 96×2, 112×1, 119×2, 187×16, 191×7, 216×14,
    222×24, 350×2, 354×1, 371×4, 424×2, 445×8, 828×14,
    933×28, 949×12, 1122×2, 1337×1, 1512×2, 1776×4,
    1941×16, 2073×7, 2495×14, 2670×1, 3489×8, 5152×4,
    5796×2, 6531×4, 7592×2, 11466×2, 11646×2, 13766×4,
    14502×2, 14511×1, 17465×2, 19017×2, 20934×1,
    21729×1, 27810×2, 28305×1, 295945×2.

The cross-kind 315 reading has 91,867,064,142 equivalent exact-history pairs. The literal 415 reading has 91,247,042,949, a difference of **620,021,193** falsely merged exact-history pairs.

For exact histories in the candidate's cross-kind live-allowance domains, there are 248,425,279,026 comparable pairs: PUBLIC separates 1,043,362,278 and Priv separates 156,558,214,884. Under literal same-kind domains, there are 156,294,736,375 comparable pairs: PUBLIC separates 444,870,497 and Priv separates 65,047,693,426.

### 2.6 Controller, scheduler, and probe counts

Independent closure over all declared clean and recovery cuts gives this literal `D` recount:

| Remaining `d` | Decision keys |
|---:|---:|
| 3 | 3 |
| 2 | 153 |
| 1 | 3,977 |
| 0 | 78,091 |
| **Total `|D|`** | **82,224** |

There are 4,133 keys with `d>0`, hence exactly `13^4133` legal controller truth tables; the 78,091 `d=0` entries are forced FIN. `EncController` is 82,233 bytes before any outer length wrapper.

Reading “all such keys” literally as the keys formed before the crash budget is used (`HISTORY-SEED-R01I.md:350-369`) gives:

| Proposed next crossing class | `G` keys |
|---|---:|
| C | 23,621 |
| R | 25,857 |
| A | 1,660 |
| END | 12,929 |
| **Total `|G|`** | **64,067** |

That reading yields exactly `2^64067` scheduler policies, 8,009 policy bytes, and an 8,018-byte `EncScheduler` before an outer wrapper.

There is a second textually plausible closure: include nominal keys after the budget becomes zero and from recovery cuts, with their bits merely “ignored.” That closure has 519,886 keys. Because the frozen text does not explicitly select between exclusion and ignored inclusion, the canonical `G` byte list remains non-reproducible even though both closures are finite.

The independent linear-plan recount agrees exactly:

| Scope | Base probes | OLD/NEW-padded probes |
|---|---:|---:|
| Per clean plan over words length 0..3 | 18,965 | 24,906 |
| Across 157 clean histories | 2,977,505 | 3,910,242 |

These are probe-plan slots, not scheduler-policy counts.

### 2.7 Canonical witness pair counts

There are 9,895 unequal clean pairs. Under the literal same-kind quotient there are 51,037 separable normalized recovery pairs and 65,047,693,426 separable exact-recovery pairs. Thus a completed one-witness-per-separable-pair definition would have:

- 60,932 clean-plus-normalized pair-specific witnesses; or
- 65,047,703,321 clean-plus-exact-recovery pair-specific witnesses.

Those are pair counts, not established canonical byte-string counts. Exact canonical byte strings remain **UNKNOWN** because the codec and viewer-admissibility rules are incomplete as described below.

## 3. Minimized finite breaks and collisions

### F01 — Same-cut-kind contradiction

**Rule:** Only equal cut kinds are compared (`HISTORY-SEED-R01I.md:456`).

**Contrary claim:** T before A and T after A “merge at fixed r,d” (`HISTORY-SEED-R01I.md:783-787`), and the 315 count also merges both with pending non-T no-ops.

**Shortest cross-kind merger used by 315:** From clean `H()`, interrupt `RI` immediately after its C crossing; compare with `T` interrupted immediately after C and before A. Both have `r=(U,EMPTY,E0)` and `d=2`. Their recovery suffixes contain the same OLD/NEW RESUME values and no interrupted A or R. The printed quotient merges them, while their cut kinds are PENDING_NON_T and T_PRE_A.

**Verdict:** FAIL. Literal result is 415 classes with the histogram in Section 2.4.

### F02 — Zero-ordinary-message clean separator

Take the candidate's own smallest unequal clean pair, `H()` and `H(O0)`. Use a controller that chooses FIN. Set the scheduler to crash at the initial gap before FIN crosses. Idle recovery emits:

    F:RESUME ACTIVE O=U P=EMPTY E=E0

versus:

    F:RESUME ACTIVE O=0 P=EMPTY E=E0.

No ordinary C occurs; FIN is typed and is not ordinary. SELECTOR and Priv distinguish the pair immediately. PUBLIC remains equal, so X is still the minimal **PUBLIC** separator.

The candidate instead claims that an empty future exposes only FIN/STOP and that no empty separator exists (`HISTORY-SEED-R01I.md:545-554,750-751,944-948`). Its canonical order minimizes ordinary-C count before crash count (`HISTORY-SEED-R01I.md:727-735`), so the zero-C witness beats X contractually.

**Verdict:** FAIL.

### F03 — EncCut and EncBranchRecord are not uniquely encoded

`EncCut` has optional residual and alias components, followed only by “Presence is determined uniquely by kind” (`HISTORY-SEED-R01I.md:663-666`). No normative kind-to-presence table follows. In particular, the text does not state whether CLEAN includes a residual or whether T_PRE_A/T_POST_A include their redundant T alias.

`EncBranchRecord` similarly carries a residual-present byte but does not state the normative condition selecting zero or one (`HISTORY-SEED-R01I.md:693-702`). The conceptual branch record includes a validated application fold and selected phase (`HISTORY-SEED-R01I.md:397-404`), but the encoding does not say when those are wholly derived instead of encoded.

These choices change `EncCut`, pair orientation, witness length, and the last bytewise tie-break. More than one byte string is consistent with the prose.

**Verdict:** FAIL for exact canonical reproduction.

### F04 — Viewer-code ambiguity in a privileged-only witness

Use the candidate's orientation pair:

- interrupted `AI`, `EMPTY → ID`;
- interrupted `D`, `ID → EMPTY`.

They have equal unordered PUBLIC endpoints, while SELECTOR/Priv distinguishes OLD/NEW orientation with no client message (`HISTORY-SEED-R01I.md:770-775`). `EncWitness` contains a viewer code, but the text never says that the named viewer's May value must differ, whether witnesses are per-viewer or global, or how Priv-only separation is named (`HISTORY-SEED-R01I.md:660-661,716-725`). Since `EncOutcome` already includes every projection and Priv, raw byte ordering can choose CLIENT code 0 even though CLIENT May is equal; an admissibility reading chooses SELECTOR code 3.

**Verdict:** FAIL. Prediction 13 has at least two consistent canonical bytes for the same minimal separator.

### F05 — Vacuous Must is not distinguished in the encoded verdict

The frozen rule makes every absent-antecedent implication true and explicitly has no inapplicable value (`HISTORY-SEED-R01I.md:425-452`). A no-crash run and a lifecycle-correct crash run therefore both set Must proposition 1 true, although one is vacuous and the other non-vacuous. The truth mask carries no applicability distinction.

The blind attack requires a vacuous universal truth to remain distinguishable from an operational guarantee. The prose acknowledges vacuity, but the contractual Must answer deliberately collapses the two cases.

**Verdict:** FAIL for B14. This is not a claim that the Boolean implication was computed incorrectly; it is a failure of the required evidence distinction.

## 4. Public versus privileged minimized equivalences

| Pair | Full-history relation | PUBLIC continuation | SELECTOR/Priv continuation |
|---|---|---|---|
| `H()` vs `H(RI)` | Exact prefixes differ | Equal | Equal; intended clean merge |
| Interrupted `RI` vs interrupted `RN` from initial residual | Request identities differ | Equal | Equal; shortest distinct same-kind no-op merge |
| Completed `RI`, then idle crash vs interrupted `RI` before R, both at `d=2` | IDLE vs PENDING_NON_T | Equal | NONE branch versus OLD/NEW branches; distinct |
| Interrupted `AI` EMPTY→ID vs interrupted `D` ID→EMPTY | Directed causes differ | Equal unordered endpoints | OLD/NEW orientation differs immediately |
| T before A vs T after A | Post-A full prefix contains A | Equal future suffix | Equal future behavior, but literal cut kinds differ |

The last row also shows why full viewer history and continuation quotient must not be conflated. PUBLIC retains the already-crossed A in the full prefix, but the quotient explicitly omits that prefix (`HISTORY-SEED-R01I.md:467-470`).

## 5. Falsifiable-prediction table

| Prediction | Verdict | Independent result |
|---:|---|---|
| 1 | PASS | 157 clean histories, 14 coordinates, stated class multiset reproduced. |
| 2 | PASS | 2,351 same and 9,895 unequal pairs reproduced. |
| 3 | **FAIL** | X separates every unequal clean pair publicly, but pre-FIN idle crash gives a zero-ordinary-C SELECTOR/Priv separator. |
| 4 | PASS | Exhaustive finite transition induction found no split of equal clean coordinates. This is model evidence only. |
| 5 | PASS | All six exact phase totals and 1,208,429 total cuts reproduced. |
| 6 | PASS | 854 normalized conditions reproduced. |
| 7 | **FAIL** | PUBLIC observational 139 reproduced; contractual Priv is 415 under the literal same-kind rule, not 315. |
| 8 | **FAIL** | Literal histogram is `363×1,9×6,27×7,14×8,2×68`, not the printed 315-class histogram. |
| 9 | PASS | OLD/NEW interrupted-AI application semantics and absence of interrupted R reproduced. |
| 10 | PASS | Fixed CLIENT-blind retry yields one total A from pre-A and two from post-A. No receiver effect follows. |
| 11 | PASS | FIN-pending produces one STOPPED; terminal recovery produces none. |
| 12 | PASS | All four linear counts reproduced exactly. |
| 13 | **FAIL** | Abstract D/G closures are finite, but EncCut presence, EncBranchRecord residual presence, G scope, and witness-viewer admissibility do not determine one canonical byte string. |
| 14 | PASS | Every history generated by the frozen grammar satisfies all ten implications under its vacuity rule. This is a generative theorem, not malformed-history verifier or TCB evidence. |

## 6. Mandatory individual attack verdicts

PASS below means the finite frozen model itself supplied complete evidence for that attack's stated semantic obligation. It does not credit an unbuilt realization.

| Attack | Verdict | Evidence |
|---|---|---|
| B00 Totality envelope | **FAIL** | Canonical inputs are not uniquely delimited by kind/presence rules, so the exact parser/canonical answer is not total and reproducible as claimed. Runtime totality remains additionally UNKNOWN. |
| B01 Full history vs viewer projection | PASS | Exact prefixes, four projections, May dedup, and Priv are separately defined; the public/privileged pairs in Section 4 validate the distinction. |
| B02 Viewer-relative hidden-cause explanation | **FAIL** | X returns only the current coordinate. Histories with different causes and the same residual receive the same `WHY`; no viewer-relative causal/counterfactual explanation is defined. |
| B03 Attempt/deny/apply/complete visibility | UNKNOWN | C/A/R/F cuts are formalized, but the complete four-way action experiment and independent completion evidence do not exist. |
| B04 Permission change | UNKNOWN | Authorization and privacy are excluded and untested; exclusion is not PASS evidence. |
| B05 Occurrence/application/completion adjacency | UNKNOWN | Boundary occurrence/application/R completion are specified; no independently established physical completion realization exists. |
| B06 Crash after physical completion | UNKNOWN | Receiver effects, exactly-once behavior, and physical completion are expressly unevidenced. |
| B07 Rejected/failed/no-op/success collision | UNKNOWN | Static reply classes exist, but no executable four-class attempt/explanation evidence exists. |
| B08 Truncation vs absence | UNKNOWN | No controllable history-observation window or capture-loss experiment is supplied. |
| B09 Labeled vs hidden nondeterminism | PASS | OLD/NEW remains ordered in Priv before viewer May dedup; PUBLIC projection hides orientation without erasing Priv. |
| B10 Repetition vs determinism | UNKNOWN | Finite closure is derivable, but its proof has not survived B34/B35 or a realization. |
| B11 Adaptive scheduler identity | PASS | A common total decision/scheduler domain binds divergent adaptive suffixes in the finite model; the canonical byte identity still fails B23/B24. |
| B12 Scheduler recovery context loss | UNKNOWN | Controller/scheduler severing and recovery reconstruction were not executed. |
| B13 MAY vs MUST on two carriers | UNKNOWN | May is a trace set and Must has only ten fixed implications; no executable arbitrary `q`/counterexample query is defined. |
| B14 Empty-carrier vacuity | **FAIL** | Must truth does not carry applicability and deliberately collapses vacuous with non-vacuous truth. |
| B15 Carrier collision under projection | PASS | PUBLIC unordered endpoint collisions remain distinct in SELECTOR/Priv where orientation matters; Must precedes projection dedup. |
| B16 Exact depth boundary | PASS | Independent closure reproduces d=3..0 accounting and exact-length termination. |
| B17 Phase-specific capability across crash | UNKNOWN | The formal decrement-at-C rule is exact, but controller/manifest severing is explicitly untested. |
| B18 Empty recovery-cycle drift | UNKNOWN | Zero versus one cycle is specified; the required follow-on one-versus-two comparison exceeds the one-crash scope and has no evidence. |
| B19 Recovery at exhaustion | PASS | At d=0 FIN is forced and ordinary C is unsupported; no finite-model path resurrects allowance. |
| B20 Graceful termination cuts | PASS | FIN-pending, STOPPED, terminal-gap crash, and terminal READY are distinct and exhaustively specified. |
| B21 Crash as physical terminal | UNKNOWN | Irrecoverability, power loss, and surviving external observation are unsupported and unevidenced. |
| B22 Post-terminal continuation | PASS | The finite oracle forbids later C/R and classifies outside-domain descriptions; no semantic client continuation is generated. |
| B23 Incomparable canonical witnesses | **FAIL** | EncCut/EncBranchRecord presence and viewer admissibility do not select one bytewise canonical witness. |
| B24 External canonicalizer context | **FAIL** | Two text-consistent canonicalizer readings change bytes while the claimed frozen history is fixed. |
| B25 Evolution reinterpretation | UNKNOWN | Only E0→E1 state evolution is specified; no meaning-changing two-version experiment exists. |
| B26 Authored in one version/applied in another | UNKNOWN | Serial grammar prevents the required interposed evolution, and no cross-version authoring experiment is defined. |
| B27 Unknown future extension | UNKNOWN | Arbitrary migration/future interpretation is excluded; the blind rule explicitly keeps this UNKNOWN. |
| B28 External controller context | UNKNOWN | Responsibility is charged externally, but no hold-apart or severing experiment ran. |
| B29 External capture omission | UNKNOWN | Capture availability and durability are untested. |
| B30 External selector choice | UNKNOWN | Both formal labels are generated, but external selector perturbation did not run. |
| B31 Manifest/spec identity collision | UNKNOWN | The manifest is future work and no independent collision/TCB evidence exists. |
| B32 Human-local burden | UNKNOWN | No human trial, resource bound, or error evidence exists. |
| B33 Quantifier/vacuity cognition | UNKNOWN | B14 fails statically, but the required controlled human study has not run. |
| B34 TCB closure | UNKNOWN | The candidate explicitly says the TCB is unperturbed. |
| B35 Circular self-validation | UNKNOWN | No independent realization oracle or shared-influence perturbation exists. |
| B36 Materially unlike realizations | UNKNOWN | No realization was built. |
| B37 Simulated vs physical completion | UNKNOWN | Physical receiver completion is excluded and unevidenced. |
| B38 Cross-realization canonical ambiguity | UNKNOWN | Neither unlike realization evidence nor realization-scoped canonicalization exists. |

## 7. Mandatory composite verdicts

| Composite | Verdict | Evidence |
|---|---|---|
| C1 Projection × action × crash | UNKNOWN | Projection semantics is finite, but action completion and realized crash/recovery explanation are absent. |
| C2 Nondeterminism × scheduler × evolution | UNKNOWN | Label grammar exists; external scheduler recovery and meaning-changing evolution do not. |
| C3 MAY/MUST × depth × recovery | UNKNOWN | Depth is exact and vacuity fails, but the required two-carrier predicate query and recovery run are absent. |
| C4 Terminal × physical realization | UNKNOWN | Formal terminal traces cannot substitute for unlike physical terminal-crash evidence. |
| C5 Canonical × viewer × external context | **FAIL** | The orientation pair plus undefined witness-viewer eligibility and optional encoding choices is a finite cross-axis counterexample. |
| C6 Human × TCB × vacuity | UNKNOWN | Vacuity fails statically, but no human or TCB perturbation was executed. |

## 8. Final classification

The candidate remains a useful finite grammar, and most printed corpus and linear-probe arithmetic is reproducible. It does **not** pass the frozen blind pack:

- the contractual recovery quotient is internally inconsistent;
- the advertised smallest clean witness is not smallest under the contract's privileged evidence;
- canonical bytes are not uniquely specified;
- the simultaneous external, physical, human, and TCB gates remain UNKNOWN.

One finite FAIL dominates the passes. No implementation or representation may inherit conformance from the specification alone.
