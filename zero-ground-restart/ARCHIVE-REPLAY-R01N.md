# ZERO GROUND R0.1N — post-freeze archive replay

Status: quarantined replay of prior counterexample shapes; no old solution, representation, or ontology is adopted  
Candidate: `R01N/FT-FE`  
Overall result: **FIRST MILESTONE FAIL / NOT ACHIEVED**

## 0. Authority, chronology, and integrity gates

The four current artifacts form this verified linear Git ancestry:

```text
candidate -> audit script -> post-freeze break -> experiment result
```

`git merge-base --is-ancestor` returned zero for each adjacent arrow. Scoped `git log -1` gave the following commits and author timestamps:

| chronological artifact | commit | author time UTC | required SHA-256 | observed SHA-256 |
|---|---|---|---|---|
| `HISTORY-SEED-R01N.md` | `0ba35affe0a587d0d80ca4ba28a26602d8e269ba` | `2026-09-02T11:28:47+00:00` | `10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7` | same |
| `r01n_history_audit.py` | `807b0fd243f645fc8c2a11a51cdad072da9b9148` | `2026-09-02T11:41:18+00:00` | `afb21585f1b9523f16f6fb4d3d647eadac5c461d30de8cda92f19ecd40f18f49` | same |
| `POSTFREEZE-BREAK-R01N.md` | `cb535b869d543e1219381867b515889a5a502423` | `2026-09-02T11:45:18+00:00` | `f00a9841cc9baaa349ff9300f85a8b6a68293e91af560452cf7c2d463bd9773a` | same |
| `EXPERIMENT-RESULT-R01N.md` | `12fad32b34ff1c4a5ca67f031db4ad626ff9cb91` | `2026-09-02T11:50:24+00:00` | `c02d41b50c2a700d93ccfaf4f0807c18ac6e2897296763db24a566e5f1df4c41` | same |

This is byte and repository chronology, not proof of private cognition or authorship independence. In particular, the audit script's commit precedes the post-freeze report's commit; the break's own access attestation remains the evidence about what its breaker read.

I reran the committed audit script from `/root/pareto`:

```text
command: /usr/bin/python3 /root/pareto/zero-ground-restart/r01n_history_audit.py
exit: 1 (intentional because FAIL results exist)
stdout: 7,254 bytes, 1 line
stdout SHA-256: 536fe90528116883e0d32dc5f1ca90f392794b7393b6e5cd0b09c249afc1ecb9
stderr: 0 bytes
stderr SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
summary: 6 PASS / 3 FAIL / 11 UNKNOWN
verdict: FIRST MILESTONE FAIL / NOT ACHIEVED
```

These values exactly match the committed result. This rerun is reproducibility evidence for that script, not an independent implementation or physical realization.

## 1. Quarantined archive inputs

I first obtained a filename inventory of `zero-ground-restart`, then closed discovery. I read the contents of exactly these nine prior artifacts and verified each hash:

| prior artifact read | SHA-256 | use in this replay |
|---|---|---|
| `ARCHIVE-REPLAY.md` | `4ddd2d7641e4689720b783b1e38e4e467539bc614582f708b71668f81cf72309` | base transformation/evidence attack index |
| `BLIND-ATTACK-PACK-R01I.md` | `0b5a7c3f91af525559570be8e77a69a83adc9b980b97b0727877caca1974d24b` | B00–B38 and composite black-box attack shapes |
| `ARCHIVE-REPLAY-R01I.md` | `921b7589a0694942531dc078ffb48d03436e78c0f32717b79e8516373b8af9cf` | consolidated viewer, policy, recovery, evolution, and evidence pressures |
| `RECOVERY-QUOTIENT-R01H.md` | `78785ae88d0b8796d69ccf5060abe524434a8626389f757cc1b70edb6687a149` | snapshot/cut, action-occurrence, terminal, and remaining-capability shapes |
| `LITERAL-SPEC-AUDIT-R01J.md` | `370642e1ea148c4702a373a3e33347d3987c160db1fe41dc5e9364cb4ead3956` | total grammar, progress, evidence self-credit, and minimization attacks |
| `POSTFREEZE-BREAK-R01K.md` | `9c78c4830db263e5e200923fc51a36edbd1f7f37b70f90d420aae1e0e3ac983b` | delimiter, common-root, phase, progress, viewer, and retained-evidence shapes |
| `ARCHIVE-REPLAY-R01L.md` | `217efe1524c1ffab09e8b7a2b2e6412833a8562e64abd444e279fc9e0a0ed64a` | latest cumulative attack taxonomy and scope discipline |
| `REALIZATION-AUDIT-R1.md` | `34cec7d02f0224f095ccfb05ae75b206f80b5d66156c4a3219690ab37855c656` | physical completion, false attestation, corruption, recovery, and unlike-runtime cautions |
| `TRANSITION-WIRE-R1.md` | `3dad74ed3048289a1afff3129bd6f06f8d8c3623e2c406a177b3d3a6e5ba108b` | late/private wire-specification externalization shape |

