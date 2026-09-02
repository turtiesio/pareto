# ARCHIVE REPLAY R0.1H

## Scope, integrity, and chronology

The quarantine gate opened only after the fresh R0.1H break was frozen at
commit `bf1c698`.  Before replay, the candidate was verified as:

```text
HISTORY-SEED-R01H.md
SHA-256 4954ed2a9612ea8a7e95041b689b549a1b9636e2d7457bf003d7d2c056958658
31,084 bytes
597 lines
```

The candidate was not edited.  Prior ZERO GROUND material was used only as an
attack vocabulary, principally `ARCHIVE-REPLAY.md`, the R0.1F/R0.1G archive
replays, `BLIND-ATTACK-PACK-R01F.md`, `FRESH-ATTACKS-B0.md`,
`FORMAL-AUDIT-B2.md`, `REALIZATION-AUDIT-R1.md`, and the earlier feasibility
audits.  No earlier representation, primitive, architecture, state schema, or
solution was imported into FBH-12/2/3.

Verdicts mean:

- **PASS**: the frozen abstract boundary model answers the attack without an
  extra choice, or it explicitly and coherently excludes the attacked
  capability while making no positive claim about it;
- **FAIL**: the frozen candidate has incompatible requirements or a concrete
  counterexample;
- **UNKNOWN**: a semantic choice or unexecuted realization/evidence attack is
  still required.

A scope PASS is not a capability pass and is not empirical evidence.

## Fresh-break baseline

The following defects were already found without archive access and are not
new archive discoveries:

1. After an interrupted `O0/O1`, `AI/AN/RI/RN/D`, or `E`, the erased hidden
   selector can leave two required residuals behind one exact observable
   prefix, contradicting the claim that `O(prefix)`, `P(prefix)`, and
   `G(prefix)` cover every legal prefix.
2. The common scheduler domain for adaptive controllers is not defined when
   the compared runs have different crossing shapes.
3. It is unspecified whether the legal client controller observes the capture
   peer's `A` crossings.
4. `Must` lacks vacuity/inapplicability rules and a carrier for hidden branches
   that trace-set deduplication erases.
5. A scheduled crash after `STOPPED` may or may not append `DOWN,READY` to the
   complete trace.
6. The claimed canonical witness order lacks complete controller, scheduler,
   crossing, integer, and length-prefix encodings.
7. Padded selector prediction 9 omits `T`'s second in-flight gap.  Exhaustive
   per-gap padding is `3,910,242`, not `3,838,493`.
8. Consequently the total adaptive oracle, same-coordinate crash theorem,
   several classification claims, and fresh-implementer cognition result are
   conditional, failed, or unknown as recorded by the fresh break.

## Archive attack replay

