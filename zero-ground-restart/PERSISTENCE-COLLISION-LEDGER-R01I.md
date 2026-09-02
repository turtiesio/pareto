# R0.1I persistence-collision ledger

## 0. Authority, scope, and verdict grammar

This ledger audits the behavioral responsibility table in Section 14 of
`HISTORY-SEED-R01I.md` against R0.1I's literal future-equivalence rule.  Its
only source documents are:

| Source | SHA-256 |
|---|---|
| `HISTORY-SEED-R01I.md` | `d52c083c34aa37144fa47ee8a02d9279adb75029613125f38dad5a98b0df8d9c` |
| `LITERAL-SPEC-AUDIT-R01I.md` | `e26af4a66ff1884371973a60710c5b0f556b9d4b78b5259bb50d355007262ad5` |
| `POSTFREEZE-BREAK-R01I.md` | `57f007f0457595e5545eb9dd76fda210b9eea94483a1d74cb6d074230b8ac015` |
| `EXPERIMENT-RESULT-R01I.md` | `6c1458f369ec6d576d7e7dd44b2fc23ae3fe8d38c5047475ece2d7915553c858` |

No older archive, storage proposal, or representation is adopted.  This is an
information and evidence ledger, not a storage layout.

The literal rule being audited compares only cuts of the same cut kind and
the same live-allowance contract.  It compares complete future `Priv`, four
viewer `May` values, and `Must`, but does not append the exact prefix before
the cut.  Therefore a difference in the retained experiment record is not by
itself a proof that a service must retain that difference across executions.

The only justified verdict labels are:

- **MUST SURVIVE**: deleting or merging the information changes a permitted
  contractual future, or destroys the identity of evidence that is expressly
  being retained in the stated scope.
- **MAY REBUILD**: the information is a total mechanical function of named
  surviving inputs under the frozen rules.  This says nothing about replay
  cost or physical availability of those inputs.
- **MAY FORGET**: an exact permitted merger has equal contractual futures, or
  the grammar removes the obligation.
- **UNKNOWN**: the frozen sources provide neither an admissible collision nor
  a total derivation, combine responsibilities with different answers, or
  require an unexecuted persistence/externalization experiment.

Every responsibility receives two audit verdicts:

1. **Manifest evidence** concerns what must remain to substantiate the exact
   experiment record.  Expected bytes regenerated from the model are not
   evidence that those bytes crossed an observed boundary.
2. **Between executions** concerns information that the total system must
   carry across a crash/restart boundary to preserve permitted futures.  The
   carrier may be external, but no carrier is selected here.

The R0.1I executable result is finite model evidence.  Its stdout was not
retained as another authority; a digest identifies the run.  It is not a
DELETE, RECOMPUTE, EXTERNALIZE, COGNITION, or TCB persistence experiment.

## 1. Exact symbolic witnesses and derivations

`H(w)` denotes the exact failure-free clean history for word `w`, including
all ordinary C/A/R crossings and the final `F:CUT REMAINING=3` crossing.  The
recovery-cut prefixes below end after `L:DOWN`.  Frame spellings are the exact
seed spellings; `C:FIN`, `L:DOWN`, and `L:READY` are typed crossings.

### W1 — the fourteen-way clean lower bound

The smallest unequal clean pair is `H()` versus `H(O0)`:

    H():    F:CUT REMAINING=3

    H(O0):  C:OBSERVE 0
             R:OK OBSERVE 0
             F:CUT REMAINING=3

Choose FIN and crash at the initial gap before FIN.  With zero ordinary future
C occurrences, SELECTOR receives respectively:

    F:CRASH GAP=0
    F:RESUME ACTIVE O=U P=EMPTY E=E0
    F:ALLOWANCE 3

and

    F:CRASH GAP=0
    F:RESUME ACTIVE O=0 P=EMPTY E=E0
    F:ALLOWANCE 3

Every unequal reachable clean residual is separated in the same way because
`F:RESUME ACTIVE` prints all three residual coordinates.  A no-crash X remains
the smallest PUBLIC separator, but it is not the smallest contractual one.

### W2 — OLD/NEW orientation

These are same-kind `PENDING_NON_T` cuts with the same live allowance `d=2`:

    H();     C:AUTHOR ID
             F:CRASH GAP=1
             L:DOWN

    H(AI);   C:RETIRE
             F:CRASH GAP=1
             L:DOWN

The first map is `EMPTY -> ID`; the second is `ID -> EMPTY`.  PUBLIC May has
the same unordered endpoints.  SELECTOR and `Priv` distinguish which endpoint
is OLD and which is NEW immediately, with no ordinary future C.  Erasing the
label-to-endpoint association is therefore a real same-domain collision.

### W3 — no-selector versus selector evidence