No prior seed, representation implementation, proposed repair, or other prior file content was read. Old results are not R01N evidence. Only attack forms were translated into R01N's frozen boundary language. The broad initial filename inventory exposed names, not file contents.

## 2. Current baseline before archive replay

Archive findings are measured against both frozen current reports, not against a retrospectively altered candidate.

### 2.1 Post-freeze B1–B7

| current ID | existing R01N result |
|---|---|
| B1 | Typed requests/responses have no exact `(direction,payload)` wire mapping, capture order, or snapshot-resolution order. This is a missing required capability. |
| B2 | E01 lacks opcodes, binary grammar, `mode`, and several edge semantics; required futures cannot be executed exhaustively. |
| B3 | The Python future suite is exact as a listed finite set but does not enumerate C01: no encoded `RUN`, `SLICE`, `COMPARE`, capture, or all bounded append symbols. |
| B4 | Mathematical P01 framing is total in an ideal unbounded model; executable/full-system resource boundaries were left UNKNOWN. |
| B5 | Malformed forms reject, but canonical `0000` becomes canonical `0100` after one bit and silently changes history. Raw retrieval alone does not detect corruption. |
| B6 | Counts/offsets/indexes rebuild; E01 traces, installed policy/configuration, evidence associations, and physical recovery do not yet have an exact reconstruction basis. |
| B7 | The in-file fresh corpus is reproducible but not independently precommitted; hidden/fresh independence remains bounded evidence. |

### 2.2 Committed audit F01–F03 and bounded positives

The later committed audit adds three current failures:

- **F01, snapshot/harness correspondence:** on `()` and `((0,empty),)`, the harness `LENGTH` gives `(0,1)`, but no fixed snapshot in `{0,1,2}` gives that pair before request capture. This is not a P01 collision.
- **F02, external extent:** `encode(one)||encode(one)==encode(two)` for the empty-payload occurrence. P01 frames are delimited, but the history word is not delimited from a following history or material without an external byte-string extent/EOF.
- **F03, semantic substitution:** the direct Python projections are not encoded E01 programs and do not execute the declared `RUN`/view/interpretation/action/explanation interface.

The six current PASS results remain narrow: artifact integrity, deterministic reproduction, bounded round-trip/injectivity, selected ULEB boundaries, a bounded storage-only alternative, and a 13-history witness-union upper bound. None is architecture or total-system dominance.

## 3. Minimization and verdict discipline

For fixed finite history pairs, this replay minimizes lexicographically by:

```text
Mfixed = (
  total initial boundary occurrences,
  differing occurrences,
  common future requests,
  total payload bytes,
  viewers,
  realizations,
  nondeterministic choices,
  varied external influences,
  lexical histories and future
)
```

For a representation mutation, equality of mutated representations is required; a missing definition, timeout, resource impossibility, valid-to-valid corruption, and unsupported physical fact are not mislabeled as pairwise collisions.

For literal physical capacity, the parametric metric is:

```text
Mphysical(R) = (CROSS request count per history, payload length,
                continuation requests, lexical payload pair)
```

where `R` is a fixed finite realization and `Q_R` is the number of total-system states it can distinguish durably at restart. Define:

```text
m_R = min { m >= 0 : 2 * 256^m > Q_R }.
```

There are more one-occurrence histories `(d,p)` with `|p|=m_R` than durable states, so two collide or at least one valid `CROSS` is not accepted. A common `AT(snapshot,0)` distinguishes any two such occurrences. The numeric `m_R` is unavailable until a realization and capacity are named; the family is nevertheless a proof for every finite `Q_R`, not an empirical UNKNOWN.

## 4. Literal totality versus physical realizability

This replay sharpens B4 and keeps four claims separate.

### 4.1 P01 mathematical encoder

For every mathematical finite history, each finite payload has a finite natural length, shortest ULEB exists, and inductive frame parsing is unique when the complete byte-string extent is supplied. No archive attack produces two different histories with equal mathematical P01 bytes. This remains a conditional mathematical PASS, not a physical claim.

### 4.2 Bounded Python falsifier

The reference program is expressly bounded. It round-trips the frozen 585 and 157 histories and selected ULEB tiers; the committed audit reproduces those results. It does not advertise or establish execution over all mathematical finite histories, so no unbounded implementation PASS is credited.

### 4.3 Literal C01 physical realization

C01 admits every finite payload and every finite history. `CROSS(d,p)` “appends exactly one occurrence”; unlike `RUN`, it has no `REJECTED`, `EXHAUSTED`, or resource-failure result. Any fixed physical realization has finitely many distinguishable total-system restart states. The `Q_R+1`/one-CROSS construction above forces a collision or refusal, while byte-exact `AT` distinguishes the histories.

Therefore:

```text
LITERAL ALL-DOMAIN PHYSICAL CONFORMANCE: FAIL for every finite realization.
```

If “for every accepted continuation” in the realization paragraph is instead read as permission to reject an arbitrary capacity-dependent subset of otherwise valid `CROSS` requests, the contract never defines that refusal or its boundary behavior. On that reading the domain is underdefined rather than total. This replay does not choose or propose a repair.

Repeated empty-payload occurrences give the same conclusion for unbounded history length. The result is distinct from ULEB injectivity and from a fixed numeric buffer overflow.

### 4.4 E01 values and buffers

E01 additionally claims arbitrary integers, arbitrary finite byte strings, finite lists, unbounded integer arithmetic, and buffered view/action output. `EXHAUSTED` is tied to instruction fuel; resource exhaustion is not a listed outcome. Even if the missing program grammar were completed, any finite realization could be forced past its representable/durable states by sufficiently large valid literal/output distinctions. Concatenation and lists add further growth routes.

Because E01's grammar is absent, there is no exact program-byte witness to minimize; current F03/B2 already fails earlier. The physical impossibility is conditional on honoring the stated arbitrary value domain and is separate from the mathematical evaluator's possible totality for each ideal finite input.

This is the one genuinely new failure family established by replay relative to the frozen B1–B7/current F01–F03 baseline: **unbounded mandatory valid input plus no resource outcome makes literal finite physical conformance impossible**. It strengthens B4 from UNKNOWN resource evidence to a parametric physical-totality FAIL. It adds no smaller fixed byte-history collision.

## 5. Archive-shape replay

### 5.1 Delimiters, extent, and framing

- Empty/content, direction, payload, order, multiplicity, and normalization merges are already caught by `AT`/`LENGTH` and the frozen mutants.
- P01's ULEB framing blocks the old delimiter-within-payload collision when the complete outer byte-string extent is supplied.
- The old “who delimits the whole artifact?” shape lands exactly on current F02. With `e=((0,empty),)`, `P01(e)=0000` and `P01(e)||P01(e)=P01(e+e)=00000000`. This is not `encode(h1)=encode(h2)` for two histories; it is an external container/EOF responsibility.
- Removing the containing extent or treating a complete-frame truncation as malformed fails: truncating `0000` to the empty string yields the valid empty history. That is coherent rollback/truncation, not a codec collision.

No shorter nonempty framing witness is added. Complexity remains in the containing object's extent, EOF/close rule, storage freshness, and decoder TCB; no dedicated terminator is inferred.

