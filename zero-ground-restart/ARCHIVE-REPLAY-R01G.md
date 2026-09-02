Verified H11 SHA-256:

`9fcf79f7544e3fe7d11f0830e224635758921f199e4478bb4180ada991629008`

No old-taxonomy-only attack produced a new exact H11 counterexample.

| Attack family | H11 disposition |
|---|---|
| Completion, EOF, framing | **Already fresh:** `30 00` is atomically distinct from `30;00`, but the claimed “empty submission” has no legal history. Crashes around terminal `C↓` remain unspecified under §§2–3. |
| Output commit races | **Executable-discharge candidate:** §4.1 specifies durability-before-success, atomic replies, discarded interrupted replies, and no automatic replay. Actual transport completion and durable ordering remain **UNKNOWN physical evidence**. |
| Crash nondeterminism/correlation | **Already fresh:** after `C!10,K!CRASH,K!RESTART,R!88,C!30`, byte-old permits `R!e0 03` while byte-new permits `R!e0 04`; §5 never states may-trace-set equality, so `~` is not uniquely defined. |
| Action externalization | Logical before-`D`, after-`D`, and after-`R` traces are an **executable-discharge candidate**. Receiver application, status, deduplication, and exactly-once effect are **explicitly unsupported** by §4.1; the physical attempt adapter remains **UNKNOWN**. |
| Hidden path/cache/latest-response state | **Already fresh:** §§2.2–2.3 and 4.9 establish behavioral irrelevance, not physical absence or fresh recomputation. Alternate-history hidden-state checks remain **UNKNOWN** without builds. |
| Identity and exact targets | `60` injectively exposes exact `D0/D1`, not hashes, and is an **executable-discharge candidate**. Correct caching is observationally indistinguishable from fresh generation. Full seed/build/run evidence binding is **UNKNOWN** because H11 supplies no realization manifest or evidence envelope. |
| Authoring/query breadth | Fixed I/N selection, retirement, query, coded rejection, and revision behavior are **executable-discharge candidates**. **Already fresh:** `10/11` carry no authored table bytes and are behaviorally equivalent to selecting frozen built-ins. Arbitrary interpreters, inputs, queries, and later versions are gated by §§1,4,5.3. |
| Persisted corruption/replay | Random corruption, hybrid bytes, lost acknowledged writes, reordering, coherent rollback, and second/recovery crashes are **explicitly unsupported** under §§1 and 7. Reachable old/new L/S images are finite check candidates; real-byte durability and cold recovery remain **UNKNOWN**. |
| Reset/cleanup/external services | Reset is not in the eleven-message alphabet. §9’s cache erasure and externalization probes are prescribed but unexecuted; future-visible process, service, or cleanup state is **UNKNOWN physical evidence**. |
| Clocks/processes/ambient state | Clocks, concurrency, multiple clients, and partitions are **explicitly unsupported** by §1. Actual absence of environmental, process, timer, or background-retry dependencies remains **UNKNOWN**. |
| Common domains and horizon | The total eleven-message domain, 133 cuts, and bounded adaptive structure are **executable-discharge candidates**. Inputs outside `M`, more than five total occurrences, and extra crashes are explicitly gated. Successful query/action forgettability outside the two-message cut corpus is **already fresh as conditional**, not established physical absence. |
| Quotient versus representation | Independent in-memory enumeration confirmed 133 histories, 14 cut classes, 18 full states, and injectivity of packed, representative, and probe encodings. **Already fresh:** the printed class multiset, two minimality claims, tie-breaking order, and exhaustive schedule count are false or underspecified. The quotient result remains conditional on set-valued crash semantics. |
| DELETE/MERGE/DERIVE claims | Finite logical searches are **executable-discharge candidates**; H11 correctly avoids componentwise `MUST STORE`. Full deletion, collision, alternate-path, and TCB runs remain **UNKNOWN** because §9 is a program, not evidence. |
| Recovery images/import | L’s contiguous-prefix rule and S’s `00..11` range are logical check candidates. Counterfeit, arbitrary valid rollback, and malformed-image product behavior are gated; implementation-specific import and corruption handling remain **UNKNOWN**. |
| TCB/bootstrap/cognition | **UNKNOWN:** §9 inventories responsibilities but supplies no builds, bootstrap/toolchain record, mutation results, participant protocol, or cognition measurements. |
| Unlike realization/oracle independence | Logical L/S old/new quotient correspondence is an executable candidate. Independently authored builds, real power faults, complete trace-set equality, physical byte costs, and independent-oracle evidence are expressly absent under §§8 and 11. |
| Evidence/gate claims | Ordered `R/D` traces are exact semantic observations, but no canonical evidence stream, trial identity, source/build association, or replay pack is supplied. The erroneous schedule total is **already fresh**; empirical evidence completeness remains **UNKNOWN**. |
| Privacy, authority, erasure, randomness, exact-history readers | **Explicitly gated/unsupported** by §§1 and 5.3. The characteristic-interpreter theorem is **already fresh** as conditional and non-executable within `M`. |

Verdict impact: unchanged. H11 retains a coherent deterministic core and plausible logical L/S candidates, but remains internally unclean due to the fresh contradictions, false predictions, minimization defects, and missing nondeterministic-equivalence rule. The archive adds no new exact-history failure; it principally keeps physical realization, hidden-state, evidence-binding, TCB, and cognition claims at `UNKNOWN`.

No files were modified.
