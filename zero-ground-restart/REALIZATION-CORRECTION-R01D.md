# REALIZATION CORRECTION R0.1D — COLLISION-CARRYING SUCCESSOR CANDIDATE

## 0. Authority, status, and prohibition

R0.1D is a successor candidate, not an edit to R0.1C.  Its frozen attack
authorities are:

| file | SHA-256 |
|---|---|
| `REALIZATION-CORRECTION-R01C.md` | `ea711583b1d5911ceb759f0b91823d9609acef026a91fdf5b4e4ece1b38f84ef` |
| `FEASIBILITY-AUDIT-R01C.md` | `8fedcc1de885e0f2c45544bed36349553e329fcd209821da5a52bc1ae385109e` |

Both are present in repository commit `9e367b6`; the first was already fixed in
commit `1eca48b`.  Every R0.1C defect C1--C23, its minimized history pair, and
its `CONTRACT_DEFECT_UNDECIDABLE` result remain immutable.  R0.1D may answer an
attack but may not reinterpret either authority into a pass.

Except where this file says **R01D REPLACEMENT**, R0.1C's exact clauses inherit
after the profile lift in section 1.  R0.1B semantic sources and subject B wires
remain unchanged.  R0.1D is still a bounded falsification candidate: it is not
the target contract, a least total system, proof of global future completeness,
or proof of physical persistence.

This file does not close a gate.  Pure contract review, construction of the
future `S_D` artifacts, and construction of bounded history/continuation
carriers are allowed.  After an external freeze, exactly the two S decoders
and the minimal authorization membership writer needed to attempt `S_D` may be
authored as bootstrap machinery; they authorize no target behavior and remain
charged TCB.  No subject, LAB, publisher, recovery reader, adapter, collector,
locator parser, realization verifier, provider, or replay implementation may
be authored or adapted until an exact `S_READY` occurrence for these bytes
exists under section 7.  No realization may enter preflight until its
`R_READY` occurrence exists.  No subject or ordinary LAB trial may start until
`P_D` closes.

## 1. Exact inheritance, profile lift, and digest discipline

### 1.1 Profile lift

For the effective R0.1D corpus, the following substitutions apply to inherited
R0.1C *semantic values*, not to prose citations or frozen attack names:

| inherited semantic value | R0.1D value |
|---|---|
| ASCII protocol prefix beginning `ZGR01C-` | same suffix after `ZGR01D-` |
| role/schema/profile text beginning `R01C-` | same suffix after `R01D-` |
| exact profile text `R01C` | `R01D` |
| newly derived prefix `r01c-case-` | `r01d-case-` |
| newly derived prefix `r01c-` for a trial | `r01d-` |
| newly derived prefixes `r01c-run-`, `r01c-realization-`, `r01c-semantic-` | corresponding `r01d-` prefix |

The literal filenames, hashes, R0.1C attack IDs, old malformed case/trial IDs,
and quoted old wire bytes in the two attack authorities do not change.  The
source row is replaced explicitly in section 10 rather than by textual search.
Namespace numbers, reason codes, status codes, 2 GiB evidence limit, and the
`1,800,000,000,000` nanosecond decision limit do not change.

The effective R0.1D L magic is therefore
`ASCII("ZGR01D-L-STREAM") || 00 || u16be(1)`.  Every other inherited R0.1C
protocol tag is lifted by the first row above.  A mixed C/D tag is invalid.

### 1.2 Exact-target rule for every finite digest

This section is an **R01D REPLACEMENT** for every inherited statement that a
digest or digest-derived text is a unique authority.

Every digest constructor is backed by its exact domain-framed source bytes or
by a lossless representation that regenerates those bytes.  Digest equality
never establishes equality of unequal sources.  In every addressable semantic,
descriptor, realization, inventory, run, stream, envelope, range, request, or
store domain, an existing digest or derived ID bound to unequal backing bytes
causes rejection before overwrite, merge, deduplication, authorization, or
selection.  The existing binding and both unequal targets remain distinguishable
attack evidence; the new target receives no alternate silently chosen ID.

Case and trial construction validates full identity preimages before admitting
the effective registry.  `C_digest`, `A_real`, `inventory_blob_id`, `run_id`,
the primary-stream hash, envelope/range hashes, and request hashes are integrity
checks on already selected exact targets.  They are never sole locators.  The
retained target association in section 8 is authoritative.  If the system
cannot compare exact targets, the gate or continuation is `UNSUPPORTED`; hash
collision resistance is not silently assumed.

No persisted “collision bit” is added.  The unequal target bytes and their
attempted association are the distinguishing information; exact-preimage
comparison, indexing, and rejection are charged to storage, operations, and
TCB.

## 2. Minimal observation grammar

This section is an **R01D REPLACEMENT** for R0.1C sections 4.1--4.3 where the
forms below differ.  All actual values named here are observations unless an
exact constructor is stated.  Canonical container bytes may rebuild; that does
not make their nonderivable leaves rebuildable.

### 2.1 Operation facts

An operation fact has exactly three members:

```text
{
  evidence_sources: list(text from the inherited evidence-source registry),
  fact: text from the inherited operation-fact registry,
  registered_errno: text("NONE") | text("EEXIST_17") | text("EIO_5") |
                    {number: U64}
}
```

R0.1C's `unknown_detail` member is forbidden.  `fact="UNKNOWN"` remains legal
only for a cause-stopped observation and, together with that stop cause,
rebuilds the exact structured-unknown query detail.  The actual fact,
evidence-source list, and registered or unregistered errno remain MUST SURVIVE.
The inherited errno/fact consistency rules and unregistered-errno failure rule
continue unchanged.

### 2.2 B and process observations

`b_observation` has exactly one of these key sets:

```text
{}
{history: nested complete BH_value}
{observed_prefix: list(B events)}
```

An `observed_prefix` is a strict prefix of one legal `BH_value` and is legal
only under a cause-stopped row.  Its structured unknown is rebuilt from the
prefix branch and stop cause; it does not cross L.  Once a complete B event
list has crossed B, it remains `{history:BH_value}` even if normalization,
locator processing, serialization, or another apparatus step later fails.
Neither a parser nor a stop constructor can retract or demote a B crossing.

`process_observation` is exactly:

```text
{
  terminal: list(text from the inherited terminal registry) of length 0 or 1,
  wait_order: list(text from the inherited wait-order registry) of length 0 or 1
}
```

A one-member list carries the exact accepted observation.  An empty list means
that named fact was not accepted before the row stopped and rebuilds the one
cause-selected structured unknown.  The two list cardinalities are independent
because terminal observation and wait observation can stop at different
points.  Every LAB-only row has exactly `["NO_EXECUTION"]` for both members;
R0.1D claims no LAB child-process terminal or wait observation.  A profile that
wants one needs a different capture contract.

### 2.3 Single ownership of comparison results

Each comparison edge's actual result occurs exactly once: the endpoint with
the lower effective global ordinal owns it.  That owner's
`comparison_edge_results` list contains its owned incident edges in unsigned
edge-ID order.  A higher endpoint stores no second copy.  A full-stream scan
locates the owner and rebuilds the result for either endpoint's status and
constituent comparison-check query.

The owner result is still a nonderivable comparator observation and MUST
SURVIVE.  Equal retained B inputs do not license deleting it: a faulty
comparator report and the required report remain different admitted apparatus
histories until a future profile supplies a total trusted constructor.  Prefix
execution ensures an owner envelope exists whenever its higher endpoint does;
an unresolved or unrun higher endpoint gives the owner the exact `UNKNOWN`
result during stop completion.

### 2.4 Positional locator results

Derive the locatable-address sequence by visiting, in this order, the
`b_observation` root, checkpoint values, constituent checks, measurement cells,
operation facts, and the `process_observation` root.  Within a list, visit
ascending list index; within a TV map path, visit ascending map-key bytes.  Edge
results have no locator address.  Let `K(record)` be the resulting finite count.

A raw locator retains the R0.1C four-member shape.  Its `length` must be
positive; an observation with no reported source span uses an empty locator
list, never a zero-length range.

`canonical_records` is now this exact eight-member map:

```text
{
  b_observation: section-2.2 value,
  checkpoint_observations: list(bytes(exactly 40 bytes)),
  comparison_edge_results: list(enum namespace 5) owned by this row,
  constituent_checks: list(constituent_check),
  locator_results: list(list(raw_locator)),
  measurements: list(measurement_cell),
  operation_facts: list(section-2.1 operation_fact),
  process_observation: section-2.2 map
}
```