From `H()` compare these `d=2` recovery prefixes:

    C:REPLACE ID
    R:ERR EMPTY
    F:CRASH GAP=2
    L:DOWN

and

    C:REPLACE ID
    F:CRASH GAP=1
    L:DOWN

Their selected residual and PUBLIC continuation are equal.  The first has one
NONE branch; the second has ordered OLD and NEW branches.  Their kinds are
IDLE_RECOVERY and PENDING_NON_T, so Section 7.3 does not permit quotient
comparison.  The pair demonstrates a manifest distinction, not a literal
between-execution lower bound.

### W4 — FIN-pending versus terminal

The shortest prefixes are:

    H(); C:FIN; F:CRASH GAP=1
         L:DOWN

and

    H(); C:FIN; R:STOPPED
         F:CRASH GAP=2
         L:DOWN

The first future is `F:RESUME FIN_PENDING; L:READY; R:STOPPED`; the second is
`F:RESUME TERMINAL; L:READY` and has no later C or R.  The futures differ with
zero ordinary C, but the cut kinds differ.  Thus the grammar forces both
phase behaviors while the literal equivalence relation supplies no
cross-kind MERGE witness.

### W5 — smallest proved clean merger

`H()` and `H(RI)` are both CLEAN cuts with `d=3` and residual
`(U,EMPTY,E0)`.  `H(RI)` additionally contains:

    C:REPLACE ID
    R:ERR EMPTY

The prefix is omitted from comparison.  Exhaustive future enumeration through
the full allowance and every one-crash linear gap found equal futures.  This
is the smallest intended exact pre-cut distinction that execution may forget.

### W6 — smallest same-kind request-identity merger after SELECT

From `H()` interrupt RI and RN immediately after C:

    C:REPLACE ID
    F:CRASH GAP=1
    L:DOWN

versus

    C:REPLACE NOT
    F:CRASH GAP=1
    L:DOWN

Both are `PENDING_NON_T`, have `d=2`, and are no-ops at `(U,EMPTY,E0)`.
Their ordered OLD/NEW recovery suffixes are byte-identical.  After SELECT, the
request identity has no permitted future observer if selected residual,
allowance, phase, and branch fact agree.

### W7 — T before A versus T after A

From `H()`:

    C:ATTEMPT
    F:CRASH GAP=1
    L:DOWN

versus

    C:ATTEMPT
    A:TRY O=U P=EMPTY E=E0 V=NONE
    F:CRASH GAP=2
    L:DOWN

The recovery suffixes are equal at fixed residual and `d=2`, while the full
prefixes differ by the A crossing.  The seed gives the cuts different kinds,
`T_PRE_A` and `T_POST_A`; literal Section 7.3 consequently forbids the merger
that Section 11.4 asserts.  It cannot prove a literal MAY FORGET verdict.

### W8 — unused allowance after FIN

These same-kind FIN_PENDING cuts differ in unused pre-FIN allowance:

    H(); C:FIN
         F:CRASH GAP=1
         L:DOWN

and

    H(); C:OBSERVE 0
         R:OK OBSERVE 0
         C:FIN
         F:CRASH GAP=3
         L:DOWN

Their complete recovery suffix is identical.  FIN makes the numerical
allowance dead, and no `F:ALLOWANCE` is emitted.  The differing value may be
forgotten by execution; an evidence evaluator can recompute it from ordinary
C occurrences if the exact prefix remains.

### W9 — unselected alternative after one realized selection

From `H()` interrupt AI and AN after C.  Both are same-kind cuts with `d=2`
and the same OLD endpoint `EMPTY`; their NEW endpoints are ID and NOT.  In an
OLD realized branch, both continue as:

    F:SELECT old
    F:RESUME ACTIVE O=U P=EMPTY E=E0
    F:ALLOWANCE 2
    L:READY

followed by the same controller future.  The complete two-branch `Priv`
families differ in their NEW records.  The selected execution may forget that
alternative only after the complete family is retained as evidence elsewhere.

### D1 — exact output-byte derivation

For a named pre-residual, request, selected branch or special phase, and `d`,
Sections 3 and 4 are total finite functions for ordinary reply bytes, A bytes,
`F:RESUME`, and `F:ALLOWANCE`.  This derives expected bytes.  It does not prove
that regenerated bytes were the bytes independently observed at a boundary.

### D2 — residual fold

Starting from `(U,EMPTY,E0)`, process each validated ordinary R as one
application, `F:SELECT new` as one interrupted application, and
`F:SELECT old` as none.  This mechanically derives the residual from a
validated full application history plus the specification.

### D3 — allowance fold

Before FIN, `d = 3 - N`, where `N` is the number of ordinary C occurrences
since the declared cut.  FIN does not decrement.  This mechanically derives
`d` from the exact C history; after FIN, W8 shows that `d` has no future role.

