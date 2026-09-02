# ZERO GROUND R0.1J literal/canonical audit

## 0. Quarantine, inputs, and verdicts

This audit used only the following two frozen inputs:

| Input | Independently verified SHA-256 |
|---|---|
| `HISTORY-SEED-R01J.md` | `7c9b2a742eab81f6c104b6ca3566315ddb29ecc63d216d25cff91bf1c70836dc` |
| `BLIND-ATTACK-PACK-R01I.md` | `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b` |

No R0.1I candidate, audit, archive, builder discussion, implementation, or git
history was used. All enumerations below were independently derived from the
R0.1J transition and codec text.

Verdicts have deliberately different meanings:

- **PASS**: the literal finite claim was reproduced or its required rule is
  complete.
- **FALSE / FAIL**: a finite minimized history or byte-carrier counterexample
  contradicts the claim.
- **UNDERDEFINED**: the frozen text permits two results or does not define the
  data/order needed to choose one. This is not repaired by picking a plausible
  interpretation.
- **UNKNOWN**: the rule is defined, but the required independent experiment or
  evidence does not exist. Scope exclusion is not positive capability evidence.

## 1. Result summary

| Frozen claim or audit target | Verdict | Exact result or smallest witness |
|---|---|---|
| 157 clean cuts and clean residual multiset | **PASS** | Fourteen residuals; class sizes `59,17,17,16,16,16,2,2,2,2,2,2,2,2`; clean pairs `2,351/9,895/12,246`. |
| 1,208,272 recovery cuts | **PASS** | `7,696` per clean cut and `157 * 7,696 = 1,208,272`. |
| 854 normalized recovery conditions | **PASS** | `68 idle + 195 changing + 355 no-op + 50 T-pre + 50 T-post + 68 FIN + 68 terminal`. |
| One ungated all-cut relation | **PASS** | Clean/recovery and every recovery-kind pair are compared under the same total policy pair; no kind gate remains. |
| Recovery quotient | **PASS** | `315` all-scope classes and histogram `263x1,9x8,27x9,14x10,2x68`; `139` PUBLIC functions. |
| Combined quotient | **PASS** | `329` all-scope classes, `153` PUBLIC functions, histogram `277x1,9x8,27x9,14x10,2x68`. |
| Decision closure `D` | **PASS** | `N=82,224`, by allowance `{0:78,091, 1:3,977, 2:153, 3:3}`. |
| Gap closure `G` | **PASS** | `M=64,067`; `12,929` are END keys. |
| Encoded-policy routing | **PASS** | Every globally legal total table has an `Eval` at every declared cut; unreached entries are inert. |
| Raw operational-description classifier | **UNDERDEFINED** | No byte grammar or other exact representation is supplied for the descriptions to which the seven raw refusal reasons are applied. |
| Primitive framing and five top-level binary magics | **PASS** | `Block`, `Seq`, tags, widths, trailing-byte rule, and top-level magic dispatch are disjoint and exact. |
| Manifest framing, field presence, and case sorting | **PASS** | Fixed digest, count, mandatory case fields, bytewise `EncEvidenceCase` order, and duplicate rejection are sufficient for a single interpretation. |
| Timeout after a captured proper prefix | **FALSE / FAIL** | Kind 1 requires an empty body, so timeout before `C:FIN` and timeout after captured `C:FIN` encode identically. |
| Manifest result as a function of manifest bytes | **UNDERDEFINED** | The same one-timeout manifest is `UNKNOWN(OBSERVATION_BOUND)` without, but `FAIL(NON_TOTAL)` with, an external envelope that has no frozen codec or binding. |
| Mixed timeout-result precedence | **UNDERDEFINED** | One manifest can contain one qualifying and one nonqualifying timeout; both timeout results occupy the same precedence item with no tie rule. |
| Zero-case `SUPPORTED_EVIDENCE` | **UNDERDEFINED**, not a proved conformance falsehood | The exact 57-byte empty manifest is accepted, but the proposition supported by that result is not defined. The text separately forbids treating absence as conformance. |
| Origin-0-only manifest as verifier evidence | **PASS, narrowly** | It can support generator self-consistency only; the frozen text explicitly says it is not a verifier test. |
| Witness scope admissibility | **PASS** | Scope code must itself separate; PUBLIC and contractual searches are distinct. Q4 is SELECTOR/PRIV-only. |
| Section 8.7 canonical existence/uniqueness | **PASS** | Finite policy universes, actual-scope eligibility, fixed cut orientation, and a total byte tie-break yield one witness for every separable pair. |
| Exact canonical witness bytes | **UNKNOWN** | This audit computed `N` and `M` but did not exhaustively emit every pair's minimum witness. |
| Section 10.1 “exact smallest” order | **UNDERDEFINED** | It gives singular post-cut counts for multi-suffix pairs and no exact prefix-difference metric. |
| Listed S1-S5, R1-R4, and F1-F5 semantic pairs | **PASS** | Each listed pair has the claimed formal distinction, derivation, or merger. Empirical deletion/recovery evidence remains UNKNOWN. |
| Completeness of Section 10 responsibility labels | **FALSE / FAIL** | Clean-active versus DOWN-idle recovery is behaviorally necessary (Q7) but receives no MUST row; active-recovery versus FIN-pending is also omitted. |
| Human, TCB, external-service, and unlike-physical-realization claims | **UNKNOWN** | No permitted physical realization or attack campaign exists; formal scope exclusion supplies no PASS evidence. |