### 5.2 Semantic substitution and evidence self-credit

The old substitution shape asks whether a convenient host-language projection is being used in place of the contracted interpreter. It reproduces current F03 exactly: `make_futures` calls direct Python lambdas and `render`, not canonical E01 byte programs. The absent grammar prevents an exact cross-implementation result.

The candidate's encoder, decoder, expected assertions, and alternate construction path share code and authority; the committed audit re-executes that code. This establishes bounded self-consistency only. The candidate/result explicitly avoid treating it as architecture or independent realization, so the old circular-self-validation attack adds no contradiction. Independent semantic conformance remains UNKNOWN.

E01's returned trace is machine-produced by the evaluator it describes. The candidate calls it machine explanation and denies guaranteed human meaning. It is not independent proof that the evaluator, history capture, action, or physical result was correct. Any stronger evidence reading is blocked by scope rather than passed.

### 5.3 Snapshot roots and request/response capture

The old common-root/cut attacks reproduce B1 and audit F01:

- the smallest missing-definition witness remains empty history plus one `LENGTH(0)` request; request bytes, response bytes, directions, and append order are not fixed;
- the smallest frozen harness mismatch remains `()` versus `((0,empty),)`; direct `len(h)` is not one fixed snapshot-bearing request;
- whether request capture occurs before snapshot validity and whether `CROSS(d,p)` is itself the sole occurrence are unspecified; and
- later `AT` can observe any adapter choice, so the missing mapping cannot be dismissed as internal formatting.

No archive witness is smaller than zero initial occurrences and one future request. Complexity remains in an unspecified boundary adapter, capture sequencer, request grammar, and snapshot rule.

### 5.4 Causality, action, application, and physical completion

C01 distinguishes a buffered action byte output from normal halt, but defines no physical target, application fact, completion condition, acknowledgement, receiver, or crash cut. The candidate expressly withholds exactly-once and durability claims. Old occurrence/application/completion attacks therefore cannot be executed and remain unsupported, not PASS.

There is still a current logical gap: replay is told not to re-emit historical external actions, but raw `(d,p)` occurrences have no specified request/response/action typing or causal association. That is already B1/B6. If an action crosses and physical completion happens before its capture becomes durable, C01 supplies no outcome. Old false-attestation and persist-before-success shapes add no finite R01N result because there is no realization or physical completion predicate.

Complexity sits with the absent adapter, effect driver, receipt/correlation rule, physical observer, durable publication ordering, and recovery protocol.

### 5.5 Terminal and progress attacks

`HALT` is an E01 instruction result, not a system shutdown or irreversible terminal history. C01 defines no graceful termination request, post-terminal query, terminal crash, or physical halt. Old terminal attacks B20–B22 are blocked by absent capability and remain unsupported.

Fuel bounds instruction visits after successful decoding. It does not bound request decoding, ULEB work, replay scan time, memory, buffering, response serialization, store growth, physical append, or wall-clock response. There is no resource-exhaustion response. Thus bounded VM step progress does not cure Section 4's physical-totality failure. For a particular finite service-level claim, progress remains UNKNOWN because no time/memory envelope or physical runner exists.

### 5.6 Viewers, policies, permissions, and adaptive context

C01 has no viewer identity, permission projection, credential/authority rule, MAY/MUST carrier, scheduler identity, adaptive-controller state, or policy installation lifecycle. Passing raw bytes or a program can encode a caller convention, but a convention is not a frozen authorized-viewer contract. E01's `mode` is not defined.

Accordingly:

- viewer-relative leakage/explanation, permission evolution, policy persistence, vacuity, scheduler recovery, and canonical witness attacks are blocked/unsupported;
- the broad goal's advertised viewer/policy support is not established, already within B2/F03;
- raw `AT` deliberately exposes all history under C01, so no low-viewer confidentiality can be inferred; and
- external controller choices are not history-determined unless their bytes actually cross and their semantics are fixed.

Complexity remains with authorization, projection, policy grammar/lifecycle, adaptive controller capture, and human-facing explanation.

### 5.7 Corruption, rollback, and recovery