### D4 — projection and Must limitation

Each viewer projection and May deduplication is mechanical from complete
branch traces.  The combined `Viewer May sets and Must mask` responsibility is
not total, however: the frozen sources leave Must's recovery-cut history scope
as suffix-only versus prefix-plus-suffix.  The executable chose and disclosed
a scope for its experiment; that choice does not repair the frozen rule.

## 2. Responsibility-by-responsibility ledger

The candidate label is quoted for comparison.  Audit verdicts apply only to
their column's scope.

| # | Section 14 responsibility | Candidate label | Smallest collision or derivation | Manifest evidence | Between executions |
|---:|---|---|---|---|---|
| 1 | Distinguish fourteen clean classes | MUST SURVIVE | W1; every unequal residual changes zero-ordinary-C SELECTOR/Priv | MAY REBUILD | MUST SURVIVE |
| 2 | Distinguish contractual recovery branch/phase/allowance classes | MUST SURVIVE | W2 forces orientation, but the claimed 315 classes conflict with the literal 415; phase and live-allowance domains are also gated | UNKNOWN | UNKNOWN |
| 3 | Exact specification identity and application rules | MUST SURVIVE | No legal pair varies specification identity; no derivation of the authority from lower surviving inputs is named | UNKNOWN | UNKNOWN |
| 4 | Controller allowance and continuation policy during a full run | MUST SURVIVE | D3 derives allowance, but a total controller policy, including unused keys, is not derivable from a realized trace; D/G identity is unresolved | MUST SURVIVE | UNKNOWN |
| 5 | Selector authority and OLD/NEW branch association | MUST SURVIVE | W2; deleting orientation changes SELECTOR/Priv with zero ordinary C | MUST SURVIVE | MUST SURVIVE |
| 6 | Complete branch records before May dedup | MUST SURVIVE | W3 and the two records of any interrupted no-op; deleting a record changes `Priv` even when PUBLIC dedups | MUST SURVIVE | MAY FORGET |
| 7 | FIN-pending exactly-one STOPPED responsibility | MUST SURVIVE | W4; the phase is derivable as FIN without STOPPED, and deleting the owed STOPPED changes that cut's required suffix | MAY REBUILD | MUST SURVIVE |
| 8 | Terminal no-more-C/R responsibility | MUST SURVIVE | W4; the phase is derivable as STOPPED already crossed, and any later C/R violates the required suffix | MAY REBUILD | MUST SURVIVE |
| 9 | An A crossing that already occurred | MUST SURVIVE | W7; the A is in the exact prefix but absent from the compared suffix, and literal kind gating prevents the proposed future merger | MUST SURVIVE | UNKNOWN |
| 10 | Canonical codec and closure-domain identity | MUST SURVIVE | EncCut/EncBranchRecord presence, witness-viewer admissibility, and G closure have multiple frozen-text readings | UNKNOWN | UNKNOWN |
| 11 | Exact reply, A, RESUME, and ALLOWANCE bytes | MAY REBUILD | D1 | MUST SURVIVE | MAY REBUILD |
| 12 | Clean residual coordinate | MAY REBUILD | D2; W5 also shows different prefixes can fold to the same coordinate | MAY REBUILD | MAY REBUILD |
| 13 | Remaining d before FIN | MAY REBUILD | D3 | MAY REBUILD | MAY REBUILD |
| 14 | Viewer May sets and Must mask | MAY REBUILD | D4; projections are derived, but the combined Must scope is unfrozen | UNKNOWN | UNKNOWN |
| 15 | Exact pre-cut distinctions within one proved clean class | MAY FORGET | W5; same kind, same live allowance, exhaustive equal future | MUST SURVIVE | MAY FORGET |
| 16 | Interrupted ordinary R completion | MAY FORGET | In W2's interrupted occurrences no such R crossed; every permitted branch omits it and a later unpaired R fails Must 3 | MAY REBUILD | MAY FORGET |
| 17 | Interrupted request identity after SELECT | MAY FORGET | W6; same-kind exact future merger | MUST SURVIVE | MAY FORGET |
| 18 | Pre-A versus post-A service continuation | MAY FORGET | W7 has equal suffix behavior but different cut kinds; the literal relation forbids the claimed merger | MUST SURVIVE | UNKNOWN |
| 19 | Unused allowance after FIN | MAY FORGET | W8; same-kind exact future merger, with D3 available for evidence reconstruction | MAY REBUILD | MAY FORGET |
| 20 | Old/new alternative not selected in one realized branch | MAY FORGET | W9; equal selected OLD future, conditional on retaining both complete conformance records elsewhere | MUST SURVIVE | MAY FORGET |

### 2.1 Why the two evidence columns differ