`locator_results` is the exact chronological prefix of successful locator
results for the derived address sequence.  Position supplies the address, so
no address, ID, parser name, or repeated success flag is stored.  A successfully
reported empty list is an element and differs from an unattempted suffix.

A COMPLETE primary run requires `length(locator_results)=K(record)` for every
row.  A cause-stopped stream permits `0 <= length(locator_results) <= K(record)`.
For a later query at position `i` below the retained length, the exact retained
list is returned.  At or beyond the prefix, the query returns the structured
unknown selected by the stream's stop cause.  There is no missing-position
unknown stored in the record.  Deleting one successful list merges the frozen
`L`/`L'` witness; a digest cannot replace it.

The selected row still determines operation, measurement, check, and owned-edge
positions.  Subject rows have ten operation facts and 1,040 measurement cells;
LAB rows have neither.  Check triples that actually completed are
nonderivable verifier observations and survive.  A stop-filled check is instead
the exact constructor in section 6.  No claim that the whole canonical record
is mechanically derivable survives R0.1D.

## 3. Raw streams and realization-manifest reductions

This section is an **R01D REPLACEMENT** for R0.1C sections 5.1--5.2 where
specified.

### 3.1 One completion bit

Each active raw entry is exactly:

```text
{
  bytes: bytes(exact accepted stream content),
  missing_suffix: bool
}
```

`missing_suffix=false` means that the branch-specific terminal condition was
observed; it is the former COMPLETE shape.  `true` means the accepted bytes are
a strict-or-empty prefix whose terminal condition was not observed; it is the
former PREFIX_ONLY shape.  The Boolean is MUST SURVIVE.  Its structured-unknown
query payload is determined by the row stop cause and is forbidden in the raw
entry.

An inactive declaration is absent from that row's pack.  It is never encoded
as an empty complete entry.  A configured active source may be empty with
either Boolean, preserving terminal-empty versus empty-prefix.  Pack plus
filtered declaration position still derives `stream_id`.

### 3.2 Branch-specific source binding

A raw-stream declaration is exactly:

```text
{
  active_trial_ids: nonempty list(text),
  pack: text("RAW_MEASUREMENT") | text("RAW_TRACE"),
  source_binding:
      {producer_fd: U64, producer_path: text(captured member path)} |
      {producer_path: text(captured member path), relative_path: text} |
      {fixture_output: nonempty printable-ASCII text},
  stream_id: nonempty printable-ASCII text
}
```

There is no outer `producer_path` and no fixture `fixture_recipe`.  Pipe and
run-file producers must be captured executable members; a derived unknown slot
cannot be launched or reaped.  The selected active LAB row supplies its unique
derived-closure recipe, which must contain exactly one output named by
`fixture_output`.  A non-LAB row cannot use the fixture branch.

Expanded uniqueness keys are respectively
`(trial_id,producer_path,producer_fd)`, `(trial_id,relative_path)`, and
`(trial_id,fixture_output)`.  The R0.1C anti-alias rule across branch kinds and
the terminal conditions remain, with “that producer” referring only to the
captured member in the first two branches.  Fixture completion is acceptance
of its last exact recipe byte.

The manifest's five inherited role selectors, member list, and raw-stream list
remain.  R0.1D does not treat uid/gid, ACLs, directory search authority, file
capabilities, mount flags, interpreter state, argv, environment, or physical
placement as if they were in `A_real`.  `A_real` identifies the reported
captured content/mode bundle only.  Launch feasibility and ambient authority
are observed by `P_D` and later apparatus outcomes; complete realization
identity remains UNKNOWN.  A realization that needs ambient bytes or authority
not admitted by the closed protocols is unsupported rather than silently
fixed by the digest.

### 3.3 Source-row closure

The effective source trial in section 10 is active in exactly two declarations
and no others:

```text
{pack:"RAW_MEASUREMENT", stream_id:"measurement",
 source_binding:{fixture_output:"measurement"}}

{pack:"RAW_TRACE", stream_id:"trace",
 source_binding:{fixture_output:"trace"}}
```

Both active-ID lists contain the source trial ID.  No other declaration may
contain it.  This all-and-only rule is checked at `R_D` before the preflight
source payload is constructed.  It removes the temporal dependency on an
unlaunched pipe or run-file producer.

## 4. Frozen semantic members without repeated paths

This section is an **R01D REPLACEMENT** for R0.1C section 5.3's semantic-member
shape and count.

Derive the exact semantic path list by parsing the twelve R0.1B S0 member paths,
then adding `R01B-S1.json` and these six delta paths:

```text
FEASIBILITY-AUDIT-R01B.md
FEASIBILITY-SUPPLEMENT-R01B-RUN-BOUNDARY.md
R01B-BLACKBOX-BREAKER.json
REALIZATION-CORRECTION-R01C.md
FEASIBILITY-AUDIT-R01C.md
REALIZATION-CORRECTION-R01D.md
```

Reject duplicates and sort all nineteen paths by unsigned path bytes.  The
inventory member is:

```text
semantic_members: list(bytes) of exactly length 19
```

Position binds each byte string to the derived path.  A repeated path would be
DERIVE-able and is forbidden.  Exact semantic bytes remain nonderivable.  The
generated R0.1D projection and manifests are not members.

`inventory_blob`, its ID, realization ID, and run ID otherwise retain their
profile-lifted R0.1C constructions, subject to the exact-target rule and the
authorization/store association below.

## 5. Locator acceptance and historical query

This section is an **R01D REPLACEMENT** for R0.1C's locator parser protocol.
Locator processing observes a frozen record; it does not decide whether the
record's logical observations occurred.

### 5.1 Frozen input

Define `observation_record` as the seven-member projection of
`canonical_records` obtained by deleting only `locator_results`.  Before the
first locator invocation for a row:

1. every accepted B, checkpoint, operation, measurement, process, check, and
   owned-edge observation in that prospective envelope is frozen;
2. every raw-pack entry's bytes and completion Boolean are frozen; and
3. stop filling, if applicable, has already produced the exact final
   observation projection under section 6.

No later byte or stop substitution may change those parser inputs.  A parser
result cannot be computed against a candidate prefix and then claimed for a
different retained record.

For address `i`, each of two fresh closed-scope invocations receives exactly:

```text
ASCII("ZGR01D-LOCATOR-REQUEST") || 00 || u16be(1) || TV({
  active_stream_ids: {
    RAW_MEASUREMENT: list(text),
    RAW_TRACE: list(text)
  },
  leaf_address: list({map_key:text} | {list_index:U64}),
  observation_record: the frozen seven-member projection,
  raw_measurement_pack: the frozen nested list,
  raw_trace_pack: the frozen nested list
})
```

The active-stream lists and address retain their R0.1C derivations.  The only
successful response is the profile-lifted response tag followed by
`TV(list(raw_locator))`, EOF, empty stderr, exit zero, and closed-scope cleanup.
Both response byte strings must be identical.  The decoded list must be sorted,
unique, in bounds, active-source-valid, and select the addressed retained
target bytes.  Adjacent spans in one source are coalesced.  A checkpoint result
must be nonempty and its selected concatenation must equal the exact 40-byte
checkpoint observation.  For other addresses, an empty list is a truthful
realization-reported absence of a link.

R0.1D does not promote the parser into its own semantic oracle.  Outside the
independently checked checkpoint equality, completeness and causal adequacy of
reported links remain UNKNOWN.  The retained lists support exact navigation
and explain what this realization reported; they do not prove that every raw
cause was found.

### 5.2 Append and failure

A decoded result is appended to `locator_results` only after both invocations
close successfully and the exact storage projection containing that list fits.
Appending the whole list is atomic.  The next address is not attempted first.

Any launch, write, response, stderr, exit, cleanup, disagreement, bounds,
source, ordering, checkpoint, or storage failure fixes the applicable stop
cause.  Every already appended list survives.  The failed and later positions
are absent; no structured unknown is copied for them.  Logical observations
and raw bytes accepted before the parser failure remain accepted.  In
particular, a complete B history remains the complete `history` branch.

If a run stop was already fixed before a prospective envelope reached locator
processing, no locator invocation is required for that envelope and its
retained prefix may be empty.  If the stop occurs during locator processing,
the exact prior prefix survives.  A stream that reaches COMPLETE instead
requires a full `K(record)` prefix for every envelope.

