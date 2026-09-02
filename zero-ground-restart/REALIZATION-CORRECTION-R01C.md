# REALIZATION CORRECTION R0.1C — ATTACK-INFORMED SUCCESSOR CONTRACT

## 0. Authority, status, and prohibition

R0.1C is a successor candidate, not a repair in place.  Against base repository
commit `6742676`, the following exact file bytes are immutable attack
authorities:

| file | SHA-256 |
|---|---|
| `FEASIBILITY-AUDIT-R01B.md` | `8ca5b9a1e3d3b6b4589978a806756cfa3dd60f52637848128e776430f7ecc2a6` |
| `FEASIBILITY-SUPPLEMENT-R01B-RUN-BOUNDARY.md` | `465dbe64f9600270fea926b7dc1aa7bfdc1c4f86e0897643c185ad4e57a339f7` |
| `R01B-BLACKBOX-BREAKER.json` | `77dd3ef14b848135cb9ebbcd62b1c86cd2b1cf60f08d469263fb5f5308ffa9df` |

Their `CONTRACT_DEFECT_UNDECIDABLE` result, all nine fatal defects F1--F9,
every minimized witness, and the fact that no R0.1B subject trial ran remain
results.  R0.1C neither edits nor reinterprets an R0.1B byte into a pass.  The
old positive and hash-only replay fixtures are malformed retained attacks
after this correction.

Except where this file explicitly says **R01C REPLACEMENT**, the semantics of
`REALIZATION-CORRECTION-R01B.md`, its frozen S0/S1 corpus, and its registries are
inherited.  A replacement clause applies only to an R0.1C effective corpus; it
does not change the meaning or hash of an R0.1B artifact.  In particular,
R0.1B's `D_sem`, record bytes, B wires, descriptor domains, oracles, aggregation
precedence, apparatus bounds, and boundary-scoped persistence meanings remain
unchanged unless named below.

This one file does **not** close a semantic gate.  No publisher, recovery
reader, adapter, controller, tracer, normalizer, serializer, replay service,
verifier, schema validator, or other subject implementation may be authored or
adapted from this candidate; no gate-R package may be frozen; and no registered
subject or LAB trial may be launched until the new semantic gate `S_C` in
section 12 has been independently materialized, byte-checked, attacked, and
closed.  Pure contract review and construction of the future S-gate artifacts
are the only authorized next work.  A later gate close would authorize a new
implementation phase, not a trial; the resulting realization must then close
gate `R_C` before its first trial.

R0.1C remains a finite falsification instrument.  It is not the target
contract, a global architecture, a least system, or proof of physical
persistence.

## 1. Exact notation and inherited codec

`ASCII(s)`, `UTF8(s)`, `u8`, `u16be`, `u32be`, `u64be`, `i32be`, `LP`,
`SHA256`, and lowercase hexadecimal have their R0/R0.1B meanings.  `LP(x)` is
`u32be(length(x)) || x`.  `TV` is exactly the recursive codec in R0.1B section
3.  A TV map is encoded by ascending unsigned map-key bytes.  Every closed map
in this file rejects missing, additional, or duplicate members.

When this file writes a map or list without an outer `bytes(...)`, it is a TV
map or list value nested directly in its parent.  `bytes(TV(v))` is a tag-`03`
byte string containing already encoded bytes and is used only where explicitly
written.  This distinction rejects the prior map/list/double-encoding
alternatives.

All controlled text in this file is exact printable ASCII and is not Unicode
normalized.  Unless a list is explicitly chronological or registry-positional,
its order is fixed in section 10.  Duplicate members in every set-like list
are invalid; silently deduplicating them is invalid.

## 2. Closed B values

This section is an **R01C REPLACEMENT** for R0.1B section 1.2's three uses of
`typed(...)`.  It does not change which values cross B.

### 2.1 B-event namespace and event value

TV enum namespace `8` is reserved for B events:

| code | event | exact payload type |
|---:|---|---|
| `0` | `SETUP` | setup text from R0.1B section 1.3 |
| `1` | `ARM` | text `J0` through `J5`, or `NORMAL` |
| `2` | `INJECT` | registered injected-fault text |
| `3` | `REQUEST_PUBLISH` | exact requested-payload bytes |
| `4` | `PUBLISH_RESULT` | exact R0.1 publication-result wire as bytes |
| `5` | `INSTALL_RECOVERY_FIXTURE` | the closed recovery-fixture map from R0.1B section 1.3 |
| `6` | `REQUEST_RECOVER` | exact continuation bytes |
| `7` | `RECOVERY_OBSERVATION` | exact recovery-observation wire as bytes |

An event is exactly a TV list of length two:

```text
[enum(namespace=8, code), payload]
```

No event map, tuple concatenation, text label in place of the enum, or encoded
TV event wrapped in tag `03` is legal.

### 2.2 `BH_value` and `BH_bytes`

`BH_value(d,o)` is the nested `history_events` TV value below.
`BH_bytes(d,o) = TV(BH_value(d,o))`.  The names are deliberately distinct:
canonical records contain the nested value, while behavioral comparison uses
its encoded bytes.  No tag-`03` wrapper around `BH_bytes` is legal.

`BH_value` has exactly one of these two shapes.

For `PUBLICATION` it is the chronological list:

```text
[
  [SETUP, setup],
  [ARM, cut],
  [INJECT, injected_fault],
  [REQUEST_PUBLISH, requested_payload],
  [PUBLISH_RESULT, publish_result],        # present iff that B crossing occurred
  [REQUEST_RECOVER, continuation],
  [RECOVERY_OBSERVATION, recovery_wire]
]
```

The fifth displayed item is omitted, without a null or sentinel, exactly when
the publisher was killed before a publication-result crossing.  All other
items are mandatory.

For `RECOVERY_ONLY` it is exactly:

```text
[
  [INSTALL_RECOVERY_FIXTURE, recovery_fixture],
  [REQUEST_RECOVER, continuation],
  [RECOVERY_OBSERVATION, recovery_wire]
]
```

`LAB_ONLY` and an attempt ending in `CONTROL_UNAVAILABLE` before B have no
`BH_value` or `BH_bytes`.  An empty list is not a history for either case.

### 2.3 `B_input_key` and `B_response`

`B_input_key(d)` is the TV encoding of the input-event projection, retaining
the original chronological positions while deleting response events:

```text
PUBLICATION = TV([
  [SETUP, setup], [ARM, cut], [INJECT, injected_fault],
  [REQUEST_PUBLISH, requested_payload],
  [REQUEST_RECOVER, continuation]
])

RECOVERY_ONLY = TV([
  [INSTALL_RECOVERY_FIXTURE, recovery_fixture],
  [REQUEST_RECOVER, continuation]
])
```

`B_response(d,o)` is the TV encoding of the response-event projection:

```text
PUBLICATION, publish crossing present =
  TV([[PUBLISH_RESULT, publish_result],
      [RECOVERY_OBSERVATION, recovery_wire]])

PUBLICATION, publish crossing absent =
  TV([[RECOVERY_OBSERVATION, recovery_wire]])

RECOVERY_ONLY =
  TV([[RECOVERY_OBSERVATION, recovery_wire]])
```

Thus the former logical `publish_result_list` is uniquely represented by zero
or one event in the displayed response list.  `ABSENT`, `REJECT`, `OK(Y0)`, and
`OK(Y1)` payloads remain the exact tag-`03` byte values `00`, `01`,
`0200000000`, and `020000000100`.  They are not TV integers or enums.

For a complete B history, TV-encoding `BH_value` filtered by event codes
`{0,1,2,3,5,6}` must equal `B_input_key` byte-for-byte, and TV-encoding the
filter by codes `{4,7}` must equal `B_response`.  This is the independently
checkable relation between stored canonical evidence and B.

## 3. Failure reasons and the complete status value

This section is an **R01C REPLACEMENT** for the incomplete status-map and
failure-reason rules in R0.1B section 5.

### 3.1 Namespace closure

Namespaces `1` through `6` and all their codes retain the R0.1B tables:

| namespace | coordinate | codes in numeric order |
|---:|---|---|
| `1` | applicability | `0 APPLICABLE`, `1 CONDITIONAL_ONLY`, `2 NOT_APPLICABLE`, `3 UNSUPPORTED_HERE`, `4 UNKNOWN` |
| `2` | execution | `0 NOT_RUN`, `1 COMPLETE`, `2 CONTROL_UNAVAILABLE`, `3 APPARATUS_FAILURE`, `4 TIME_BOUND_EXCEEDED`, `5 STORAGE_BOUND_EXCEEDED` |
| `3` | oracle | `0 ASSERTED`, `1 CONDITIONAL_RETAINED`, `2 NOT_DECLARED`, `3 UNKNOWN` |
| `4` | full conformance / check status | `0 PASS`, `1 FAIL`, `2 UNKNOWN`, `3 UNSUPPORTED`, `4 NOT_APPLICABLE` |
| `5` | behavioral comparison | `0 MATCH`, `1 DIFFER`, `2 UNKNOWN`, `3 NOT_COMPARED` |
| `6` | scope | `0 B_PROCESS_KILL`, `1 L_EVIDENCE`, `2 GUEST_REALIZATION`, `3 CONDITIONAL_FUTURE`, `4 PHYSICAL_OR_POWER` |

TV enum namespace `7` is reserved exclusively for failure reasons.  Codes
`0..33` retain the R01B registry verbatim; R0.1C appends codes `34..43` in
ascending unsigned-UTF-8 label order:

| code | label |
|---:|---|
| `0` | `COMPARATOR_FALSE_MATCH` |
| `1` | `CUT_OVERRUN` |
| `2` | `DUPLICATE_LEGACY_STAGE` |
| `3` | `DUPLICATE_NEUTRAL_FRAME` |
| `4` | `EVIDENCE_UNAVAILABLE` |
| `5` | `FALSE_SUCCESS_ATTESTATION_DIRECTORY_FSYNC` |
| `6` | `FALSE_SUCCESS_ATTESTATION_EXCLUSIVE_CREATE` |
| `7` | `FALSE_SUCCESS_ATTESTATION_FILE_FSYNC` |
| `8` | `FALSE_SUCCESS_ATTESTATION_REPLACE` |
| `9` | `KILL_NOT_CAUSAL` |
| `10` | `MALFORMED_STRUCTURED_UNKNOWN` |
| `11` | `MISSING_MEASUREMENT` |
| `12` | `MISSING_RECOVERY_OBSERVATION` |
| `13` | `MISSING_REQUIRED_CONTAINER_MEMBER` |
| `14` | `RECOVERY_BEFORE_REAP` |
| `15` | `SELECTION_MISSING` |
| `16` | `SEMANTIC_MISMATCH` |
| `17` | `STRUCTURED_STATUS_FORBIDDEN` |
| `18` | `B_RESPONSE_MISMATCH` |
| `19` | `COMMON_MODE_NEGATIVE_NOT_REJECTED` |
| `20` | `COMPARISON_EDGE_EXPECTATION_MISMATCH` |
| `21` | `CONTROL_PROTOCOL_MISMATCH` |
| `22` | `CUT_REACHABILITY_MISMATCH` |
| `23` | `DESCRIPTOR_OR_OVERLAY_MISMATCH` |
| `24` | `EVIDENCE_ENVELOPE_SCHEMA_MISMATCH` |
| `25` | `MANIFEST_SELF_REPORT_TRACE_DISAGREEMENT` |
| `26` | `OPERATION_ERRNO_MISMATCH` |
| `27` | `OPERATION_FACT_MISMATCH` |
| `28` | `OPERATION_SOURCE_MISMATCH` |
| `29` | `REPLAY_EXACT_BYTES_MISMATCH` |
| `30` | `TERMINAL_MISMATCH` |
| `31` | `UNREGISTERED_B_OR_L_CROSSING` |
| `32` | `UNREGISTERED_ERRNO` |
| `33` | `WAIT_ORDER_MISMATCH` |
| `34` | `B_TV_SHAPE_MISMATCH` |
| `35` | `CANONICAL_RECORD_SCHEMA_MISMATCH` |
| `36` | `FAILURE_REASON_NAMESPACE_MISMATCH` |
| `37` | `GATE_R_IDENTITY_MISMATCH` |
| `38` | `INVENTORY_REFERENCE_MISMATCH` |
| `39` | `LIST_ORDER_MISMATCH` |
| `40` | `MM_ASSIGNMENT_MISMATCH` |
| `41` | `POSITIVE_REPLAY_FIXTURE_MISMATCH` |
| `42` | `RAW_PACK_OR_LOCATOR_MISMATCH` |
| `43` | `STATUS_MAP_MISMATCH` |

For example, `COMPARATOR_FALSE_MATCH` is exactly
`0b 0007 0000`; `0b 0008 0000` is an unknown namespace and invalid.  Runtime
observations cannot add a reason code.

Namespace `8` remains the B-event namespace from section 2; it is not a
failure-reason alternative.  R0.1C allocates no completeness enum: the
zero/one missing-suffix union carries that one bit directly.

TV enum namespace `10` is reserved for the post-terminal continuation
supervisor:

| code | outcome |
|---:|---|
| `0` | `VALID_PROCESS_RESPONSE` |
| `1` | `REQUEST_WRITE_FAILURE` |
| `2` | `PROCESS_LAUNCH_FAILURE` |
| `3` | `PROCESS_TIME_BOUND_EXCEEDED` |
| `4` | `PROCESS_EXIT_FAILURE` |
| `5` | `MALFORMED_OR_OVERLONG_RESPONSE` |
| `6` | `RETAINED_STREAM_PROVIDER_FAILURE` |

No runtime outcome may add a code or reinterpret this enum as a reason.
Section 9 reuses codes one through five for its nonempty preflight failure
payload; codes zero and six are invalid there.  The enclosing PREFLIGHT frame
versus post-terminal outcome channel already distinguishes the two contexts,
so a second isomorphic enum namespace would add no information.  A successful
PREFLIGHT has no outcome enum and an empty payload: its complete kind-`03`
frame at physical ordinal one is the success occurrence.  These codes are
apparatus observations, not failure-reason enums.

### 3.2 Exact eight-member map

`status_coordinates` is a required derived query value for one envelope, not a
member persisted inside that envelope.  Its exact TV map has this shape and no
other:

```text
{
  applicability:          enum namespace 1,
  behavioral_comparison: enum namespace 5,
  execution:              enum namespace 2,
  failure_reasons:        list(enum namespace 7),
  full_conformance:       enum namespace 4,
  needed_evidence:        list(nonempty text),
  oracle:                 enum namespace 3,
  scope:                  list(enum namespace 6)
}
```

`scope`, `failure_reasons`, and `needed_evidence` are sorted and unique by
section 10.  Every needed-evidence text must occur in the mechanically derived
controlled set in section 12; that set is not repeated in the derived closure
view, and
diagnostics cannot mint a new value.  `scope` is nonempty.
`failure_reasons` is nonempty iff full
conformance is `FAIL`; otherwise it is empty.  It is the sorted set union of
all failed constituent checks' reason enums.  `needed_evidence` is the sorted
set union of every constituent check's needed-evidence text plus every
coordinate-level missing-evidence requirement.  It is nonempty whenever an
applicable constituent check is `UNKNOWN` or `UNSUPPORTED`; it may also be
nonempty for a retained conditional future.  Free-form diagnostics never enter
either list.

Full-conformance aggregation remains
`FAIL > UNKNOWN > UNSUPPORTED > PASS > NOT_APPLICABLE`; behavioral aggregation
remains `DIFFER > UNKNOWN > MATCH > NOT_COMPARED`.  The aggregate is recomputed
from the canonical check and edge records; an asserted aggregate without those
inputs is invalid.

Applicability, oracle, and scope derive from the selected effective S1 row;
behavioral comparison, full conformance, failure reasons, and needed evidence
derive from its positional edge/check results under the rules above.  Execution
derives without another per-envelope field: when a stop terminal has
`submitted_stop=true`, its final envelope has that stop code; a false bit gives
the cause to no envelope.  Any remaining subject envelope with empty
`b_observation` is `CONTROL_UNAVAILABLE`; every LAB envelope and every other
subject envelope is `COMPLETE`.  The closed record rules make these branches
disjoint.  A consumer may materialize the eight-member map, but it must equal
this reconstruction byte-for-byte.

## 4. Canonical records: one closed per-trial grammar

This section is an **R01C REPLACEMENT** for R0.1B's undefined
`canonical_records` field.  The envelope member is a nested TV map value, not
an opaque tag-`03` string and not a concatenation of implementation records.
It contains exactly one trial record because every envelope is already scoped
to one submitted descriptor.  A redundant one-element stream wrapper is
forbidden.

### 4.1 Common leaves

A rebuilt raw-locator query value is exactly:

```text
{
  length: U64,
  offset: U64,
  pack: text("RAW_MEASUREMENT") | text("RAW_TRACE"),
  stream_id: nonempty printable-ASCII text
}
```

Offsets address the unwrapped content bytes of the named raw stream, starting
at zero; they never address TV tags, envelope bytes, or the L-stream frame.
`offset + length` is evaluated without u64 wrap and must not exceed the stream
length.  The exact range hash is mechanically rebuilt from the retained target
bytes and is not repeated in the locator.  A locator list is sorted and unique
by section 10.  A digest never substitutes for its bytes.

An operation fact is exactly:

```text
{
  evidence_sources: list(text from the inherited evidence-source registry),
  fact: text from the inherited operation-fact registry,
  registered_errno: text("NONE") | text("EEXIST_17") | text("EIO_5") |
                    {number: U64},
  unknown_detail: list(structured-unknown tag 09)
}
```

