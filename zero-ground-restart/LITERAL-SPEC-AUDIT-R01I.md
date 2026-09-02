# Literal-spec audit of FBH-12/2/3-I

## 0. Scope and authority

This is a pre-implementation audit of the frozen R0.1I candidate. It reads the
candidate literally and does not repair omissions by choosing convenient
defaults. It uses no quarantined pre-R0.1I solution. The candidate under audit
is:

- `HISTORY-SEED-R01I.md`
- git commit `c8f912b08a468dffdfb29352aaa9924aee9048ba`
- SHA-256 `d52c083c34aa37144fa47ee8a02d9279adb75029613125f38dad5a98b0df8d9c`

The audit is not an implementation result and does not replace either the
independent breaker or the independent enumerator. Its purpose is to identify
literal specification forks that an implementation must not silently resolve.

## 1. Decisive quotient contradiction

Section 7.3 permits comparison only when both cuts have the same cut kind.
Section 10.1 assigns different kind codes to:

- `PENDING_NON_T`;
- `T_PRE_A`; and
- `T_POST_A`.

Section 11.4 nevertheless says the two T phases merge at fixed residual and
allowance. Section 9's 315-class calculation goes further: it groups both T
phases with the corresponding interrupted no-op class. Those mergers cross
the exact kinds that Section 7.3 forbids comparing.

The contradiction has a one-condition witness. Fix any reachable residual
`r` and live allowance `d` after a T occurrence. The recovery suffix after a
pre-A T cut and the suffix after a post-A T cut are the same under the frozen
recovery rules. Relaxing the kind gate therefore merges them. Applying the
kind gate forbids even asking whether they merge. The behavior and the declared
relation give different answers without changing a crossing.

### 1.1 Literal privileged count

The 854 normalized recovery conditions decompose literally as follows:

| Same-kind family | Literal classes |
|---|---:|
| idle active | 68 |
| changing interrupted non-T | 195 |
| no-op interrupted non-T | 50 |
| T pre-A | 50 |
| T post-A | 50 |
| FIN-pending | 1 |
| terminal | 1 |
| **Total** | **415** |

The corresponding literal multiplicity histogram is:

| Raw conditions per class | Classes |
|---:|---:|
| 1 | 363 |
| 6 | 9 |
| 7 | 27 |
| 8 | 14 |
| 68 | 2 |

Both checks close:

    363 + 9 + 27 + 14 + 2 = 415
    363 + 9*6 + 27*7 + 14*8 + 2*68 = 854

Deleting the same-kind gate yields the candidate's behavioral grouping:
the 100 T conditions join the 50 non-T no-op classes, producing 315 classes
and its stated `263x1, 9x8, 27x9, 14x10, 2x68` histogram. Thus 315 is a
coherent result for a different equivalence relation, not for literal R0.1I.

### 1.2 Literal PUBLIC count

The same gate changes the PUBLIC projection quotient. Keeping kinds separate
gives:

| Same-kind PUBLIC family | Literal classes |
|---|---:|
| idle active | 51 |
| interrupted non-T | 119 |
| T pre-A | 33 |
| T post-A | 33 |
| FIN-pending | 1 |
| terminal | 1 |
| **Total** | **238** |

Deleting the gate permits the cross-kind behavioral mergers used by Section
9.2 and gives 139. Prediction 7 therefore fails under the literal relation for
both PUBLIC and privileged behavior. Prediction 8 fails with it.

## 2. Canonical bytes are not total

### 2.1 Missing EncCut presence map

Section 10.1 defines `EncCut` using an optional residual and optional alias,
then says their presence is determined uniquely by kind. It never gives the
kind-to-field-presence map. At least these choices remain unselected by the
bytes of the document:

- whether a T kind carries the implied T alias;
- whether FIN-pending carries its source residual or treats it as dead; and
- whether terminal carries its last active residual.

Different choices change lengths, pair orientation, and canonical witnesses.
An implementation selecting one has added specification. Prediction 13 is
therefore UNKNOWN or FAIL, not PASS.

### 2.2 Conceptual branch record and EncBranchRecord disagree in scope

Section 7.1 says a branch record contains a validated application fold,
selected residual or phase, starting and ending allowance, truth evidence,
and four projections. `EncBranchRecord` encodes a branch code, two allowance
bytes, an optional residual, a truth mask, and a suffix trace. It does not say:

- which phase determines residual presence;
- whether the application fold is encoded or mechanically derived;
- whether a special phase is encoded or inferred from the suffix; or
- which value is used for a dead starting allowance at FIN-pending or terminal.

If these are derived, the specification must identify the derivation inputs
and validation rule. If they are contractual record components, omitting them
can collide records. The frozen text does neither completely.

### 2.3 Viewer code need not name a separator