Later queries read the retained result directly.  A diagnostic rerun is a new
observation and may test the captured parser, but it cannot define, replace, or
reconstruct the historical list.  Parser response framing may rebuild from the
retained list and fixed codec; the list itself is MUST SURVIVE.  Parser code,
launcher, runtime, bounds checking, dual execution, storage projection, and
checkpoint validation remain charged TCB.

For the section-10 source row, `K=5`: B root, three constituent checks, and
process root.  Its complete envelope therefore contains exactly five retained
empty locator lists.

## 6. Total stop and completion constructor

This section is an **R01D REPLACEMENT** for R0.1C's underspecified
`pending_frames`, `stop_frames`, terminal association, and
`empty-nonderivable-prefix` rules.

### 6.1 Accepted state and fixed visit order

Submission remains one atomic transition.  A subject submission materializes
all thirteen exact `NATIVE_ONLY` cells; a LAB submission materializes the two
`["NO_EXECUTION"]` process lists.  Those derived values are accepted at the
transition.  No other nonderivable observation is accepted by submission
alone.

After submission, accepted state consists only of the following exact
occurrences and values:

- B events in B chronological order;
- checkpoints in observed chronological order;
- operation results in inherited operation-registry order;
- non-native measurement results in unsigned path order;
- terminal then wait process facts;
- raw byte prefixes per active source and the independent terminal-observed bit
  per source;
- owned comparison results when their two required B inputs have closed;
- constituent-check results in unsigned selected-check-key order; and
- locator result lists in the section-5 address order.

Concurrent raw sources retain one exact byte prefix and terminal bit each; pack
serialization still uses filtered stream-ID order.  An acceptance is atomic at
the displayed value granularity.  A transient computation, provisional parser
output, or unclosed channel is not accepted state.

### 6.2 Cause-selected fills

Let `c` be one of `APPARATUS_FAILURE`, `TIME_BOUND_EXCEEDED`, or
`STORAGE_BOUND_EXCEEDED`.  Let `STOP[c]` be the exact positional
`stopped_before_capture_map` pair and `RAW[c]` the exact `raw_suffix_map` pair.
The maps remain derived semantic rules; their repeated payloads do not enter
the reduced fields below.

For a submitted row, `finalize_stop(row,state,c)` preserves every accepted
value and applies exactly these rules to every unaccepted responsibility:

1. **B.** No accepted B event gives `{}`.  A nonempty strict legal prefix gives
   `{observed_prefix:prefix}`.  A complete legal production gives
   `{history:BH_value}`.  No event is deleted.
2. **Checkpoints.** Retain exactly the accepted chronological list; there is no
   placeholder for a checkpoint that did not occur.
3. **Owned edges.** Retain each accepted comparator result.  Every unaccepted
   owned edge position is `enum(5,UNKNOWN)`.
4. **Checks.** Retain each accepted constituent-check triple.  Every
   unaccepted check position is exactly
   `{failure_reasons:[], needed_evidence:[STOP[c].needed_evidence],
     status:enum(4,UNKNOWN)}`.  No other controlled text may be selected by
   this fill rule.
5. **Measurements.** Retain every accepted cell and all submission-native
   cells.  Every other path whose policy admits UNKNOWN receives the exact
   tag-09 value `STOP[c]`.  A missing `NATIVE_ONLY` value would have prevented
   submission and is not fillable.
6. **Operations.** Retain every accepted operation fact.  Every unaccepted
   position is `{evidence_sources:[], fact:"UNKNOWN",
   registered_errno:"NONE"}`; its query detail derives as `STOP[c]`.
7. **Process.** Retain each accepted one-member list.  Each unaccepted field is
   `[]`; its query value derives as `STOP[c]`.  LAB submission values are never
   emptied.
8. **Raw.** Retain each active source's accepted bytes.  Its Boolean is false
   iff its exact branch terminal was accepted, otherwise true.  A true entry's
   suffix query derives as `RAW[c]`.  Inactive sources remain absent.
9. **Locators.** Retain exactly the accepted locator-result prefix.  Do not fill
   its suffix.

These nine rules, the selected row, and exact accepted state determine one
byte string.  Captured check triples are deliberately not reconstructed from
other observations: they are actual verifier outputs.  Their semantic
adequacy remains in TCB, while stop-created triples are distinguishable by the
single exact rule above.

For an already submitted prior row awaiting a comparison partner, the same
constructor preserves its completed observations, fills only unresolved
owned-edge/check positions, and leaves its per-row execution COMPLETE.  The
run terminal still supplies `c` for its missing-evidence query.  No completed
prior observation is relabeled as a failed execution.

### 6.3 Empty nonderivable prefix

For submitted effective row `k`, define:

```text
empty_nonderivable_prefix(k,c) =
  finalize_stop(row_k, submission_state_only, c)
```

For a subject this contains the thirteen native cells, empty B/checkpoint and
process observations, UNKNOWN fills for every non-native measurement,
operation, owned-edge, and check position, empty bytes with
`missing_suffix=true` for every active source, and no locator result.  For a
LAB row it contains empty B/checkpoint/measurement/operation values, the two
one-member `NO_EXECUTION` process lists, the check and owned-edge fills, empty
active raw prefixes, and no locator result.  Thus the former undefined phrase
now selects one exact envelope payload after `c` and row `k` are known.

### 6.4 Complete finalization

`finalize_complete(row,state)` is legal only when every required actual B,
process, operation, measurement, owned-edge, and check responsibility has an
accepted value, every active raw source has `missing_suffix=false`, and the
locator prefix has length `K(record)`.  It preserves those exact values and
adds no status, ID, path, completion payload, or unknown text.

All comparison partners must have finalized before a complete envelope can
cross.  Envelopes still cross in effective ordinal order.  A complete run has
exactly 6,317 envelopes under the effective registry in section 10.

### 6.5 Terminal association and closure projections

The two terminal payload shapes remain the profile-lifted R0.1C shapes.  The
Boolean meaning is now total:

- `true`: the stop cause is assigned to the final submitted envelope;
- `false`: no envelope receives the cause.

For false with `k < N`, the cause occurred before row `k` submission.  For
false with `k = N`, all rows were submitted and the cause occurred during
pending-envelope finalization or before COMPLETE terminal emission; the unrun
suffix is empty.  The latter is a run-scoped failure, not a fictional
prelaunch row.

Define:

```text
pending_frames(k,q,c) =
  ordinal-ordered ENVELOPE frames for every submitted row represented by q,
  using finalize_stop on unresolved responsibilities and preserving all
  accepted state

stop_frames(k,q,p,c) =
  pending_frames(k,q,c) followed by the ENVELOPE for submitted row k obtained
  from finalize_stop(row_k,p,c)

unassigned_stop_projection(k,q,c) =
  already-crossed primary prefix || pending_frames(k,q,c) ||
  stop_tail(k,c,false), for 0 <= k <= N

submitted_stop_projection(k,q,p,c) =
  already-crossed primary prefix || stop_frames(k,q,p,c) ||
  stop_tail(k+1,c,true), for 0 <= k < N
```

Here `k` is the submitted count before row `k`; at `k=N` there is no row `k`.
`q` and `p` are exact accepted-state values under section 6.1, not free-form
serializer descriptions.  `unassigned_closure_bound(k,q)` and
`submitted_closure_bound(k,q,p)` are the maximum exact lengths over the three
causes.  The unused inherited set `X` is deleted.

Before each submission, both the unassigned projection and every
`empty_nonderivable_prefix(k,c)` submitted projection must fit.  Before each
value, raw byte, terminal bit, check triple, or locator list is accepted, the
exact prospective projections must fit.  Logical component bytes are replaced
by their one envelope serialization rather than double-counted.

After the last row, the apparatus reserves both
`unassigned_stop_projection(N,q,c)` for every `c` and the exact
COMPLETE-terminal plus post-replay projection.  A cause fixed before COMPLETE
terminal emission selects the unassigned `k=N` branch.  Failure of the L
emitter to write a precharged envelope or terminal leaves the exact incomplete
prefix and supports no completed result.

The cause precedence remains explicit apparatus failure, then the at-or-beyond
time sample, then projected storage.  The first fixed cause is immutable.  This
constructor is finite because schemas, positions, accepted prefixes, raw bytes,
and controlled texts are all exact at each check; it does not assume a maximum
future native value.

## 7. Authorization occurrences

