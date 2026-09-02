# R0.1J executable finite-history experiment result

## Frozen inputs

| Artifact | Identity |
|---|---|
| Candidate | `HISTORY-SEED-R01J.md`, commit `c1ddc239ec17516e53c30d8225a396c3348dbdde`, SHA-256 `7c9b2a742eab81f6c104b6ca3566315ddb29ecc63d216d25cff91bf1c70836dc` |
| Falsifier | `r01j_history_experiment.py`, commit `1db2506930b58d9178a31d13fbe2d0774b7c08c0`, SHA-256 `55ae07d48029e326cfe32390e8cd5ad4254a6624902a7752a561cc2881120d35` |

The final falsifier commit changes only the falsifier. The program verifies the
candidate digest before semantic work, does not edit the candidate, and exits
one when any finite check fails. It implements the candidate's literal formal
rules; explicit collision controls then test responsibilities and evidence
semantics that the frozen candidate omitted or left outside its bytes.

## Runs

The author's post-commit verification emitted the complete result JSON and
reported:

| Measure | Result |
|---|---:|
| Exit status | 1 |
| PASS | 63 |
| FAIL | 5 |
| UNKNOWN | 4 |
| Whole-program elapsed time recorded in JSON | 287.949434 s |
| Wrapper wall time | 288.049929 s |
| Maximum resident set | 175,232 KiB |
| Whole-stdout SHA-256 | `fa132536f0aff45e2592f23cccd04c88cd7e50bfb51cd409b4a89a705b12a930` |

An independent run from `/root/pareto` used

    set -o pipefail
    /usr/bin/time -v python3 -B zero-ground-restart/r01j_history_experiment.py | sha256sum

and reported:

| Measure | Result |
|---|---:|
| Exit status | 1 |
| Wall time | 294.08 s |
| User CPU | 292.63 s |
| System CPU | 1.33 s |
| Maximum resident set | 174,052 KiB |
| Whole-stdout SHA-256 | `7d7aff5aff0e9ce04a1ac7ebcc316361428efca2ff24d2b21fa80e7f1a558588` |

The JSON contains measured runtime, so byte-identical whole-report regeneration
is not expected. The unequal hashes alone do not prove that timing is their only
difference and do not independently reproduce the named verdicts. The author's
full-output run supplies the 63/5/4 summary and names; the separate run verifies
the exact frozen source's exit behavior and resource envelope and supplies an
independent whole-output digest. No runtime-stripped normalized comparison was
performed. Run-specific timing does not participate in the candidate's
quotient.

## Directly executed finite domain

The executable directly constructs and folds:

- all 157 clean histories and their fourteen residual values;
- the arithmetic for all 12,246 unordered clean-history pairs, including
  2,351 same-residual and 9,895 unequal-residual pairs, plus direct separator
  execution for all 91 unequal residual-value pairs;
- all 1,208,272 recovery histories, 7,696 from each clean history;
- all 1,208,429 declared clean and recovery cuts;
- all 854 normalized recovery conditions and their seven phase/family counts;
- the partitions of 854 normalized recovery conditions under 1,885 fixed
  failure-free request words of length zero through three, applying the same
  word to both selector branches;
- the decision-key closure `D` and one-crash gap-key closure `G`, seeded from
  fourteen clean residual coordinates and the normalized recovery conditions;
- all eight FIN-path scheduler masks for the bounded clean separator checks;
- structural and negative controls for cut, controller, scheduler, witness,
  evidence-case, and manifest codecs; and
- the five responsibility/evidence collision controls listed below.

Every exact recovery history is parsed, folded, serialized into the ordered
enumeration digest, and counted. Quotient signatures are evaluated over the
854 normalized conditions and then lifted symbolically to exact histories.
The executable does not relabel that lift as 1,208,272 independent future
evaluations.

## Bounded formal results reproduced

The finite formal model reproduces:

| Claim | Result |
|---|---:|
| Clean histories | 157 |
| Clean residual classes | 14 |
| Exact recovery histories | 1,208,272 |
| Normalized recovery conditions | 854 |
| Fixed-word recovery PUBLIC partition | 139 |
| Fixed-word recovery contractual partition | 315 |
| Derived combined PUBLIC image count | 153 |
| Derived combined contractual class count | 329 |
| `D` closure | 82,224 |
| `G` closure | 64,067 |