`EncWitness` contains one of four viewer codes, but no admissibility rule says
that the named viewer's projected outcome must differ. There is also no code
for a distinction visible only in `Priv` or `Must`.

Use Section 11.3's own orientation pair: interrupted EMPTY-to-ID versus
interrupted ID-to-EMPTY at the same allowance. CLIENT, CAPTURE, and PUBLIC see
the same unordered alternatives; SELECTOR and `Priv` retain orientation.
With no separating-viewer restriction, all four viewer bytes are candidate
encodings of the same outcome difference, and the final bytewise tie-break
selects CLIENT code zero. That byte claims a viewer which does not separate
the pair. Adding a restriction repairs the result but changes the frozen
algorithm.

### 2.4 Redundant derived cut fields have no mismatch result

The full prefix in `EncCut` determines kind, remaining allowance, pending
alias, and residual under the declared fold. The encoding repeats some of
those values. The total classifier gives no result for a structurally
canonical cut whose repeated value disagrees with its trace. Treating the
trace as authoritative, treating the repeated field as authoritative, and
rejecting the input are three observably different algorithms. None is
selected.

## 3. Must evaluation has two possible history scopes

A recovery cut is after `F:CRASH` and `DOWN`. Its encoded continuation suffix
therefore does not contain that crash. A terminal recovery cut also has its
STOPPED crossing in the prefix; a FIN-pending cut has FIN in the prefix and
STOPPED in the suffix.

Section 7.1 calls the recorded trace a complete suffix. Section 7.2 then says
the propositions are evaluated in every complete branch record, without
stating whether that means:

1. the encoded suffix alone; or
2. the cut prefix concatenated with the suffix.

The first interpretation makes crash clauses vacuous at a recovery cut and
cannot see FIN and STOPPED together at FIN-pending. The second can validate
them but requires an unprinted concatenation and validation rule. Prediction
14 cannot be independently reproduced until the scope is fixed.

Moreover, the generated oracle constructs only conforming suffixes, so all
ten truths being true is construction evidence. The parser/classifier does not
define how an observed nonconforming branch history enters the oracle domain
or which typed result it receives. This leaves verifier and negative-history
behavior untested.

## 4. Persistence verdicts exceed the surviving witnesses

The candidate correctly labels its table as behavioral rather than physical,
but several `MUST SURVIVE` entries have no deletion collision in its frozen
future corpus:

- specification identity never varies;
- codec/closure-domain identity never varies;
- a previously crossed A is absent from the compared suffix, and no future
  historical query is declared that can retrieve it;
- complete branch records, projections, and masks are mechanically related,
  but no cold-start deletion test establishes which information must be
  retained and which can be regenerated; and
- the full exact prefix is present in the evidence encoding while the
  equivalence deliberately omits it from compared outcomes.

These may be real total-system responsibilities. R0.1I has not yet supplied
the minimized pair of histories and permitted future continuation required to
classify each as persistent MUST SURVIVE information. Declaring a conformance
artifact contractual does not by itself show that the artifact, rather than
smaller generating information plus a specification, must persist between
executions.

## 5. Simultaneous accounting of the failed simplifications

| Finding | Preservation | Runtime/storage | Cognition/authoring | TCB/externalization |
|---|---|---|---|---|
| kind gate retained | prevents claimed mergers; quotient 238/415 | more class identities | user must know nonbehavioral comparability rule | gate moves correctness into oracle/spec |
| kind gate deleted | restores 139/315 behavior | fewer class identities | simpler behavioral model | codec and witness relation must change |
| optional fields guessed | unknown collision behavior | implementation-dependent bytes | undocumented choice | choice moves into implementer/canonicalizer |
| viewer admissibility guessed | may mislabel a witness | little machine cost | reviewer can trust wrong viewer | canonicalizer silently expands TCB |
| suffix-only Must | loses prefix obligations | smaller evaluator input | misleading vacuity | hidden dependence on generator correctness |
| prefix-plus-suffix Must | can preserve obligations | concatenation/validation work | rule must be authored and checked | cut decoder and validator join TCB |

No scalar score resolves these forks. They are different contracts.

## 6. Verdict

R0.1I is falsified before implementation:

- predictions 7 and 8 are false under its literal equivalence relation;
- prediction 13 is not reproducible from the frozen bytes;
- prediction 14 has an unresolved evaluation scope; and
- the persistent-state table is not yet supported responsibility-by-
  responsibility by deletion collisions.

The candidate remains useful as a finite attack surface. It is not a valid
representation of the history quotient and does not establish the first
milestone. A successor must at minimum choose one equivalence relation for all
declared cuts, make every canonical byte and mismatch result total, separate
evidence retained for falsification from information required between
executions, and attach a minimized future-observable witness to every claimed
persistent responsibility.
