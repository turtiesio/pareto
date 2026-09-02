# R0.1I unified all-cuts behavioral quotient audit

## 0. Status and claim boundary

This note evaluates one conditional mathematical hypothesis: remove the
same-cut-kind comparability guard from R0.1I and place all 157 clean cuts and
all 1,208,272 recovery cuts in one behavioral quotient.

The only source files inspected were:

| Source | SHA-256 |
|---|---|
| `HISTORY-SEED-R01I.md` | `d52c083c34aa37144fa47ee8a02d9279adb75029613125f38dad5a98b0df8d9c` |
| `POSTFREEZE-BREAK-R01I.md` | `57f007f0457595e5545eb9dd76fda210b9eea94483a1d74cb6d074230b8ac015` |
| `r01i_recovery_experiment.py` | `770269f9a723d7a737a6a4c3c6e8e3a27952213b9b60c31b09924bc3c3888ff1` |

No archive, proposed replacement, implementation, or persistence design was
inspected. Nothing here is an architecture, representation, storage,
durability, physical-recovery, or implementation claim.

The result is:

- **153 PUBLIC classes** over both the 868 normalized conditions and the
  1,208,429 exact cut histories;
- **329 privileged classes** over both populations; and
- **no clean class merges with any recovery class**.

Those numbers are exact for the legal-path total-table hypothesis in Section
1. They are not a theorem of merely deleting one sentence from the seed. The
seed does not define a raw action at every mismatched phase. Section 7 states
the extra semantics required before this can become an unconditional new
contract.

## 1. Conditional common interface

Call the tested hypothesis **LPT** (legal-path total tables):

1. The exact prefix before a cut remains excluded from the compared suffix,
   as in Section 7.3 of the seed.
2. One controller truth table over the seed's union domain `D` and one
   scheduler bit vector over its union domain `G` are used on both sides of
   every comparison.
3. A recovery cut first performs its mandatory recovery closure. Pending
   requests produce the ordered OLD/NEW oracle family; idle, FIN-pending, and
   terminal cuts produce their required NONE branch. The controller is
   consulted only after an active branch reaches READY.
4. SELECT is an oracle branch label, not a new client command. A table entry
   whose key is not reached is inert. Scheduler bits are ignored after the
   crash budget is spent, exactly as the seed states.
5. The remaining allowance is behavioral, not a comparability axiom. At
   `d=0`, FIN is forced. Different live allowances are separated by the legal
   controller that repeatedly sends an ordinary request while `d>0`; in the
   privileged view they are also exposed by `F:ALLOWANCE` after active
   recovery.
6. PUBLIC equality compares `May_PUBLIC` for every common table pair.
   Privileged equality compares the ordered branch record, all four May
   projections, and Must for every common table pair.

Thus the kind tag is not placed in a grouping key. Phase matters only when its
specified continuation emits different behavior. Dead source allowance and
source residual remain irrelevant after FIN or STOPPED.

LPT uses only legal reachable actions. If “common total interface” instead
means that every raw command can be issued in every phase, the seed is
incomplete; Section 7 is then mandatory.

## 2. Exact enumeration method

The recount used no implementation hash as an equality oracle.

1. Enumerating all words of length zero through two reproduced 157 distinct
   clean histories and fourteen residual conditions. Their exact-history
   multiplicities are:

       2×8, 16×3, 17×2, 59×1.

2. For every clean residual, every completed future word of length zero
   through three was folded exactly. The six recovery constructions produced
   854 normalized conditions and exact lift weights summing to 1,208,272.
3. For each normalized recovery condition, all legal words through its
   remaining allowance were evaluated with the exact branch generator. PUBLIC
   grouping used exact encoded projected trace sets. Privileged grouping used
   exact encoded ordered outcomes. Cut kind was omitted; live `d` was retained
   only because Step 5 of LPT makes unequal `d` behaviorally separable.
4. The direct trace grouping reproduced 139 recovery PUBLIC classes with
   normalized histogram

       1×64, 2×40, 9×6, 10×18, 11×8, 68×2, 252×1,

   and 315 recovery privileged classes with normalized histogram

       1×263, 8×9, 9×27, 10×14, 68×2.

   All 122,908 branch-family evaluations performed during that signature run
   satisfied all ten declared Must implications.
5. The fourteen clean conditions were then compared against every recovery
   condition with the common separator in Section 4. There were zero PUBLIC
   and zero SELECTOR signature collisions.

The exact-history histograms below are a symbolic exact lift, not a sampled or
hash-based estimate: every exact history contributes once to its enumerated
normalized condition, and exact future equality was checked at that condition.

## 3. Unified normalized quotient

The 868 normalized objects decompose as follows:

| Family | Raw normalized conditions | PUBLIC classes | Privileged classes |
|---|---:|---:|---:|
| Clean, `d=3` | 14 | 14 | 14 |
| Active recovery, `d=3` | 14 | 14 | 14 |
| Active recovery, `d=2` | 200 | 59 | 89 |
| Active recovery, `d=1` | 252 | 63 | 105 |
| Active recovery, `d=0` | 252 | 1 | 105 |
| FIN-pending recovery | 68 | 1 | 1 |
| Terminal recovery | 68 | 1 | 1 |
| **Total** | **868** | **153** | **329** |

The PUBLIC recovery terms are the seed's behavioral vertex/undirected-edge
quotient:

    14 + (18+41) + (18+45) + 1 + 1 + 1 = 139.

The privileged recovery terms retain no-selector vertices, equal-selector
vertices, and directed changing edges:

    14 + (18+14+57) + (18+18+69) + (18+18+69) + 1 + 1
    = 315.

The clean fourteen are separate from all 139 or 315 recovery classes, so:

    PUBLIC:      14 + 139 = 153
    privileged:  14 + 315 = 329.

The unified normalized class-multiplicity histograms, where `s×n` means `n`
classes containing `s` normalized conditions, are:

    PUBLIC:
    1×78, 2×40, 9×6, 10×18, 11×8, 68×2, 252×1.

    privileged:
    1×277, 8×9, 9×27, 10×14, 68×2.

Checks:

    PUBLIC classes: 78+40+6+18+8+2+1 = 153
    PUBLIC objects: 78+2*40+9*6+10*18+11*8+68*2+252 = 868

    privileged classes: 277+9+27+14+2 = 329
    privileged objects: 277+8*9+9*27+10*14+68*2 = 868.

## 4. No clean/recovery merger and the smallest separators

One common policy separates every clean cut from every recovery cut:

- choose FIN at every reached idle controller key; and
- use the all-zero scheduler vector.

FIN is typed and is not an ordinary C, so this policy spends zero ordinary
messages. The complete PUBLIC suffix shapes are:

| Starting family | Deduplicated PUBLIC suffix shape |
|---|---|
| Clean | `C:FIN, R:STOPPED` |
| Active recovery: idle, pending non-T, T pre-A, or T post-A | `L:READY, C:FIN, R:STOPPED` |
| FIN-pending recovery | `L:READY, R:STOPPED` |
| Terminal recovery | `L:READY` |

The recovery cut is after its prefix DOWN, so the READY in this table is part
of the compared suffix. It cannot be canceled by prefix omission. None of the
854 recovery conditions has the clean PUBLIC signature under this policy.

SELECTOR is even more direct. With no clean crash, the clean SELECTOR suffix is
empty. Every recovery family emits a nonempty selector suffix:

- idle: `RESUME ACTIVE ...; ALLOWANCE d`;
- pending non-T or either T phase: `SELECT old/new; RESUME ACTIVE ...;
  ALLOWANCE d`;
- FIN-pending: `RESUME FIN_PENDING`; or
- terminal: `RESUME TERMINAL`.

Consequently Priv is also unequal for every clean/recovery pair.

The smallest exact cross-family pair is the clean `H()` cut and its initial
idle recovery cut

    H(); F:CRASH GAP=0; L:DOWN; [cut].

Both prefixes contain zero ordinary C crossings. Under the policy above,
PUBLIC distinguishes them by the recovery READY, and SELECTOR distinguishes
empty from `RESUME ACTIVE O=U P=EMPTY E=E0; ALLOWANCE 3`. Zero ordinary
messages is minimal. The same policy is a universal cross-family separator,
not merely a witness for this smallest pair.

This no-merger result is robust under any conservative totalization that
retains the seed's legal traces: adding invalid-action observations may split
classes, but it cannot erase this already legal separator.

## 5. Unified exact-history quotient

Every one of the 1,208,429 exact cuts maps to one of the 868 normalized
conditions. No clean class crosses into a recovery class, so the unified exact
class count is again 153 PUBLIC and 329 privileged.

The exact PUBLIC class-size histogram is:

    2×28, 4×6, 6×4, 12×4, 16×14, 17×6, 18×2, 19×4,
    32×1, 34×1, 50×4, 53×4, 59×9, 68×2, 71×4, 73×2,
    75×2, 100×1, 106×5, 187×6, 191×2, 216×2, 241×2,
    269×4, 282×4, 315×2, 335×1, 369×2, 374×1, 432×1,
    445×3, 632×2, 917×1, 1278×2, 1410×4, 1479×2,
    3437×2, 3792×1, 4439×2, 7049×1, 295945×2,
    565200×1.

It contains 153 classes and its weighted sum is 1,208,429.