R0.1C correctly required actual `S` and `R` checks but retained only their
deterministic targets.  This section is an **R01D REPLACEMENT** for those gate
closure semantics.  Successful occurrence is represented by membership, not by
a repeated Boolean or a hash that could exist without execution.

### 7.1 Exact target carriers

Let:

```text
S_target = TV(the exact nineteen-element semantic_members byte list)
R_target = TV(the exact realization_manifest value)
```

Their path/schema rules are already in the governing semantic bytes.  A
persistent authorization store has the following logical nesting:

```text
semantics: list({
  target: bytes(S_target),
  realizations: list({
    target: bytes(R_target),
    runs: list(run association from section 8)
  })
})
```

Semantic rows sort and are unique by exact `S_target` bytes.  Realization rows
sort and are unique by exact `R_target` bytes within their semantic parent.
Exact byte equality, not an ID, selects a row.  Physical deduplication or a
content index is allowed only when the lossless targets and association
reconstruct; a digest lookup must compare the complete target and reject
ambiguity.

### 7.2 `S_READY` occurrence

`S_D` runs both required independently implemented decoders in separate closed
scopes on the exact target, requires byte equality for every R0.1D projection,
source row, inherited-oracle conversion, attack relation, and constructor, and
cleans both scopes.  Only then may the authorization controller atomically
insert `{target:S_target, realizations:[]}` if no equal row exists.

Row presence is the one durable `S_READY` occurrence.  A failed or interrupted
check inserts nothing and restores the exact pre-attempt authorization state.
Repeated success for byte-identical `S_target` merges because this contract
permits no query for the count or timing of successful gate executions.  An
unequal target never merges, even under an equal digest.

No implementation-authoring action is authorized unless it checks exact
`S_target` membership at that action.  The controller capability used for the
check is execution-scoped and revoked afterward.  R0.1D does not claim to
observe authorship outside this declared controller; organizational provenance
and human compliance remain UNKNOWN.

### 7.3 `R_READY` occurrence

`R_D` requires the exact semantic parent to exist, performs the profile-lifted
R0.1C inventory walk, role/source validation, exact-target comparisons, and
loaded-file checks on `R_target`, and closes its verifier scope.  Only then may
the controller atomically insert the exact realization child.  Child presence
under that parent is the durable `R_READY` occurrence.  It authorizes `P_D` for
that exact pair and no other.

Failure inserts no child and leaves no live token, lease, verifier state, or
future-visible cache mutation.  One semantic row may contain multiple unequal
realization targets.  Equal reported target bytes intentionally merge; a claim
that they are unlike physical systems remains UNKNOWN because those physical
facts are not in `R_target`.

The semantic and realization rows may be physically compacted into later
accepted frame-zero occurrences only if exact target membership and all future
authorizations still reconstruct.  Until then they are MUST SURVIVE.  Their
controller, two decoders, verifier, atomic insert, target comparator, durable
recovery, cleanup, and authorization checks are TCB and nonzero operations.

## 8. Minimal retained-run association

This section is an **R01D REPLACEMENT** for the ambient used-tuple set and
hash-selected retained-stream binding.

### 8.1 Direct run key and nested state

The inventory's 32-byte `run_nonce` is renamed conceptually `run_key`; its wire
member name remains `run_nonce` so no second copy is added.  It is a direct
chosen token, not a digest and not a claim of entropy.  Its authority is the
store's atomic global unused-to-reserved transition.

Each realization child contains:

```text
runs: list({
  crossings: list({bytes: bytes, eof: bool}) of length 1..3,
  key: bytes(exactly 32)
})
```

Runs sort and are unique by `key`, and a key is unique across the entire
authorization store, not merely within one realization.  It is never rebound
or deleted while any retained future can address it, including after an
incomplete or failed run.  The nesting supplies exact semantic and realization
association; no parent ID is stored.

`crossings[0]` is the primary L-channel prefix, `[1]` the post-terminal replay
request channel when begun, and `[2]` its outcome channel when begun.  Each
`bytes` value is the exact accepted prefix and each `eof` Boolean is the
independent channel-closure occurrence.  An absent list position means that
channel never began; a present empty prefix differs from absence.  Valid frame
or message parsing plus EOF derives every phase, success, and failure state, so
no phase enum, sealed bit, `P_READY`, stream ID, run ID, or request-hash key is
stored.

### 8.2 Reservation and append

`RUN_RESERVE(S_target,R_target,run_key)` requires exact `R_READY` membership and
a globally unused key.  Before any `P_D` side effect, it atomically inserts:

```text
{key:run_key, crossings:[{bytes:bytes(""),eof:false}]}
```

A duplicate key is rejected before a byte crosses or a process starts.  A
reserved key stays consumed after failure; otherwise an old failed run and a
new run can form an ABA collision.  This membership, rather than an ambient
nonce ledger, is the reuse fact.

`RUN_APPEND(run_key,channel_index,expected_length,suffix,eof_transition)`
locates the exact nested row by the direct key, requires the channel index to be
the current or immediately next legal position, compares the current exact
length, and atomically appends the accepted suffix.  `eof_transition=true`
also changes that channel's Boolean exactly once in the same commit.  No append
is legal after EOF or to a sealed primary stream.  If a smaller physical source
representation is used, its profile-lifted exact regeneration rule is part of
`S_target` and append must still preserve the same logical crossing.

The complete successful PREFLIGHT frame parsed inside primary crossing zero is
the `P_D` success occurrence.  Only a prefix containing frame zero, the exact
zero-payload PREFLIGHT frame, and no failure terminal authorizes the first row
submission.  No separate P bit exists.  Crossed failure bytes remain evidence,
never a live grant.

Acceptance of the primary terminal's last byte and primary EOF seals the exact
logical primary source by grammar.  While addressable it cannot be appended,
replaced, rebound, or resolved by hash alone.  An incomplete prefix remains
MUST SURVIVE but has UNKNOWN resumability and cannot be acquired as a completed
run.

### 8.3 Acquisition and reset

`RUN_ACQUIRE(run_key)` is legal only when the first crossing has EOF and parses
as one closed primary run.  It returns a fresh, request-scoped, read-only,
offset-zero byte view of that exact primary target.  The provider request uses
`run_key`; derived `run_id` and primary hash are integrity checks only.

Acquisition, cursors, caches, transactions, capability transfer, and cleanup
may not mutate the logical authorization/run store.  Before a completed
provider-failure outcome crosses, all request-scoped processes and handles must
be gone and state reachable by any permitted future request must be
future-observably equivalent to its pre-invocation state, including deadline-
relevant cache effects.  A file, database, or CAS realization must roll back or
isolate such state.  If it cannot, the mutation is additional MUST SURVIVE
information and this profile permits no completed outcome.

Failed S/R checks and provider attempts restore exact prior logical state.
`RUN_RESERVE` is the exception because reservation itself is the admitted
persistent occurrence.  Store code, exact comparators, global unique insert,
compare-and-append, crash recovery, prefix parser, snapshot provider, reset
path, access control, physical storage, and availability are charged.  Power-
loss durability and independent physical failure domains remain UNKNOWN.

### 8.4 Selectors and launch overlay

Every R0.1D replay selector replaces inherited `run_id:text` with
`run_key:bytes(exactly 32)`.  The key selects the exact nested run; the inventory
rebuilds `run_id` for display and integrity checking.  A selector missing the
key, containing an extra run ID, or resolving outside its exact parent is
invalid.

The launch overlay is reduced to:

```text
{
  descriptor_template: d0,
  run_key: bytes(exactly 32)
}
```

The controller resolves the key, verifies the parsed frame-zero semantic and
realization targets against its exact parents, and rebuilds semantic,
realization, and run IDs.  Repeating those three derived texts in every overlay
would add no selection responsibility.  The subject-facing identity
measurement values still expose their derived texts under the frozen schemas.

## 9. Total continuation supervisor

This section is an **R01D REPLACEMENT** for the inherited replay and PREFLIGHT
phase ordering wherever the old clauses leave a launch, deadline, provider, or
terminal transition unordered.  It changes no public reason-code namespace.

### 9.1 Launch commitment

Every closed process role is started with a supervisor-owned, bounded,
one-shot launch-status channel.  The selected executable has committed only
after it has loaded, accepted exactly its declared descriptors, emitted
`ASCII("ZGR01D-LAUNCH-READY") || 00 || u16be(1)`, and closed that channel with
no trailing byte.  The supervisor validates the token before enabling any
role-specific input or treating an exit as a process observation.