There is exactly one fact for each inherited operation, in registry order;
position supplies the operation, so its text is not repeated.
`OBSERVED_KERNEL_ERROR` and `SIMULATED_ERROR_WITHOUT_KERNEL_ENTRY` require a
non-`NONE` errno.  All other facts require `NONE`.  The map alternative itself
means unregistered and truthfully retains the numeric value of an observed errno outside the two
registered literals; the rebuilt locator view must also select the observation bytes and
the relevant check fails with reason `UNREGISTERED_ERRNO`.  It is not encoded
as `NONE`, guessed into a registered label, or hidden only in free-form raw
text.  Repeating `state="UNREGISTERED"` inside the sole map branch is
forbidden.
`unknown_detail` has length one iff `fact="UNKNOWN"` and length zero otherwise.
It is a zero-or-one union, not a set and not a null substitute.
`UNKNOWN` is legal only when the enclosing execution is one of the three
section-5.4 stop causes; its sole value is the exact
`stopped_before_capture_map[execution]` pair.  A different reason/evidence pair
or an `UNKNOWN` fact in a completed execution is invalid.

A constituent check is exactly:

```text
{
  failure_reasons: list(enum namespace 7),
  needed_evidence: list(nonempty text),
  status: enum namespace 4
}
```

The enclosing trial supplies case identity.  Position in the selected row's
unsigned-check-key order supplies the check key, target, and oracle reference.
A display ID, repeated check key, case ID, target, expected value, and repeated
aggregate status are forbidden.
The reason-list iff rule applies to the check's own `status`.

An edge result is exactly one enum in namespace 5.  Position in the selected
row's unsigned incident-edge-ID order supplies its edge ID.  The effective S1
edge registry supplies both endpoints and expected result.
Each incident result occurs once in each endpoint envelope; that repetition is
required so either descriptor's aggregate status can be checked from its own
envelope.  No endpoint, expected result, response, or display text is repeated
in the edge-result list.

A measurement cell is exactly one TV value allowed by that path schema.

For a subject trial, the measurement-cell list has exactly one cell for every
effective measurement-registry path in ascending unsigned path-text order;
position supplies the path, so path text and ordinal are not repeated.  An
unavailable value is tag `09`, and an unsupported value is tag `0a`; neither
is zero.  Every LAB-only row has no measurement cells; its deterministic
fixture values remain in S1 and are not repeated as observations.
Outside cause-specific stop completion, a tag-`09` value must equal the unique
section-12 derived `inherited_measurement_status_constructor` output for that exact path,
and a tag-`0a` value must equal that constructor's unsupported output.  The
inherited status policy must
admit the selected tag.  During stop completion, an unaccepted path whose
policy admits tag `09` instead uses the cause-selected
`stopped_before_capture_map` value; an already accepted cell is never
rewritten.  A `NATIVE_ONLY` path admits neither tag and is governed by the
atomic submission rule in section 5.4.  Thus a status text valid at one path is
not an allowlist entry for another path.
For every row where the identity paths apply,
`identity.contract_profile="R01C"` and `identity.run_id` is the section-5.3
run ID.  The inherited 1,040-path registry has no `identity.trial_id` path;
trial identity is rebuilt from envelope position and is not invented as a
measurement cell.

The thirteen subject `NATIVE_ONLY` cells use this exact total resolver; `d0`
is the selected subject descriptor and
`effective_measurement_registry_bytes` is canonical JSON after applying the
section-12 delta to the exact inherited registry:

```text
human_cognition.no_inference_from_loc_alone = true
identity.backend = d0.backend
identity.breaker_object_sha256 =
  "99f81a9a4d4f4bf55109a9f43b7cd361c887c9b0b7255a22d009767238e79dfa"
identity.contract_profile = "R01C"
identity.descriptor_stream_sha256 =
  "e20460d1ba30f1e91e274ee7670aa009bb1d2c37def6e8a6f31d067995198f12"
identity.implementation_bundle_sha256 = lowercase_hex_64(A_real)
identity.literal_oracle_sha256 =
  "68139147030cfa67a381b45910b87f04b74f351b131aa8f9cef5e69ee6f63b32"
identity.manifest = d0.mechanism_manifest
identity.measurement_registry_sha256 =
  lowercase_hex_64(SHA256(effective_measurement_registry_bytes))
identity.run_id = run_id
identity.schema_id = "R01C-MEASUREMENT-PATHS-1"
identity.suite_digest =
  "996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6"
runtime.timing_is_measurement_only = true
```

The three inherited-file digests above identify exact S_C semantic members;
they are not recomputed from ambient paths.  A missing descriptor member or
failed effective-registry construction prevents submission rather than
creating an alternate native value.

### 4.2 B observation and process observation

`b_observation` has exactly one of these closed shapes:

```text
{}

{history: nested `BH_value` event list}

{observed_prefix: list(B events),
 unknown: structured-unknown tag 09}
```

The empty map means no B history and is legal only for `LAB_ONLY` or execution
that ended before B.  A `history` must be exactly a section-2 `BH_value`.  An incomplete list
must be a strict prefix of one legal `BH_value` production and cannot support a
`B_response`, `MATCH`, or `DIFFER` result.
The three disjoint key sets determine the variant; repeating a `kind` field is
forbidden.  `observed_prefix` is legal only under one of the three run-stop execution codes, and
its `unknown` must equal the exact
`stopped_before_capture_map[execution]` pair.

`process_observation` is exactly:

```text
{
  terminal: text from the inherited terminal registry | structured-unknown tag 09,
  wait_order: text from the inherited wait-order registry | structured-unknown tag 09
}
```

Terminal and wait facts are actual observations.  The expected values remain
only in S1.  A tag-`09` value is required when an apparatus failure prevents
the named observation; it must equal
`stopped_before_capture_map[execution]`, the enclosing execution must be one of
the three stop codes, and a free-form `UNKNOWN` text is not legal.

A checkpoint observation is exactly `bytes(exactly 40 bytes)`.  Checkpoint
observations occur in observed chronological order and are validated by
section 8.  Their rebuilt locator lists must each contain at least one range,
and every range must select the same exact frame bytes from its retained raw
target; disagreement is invalid.

### 4.3 Exact trial record

`canonical_records` is exactly the following seven-member map:

```text
{
  b_observation: one section-4.2 value,
  checkpoint_observations: list(bytes(exactly 40 bytes)),
  comparison_edge_results: list(enum namespace 5),
  constituent_checks: list(constituent_check),
  measurements: list(measurement_cell),
  operation_facts: list(operation_fact),
  process_observation: section-4.2 map
}
```

The envelope's physical position after PREFLIGHT selects the effective S1
ordinal and trial ID; frame zero selects the run.  Those values and the fixed
record schema ID are therefore not repeated inside the record.  The existence
of the envelope is the submission-occurrence fact.  Its position, effective S1
row, and three run identifiers regenerate the exact four-member launch overlay.
A wrong or otherwise noncanonical submitted byte string is a failed launch
observation, not an admitted trial record, and must be retained in its bounded
raw failure carrier if this profile is later extended to claim it.

For a subject record, operation facts contain exactly ten entries and
measurements contain the complete 1,040-path list.  Every LAB record has empty
operation and measurement lists: its deterministic semantic inputs remain in
the selected S1 descriptor and its actual pass/failure survives in constituent
checks rather than being copied as observations.  Check and incident-edge list
lengths and positions must equal, not merely be subsets of, the effective S1
registries for the selected descriptor.  Missing, extra, duplicate, or
out-of-order material is `CANONICAL_RECORD_SCHEMA_MISMATCH`.

The ABSENT/REJECT witness is closed directly: a complete record containing
event payload `bytes(00)` derives `B_response` ending in `00`; replacing only
that payload with `bytes(01)` changes both the trial-record bytes and derived
response.  No decoder choice remains.

## 5. Exact raw packs and one shared inventory crossing

The per-descriptor R0.1B inventory rule is infeasible under its own run bound:
the frozen semantic inputs alone exceed 51 MB, and copying them into 3,028
subject envelopes would exceed 2 GiB.  Hash-only references would instead
delete bytes required by exact replay.  This section is therefore an
**R01C REPLACEMENT** for the R0.1B L-envelope/inventory packaging rule.

### 5.1 Raw packs remain per trial

Both `raw_trace_pack` and `raw_measurement_pack` are nested TV lists of exact
raw-stream maps:

```text
{
  bytes: bytes(exact accepted stream content),
  missing_suffix: list(structured-unknown tag 09)
}
```

Each pack contains exactly one entry for every source declared for that pack
whose exact `active_trial_ids` contains the selected row, and no entry for an
inactive source.  Entries occur in the unsigned-`stream_id` order of those
filtered manifest declarations; pack plus position therefore derives the
stream ID, which is not repeated in the entry.  A configured active source with
no observed byte is present with empty `bytes`; it is
complete only after its source-binding branch's section-5.2 terminal rule was
observed.  A
`COMPLETE` entry has an empty `missing_suffix`; a `PREFIX_ONLY` entry has
exactly one structured unknown naming the absent suffix and needed evidence.
The zero/one list cardinality is the one surviving completion bit; repeating
it as a namespace-9 `completeness` enum is forbidden.  The names `COMPLETE` and
`PREFIX_ONLY` below denote these two list shapes.
Thus configured-empty active, retained-empty-prefix, inactive, and undeclared
are distinct using the entry shape plus the manifest declaration.
The unknown is not author-selected: section 12's derived total
`raw_suffix_map` maps the
immutable execution stop code to one exact direct reason/needed-evidence pair;
the enclosing pack and position already supply pack name and `stream_id` and do
not select different text.  An unmapped cause or
alternate registered text is invalid.
A `PREFIX_ONLY` entry therefore requires the envelope execution to be one of
those three stop codes; an otherwise-complete run with a silently partial raw
source is invalid.

Channel provenance, EOF/loss facts, concurrent collector order, partial bytes,
diagnostics, timestamps, PIDs, scratch spellings, environment output, and any
producer framing are the exact retained content of separately named streams.
The captured locator parser has the one section-5.2 wire; no private codec name
changes the meaning of completion or locators.  Host iteration order is never
used.

Raw packs are inline in the canonical L-stream wire.  They are never replaced
there by a digest.  After crossing L, a persistent realization may use a
lossless encoding or physical deduplication only if the exact canonical stream
reconstructs byte-for-byte and the codec, version, dictionary, availability,
compute, operations, and TCB are inventoried and charged.  Lossy compression,
hash-only retention, or an unaccounted external service is invalid.

For a completed parser pass, every normalized leaf's locator list is the
all-and-only list of source spans reported by its gate-R-selected deterministic
parser.  Spans are half-open, minimal for that parser, sorted by section 10,
and adjacent spans in the same source are coalesced.  A checkpoint span is
exactly its 40 frame bytes.  A parser that can report two span sets chooses the
lexicographically smaller locator tuple list.  Supersets, omitted consumed
bytes, and implementation read-chunk boundaries are invalid.  The sole
parser-stop exception is closed in section 5.2; it does not authorize an
implementation to choose locators.  This rule makes locator views
rebuildable rather than author-selected evidence decoration.

### 5.2 Realization manifest member

A gate-R member has exactly this shape:

```text
{
  bytes: bytes(exact member bytes),
  mode: U64(exact st_mode & 07777),
  path: text,
}
```

