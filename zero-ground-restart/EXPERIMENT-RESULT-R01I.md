# R0.1I executable recovery experiment result

## Frozen inputs

| Artifact | Identity |
|---|---|
| Candidate | `HISTORY-SEED-R01I.md`, SHA-256 `d52c083c34aa37144fa47ee8a02d9279adb75029613125f38dad5a98b0df8d9c` |
| Falsifier | `r01i_recovery_experiment.py`, SHA-256 `770269f9a723d7a737a6a4c3c6e8e3a27952213b9b60c31b09924bc3c3888ff1` |
| Falsifier commit | `a905bedc256e138a63b15ea7db740e14021fb99b` |

The program checks the seed hash before doing semantic work and exits one on
any finite failure. It does not edit the seed.

## Independent run

The frozen script was run from `/root/pareto` with Python 3 while stdout was
fed directly to SHA-256. The run completed with:

| Measure | Result |
|---|---:|
| Exit status | 1, expected for a falsified candidate |
| PASS | 97 |
| FAIL | 5 |
| UNKNOWN | 7 |
| Stdout SHA-256 | `5172c93e092b60837f759ea2cf7326d32124cf4f84c490394d18fc82c93e341f` |
| Wall time | 111.38 s |
| User CPU | 110.96 s |
| System CPU | 0.40 s |
| Maximum resident set | 330,196 KiB |

The stdout was not retained as a second authority. The frozen program emits
the complete sorted JSON result deterministically; its digest identifies this
run.

## What was directly enumerated

- all 157 clean histories and their fourteen residual classes;
- all 12,246 clean unordered pairs;
- all 1,208,272 exact recovery prefixes, with exact crossing-sequence
  uniqueness checked by an injective finite-alphabet sequence code;
- all 854 normalized recovery conditions;
- exact future probe bytes for every normalized condition through its entire
  remaining allowance;
- every no-crash and one-crash linear word/gap structure through depth three
  for every reachable clean residual;
- 122,908 generated recovery branch families evaluated against all ten Must
  propositions; and
- ten independently mutated families, one targeted at each Must bit.

The exact-prefix class-size lifts map the enumerated 1,208,272 prefixes through
their normalized conditions. They are explicitly symbolic lifts; the program
does not mislabel them as 1.2 million separate future evaluations.

## Reproduced claims

- clean count 157, clean quotient 14, and the stated clean class-size
  multiset;
- 2,351 same-class and 9,895 unequal clean pairs;
- recovery phase total 1,208,272 and total cuts 1,208,429;
- normalized recovery total 854;
- relaxed suffix-only quotients 139 PUBLIC and 315 privileged;
- the relaxed 315-class multiplicity histogram;
- all base and padded linear schedule counts, including 3,910,242 padded
  slots across the clean corpus;
- generated branch families satisfy all ten Must implications; and
- each of the ten targeted corruptions is detected by its intended Must bit.

These passes are finite-model evidence only. They are not realization,
physical persistence, externalization, cognition, or TCB evidence.

## Five finite failures

1. Prediction 3's “no empty separator” is false contractually. With controller
   FIN and a crash at the initial pre-FIN gap, SELECTOR sees the residual in
   `F:RESUME` with zero ordinary C occurrences.
2. Literal Section 7.3 yields 238 PUBLIC classes, not the printed 139.
3. Literal Section 7.3 yields 415 privileged classes, not 315.
4. The literal privileged histogram is
   `363x1, 9x6, 27x7, 14x8, 2x68`, not the advertised histogram.
5. Section 11.4's T-pre/T-post merger has equal future suffix bytes but is
   forbidden by their distinct cut kinds under Section 7.3.

The relaxed 139/315 values are not arithmetic mistakes. They are exact results
for a different relation which deletes the frozen same-kind gate.

## Seven explicit unknowns

- the kind-to-optional-field map for `EncCut`;
- the semantic population rule for `EncBranchRecord`'s residual;
- exact `EncWitness` bytes that depend on those two rules;
- viewer eligibility for a canonical witness;
- numeric `D` closure size and controller-table count;
- numeric `G` closure size and scheduler-table count; and
- the unexecuted DELETE/DERIVE/RECOMPUTE/EXTERNALIZE/REALIZE/COGNITION/TCB
  gate.

The separate blind break derives conditional `D` and `G` closures; this
program intentionally does not import them or convert that independent result
into a pass.

## Interpretation

The experiment falsifies R0.1I without selecting a representation. It also
shows which parts of the finite corpus are stable enough to reuse as attacks:
the corpus arithmetic, transition behavior, exact recovery prefixes, and
relaxed behavioral signatures. The frozen equivalence relation, witness
minimum, and canonical-byte claim do not survive.