## 2. Independent finite recomputation

### 2.1 Exact cut corpus

The clean corpus arithmetic is direct:

    1 + 12 + 12^2 = 157.

Folding those words gives fourteen residuals with the stated multiplicities.
Their unordered within-class pair sum is `2,351`; subtracting from
`C(157,2)=12,246` gives `9,895` unequal pairs.

For a recovery prefix, only the already crossed word prefix matters. Per clean
history:

- idle, FIN-pending, and terminal prefixes each have
  `1+12+12^2+12^3 = 1,885` possibilities;
- a pending non-T request has
  `11(1+12+12^2) = 1,727` possibilities; and
- each of T-before-A and T-after-A has `1+12+12^2 = 157`.

Thus

    3(1,885) + 1,727 + 157 + 157 = 7,696
    157(7,696) = 1,208,272.

Deduplicating only continuation-relevant conditions independently reproduces
all 854 rows.

### 2.2 Why the all-scope recovery quotient is 315

For contractual comparison, the exact continuation key of an active recovery
condition is:

- `(idle,r,d)` for idle recovery;
- `(pending,pre,post,d)` for every pending request; or
- the single forced FIN-pending or terminal behavior.

The pending alias and T stage disappear only when the complete future family
is identical; OLD/NEW direction remains in SELECTOR and PRIV. This yields:

| Contractual component | Classes | Source conditions |
|---|---:|---:|
| Idle `(r,d)` | 68 | 68 |
| Changing directed pending edges | 195 | 195 |
| Identity pending edges | 50 | 455 |
| FIN-pending | 1 | 68 |
| Terminal | 1 | 68 |
| **Total** | **315** | **854** |

The 50 identity-edge classes have multiplicities `9x8,27x9,14x10`; the 195
changing edges and 68 idle rows are singleton classes; FIN and terminal each
have multiplicity 68. Hence the exact histogram is
`263x1,9x8,27x9,14x10,2x68`.

For PUBLIC, direction and F labels are hidden. At `d=0`, every active or
pending condition is followed by forced FIN, so all residuals, no-ops, and
changing endpoint sets collapse into one projected function. At positive d:

- idle/no-op active states contribute `18 + 18 + 14 = 50` functions for
  `d=1,2,3`;
- unordered changing edges contribute `45 + 41 = 86` functions for `d=1,2`;
- the single exhausted function contributes 1; and
- FIN-pending and terminal contribute 2.

Therefore `50+86+1+2 = 139` PUBLIC functions.

Clean histories contribute fourteen functions/classes. No clean class joins a
recovery class: under the common FIN controller and all-zero scheduler, clean
PUBLIC begins `C:FIN,R:STOPPED`, while every recovery suffix contains the
mandatory `L:READY` first (and SELECTOR sees RESUME). Thus the combined counts
are `153` and `329`, with fourteen additional singleton contractual classes.

### 2.3 Independently closed policy domains

I explored the least fixed points exactly as stated: seed every normalized
cut condition; branch over every legal controller action, scheduler pass/crash,
and OLD/NEW; retain exact CLIENT or PUBLIC crossing tuples; and deduplicate only
after exact encoding-equivalent tuples agree.

The decision closure is:

| Live `d` | Distinct `EncDecisionKey` values |
|---:|---:|
| 0 | 78,091 |
| 1 | 3,977 |
| 2 | 153 |
| 3 | 3 |
| **Total `N`** | **82,224** |