The exact privileged class-size histogram is:

    2×46, 6×16, 16×20, 17×12, 18×6, 20×2, 50×10, 53×28,
    59×7, 60×4, 128×2, 144×1, 153×2, 187×12, 191×5,
    216×10, 222×16, 445×6, 450×2, 472×1, 477×4, 530×2,
    828×10, 933×20, 949×8, 1496×2, 1719×1, 1941×12,
    1944×2, 2073×5, 2220×4, 2495×10, 3489×6, 3560×1,
    5152×4, 7452×2, 8397×4, 9490×2, 11466×2, 13766×4,
    14502×2, 15528×2, 18657×1, 19017×2, 21729×1,
    22455×2, 27810×2, 27912×1, 28305×1, 295945×2.

It contains 329 classes and its weighted sum is 1,208,429.

The only changes from the exact recovery histograms are the fourteen clean
classes:

    2×8, 16×3, 17×2, 59×1.

That additive relation is justified by the exhaustive cross-family collision
check in Section 4; it was not assumed.

## 6. What the quotient does and does not forget

Removing the kind guard permits the recovery mergers already described by the
suffix behavior:

- PUBLIC forgets no-selector versus selector-no-op recovery cause at fixed
  live behavior, treats a changing recovery as an unordered endpoint edge,
  and at `d=0` merges every active recovery condition.
- Privileged behavior distinguishes no selector, equal OLD/NEW selector
  branches, and directed changing branches. It can forget the interrupted
  no-op request identity and can merge T pre-A with T post-A because the
  already-crossed A is in the omitted prefix.
- FIN-pending sources merge with one another, terminal sources merge with one
  another, and the two special phases remain separate.

It does **not** permit clean/recovery merging. READY and the mandatory recovery
records survive in the continuation even though the pre-cut prefix does not.

These are behavioral statements about the stipulated finite suffix oracle.
They do not say that a phase tag, residual, branch record, history, or any
other datum may be physically deleted or need be stored in a particular form.

## 7. Missing raw total-action semantics

The seed makes controller and scheduler *tables* total on their finite union
domains, but it does not make every conceivable raw action meaningful in every
phase. Therefore LPT is a complete legal-path quotient, not a fully specified
raw labeled transition system.

Before a stronger “every action at every cut” quotient is well-defined, a new
specification must fix all of the following:

| Action family | Mismatched cases needing a total rule |
|---|---|
| Client ordinary C or FIN | Before recovery READY; while another request is pending; at `d=0`; after FIN; after STOPPED; at terminal recovery |
| Selector OLD/NEW/NONE | Clean and idle cuts; wrong or absent label at a pending cut; FIN-pending and terminal cuts; duplicate selection |
| Scheduler pass/crash | At the recovery cut after the crash budget is spent; during mandatory recovery; after terminal END; a second crash request |
| Service/oracle crossing proposal | Unexpected R, A, READY, RESUME, ALLOWANCE, or STOPPED for the current phase |

For every such case the contract must additionally say:

1. whether the action is rejected, ignored, or causes a transition;
2. the exact typed result and which viewer projections retain it;
3. whether the experiment terminates or may continue;
4. whether allowance or crash budget changes;
5. whether a branch record is produced and what its label, selected
   residual/phase, and Must evidence are; and
6. whether recovery closure has priority over an offered external action.

These choices are quotient-relevant. For example, exposing SELECT as a raw
input makes it valid at pending recovery but invalid at idle recovery; a
phase-specific error would split PUBLIC or privileged classes that LPT merges.
Encoding the hidden cut kind in an error reason would refine still more.
Ignoring an invalid action, terminating it uniformly, and stuttering it are
also observably different once later continuation is allowed.

Accordingly:

- **153/329 is exact for LPT** and is the coarsest all-cuts quotient supported
  by the existing legal continuation traces under the stated relaxation.
- Any conservative raw-action totalization preserves the no-clean/recovery-
  merger proof but may increase either class count.
- No unique stronger quotient follows until the invalid and mismatched phase
  semantics above are frozen.

## 8. Conditional conclusion

Deleting only the same-cut-kind gate exposes a coherent all-cuts behavioral
hypothesis when the seed's common total controller/scheduler tables are used
as the interface. Its exact quotient is:

| Population | PUBLIC | Privileged |
|---|---:|---:|
| 868 normalized conditions | **153** | **329** |
| 1,208,429 exact cut histories | **153** | **329** |

The result is not `139/315`: those are the recovery-only counts. Nor do any of
the fourteen clean classes disappear into them. A zero-ordinary-message legal
continuation separates clean from recovery universally.

This conditional quotient is a finite mathematical observation only. It
supplies no persistence, deletion, realization, externalization, TCB, human,
or architectural evidence.