A failure before that commitment is a launch failure.  No `process_exit`
member crosses, even if an operating-system child briefly existed, and every
spawned child or helper must still be reaped.  After commitment, every exit or
signal, including an immediate exit 127, is a process-exit observation and the
one inherited truthful exit record is required.  This rule applies identically
to the replay process, PREFLIGHT roles, verifier, locator parser, and fixture
roles whenever their inherited protocol records launch versus process exit.

The ready token and channel are deterministic internal machinery and MAY
REBUILD or MAY FORGET after the corresponding public outcome has crossed.
Their launcher, descriptor handoff, channel framing, validation, reaping, and
commitment state machine are nevertheless TCB and runtime cost.

### 9.2 One pre-action decision turn

For request crossing, primary-release waiting, provider acquisition, process
launch, and request writing, each supervisor turn obtains one joint poll result
containing already-observed explicit phase failure/readiness and one monotonic
clock sample.  It chooses exactly the first applicable branch:

1. an already-observed explicit phase failure;
2. `clock >= deadline`;
3. one enabled nonblocking phase action.

The selected action and any bytes or result it accepts close that turn; there
is no second clock sample within it.  If an action accepts the final request
byte, its EOF close is attempted in the same turn.  Close success commits EOF;
close failure fixes the phase-specific failure with the full accepted count.
The clock becomes eligible again only on the next turn.

Consequently, when the final byte is ready and the sampled clock equals the
deadline, branch 2 wins: no byte crosses and the retained count is `L-1`.  If
the final byte was accepted on an earlier below-deadline turn, same-turn EOF
success or failure wins even if the next clock sample is beyond the deadline.
The provider request writer and every PREFLIGHT writer use this same rule.
The inherited stdout-before-stderr-before-exit capture-turn ordering remains
unchanged after launch commitment.

### 9.3 Exact terminal-to-outcome phases

Acceptance of the primary terminal's last byte fixes its terminal value.  The
primary emitter then performs its already-precharged EOF transition, which
sets `crossings[0].eof=true`; a failure leaves only the exact incomplete
crossing and produces no completed continuation.  Starting with that last
terminal byte, one monotonic deadline covers these phases in this order:

1. post-terminal replay request crossing and EOF;
2. the primary-release barrier;
3. `RUN_ACQUIRE(run_key)` and provider validation;
4. replay launch commitment;
5. replay-process request writing and EOF;
6. response/stderr/exit capture;
7. closed-scope cleanup and reset; and
8. replay outcome crossing and EOF.

The primary-release barrier reaps every primary producer and helper and
revokes every primary writer, inherited descriptor, mutable capability, and
direct readable mapping before acquisition succeeds or replay launches.
Physical erasure is not claimed.  An explicit seal/release failure selects
inherited code 6 with no replay-process exit.  A deadline reached while waiting
selects code 3 with no process exit and zero process-write count.  If time was
fixed while the already-precharged boundary request was crossing, only its
deterministic closure completes; provider acquisition and launch are skipped.
Failure to close a crossing or reap a required scope leaves an unsupported
request-only prefix rather than a fabricated completed outcome.

The provider receives the selected exact parent association and `run_key` and
must return a fresh, read-only, offset-zero view of `crossings[0].bytes`.  A
stream digest is a check only.  Before the provider phase can complete, the
controller exact-compares the acquired view with the selected sealed bytes;
unequal length or content is provider failure, never an alternate run.

The outcome is associated with the request by the enclosing run row and the
sole chronological positions `crossings[1]` and `crossings[2]`.  A request hash
does not select an exchange.  The outcome prefix and EOF are appended only to
that run.  A second exchange for the same run is outside R0.1D.

### 9.4 Corrupt-provider classification

The inherited replay response grammar has these exact interpretations:

- inner `PASS` is well formed only when the replay process's full-stream hash
  equals the requested check hash and its exact checked bytes equal the
  selected sealed source;
- inner `FAIL` carries the process's actual full-stream hash `H'`, which need
  not equal the requested check hash `H`;
- a well-formed `FAIL` with `H' != H`, or any exact checked-view mismatch,
  deterministically selects outer code 6; and
- malformed inner framing, impossible lengths, trailing bytes, or a response
  inconsistent with the process's actual computation selects inherited code
  5, not code 6.

Code 6 therefore has two disjoint public forms.  Its prelaunch form has the
inherited empty response prefix, zero process-write count, and no process-exit
record.  Its postlaunch corrupt-provider form has the full process-write count,
the exact retained well-formed `FAIL` response, empty stderr, and one truthful
exit-zero record.  Any partial or malformed postlaunch response retains its
exact accepted prefix and truthful postcommit exit observation under the
applicable inherited failure code.  `FAIL` with `H' == H` remains the inherited
inner negative result and selects outer code 0; digest equality alone still
cannot authorize unequal bytes under section 1.2.

Provider failure may complete only after the reset condition in section 8.3.
A source that mutated reachable database, file, CAS, cursor, cache, or timing
state and could not restore future-observable equivalence has not completed
this branch.  Its additional state must cross a later contract or the
continuation is unsupported.

### 9.5 PREFLIGHT inheritance

PREFLIGHT uses the launch-commitment and one-turn rules in sections 9.1--9.2,
and the same response-capture and cleanup rules, but has no primary-release or
retained-stream-provider phase.  Its exact timer begins at the inherited
PREFLIGHT start occurrence and covers launch, request write/EOF, capture,
cleanup, and result crossing.  Only its complete successful zero-payload frame
inside the reserved primary crossing is the `P_D` occurrence described in
section 8.2.

## 10. Effective semantic projection and source row

This section is an **R01D REPLACEMENT** for the inherited branch-partial oracle
conversion, delta source, and `D_C` profile-dependent values.  It adds no
execution result to semantic identity.

### 10.1 Branch-total inherited-oracle conversion

`R01B-TO-R01D-ORACLE-1` first selects the row kind from membership in the two
closed frozen registries.  The 3,028 literal-oracle rows are SUBJECT.  The
3,288 retained holdout rows after the two inherited evidence-replay exclusions
are LAB.  Membership in both, neither, or a third layout is invalid.

For a SUBJECT row, the converter requires
`expected.status_coordinates` to contain exactly these eight string-labelled
coordinates: `applicability`, `behavioral_comparison`, `execution`,
`failure_reasons`, `full_conformance`, `needed_evidence`, `oracle`, and
`scope`.  It maps the five scalar labels and every scope label through the
frozen namespace tables, maps every failure label through namespace 7, retains
the two lists from that same map, and rejects any unknown, duplicate, or
misordered value.  The row's check and edge expectations are retained.

For a LAB row, the converter requires exactly the six coordinate members
`applicability`, `behavioral_comparison`, `execution`, `full_conformance`,
`oracle`, and `scope`; every scalar or scope element must be the exact
`{code,label,namespace}` triple selected by its coordinate.  It takes
`failure_reasons` and `needed_evidence` from the `expected` root, validates
every reason's code/label against namespace 7 and every text against the
controlled set, and inserts those two lists.  It separately validates every
constituent check's status triple, reason code/label pairs, and needed-evidence
list.  No lists are copied from an invented coordinate location.

Both branches emit the exact inherited eight-member typed status value and the
positional expectations required to verify the reduced record.  The emitted
aggregate must also equal recomputation from retained check and edge
expectations.  Label, code, namespace, list location, count, or aggregate
disagreement fails `S_D`; a decoder may not repair the frozen input.  The
section-10.2 source row does not pass through this converter and has its exact
direct oracle below.

### 10.2 One replacement source descriptor

The effective delta source identity is:

```text
source_s0 = {
  attack_kind: text("EMIT_FIXED_REPLAY_SOURCE"),
  family: text("EVIDENCE_REPLAY"),
  fixture_recipe: text("R01D_REPLAY_SOURCE_1"),
  history_production: text("LAB_ONLY"),
  logical_id: text("EVIDENCE_REPLAY_SOURCE_R01D"),
  origin: text("R01D"),
  repetition: U64(0),
  semantic_profile: text("R01D")
}

TV(source_s0) = hex(
  080000000000000008000b61747461636b5f6b696e64040000000000000018
  454d49545f46495845445f5245504c41595f534f55524345000666616d696c
  7904000000000000000f45564944454e43455f5245504c4159000e66697874
  7572655f726563697065040000000000000014523031445f5245504c41595f53
  4f555243455f310012686973746f72795f70726f64756374696f6e04000000
  00000000084c41425f4f4e4c59000a6c6f676963616c5f6964040000000000
  00001b45564944454e43455f5245504c41595f534f555243455f523031440006
  6f726967696e04000000000000000452303144000a72657065746974696f6e
  010000000000000000001073656d616e7469635f70726f66696c6504000000
  000000000452303144)

source_case_id =
  "r01d-case-9905205e07177d41236220bf201d32bac84a62c0dffd1b7b2bbe2b6d89027452"

source_d0 = {case_id:text(source_case_id), lab_input:source_s0}

source_trial_id =
  "r01d-5e0407de7966387691161282cf696e9706a3fc2e530e6d91456022903fe85876"
```

The displayed TV value is exactly 290 bytes; line breaks are presentation only.
The case and trial constructors are the profile-lifted inherited domain-framed
constructors and must independently reproduce both IDs from the displayed
bytes.  Digest equality is still subordinate to exact target equality.

Starting from 6,318 R0.1B rows, delete the same two malformed historical
evidence-replay case IDs named in R0.1C and add this row.  The result is 6,317
rows: 3,028 SUBJECT and 3,289 LAB.  All retained trial IDs begin `r01b-`; the
new ID begins `r01d-`, so its zero-based effective global ordinal is 6,316.
No stored old ordinal is consulted.

The source fixture has exactly two outputs:

```text
trace       = ASCII("R01D-HOLDOUT-TRACE") || 00
measurement = ASCII("R01D-HOLDOUT-MEASUREMENT") || 00
```

`trace` is 19 bytes, hex
`523031442d484f4c444f55542d545241434500`, SHA-256
`f3cbdbfcbc1ef426147753d79c9ca3939b9e38082a08956e97cbedd6bd581b23`.
`measurement` is 25 bytes, hex
`523031442d484f4c444f55542d4d4541535552454d454e5400`, SHA-256
`425d5baff740fd9939fda12b34da21cccee84a45f30fb773c7ea2ebc0d916f37`.
The hashes are checks, not selectors.

Its canonical record is exactly:

```text
{
  b_observation:{},
  checkpoint_observations:[],
  comparison_edge_results:[],
  constituent_checks:[
    {failure_reasons:[],needed_evidence:[],status:enum(4,PASS)},
    {failure_reasons:[],needed_evidence:[],status:enum(4,PASS)},
    {failure_reasons:[],needed_evidence:[],status:enum(4,PASS)}
  ],
  locator_results:[[],[],[],[],[]],
  measurements:[],
  operation_facts:[],
  process_observation:{terminal:["NO_EXECUTION"],
                       wait_order:["NO_EXECUTION"]}
}
```

The three check positions are, in unsigned check-key order,
`ATTACK_ORACLE/EVIDENCE_REPLAY/EMIT_FIXED_REPLAY_SOURCE`,
`LAB_BOUNDARY_ISOLATION`, and `LAB_FIXTURE_SCHEMA`.  Its raw measurement and
trace packs each contain their one active entry with the exact bytes above and
`missing_suffix=false`; all inactive declarations are absent.  Its derived
status is exactly `APPLICABLE`, `NOT_COMPARED`, `COMPLETE`, empty failure
reasons, `PASS`, empty needed evidence, `ASSERTED`, and `[L_EVIDENCE]` in the
eight-member status-map order.  This row has no subject process, comparison,
measurement, operation, B, or checkpoint observation.

### 10.3 Exact derived projection

`D_D` remains a transient, rebuildable five-member projection with exactly the
inherited top-level members:

```text
controlled_text_registry
effective_descriptor_registry
failure_reason_registry
measurement_registry_delta
realization_slot_registry
```

The controlled-text, failure-reason, and realization-slot values are the
R0.1D-profile-lifted inherited values.  The effective descriptor registry has
the same two exclusions and its one `delta_s0_tv_hex` element is the
concatenation of the displayed source hex.  The measurement delta makes these
explicit replacements in the inherited operation order:

- schema and contract-profile constants become
  `R01D-MEASUREMENT-PATHS-1` and `R01D`;
- the derived display run-ID pattern becomes `^r01d-run-[0-9a-f]{64}$`;
- the effective trial-ID pattern becomes `^r01[bd]-[0-9a-f]{64}$`;
- every replay-selector branch replaces `run_id` by required `run_key`;
- the JSON surface form of `run_key` is exactly 64 lowercase hex digits and
  the TV selector constructor bijectively decodes it to the section-8
  `bytes(exactly 32)` field; and
- the replay-consistency rule list replaces hash-only run selection with exact
  nested target plus direct-key selection, and adds successful locator-prefix,
  launch-commitment, deadline-turn, provider-reset, and single-owner-edge
  consistency.

No other inherited measurement-registry byte changes.  For base-fixture
synthesis, a replay-selector `oneOf` still chooses its first branch, uses zero
for offset and length, and now uses 64 zero hex digits for `run_key`; TV
materialization converts only that field to 32 zero bytes.  The converter is
part of the semantic rule and is checked by both decoders; it is not an
ambient JSON convention.

The nineteen semantic members in section 4, including this file's frozen
bytes, define the successor C0 digest with the inherited length-framed manifest
constructor after changing its domain to
`ASCII("ZERO-GROUND-R01D-S0-DELTA") || 00`.  `D_D`, generated JSON, hashes,
semantic IDs, realization IDs, inventories, run keys, run crossings, source
fixture materialization, PREFLIGHT observations, and replay outcomes are not
additional semantic members.  The profile-lifted semantic-freeze constructor
uses domain `ASCII("ZERO-GROUND-R01D-SEMANTIC-FREEZE") || 00` and the resulting
C0 digest; it does not include its own output.

Two independently authored decoders must reproduce byte-identical `D_D`, the
6,317-row effective registry, both oracle branches, the source row, all
constructors, and section 11's attack registry before `S_D` may insert the
authorization row.  Decoder agreement is an observed bounded check, not proof
that the implementations or physical failures are independent.

## 11. Attack registry and gate placement

The frozen R0.1C relation table remains an adversarial archive.  Its 26 literal
attack IDs and historical witnesses do not become R0.1D conclusions.  Each is
replayed against the effective R0.1D candidate after these exact carrier lifts:

- `R01C_GATE_R_SEMANTIC_FIXTURE_ALIAS_NEGATIVE` mutates the second fixture
  output to the first while retaining distinct pack/stream declarations; the
  expanded `(trial_id,fixture_output)` collision is rejected;
- `R01C_RAW_PREFIX_MARKED_COMPLETE_NEGATIVE` replaces
  `missing_suffix=true` by false while retaining the independent carrier fact
  `source_terminal_observed=false`;
- `R01C_REPLAY_OLD_R01B_ENVELOPE_NEGATIVE` uses the complete R0.1D source
  payload, including five locator results, as its positive base;
- `R01C_RUN_ID_MISSING_NEGATIVE` deletes required `run_key` from the effective
  selector; the historical name remains only for archive continuity;
- every source selector uses the section-10.3 hex surface and its exact
  32-byte TV conversion; and
- pending-edge, terminal-association, source-status, and source-binding bases
  use sections 2, 3, 6, and 10 rather than their superseded R0.1C shapes.

All other relation operands receive only the section-1 profile lift.  If an
operand cannot be constructed under these rules, its replay is unsupported
and its gate cannot close; a validator may not silently skip it.  This gives
exactly 26 lifted archive relations.

The following 23 successor relations are normative.  `S` means two semantic
decoders evaluate the finite constructor relation before `S_READY`; `R` means
the realization verifier evaluates the manifest/source relation before
`R_READY`; `P` means two fresh closed-scope preflight invocations exercise the
realization behavior before the successful PREFLIGHT frame.  A pair is the
smallest retained carrier presently known, not a claim of global minimality.