Only `4,133` entries have positive d. Consequently the exact legal-controller
count is `13^4133`; all `78,091` exhausted entries are forced FIN. The complete
`EncController` length is `13 + 8 + 82,224 = 82,245` bytes.

The gap closure contains exactly `M=64,067` keys. As a cross-check, their
counts by current PUBLIC suffix crossing length are:

    0:13, 1:49, 2:457, 3:890, 4:7,466, 5:12,726,
    6:12,880, 7:12,332, 8:12,052, 9:4,740, 10:448, 11:14.

Of these, `12,929` propose END. The exact legal-scheduler count is `2^64067`.
Its policy vector occupies 8,009 bytes, with five unused low bits fixed to
zero, and the complete `EncScheduler` length is `8,030` bytes.

This closure also verifies scheduler identity across divergent adaptive paths:
one sorted `G` and one positional bit vector govern every clean path; recovery
adds no scheduler keys, and no post-crash context is silently consulted.

## 3. Literal defects and minimized witnesses

### F1 — Timeout evidence erases the observed prefix

**Classification:** FALSE / blind attack FAIL.

Use cut `H()`, the FIN controller, and the all-zero scheduler. The expected
formal suffix is typed `C:FIN` followed by typed `R:STOPPED`. Compare:

1. observation bound expires before `C:FIN`; and
2. `C:FIN` is captured, then the bound expires before `R:STOPPED`.

The two evidence histories differ by the smallest possible nonempty observed
prefix: one crossing. Yet result-kind 1 requires its body to be empty. With
the same origin, cut, controller, and scheduler, both become the identical
`EncEvidenceObservation`, identical case, and identical manifest. Encoding the
second run as kind 0 instead would assert a completed raw family and produce
`FAIL(CONFORMANCE)`, not preserve “proper prefix followed by timeout.”

This contradicts Section 9.1's carrier purpose for bounded, missing, and
nonterminating observations. Duplicate-case rejection also prevents putting
the two identical timeout cases into one manifest. This is the minimized
`B08` observation-truncation collision and also exercises `B29`; operators are
`DELETE + MERGE + COLLIDE`.

### U1 — The top-level manifest classifier depends on unbound external state

**Classification:** UNDERDEFINED.

Take the one-case manifest from F1 with origin 1 and kind 1. Hold every manifest
byte fixed:

- without an envelope proving a contract-authorized bound violation, the
  required result is `UNKNOWN(OBSERVATION_BOUND)`;
- with such an envelope, the required result is `FAIL(NON_TOTAL)`.

The envelope is not an `EncManifest` field or any other admitted top-level
binary object. No envelope codec, identity, signature authority, manifest
binding, or classifier argument is frozen. Therefore “EncManifest dispatches
to the separate total evidence classifier” does not define a function from
the dispatched bytes to one result.

An implementation could define a classifier over a pair
`(manifest,envelope)`, but that is a new interface, not a literal consequence
of these bytes. This is `EXTERNALIZE + COLLIDE`, principally `B31` and `B34`.

### U2 — Two timeout outcomes have no mutual precedence

**Classification:** UNDERDEFINED.

Make a sorted two-case manifest at the same cut `H()` and with the same FIN
controller. Make the two legal schedulers differ in exactly one bit at a `G`
key that is unreachable under that controller; this is the smallest policy
change that makes the case bytes distinct without changing their expected
suffix. Let the external envelope establish a bound violation for one case but
not the other. Both
`FAIL(NON_TOTAL)` and `UNKNOWN(OBSERVATION_BOUND)` are applicable. They occupy
one shared precedence item—“UNKNOWN or FAIL ... as just defined”—and neither
case order nor verdict dominance is specified.

The broader precedence is otherwise reproducible: encoding, digest, ordinary
input validity, generator disagreement, timeout, conformance, supported. A
generator disagreement therefore precedes a conformance disagreement. Sorted
cases do not resolve the two-timeout tie.

### U3 — An empty manifest has an exact structural result but no exact claim

**Classification:** UNDERDEFINED semantic status; no conformance FAIL proved.

`FBH-R01J-FALSIFY\0`, the correct 32-byte digest, and U64 zero form a legal
57-byte manifest: ordering and duplicate rules hold vacuously and no rule says
the count must be positive. Its literal classifier result is
`SUPPORTED_EVIDENCE`.