Rows 15, 17, 19, and 20 have genuine execution-side mergers.  Their exact
pre-cut differences may nevertheless be needed in an experiment manifest to
prove which corpus case was run.  Forgetting a service continuation is not
permission to rewrite the evidence record.

Rows 6 and 9 are the converse trap.  R0.1I declares complete branch records
and the already-crossed A to be contractual full-history evidence.  No legal
future query retrieves either fact from the omitted prefix.  Their manifest
importance therefore does not establish a service-state persistence lower
bound.  In particular, the executable's exact-prefix count and Must audit
show that the facts were represented in its model; they do not show capture
durability or cold-start survival.

Rows 7 and 8 are obligations, not arguments for a particular phase bit.  A
system may mechanically fold the exact prefix to recover FIN_PENDING or
TERMINAL, but some total-system input must still distinguish the obligations
long enough to produce STOPPED exactly once or prohibit all later C/R.

## 3. Mandatory attack accounting

### DELETE

The finite rules give semantic deletion controls for rows 1, 5, 6, 7, and 8:
remove the clean distinction, orientation, a branch record, owed STOPPED, or
terminal prohibition and the stated future changes.  No source reports the
required cold-start deletion of a named implementation responsibility for any
row.  Physical or operational DELETE evidence is therefore **UNKNOWN**.

For rows 9, 15, 17, 18, 19, and 20, deletion must be scoped.  Deleting an exact
prefix fact from the retained manifest changes the evidence identity.  That
does not imply that the selected service continuation must retain it.

### MERGE

The exact finite MERGE inventory is:

- W1 and W2 are forbidden mergers: they change contractual futures.
- W5 and W6 are permitted literal same-kind mergers.
- W8 is a permitted same-kind merger after FIN.
- W9 is a permitted selected-branch merger only after its unlike complete
  branch families remain retained externally.
- W7 is behaviorally equal but not a permitted literal merger because the cut
  kinds differ.

The advertised 139/315 recovery counts cannot serve as persistence evidence:
they use a cross-kind relation different from literal Section 7.3.  Literal
counts are 238 PUBLIC and 415 privileged.

### DERIVE

D1, D2, and D3 are total finite derivations of expected boundary bytes,
residual, and pre-FIN allowance from named inputs.  Viewer projections and May
sets are also mechanically derived from complete branch traces.  A derived
expected byte is not independent observation evidence, and the combined Must
derivation remains **UNKNOWN** because its history scope is not frozen.

Specification identity, total controller policy, selector authority,
unobserved alternative execution evidence, and canonical closure identity
have no derivation from smaller named surviving inputs in the authorized
sources.

### RECOMPUTE

No authorized source performs a restart without a target form, measures replay
or evaluation work, or records recovery dependencies.  D1-D3 prove finite
recomputability only.  Runtime, cost, cold-start availability, and dependency
survival are **UNKNOWN**.

### EXTERNALIZE

R0.1I names the controller, capture peer, selector, manifest, specification,
canonicalizer, and build inputs as external or total-system carriers.  No
severing experiment was run.  Moving rows 4, 5, 6, 9, 10, 11, 15, 17, 18, or
20 to one of those carriers is movement, not deletion, and does not establish
availability across executions.  Externalization evidence is **UNKNOWN**.

### COGNITION

No fresh implementer was given only the frozen sources with time, choices,
and errors recorded.  The missing EncCut field-presence map, branch residual
population rule, Must scope, G closure scope, and witness-viewer admissibility
already demonstrate undocumented choices.  COGNITION evidence is **UNKNOWN**.

### TCB

No runtime, OS, transport, serializer, compiler, cache, fault hook, capture
peer, selector, manifest, oracle, canonicalizer, specification, or build input
was independently perturbed.  The experiment and its manifest are model
evidence produced by code that necessarily shares some of those influences.
TCB persistence evidence is **UNKNOWN**.

## 4. Collision-ledger conclusion

R0.1I establishes several finite behavioral lower bounds and several exact
mergers, but it does not justify its Section 14 table as one undifferentiated
persistence classification.

- W1 and W2 force clean-coordinate and selector-orientation information to
  survive somewhere in the total system.
- D1-D3 justify rebuilding expected bytes, residual, and pre-FIN allowance
  from named surviving inputs, without establishing replay cost.
- W5, W6, W8, and W9 justify tightly scoped forgetting.
- W7 is not a legal literal merger, so pre-A/post-A forgetting remains
  UNKNOWN under the frozen relation.
- Exact-history and branch-family artifacts often MUST SURVIVE in the
  experiment manifest even when the service continuation MAY FORGET them.
- The 315-class recovery responsibility, specification/codec identity,
  combined May/Must reconstruction, external availability, cognition, and TCB
  persistence remain UNKNOWN.

These are information-flow verdicts only.  They select no record, field,
journal, service, device, or storage family.