Current B5/U01 is already the smallest one-bit coherent substitution under its metric:

```text
0000  ->  0100
(0,empty)  ->  (1,empty)
```

The archive adds the minimized rollback shape but not a new family:

```text
0000  ->  empty
(0,empty)  ->  ()
```

Both endpoints are canonical, and one `AT(0)` distinguishes them. No retained integrity/freshness anchor exists. Malformed rejection cannot detect a different valid history, stale prefix, counterfeit whole transcript, or restoration from a coherent older copy.

Crash atomicity, partial append, backup, repair, replica divergence, and effect/capture coordination remain unsupported. Complexity remains with independent integrity/freshness state, recovery media and rules, writer authority, and operations; no particular mechanism is proposed.

### 5.8 Evolution and semantic roots

Raw byte preservation blocks silent deletion of a future-version occurrence, but does not define its meaning. Supplying a new E01 program is a new future request, not an installed cross-restart policy or decoder migration. P01 is bound to one external C01/P01 decoder; E01 itself is incomplete.

Old “meaning then versus meaning now,” authored-under-one-version/applied-under-another, unknown future opcode, rollback, and contract selection attacks are therefore UNKNOWN/unsupported. A future observer can still read old raw bytes, but no frozen conversion, program-version rule, authority, rollback rule, or cross-version action semantics exists. The initial semantic root is external and has no boot occurrence by C01's declared scope; changing that scope would create new history responsibility.

### 5.9 Human cognition, authoring, navigation, and explanation

No participants, tasks, expertise levels, access bounds, times, error measurements, or adjacent controlled cases exist. Raw bytes are exact but semantically opaque. No E01 grammar, authoring tool, schema discovery, search facility, or measured cold-replay latency exists. `AT`, `SLICE`, and rebuilt offsets supply only abstract raw navigation, with `SLICE` edges still underdefined.

Machine offsets/stack depths are not a human explanation or independent evidence. Human cognition, authoring, discovery, query service levels, and semantic explanation remain UNKNOWN/unsupported. Their burden moves to tools, specifications, replay/search computation, reviewers, and organizations.

### 5.10 TCB and unlike realizations

The named TCB includes at least the external C01/P01 authority, missing request adapter, byte extent/container, canonical decoder, scanner, store, E01 specification/implementation, effect driver, physical integrity/recovery mechanism, and evidence comparator. No one-at-a-time perturbation or closure inventory was run. The self-authored test paths share critical code.

No R01N physical realization exists. Prior ext4/tmpfs and Python/Rust results used different contracts/artifacts and cannot transfer. The two unlike-realization obligations in the break remain unrun. Moreover, Section 4 shows that no finite realization can conform to literal unbounded C01; any bounded physical experiment would establish only an explicitly smaller contract/domain, not C01-wide conformance.

## 6. Operator replay and complexity displacement

| operator | archive replay against R01N | classification | where complexity remains or moved |
|---|---|---|---|
| DELETE | occurrence/direction/payload/order/framing deletions collide; derived count/index deletion succeeds; deleting outer extent makes concatenation/truncation ambiguous | current collisions plus successful derived-component deletion | exact distinctions remain somewhere; scans, extent, and decoder move to runtime/TCB |
| MERGE | sort, deduplicate, byte normalization, direction merge, and coherent rollback are observable; no distinct abstract C01 histories can merge | failed history merges | reversible discriminator or original history must remain; side state is still persistence |
| DERIVE | count/offsets/indexes derive; E01 traces/policy/evidence do not yet have an exact available specification; self-produced trace is not independent evidence | conditional success / missing capability | replay CPU, versioned specification, independent evidence, and review |
| RECOMPUTE | exact raw projections can be recomputed; physical outcomes, nondeterministic external results, policy context, and human meaning cannot be regenerated | conditional / unsupported | external results stay in history; algorithms, context, and cold-run operations remain |
| COLLIDE | no mathematical P01 collision found; lossy mutants collide; valid corruption/rollback changes to another valid history; finite physical state forces a parametric collision/refusal | bounded negative evidence; definite integrity and physical-totality failures | integrity/freshness and capacity semantics are absent, not free |
| FUTURE | `AT`/extent observations force raw distinctions; snapshot-bearing harness does not implement its claimed common request; RUN/view/action futures are not executable | current F01/F03 | exact future grammar, adapter, evaluator, and physical completion contract |
| EXTERNALIZE | decoder/specification selection, outer extent, adapter, E01, controller/viewer policy, durability, and evidence are external | missing/large TCB | deployment roots, code, operations, organizations, and human conventions |
| REALIZE | no prior physical evidence transfers; literal unbounded C01 has no finite conformer | physical all-domain FAIL; empirical pair UNKNOWN | finite capacity, media, fault boundaries, observers, and comparator |
| COGNITION | no human study or bounded local-verification claim | UNKNOWN/unsupported | authoring, discovery, review, training, and interface work |
| TCB | no dependency perturbation or independent semantic implementation; common-authority agreement remains only bounded self-consistency | UNKNOWN/incomplete | adapter, container, decoder, evaluator, store, effect/recovery, evidence roots |

