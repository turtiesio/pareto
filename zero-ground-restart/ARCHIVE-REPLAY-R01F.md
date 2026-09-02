Verified CF-1 SHA-256:

`f9fce4d2f0fd43594553f06ab05403d90b088b3f2fd50b7c3f883be7f7b03445`

The top-line R0.1F verdict remains failed/non-uniquely executable. Archive replay adds one independent failure to the fresh audit’s six findings.

| Old attack family | CF-1 disposition |
|---|---|
| Malformed streams, truncation, completion boundaries | **Already found:** POSTFREEZE defect 1. `ε`, short `00 01`, and excess `00 00 00` require an undeclared record boundary despite §§2,4,8.2. |
| Output commit/delivery races | **Explicitly gated** for ordinary responses: crossings are indivisible under §§2,5,12.3. Physical partial delivery is outside §24. The `A0/AE` special case is **already failing** under defects 2–3. |
| Action lifecycle, deduplication, replay/status | **Already found** for the §10/§12 contradictions. Ordinary non-deduplicating receiver impossibility is **explicitly gated** by §10.4. |
| Recovery-machine faults and crash count | **Already found:** defect 4; “crash during recovery machinery” conflicts with the one-crash limit in §§11,13–14. |
| Successful-request provenance and rejection ancestry | **Already found:** defect 5. Older-than-latest ancestry is explicitly unavailable under §§8.3–8.4. |
| DELETE/DERIVE and over-preservation | **Newly failing.** Section 18 classifies detailed `length` and `offset` as `MUST SURVIVE`, although both reconstruct exactly from retained rule/raw. Smallest well-framed witness: reject `00 00`, immediate detailed response `00 03 83 04 02`; future EXPLAIN `00 01 40` returns `00 07 95 04 02 00 02 00 00`. Removing stored length/offset changes no future because length is `u16be(2)` and offset recomputes as `02`. This was independently corroborated by the executable falsifier. |
| Exact wire bytes, arbitrary invalid bytes, validation precedence | **Discharged by executable checks:** CT lengths `172/182`, UPDATE frames `177/187`, `P=43`, all representative rule/offset branches, symbolic partition of all `U`, detailed replacement shapes, and one-byte CT mutation rejection passed. |
| Presence/value/order/association/lifecycle/query/nonce distinctions | **Discharged for atomic no-crash behavior:** all twelve unambiguous §15 seeds, negative dropped-`o`/version collisions, tuple congruence, and retired/exhausted-action deletions passed. Full power results remain **UNKNOWN** because its oracle is contradictory. |
| Adaptive policies and nondeterministic correlation | Complete ordered transcript sets in §§13–14 discharge the marginal-correlation attack; the executable checker proved representative atomic congruence. Beyond the three-request/one-crash horizon is **explicitly unsupported** by §§13,23–24. |
| Path-dependent shortest histories | Literal latest-IDENTIFY state is **already found** as defect 6. Arbitrary prior-history readers are **gated** by §§9,13,23. Hidden implementation state remains **UNKNOWN** without builds, despite §§14.2 and 20 requiring all pre-cut histories. |
| Witness minimization | **UNKNOWN:** §15 does not specify serialization/orientation of the history pair, outputs, or nondeterministic sets for `total raw bytes` and lexical ordering, so a globally first witness is not executable uniquely. |
| Authoring and evolution | Exact CREATE, CT1/CT2 UPDATE, RETIRE, IDENTIFY, QUERY2 and downgrade behavior are **executable-check passes**. Arbitrary authored bytes, interpreters, migrations, versions, undo, or historical reinterpretation are **unsupported** under §§7,23–24. |
| Queries/navigation/selectors | Fixed OBSERVE/QUERY/QUERY2/EXPLAIN/IDENTIFY behavior passed. Discovery, search, aggregation, and general selectors are **unsupported** by §§4,7,24. |
| Exact targets versus hashes | Semantic target selection is **discharged**: exact CT bytes are compared; §17.3 forbids hash-only equality. Section 19’s stale “latest IDENTIFY” identity is **already failing**. Exact binding of evidence to either physical build is **UNKNOWN** because no build dossiers exist. |
| Cleanup/reset and hidden external-service state | **UNKNOWN.** Sections 13 and 20 would reject future-visible hidden state, while §§18,21–22 charge externalized receiver/interpreter/transport state, but no service or reset experiment exists. |
| Counterfeit, malformed, replayed recovery images | **Already classified/gated** in POSTFREEZE: §§12.2–12.4 admit only crash-derived pre/post states; arbitrary corruption/rollback is TCB failure under §§18,22. Build-specific import validation remains **UNKNOWN**. |
| Clocks, deadlines, timeout races | Real time, expiry, scheduler state, and resource deadlines are **unsupported** by §§5,10,13,24. The exact timeout-marker schedule passed; an actual timeout source remains **UNKNOWN**. |
| Processes, providers, EOF, launch, cleanup phases | **Unsupported** as semantic inputs by §§5,11,24. Any required transport/driver realization is charged in §§21–22 but has no evidence. |
| Privacy, authority, erasure, randomness, concurrency, ambient modes | **Explicitly unsupported** by §§1,5,11,13,23–24. |
| TCB, bootstrap, offline dependencies, cognition | **UNKNOWN.** Sections 18 and 21–22 require corruption/removal, cold-rebuild, operations, and human-procedure evidence, but provide no implementation or measurements. |
| Unlike physical realization | **UNKNOWN:** §20 prescribes two families, but supplies neither build nor physical fault dossier. Software or logical diversity cannot substitute. |
| Enumeration/resources | Mathematical finiteness was **discharged**; physical materialization of the 600-plus-digit `U`, dense table, and residual DAG remains **UNKNOWN**. |
| Evidence/gate claims | Exact protocol bytes have executable checks. R0.1-style canonical evidence envelopes are not claimed and are **gated** by §5/§24; the mandatory §18–§22 probes and dossiers themselves remain **UNKNOWN** because no evidence exists. |

Material verdict change: none at the top level—R0.1F was already rejected by the fresh oracle-blocking defects. The archive’s DERIVE family adds a distinct seventh defect in the preservation ledger; minimization, full-power quotient, dense/DAG equality, physical realization, TCB, and dossier claims remain unearned `UNKNOWN`s.

No files were modified.