`path` is nonempty printable ASCII, uses `/` only as a separator, has no empty,
`.` or `..` component, no leading or trailing `/`, no `\`, and is unique.
Every member is one captured package/loaded-file observation.  The four fixed
unknown slots and every dynamic slot are derived from section 12 plus the captured
external-slot configuration under the exact procedure below; neither their
paths nor their direct pairs are repeated in `members`.  R0.1C
intentionally has no persisted role
label: deleting such a label changes no admitted execution or replay result,
while retaining it creates an unconstrained authoring choice.  Executable
selection is an observed loaded-file fact enforced against `members`.  The
five closed protocol roles below need manifest fields of their own because
swapping two captured executables while retaining the same member set can
change a permitted continuation.  Adding an unused
executable subset would change `A_real` without changing admitted behavior and
is therefore forbidden.  `mode` preserves the permission bits that can change whether a
captured file is usable; timestamps, ownership display names, and directory
iteration order are not members of this reported software realization.

The realization manifest value is exactly:

```text
{
  attack_validator: text(member path),
  locator_parser: text(member path),
  members: list(gate-R member),
  process_supervisor: text(member path),
  retained_stream_provider: text(member path),
  raw_streams: list({
    active_trial_ids: nonempty list(text),
    pack: text("RAW_MEASUREMENT") | text("RAW_TRACE"),
    producer_path: text,
    source_binding: {producer_fd: U64} |
                    {relative_path: text} |
                    {fixture_output: nonempty printable-ASCII text,
                     fixture_recipe: text},
    stream_id: nonempty printable-ASCII text
  }),
  replay_process: text(member path)
}
```

Members sort by unsigned path bytes.  Each of
`attack_validator`, `locator_parser`, `process_supervisor`, and `replay_process`
and `retained_stream_provider` names one member whose mode has
an execute bit.  Two or more may name the same
member only when it implements every named closed protocol; the inventory
still charges its bytes once.  The role key and S_C select the protocol, so a
one-member wrapper or a repeated fixed protocol literal would add no
realization distinction.  The
manifest includes every publisher, recovery, adapter, controller, trace,
normalizer, serializer, replay, verifier, schema validator, configuration,
test, runtime entry point, direct/transitive dependency, and S/R gate-machinery
byte that the closed package procedure reports.  Every actually loaded regular
file must occur in `members`; an unlisted loaded member fails gate R.  Derived
unknown slots limit claims and never mean zero bytes or a captured member.

Free-form choices do not determine unknown entries.  The identifier
`R01C-PACKAGE-AND-LOADED-BYTES-1` denotes this exact procedure, rather than an
uninterpreted plugin name: Gate R receives one already-open package-root
directory descriptor; it walks
components by unsigned raw ASCII name with `lstat` and without following
links; accepts only directories and single-link regular files; rejects a
symlink, hard link, device, socket, FIFO, non-ASCII name, or path-rule
violation; reads each regular file through that root descriptor; and requires
byte length, bytes, and `(st_mode & 07777)` to be unchanged across a stat/read/
stat sequence.  The all-and-only regular-file results, sorted by relative path,
must equal `members`.  The packaged launcher and loaded-file
monitor are themselves captured members.  During preflight probes and the
run, any executed, opened, or mapped regular file outside this captured set,
or any member whose bytes/mode changes, invalidates R_C for that evidence; it
is not patched into the manifest afterward.

The same procedure derives a query view containing the fixed `unknown/runtime`,
`unknown/os-kernel`, `unknown/hypervisor`, and `unknown/firmware` slots plus the
registered dynamic `unknown/external-service/*` and
`unknown/physical-component/*` slots fixed in section 12.  Each resulting slot
fixes its path and the exact direct
`{reason,needed_evidence}` pair in section 12; an operator cannot choose
alternate wording, and there is no behaviorless numeric alias to renumber.
Registered external-service and physical-component
suffixes are exact sorted values parsed from the section-12-named captured
configuration member.  If present, its bytes must be exactly
`TV({external_services:list(text), physical_components:list(text)})`; both
lists are unsigned-UTF-8-sorted and unique, and every text is one nonempty
printable-ASCII path component containing neither `/` nor `\` and is not `.`
or `..`.  The two keys map respectively to
`unknown/external-service/<text>` and
`unknown/physical-component/<text>` using the derived direct pairs.  Absence of
that member means both sets are empty.  A different procedure or slot registry
is a different semantic profile.  This is a closed reported-software inventory
rule, not evidence of unobservable physical completeness.

`raw_streams` sorts uniquely by `(pack text bytes, stream_id bytes)`.
`producer_path` must name one captured member or one path in that derived
unknown-slot view.
`active_trial_ids` is a nonempty, unsigned-ID-sorted unique exact subset of the
6,317 effective trial IDs for which that source is active.  A source active for
no row is absent from `raw_streams`; retaining a globally inactive declaration
would add author-selected manifest and empty-pack bytes without observing a
channel.  Thus no named row-domain function can silently classify the same row
two ways.  For every other row a declared source is canonically empty and
`COMPLETE`.  These declarations supply the all-and-only raw source domain used
by section 5.1.

`source_binding` has exactly one of the three displayed closed shapes.  A
`producer_fd` is the producer-process descriptor fixed by the captured
launcher before exec.  A `relative_path` obeys the member path syntax
and resolves beneath the run's gate-R-created scratch-directory descriptor;
absolute paths, links, and resolution outside that descriptor are invalid.  A
`fixture_recipe` must equal the selected LAB row's exact derived-closure
recipe name and `fixture_output` names one unique output of that recipe.
Expand the registry across `active_trial_ids`.  Binding identity is
branch-specific and unique across both packs: a producer-fd key is
`(trial_id, producer_path, producer_fd)`; a `RUN_FILE` key is
`(trial_id, relative_path)` regardless of its `producer_path`; and a
semantic-fixture key is
`(trial_id, fixture_recipe, fixture_output)` regardless of its
`producer_path`.  Thus changing a writer name cannot register the same file or
fixture output twice.  In addition, one accepted byte channel and its one
terminal observation may satisfy only one expanded declaration; a captured
launcher that aliases the same source across binding kinds is invalid.  For a
given trial, the captured launcher must create at most one live producer
instance for a particular `producer_path`; a realization needing two such
instances is unsupported by this profile rather than distinguished by an
author-chosen instance label.  Consequently two stream declarations cannot
duplicate or fan out one observed channel merely by changing stream ID,
producer wording, or binding spelling.  The disjoint keys derive both the
binding discriminator and its sole terminal rule; persisting `kind` or
`terminal_condition` would repeat the same branch bit.  A `producer_fd` branch
completes only after both EOF on the bound captured byte channel and successful
wait/reap of the exact producer.  A `relative_path` branch completes only after
that reap followed by an unchanged length/bytes/mode stat/read/stat of the
bound scratch-relative file.  A fixture branch completes only after acceptance
of the last exact recipe byte and is legal only for a LAB row whose named derived-closure
fixture recipe fixes the content.  A different observation, inferred
silence, timeout, or a parser decision does not complete a stream.

`R01C-CLOSED-PROCESS-SCOPE-1` is the common launch and cleanup protocol for
the locator parser, attack validator, retained-stream provider, replay process,
and every captured producer.  Each invocation starts in a newly empty supervised descendant
scope.  The direct child receives only the protocol-declared descriptors;
every other inherited descriptor is close-on-exec.  Before an invocation is
accepted, every process in that scope has terminated and been reaped, every
stdout/stderr writer has closed, and every request-scoped capability or
retained-stream handle has been revoked.  The sole exception is the provider's
one success handle: it leaves the provider scope only through the transfer
endpoint below, enters the immediately following replay scope exactly once,
and is revoked before the replay outcome is accepted.  A realization that cannot establish
and observe those conditions is `UNSUPPORTED`; a runtime failure to close the
scope leaves only an incomplete boundary prefix and supports no R0.1C result.
The process supervisor, OS facility, handle registry, and cleanup path are
charged TCB.  This rule prevents a reaped direct child from concealing a live
descendant or transferred service handle; it does not prove physical isolation.

`R01C-RETAINED-STREAM-PROVIDER-1` is the closed role selected by
`retained_stream_provider`.  When the post-terminal state machine reaches
acquisition, the supervisor starts that member in one fresh closed scope with
only an input channel and a supervisor-created capability-transfer endpoint.
It writes exactly this request followed by the same-turn EOF transition:

```text
ASCII("ZGR01C-RETAINED-STREAM-REQUEST") || 00 || u16be(1) || TV({
  run_id: text(current run_id),
  source_l_stream_sha256: bytes(exactly 32 bytes)
})
```

The provider has no stdout or stderr descriptor.  Success consists of exactly
one channel capability transferred before transfer-endpoint EOF, direct-child
exit zero, and complete scope cleanup.  No application response byte exists.
The transferred channel is fresh, positioned at offset zero, read-only, and
produces through EOF the exact retained primary L stream selected by the two
request members.  Any explicit launch, request, transfer, exit, or cleanup
failure before that success selects `RETAINED_STREAM_PROVIDER_FAILURE` only
after scope quiescence is proven; failure to establish quiescence follows the
common unsupported/no-completed-outcome rule.  Reaching the
shared replay deadline first selects `PROCESS_TIME_BOUND_EXCEEDED`.  Neither
case creates a replay-process exit record.  The success handle is passed only
to the replay process on its protocol-declared retained-input descriptor and
is revoked before an outcome crosses L; the replay process validates the full
scan and whole-stream hash.  The selected provider member, capability-transfer
mechanism, run-store binding/creation code, access-control configuration,
handle registry, and dependencies are captured manifest members.  Moving any
of them to an ambient service or operator choice is EXTERNALIZE.  This byte-and-
capability contract permits unlike file, database, or content-addressed
realizations but does not establish their physical independence.

`R01C-LOCATOR-PARSER-TV-1` is also a closed execution protocol.  The exact
locatable observation addresses are the `b_observation` root, each checkpoint
byte value, each constituent check, each measurement value, each operation
fact, and the `process_observation` root.  Edge-result enums have no locator
view.  For every locatable address, the independent validator starts the
captured parser member in a fresh process and writes exactly this single value
followed by input EOF:

```text
ASCII("ZGR01C-LOCATOR-REQUEST") || 00 || u16be(1) || TV({
  leaf_address: list({map_key: text} | {list_index: U64}),
  active_stream_ids: {
    RAW_MEASUREMENT: list(text),
    RAW_TRACE: list(text)
  },
  canonical_record: section-4.3 nested map,
  raw_measurement_pack: section-5.1 nested list,
  raw_trace_pack: section-5.1 nested list
})
```

Each `active_stream_ids` list is the unsigned-stream-ID projection of the
manifest declarations for that pack whose active-ID list contains this trial;
it is derived for the request and is not persisted in the envelope.

`leaf_address` traverses from the `canonical_records` root and every step has
exactly one displayed member.  The only legal standard output, followed by
output EOF and exit status zero, is:

```text
ASCII("ZGR01C-LOCATOR-RESPONSE") || 00 || u16be(1) ||
TV(list(raw_locator))
```

Parser standard error must be empty.  A diagnostic byte, nonzero exit, or
missing EOF makes the parser invocation an apparatus failure and cannot be
inserted into a raw pack that was itself parser input.  Such a byte remains an
internal failed-gate diagnostic unless a later, separately specified boundary
crossing admits it; R0.1C makes no result claim from it.  Two isolated
invocations must return identical bytes, and the returned list must satisfy
bounds, source activity, selected-target equality, and section-10 order.  An
accepted envelope is the occurrence fact that both pre-finalization invocations
agreed for every locatable address.  Their derived bytes are not copied into
the envelope; a later locator query reruns this same total function from the
retained record/raw inputs and must reproduce them byte-for-byte.
Crash, trailing output, undeclared input, nondeterminism, or disagreement is a
parser failure, not verifier discretion.  The parser code, launcher, runtime,
and this protocol remain charged TCB; exact code identity does not prove its
semantic adequacy or physical independence.  The parser runs only on a
candidate observation before its envelope is finalized.  Locatable fields are
visited depth-first in TV map-key order and list-index order; each successful
response is accepted atomically.  A parser failure fixes
`APPARATUS_FAILURE` and switches once to the section-5.4 cause-specific stop
completion.  The candidate logical observation was not accepted and is
treated, with every later field, by the ordinary STOP_A rule; previously
accepted observations survive unchanged and their locator views remain
rebuildable.  No
locator-specific tag, check selector, or diagnostic crosses L.  Parser failure
versus another internal apparatus failure therefore creates no additional
contract-permitted boundary distinction, and the stop record is not
recursively submitted to the parser.

The realization manifest value, inventory blob, `A_real`, realization ID,
run ID, preflight requests/responses/outcomes, and derived gate/closure/
replay-index/replay-exchange outputs are expressly
excluded from `members`, avoiding self-membership.  Their builders, validators,
schemas, configuration sources, and runtime dependencies are included.
Semantic members from section 5.3 are also not duplicated in `members`; their
co-location in the inventory blob and the enclosing S_C/R_C validation context
bind the selection.  Repeating a fixed manifest schema ID or the final semantic
ID here would add no choice and is forbidden.
All excluded outputs and semantic-member files must reside outside the
package-root descriptor walked by Gate R.  No path is skipped by name: a
semantic-member path inside that root, a later output created there, or any
write that changes the walked tree is a gate failure.  The monitor holds the
root descriptor and rejects creation, deletion, renaming, linking, or change
to captured bytes or `(st_mode & 07777)` beneath it through the end of the run.
Thus the all-regular-files walk
and the no-duplication rule cannot choose different answers, and no open
`self_excluded_outputs` list exists.

### 5.3 Inventory blob

A semantic member is exactly
`{bytes: bytes(exact file bytes), path: text}` with the same path restrictions.
The inventory blob value is exactly:

```text
{
  realization_manifest: the nested section-5.2 manifest value,
  run_nonce: bytes(exactly 32 bytes),
  semantic_members: list(semantic member)
}
```

`semantic_members` has exactly seventeen paths: the twelve inherited R0.1B S0
member paths, `R01B-S1.json`, and the four S_C0 delta-member paths in section
12.  It is sorted by path and contains each path and byte string once.  The
derived `R01C-S1.json` validation projection, generated S0/S1 manifest bytes,
manifest indexes, hashes, and closure records are rebuilt and are not repeated
as semantic members.  The list nevertheless reconstructs and verifies the
complete inherited and delta semantic gate.  Consequently the roughly 51 MB
base closure crosses L once, not once per descriptor or again inside the
realization manifest.

`run_nonce` is supplied before the inventory blob is packaged.  The exact
semantic ID is rebuilt from `semantic_members`, and the exact realization ID
from `realization_manifest`; neither fixed/derived ID nor an inventory schema
ID is repeated in the blob.  The evidence store rejects reuse of the same
`(derived semantic ID, derived realization ID, run_nonce)` tuple.  This is a selection
and uniqueness responsibility, not free entropy or proof of global
uniqueness; its generator, store, and failure behavior are charged.

Let `R_manifest_bytes = TV(realization_manifest)` and
`inventory_blob_bytes = TV(inventory_blob)`.  Define:

```text
A_real = SHA256(ASCII("ZERO-GROUND-R01C-A-REAL") || 00 ||
                u64be(length(R_manifest_bytes)) || R_manifest_bytes)

realization_id = ASCII("r01c-realization-") || lowercase_hex_64(A_real)

inventory_blob_id = SHA256(ASCII("ZERO-GROUND-R01C-INVENTORY-BLOB") || 00 ||
                           u64be(length(inventory_blob_bytes)) ||
                           inventory_blob_bytes)

run_id = ASCII("r01c-run-") || lowercase_hex_64(
           SHA256(ASCII("ZERO-GROUND-R01C-RUN") || 00 ||
                  inventory_blob_id))
```

This resolves the `xy` versus framed-manifest witness: neither `78 79` nor an
R0 guessed file frame is the preimage.  `A_real` identifies the reported
software manifest, not unavailable physical bytes or physical independence.

No envelope repeats an inventory reference or run ID.  Its physical position
in the one stream after frame zero supplies that association; the submitted
launch overlay contains the derived `run_id`.  From the stream bytes the
inventory blob ID, length, run ID, and frame ordinal are mechanically rebuilt.
Persisting the former four-member
`inventory_pack` in every envelope would therefore add no distinction.  A
verifier must still reconstruct and validate the complete inventory frame as
the first frame of that L stream.  A persistent encoding may retain its exact
constituent facts and regenerate the canonical bytes, but an external blob
locator, matching hash without reconstructible targets, blob from another
stream, or partial target cannot satisfy it.

### 5.4 One retained L stream

The complete successful R0.1C L stream is:

```text
ASCII("ZGR01C-L-STREAM") || 00 || u16be(1) || frame*

frame = u8(kind) || u64be(payload_length) || payload
```

The only frame kinds are `01 INVENTORY`, `02 ENVELOPE`, `03 PREFLIGHT`, and
`ff TERMINAL`.  Every closed stream has exactly one `INVENTORY` frame first,
exactly one compact section-9 `PREFLIGHT` frame second, zero or more
`ENVELOPE` frames in effective trial-ordinal order, and exactly one `TERMINAL`
frame last, with no trailing byte.  A successful preflight variant may be
followed by envelopes; a failure variant must be followed immediately by a
cause-matched stop terminal with `submitted_stop=false`, zero envelopes, and
all 6,317 IDs unrun.  The
preflight frame is run evidence, never a descriptor envelope.  There is
deliberately no persisted INDEX frame: a linear scan reconstructs the logical
replay index, so persisting it would add navigation state without preserving
another history distinction.  Frame ordinal counts from zero, so inventory is
ordinal zero and preflight is ordinal one.  Inventory payload is exactly
`inventory_blob_bytes`.  A successful preflight payload is exactly zero bytes;
a failure payload is the one nonempty section-9 TV map.  No empty TV value or
success enum substitutes for the zero-byte payload.
No subject or ordinary LAB process may start until frame zero and the success
preflight frame have crossed L and fit the retained evidence budget.
For a complete 6,317-envelope run, ENVELOPE frames have physical ordinals 2
through 6,318, the source envelope is ordinal 6,318, and TERMINAL is ordinal
6,319.  A preflight-failure stream has ordinals zero, one, and two only.  These
are derived checks, not stored selector fields; any later stopped run derives
its shorter physical sequence from the same scan.
Every descriptor actually submitted to L yields exactly one envelope frame;
an ID listed as unrun was never submitted and has no synthetic envelope.

Submission is one atomic controller transition before subject/LAB launch.  It
validates the descriptor and launch overlay and materializes every applicable
measurement cell whose inherited status policy is `NATIVE_ONLY` from the
already fixed S_C, R_C, run, and descriptor values.  A subject row gets all
thirteen section-4.1 values; a LAB row has no applicable measurement cells.
If any applicable value
cannot be derived, the transition does not occur: the row remains unsubmitted,
the apparatus takes the cause-specific prelaunch branch, and no envelope is
invented.  After submission, even an otherwise empty capture prefix contains
these native cells.  This materialization reports derived identity/constants,
not a fabricated subject observation, and its compiler, validation, storage,
and TCB costs remain charged.  This atomic transition is the submission
occurrence used by the envelope/unrun and closure rules; there is no earlier
half-submitted state.

Trials execute in effective ordinal order after the successful PREFLIGHT frame.  Their raw bytes
and actual B crossings are staged in the bounded apparatus, but envelope
frames are finalized and cross L only after all comparison partners have
finished or a run stop has been fixed.  They are then emitted in ordinal
order.  This makes each edge/check aggregate final rather than stale and
removes the emit-now/defer ambiguity from F8.  Staged bytes count against the
same evidence limit.  An apparatus crash before they cross L leaves only the
exact already-crossed prefix; its terminal state and lost internal bytes are
unsupported rather than represented as a completed capture failure;
the batching latency, memory/storage, and recovery mechanism are charged.

An envelope payload is exactly:

```text
ASCII("ZGR01C-ENVELOPE") || 00 || u16be(1) || TV({
  canonical_records: section-4.3 nested map,
  raw_measurement_pack: section-5.1 nested list,
  raw_trace_pack: section-5.1 nested list
})
```

The deterministically rebuilt `replay_index_value` logical view is exactly
this nested TV map value:

```text
{
  entries: list({
    envelope_frame_ordinal: U64,
    envelope_length: U64,
    envelope_offset: U64,
    envelope_sha256: bytes(exactly 32 bytes),
    ordinal: U64,
    trial_id: text
  }),
  inventory_blob_id: bytes(exactly 32 bytes),
  run_id: text(run_id)
}
```

The `REPLAY_INDEX` selector and current contract supply the view schema, so a
fixed schema-ID member would be mechanically constant and is forbidden.
Define `replay_index_bytes = TV(replay_index_value)`.  The names are distinct:
the map is used for validation, while byte-range selectors address its one
encoding.  A tag-03 wrapper or a second `TV` encoding is invalid.

`envelope_offset` addresses the first envelope-payload byte in the complete L
stream.
`envelope_length` is exactly that payload's length and `envelope_sha256`
hashes exactly those payload bytes; neither covers the one-byte kind or
eight-byte frame length.
Entries are produced by one forward scan, are in ascending ordinal order,
match the effective row selected by that envelope position, and contain no
duplicate ID, ordinal, frame
ordinal, or offset.  The scanner validates the single intervening PREFLIGHT
frame and permits envelope entries only after its zero-payload success
variant.  It
includes that frame when counting `envelope_frame_ordinal` and offsets but
creates no replay-index entry for preflight.  `inventory_blob_id` is
recomputed from frame zero.  The
view is not accepted as a substitute for the scanned source stream.  The
terminal payload has exactly one of these shapes:

```text
TV(enum(2,COMPLETE))
TV([enum(2,APPARATUS_FAILURE | TIME_BOUND_EXCEEDED |
           STORAGE_BOUND_EXCEEDED), bool(submitted_stop)])
```

Every other code or shape is invalid.  `submitted_stop=true` means the stop
cause belongs to the final envelope; false means it occurred before submission
of the first unrun row and no envelope receives that execution code.  Without
this bit, the smallest collision is (a) a completed row followed by a prelaunch
failure and (b) the same row suffering a post-observation failure before its
submitted execution closes: both have the same envelope count, unrun suffix,
and cause, but a later per-row execution query distinguishes them.  The cause
and this association bit are the only terminal values not fixed by the prefix.
A scan derives envelope count
(PREFLIGHT is not counted), run ID from frame zero, and the unsigned-ID-sorted
unrun suffix from the effective registry and submitted envelope prefix.  It
also derives empty reason/evidence lists for COMPLETE; for a stop it derives
failure reason `[EVIDENCE_UNAVAILABLE]` and the one needed-evidence text from
`stopped_before_capture_map[c]`.  These generated fields may appear in query
views but do not cross again in TERMINAL.
A bounded
apparatus stop emits an envelope for the attempted row with the exact accepted
prefix and applicable failure status before the terminal frame.  If the
apparatus cannot emit those frames, the exact retained prefix remains bytes
that crossed L, but terminal state, recoverability, and permanent-failure
claims are `UNSUPPORTED`; it is not a complete replay corpus and supports no
conformance claim.

A replay selector is exactly one of these three shapes:

```text
# canonical row payload
{
  length: U64,
  offset: U64,
  run_id: text(run_id),
  stream: text("CANONICAL_RECORDS"),
  trial_id: text
}

# raw row/source payload
{
  length: U64,
  offset: U64,
  run_id: text(run_id),
  stream: text("RAW_MEASUREMENT") | text("RAW_TRACE"),
  stream_id: nonempty printable-ASCII text,
  trial_id: text
}

# run-scoped singleton payload
{
  length: U64,
  offset: U64,
  run_id: text(run_id),
  stream: text("APPARATUS_FAILURES") | text("INVENTORY") |
          text("REPLAY_INDEX")
}
```

For `CANONICAL_RECORDS`, offsets address `TV(canonical_records)` and
the trial ID must resolve through the scan-rebuilt entry; its global ordinal
derives from that unique row.  For
`INVENTORY`, offsets address `inventory_blob_bytes`.  For raw packs, offsets
address the named unwrapped stream content and the row ID, rebuilt
entry, and stream ID must all agree.  Range bounds must agree.  The range hash
is rebuilt from the exact selected bytes rather than repeated in the selector;
exact bytes, not their digest, are returned in a fresh process.

For `REPLAY_INDEX`, offsets address `replay_index_bytes` rebuilt above; for
`APPARATUS_FAILURES`, they address `apparatus_failures_bytes` defined below.
All three singleton selectors are run-scoped and remain legal even when a stop
before row zero produced no envelope.  Thus all six required logical evidence
stream names have a legal replay address without an irrelevant row anchor or
private/local ordinal.

The R0.1C measurement-registry delta maps its six required logical evidence
stream names to three singleton views and three keyed families without
duplicating source bytes:

```text
inventory_pack       = singleton inventory_blob_bytes
replay_index          = singleton replay_index_bytes
canonical_records     = keyed family trial_id -> TV(canonical_records)
raw_measurement_pack  = keyed family (trial_id, stream_id) -> raw content bytes
raw_trace_pack        = keyed family (trial_id, stream_id) -> raw content bytes
apparatus_failures    = singleton apparatus_failures_bytes
```

Here `inventory_pack` is the inherited logical evidence-stream name, not a
member of each envelope.  A selector addresses exactly one family member, so
offset zero means that member's first byte rather than the tag of an invented
aggregate list.  Logical-byte/storage metrics for a family sum its members in
scan order but do not create another replayable byte stream.

An `apparatus_failure_view` entry is exactly:

```text
{
  envelope_frame_ordinal: list(U64) of length zero or one,
  execution: enum namespace 2,
  failure_reasons: list(enum namespace 7),
  needed_evidence: list(text),
  selector: list({trial_id: text}) of length zero or one
}
```

It contains one entry for every envelope whose execution is apparatus, time,
or storage failure, plus one selectorless entry when the terminal
enum is not `COMPLETE`; envelope entries precede the terminal entry
and otherwise follow frame order.  Empty lists, not sentinel IDs, express run
scope.  An envelope entry uses `execution`, `failure_reasons`, and
`needed_evidence` exactly from that envelope's derived status view; its frame ordinal
and selector are scan-derived.  The terminal entry uses the parsed terminal cause,
`[EVIDENCE_UNAVAILABLE]`, and the exact cause-selected completion evidence
defined above, with empty selector/frame lists.  It never substitutes terminal
cause text for a more specific envelope status.  Define
`apparatus_failures_value` as the TV list value of those entries
and `apparatus_failures_bytes = TV(apparatus_failures_value)`; no tag-03 wrapper
or double encoding is legal.  The three singleton values, three keyed families,
and `identity.run_id` are deterministic rebuilds from the retained stream.
Their scanner, construction cost, and TCB remain charged.

The inherited 2 GiB total limit remains, but the inherited fixed 1 MiB
terminal reserve is an **R01C REPLACEMENT** and is forbidden.  Before frame
zero, S_C bounds every reason, needed-evidence value, unknown code/text
mapping, and schema-required cardinality, while the already frozen R_C
manifest fixes the realization-specific member paths, stream IDs, source
count, and framing.  Native measurement strings and collections may be
contractually unbounded; the apparatus therefore reserves a deterministic
completion, not a nonexistent largest native value.

Let `C = {APPARATUS_FAILURE, TIME_BOUND_EXCEEDED,
STORAGE_BOUND_EXCEEDED}` and `X = C union {COMPLETE}`.  For registry size `N`,
submitted-row count `k`, exact staged state `q` of all submitted ordinals below
`k` whose envelopes have not crossed L, current-row capture phase/prefix `p`,
and immutable stop cause `c in C`, define:

```text
complete_tail(N) = exact TERMINAL frame carrying TV(enum(2,COMPLETE)); empty
                   unrun/reason/evidence query fields derive from N, frame
                   zero, and S1

stop_tail(k,c,b) = exact TERMINAL frame carrying TV([enum(2,c),bool(b)]);
                   remaining IDs, count, run ID, execution association, and
                   reason/evidence query fields derive from k, b, frame zero,
                   S1, and c

pending_frames(k,q,c) = exact ordered ENVELOPE frames that finalize every row
                        represented by q, preserving every accepted fact and
                        completing every still-unresolved edge/check/status
                        under the inherited aggregation and c-selected
                        registered unknowns

stop_frames(k,q,p,c) = pending_frames(k,q,c) followed by the exact ENVELOPE
                       frame closing submitted row k from p; every
                       not-yet-accepted fact, and every not-yet-accepted
                       measurement whose path policy admits tag 09, uses the
                       exact `stopped_before_capture_map[c]` unknown; every
                       NATIVE_ONLY measurement retains its atomically
                       materialized native value,
                       every active not-yet-complete raw source is PREFIX_ONLY,
                       every inactive source is absent, and no locator
                       exists without retained target bytes

prelaunch_stop_projection(k,q,c) = already-crossed primary-L prefix followed
                                   by pending_frames(k,q,c) and
                                   stop_tail(k,c,false)

submitted_stop_projection(k,q,p,c) = already-crossed primary-L prefix followed
                                     by stop_frames(k,q,p,c) and
                                     stop_tail(k+1,c,true),
                                     for 0 <= k < N

prelaunch_closure_bound(k,q) = max over c in C of
                               length(prelaunch_stop_projection(k,q,c))

submitted_closure_bound(k,q,p) = max over c in C of
                                 length(submitted_stop_projection(k,q,p,c))
```

Here `k` counts rows already submitted before row k, so the stop envelope makes
the indexed submitted count `k+1`; row k can never be both enveloped and listed
unrun.  `q` contains the exact accepted canonical/raw components, completed
execution facts, and unresolved partner dependencies for every pending prior
row; an already emitted row is absent.  A completed prior row is not relabeled
as a failed execution merely because a later partner is unrun, but its
unresolved edge and consequent aggregate are completed with the exact
registered unknown/evidence selected by the stop rule.  Thus the minimum
two-row witness in which row A waits for row B is included in
`prelaunch_stop_projection(1,q,c)` before B can be listed unrun.

The prelaunch projection is the distinct branch in which row k has not been
submitted and therefore has no envelope.  Cause is never inferred from
`(k,q,p)`: each cause selects its own execution enum, reason/evidence lists,
and raw-suffix unknown through the section-12 derived maps.  The serializer enumerates the finite schema
capture phases and prefix positions before launch.  Bytes of already accepted
native values are charged at their actual encoded length; in every projection
their staged logical components are replaced by, not added to, their one
serialized envelope.  TV widths, fixed IDs, finite required field sets, and
bounded completion texts make each cause-specific projection exact even when a
future native value has no semantic maximum.  A fixed 1 MiB value is neither
the representation nor the rule: it over-reserves either exact terminal shape.
The registered old-reserve control freezes both unequal symbolic evaluations,
`stop_tail(0,c,false)` and `complete_tail(N)`, and rejects replacing either by
the constant; it no longer relies on the deleted persisted-index lower bound.

`complete_tail(N)` is the only legal use of `COMPLETE`; its derived unrun,
reason, and evidence lists are empty.  A stop-cause tail is legal for any
`0 <= k <= N`; its scan-derived query fields use fixed
`[EVIDENCE_UNAVAILABLE]` plus that cause pair's `needed_evidence`.

The total limit charges frame zero once, the PREFLIGHT header plus its actual
zero-byte-success or bounded-failure payload once, every
staged/emitted envelope and raw byte, all frame headers, the post-stream reserve in section 5.5 when
applicable, and the applicable closure.  Before the first row, both
`prelaunch_closure_bound(0,empty)` and the submitted-empty-nonderivable-prefix
bound, including all applicable native-only cells, must fit;
the two alternative projections are not added together.  Otherwise no subject
or LAB row starts.  Before every later launch, the controller constructs and
checks the exact no-submit projection, including all of `q`, and the exact
submitted empty-nonderivable-prefix projections.  Before every atomic value/byte acceptance
it serializes the exact prospective whole staged state and requires every
cause-specific submitted projection to fit.  Comparing the complete projected
byte length, rather than adding a full envelope to already charged staged
components, enforces the replacement accounting above.  It tests in this exact
order: an already observed apparatus failure; monotonic time at or beyond the
deadline; then that projected storage total.  The first matching cause becomes
immutable, so simultaneous pressure resolves `APPARATUS_FAILURE >
TIME_BOUND_EXCEEDED > STORAGE_BOUND_EXCEEDED`.  A byte that would violate the
projection is not accepted; the already accepted prefix is emitted as
`PREFIX_ONLY`.  Serialization and cleanup may finish after the time decision,
as in R0.1B.

Failure to emit the precharged stop envelope or terminal is itself an
apparatus failure and supports no conformance claim.  A derived index can
improve later navigation but adds compute, code, validation, operator concepts,
and TCB; it is rebuilt only when requested and none of that cost is scored as
free.

### 5.5 Mandatory post-terminal replay continuation

The primary L stream is immutable when its `TERMINAL` frame crosses L.  No
row is allowed to claim replay of that retained stream while its bytes are
only staged.  A completed primary stream instead requires exactly one later
request/outcome exchange, outside that stream, after the producer and all
inherited file descriptors and memory have exited.  After the request below
crosses L and provider acquisition succeeds, the manifest-selected process
supervisor launches the member selected directly by `replay_process` in a
fresh closed scope.  That process receives only the request bytes and the one
request-scoped, revocable byte-channel handle returned by the manifest-selected
`R01C-RETAINED-STREAM-PROVIDER-1` role.  It
must reopen the completed stream selected by `run_id`, validate frame zero,
the single successful PREFLIGHT frame, every envelope, TERMINAL, the
scan-rebuilt replay index, and the hash of the whole stream, then answer from
that reopened byte source.  PREFLIGHT affects physical frame ordinals and the
whole-stream hash but is skipped as a non-row frame by the derived-index entry
builder.
`R01C-REPLAY-PROCESS-TV-1` denotes exactly this request, provider-handle access,
validation, response, stderr, and closed-scope behavior; it is not an
implementation-chosen plugin name.

The request crossing is exactly:

```text
ASCII("ZGR01C-REPLAY-REQUEST") || 00 || u16be(1) || TV({
  selector: section-5.4 nested replay selector,
  source_l_stream_sha256: bytes(exactly 32 bytes)
})
```

It is one EOF-delimited request channel.  The response below is a distinct
process channel; concatenating them or treating their boundary as an ambient
message convention is invalid.  The complete request first crosses L and is
retained.  The supervisor then writes the identical bytes to the fresh process
and counts the exact prefix successfully written.  When the last request byte
is accepted, the supervisor must, in that same write turn, close its sole
request-write handle to deliver EOF before any clock, process-exit, failure,
service, or capture poll.  The close result is observed synchronously: failure
fixes `REQUEST_WRITE_FAILURE` with the full byte count; success advances to the
capture state.  No timeout or other post-write state exists between the last
byte and that EOF decision.

The selector is the section-7 source row's actual run ID, trial ID,
`RAW_TRACE`, stream ID `trace`, offset zero, and length 19.  The unique trial
ID derives the global ordinal, so the request does not repeat it.
`source_l_stream_sha256` hashes every byte from the primary
stream magic through the end of its TERMINAL payload.  Define
`request_sha256 = SHA256(exact request-crossing bytes)`.

The only well-formed process response is exactly:

```text
ASCII("ZGR01C-REPLAY-PROCESS-RESPONSE") || 00 || u16be(1) || TV({
  failure_reasons: list(enum namespace 7),
  needed_evidence: list(nonempty text),
  request_sha256: bytes(exactly 32 bytes),
  selected_bytes: list(bytes) of length zero or one,
  source_l_stream_sha256: bytes(exactly 32 bytes),
  status: enum namespace 4
})
```

On `PASS`, both text/reason lists are empty and `selected_bytes` has exactly
one member equal to the selected 19 bytes.  On `FAIL`, `selected_bytes` and
`needed_evidence` are empty and `failure_reasons` is exactly
`[REPLAY_EXACT_BYTES_MISMATCH]`.  On `UNKNOWN` or `UNSUPPORTED`,
`selected_bytes` and `failure_reasons` are empty and `needed_evidence` is
respectively exactly `[POST_STREAM_REPLAY_SOURCE]` or
`[POST_STREAM_REPLAY_CAPABILITY]`.  `NOT_APPLICABLE` is invalid.
`request_sha256` must match the request.  For `PASS` or `FAIL`, the source hash
must equal the fresh process's own whole-stream computation; for `UNKNOWN` or
`UNSUPPORTED` it echoes the requested source hash and earns no source-read
claim.

Let `max_process_response_length` be the greatest exact length of those four
legal response encodings.  Standard output and standard error are distinct
nonblocking channels.  The supervisor accepts at most
`max_process_response_length + 1` bytes from the process; the extra byte is the
bounded witness for overlength.  It retains the exact accepted prefix and
selects `MALFORMED_OR_OVERLONG_RESPONSE` at the end of the capture turn in
which that cap is reached.  It accepts at most one standard-error byte; the
first such byte selects the same outcome at the end of that capture turn and
is retained.  If both conditions occur in one turn, both bounded prefixes are
retained under that one outcome.  Scope termination begins after the turn is
closed.  A valid response requires witnessed empty stderr EOF.
Its separate
`replay_decision_limit` is the inherited
`1,800,000,000,000` monotonic-nanosecond duration, beginning immediately after
the primary TERMINAL's last byte crosses L.  It covers deterministic request
construction and crossing, retained-stream-provider acquisition, process launch,
request write, capture, and the cleanup decision.  At the first observation
at or beyond that duration it fixes `PROCESS_TIME_BOUND_EXCEEDED`, terminates
the scope, and completes cleanup.  Request/outcome serialization may finish
later because its bytes are precharged; failure of the L emitter itself leaves
an unsupported incomplete prefix rather than a fabricated timeout outcome.

Exactly one supervisor outcome then crosses L:

```text
ASCII("ZGR01C-REPLAY-OUTCOME") || 00 || u16be(1) || TV({
  apparatus_outcome: enum namespace 10,
  process_exit: list({kind: text("EXIT") | text("SIGNAL"), number: U64})
                of length zero or one,
  process_response_prefix: bytes,
  process_request_bytes_written: U64,
  process_stderr_prefix: bytes
})
```

It is a second EOF-delimited L channel.  The request and outcome are retained
as one chronological ordered pair; a trailing byte, intervening exchange, or
second outcome is invalid.  A keyed view is rebuilt by hashing the retained
request rather than repeating its hash in the outcome.

`process_request_bytes_written` cannot exceed the request length and selects its exact
prefix.  This exit field concerns only the replay process; it is empty exactly
when no replay process came into existence: service failure, launch failure, or
a replay-time decision before replay launch completed.  Every outcome after a successful launch requires exactly
one truthful direct-child exit-code or signal record, and the supervisor emits
no outcome until the complete scope is quiescent and the retained-stream
capability is revoked.  A valid response and a malformed response observed
after exit zero use `[{kind:"EXIT",number:0}]`;
`PROCESS_EXIT_FAILURE` is selected when a nonzero exit or signal is the first
cause.  A nonzero/signal cleanup record may accompany an earlier immutable
time, cap, stderr, or write cause without changing that earlier outcome.
`process_response_prefix` has length at most
`max_process_response_length + 1` and is the exact accepted raw process output,
not a decoded substitute.  `process_stderr_prefix` is empty for every outcome
except `MALFORMED_OR_OVERLONG_RESPONSE`; for that outcome it has length zero
or one.  Length one records that stderr was accepted in the cause-fixing turn,
including a turn that also reached the stdout cap.

For namespace-10 `VALID_PROCESS_RESPONSE`, the request was written completely,
the process reached stdout and empty-stderr EOF and exit zero before the
deadline, its closed scope and provider handle were cleaned, and its
response prefix is one exact well-formed process response with no trailing
byte.  Its status,
reason/evidence lists, selected bytes, request hash, and source hash are parsed
from that retained prefix and checked against the retained request; none is
repeated in the outcome.  Every other outcome has the derived status
`UNKNOWN`, empty derived failure reasons and selected bytes, and the requested
source hash.  Its derived needed-evidence list is exactly the following
one-member value:

| outcome | exact needed evidence |
|---|---|
| `REQUEST_WRITE_FAILURE` | `POST_STREAM_REPLAY_REQUEST_WRITE` |
| `PROCESS_LAUNCH_FAILURE` | `POST_STREAM_REPLAY_PROCESS_LAUNCH` |
| `PROCESS_TIME_BOUND_EXCEEDED` | `POST_STREAM_REPLAY_TIME_BOUND` |
| `PROCESS_EXIT_FAILURE` | `POST_STREAM_REPLAY_PROCESS_EXIT` |
| `MALFORMED_OR_OVERLONG_RESPONSE` | `POST_STREAM_REPLAY_RESPONSE_BYTES` |
| `RETAINED_STREAM_PROVIDER_FAILURE` | `POST_STREAM_REPLAY_SOURCE` |

Provider/launch failure, and a time decision before writing begins, require
`process_request_bytes_written=0` and empty response/stderr prefixes.  A time decision during
the nonblocking write records its exact prefix length.  Every outcome after a
complete write uses the full request length; only `REQUEST_WRITE_FAILURE` or a
write-phase time decision may use a smaller value, and request-write failure
may equal the full length only when the immediate EOF close failed after all
bytes.  Every non-write-failure outcome with the full count therefore certifies
that request EOF crossed.  No unlisted combination is legal.

The supervisor state machine is exact and nonblocking: construct and cross the
request; acquire the retained-stream handle through the provider; launch the
closed replay scope; write the
request and perform the same-turn EOF transition specified above; then capture
stdout and stderr under their separate caps.
The deadline is polled in every phase.  An explicitly observed service,
launch, or write failure in the same poll precedes the time decision;
otherwise reaching the deadline fixes `PROCESS_TIME_BOUND_EXCEEDED`.  During
capture, one poll call returns one ready-channel bitset; the supervisor does
not reconstruct it by iterating channels.  In each capture turn it drains only
the channels in that bitset, first stdout and then stderr, each in byte order
until EOF, nonblocking would-block, or its cap.  It then closes the turn.  A
stderr byte or stdout-cap arrival in that turn selects the one
`MALFORMED_OR_OVERLONG_RESPONSE` cause and both prefixes accepted in the turn
survive.  That cause precedes the time check; the time check precedes
process-exit classification; nonzero/signal exit precedes parsing; and both
channel EOFs plus exit zero are parsed last as valid or malformed.  This fixed
turn and channel order, not host map/fd iteration order, resolves simultaneous
readiness.  Once any post-launch failure is fixed, the supervisor
terminates the entire scope, drains no more than the two caps, reaps every
descendant, revokes the provider handle, and only then emits the outcome.
The two accepted prefixes freeze at the end of the cause-fixing turn; bytes
drained only for cleanup afterward do not enter either prefix or cross L.
It never rewrites TERMINAL.  A scope or capability that cannot be closed makes
the realization unsupported for this continuation and permits no completed
outcome.

This exchange, not an ordinary consumer descriptor, is the positive future
continuation.  There is deliberately no dedicated positive row or mutable
pre-terminal envelope: the observable distinction requires the query and
answer responsibility, not a constructor in the descriptor ontology.  Only a
`VALID_PROCESS_RESPONSE` whose retained response parses to `PASS` earns exact
retained-stream replay for the completed run.  Every other outcome is retained
replay-failure/unknown evidence, not a subject verdict.
Because this bounded source value is also present in the semantic recipe, a
PASS falsifies wire/address/timing failures but cannot prove that a physical
implementation reread storage instead of recomputing or duplicating the same
bytes.  That physical-provenance claim remains `UNKNOWN`; nonderivable raw
histories supply the persistence witness in section 11, and a future challenge
experiment would be a new semantic profile rather than silently stronger
credit here.

After S_C, R_C, and P_C fix all identifiers and alternatives, define
`post_replay_reserve` as the exact request-crossing length plus the greatest
exact outcome-crossing length over every legal namespace-10 outcome/exit-list/
request-prefix-count combination and a process-response prefix of
`max_process_response_length + 1` bytes plus the one-byte stderr prefix where
each is legal.  This finite enumeration
contains no native measurement value.  The final row may be accepted as
complete only if the exact final projection fits the 2 GiB limit.  That
projection is the already-crossed primary-L prefix followed by every still
pending completed envelope in effective ordinal order, `complete_tail(N)`, and
the post-replay reserve.  As with a stop projection, staged components are
replaced by their envelope serialization rather than added to it.  All
comparison partners have then completed; an unresolved edge makes the final
projection invalid rather than receiving a stop-cause unknown.

Accepted raw/process bytes are logical precursors to their one serialized
container: when an envelope or outcome is finalized, its serialized bytes
replace, rather than add to, the staged component-byte charge.  Transient
duplicate buffers count against runtime memory/operations but not twice
against `total_evidence_limit`; retained physical copies are charged in the
storage dimension.  The actual request and outcome bytes replace the reserve
and are not charged twice.  An incomplete primary stream emits its
cause-specific tail and has no replay exchange.  Failure of the continuation
supervisor itself to emit the complete request or the precharged outcome is an
apparatus failure and supports no R0.1C result; any bytes that already crossed
L remain the exact retained prefix.  This is the same final TCB boundary as
failure to emit the primary terminal, and the contract does not hide it.

## 6. Gate R and launch overlay

Section 5.3 is the canonical manifest and `A_real` authority.  Gate `R_C`
closes only after an independent inventory verifier has:

1. reconstructed the exact effective S_C semantic-member list and bytes;
2. executed the section-12 derived member/unknown-slot procedure, captured every realization
   member, derived the exact fixed/configured unknown-slot view, and verified
   each path's direct pair against the slot registry;
3. validated paths/modes, the captured attack validator, locator parser,
   process supervisor, retained-stream provider, and replay process, exact
   raw-source bindings/branch terminal rules/active-ID declarations,
   package-root separation, ordering, uniqueness, semantic ID, and manifest TV bytes;
4. recomputed `A_real` and the exact `realization_id` spelling.

Closure of R_C fixes the realization; it does not yet create a run.  A
separate acyclic run preflight `P_C` then rejects nonce reuse, constructs and
emits the exact inventory blob that will be frame zero while retaining its
reconstructing source facts, derives its run ID and overlays, materializes the
source fixture, and runs every section-9 attack
relation through the captured attack-validator protocol.  Frame zero crosses
once; individual successful request/response transcripts do not cross L.
Instead, one
compact PREFLIGHT frame crosses after either all 26 relations succeed or the
first relation fails: success closes P_C; failure is followed immediately by its
cause-matched all-unrun terminal and prohibits every descriptor launch.  It
validates the finite post-terminal reserve but does not execute
or claim the replay continuation before a retained TERMINAL exists.  Those
bytes are consequences of closed S_C and R_C, never prerequisites or members
of either.  A failure PREFLIGHT frame leaves P_C open but closes the retained
preflight evidence stream; no subject or ordinary LAB row starts.  Before
frame zero crosses, P_C derives all 26 fixed requests, the exact compact
zero-payload success frame, and the greatest legal bounded failure frame.  It requires
frame zero plus the larger of (a) success followed by every initial
cause-specific no-submit/submitted closure projection and (b) failure followed
by its exact terminal to fit the 2 GiB evidence limit under replacement
accounting.  It then emits frame zero and runs attacks in unsigned-ID order.
A later actual response cannot widen the precharged failure carrier; an
overlength byte is its bounded witness.

The launch overlay is the following R0.1C four-member replacement:

```text
TV({
  descriptor_template: d0,
  run_id: text(run_id),
  semantic_freeze_id: text(final S_C ID),
  realization_id: text("r01c-realization-" + 64 lowercase hex digits)
})
```

All three IDs are TV text, not bytes or ambient command-line strings.  Before
launch, the validator recomputes the semantic ID from the packaged semantic
members, extracts the nested realization manifest from frame zero, recomputes
`A_real`, recomputes `run_id` from frame zero, and requires byte equality with
all three overlay texts.  The frame-zero-derived blob ID/length/run ID must
agree with the one retained stream association, every later replay selector,
and every submitted overlay.  An overlay does not alter case ID, trial ID, B input, subject record
bytes, or oracle.

Any captured member-byte change creates a new `A_real`, realization ID,
inventory blob, and run.  A different registered unknown pair or fixed-slot
rule creates a new semantic ID and therefore a new inventory/run; changed
dynamic slots change the captured configuration, `A_real`, and run.  Alternate
free wording is invalid.  Runtime-loaded
bytes discovered after closure invalidate the gate; they are not patched into
the evidence after execution.

## 7. Replay source identity and positive future

The old R0.1B case
`r01b-case-42ae315f4fd5286123fde985e90ee1b755470b06855f00b8cfafb174012689ef`
and its 365-byte envelope with SHA-256
`23ef24df0532a76909d23ce60bb77660db2a15cd60091bf6a948f07780c3c271`
remain immutable malformed inputs.  The paired old hash-only case
`r01b-case-1612f553ac1e59486bc9898c77d3bea00c32235a62415f44e305d4dd74c4fc7a`
is likewise retained as an attack but excluded from the effective registry.
Both old rows use the absent private source trial
`r01b-dad8b571816d3bfc75f28a217e81ce5985cde623ec3502d52f2f07f888a5362e`
and local ordinal zero identified by F9; neither is silently reinterpreted
under the new selector.  R0.1C derives the global ordinal from the unique trial
ID and rejects any added ordinal field, so the old local/global choice has no
persisted carrier.

R0.1C does not create a replacement positive descriptor.  The positive is the
post-terminal future in section 5.5; giving it a case, trial, pre-terminal
envelope, and constructor would add state without preserving another history
distinction.  The completed source history still needs one registered row.
Its exact symbolic identity is:

```text
source_s0 = {
  attack_kind: text("EMIT_FIXED_REPLAY_SOURCE"),
  family: text("EVIDENCE_REPLAY"),
  fixture_recipe: text("R01C_REPLAY_SOURCE_1"),
  history_production: text("LAB_ONLY"),
  logical_id: text("EVIDENCE_REPLAY_SOURCE_R01C"),
  origin: text("R01C"),
  repetition: U64(0),
  semantic_profile: text("R01C")
}

source_case_id =
  "r01c-case-e2bb3c409e8892e2e4d6725328ff9a3a80698e24f97a45179161e0266e279784"

source_d0 = {case_id: text(source_case_id), lab_input: source_s0}

source_trial_id =
  "r01c-81d0a5a0dfb3dec37fb623d2a065c48825f0845c44c607fe347e198d44ef34b5"
```

The source is the only R0.1C delta descriptor and uses this identity rule:

```text
case_digest = SHA256(ASCII("ZGR01C-CASE") || 00 || TV(s0))
case_id = ASCII("r01c-case-") || lowercase_hex_64(case_digest)

d0 = {case_id: text(case_id), lab_input: s0}
trial_digest = SHA256(ASCII("ZGR01C-TRIAL") || 00 || TV(d0))
trial_id = ASCII("r01c-") || lowercase_hex_64(trial_digest)
```

Section-9 attack IDs are the literal relation names in that table; they never
enter this constructor and have no case or trial identity.

The section-12 derived registry adds the source and sorts it with every
effective row.  Deleting the
two old `r01b-` rows leaves 6,316 retained base IDs; because every one begins
with `r01b-` and the source begins with `r01c-`, its zero-based global ordinal
is exactly 6,316.  The constants and ordinal are independently recomputed at
S_C rather than trusted from this prose.  Importing either without
recomputation fails the gate.

The derived closure view contains only the acyclic source recipe, not a source
envelope containing a not-yet-derived semantic, realization, or run ID.  The
expected selected bytes are fixed in this C0 contract rather than copied into
that view.  After S_C and R_C close, P_C constructs the source fixture with the
actual section-6 overlay, run ID, same-stream frame-zero association, and
effective source ordinal.  Its source record has:

- `b_observation = {}`;
- empty checkpoint, comparison, measurement, and operation lists;
- `process_observation` with `terminal="NO_EXECUTION"` and
  `wait_order="NO_EXECUTION"`;
- exactly the three inherited LAB checks, in unsigned check-key order, each
  `PASS` with empty reasons and needed evidence;
- raw trace stream ID `trace` with exact content
  `ASCII("R01C-HOLDOUT-TRACE") || 00` and an empty missing-suffix list;
- raw measurement stream ID `measurement` with exact content
  `ASCII("R01C-HOLDOUT-MEASUREMENT") || 00` and an empty missing-suffix list;
  every source inactive for this row is absent from its pack; and
- the exact derived complete status view: `APPLICABLE`, `NOT_COMPARED`, `COMPLETE`,
  empty `failure_reasons`, `PASS`, empty `needed_evidence`, `ASSERTED`, and
  `[L_EVIDENCE]` in the field order imposed by TV map keys.

The actual gate-R raw-source registry must contain `trace` and `measurement`
with `source_trial_id` in each exact `active_trial_ids` list; the captured
locator parser must return an empty list for every locatable source-record
address,
and both declarations use `fixture_recipe="R01C_REPLAY_SOURCE_1"`,
the exact source-binding branches
`{fixture_output:"trace",fixture_recipe:"R01C_REPLAY_SOURCE_1"}` and
`{fixture_output:"measurement",fixture_recipe:"R01C_REPLAY_SOURCE_1"}`.
Their branch key sets derive semantic-fixture completion after acceptance of
the last exact recipe byte.  The source envelope's physical position resolves
in effective S1; the launch occurrence
used the real four-member overlay, whose bytes rebuild under section 4.3.  P_C derives the exact source fixture
bytes after all IDs exist; those derived bytes do not feed S_C, A_real, or
trial identity.  The envelope does not claim that its own future replay has
already happened.

Only after the complete primary stream has crossed L does section 5.5 launch
the fresh replay process.  Its exact selector must resolve the actual run ID,
source trial ID, source envelope, `RAW_TRACE` pack, stream ID
`trace`, offset zero, and fixed length.  A `PASS` must return
exactly
`ASCII("R01C-HOLDOUT-TRACE") || 00`: 19 bytes, lowercase hex
`523031432d484f4c444f55542d545241434500`, SHA-256
`4e05f02c3e62dd9c57b1ab4ebe1e364796d5945f647b568ab5515be8ea31cf52`.
The request and supervisor outcome then cross L as a separate continuation;
the raw process response survives inside the outcome and no earlier envelope
is rewritten.  The retained-stream provider, supervisor/fresh-process launcher,
three codecs, access control, and failure behavior are gate-R members and
remain charged.

Deleting either empty status list, accepting the old envelope, accepting only
the source or inventory hash, adding a private/local ordinal, changing a
selected byte, or interpreting an offset against TV framing is a distinct
negative, never the positive future.  The old R0.1B positive and hash-only
rows are both excluded from the effective R0.1C descriptor registry and
retained only as malformed historical attacks; C-native preflight attack
relations replay both
pressures.

## 8. Total neutral-frame function

This section is an **R01C REPLACEMENT** for the missing R0.1B `mm` assignment.
The forty-byte frame remains:

```text
5a 47 4e 46 01 ss mm ff || trial_digest[32]
```

`ss` is `J0..J5` as `00..05`.  `ff` has no legal bits except bit 0
`NO_ACK_REQUIRED` and bit 1 `SELF_CUT_TARGET`.

First define the base `mm` table.  It is slot-local: an omission does not color
unrelated checkpoints as omitted.

| mechanism manifest | J0 | J1 | J2 | J3 | J4 | J5 |
|---|---:|---:|---:|---:|---:|---:|
| `REFERENCE` | `00` | `01` | `00` | `01` | `01` | `01` |
| `NO_FILE_FSYNC` | `00` | `01` | `00` | `02` | `01` | `01` |
| `NO_DIRECTORY_FSYNC` | `00` | `01` | `00` | `01` | `01` | `02` |
| `NO_EXCLUSIVE_CREATE` | `00` | `03` | `00` | `01` | `01` | `01` |
| `NO_REPLACE` | `00` | `01` | `00` | `01` | `02` | `01` |
| `NO_PRE_RECOVERY_REAP_BEHAVIORAL` | `00` | `01` | `00` | `01` | `01` | `01` |
| `DROP_STAGE_CONTROLLER` | `00` | `01` | `00` | `01` | `01` | `01` |
| `SELF_CUT` before target or at `NORMAL` | `00` | `01` | `00` | `01` | `01` | `01` |

The values mean `00 INVARIANT`, `01 REFERENCE`, `02 OMITTED`,
`03 ALTERNATE`, and `04 SELF_CUT_PLACEMENT`.  `NO_PRE_RECOVERY_REAP_BEHAVIORAL`
changes work after the checkpoint program, so its slot work is reference.
`DROP_STAGE_CONTROLLER` can emit frames only for `NORMAL`; those publisher
slots remain reference/invariant.

For every registered descriptor, slot, and `ff`, the total result is a byte,
`NO_FRAME`, or `INVALID`:

| descriptor condition | emitted slot condition | required `ff` | result |
|---|---|---:|---|
| manifest neither `SELF_CUT` nor `DROP_STAGE_CONTROLLER`, cut `Jk` | `slot <= Jk` | `00` | base-table byte |
| same | `slot > Jk` | any | `NO_FRAME` |
| manifest neither `SELF_CUT` nor `DROP_STAGE_CONTROLLER`, cut `NORMAL` | any J0..J5 | `01` | base-table byte |
| `DROP_STAGE_CONTROLLER`, cut J0..J5 | any | any | `NO_FRAME` |
| `DROP_STAGE_CONTROLLER`, cut `NORMAL` | any J0..J5 | `01` | base-table byte |
| `SELF_CUT`, cut `Jk` | `slot < Jk` | `01` | base-table byte |
| `SELF_CUT`, cut `Jk` | `slot = Jk` | `03` | `04` |
| `SELF_CUT`, cut `Jk` | `slot > Jk` | any | `NO_FRAME` |
| `SELF_CUT`, cut `NORMAL` | any J0..J5 | `01` | base-table byte |

Every combination not matching exactly one row, including a reserved flag bit,
wrong legal-bit pattern, unknown manifest/cut/slot, `SELF_CUT_TARGET` on a
non-self-cut descriptor, or a frame where the table says `NO_FRAME`, is
`INVALID`.  An operation failure may shorten the observed prefix but cannot
change the byte for a frame that was emitted.  At a self-cut target `mm=04`
even when the base slot is `00` or `01`; both `mm` and `ff` are required so a
one-byte mutation is detectable.

## 9. Required ambiguity attacks, not trial constructors

The rows below are frozen mutation relations.  A surviving distinction does
not imply a descriptor, case ID, trial ID, ordinal, raw-pack entry, or envelope,
so none of those constructors exists for these attacks.  They are not members
of the effective descriptor registry.  Every relation is exercised in the
single `POST_INVENTORY_PREFLIGHT` phase of P_C, after S_C/R_C and the run ID
exist but before any descriptor launch.

For one relation, the exact base resolver below produces the sole eligible
base and the row's deterministic mutation produces the candidate.  The
candidate differs only by the displayed semantic mutation and mechanically
forced enclosing count/length/hash changes; every other decoded value and raw
byte remains equal.  There is no author-selected witness choice.  Passing the
fixed witness only falsifies that witness; it never proves the validator
complete.

The captured `R01C-ATTACK-VALIDATOR-TV-1` member receives exactly one request
followed by input EOF:

```text
ASCII("ZGR01C-ATTACK-REQUEST") || 00 || u16be(1) || TV({
  attack_id: nonempty printable-ASCII text from the table,
  base_input: bytes(exact eligible validator input),
  mutated_input: bytes(exact candidate validator input)
})
```

Its only successful standard output, followed by output EOF, empty standard
error, and exit status zero, is:

```text
ASCII("ZGR01C-ATTACK-RESPONSE") || 00 || u16be(1) || TV({
  attack_id: the request attack_id,
  reason: enum namespace 7,
  rejected: bool(true)
})
```

Two isolated invocations on the identical request must each return the exact
same expected response bytes.  The reason must be the table's expected first
reason.  Successful requests and responses are deterministic consequences of
S_C, R_C, the inventory/run values, and that occurrence fact; copying their
large bytes into 26 frames would not prove that either process ran.  They
therefore do not cross L individually.

Instead, the one kind-`03` PREFLIGHT has exactly one of two payload shapes:

```text
SUCCESS payload = empty raw byte string

FAILURE payload = TV({
  failed_relation_index: U64,
  invocation: U64,
  outcome: enum namespace 10 restricted to codes 1..5,
  process_exit: list({kind:text("EXIT") | text("SIGNAL"), number:U64})
                of length zero or one,
  process_request_bytes_written: U64,
  process_response_prefix: bytes,
  process_stderr_prefix: bytes
})
```

The complete zero-payload frame's position after frame zero is the surviving
fact that every relation, in unsigned attack-ID order, received two exact
responses from two fresh invocations before any descriptor launch.  A success
enum, the fixed count 26, an empty detail wrapper, a count bitmap, attack ID,
request, or response would be mechanically fixed duplication and is forbidden.

In a failure payload, `failed_relation_index` is in `0..25` and selects the
failed relation at that position in the fixed unsigned-ID order; `invocation`
is U64(0) or U64(1).  All earlier relations, and invocation zero when
`invocation=1`, succeeded exactly and are mechanically reconstructed.  The
bounded write/prefix/exit fields retain the first nonderivable failed
observation under the same legality rules and fixed capture turns as section
5.5.  Response length is at most the one exact expected-response length plus
one; stderr length is zero or one.  `MALFORMED_OR_OVERLONG_RESPONSE` covers an
accepted mutant, wrong ID/reason, malformed/trailing output, the stdout
overlength byte, any stderr byte, or their simultaneous occurrence.  Both
prefixes accepted in the cause-fixing turn survive.  Launch failure has no exit
record; every outcome after launch has one truthful direct-child exit/signal
record after closed-scope cleanup.  No unlisted combination is legal.

Each isolated invocation uses the manifest-selected closed process supervisor
and fresh scope with its own `1,800,000,000,000` monotonic-nanosecond decision
limit.  Its timer origin is the monotonic sample taken after the exact request
bytes and invocation inputs exist and immediately before the first scope-
creation or launch operation; no blocking operation or clock/failure/exit poll
may intervene.  Request write, its same-turn final-byte/EOF transition, stdout,
stderr, exit, scope cleanup, and cause precedence are the section-5.5 state machine with
retained-stream-provider acquisition omitted.  A failed invocation fixes the one
failure payload, which crosses L and is immediately followed by a terminal:
`TIME_BOUND_EXCEEDED` only for `PROCESS_TIME_BOUND_EXCEEDED`, otherwise
`APPARATUS_FAILURE`; it has zero envelopes and all effective IDs unrun.  A
zero-payload success frame closes P_C and permits launch.  Failure to emit the precharged
PREFLIGHT/TERMINAL pair leaves an unsupported incomplete prefix and supports
no result.  Thus a missing validator, watchdog, stderr collector, or scope
supervisor is not credited as zero runtime or TCB.

The semantic relations survive in this C0 member, the compact frame preserves
success occurrence or the first bounded failure, and detailed successful wires
are rebuildable.  The validator, supervisor, codecs, relation checker, and
failure carrier are charged TCB.  The table contains exactly 26 relations;
adding or deleting one requires a new semantic profile.

The following base resolvers are exact.  A resolver returns one typed value and
`base_input` is `TV(value)`, except `SOURCE_PAYLOAD_BASE`,
`OLD_R01B_ENVELOPE_BASE`, and `SELF_CUT_FRAME_BASE`, which return their stated
raw bytes directly.

```text
ABSENT_BH = [
  [enum(8,5), {authoritative_entry:{kind:"ABSENT"},
               auxiliary_regular_entries:[]}],
  [enum(8,6), bytes("")],
  [enum(8,7), bytes(00)]
]

ABSENT_B_OBSERVATION =
  {history:ABSENT_BH}

ABSENT_RESPONSE_RELATION =
  {history:ABSENT_BH,
   response:bytes(TV([[enum(8,7),bytes(00)]]))}

FAIL_REASON_ZERO = enum(7,0)
REALIZATION_MANIFEST_BASE = actual section-5.2 manifest value fixed by R_C
REALIZATION_UNKNOWN_PAIR_BASE = section 12's derived
  realization_slot_registry.fixed_unknown_pairs[0]
GATE_R_IDENTITY_BASE =
  {claimed_a_real:bytes(A_real),
   realization_manifest:REALIZATION_MANIFEST_BASE}
INVENTORY_BLOB_BASE = actual section-5.3 inventory-blob value fixed by P_C
SOURCE_STATUS_BASE = exact section-7 eight-member derived source status view
SOURCE_PAYLOAD_BASE = exact raw section-7 source envelope payload bytes
SOURCE_RAW_SELECTOR_BASE = exact section-5.5 source RAW_TRACE selector with
  actual run ID, source trial ID, stream_id "trace",
  offset U64(0), and length U64(19)
REPLAY_RANGE_BASE =
  {length:U64(19),
   range_sha256:"4e05f02c3e62dd9c57b1ab4ebe1e364796d5945f647b568ab5515be8ea31cf52",
   retained_target:[bytes(ASCII("R01C-HOLDOUT-TRACE") || 00)]}
INVENTORY_REFERENCE_BASE =
  {inventory_blob_id:bytes(inventory_blob_id),
   inventory_frame_payload:[bytes(inventory_blob_bytes)]}
RAW_ADDRESS_BASE =
  {address_space:"UNWRAPPED_CONTENT",
   content:bytes(ASCII("R01C-HOLDOUT-TRACE") || 00),
   selector:SOURCE_RAW_SELECTOR_BASE}
RAW_PREFIX_BASE =
  {execution:enum(2,3),
   entry:{bytes:bytes(52), missing_suffix:[raw_suffix_map[3]]}}
ERRNO_NORMALIZATION_BASE =
  {fact:"OBSERVED_KERNEL_ERROR", observed_errno:U64(1),
   operation:"ACQUIRE_EXCLUSIVE",
   registered_errno:{number:U64(1)}}
INDEX_HASH_BASE =
  {envelope_payload:bytes(SOURCE_PAYLOAD_BASE),
   envelope_sha256:bytes(SHA256(SOURCE_PAYLOAD_BASE))}
SELF_CUT_FRAME_BASE =
  raw bytes 5a474e4601030403 ||
  trial_digest(r01b-093aad9420adb5b83a7b7a0dd9c41bf22931f4602620d081f8ecb6832bc7c257)
RESERVE_RULE_BASE =
  {TAIL_0_APPARATUS:U64(length(stop_tail(0,APPARATUS_FAILURE,false))),
   TAIL_N_COMPLETE:U64(length(complete_tail(6317)))}
OLD_R01B_ENVELOPE_BASE = parse the exact semantic member
  R01B-HOLDOUTS.json, select its unique rows member whose case_id is
  r01b-case-42ae315f4fd5286123fde985e90ee1b755470b06855f00b8cfafb174012689ef
  and whose body.logical_id is EVIDENCE_REPLAY_POSITIVE, decode the lowercase
  even-length hex at body.fixture.envelope_hex, and require exactly 365 bytes
  with SHA-256
  23ef24df0532a76909d23ce60bb77660db2a15cd60091bf6a948f07780c3c271;
  return those raw bytes
ACTIVE_SOURCE_BASE = REALIZATION_MANIFEST_BASE, targeting the unsigned-first
  raw_streams declaration
RUN_FILE_BINDING_BASE =
  {bindings:[
    {producer_path:"p", source_binding:{relative_path:"a"},
     trial_id:source_trial_id},
    {producer_path:"q", source_binding:{relative_path:"b"},
     trial_id:source_trial_id}]}
SEMANTIC_FIXTURE_BINDING_BASE =
  {bindings:[
    {producer_path:"p",
     source_binding:{fixture_output:"trace",
                    fixture_recipe:"R01C_REPLAY_SOURCE_1"},
     trial_id:source_trial_id},
    {producer_path:"q",
     source_binding:{fixture_output:"measurement",
                    fixture_recipe:"R01C_REPLAY_SOURCE_1"},
     trial_id:source_trial_id}]}
PENDING_ENVELOPE_BASE = the exact two-endpoint relation carrier projected from
  the unsigned-first comparison edge E: A is its lower-ordinal completed
  endpoint and B its higher-ordinal unlaunched endpoint, encoded as
  {cause:enum(2,3),
   pending_envelopes:[{edge_id:E, ordinal:A.ordinal, trial_id:A.trial_id}],
   submitted_trial_ids:[A.trial_id],
   terminal_unrun_trial_ids:[B.trial_id]}
TERMINAL_ASSOCIATION_BASE = from the exact
  submitted_stop_projection(0,empty,empty-nonderivable-prefix,
                            APPARATUS_FAILURE), select
  {envelope_frame:bytes(its sole ENVELOPE frame),
   terminal_payload:[enum(2,3),bool(true)]}
```

`ABSENT_BH` is independently checked against retained trial
`r01b-1a3272a91627ea5448e7db15a7d6edbf7ae2115de407048c9552f28ab502c65e`.
The self-cut resolver is independently checked to be `SELF_CUT` at `J3`.
`raw_suffix_map[3]` means the one exact structured unknown selected
by the section-12 derived map, not a function-valued TV member.  A missing resolver prerequisite leaves
P_C open rather than selecting another base.  The two binding bases are
closed relation carriers for the branch-specific uniqueness check after path and
member validation; `p` and `q` are exact distinct producer-identity tokens, not
claims that those paths occur in the realization manifest.

| attack ID | base | unique target and deterministic mutation | validator | reason code |
|---|---|---|---|---:|
| `R01C_BH_BYTES_WRAPPED_IN_RECORD_NEGATIVE` | `ABSENT_B_OBSERVATION` | `/history`: replace list `V` by bytes value `bytes(TV(V))` | `B_TV_SHAPE` | 34 |
| `R01C_B_TV_MAP_INSTEAD_OF_EVENT_LIST_NEGATIVE` | `ABSENT_B_OBSERVATION` | `/history`: replace `V` by `{events:V}` | `B_TV_SHAPE` | 34 |
| `R01C_CANONICAL_ABSENT_AS_REJECT_NEGATIVE` | `ABSENT_RESPONSE_RELATION` | `/response`: replace by `bytes(TV([[enum(8,7),bytes(01)]]))`; history is unchanged | `CANONICAL_B_DERIVATION` | 35 |
| `R01C_FAILURE_NAMESPACE_0008_NEGATIVE` | `FAIL_REASON_ZERO` | root: replace `enum(7,0)` by `enum(8,0)` | `FAILURE_REASON_NAMESPACE` | 36 |
| `R01C_GATE_R_EMPTY_ACTIVE_SOURCE_NEGATIVE` | `ACTIVE_SOURCE_BASE` | replace the targeted declaration's nonempty `/active_trial_ids` by `[]` | `GATE_R_IDENTITY` | 37 |
| `R01C_GATE_R_RAW_XY_NEGATIVE` | `GATE_R_IDENTITY_BASE` | `/claimed_a_real`: replace by `bytes(SHA256(78 79))` | `GATE_R_IDENTITY` | 37 |
| `R01C_GATE_R_RUN_FILE_ALIAS_NEGATIVE` | `RUN_FILE_BINDING_BASE` | second `/source_binding/relative_path`: replace `b` by `a`; retain both producer paths | `RAW_BINDING_UNIQUENESS` | 37 |
| `R01C_GATE_R_SEMANTIC_FIXTURE_ALIAS_NEGATIVE` | `SEMANTIC_FIXTURE_BINDING_BASE` | binding with output `measurement`: replace it by `trace`; retain distinct producer path/recipe | `RAW_BINDING_UNIQUENESS` | 37 |
| `R01C_GATE_UNKNOWN_FREE_TEXT_NEGATIVE` | `REALIZATION_UNKNOWN_PAIR_BASE` | `/reason`: replace `r` by `r || "!"`, retaining its registered needed-evidence text | `GATE_R_IDENTITY` | 37 |
| `R01C_INDEX_HASHES_COMPLETE_FRAME_NEGATIVE` | `INDEX_HASH_BASE` | `/envelope_sha256`: replace by hash of `02 || u64be(length(payload)) || payload` | `REPLAY_INDEX_HASH` | 29 |
| `R01C_INVENTORY_HASH_ONLY_NEGATIVE` | `INVENTORY_REFERENCE_BASE` | delete sole `/inventory_frame_payload/0`; retain ID | `INVENTORY_REFERENCE` | 38 |
| `R01C_MM_SELF_CUT_ORDINARY_NEGATIVE` | `SELF_CUT_FRAME_BASE` | raw offset 6: replace `04` by ordinary J3 byte `01`; retain `ff=03` | `MM_ASSIGNMENT` | 40 |
| `R01C_NEEDED_EVIDENCE_TV_ORDER_NEGATIVE` | exact TV list `["aa","z"]` | swap indices 0/1 to exact `["z","aa"]` | `NEEDED_EVIDENCE_ORDER` | 39 |
| `R01C_OLD_ONE_MIB_RESERVE_NEGATIVE` | `RESERVE_RULE_BASE` | atomically replace both U64 values by `1048576` | `CLOSURE_RESERVE` | 24 |
| `R01C_PENDING_ENVELOPE_OMITTED_AT_STOP_NEGATIVE` | `PENDING_ENVELOPE_BASE` | delete A's sole pending ENVELOPE before the cause-specific terminal; retain submitted count and unrun suffix | `BOUNDARY_CLOSURE` | 24 |
| `R01C_RAW_OFFSET_AT_TV_TAG_NEGATIVE` | `RAW_ADDRESS_BASE` | `/address_space`: replace `UNWRAPPED_CONTENT` by `TV_BYTES_VALUE_ENCODING`; retain offset zero | `RAW_ADDRESSING` | 42 |
| `R01C_RAW_PREFIX_MARKED_COMPLETE_NEGATIVE` | `RAW_PREFIX_BASE` | delete sole `/entry/missing_suffix/0`; retain byte `52` | `RAW_COMPLETENESS` | 42 |
| `R01C_REPLAY_HASH_ONLY_RAW_NEGATIVE` | `REPLAY_RANGE_BASE` | delete sole `/retained_target/0`; retain length/hash | `REPLAY_RANGE_RETENTION` | 29 |
| `R01C_REPLAY_OLD_R01B_ENVELOPE_NEGATIVE` | `SOURCE_PAYLOAD_BASE` | replace root by `OLD_R01B_ENVELOPE_BASE` | `POSITIVE_REPLAY_FIXTURE` | 41 |
| `R01C_REPLAY_PRIVATE_ORDINAL_ZERO_NEGATIVE` | `SOURCE_RAW_SELECTOR_BASE` | insert additional `/ordinal:U64(0)` | `REPLAY_SELECTOR` | 42 |
| `R01C_RUN_ID_MISSING_NEGATIVE` | `SOURCE_RAW_SELECTOR_BASE` | delete `/run_id` | `REPLAY_SELECTOR` | 42 |
| `R01C_SEMANTIC_MEMBER_DUPLICATED_IN_R_NEGATIVE` | `INVENTORY_BLOB_BASE` | insert semantic member zero into realization members as captured branch `{bytes,mode:U64(0),path}` with the same path/bytes, then re-sort | `INVENTORY_REFERENCE` | 38 |
| `R01C_STATUS_DELETE_FAILURE_REASONS_NEGATIVE` | `SOURCE_STATUS_BASE` | delete `/failure_reasons` | `STATUS_SCHEMA` | 43 |
| `R01C_STATUS_DELETE_NEEDED_EVIDENCE_NEGATIVE` | `SOURCE_STATUS_BASE` | delete `/needed_evidence` | `STATUS_SCHEMA` | 43 |
| `R01C_TERMINAL_SUBMISSION_ASSOCIATION_NEGATIVE` | `TERMINAL_ASSOCIATION_BASE` | `/terminal_payload/1`: replace `true` by `false`; retain the submitted stop envelope | `TERMINAL_CONSISTENCY` | 30 |
| `R01C_UNREGISTERED_ERRNO_AS_NONE_NEGATIVE` | `ERRNO_NORMALIZATION_BASE` | `/registered_errno`: replace map by text `NONE`; retain observed errno | `OPERATION_ERRNO` | 26 |

One displayed mutation replaces a closed function rather than two independently
selectable leaves.  `RESERVE_RULE_BASE` is a two-observation carrier for one
total reserve function, and its mutation replaces that root function by the
old constant function.  The validator must compare the whole function carrier;
checking only one physical map member does not satisfy that row.  The raw-prefix
negative is now an ordinary one-element deletion because list cardinality is
the only completion bit.

The validator column is a closed mnemonic for the exact normative rule named
by the row: it never selects an implementation, plugin, or alternate policy.
The one manifest-selected attack validator dispatches on `attack_id`, applies
that row's base resolver/mutation/rule, and has no other validator name.  The
numeric reason is the namespace-7 code and must map to the label used elsewhere
in this section; numeric/label disagreement is invalid.

The corresponding positive two-text witness is `aa,z`.  Its exact TV bytes are
`07000000000000000204000000000000000261610400000000000000017a`; the rejected
raw-TV ordering is
`0700000000000000020400000000000000017a0400000000000000026161`.

## 10. Complete ordering ledger

This table is normative and closes every use of “sorted,” “set,” or ordered
list in the R0.1C delta.  Unsigned comparison is lexicographic by byte, with a
proper prefix before its extension.

| list or set | exact order / duplicate rule |
|---|---|
| TV map entries | unsigned ASCII key bytes; duplicate key invalid |
| auxiliary fixture entries | unsigned `name_bytes`; duplicate name invalid (inherited) |
| B events / partial prefix | B crossing chronology; never sorted |
| checkpoint observations | observation chronology; slots must follow the legal prefix |
| scope enums | ascending `(u16 namespace, u16 code)`; unique |
| failure reasons | ascending `(u16 namespace, u16 code)`; unique |
| needed-evidence text | unsigned exact UTF-8 text bytes; unique |
| constituent checks | selected S1 unsigned `check_key` position; key not repeated; exact count |
| comparison edge results | selected S1 unsigned incident-`edge_id` position; ID not repeated; exact count |
| operation facts | inherited operation-registry position; operation text not repeated; exactly one per applicable operation |
| evidence sources in an operation fact | inherited evidence-source-registry position; unique |
| measurement cells | position of ascending unsigned measurement-path UTF-8 bytes; exact applicable count |
| constructed inherited measurement-status applications | unsigned measurement-path UTF-8 bytes when enumerated; policy admits respectively exactly 1,027 UNKNOWN and 9 UNSUPPORTED applications; unique |
| raw-suffix / stopped-before-capture maps | positions zero through two mean namespace-2 codes 3 through 5; exactly three each |
| raw-pack entries | positions follow active declarations in unsigned `stream_id` order; ID not repeated; exact active count |
| gate-R raw-stream declarations | tuple `(pack text bytes, stream_id bytes)`; unique |
| raw-stream active trial IDs | nonempty; unsigned trial-ID bytes; unique; exact effective-registry subset |
| expanded pipe bindings | tuple `(trial_id bytes, producer_path bytes, producer_fd numeric)`; unique across both packs |
| expanded run-file bindings | tuple `(trial_id bytes, scratch-relative-path bytes)`; unique across both packs, independent of producer path |
| expanded semantic-fixture bindings | tuple `(trial_id bytes, fixture-recipe bytes, fixture-output bytes)`; unique across both packs, independent of producer path |
| raw locators | tuple `(pack text bytes, stream_id bytes, offset u64 numeric, length u64 numeric)`; unique |
| realization members | unsigned path bytes; unique |
| semantic members | unsigned path bytes; unique |
| section-9 attack relations | unsigned `attack_id` bytes; exactly 26; unique |
| L-stream preflight frame | exactly one at physical ordinal one; success or one first-failure union |
| L-stream envelope frames | effective numeric trial ordinal; unique |
| replay-index entries | numeric ordinal; unique ID, ordinal, frame ordinal, and offset |
| terminal unrun trial IDs | unsigned trial-ID bytes; unique |
| effective S1 descriptor rows | unsigned trial-ID bytes; unique; ordinal is zero-based position |
| comparison partners / edge IDs retained in S1 | unsigned identifier bytes; unique |
| derived-closure delta rows | exactly the one source row |
| fixed unknown pairs | positions follow the four unsigned C0 path rows; exactly four |
| dynamic unknown pairs | positions follow the two unsigned C0 `config_key` rows; exactly two |

Set union for reasons and needed evidence means concatenate all contributors,
reject any malformed contributor, remove exact duplicate typed values, then
apply the listed sort.  No locale, JSON order, host sort, Unicode collation,
TV-encoded-length order, or insertion order is consulted.

## 11. Persistence and information responsibility

These classifications are boundary-scoped and simultaneous.

### MUST SURVIVE

- Enough occurrence, order, source-association, and nonderivable payload
  information survives to regenerate every admitted B or L crossing exactly.
  In particular, deleting an actual recovery response `00` versus `01` merges
  histories distinguished by a later recovery query.  A deterministic input
  value may rebuild from its descriptor, but the fact and position of its
  crossing may not be invented.
- The exact author-selected semantic choices and every nonderivable
  realization observation used by frame zero survive: each captured member's
  bytes/path/mode, the external-slot configuration bytes when present, the
  once-declared realization-slot rules, the run nonce, and their one run
  association.  Fixed unknown paths derive from section 12; dynamic paths and
  all unknown pairs derive from its rules plus that configuration rather than surviving
  again in the manifest.
  Deleting a target member while retaining only its digest or remote locator
  makes an exact inventory replay impossible.  The canonical inventory map and
  frame encoding themselves are not additional MUST information.
- The one PREFLIGHT occurrence survives.  Its complete zero-payload success
  frame is the compact fact that all 26 ordered relations each received two
  exact fresh-process responses before launch.  Its nonempty failure payload
  retains the selected relation
  index, invocation, raw bounded stdout/stderr prefixes, write count, direct
  exit, and first failure outcome.  Twenty-six deterministic transcript copies
  or invented descriptor envelopes are not substitutes.
- Every descriptor-submission occurrence, B crossing, apparatus/loss fact not
  derivable from an accepted prefix, and nonmechanically generated per-trial raw
  trace or measurement byte accepted at L survives.  This includes actual
  partial output, diagnostics, scratch spellings, timestamps, PIDs, environment
  output, and framing when they entered a declared raw stream.  A fixed
  semantic-fixture byte string may instead rebuild from its recipe plus the
  fact that its terminal condition was accepted.
- A stopped run's cause and submitted/prelaunch association bit survive.
  Deleting the bit merges a row completed before the next row's prelaunch
  failure with the same row failing after its own observations but before its
  submitted execution closes; the per-row execution query distinguishes them.
- Every completed post-terminal request/outcome occurrence and every
  nonderivable outcome field survives, including raw stdout/stderr prefixes,
  partial request-write count, and direct exit/signal.  A valid deterministic
  PASS wire may rebuild from the retained stream plus its success occurrence;
  an actual failure cannot.  A request-only or primary-only prefix is retained
  as exact crossed bytes, but its permanent failure, resumability, and future
  completion state are `UNSUPPORTED`, not silently represented by absence.
- The run nonce and used-tuple/replay-selection responsibility survive while
  multiple retained runs are addressable.  Forgetting it can make the same
  trial/ordinal/range tuple select two histories even when all per-trial bytes
  remain.
- The governing semantic choices, codecs, normalizer/comparator/oracle rules,
  version selection, and facts that S_C/R_C closed survive wherever later
  interpretation relies on them.  A generated JSON/TV rendering carries no
  extra responsibility when those sources and its exact construction rule
  survive.

Moving any such byte or rule to a service, operator convention, private
decoder, cache, or deployment script is `EXTERNALIZE`, not deletion.

### MAY REBUILD

Given the exact surviving source bytes, occurrence/apparatus facts, and
identified closed rules, B input events, `BH_value/BH_bytes`, submitted overlay
bytes, atomically materialized native-only cells, canonical records and their
position-derived identities, locator views, status maps, terminal query fields, the source
semantic-fixture raw bytes,
envelope/terminal frames, the replay-index view, case/trial/run IDs, ordinals,
offsets, hashes, normalized operation facts, edge results, aggregates, counts,
and quantiles may be rebuilt.  The generated closure-view JSON, manifests, inventory
blob/frame, digests, and IDs likewise rebuild from their exact source choices,
nonce, and codecs; this moves compiler/verifier work into TCB rather than
making it zero.  The inherited measurement-status constructor outputs and fixed protocol literals
likewise rebuild from the immutable B registries, exact attack fixtures, role
keys, and this C0 contract.  Given S/R/P values and the surviving PREFLIGHT success fact,
every successful attack request and response is rebuilt from the exact
section-9 resolver/rule; an actual failure payload is not.  Parsed
post-terminal status, reasons, needed evidence, selected bytes, and hashes are
rebuilt from the retained request/outcome pair.  The deterministic request and
a valid PASS outcome may likewise be rebuilt from that exact retained stream,
recipe, and crossing/success occurrence; an actual failure fact must survive.
If a permitted replay asks for the historical canonical L-stream, the smaller
retained source representation and occurrence/order facts must regenerate it
byte-identically; otherwise that stream encoding itself must be retained.
The logical bytes that crossed L remain the replay contract even when their
literal serialization is not the physical persistent form.  Rebuilding charges the selected
specification, dependencies, compute, time, storage, operations, and TCB.  A
value whose actual source byte/fact or governing rule is absent is not
rebuildable.

### MAY FORGET

R0.1C awards no new unconditional `MAY_FORGET` item.  A value proven never to
have crossed either boundary is outside persisted history; that is not a
license to discard an incidental byte that did cross inside an exact raw pack.
The deleted attack case IDs, trial IDs, ordinals, descriptors, and envelopes
never cross and have no constructor; they are absent rather than forgotten
history.
Earlier bounded B1 conclusions retain only their original scope.

## 12. Acyclic semantic delta gates

R0.1C preserves the inherited R0.1B suite digest
`996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6`
and all resulting subject record/fixture bytes.  It does not pretend the new
evidence grammar changes those B bytes.

The immutable base closure is accepted only after reconstructing and checking:

- R0.1B semantic seed
  `078acf7c35cf1840b70886dd854f4fffcc0be1a7c5f8b1627d3bd36e148c2ece`;
- `R01B-S1.json` SHA-256
  `fb72f6b36ca3eae284003ee1983e995afb13d3e8ec9d518f0c1afeaca67a9043`;
- R0.1B semantic freeze ID
  `r01b-semantic-954e2b16b258ceb8869795dbb823a0284a8369ca1cb20481168d7f652d89fcfd`;
  and
- all three immutable attack hashes in section 0.

Gate `S_C` has two ordered obligations: one hashed source gate and one
nonpersistent derived-agreement check.

`S_C0` is R0.1B's exact binary S0 manifest and exact S1 manifest bytes followed
by a delta manifest over exactly these four files in ascending unsigned path
order:

```text
FEASIBILITY-AUDIT-R01B.md
FEASIBILITY-SUPPLEMENT-R01B-RUN-BOUNDARY.md
R01B-BLACKBOX-BREAKER.json
REALIZATION-CORRECTION-R01C.md
```

The delta manifest uses the inherited
`LP(path_utf8) || u64be(file_length) || file_bytes` framing.  Define:

```text
C0_digest = SHA256(ASCII("ZERO-GROUND-R01C-S0-DELTA") || 00 ||
                   LP(R01B_S0_manifest_bytes) ||
                   LP(R01B_S1_manifest_bytes) ||
                   LP(delta_manifest_bytes))
```

No generated R01C artifact, implementation byte, validator, or expected hash
is a C0 member.  The contract may therefore be hashed without containing its
own hash.

`D_C` is the exact derived validation projection that two independent decoders
must reproduce.  It may be materialized transiently as canonical JSON named
`R01C-S1.json` under R0.1B's canonical JSON rules, but that file and its hash
are not semantic members, do not enter identity, do not cross L, and may be
discarded after validation.  Its value has exactly these five top-level
members:

```text
controlled_text_registry
effective_descriptor_registry
failure_reason_registry
measurement_registry_delta
realization_slot_registry
```

The enclosing C0 contract and base inputs already select the projection schema
and base semantic ID, so copying either fixed value into `D_C` is forbidden.
Every nested shape is closed as follows; an additional or missing member makes
the derived-agreement check fail rather than becoming generator convention.

`failure_reason_registry` is a list of exactly 44 nonempty printable-ASCII JSON
strings materializing section 3.1 in numeric-code order.  Position supplies
code `0..43`, and the enclosing registry name supplies namespace 7; repeating
either per label would add no choice.

`controlled_text_registry` is exactly:

```text
{
  inherited_measurement_status_constructor: {
    unknown_needed_evidence_prefix: text("native measurement for "),
    unknown_reason: text("measurement unavailable in this holdout"),
    unsupported_reason: text("measurement unsupported in this holdout")
  },
  raw_suffix_map: list of exactly three {
      needed_evidence: nonempty printable-ASCII text,
      reason: nonempty printable-ASCII text
  } maps,
  stopped_before_capture_map: list of exactly three {
      needed_evidence: nonempty printable-ASCII text,
      reason: nonempty printable-ASCII text
  } maps
}
```

There is no numeric unknown code: tag-09 and manifest-UNKNOWN values carry the
two texts directly, so alpha-renaming a code cannot create semantic state.
The inherited measurement statuses are closed by path, not by global text
allowlists.  For every inherited measurement path `p`, select the unique
effective LAB descriptor whose decoded `lab_input` has respectively:

```text
attack_kind = "REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNKNOWN"
logical_id = "MEASURE_STRUCTURED_UNKNOWN(" || p || ")"
fixture.path = p

attack_kind = "REPLACE_EXACT_MEASUREMENT_LEAF_WITH_STRUCTURED_UNSUPPORTED"
logical_id = "MEASURE_STRUCTURED_UNSUPPORTED(" || p || ")"
fixture.path = p
```

Decode the schema-declared `replacement_tv_hex`.  For the UNKNOWN row it must
be tag 09 and its two texts must equal the descriptor replacement's
`status="UNKNOWN"`, `reason`, and `needed_evidence` fields; for the UNSUPPORTED
row it must be tag 0a and its reason must equal the replacement's
`status="UNSUPPORTED"` and `reason` fields.  Across all 1,040 UNKNOWN rows the
reason must be exactly `unknown_reason` and needed evidence must be exactly
`unknown_needed_evidence_prefix || p`; across all 1,040 UNSUPPORTED rows the
reason must be exactly `unsupported_reason`.  Any counterexample fails S_C
rather than creating an exception row.  The immutable path policy then admits
the UNKNOWN constructor output at exactly 1,027 paths, the UNSUPPORTED output
at exactly nine paths, and neither at the thirteen `NATIVE_ONLY` paths.  Thus
1,036 repeated path rows are DERIVE-able and forbidden; the path remains the
context key.

Define `B_needed` mechanically from the 6,316 retained base literal-oracle
rows after the two section-7 exclusions.  Traverse only members declared by
their closed expected-value schemas and collect every exact text occupying a
`needed_evidence` field or list.  The result must contain exactly 1,041 unique
texts: all 1,027 policy-admitted values
`unknown_needed_evidence_prefix || p`, plus exactly these fourteen direct
values in unsigned-byte order:

```text
[
  "CUT_CONTINUATION_WITHOUT_STAGE_CONTROLLER",
  "PASSIVE_REAP_OBSERVER_WITH_FROZEN_SEMANTICS",
  "complete legal 28-row trace and recovery matrix",
  "frozen applicable opaque alternative selection realization",
  "identified physical realization with controlled total power loss and independent cold readback",
  "realization supporting a native measurement for evolution.format_support",
  "realization supporting a native measurement for evolution.freshness_support",
  "realization supporting a native measurement for evolution.generation_support",
  "realization supporting a native measurement for evolution.migration_support",
  "realization supporting a native measurement for evolution.rollback_support",
  "realization supporting a native measurement for evolution.version_support",
  "realization supporting a native measurement for information_loss_risk.physical_faults",
  "realization supporting a native measurement for information_loss_risk.power_loss_faults",
  "realization supporting a native measurement for portability.physical_portability_status"
]
```

The source delta row contributes empty needed-evidence lists.  A verifier also
constructs the 1,027 path values independently from the path-policy map and
requires set equality; arbitrary JSON text and undeclared hex strings are
never scanned.  Define `C_needed` as exactly this already-sorted list:

```text
[
  "APPARATUS_FAILURE_COMPLETION",
  "COMPLETE_EXTERNAL_SERVICE_BYTES",
  "COMPLETE_FIRMWARE_BYTES",
  "COMPLETE_HYPERVISOR_BYTES",
  "COMPLETE_OS_KERNEL_BYTES",
  "COMPLETE_PHYSICAL_COMPONENT_BYTES",
  "COMPLETE_RUNTIME_BYTES",
  "POST_STREAM_REPLAY_CAPABILITY",
  "POST_STREAM_REPLAY_PROCESS_EXIT",
  "POST_STREAM_REPLAY_PROCESS_LAUNCH",
  "POST_STREAM_REPLAY_REQUEST_WRITE",
  "POST_STREAM_REPLAY_RESPONSE_BYTES",
  "POST_STREAM_REPLAY_SOURCE",
  "POST_STREAM_REPLAY_TIME_BOUND",
  "STORAGE_BOUND_COMPLETION",
  "TIME_BOUND_COMPLETION"
]
```

The controlled needed-evidence set is the unsigned-byte-sorted unique union of
the 1,041-value `B_needed` and 16-value `C_needed` sets.  They are disjoint, so
its checked cardinality is 1,057.  This is a derived validation view, not a `D_C`
member or open allowlist.  Every direct pair below and in
`realization_slot_registry` must draw its needed-evidence text from that set.
Define these exact direct pairs:

```text
RAW_A = {needed_evidence:"APPARATUS_FAILURE_COMPLETION",
         reason:"RAW_SUFFIX_NOT_CAPTURED_AFTER_APPARATUS_FAILURE"}
RAW_T = {needed_evidence:"TIME_BOUND_COMPLETION",
         reason:"RAW_SUFFIX_NOT_CAPTURED_AFTER_TIME_BOUND"}
RAW_S = {needed_evidence:"STORAGE_BOUND_COMPLETION",
         reason:"RAW_SUFFIX_NOT_CAPTURED_AFTER_STORAGE_BOUND"}
STOP_A = {needed_evidence:"APPARATUS_FAILURE_COMPLETION",
          reason:"STOPPED_BEFORE_CAPTURE_AFTER_APPARATUS_FAILURE"}
STOP_T = {needed_evidence:"TIME_BOUND_COMPLETION",
          reason:"STOPPED_BEFORE_CAPTURE_AFTER_TIME_BOUND"}
STOP_S = {needed_evidence:"STORAGE_BOUND_COMPLETION",
          reason:"STOPPED_BEFORE_CAPTURE_AFTER_STORAGE_BOUND"}
```

`raw_suffix_map` is exactly `[RAW_A,RAW_T,RAW_S]`; positions zero through two
select execution codes 3 through 5.  Both
raw packs use the same cause-selected row because the enclosing pack already
preserves their distinction.  The
`stopped_before_capture_map` is exactly `[STOP_A,STOP_T,STOP_S]` under the same
position rule.  Elsewhere `map[c]` denotes physical list index `c-3` for
namespace-2 stop code `c`.  Repeating each execution code inside its position
would add no choice.  These maps close every use in
`stop_frames(k,q,p,c)` before P_C asks whether the projection fits.  No JSON
number/string coercion is legal.

No terminal-stop map is stored.  For terminal `COMPLETE`, the scan-derived
failure-reason and needed-evidence lists are empty.  For a terminal stop code
`c`, they are respectively `[enum(7,4)]` and
`[stopped_before_capture_map[c].needed_evidence]`; code 4 is
`EVIDENCE_UNAVAILABLE`.  The execution enum keeps the three stop histories
distinct; the submitted-stop Boolean keeps prelaunch and submitted failures
distinct.  They are the only nonderived terminal responsibilities.  This construction
parameterizes scan-derived terminal query fields and the selectorless apparatus
view without copying the same cause table; terminal bytes carry only the
complete enum or the stop-cause/association pair.
`raw_suffix_map` is total over execution codes
`APPARATUS_FAILURE`, `TIME_BOUND_EXCEEDED`, and `STORAGE_BOUND_EXCEEDED`; its
selected value applies independently inside either raw pack.  Runtime
diagnostics remain raw bytes.  Every measurement tag-09/tag-0a value must be
selected by the exact path constructor plus policy or the eligible stop rule,
and every other tag-09 use must be selected by `raw_suffix_map` or
`stopped_before_capture_map`; every derived manifest unknown-slot view row gets
its query pair from the exact realization-slot row governing its path.  Parser
failure creates the ordinary STOP_A completion and no locator-specific tag.
No tag-09 member, tag-0a member, terminal value, or failure
envelope may introduce free text or borrow text registered for another
context;
this makes the closure reserve finite.  Locator parsing has the single exact
section-5.2 protocol and captured parser member; an implementation cannot add
a codec name whose behavior lives outside S_C/R_C.

`effective_descriptor_registry` is exactly:

```text
{
  base_excluded_case_ids: list(text),
  delta_s0_tv_hex: list(lowercase even-length hex) of length one
}
```

The exclusion list is exactly the two old R0.1B evidence-replay case IDs from
section 7, in unsigned order.  `delta_s0_tv_hex[0]` is the registered source
`TV(source_s0)`.  Its case ID, descriptor template, trial ID, fixture recipe,
and LAB-only production all derive from that value plus section 7 and are not
repeated.  The effective count, transform name, and ordinal rule are likewise
fixed by C0 rather than copied into `D_C`.  Starting from 6,318 base rows, the
effective count is therefore exactly
`6,317`: 6,318 minus the two malformed replay rows plus one source row.  The 26
section-9 attacks and the post-terminal positive are respectively preflight
relations and a future continuation, not descriptor rows.
The inherited 3,028 subject rows are unchanged; LAB rows are 3,289
(`3,290 - 2 + 1`).

The delta source's exact expected checks and status are fixed by section 7 and
mechanically rebuilt; copying a second expected-value encoding into the row
would add no semantic choice.
Expected answers never enter identity.

The effective registry is rebuilt by deleting the two named base rows, adding
the one source delta row, sorting all 6,317 trial IDs, and assigning zero-based
global ordinals.  Existing stored base ordinals are ignored.  Inherited descriptor
templates, case/trial IDs, fixtures, B wires, and comparison edges otherwise
retain exact bytes.  `R01B-TO-R01C-ORACLE-1` mechanically converts every
retained base literal: it inserts the row's existing root `failure_reasons` and
`needed_evidence` into the new eight-member status map, encodes reason codes in
namespace 7, retains check/edge expectations, and rejects an unknown label.
Thus the old incomplete status bytes are attack input, not effective R0.1C
status bytes.

`measurement_registry_delta` is exactly:

```text
{
  operations: list({pointer: text, value: JSON value})
}
```

The exact inherited registry and its 1,040-path count are selected by C0.  All
operations are `REPLACE`, so repeating that opcode, the fixed base hash, path
count, resulting fixture bytes, or their hash would add no choice; each is
recomputed during agreement.  Operations are in the displayed order and
replace exactly these RFC-6901
pointers: `/schema_id` with `R01C-MEASUREMENT-PATHS-1`;
`/native_value_kinds/definitions/registry_schema_id/const` with
`R01C-MEASUREMENT-PATHS-1`;
`/native_value_kinds/definitions/contract_profile_id/const` with `R01C`;
`/native_value_kinds/definitions/run_id/pattern` with
`^r01c-run-[0-9a-f]{64}$`;
`/native_value_kinds/definitions/trial_id/pattern` with
`^r01[bc]-[0-9a-f]{64}$`;
`/closed_container_schemas/replay_selector_record` with this exact JSON value:

```text
{
  oneOf: [
    {
      additionalProperties: false,
      properties: {
        length: {minimum: 0, type: "integer"},
        offset: {minimum: 0, type: "integer"},
        run_id: {$ref: "#/native_value_kinds/definitions/run_id"},
        stream: {const: "CANONICAL_RECORDS", type: "string"},
        trial_id: {$ref: "#/native_value_kinds/definitions/trial_id"}
      },
      required: ["length", "offset", "run_id",
                 "stream", "trial_id"],
      type: "object"
    },
    {
      additionalProperties: false,
      properties: {
        length: {minimum: 0, type: "integer"},
        offset: {minimum: 0, type: "integer"},
        run_id: {$ref: "#/native_value_kinds/definitions/run_id"},
        stream: {enum: ["RAW_MEASUREMENT", "RAW_TRACE"], type: "string"},
        stream_id: {pattern: "^[ -~]+$", type: "string"},
        trial_id: {$ref: "#/native_value_kinds/definitions/trial_id"}
      },
      required: ["length", "offset", "run_id",
                 "stream", "stream_id", "trial_id"],
      type: "object"
    },
    {
      additionalProperties: false,
      properties: {
        length: {minimum: 0, type: "integer"},
        offset: {minimum: 0, type: "integer"},
        run_id: {$ref: "#/native_value_kinds/definitions/run_id"},
        stream: {enum: ["APPARATUS_FAILURES", "INVENTORY", "REPLAY_INDEX"],
                 type: "string"}
      },
      required: ["length", "offset", "run_id", "stream"],
      type: "object"
    }
  ]
}
```

The final operation replaces `/invariants/replay_consistency/rules` with this
exact ordered JSON string list:

```text
[
  "run_id_matches_inventory_derived_index_replay_selector_and_overlays",
  "one_preflight_frame_is_exact_success_or_first_failure_after_ordered_attacks",
  "trial_id_is_unique_in_effective_registry",
  "ordinal_equals_global_unsigned_trial_id_position",
  "scan_rebuilt_entry_id_ordinal_offset_length_and_payload_hash_agree",
  "selector_shape_stream_and_optional_stream_id_select_exactly_one_payload",
  "offset_and_length_are_payload_relative_and_in_bounds_without_wrap",
  "selected_target_bytes_are_retained_not_hash_only",
  "positive_replay_occurs_after_terminal_in_a_fresh_process"
]
```

No other base byte is changed.  The six-member
`evidence_stream_registry` is retained and its physical/derived mapping is
section 5.4.  The R0.1B base-fixture synthesis algorithm then regenerates all
1,040 cells under the effective schemas, with its four profile-specific
special values replaced by `R01C-MEASUREMENT-PATHS-1`, `R01C`,
`r01c-run-` plus 64 zeroes, and `r01c-` plus 64 zeroes.  R0.1C adds one exact
base-synthesis rule for this replacement schema: a `oneOf` selects its first
displayed branch.  The resulting replay selector uses
`CANONICAL_RECORDS`, has no `stream_id`, uses zero for its nonnegative integers,
and contains no range hash.  `D_C` derives the resulting exact TV bytes; the
validators may hash those bytes for agreement checking but do not persist the
digest as another member.

`realization_slot_registry` is exactly:

```text
{
  dynamic_unknown_pairs: list of exactly two {
      needed_evidence: nonempty printable-ASCII text,
      reason: nonempty printable-ASCII text
  } maps,
  fixed_unknown_pairs: list of exactly four {
      needed_evidence: nonempty printable-ASCII text,
      reason: nonempty printable-ASCII text
  } maps
}
```

It materializes only section 5.2's exact direct text mappings.  The row paths,
dynamic config keys/prefixes, enumerator
`R01C-PACKAGE-AND-LOADED-BYTES-1`, and configuration path
`configuration/external-components.tv` are already fixed in C0, so repeating
them in `D_C` would add no choice.  The five role keys and section-5.2 protocol
definitions likewise select the captured protocol wires.  The exact positional
rows are:

| kind | path or prefix | config key | exact direct unknown pair |
|---|---|---|---|
| fixed | `unknown/firmware` | -- | `{reason:"FIRMWARE_BYTES_NOT_CAPTURED", needed_evidence:"COMPLETE_FIRMWARE_BYTES"}` |
| fixed | `unknown/hypervisor` | -- | `{reason:"HYPERVISOR_BYTES_NOT_CAPTURED", needed_evidence:"COMPLETE_HYPERVISOR_BYTES"}` |
| fixed | `unknown/os-kernel` | -- | `{reason:"OS_KERNEL_BYTES_NOT_CAPTURED", needed_evidence:"COMPLETE_OS_KERNEL_BYTES"}` |
| fixed | `unknown/runtime` | -- | `{reason:"RUNTIME_BYTES_NOT_CAPTURED", needed_evidence:"COMPLETE_RUNTIME_BYTES"}` |
| dynamic | `unknown/external-service/` | `external_services` | `{reason:"EXTERNAL_SERVICE_BYTES_NOT_CAPTURED", needed_evidence:"COMPLETE_EXTERNAL_SERVICE_BYTES"}` |
| dynamic | `unknown/physical-component/` | `physical_components` | `{reason:"PHYSICAL_COMPONENT_BYTES_NOT_CAPTURED", needed_evidence:"COMPLETE_PHYSICAL_COMPONENT_BYTES"}` |

The dynamic rows sort by config-key bytes and fixed rows by path bytes; no
other row is legal.  There is no self-exclusion list: section 5.2's all-files
walk and immutable-root rule make an omitted filename unnecessary.
The member shape, five captured-protocol conditions, and exact active-trial-ID lists
live in the closed R-manifest grammar rather than in
uninterpreted role, codec, or row-domain names.  Dynamic captured package
paths are outputs of the frozen enumerator, not operator wording choices.

Section 9 itself is the closed attack-relation registry because this file is an
S_C0 semantic member.  `D_C` does not repeat those rows, attach descriptor
identities, or encode a final-value template.  Their concrete post-inventory
requests and responses are run-dependent internal observations summarized by
the one PREFLIGHT frame, so placing them in `D_C` would create either a temporal
cycle or redundant semantic state.

There is no `positive_replay_recipe` member.  `delta_s0_tv_hex[0]` must equal
lowercase hex of `TV(source_s0)` in section 7 and
must reproduce its displayed case/trial IDs.  Section 7 fixes the selected
source bytes and stream ID; their length and hash derive mechanically.  Section
5.5 fixes the request, response, outcome wires and decision limit.  Repeating
any of those values in `D_C` would add no semantic choice.  The positive remains
a future continuation rather than a descriptor, eliminating the former
temporal and identity cycles.

Because every `D_C` byte is a deterministic projection of C0 plus the immutable
base, hashing or inventorying it would duplicate no history distinction.
Define instead:

```text
C_digest = SHA256(ASCII("ZERO-GROUND-R01C-SEMANTIC-FREEZE") || 00 ||
                  C0_digest)

semantic_freeze_id =
  ASCII("r01c-semantic-") || lowercase_hex_64(C_digest)
```

Dependency order is therefore:

```text
immutable R01B S0/S1 + attacks
  -> this C0 contract, one source row, and 26 attack relations
  -> C0_digest
  -> exact source d0/trial ID, effective order, and independently equal D_C
  -> final S_C closure and ID
  -> gate-R manifest and A_real
  -> P_C run nonce, inventory blob, run ID, launch overlays, source fixture,
     26 internal two-invocation checks, and one compact PREFLIGHT frame
  -> primary run through immutable TERMINAL
  -> fresh-process post-terminal replay request and supervisor outcome
```

The final semantic ID and realization ID are excluded from C0/`D_C` row identity;
the inventory blob, nonce, run ID, launch overlays, derived source fixture,
preflight process observations, and replay exchange are excluded from `A_real`,
the semantic source gate, and its derived-agreement check; run evidence is
excluded from both semantic obligations.  Their constructing code and
rules remain inventoried.  There is no hash, identity, or replay-time cycle.

`S_C` closes only if two independently authored decoders reproduce every exact
value above, the one source row, and the exact section-9 relation table.  Attack
execution is not fed back into S_C.  After R_C and frame zero, P_C derives the
one base/candidate request for every relation, requires two identical
captured-validator responses with the declared first reason, and crosses the
one zero-payload-success or bounded-failure PREFLIGHT frame before any primary
row starts.
Agreement does not establish physical
independence.  Until S_C closes, R_C, P_C, and every implementation/trial
remain prohibited; until P_C closes, the primary run remains prohibited.

## 13. Simultaneous total-system account

There is no scalar score and no tradeoff is erased by another coordinate.

| dimension | R0.1C pre-S result and charge |
|---|---|
| information/distinction preservation | closed responsibilities are specified for F1--F9 and the successor audits; actual run preservation is `UNKNOWN` because none exists |
| persistence | exact B/raw/inventory duties are classified; no new global `MAY_FORGET` is awarded |
| semantic machinery | inherited ~51 MB semantic corpus, this delta, a rebuildable `D_C` projection including a three-string measurement-status constructor checked against 2,080 fixtures and path policies, two decoders, codecs, a linear scanner/derived-index formatter, registries, and attacks are all nonzero |
| cognition | decoder choices are removed, but participant/operator comprehension, error, learnability, and study results remain `UNKNOWN`; the shared-blob and locator model adds concepts |
| authoring | the closed grammar, package/loaded-file inventory, bound-source active-row lists, measurement-status constructor/policy check, ordering ledger, 26 mutation relations plus one failure carrier, and rebuildable `D_C` add review and maintenance burden; no participant study exists |
| query/navigation | selectors plus a full linear scan make exact lookup decidable; rebuilding/validating the optional logical index is charged, and no search cache is persisted in this first candidate |
| runtime | no subject or LAB runtime is measured; hashing and validating a large frame-zero blob, building status maps, and atomically deriving native-only cells will cost time and compute, presently `UNKNOWN` |
| storage | the evidence bound charges every logical byte crossing L, including inventory, preflight, envelopes/raw packs, terminal, and replay exchange; persistent storage may instead retain a smaller source representation only when it regenerates those exact bytes. Semantic source bytes cross once rather than per descriptor, while derived frame encodings, IDs, query fields, closure projections, and replay index need not be separately persisted; physical copies, regeneration compute, and availability remain charged |
| operations | S_C construction/attack, R_C inventory, frame-zero delivery, attack validation, atomic submission/native-cell materialization, overlay validation, deterministic two-channel capture, replay retention, access control, and cleanup are required operations |
| TCB | both decoders, TV/stream codecs, manifest walker, status-map/native-cell builders, attack validator, process supervisor/poll semantics, hash, linear scanner/derived-index builder, collector, normalizer, verifier, runtime, OS, and storage path remain in or adjacent to TCB |
| evolution | explicit namespaces, ordering, schema IDs, and new profile identities prevent silent widening; any new code, event, inventory rule, list rule, or schema requires a new freeze |
| portability | byte formats are language-neutral; unlike software and physical media/failure-domain portability remain `UNKNOWN` until executed evidence exists |
| explainability | records link B, checks, edges, operations, waits, measurements, and raw ranges; human usefulness is still `UNKNOWN` without study |
| information-loss risk | hash-only inventory, missing raw bytes, partial capture, wrong overlay, private decoding, and unknown physical components remain explicit high/unknown risks |

## 14. Where complexity moved; unsupported capability

- Closing `canonical_records` moves meaning from a private decoder into the
  contract, derived closure view, two decoders, validators, and rebuildable
  locator views.
- Closing B shapes moves container choice into namespace-8 event schema, its
  frozen relation, and the compact preflight occurrence/failure carrier.
- Closing failure reasons and list order moves host conventions into registry
  bytes, union/deduplication logic, and ordering tests.
- Closing structured UNKNOWN/UNSUPPORTED text moves path selection into one
  three-string constructor plus the inherited policy and a 2,080-fixture
  validator; it does not turn those texts into a global allowlist.
- Closing gate R moves realization selection into a large self-contained TV
  manifest, manifest walker, inventory frame, hash computation, and overlay
  validator.
- Avoiding per-descriptor semantic duplication moves shared state into frame
  zero and moves availability/navigation responsibility into a same-stream
  verifier plus linear scanner.  It reduces repeated bytes, not the
  information responsibility; an optional derived index moves runtime into a
  rebuild cache rather than persistent history.
- Closing `mm` moves branch interpretation into the total table and frame
  validator; `SELF_CUT` still relocates control logic into the publisher and
  lifecycle supervisor.
- Preserving the submitted/no-submit distinction moves native-only derivation
  into one atomic controller transition and every submitted closure projection.
- Merging stderr and overlength into one outcome moves simultaneous-event
  resolution into the supervisor's fixed poll/capture-turn semantics; the raw
  bounded prefixes still survive.
- Exact replay keeps incidental raw bytes and access-control/retention work; a
  digest does not make them disappear.

The actual target contract, global future completeness, malicious coherent
replacement, freshness, writer authority, replay prevention, concurrency,
power-loss durability, cold recovery, physical capture/delivery, independent
physical failure domains, physical media identity, cache behavior, complete
runtime/OS/kernel/hypervisor/firmware bytes, observer completeness and
perturbation, total human cognition, and unbuilt alternative realizations are
`UNKNOWN` or `UNSUPPORTED`.  Distinct source bytes, `A_real` values, guest
paths, or filesystems do not establish unlike physical realization.

The new grammars specify representability; they do not show that a subject,
apparatus, or operator can realize them within the time/storage bounds.  If S_C
materialization, the once-per-run inventory, or later evidence cannot fit a
bound, the candidate is infeasible and reports no conformance or mechanism
verdict.  No implementation or trial is authorized until a new S gate closes.