| attack ID | gate | minimized colliding histories after the attacked simplification | future-observable requirement |
|---|---|---|---|
| `R01D_C01_WRITE_READY_AT_DEADLINE` | P | final request byte ready with sampled time `deadline-1` versus `deadline`; deleting the sample/precedence makes both the same pre-write state | first accepts byte plus same-turn EOF; second retains count `L-1` and times out |
| `R01D_C02_PROVIDER_EOF_AT_DEADLINE` | P | provider final request byte accepted below deadline versus merely ready at deadline | same turn commits EOF/failure in the first; deadline wins before write in the second |
| `R01D_C03_LAUNCH_PRECOMMIT_EXIT` | P | child exits 127 before ready token versus after validated ready-token EOF | first is launch failure with no public exit; second has a truthful exit record |
| `R01D_C04_LIVE_PRIMARY_AT_DEADLINE` | P | primary-release barrier completes just before deadline versus remains live at deadline | only the first may acquire/launch; the second is code 3 with no process exit |
| `R01D_C05_CORRUPT_PROVIDER_STREAM` | P | exact selected bytes versus one unequal provider byte with well-formed inner `FAIL(H')` | exact branch follows inner result; unequal branch is outer code 6 postlaunch |
| `R01D_C06_PROVIDER_SIDE_EFFECT` | P | failed provider leaves reachable state unchanged versus changes one later-readable byte/cache timing fact | only the reset-equivalent branch may emit a completed provider-failure outcome |
| `R01D_C07_KN_TERMINAL_ASSOCIATION` | S | after all `N` submissions, COMPLETE terminal crosses versus an apparatus cause occurs before terminal | second uses unassigned stop at `k=N`; it is not COMPLETE or a nonexistent submitted row |
| `R01D_C08_COMPLETE_B_PARSER_FAILURE` | P | complete B recovery byte `00` versus `01`, followed by the same locator-parser failure | both retain their full `{history:BH_value}` and the later B query distinguishes them |
| `R01D_C09_PROVISIONAL_LOCATOR_INPUT` | P | locator `L` computed on frozen final observation `x` versus provisional `x'` later stop-filled to `x` | only the first result may append for the retained record |
| `R01D_C10_LOCATOR_RESULT_DELETE` | P | successful empty locator list versus unattempted position, and successful `L` versus `L'` | positional retained result answers the later query without rerunning the parser |
| `R01D_C11_LOCATOR_ADEQUACY_UNKNOWN` | S | identical retained reported links under an adequate versus incomplete causal parser | R0.1D reports exact navigation but leaves causal completeness UNKNOWN |
| `R01D_C12_AUTHORIZATION_OCCURRENCE` | P | exact S/R target bytes merely present versus the corresponding nested success membership present | implementation/preflight authorization succeeds only for the membership history |
| `R01D_C13_RUN_KEY_REBIND` | P | key `K` reserved to exact run prefix `p` versus a failed row deleted and `K` rebound to unequal `q` | later `RUN_ACQUIRE(K)` must return `p` or its retained incomplete state, never `q` |
| `R01D_C14_EQUAL_DIGEST_UNEQUAL_TARGET` | P | unequal exact targets carrying one injected equal digest versus equal targets | unequal targets reject merge/selection; the test digest double does not weaken runtime SHA checking |
| `R01D_C15_NONDERIVABLE_LEAF_DELETE` | S | two accepted B, check, raw, operation, process, or locator values differing in one actual leaf | the corresponding future query returns different values, so only framing/path/status payloads may rebuild |
| `R01D_C16_INACTIVE_RAW_ABSENCE` | S | inactive source absent versus active terminal-empty source `{bytes:"",missing_suffix:false}` | declaration/pack query distinguishes absence from a completed empty stream |
| `R01D_C17_UNKNOWN_PRODUCER_PATH` | R | captured producer member versus an unrepresented path with otherwise equal declaration | only the captured member can supply a legal completion/reap obligation; other branch rejects |
| `R01D_C18_SOURCE_EXTRA_FUTURE_STREAM` | R | source row active in exactly trace/measurement fixtures versus one extra active or pipe/file declaration | only all-and-only fixture binding constructs the source preflight base before execution |
| `R01D_C19_RAW_PREFIX_TERMINAL_FALSE` | S | byte `52` with source terminal unobserved versus the same byte with terminal observed | `missing_suffix` is respectively true versus false; the independent carrier prevents invention |
| `R01D_C20_ORACLE_BOTH_LAYOUTS` | S | one valid SUBJECT layout, one valid LAB layout, and either with its list location/enum triple corrupted | each valid branch converts exactly; the corresponding corrupted branch rejects |
| `R01D_C21_TOTAL_STOP_FILL` | S | submission-only accepted state under each of three causes, plus an accepted-value variant at every position class | `finalize_stop` yields one exact projection and preserves every accepted variant |
| `R01D_C22_LAB_PROCESS_FIXED` | S | ordinary LAB row with `NO_EXECUTION` pair versus author-selected terminal/wait text | only the fixed pair is admitted; a different LAB capture contract would be a new semantic target |
| `R01D_C23_UNREPORTED_LAUNCH_CONTEXT` | P | equal reported content bundles with launch authority available versus unavailable | `A_real` may merge only the reported bundle; physical sameness is UNKNOWN and preflight observes success/failure |

The table order is unsigned `attack_id` order.  Counts are exact: eight `S`,
two `R`, and thirteen `P` successor relations.  `S_D` also checks that every
lifted archive relation is constructible; `R_D` performs the two R rows;
`P_D` performs the 26 lifted archive relations and thirteen P rows, exactly 39
relations, in that order by attack ID.  Each P relation retains the inherited
two-fresh-invocation equality requirement.  Its successful zero-payload
PREFLIGHT frame is valid only after all 39 pass.  The eight S and two R rows
are not credited again as zero-cost P checks.

The equal-digest P row uses a captured, preflight-only digest double returning
one fixed 32-byte value for two unequal targets, then exercises the same exact
comparison and selection path used after a runtime digest lookup.  The double,
injection boundary, and proof that it cannot be selected in ordinary operation
are R-manifest members and TCB.  This tests the collision branch without
claiming a known SHA-256 collision.

No relation receives a descriptor row, case ID, or trial ID.  Static relation
definitions live in these semantic bytes; exact run-dependent requests and
responses live only in the PREFLIGHT crossing.  A passing bounded relation is
evidence against its named simplification, never proof that the candidate is
the quotient of all contract-permitted histories.

## 12. Persistence verdicts and forcing witnesses

These verdicts concern information responsibility under the declared R0.1D
boundary.  They do not predeclare fields, records, layers, or physical media.
A physical representation may combine responsibilities if its decoder
preserves the same distinctions.

### MUST SURVIVE

| information responsibility | smallest forcing witness or future |
|---|---|
| exact semantic target plus its successful membership while it authorizes work | C12: identical target bytes without versus with the actual `S_READY` occurrence permit different implementation-authoring behavior |
| exact realization target, semantic-parent association, and successful membership while it authorizes preflight | C12 with the R child: equal bytes without versus with `R_READY` must reject versus admit `P_D` |
| each reserved direct run key and its exact semantic/realization association | C13: deleting a failed reservation permits ABA rebinding and changes later `RUN_ACQUIRE(K)` |
| chronological boundary-crossing prefixes, independent EOF occurrences, and their run/channel association | C1, C2, C4, C7 and the post-terminal query distinguish equal byte prefixes with different closure or phase histories |
| every accepted nonderivable B event and its chronology | the frozen recovery `00`/`01` pair and C8 produce different later B queries even under the same parser failure |
| every accepted checkpoint byte value and its observation order | a later checkpoint query and locator equality check distinguish a one-byte checkpoint change |
| every accepted comparison result, once at its lower-ordinal owner | equal endpoint B values with a faulty `MATCH` versus `DIFFER` report remain distinct apparatus histories; deleting both copies loses the report |
| every accepted constituent-check triple | identical underlying observations with two admitted verifier reports produce different check/explanation queries |
| every accepted operation fact, evidence-source set, and registered or numeric errno | the inherited unregistered-errno witness distinguishes actual numeric errno from `NONE`; a faulty reported fact remains observable |
| every accepted native or structured measurement value | a later path query distinguishes a one-leaf value change; the path itself can derive from position |
| each accepted actual process terminal/wait value | two subject exits or wait orders answer the later process query differently; LAB's fixed pair is derived at submission |
| every active raw byte prefix and its terminal-observed Boolean | C19 distinguishes equal byte `52` with terminal absent versus present; C16 distinguishes inactive absence from active terminal-empty |
| the chronological prefix of successful positional locator lists | C10 distinguishes successful empty from unattempted and `L` from `L'`; rerunning is not historical reconstruction |
| accepted nonderived failure/outcome bytes, counts, stderr, and truthful postcommit exit observations | C3--C6 distinguish launch, timeout, corrupt-provider, and malformed-process histories that later explanation queries expose |
| exact author-selected realization member bytes/modes, source declarations, dynamic configuration, and association needed to regenerate `R_target` | deleting a selected member while keeping its digest merges exact inventory replays; C17/C18 distinguish source obligations |