That label is not bound to a claim identifier or proposition, so the frozen
text does not say what this empty object positively supports. It must not be
read as conformance: Sections 6 and 9 expressly say absence is not a guarantee,
origin-0 generated traces are not verifier tests, and no campaign has run.
Thus `B14` does not establish a formal conformance contradiction unless a
consumer inflates the status. It does establish that the semantic API meaning
of `SUPPORTED_EVIDENCE` is underdefined for the empty carrier.

An origin-0-only nonempty manifest is less problematic: equality supports only
formal-generator self-consistency, and the document explicitly denies the
stronger verifier inference.

### U4 — Raw operational refusals have no executable input language

**Classification:** UNDERDEFINED.

The five binary top-level types have exact, distinct magic strings and total
structural dispatch. The separate paragraph for a “raw operational
description” supplies a refusal precedence but no finite syntax, framing,
parser, or equality rule for such descriptions.

The smallest conceptual example is an attempted `SELECT old` at clean active
`H()`: the prose says `UNSUPPORTED(PHASE_ACTION)`, while presenting any
unframed bytes to the top-level classifier says `UNSUPPORTED(ENCODING)`. There
is no frozen rule deciding which representation invokes which classifier.
Encoded legal policy evaluation remains total; the underdefinition is confined
to the additional raw-description claim. This is `B00`.

### U5 — Section 10's separate minimization order is not exact

**Classification:** UNDERDEFINED.

Section 8.7 is exact: it specifies maximum and sum over both complete branch
families, then suffix count, crash count, scope, length, and bytes. Section
10.1 instead uses singular “post-cut ordinary C count” and “post-cut total
crossings” for a pair that can contain one suffix on one side and two on the
other. It does not say maximum, sum, or another aggregation. Its “number of
differing prefix crossings” also has no alignment/edit rule for unequal
prefixes.

S3 is already a minimized ambiguity witness: its idle side has one suffix and
its interrupted side has two. A maximum, a sum over all three suffixes, and a
sum of per-side maxima assign different numeric coordinates. F1 (`H()` versus
`H(RI)`) is the smallest unequal-length-prefix example for which “differing
crossings” likewise has no unique value.

The listed semantic facts can still be checked, but the adjectives “exact
smallest” and “lowest” cannot be independently canonicalized from Section
10.1. This does not infect the separately specified Section 8.7 witness order.

### F2 — Section 10 omits a required recovery-phase responsibility

**Classification:** FALSE / classification-completeness FAIL.

The smallest omitted pair is Q7 specialized to the initial state:

- left: clean `H()`;
- right: the recovery cut after an immediate crash in the idle gap before FIN
  from `H()`.

Both sides have residual `(U,EMPTY,E0)`, d=3, and no pending request. Apply the
same FIN controller and all-zero scheduler. The clean suffix is
`C:FIN,R:STOPPED`; the recovery suffix first emits
`F:RESUME ACTIVE ...`, `F:ALLOWANCE 3`, and `L:READY`, then FIN/STOPPED.
PUBLIC, CLIENT, SELECTOR, and PRIV separate at zero ordinary post-cut C.

Deleting the clean-active versus DOWN-active recovery phase therefore makes a
forbidden collision under Section 10.1's own `MUST SURVIVE` definition. It is
not S3: S3 compares two DOWN cuts, idle versus interrupted. It is not S5: S5
compares FIN-pending versus terminal.

A second omitted boundary confirms this is not merely clean-cut metadata:
compare the initial idle-recovery cut above with the FIN-pending recovery cut
from `H()` after FIN crossed. They have the same residual and d. Under the FIN
controller the former still owes `READY,FIN,STOPPED`, while the latter owes
`READY,STOPPED`; their F:RESUME frames also differ. No S1-S5 row names active
recovery versus FIN-pending.

The continuation relation itself preserves both distinctions, so this defect
is in the supposedly exclusive responsibility classification—especially the
statement that no other responsibility receives a label—not in `==J`.
Operators are `DELETE + MERGE + FUTURE`; it is the smallest formal Q7 phase
collision.

## 4. Scope, canonical witnesses, and non-defects

### 4.1 Public versus privileged equivalence

The viewer rules are internally consistent:

- full prefixes remain evidence but are not appended to suffix observations;
- T-before-A and T-after-A may therefore merge as continuations while their
  exact prefixes remain different;
- projected families deduplicate only after the full OLD/NEW family exists;
- SELECT labels retain directed pre/post association for SELECTOR and PRIV;
  and
- Q4 cannot use PUBLIC, CLIENT, or CAPTURE merely because those scope codes are
  smaller.