Repeated deletion leaves exact-history information in the bounded frozen transcript component. This remains a fixed point of one supplied bundle, not a proof of a globally least representation or total system.

## 7. Already-current, new, blocked, and unknown disposition

### Already current B1–B7 / F01–F03

- request/response wire and capture order missing;
- E01 and request edge domains incomplete;
- direct Python futures substitute for encoded contract futures;
- bounded future enumeration narrower than C01;
- snapshot-bearing `LENGTH` harness mismatch;
- whole-history outer extent externalized;
- valid-to-valid corruption and rollback undetected;
- rebuild/evidence classifications overbroad without exact specifications;
- fresh/hidden and independent semantic evidence limited.

Archive shapes corroborate these but do not make their witnesses smaller.

### Genuinely new failure family

`AR-F01`: literal C01 accepts unbounded finite CROSS payloads/histories and E01 specifies unbounded values/buffers while no memory/storage/resource-exhaustion result exists. Every finite physical realization must collide, refuse, hang, or violate a required response on some valid input. This is distinct from mathematical P01 encoder totality and is parametric in the realization's finite state capacity.

### Genuinely smaller witness

None. The archive adds no smaller fixed finite P01 collision, missing-wire witness, snapshot witness, semantic-substitution witness, or bit-corruption witness. It supplies an explicit one-frame rollback instance already covered in prose by B5, not a new family.

### Blocked attacks

Terminal/post-terminal behavior, viewer permissions, MAY/MUST/vacuity, scheduler identity, canonical witness stability, physical application/completion, policy installation, and cross-version action meaning cannot be instantiated because R01N does not define those capabilities. Withdrawal is not a PASS and their absence is not zero complexity.

### UNKNOWN/unsupported evidence domains

Physical durability and recovery, capture completeness, exact subject conformance, independent E01 implementation, human cognition/authoring, search/navigation service levels, TCB closure, evolution/migration/rollback, operational monitoring/repair, and materially unlike physical realizations remain UNKNOWN or unsupported. Prior executions under other contracts do not change these statuses.

## 8. Simultaneous total-system replay

No scalar, weighting, or cross-row compensation is used.

| dimension | archive-replay result |
|---|---|
| information preservation | mathematical P01 remains injective with supplied outer extent; bounded searches find no collision; capture grammar missing |
| persistent state | exact raw-history information is forced by abstract `AT`; finite physical all-domain persistence is impossible under unbounded mandatory C01 |
| semantics | FAIL: E01 grammar/`mode` and request/response wire are incomplete; Python projections do not substitute |
| cognition | UNKNOWN: raw exactness is not measured comprehension |
| authoring | UNKNOWN/unsupported: no canonical program grammar, tool, validation task, or error data |
| query/navigation | partial abstract raw access; fixed-snapshot correspondence failure; slice edges/search/service levels absent |
| runtime | bounded falsifier reproducible; literal unbounded physical totality FAIL; progress/resource envelope absent |
| storage | mathematical code exact with external extent; physical capacity, integrity, atomicity, and recovery fail or remain unsupported |
| operations | UNKNOWN/unsupported: concurrency, crash, backup, restore, repair, monitoring, migration, and effect coordination absent |
| TCB | incomplete and unperturbed; significant adapter/container/decoder/evaluator/store/evidence roots remain |
| evolution | raw bytes survive; decoder/program migration, version selection, time-scoped meaning, and rollback unsupported |
| portability | no independent R01N semantic implementation or physical pair; prior results do not transfer |
| explainability | machine trace grammar incomplete and self-produced; viewer-valid/human/physical explanation unsupported |
| information-loss risk | one-bit coherent substitution and one-frame rollback are accepted; no integrity/freshness anchor |
| unlike physical realizations | empirical evidence UNKNOWN; literal all-domain conformance impossible for each finite realization |
| evidence/research process | hashes, rerun, and post-freeze archive chronology PASS narrowly; shared-authority execution is not independent correctness |