“Survive” permits a lossless smaller code or embedding in a later crossing.  In
particular, an S/R row may be compacted into a later retained run only if the
exact target, nesting, success occurrence, and authorization behavior still
reconstruct for targets with and without runs.  Until that equivalence is
shown, the logical memberships remain.

### MAY REBUILD

The following may be regenerated from the MUST information plus the exact
semantic specification: TV/container framing; frame lengths and integrity
hashes; case, trial, semantic, realization, inventory, and display run IDs;
effective ordinals; semantic paths bound by position; repeated check/edge
keys; the nonowner edge view; status coordinates and aggregate lists; run
phase and `P_D` success from parsed crossings; structured unknown details for
stopped operation/process/raw/locator queries; canonical JSON `D_D`; replay
index entries; locator response framing from a retained list; source fixture
binding recipe at the R-manifest site; and launch overlays from descriptor
template plus run key.

Each rebuild has an identified specification above.  The decoder, scanner,
prefix parser, exact comparator, aggregation logic, and regeneration CPU are
not zero complexity.  If any specification or source bytes cease to survive,
the corresponding verdict reverts to MUST SURVIVE or the capability becomes
unsupported.

### MAY FORGET

Only these bounded classes presently have no permitted future observable after
their stated closure:

- provisional locator output that never passed both invocations and never
  appended;
- failed S/R attempt internals after no membership or boundary output was
  produced and exact prior logical state was restored;
- request-scoped provider cursors, handles, caches, and transactions after the
  reset-equivalence condition and completed outcome;
- the internal launch-ready token after the public launch/outcome distinction
  has crossed;
- nonwinning clock samples after the selected reason/count has crossed, because
  R0.1D exposes no timestamp query; and
- duplicate IDs, paths, owner-edge copies, derived unknown payloads, phase
  flags, and status maps that the grammar never admits in the first place.

This is not permission to erase incomplete boundary prefixes, used run keys,
failed outcomes that crossed, physical state with later effects, or semantic
specification bytes.  Crash-resume behavior for an incomplete reserved run is
UNKNOWN; therefore R0.1D makes no MAY-FORGET claim for it.

## 13. Simultaneous total-system account

No coordinate is collapsed into a weighted score.

| dimension | R0.1D candidate result and charged cost |
|---|---|
| information/distinction preservation | the 49 bounded archive/successor relations and the responsibility ledger are explicit; completeness for unenumerated permitted futures remains UNKNOWN |
| persistent state | exact nested S/R occurrence membership, used direct keys, boundary prefixes/EOF, and nonderivable accepted leaves survive; hashes, paths, status, indexes, and duplicate views rebuild |
| semantic machinery | nineteen semantic members, two branch-total decoders, codecs, registries, total stop/complete functions, 49 relations, exact-target rules, and JSON-to-TV selector conversion are nonzero |
| human cognition | fewer repeated payloads/paths/IDs coexist with new positional ownership, nested authorization, crossing parsing, and gate distinctions; comprehension, error rate, and learnability are UNKNOWN without a study |
| authoring burden | exact source bytes, both oracle branches, total phase order, relation carriers, source bindings, and every changed schema must be maintained; no participant data exists |
| query/navigation burden | direct key plus positional scan answers exact queries; historical locators are retained, but causal completeness of noncheckpoint links remains UNKNOWN |
| runtime | exact full-target comparisons, dual decoder/validator runs, 39 preflight relations, prefix parsing, full-stream owner lookup, dual locator calls, reset, and cleanup are charged |
| storage | duplicate paths, edge copies, unknown payloads, and IDs are removed; exact targets, authorization memberships, keys, crossings, locator lists, and actual leaves are retained without an asserted byte total |
| operations | atomic global reserve, compare-and-append, snapshot acquisition, rollback/isolation, reaping, monitoring, backup, and recovery are required; staffing and availability are UNKNOWN |
| trusted computing base | controller, store, exact comparators, two decoders, manifest verifier, codecs, prefix parser, supervisor, clock/poller, launcher, provider/reset path, locator parser protocol, collector, and physical storage all remain |
| evolution | unequal semantic or realization targets create distinct rows; migration/compatibility across profiles and garbage collection of unreachable rows remain UNKNOWN |
| portability | file, database, or CAS implementations may realize the same logical interface if exact atomicity/reset behavior holds; no unlike-physical pair has yet supplied evidence, and power-loss portability is UNKNOWN |
| explainability | retained observations, owner results, locators, terminal/outcome bytes, and derived status expose why a bounded result occurred; locator causal adequacy and external organizational causes remain UNKNOWN |
| information-loss risk | exact backing bytes and nonrebindable keys remove hash-only/ABA loss in the model; corruption, correlated faults, power loss, deletion policy, and cold independent readback remain UNKNOWN |

### Where the complexity moved

| apparent simplification | complexity now located in |
|---|---|
| delete repeated unknown payloads | cause-selected semantic constructors and query-time reconstruction |
| delete semantic paths from members | frozen path derivation, positional validation, and ordered scans |
| retain one edge result | global owner rule, full-stream lookup, and derived per-endpoint views |
| delete locator addresses/status flags | address-order derivation and prefix-length semantics; locator result bytes themselves remain |
| demote all digest IDs | exact backing targets, full comparison, ambiguity rejection, and larger store/index duties |
| delete S/R/P Boolean flags | atomic nested membership and exact crossing-prefix parsing |
| delete run phase/sealed enums | channel-position/EOF grammar, prefix parser, and crash-recovery validation |
| delete fixture recipe from each R binding | selected LAB S0 row, derived-closure resolver, and all-and-only R validation |
| reduce raw completion to one Boolean | branch-terminal observation and source-specific capture/reap machinery |
| reduce process facts to zero/one lists | launch commitment, supervisor phase order, and cause-selected query reconstruction |
| replace hash-selected run IDs with one direct key | global uniqueness, permanent anti-rebind membership, access control, and key-bearing selectors |
| permit unlike file/database/CAS realizations | each must implement the same exact snapshot, atomic append, rollback, and future-equivalence obligations; none is credited free |

### Mandatory attack disposition

DELETE and MERGE are represented by the ledger witnesses and all 49 relations.
DERIVE and RECOMPUTE license only the section-12 identified outputs.
COLLIDE is explicit in each successor pair and the frozen archive carriers.
FUTURE is the named query/action in the last column.  EXTERNALIZE is blocked by
provider reset and exact nested store accounting.  REALIZE is permitted only
behind the same logical interface and remains empirically unproved.  COGNITION
is charged and unmeasured.  TCB is enumerated above.  After every deletion, the
preceding table says where its machinery or responsibility moved.

## 14. Gate order, research exception, and present status

The only legal order is:

```text
freeze these semantic bytes and the nineteen-member manifest
  -> construct two independent S decoders and the bounded declarative corpus
  -> S_D agreement plus eight S relations
  -> durable S_READY membership
  -> implementation authoring under exact S membership
  -> R_D inventory plus two R relations
  -> durable R_READY child membership
  -> reserve a globally unused run key
  -> P_D: 26 lifted plus thirteen successor runtime relations
  -> successful PREFLIGHT crossing
  -> source and ordinary primary rows
  -> immutable terminal
  -> fresh post-terminal replay continuation
```

Before `S_READY`, one exception is allowed solely to satisfy the ZERO GROUND
research method: an external, nonauthorizing falsification instrument may read
the frozen semantic bytes, enumerate finite declarative histories/futures, and
report representation collisions.  It may not implement a subject, LAB role,
candidate decoder, controller, store, parser, provider, publisher, collector,
or gate; its output cannot close S/R/P and is not a semantic member.  Its code,
search bound, relation encoding, and failures are reported as research TCB.

R0.1D is presently **SPECIFIED CANDIDATE / NO GATE RESULT**.  Its external
file digest and repository commit, rather than a self-referential embedded
hash, establish any later freeze.  The target contract, global
history quotient, physical durability, incomplete-run resumption, locator
causal adequacy, cognition, operations feasibility, and unlike-realization
evidence remain UNKNOWN.  No implementation or passing run exists merely
because this candidate is specified.