| Prior attack family | Smallest R0.1H witness or probe | Verdict | Freshness and disposition |
|---|---|---|---|
| **Malformed framing** | Zero bytes, `"\n"`, or `"QUERY"` without LF instead of exact `"QUERY\n"` | **PASS (scope only)** | Archive check, no new defect. Sections 1.1, 1.2, and 10 explicitly restrict legal input to twelve nonempty LF-terminated frames and typed FIN. These probes receive `UNSUPPORTED`, not invented boundary replies. Atomic transport/parser realization remains untested. |
| **Universal and empty input** | Empty request versus typed `C:FIN` | **PASS (scope only)** | Archive check, no new defect. Empty frames are explicitly unsupported; FIN is typed and completes with exactly `STOPPED`. No universal byte-string claim is made. This is not a pass for empty-message behavior. |
| **Meta-classification of arbitrary malformed descriptions** | Ask for `UNSUPPORTED(reason)` on an object with two simultaneous out-of-domain causes | **UNKNOWN** | Already fresh in substance. The seed gives no description grammar or precedence for deterministic reason selection, so “total as a classifier” is not executable uniquely. |
| **Atomic completion / output-commit cut** | Crash between `C:FIN` and `R:STOPPED\n` | **PASS (abstract model)** | The exact trace `FIN,DOWN,READY,STOPPED` is frozen and no ordinary reply is invented. Partial frames and crashes inside a crossing are coherently excluded. Physical delivery, durable ordering, and parser behavior remain `UNKNOWN`. |
| **Post-terminal completion** | `H()`; `FIN`; `STOPPED`; crash in the counted final gap | **UNKNOWN** | Already fresh. The candidate does not choose between terminal trace truncation and appending `DOWN,READY`. |
| **Author crash/retry and selector collision** | `H()`; `C:"AUTHOR ID\n"`; crash before reply; `DOWN,READY`; retry `AI` | **FAIL** | Already fresh primary break. Old requires `OK AUTHOR ID`; new requires `ERR ACTIVE`, although literal completed-prefix `P` is `EMPTY` in both observable prefixes. The two-trace may example is operationally intelligible only after adding selected residual/phase to semantic oracle state. |
| **Observation and evolution recovery identity** | Interrupted `O0`, then `X`; or interrupted `E`, then retry `E` | **FAIL** | Already fresh. The required new branches expose `O=0` or `ENGINE E1 ALREADY`, while literal completed-prefix functions still return `U` or `E0`. |
| **Selector completeness and evidence binding** | Force both branches of the interrupted `AI` witness and associate each `F:SELECT` manifest entry with its exact trace | **UNKNOWN** | Archive evidence attack, no new semantic failure. Section 3.3 itself says an implementation without a forceable selector cannot establish may-set completeness. No launcher, manifest, selector, subject binding, or replay evidence exists. |
| **Nondeterministic may/must correlation** | Interrupted `AI`, recover, then FIN so unlike hidden residuals can deduplicate to one public trace | **UNKNOWN** | Already fresh. `May` correctly asks for sets, but `Must` cannot recover branch-residual propositions from the deduplicated trace set and has no vacuity rule on no-crash schedules. One sampled branch is explicitly insufficient. |
| **Adaptive scheduler common domain** | Compare `H()` with `H(AI)`; controller sends `X`, then sends `T` only when `P=EMPTY`; target “after the second request's A” | **UNKNOWN** | Already fresh. That gap exists on one run and not the other; the seed does not define a common scheduler policy for this case. |
| **Action crash before/after capture** | From `H(O1,AI)`, crash before first `A` and retry, or crash after first `A` before `R` and retry | **PASS (abstract crossing model)** | Already fresh PASS. Exact traces contain respectively one and two `A` crossings; `A` precedes an unfailed `R`. No receiver-effect or exactly-once inference follows. |
| **Controller visibility of action capture** | Same action, crash after `A` before `R`; choose retry based on whether the controller saw `A` | **UNKNOWN** | Already fresh. `A` is visible to an independent capture peer, but “entire observed suffix” does not say whether its observations are delivered to the client controller. |
| **Exactly-once external effect / receiver status** | Sever everything beyond the capture boundary after `A` and ask for application effect, durable acceptance, or dedup status | **PASS (scope only)** | Archive gate closes coherently: Sections 3.2 and 10 expressly make all downstream effects, storage, deduplication, and exactly-once behavior unsupported. The physical capture adapter itself remains `UNKNOWN`, not passed. |
| **Clean stale identity/evolution** | `H()` versus `H(E)`; future `K`; or issue `E` again | **PASS (failure-free model)** | Archive stale-identity probe is discharged at clean cuts: `K`, `X`, and `T` expose `E0/E1`, while repeated `E` distinguishes first evolution from already evolved. Interrupted evolution remains the already-fresh FAIL above. |
| **Self-description / external spec selector** | Recover identical candidate bytes under two different external transition tables, then issue `K` or `E` | **UNKNOWN** | Archive-only TCB probe. The semantic seed fixes one specification, but proposed generated/replay realizations and their specification selection are unbuilt. Correct bundle selection, availability, and identity cannot be inferred from clean `K` behavior. |
| **Rejection provenance and lineage** | `H(AI)` versus `H(AI,RI)` (both current `P=ID`), then `X` | **PASS (scope only)** | Archive provenance attack is gated. R0.1H exposes current `O/P/G/V`, `ACTIVE`, and `EMPTY`, but promises no prior rejection register, source offset, replacement ancestry, author identity, or lineage. The histories are intentionally continuation-equivalent under the repaired model. |
| **Hidden path/cache state** | `H()` versus `H(RI)` reaches the same clean coordinate; apply all legal futures, beginning with `X` | **UNKNOWN empirically** | The model predicts a merge and exposes no last-error state. No implementation exists to erase caches, run alternate paths, or show that process/runtime state cannot affect a legal future. Behavioral irrelevance would not prove physical absence. |
| **Malformed/counterfeit/replayed persistent-image scope** | Minimal insertion, deletion, substitution, counterfeit identical image, or rollback of a future J/Q image; recover then `X/K` | **PASS (scope only)** | Section 10 explicitly excludes corruption, rollback, backup restore, and arbitrary recovery images. That closes the semantic attack without proving robustness. |
| **Realization import/recovery validation** | Present the same minimal invalid/replayed images to implemented J and Q | **UNKNOWN** | J/Q have no frozen image grammar or implementation, so import validation, freshness, and physical recovery have not been tested. |
| **Externalized capture peer** | From `H(O1,AI)`, sever the capture peer and issue `T` | **UNKNOWN** | Archive EXTERNALIZE attack, not freshly executed. `A` and `OK ATTEMPTED` make the peer a named responsibility; removing it prevents conforming completion. No peer availability, recovery, authenticity, or capture evidence exists. |
| **Externalized continuation token** | Lose or substitute the client token, then issue any next request | **PASS as a nonconformance classification** | The seed explicitly says authentication/authority are outside scope and the token candidate is not presently conforming. It receives no storage saving or realization credit. No token experiment exists. |
| **Exact-history interpreter attack on the bounded quotient** | `H()` versus `H(RI)`; hypothetically install equality-to-`Encode(H())`, then query | **PASS (scope only)** | The install is explicitly outside the twelve-message language, so it cannot refute this bounded quotient. |
| **Exact-history interpreter theorem as written** | Instantiate the same pair, requiring literal equality to `Encode(H())` | **UNKNOWN** | Already fresh. The separate theorem does not explicitly require an injective `Encode`, so its literal result is not fixed. |
| **One-message separator length** | `H()` versus `H(O0)`; future `X` | **PASS** | Zero messages expose only coordinate-independent FIN/STOP, and `X` separates in one message. |
| **Canonical witness serialization** | Serialize the same pair/controller/scheduler independently in two conforming tools | **FAIL** | Already fresh. The seed omits enough byte and adaptive-tree grammar that the tools may lawfully choose different canonical bytes. |
| **Clean quotient arithmetic** | Fold all 157 words of length `0..2`; use `X` on unequal coordinates | **PASS** | Independently fresh-verified: fourteen cut classes, multiset `{59,17,17,16,16,16,2,2,2,2,2,2,2,2}`, 2,351 same-class pairs, and 9,895 unequal pairs. This is a clean-cut model result, not a persistence layout. |
| **Same-class forgettability and path independence** | Smallest intended merge `H()` versus `H(RI)`; compare every depth-three adaptive/crash future | **UNKNOWN** | Already fresh. It is conditionally valid after selected-residual repair and common scheduler semantics, but not a theorem of the literal inconsistent oracle. No hidden-state realization test exists. |
| **MUST/MAY classification of total between-crossing state** | Delete pending selected residual or pending FIN after its crossing, then recover | **UNKNOWN** | Fresh mathematics already notes that the seed predicts only the clean fourteen-way cut coordinate. Pending completion, selected old/new residual, and FIN responsibility are named but their full quotient and deletion witnesses are not enumerated. |
| **DERIVE / RECOMPUTE classifications** | Delete exact reply/action bytes or a proposed label; cold-start and rebuild solely from the named survivor plus seed | **UNKNOWN empirically** | At a clean request boundary the byte table proves model-level derivability from coordinate, request, and specification. No target bytes were deleted, no J/Q machine was cold-started, and recovery additionally requires phase/selected residual. Reconstruction machinery and cost remain charged. |
| **Linear schedule arithmetic** | For `[T]`, count five nominal crossings, six gaps, and no-crash | **PASS** | The per-word formula `2n+t+4`, aggregate 18,965, and `157*18,965=2,977,505` are exact syntactic case counts, not executions. |
| **Padded selector arithmetic** | One-message word `[T]`: both `C-to-A` and `A-to-R` are in-flight gaps | **FAIL** | Already fresh. Per-gap padding needs nine slots for `[T]`, while the frozen `3n+t+4` formula gives eight. Across the corpus the exhaustive padded result is 3,910,242, shortfall 71,749. |
| **Unlike physical realization** | Implement J and Q, cut the first physically unlike persistence/completion boundary, recover, then `X/K/T` | **UNKNOWN** | Archive REALIZE gate remains open. J, Q, and H are sketches/obligations only. No process build, cold recovery, media, controller, power-loss, or independent physical-family evidence exists. |
| **Evidence-versus-behavior non-inference** | Ask whether the mathematical traces prove physical storage, security, or receiver effects | **PASS** | The seed correctly reports no implementation or empirical result and prediction 11 forbids those inferences. There is no false physical evidence claim. |
| **Evidence dossier and subject binding** | Ask for build identity, exact trial-to-subject association, raw capture records, selector branches, and replay | **UNKNOWN** | No evidence dossier exists to pass REALIZE, TCB, or selector-completeness gates. |
| **TCB mutation** | Perturb parser, serializer, capture peer, fault hook, selector, canonicalizer, generated table/spec, runtime, OS, filesystem, compiler, and build inputs one at a time | **UNKNOWN** | Archive TCB attack adds no new semantic counterexample. Section 5.2 lists these obligations, but nothing has been built or perturbed. Hashes and prose do not prove independence or correct attestation. |
| **Independent specification reproducibility** | Give two fresh implementers only the seed and compare selected residual state, adaptive schedules, `Must`, post-terminal traces, and canonical bytes | **FAIL** | Already fresh. The text admits multiple lawful choices, so one exact oracle/canonicalizer cannot be reproduced without invention. |
| **Human cognition measurement** | Measure implementer time, recall, errors, and reconciliation burden | **UNKNOWN** | No participant protocol or data exists. |
| **Privacy, authority, concurrency, clocks, resources** | Admit the smallest excluded variation and repeat a query/action | **PASS (scope only)** | Section 10 explicitly excludes these dimensions and makes no positive claims. They are unsupported capabilities, not zero-cost or tested successes. Any future admission requires a new experiment. |