## 9. First-milestone information classification after replay

These are information responsibilities, not fields, constructors, records, objects, layers, graphs, or an architecture.

### MUST SURVIVE

- Under the abstract raw-audit contract, enough distinction to reconstruct the exact ordered sequence of every actually captured boundary occurrence: extent, boundaries, order, multiplicity, direction, and payload bytes. `AT` and suitable extent/prefix observations force this.
- The ability to delimit the complete persisted codeword from surrounding material must exist in the total representation. F02 does not force a count or terminator; it exposes an outer-extent responsibility.
- Actual nondeterministic or physical results that cross cannot be replaced by rerunning their producer.
- The exact governing specification/decoder selection must remain available as fixed TCB, though it is not history-variable quotient information under C01.

The first bullet is conditional on a capture grammar that R01N does not supply. A surviving distinction does not imply a dedicated constructor.

### MAY REBUILD

- occurrence count, offsets, direct indexes, and compatible raw navigation tables from exact transcript plus exact P01 decoder;
- deterministic projections only when their exact algorithm/version and required inputs are identified and available.

Rebuild moves cost to scan/replay time, memory, version retention, code correctness, availability, and review.

### MAY FORGET

- completed scan cursors, post-request working stacks, cache eviction order, allocation identity, and excluded host behavior that did not cross and cannot affect a permitted future;
- redundant persisted counts/indexes in the tested bundle, subject to accepting rebuild cost.

### UNKNOWN OR UNSUPPORTED

- E01 traces and installed policy/configuration, because their grammar/lifecycle is incomplete;
- causal/evidentiary typing of raw occurrences;
- physical application/completion, crash/effect coordination, integrity/freshness/recovery, and operations;
- viewer-relative explanations/policies, evolution/migration, human cognition/authoring, navigation service levels, TCB closure, and unlike realization evidence;
- any finite physical realization satisfying literal unbounded C01—in fact Section 4 establishes FAIL, not merely lack of a run.

## 10. Final archive verdict

The archive does not find a mathematical P01 encoding collision and does not shrink the already-minimal missing-wire, snapshot, semantic-substitution, or one-bit-corruption witnesses. It confirms that delimiter/extent, capture, evidence self-credit, physical action completion, terminal/progress, viewer/policy, recovery, evolution, cognition, navigation, TCB, and unlike-realization responsibilities were not removed; most are current failures or unsupported domains.

It does add one stronger family. R01N's ideal encoder may be total on mathematical finite histories, yet no finite physical realization can accept and preserve every unbounded finite C01 history—or the promised unbounded E01 value/output domain—when the contract has no resource-exhaustion refusal. That is a literal physical-totality failure, not an encoder collision and not a proposed repair.

```text
FIRST MILESTONE: FAIL / NOT ACHIEVED.

Conditional raw-history obligation: defensible.
Mathematical P01 injectivity: survives the replay with outer extent supplied.
Frozen total semantics: FAIL (capture grammar, snapshots, E01).
Literal finite physical realizability: FAIL (unbounded mandatory domain).
Minimum total system and unlike-realization evidence: UNKNOWN.
```

No prior representation, physical result, or ontology is inherited, and no scalar masks a failed or unsupported dimension.