For the reversed AI/D pair, PUBLIC sees the same unordered endpoint traces,
but SELECTOR associates `old` and `new` with opposite RESUME states. Scope 3
is admissible and scopes 0-2 are not. This independently passes the explicit
scope-eligibility rule.

### 4.2 Section 8 canonical existence

The closure results make the policy universes exact:

    controllers = 13^4133
    schedulers  = 2^64067.

They are enormous but finite. For a fixed unequal pair, failure of the
universal equality definition is exactly existence of at least one legal
policy/scope separator. Admissibility removes nonseparating scope codes; cut
byte order fixes orientation; Section 8.7's tuple and final byte order are
total. Hence every separable pair has exactly one contractual canonical
witness, and every PUBLIC-separable pair has exactly one PUBLIC canonical
witness.

This is a proof of existence and uniqueness of the algorithmic result, not an
emitted canonical byte corpus. Exact witness bytes and cross-implementation
agreement remain UNKNOWN.

### 4.3 Listed Section 10 pairs

Subject to U5's noncanonical “smallest” order, the semantic content of every
listed pair checks:

- S1 preserves the three active residual coordinates through RESUME;
- S2 preserves d; S3 preserves NONE versus OLD/NEW; S4 preserves directed
  association; S5 preserves FIN-pending versus terminal;
- R1-R4 are exact derivations from the named surviving formal inputs; and
- F1-F5 are genuine all-scope continuation mergers under the stated cut
  relation.

The formal derivations do not prove that their inputs, specification, or
machinery survive a real failure. The frozen text correctly leaves those
experiments UNKNOWN.

## 5. Blind-attack disposition

| Attack area | Literal R0.1J disposition |
|---|---|
| `B00` total boundary handling | Encoded formal policies **PASS**; raw descriptions and envelope-dependent manifest dispatch are **UNDERDEFINED**. |
| `B01-B04` history/viewer/action visibility | Formal projections and prefix/suffix distinction **PASS**; physical completion remains **UNKNOWN**. |
| `B05-B07` occurrence/application/completion | Formal C/R/SELECT rules **PASS**; receiver effect and physical completion are **UNKNOWN**. |
| `B08` bounded observation | **FAIL** by F1's empty-body timeout collision. |
| `B09-B12` selector and adaptive scheduler | Ordered OLD/NEW and global `G` **PASS** formally; external availability/recovery is **UNKNOWN**. |
| `B13-B15` MAY/MUST/vacuity | Listed formal pairs **PASS**; empty `SUPPORTED_EVIDENCE` meaning is **UNDERDEFINED**; no empty carrier proves conformance. |
| `B16-B22` depth/recovery/termination | Formal d, FIN-pending, and terminal transitions **PASS**; §10 omits phase responsibility F2; physical crash evidence is **UNKNOWN**. |
| `B23-B24` canonical witness | Section 8.7 existence/uniqueness **PASS**; exact emitted bytes and external canonicalizer perturbation are **UNKNOWN**; Section 10.1 order is **UNDERDEFINED**. |
| `B25-B31` evolution and external context | Single formal E transition and spec digest are exact; envelope binding is **UNDERDEFINED**; external severing and cross-version evidence are **UNKNOWN**. |
| `B32-B35` cognition and TCB | **UNKNOWN**. No study, independent negative verifier, or perturbation exists. |
| `B36-B38` unlike physical realizations | **UNKNOWN**. R0.1J admits no physical realization, so there is no cross-realization PASS. |

The composite attacks that require physical completion, severing, human use,
or TCB perturbation remain UNKNOWN. Generated FORMAL agreement cannot turn any
of them into PASS.

## 6. Final audit verdict

R0.1J's finite formal continuation core is substantially internally coherent:
the all-cut relation, ungated policy routing, exact D/G closures, normalized
quotients, scope eligibility, and Section 8 canonical existence all reproduce.

It is not a fully literal total evidence/classification contract. The smallest
hard failure is the one-crossing partial-timeout collision. The evidence
classifier additionally depends on an unencoded, unbound envelope and lacks a
mixed-timeout tie rule. Section 10's separate “smallest” order is not fully
specified, and its exclusive responsibility list omits the clean/recovery and
active/FIN phase obligations already forced by the candidate's own Q7
continuations.

Everything concerning external-service survival, human burden, TCB closure,
physical crash/recovery, receiver completion, and unlike physical realizations
remains UNKNOWN. None is rehabilitated by the verified formal counts.