The 153/329 results combine the normalized recovery refinement, fourteen clean
residual classes, and a FIN/pass clean-versus-recovery no-merger witness. The
script does not enumerate the full adaptive controller-table universe and does
not prove that the fixed-word probe basis is complete for that universe. The
fresh blind and literal audits provide separate support for the quoted counts;
this executable result does not silently import their stronger claim.

It also reproduces the candidate's exact clean class-size multiset, normalized
recovery family counts, clean separation controls, Q1 minimization within eight
FIN-path scheduler masks and eligible scopes, Q2 construction/separation/codec
controls, seven representative start-phase routes under one FIN/no-crash
policy pair, exact FIN/terminal STOPPED behavior for that pair, negative codec
precedence controls, and literal source tables.

These are passes about the frozen finite formal realization. They are not
evidence that the persistence classification is complete, that a physical
realization exists, or that external evidence and trust responsibilities have
been encoded.

## Five finite failures and their smallest exhibited collisions

These five statuses are literal audit expectations added by the falsifier.
They are not all failed numeric predictions printed by the candidate.

1. `responsibility_table_includes_recovery_closure_owed` fails. Compare clean
   `H()` with its initial idle-recovery cut at the same residual. Under FIN and
   pass, recovery must first expose RESUME/READY while clean execution does not.
   Section 10 classifies no bit of responsibility for whether this recovery
   closure is still owed. Deleting that phase fact merges the pair. This is the
   Q7 collision and requires zero post-cut ordinary requests.

2. `timeout_progress_evidence_is_collision_free` fails. A kind-1 observation
   has an obligatorily empty body. Timeout before any crossing and timeout
   after a typed `C:FIN` crossing has been captured therefore encode to the
   same observation bytes, although the permitted audit can distinguish the
   captured prefix and expiry point.

3. `finite_conformance_failure_survives_mixed_timeout_manifest` fails. A
   manifest containing one timeout and one finite wrong-payload trace is
   classified `UNKNOWN(OBSERVATION_BOUND)` because timeout precedence returns
   first. The independently decidable `FAIL(CONFORMANCE)` is masked.

4. `two_timeout_cases_have_per_case_envelope_binding_and_tie_rule` fails. Two
   timeout cases can differ in whether the external run was qualified as
   non-total, but the manifest binds neither qualification per case and defines
   no rule for combining their verdicts. The bytes cannot determine the
   aggregate result.

5. `same_manifest_has_context_independent_total_verdict` fails. Identical
   single-timeout manifest bytes classify as `UNKNOWN(OBSERVATION_BOUND)` with
   no supplied flag and `FAIL(NON_TOTAL)` with an unencoded external Boolean.
   Consequently the advertised classifier is not a function of its persisted
   manifest bytes.

Failures 2 through 5 are not four names for one malformed byte string. They
exhibit three separate responsibilities: retain captured progress and expiry,
preserve finite failures when other cases are incomplete, and bind all context
needed to compute a multi-case verdict.

## Four executable UNKNOWNs

- `arbitrary_pair_canonical_witness_search`: only Q1 is minimized within the
  eight FIN-path masks and scopes; Q2 is constructed and checked, and neither
  establishes arbitrary-pair global minimization.
- `zero_case_manifest_evidentiary_adequacy`: a syntactically valid zero-case
  manifest establishes no generator, verifier, or realization property.
- `origin0_only_manifest_is_not_a_verifier_test`: generated valid traces do not
  exercise rejection of invalid realized observations.
- `experiment_envelope_encoding_and_manifest_binding`: no envelope bytes,
  authority, signature grammar, or case-binding rule are frozen.

The exact-history quotient class-size multiplicities, global arbitrary-pair
witness search, operational raw-input grammar, external controller/scheduler
availability, capture durability, human cognition, TCB perturbation, and unlike
physical realizations also remain outside this executable's supported claims.
They are not counted as passes merely because the finite formal core runs.

## Interpretation

The experiment reproduces the candidate's central quotient arithmetic under
its bounded fixed-word probe basis and falsifies its claim to a complete
persistence verdict. The missing Q7 responsibility does not invalidate the
formal 153 PUBLIC-image and 329 contractual-class counts; it shows that the
candidate's stated persistence classification fails to name information that
its own quotient already distinguishes. Separately, its audit result depends
on information absent from the purported evidence carrier.

This result selects no persistent representation. It supplies finite witnesses
for the corrected persistence ledger and reusable attacks for the next
independent candidate. Passing code is only a falsification instrument here;
it is not the architecture or the first milestone.
