# R0.1K executable finite-history experiment result

## Frozen inputs

| Artifact | Identity |
|---|---|
| Candidate | `HISTORY-SEED-R01K.md`, commit `c01da738b38f65868e5c8af17d4823d2bc3f07a7`, SHA-256 `2ae3ac8fda2a78a0b1cd4eef45a8a9d412dc6617b3fff098f4f348855c8eb678` |
| Fresh break | `POSTFREEZE-BREAK-R01K.md`, commit `709faefb494f1273d7e32b6b1460ce7ce7b8b37b`, SHA-256 `9c78c4830db263e5e200923fc51a36edbd1f7f37b70f90d420aae1e0e3ac983b` |
| Falsifier | `r01k_history_experiment.py`, commit `1ea9b8bdb95c71fa6ff84aa26ecb18bbe069d762`, SHA-256 `52b0e3da349fbe5476dd68276992ecaa5dfb04572d4a90d3e8f02f36f07fabee` |

The falsifier verifies both input digests before evaluating a check. It emits
one sorted, compact JSON value, contains no time or working-directory data in
that value, and exits one when any check fails. The input gate passed in every
reported run.

This program is a falsification instrument over frozen prose, constructed byte
strings, short histories, and finite arithmetic. It is not a subject-system
implementation. It does not make the candidate's incomplete occurrence
expansion complete, instantiate storage, execute a physical realization, or
prove that its finite checks exhaust permitted futures.

## Reproduction

The author's post-commit verification reported:

| Measure | Result |
|---|---:|
| Exit status | 1 |
| PASS | 4 |
| FAIL | 11 |
| UNKNOWN | 4 |
| Wall time | 0.04 s |
| Maximum resident set | 18,688 KiB |
| Whole-stdout SHA-256 | `c6bfaddfbc6bb18569def1f40679d82bfed8e267e28cd220fd92ae9f972721c4` |

An independent run from `/root/pareto`, rather than the artifact directory,
used:

    set -o pipefail
    /usr/bin/time -f 'MEASURE wall=%e user=%U sys=%S max_rss_kib=%M exit=%x' \
      python3 -B zero-ground-restart/r01k_history_experiment.py | sha256sum

and reported:

| Measure | Result |
|---|---:|
| Exit status | 1 |
| PASS / FAIL / UNKNOWN | 4 / 11 / 4 |
| Wall time | 0.04 s |
| User CPU | 0.03 s |
| System CPU | 0.00 s |
| Maximum resident set | 18,688 KiB |
| Whole-stdout SHA-256 | `c6bfaddfbc6bb18569def1f40679d82bfed8e267e28cd220fd92ae9f972721c4` |

The identical stdout hashes reproduce the exact JSON bytes for these two
runs. They do not turn static checks into subject execution, establish
completeness, or validate claims outside the program's explicit domain.

## Executed domain

The executable performs nineteen named checks. Its direct checks construct
small byte strings, histories, finite truth tables, and displayed-table data.
Its static checks locate and compare literal obligations in the two pinned
documents. In particular it constructs:

- the bound opaque byte string `UNBOUND` and the alleged unbound-marker bytes;
- the exact sequential MAY/MUST prefixes written by the candidate;
- the two admitted first OBSERVE answers for one identical `(history, request)`;
- the refused-EVOLVE then AUTHOR continuation;
- the five carrier values and one deletion result;
- the displayed action-label and router-table arithmetic; and
- literal progress, capture, depth, direction, viewer, and ledger obligations.

It does **not** enumerate a complete history language, all candidate
representations, all continuations, all viewer or authority states, all raw
payloads, all smaller tries, or a global quotient. The eleven failures are
finite counterexamples or frozen-text contradictions. The four passes have the
narrow scopes stated below.

## Eleven executable failures

The identifiers in this section are the executable's identifiers. They are not
a renumbering of the fresh break's F01-F11 sequence.

1. `F01 unbound_sentinel_collision` constructs two meanings—an unbound
   dependency and a dependency bound to opaque ASCII `UNBOUND`—whose purported
   length-prefixed encodings are both
   `00000007554e424f554e44`. There is zero encoded-byte difference. A permitted
   dependency-sensitive continuation can require `UNKNOWN:UNBOUND-DEPENDENCY`
   for the first and a decided result for the second. These are two intended
   seal/dependency states, not two literal §2 boundary histories supplied by
   the candidate; obtaining a history-pair theorem would first require exact
   boundary occurrences that bind those dependency inputs.