## Required attack battery after replay

| Attack | Verdict after fresh break plus archive replay |
|---|---|
| DELETE | **UNKNOWN** — no implementation was mutated; clean-coordinate redundancy is conditional model reasoning. |
| MERGE | **UNKNOWN** — `X` rejects cross-coordinate merges at clean cuts, but same-coordinate adaptive/crash congruence is not unconditionally defined and no realization labels were forced together. |
| DERIVE | **UNKNOWN** — clean output bytes are mathematically derivable; no stored target was removed and cold-rebuilt. |
| RECOMPUTE | **UNKNOWN** — J/Q recovery and its machinery/cost do not exist. |
| COLLIDE | **FAIL** — exact observable prefixes after interrupted observation/author/evolution collide while required selected residuals differ. This is already fresh. |
| FUTURE | **UNKNOWN** — the repaired finite machine is plausible, but scheduler, controller-observation, Must, terminal, and literal-residual defects prevent one exact exhaustive oracle. |
| EXTERNALIZE | **UNKNOWN** — capture peer, selector, specification/bundle, and token dependencies were not severed in an experiment. |
| REALIZE | **UNKNOWN** — no independent J, Q, or H build exists; no physical result exists. |
| COGNITION | **FAIL** — the seed alone does not determine one exact implementation. This is already fresh. |
| TCB | **UNKNOWN** — the inventory is a plan, not a perturbation dossier. |

## Archive-only result and verdict impact

No genuinely new archive-only `FAIL` or smaller R0.1H counterexample was found.
The archive independently re-exposes the fresh selected-residual, adaptive,
Must, terminal, minimization, and padded-count defects.  Its additional value
is to prevent scoped exclusions from being credited as capabilities and to
keep these unexecuted dimensions explicit:

- selector completeness and artifact/trace association;
- hidden alternate-path and cache state;
- capture-peer availability and authenticity;
- recovery-image validation, rollback, and external specification selection;
- DELETE/DERIVE/RECOMPUTE mutation evidence;
- TCB perturbation and independent human reproduction; and
- unlike software, physical-media, and real power-loss realization.

The clean failure-free core survives: exact twelve-message framing, 157 cuts,
the fourteen-class arithmetic, one-message `X` separation, abstract action
crossing counts, and linear schedule arithmetic.  The total candidate remains
failed/non-uniquely executable for the already-fresh reasons.  Archive replay
does not turn any proposed family, unsupported capability, or mathematical
classification into implementation or physical evidence.

No file other than this replay report was created or changed, and no commit was
made.
