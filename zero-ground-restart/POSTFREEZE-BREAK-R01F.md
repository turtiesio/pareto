# Post-freeze ontology-blind audit

Frozen SHA-256 verified:

`f9fce4d2f0fd43594553f06ab05403d90b088b3f2fd50b7c3f883be7f7b03445`

Spaces below separate exact hexadecimal bytes. `CT1` and `CT2` denote the exact byte blocks frozen in §3.

## Blocking defects and ambiguities

### 1. Malformed “crossings” contradict universal framing

**Classification:** contradiction  
**Clauses:** §§1–2, 4–5, 8.2, 16.1.

Section 2 says every crossing is exactly `E(P)`, hence at least two bytes, with no alternative termination signal. Sections 4 and 16 nevertheless require zero- and one-byte completed crossings.

Smallest collision:

- \(h_0\): STOP/no submission; byte history `ε`.
- \(h_1\): submit the “empty raw crossing”; byte history also `ε`.

Shared future:

- EXPLAIN request: `00 01 40`.

Required responses:

- \(h_0\): `00 02 95 00`.
- \(h_1\), coarse: `00 02 95 01`.
- \(h_1\), detailed: `00 05 95 01 00 00 00`.

With only byte crossings, \(h_0\) and \(h_1\) are indistinguishable. If a zero-length datagram/call boundary distinguishes them, that is an additional non-byte termination signal and contradicts §§1–2 and §5’s “raw `E(P)` messages.” The one-byte input `00` has the same completion-boundary problem.

Consequently, the Section 16.1 strict-inclusion witness is arithmetically correct only after assuming an unlisted out-of-band submission boundary.

### 2. Receiver acceptance cannot be both two observable crossings and one atomic fault block

**Classification:** infeasibility  
**Clauses:** §§10.2, 12.2–12.4, 16.2.

Pre-cut:

- CREATE: `00 06 10 00 00 00 00 00`
- success: `00 01 80`

Future ACTION:

- `C→S 00 02 30 00`
- `S→A 00 04 41 30 00 00` (`A0`)

Section 12.2 permits a crash immediately after every observable crossing, so this exact prefix must admit:

- `F→* 00 02 46 30`
- `*→F 00 02 46 31`

But §12.3 forbids every recovery containing `A0` without `AE` and applied receiver state.

The second adjacent cut is independently contradictory:

- `S→A 00 04 41 30 00 00`
- `A→W 00 04 41 45 00 00`
- crash `00 02 46 30`
- restart `00 02 46 31`

Section 10.2 places the durable “applied” record after `AE`; §12.3 declares it already applied atomically with `A0||AE`. A subsequent status probe

- `S→A 00 03 41 32 00`

therefore has two incompatible required responses:

- absent: `A→S 00 04 41 31 00 01`;
- applied: `A→S 00 04 41 31 00 00`.

No physical realization can expose two ordered crossings, permit faults after each crossing, and simultaneously make the pair plus a later durable receiver transition one indivisible boundary.

### 3. Post-acknowledgement recovery has two specified continuations

**Classification:** underspecification  
**Clauses:** §§10.2–10.3, 12.3.

Use the same CREATE/ACTION prefix through direct acknowledgement:

- `A→S 00 04 41 31 00 00`
- crash `00 02 46 30`
- restart `00 02 46 31`

The local nonce is still pending because §10.2 commits completion after the acknowledgement. Section 10.3 says a locally pending action “always” begins recovery with:

- `S→A 00 03 41 32 00`
- `A→S 00 04 41 31 00 00`

Section 12.3 instead says post-crossing recovery continues from post-`A1`, whose next microstep is durable completion followed by:

- `S→C 00 01 80`

It does not determine whether the probe pair is present in the required trace.

### 4. Crashes in recovery machinery conflict with the one-crash bound

**Classification:** contradiction  
**Clauses:** §§11, 12.2, 12.4, 13–14.

Sections 11 and 14 allow at most one `F0,F1` pair. Section 12.2 nevertheless permits a crash during every persistent byte write in recovery machinery.

Smallest relevant prefix:

- first crash: `00 02 46 30`
- restart: `00 02 46 31`
- recovery reaches a persistent pending→completed byte write.

Faulting that write requires a second:

- `00 02 46 30`
- `00 02 46 31`

which the global bound forbids. Thus “recovery machinery” fault sites are either unreachable text or require an undefined second crash trace.

### 5. Successful-request provenance preservation has a malformed exception

**Classification:** underspecification  
**Clauses:** §6 versus §§7–8.

Section 6 says successful requests never modify saved provenance “unless their stated primary state transition independently overlaps no provenance field.” Every listed successful primary transition overlaps no provenance field, so the exception removes the stated preservation rule exactly where it should apply.

Exact histories:

- \(h_0\): reject `00 01 00`.
- \(h_1\): reject `00 01 00`, then successful IDENTIFY `00 01 70`.