2. `F02 sequential_query_common_root` expands the written sequential MAY then
   MUST corpus. The MAY root is just `DECL:K/1`; the MUST root additionally
   contains the MAY request and answer. The roots therefore cannot both equal
   DECL, and the following written depths become `a=7`, `ab=6`, `b=7`, not the
   asserted `6/5/6`.

3. `F03 depth_six_envelope_vs_depth_seven` finds one request that the frozen
   text requires to be both `OUT-OF-ENVELOPE` under `depth.full=6` and `TRUE` at
   depth seven.

4. `F04 unique_n_observation_collision` holds the pre-request history and
   OBSERVE request fixed while the candidate admits both
   `ANS|audit|s0|OBSERVE|CHUNK|a` and
   `ANS|audit|s0|OBSERVE|CHUNK|b` as the first answer. Those bytes differ even
   though the same text calls `N(h,r)` unique. This is nondetermination, not a
   proof that either branch is the intended one.

5. `F05 direction_expansion_and_cut_authority` finds the smallest
   directionless abbreviation
   `APPLICATION-UNRESOLVED:capture-missing` and six CUT words whose required
   authority is not selected. Consequently the advertised exact expansion is
   not a function of the frozen bytes.

6. `F06 successful_request_answer_or_expiry_closure` checks the written
   ATTEMPT, EVOLVE, and TERMINATE fragments. Each has CUT-only success material
   but no closing ANS or operation expiry, contrary to the stated progress
   rule. Treating a CUT as an answer would add an unstated rule.

7. `F07 refused_evolve_phase_poisoning` appends a refused EVOLVE request and
   its `BUSY|observation` answer to an observation-open prefix, then asks
   AUTHOR. The raw first-match phase rule changes the answer from
   `BUSY:observation` to `BUSY:evolution` even though evolution was refused.

8. `F08 literal_retained_capture_payload` compares retained histories with
   different original chunk bytes. The exact answer
   `ANS|audit|s1|CAPTURE|CAPTURED|retained` contains neither the chunk nor the
   expiry bytes it is claimed to contain, so it cannot be an exact transport
   of both.

9. `F09 terminal_matrix_vs_terminal_refusal` holds a terminal-tail history and
   ATTEMPT request fixed. The router matrix names constructor label `TERMINAL`;
   the literal tail names exact result `TERMINAL-REFUSAL`. No expansion equates
   or distinguishes them. The frozen text therefore fails to determine one
   exact constructor result. This is an additional literal mapping
   inconsistency in the router/progress family, not proof of two necessarily
   different wire answers and not an added persisted category.

10. `F10 limited_viewer_observation_constructor` finds that limited OBSERVE is
    routed to `N`, while every declared chunk constructor exposes a forbidden
    token identity. No exact authorized, non-token-leaking result constructor
    is supplied.

11. `F11 p_k_and_ledger_materializability` checks the claim that the frozen
    bytes determine reproducible `P_K`, `Pairs(P_K)`, C entries, and E entries.
    The directionless abbreviation, missing CUT authorities, category-only
    mutants, and absent materialized E ledger block that construction. The
    smallest blocking member is the single directionless abbreviation from
    F05. The exact-`P_K` nonfunctionality makes the affirmative reproducibility
    claim fail. Absence of a completed E enumeration or global minimization run
    is separately UNKNOWN/unissued, not an additional collision by itself.

This list does not executable-reproduce every independently reported fresh
failure one-for-one. For example, the fresh report separately minimizes the
singleton pre-RECOVER depth error. Conversely, executable F09 makes explicit a
literal terminal-result conflict that belongs to an already failed
router/progress responsibility. The fresh report remains the authority for its
own eleven independent audit findings.

The exact crosswalk is:

| Fresh-break finding | Executable coverage |
|---|---|
| fresh F01 marker/content collision | executable F01 |
| fresh F02 nonfunctional occurrence expansion | executable F05; downstream executable F11 |
| fresh F03 unequal query roots | executable F02 |
| fresh F04 refused-EVOLVE phase poisoning | executable F07 |
| fresh F05 progress closure | executable F06; executable F09 is a related literal-mapping check |
| fresh F06 singleton pre-RECOVER depth | not executed |
| fresh F07 retained capture literal | executable F08 |
| fresh F08 unconstructible ledger | executable F11 |
| fresh F09 depth-seven conflict | executable F03 |
| fresh F10 nonunique `N(h,r)` | executable F04 |
| fresh F11 limited viewer route | executable F10 |

Executable F09 has no separate fresh-break ID. This non-isomorphism prevents
the matching count of eleven from being mistaken for complete reproduction.

## Four narrow passes

| ID | What passed | What did not follow |
|---|---|---|
| P01 | The five written abbreviation scripts contain `38/38/39/36/38` occurrences for `a/b/ab/n/u`. | They cannot be promoted to exact byte histories while expansion is nonfunctional. |
| P02 | The values `{+,+,+,-,?}` yield MAY=TRUE and MUST=FALSE; deleting `n` changes MUST to UNKNOWN. | Common-root execution, support adequacy, and global carrier completeness did not pass. |
| P03 | Eight action labels have 28 unordered pairs and adding `completed` contributes eight pairs. | Pair arithmetic does not materialize the promised collision ledger. |
| P04 | The displayed router rectangle has 12 populated predicate rows and the ten stated operation columns. | Occupancy does not prove unique selection, reachability, lifecycle correctness, or totality. |

These passes are arithmetic and transcription checks. None is credited as
information preservation, implementation conformance, persistence
minimality, or architecture feasibility.

## Four executable UNKNOWNs

- `U01 implementation_conformance`: there is no subject implementation, runner
  output, or subject trace.
- `U02 physical_and_unlike_realization_claims`: independent physical evidence
  is missing and zero materially unlike realizations are instantiated.
- `U03 global_support_minimality`: no complete candidate universe, all-smaller
  trie enumeration, or global C/D/E minimization run is supplied.
- `U04 tcb_and_external_context_closure`: a finite perturbation surface,
  dependency inventory, and independent oracle are absent.

Human cognition, authoring cost, storage durability, archive availability,
operational recovery, and future-domain completeness are likewise not measured
by this executable. Their absence is not zero complexity.

## Persistence interpretation

The decisive executable transport collision is F01. Deleting the binding or
using the candidate's marker merges two intended dependency states into
identical persisted seal bytes although a dependency-sensitive classification
can require decided versus UNKNOWN. Thus the responsibility to preserve
bound-versus-unbound status and opaque content is **MUST SURVIVE** under the
candidate's affirmative byte-closure and retained-verdict contract. Because
the candidate does not make those dependency inputs exact boundary
occurrences, F01 is not by itself a literal pair of §2 histories and is not
presented as a complete quotient theorem. It falsifies the claimed seal
transport. The responsibility does not imply a field, tag, record, object,
layer, or other representation.

The exact CAPTURE promise would also make original retained chunk and expiry
bytes logically **MUST SURVIVE** when a future is allowed to reproduce them.
F08 shows that the named literal answer does not discharge that responsibility.
The experiment therefore cannot grant an operational PASS to the candidate's
HISTORY retention claim.

Mechanically reproducible counts and tables would be **MAY REBUILD** only after
their source alphabet, expansion, authorities, and specification are complete
and identified. F05 and F11 prevent that premise here, so this is a conditional
possibility rather than an achieved R0.1K classification. No positive
**MAY FORGET** verdict is inferred merely because the executable did not test a
piece of information.

## Result

The frozen R0.1K candidate is finitely falsified. Its zero-byte-difference
dependency-state collision falsifies the affirmative canonical seal transport;
it would also violate
`encode(h1) = encode(h2) => h1 ≡ h2` once those dependency inputs were supplied
as exact histories, which the frozen candidate does not do. The other checks
expose common-root, depth, progress, routing, exact-capture, viewer, and ledger
contradictions or underdefinitions. Complexity has moved into an unstated
disjoint codec, exact occurrence expander, branch/root controller, lifecycle
correlator, projection engine, archive, minimizer, and TCB evidence process.

The experiment selects no representation and establishes no architecture. It
only supplies bounded witnesses and narrow controls for the persistence ledger
and total-system feasibility audit. Passing code would not have been the
architecture; failing code is not one either.