Shared future:

- EXPLAIN `00 01 40`.

Detailed preservation requires both to return:

`00 08 95 05 02 00 03 00 01 00`

The frozen wording does not uniquely say whether successful IDENTIFY may clear or replace that tuple. Section 8 explicitly protects successful EXPLAIN but does not restate the rule for all other successes.

### 6. “Latest IDENTIFY response” introduces unmodelled path state

**Classification:** underspecification  
**Clauses:** §§6, 13, 17.1, 19.

Consider:

- \(h_0\): IDENTIFY under CT1, then UPDATE CT2.
- \(h_1\): UPDATE CT2, then IDENTIFY under CT2.

Exact relevant bytes:

- IDENTIFY request: `00 01 70`
- CT1 response: `00 b0 94 01 00 ac || CT1`
- UPDATE CT2: `00 b9 60 00 b6 || CT2`
- success: `00 01 80`
- CT2 response: `00 ba 94 02 00 b6 || CT2`

Both cuts have the same canonical semantic tuple: CT2, virgin, no rejection. Literal “latest IDENTIFY response” differs, so the total identity in §19 is path-sensitive state absent from §§6, 17, and 18.

If “latest” means a newly generated response for the current version, the histories merge, but that is not what “separately retained” says. No byte crossing is defined for reading the total identity tuple, so the future that observes it is itself unspecified.

## Attacks discharged or contract-gated

### Detailed rejection retention and precedence

Apart from defect 5, §§8.2–8.4 give a complete current-raw-byte precedence rule.

A minimal raw-retention separator with no empty-frame issue is:

- \(R_0=\) `00 01 00`
- \(R_1=\) `00 01 01`

Both reject as rule `05`, offset `02`, length `0003`. Future EXPLAIN `00 01 40` yields:

- `00 08 95 05 02 00 03 00 01 00`
- `00 08 95 05 02 00 03 00 01 01`

Thus detailed raw retention is genuinely `MUST SURVIVE`; coarse deliberately merges them. Replacement ancestry older than the latest rejection is explicitly unobservable, so that broader provenance attack is gated out.

The §16.1 payload arithmetic is correct:

- empty rejection: `95 01 00 00 00`;
- one-byte `00` rejection: `95 01 01 00 01 00`;

but its use depends on resolving defect 1.

### UPDATE framing, lengths, and version self-description

The exact lengths are correct:

- CT1: 172 bytes; UPDATE payload 175; raw frame 177:
  `00 af 60 00 ac || CT1`
- CT2: 182 bytes; UPDATE payload 185; raw frame 187:
  `00 b9 60 00 b6 || CT2`

Minimal exact validation probes also have unique results:

- `00 02 60 00` → `UPDATE_HEADER`, offset `04`.
- `00 03 60 00 01` → `UPDATE_LENGTH`, offset `05`.
- `00 04 60 00 00 00` → `UPDATE_LENGTH`, offset `05`.
- `00 03 60 00 00` → `CONTRACT_TEXT`, offset `05`.

For the last request, detailed EXPLAIN is:

`00 0a 95 0b 05 00 05 00 03 60 00 00`

Active version is semantically `MUST SURVIVE`. Exact separator:

- \(h_0=[]\) at CT1.
- \(h_1=[00 b9 60 00 b6 || CT2]\).

Future UPDATE CT1:

`00 af 60 00 ac || CT1`

returns:

- \(h_0\): `00 01 80`;
- \(h_1\), coarse: `00 01 82`;
- \(h_1\), detailed: `00 03 83 24 05`.

The immutable CT mapping used to rebuild contract text is external specification/TCB state, not an engine-semantic survival result.

### Exactly-once receiver responsibility

The ordinary non-deduplicating-receiver impossibility is acknowledged and gated out by §§10.4, 18, and 22. Receiver dedup/status state while pending is part of the total system and is semantically `MUST SURVIVE`, even when not local to the engine.

TCB-loss witness:

- world 0: receiver retains applied nonce `00`;
- world 1: the same receiver is rolled back to unseen after `AE`;
- shared recovery probe: `00 03 41 32 00`.

Responses are:

- world 0: `00 04 41 31 00 00`;
- world 1: `00 04 41 31 00 01`, followed by another `A0`/`AE`.

World 1 is outside permitted receiver behavior, so this is a required TCB consequence finding, not a conforming semantic branch. It does not cure defect 2.

### Hidden path state and shortest representatives

Except for §19’s “latest IDENTIFY” ambiguity, the path-sensitive attack is gated out explicitly:

- all pre-cut histories through two frames are enumerated, not only shortest representatives;
- future policies begin with empty post-cut observation;
- interpreter tables have no prior-history access;
- receiver state has only the specified nonce role;
- residual equality uses full adaptive structure.

Minimal intended merge:

- \(h_0=[]\)
- \(h_1=[\text{IDENTIFY }00\,01\,70]\)

Both have identical permitted residuals because the successful IDENTIFY changes no semantic state and prior transcript bytes are unavailable. An exact-history separator would distinguish them, but no such continuation is encodable in CF-1.

### Counterfeit, malformed, and replayed recovery images

These attacks are gated out of semantic conformance. The only permitted storage failures are old/new one-byte-write crash outcomes required to recover as reference pre/post configurations. Arbitrary storage corruption, provenance authentication, counterfeit images, and rollback are not recovery inputs.

A replay consequence witness is nevertheless exact at the semantic boundary:

- genuine current history: CREATE `00 06 10 00 00 00 00 00`;
- actual history: the same CREATE, then RETIRE `00 01 11`, followed by rollback to the earlier physical image;
- future OBSERVE: `00 01 20`.

Live recovery returns `00 02 90 00`; correct retired history rejects (`00 01 82` coarse or `00 03 83 21 02` detailed).

Because persistent encodings are realization-defined, no artifact-independent malformed persisted byte string exists in the frozen text. Such strings can only be instantiated after a physical build is frozen. Sections 18 and 22 charge their consequences to TCB corruption/loss analysis.

### Nondeterministic trace-set correlations

The representation is correlation-safe: §§13–14 compare sets of complete ordered transcripts and full adaptive residual structures, not one-step marginals.

The two §16.2 core traces expand distinctly. Receiver-pre contains:

`00023000, 00024630, 00024631, 0003413200, 000441310001, 000441300000, 000441450000, 000441310000, 000180`

Receiver-post contains:

`00023000, 000441300000, 000441450000, 00024630, 00024631, 0003413200, 000441310000, 000180`

Their ordering correlation survives canonicalization. The defect is that the required set omits the mandatory mid-block traces from defect 2, not that the set representation loses correlations.

### Switch identity

A/B identity is intentionally externalized into the exact manifest. Without it, the acknowledged collision is immediate:

- same CT1 IDENTIFY response under coarse and detailed;
- future invalid request `00 01 00` returns `00 01 82` versus `00 03 83 05 02`.

Thus the exact manifest line is TCB/configuration information that must survive in the charged total system. Loss or counterfeit manifest state is gated out of conforming semantics. The separate “latest IDENTIFY” issue remains defect 6.

### Unlike-realization oracle independence

The two reducers are required to be independent, but the reference vectors and comparison harness are explicitly shared. Therefore the experiment tests realization diversity, not oracle independence.

This is correctly exposed as shared TCB in §§20, 22, and limited by §24. Corrupt-oracle behavior is gated out of semantic conformance and must be reported as TCB loss risk. However, the shared oracle cannot resolve defects 1–4: for the mid-`A0` trace it must either violate §12.2 by omitting it or violate §12.3 by including it. Agreement of both builds with either choice does not make the frozen clauses consistent.

### Exact-history theorem boundary

The theorem is correctly bounded in §23. The pair

- `[]`
- `[IDENTIFY 00 01 70]`

would be separated by a future exact-history equality interpreter, but CF-1 permits only four unary tables over stored `i`; UPDATE cannot introduce another interpreter or contract text. Therefore the exact-history attack is gated out—subject to resolving whether §19’s external total-identity viewer can inspect literal prior IDENTIFY state.

### Enumerator termination

**Classification:** merely huge-but-terminating.

`U`, all pre-cut sequences, depth-three residuals, table choices, acknowledgement schedules, and one-crash branches are finite. Full structural comparison and breadth-first witness search therefore terminate on an ideal exact machine. The recurrence’s factor `804` safely covers the largest per-request environment branch: `4×201` for INTERPRET; ACTION’s `2×201` is smaller. The global `4^5` also upper-bounds mixed interpreter/acknowledgement choices because replacing an interpreter choice factor `4` with an action schedule factor `2` cannot increase it.

No deadline or finite practical resource cap converts the astronomical run into nontermination. Dense-ID and DAG rebuilding are likewise terminating in the stated mathematical sense.

However, the enumerator cannot produce a unique authoritative quotient from the frozen artifact until defects 1–4 are resolved: choosing whether an empty crossing exists, whether the mid-`A0` crash exists, which post-ack trace applies, or whether recovery can crash again requires discretionary semantics forbidden by §§18 and 21. This is an oracle-definition failure, not a cardinality failure.

## Survival boundary

Semantic `MUST SURVIVE` is supported by exact future bytes for active version, lifecycle, live creation bits, used nonces, current saved rejection, active power-recovery frame/phase, and pending receiver dedup state.

The immutable CT mapping, run manifest, receiver durability/status machinery, retained transport, interpreter selector, one-byte atomicity, drivers, reference enumerator, and equality checker are externalized specification/TCB responsibilities. Their loss changes required traces, but such loss is not a permitted semantic crash branch.
