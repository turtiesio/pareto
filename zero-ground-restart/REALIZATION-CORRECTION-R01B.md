# REALIZATION CORRECTION R0.1B — POST-AUDIT EXECUTION PROFILE

## 0. Status, provenance, and claim boundary

R0.1B is an attack-informed correction profile for the failed, unimplemented
`REALIZATION-CONTRACT-R01.md` candidate. It does not edit, reinterpret, or turn
that historical file into a passing specification. The fatal and non-unique
cases retained in `FEASIBILITY-AUDIT-R01.md` are results and remain replay
inputs.

This profile was written after those attacks were known; it has no claim of
builder/breaker independence. At this R0.1B specification freeze:

- no R0.1 or R0.1B subject publisher, recovery reader, controller, tracer,
  evidence-envelope serializer, replay process, or conformance verifier exists;
- no descriptor, adapted-mutation, measurement-path, or literal-oracle registry
  is incorporated, frozen, or credited by this profile; any separately or
  concurrently authored draft remains outside gate `S` until audited;
- no R0.1B subject trial has run; and
- every conformance, performance, portability, cognition, power-loss, and
  physical-realization result is therefore `UNKNOWN` or `UNSUPPORTED` at its
  named scope.

R0.1B remains a finite falsification instrument. Its record, checkpoint,
publication, trace, replay, and packaging mechanisms are candidates to attack,
not an architecture or a proof of total minimality.

The historical inputs retained by this profile are identified by the hashes in
`FEASIBILITY-AUDIT-R01.md`. That audit, rather than any changed copy of a
historical file, is the repair checklist.

## 1. Boundaries and the exact behavioral relation

### 1.1 Laboratory boundary `L`

Backend and mechanism selectors are laboratory configuration. They cross `L`
inside the submitted descriptor and are retained and charged there. They do
not cross the subject service interface `B`:

```text
L_descriptor = {
  semantic_freeze_id,
  realization_id,
  history_production,
  backend,
  mechanism_manifest,
  setup,
  cut,
  requested_payload,
  continuation,
  injected_fault,
  recovery_fixture,
  repetition,
  case_id
}
```

The future descriptor registry is the exhaustive legal domain. There is no
implicit cross-product, grammar union, or unregistered continuation.

### 1.2 Subject interface `B`

For an applicable subject descriptor, the complete ordered `B` history is
exactly one of two tagged productions:

```text
publication_history =
setup(setup)
arm(cut)
inject(injected_fault)
request_publish(requested_payload)
[publish_result]
request_recover(continuation)
recovery_observation

recovery_only_history =
install_recovery_fixture(recovery_fixture)
request_recover(continuation)
recovery_observation
```

A third registered `LAB_ONLY` descriptor production supplies a frozen
malformed envelope, comparator record, measurement fixture mutation, replay
request, or conditional apparatus probe directly at `L`. It has no `B`
crossing, cannot receive a `B_STATE` verdict, and is never inserted into a
subject behavioral comparison. This is how false-attestation, duplicate-frame,
schema-leaf, hash-only replay, and physical-gate attacks remain exhaustive
without fabricating a publication or recovery history.

The typed `recovery_fixture` crosses `B` in full. It declares authoritative
entry kind (`ABSENT`, `REGULAR`, or `SYMLINK`), exact regular bytes or exact
symlink-target bytes, and every auxiliary target entry and its exact bytes.
Thus a truncation, bit flip, coherent substitution, missing entry, or
nonregular entry cannot arrive through an undeclared setup channel. Backend,
fixture-installer implementation, mutation recipe name, and expected label
remain charged `L` configuration and do not replace the crossed fixture bytes.

`publish_result` is absent only when the publisher is killed. Its wire values,
and the recovery values, remain the R0.1 values pinned by the semantic registry.
No selector, checkpoint, trace, diagnostic, timing, PID, trial ID, verifier
result, or measurement uses `B`.

Define the canonical function `BH(d,o)` as the typed encoding, specified in
section 3, of the complete `B` history produced from descriptor `d` and observed
result `o`. Define:

```text
B_input_key(publication d) = typed(PUBLICATION, setup, cut, requested_payload,
                                  continuation, injected_fault)
B_input_key(recovery d) = typed(RECOVERY_ONLY, recovery_fixture, continuation)
B_response(d,o) = typed(publish_result_list, recovery_observation)
```

`publish_result_list` is a typed list of length zero when no publish-result
crossing exists and length one otherwise; no null or implicit sentinel is used.

Two rows are behaviorally comparable iff their `B_input_key` bytes are equal,
their registry applicability permits execution, and their only differing
descriptor coordinates are explicitly paired `L` realization coordinates
such as backend or mechanism manifest. Their required relation is:

```text
B_response(left) == B_response(right)
```

Equivalently, because their registered `B` inputs are byte-identical,
`BH(left)==BH(right)`. The differing `L` descriptors and evidence envelopes are
never merged. This is a conditional realization relation, not equivalence of
the complete `L` histories and not deletion of selector responsibility.

Cross-backend conformance uses this same relation. It never compares the
backend-containing `L` input bytes as though they were equal.

## 2. One complete `L` evidence crossing

Every submitted descriptor produces exactly one external success-or-failure
crossing:

```text
evidence_envelope(exact_envelope_bytes)
```

There is no separate successful raw-output channel. Apparatus error, timeout,
trace loss, malformed control, and bound overrun also return an envelope, with
the applicable failure coordinates. Every byte accepted before a declared
bound is retained; an overrun explicitly denies completeness and identifies
the unretained suffix as unknown.

The envelope is:

```text
ASCII("ZGR01B-ENVELOPE") || 00 || u16be(1) || TV(envelope_map)
```

`envelope_map` has exactly these keys:

```text
canonical_records       typed canonical record stream
raw_trace_pack          opaque exact trace/control/output bytes
raw_measurement_pack    opaque exact timing/environment/allocation bytes
inventory_pack          exact contracts, registries, sources, hashes, versions
status_coordinates      the complete coordinates from section 5
```

Opaque raw fields may contain PIDs, inode values, temporary path spellings,
timestamps, locale-sensitive tool output, and partial bytes. Their framing is
canonical; their observed content need not be repeatable. The canonical record
stream instead uses symbolic identifiers and excludes those variable spellings.
Both are inside the one envelope. A digest or index is not a substitute for an
opaque field's bytes.

## 3. Complete typed value codec

`TV(v)` is recursive and self-framing. Network byte order is used. No other
value encoding is legal.

| Tag | Value | Following bytes |
|---:|---|---|
| `01` | unsigned integer | exactly `u64be(v)` |
| `02` | signed integer | exactly two's-complement `i64be(v)` |
| `03` | byte string | `u64be(n) || n bytes` |
| `04` | UTF-8 text | `u64be(n) || n exact UTF-8 bytes` |
| `05` | false | none |
| `06` | true | none |
| `07` | list | `u64be(count) || TV(item)*` in declared order |
| `08` | map | `u64be(count) || entry*` |
| `09` | structured unknown | `TV(reason_text) || TV(needed_evidence_text)` |
| `0a` | structured unsupported | `TV(reason_text)` |
| `0b` | closed enum | `u16be(namespace) || u16be(code)` |

Every map key is printable ASCII, encoded as `u16be(length)||key_bytes`, unique,
and ordered by unsigned key bytes. Text is not normalized: the retained UTF-8
bytes are authoritative. Controlled identifiers and enum labels use ASCII.
Reasons and needed-evidence text must be nonempty. There is no null, float,
host-width integer, unordered set, duplicate key, NaN, infinity, or bare
placeholder string. A set is an explicitly sorted list under a registry rule.

The only unknown leaf is tag `09`; it always has both nonempty members. The
two-member JSON breaker object is retained as the malformed negative
`MEASURE_UNKNOWN_MISSING_EVIDENCE_NEGATIVE`. A separately registered
`MEASURE_STRUCTURED_UNKNOWN_VALID` uses tag `09`, is schema-valid, and is never
counted as a measurement pass.

Durations and sizes are unsigned integers with their unit fixed by the future
measurement registry. Median is the lower middle order statistic after unsigned
numeric sort. `p95` is the value at zero-based index
`ceil(0.95 * sample_count)-1`. Empty samples are a structured unknown, not zero.

## 4. Trial IDs, ordinals, replay selectors, and control bytes

### 4.1 Trial identity

Before `D_sem` exists, let `s0` be the symbolic case map in semantic gate `S0`.
It contains no exact digest-bearing fixture, trial ID, ordinal, realization ID,
final semantic-freeze ID, or expected answer.  Its provisional identity is:

```text
case_digest = SHA256(ASCII("ZGR01B-CASE") || 00 || TV(s0))
case_id = ASCII("r01b-case-") || lowercase_hex_64(case_digest)
```

After `D_sem` exists, let `d0` be the exact descriptor identity map.  It
contains the case ID, history production, backend, mechanism manifest, exact
`B` inputs or exact recovery fixture, cut, injected fault, and repetition.  It
excludes `semantic_freeze_id`, `realization_id`, expected answers, `trial_id`,
and `ordinal`; otherwise hashing the registry or a realization would feed back
into its row identities.  Then:

```text
trial_digest = SHA256(ASCII("ZGR01B-TRIAL") || 00 || TV(d0))
trial_id = ASCII("r01b-") || lowercase_hex_64(trial_digest)
```

The registry rejects a repeated `trial_id`. Rows sort by unsigned trial-ID
bytes. `ordinal` is the zero-based `u64` position in that exact order. Every
replay request supplies both ID and ordinal; it fails unless the indexed ID,
offset, length, and SHA-256 all agree. An ordinal never silently overrides an
ID.

The `S1` registry retains `d0` as the canonical descriptor template. It does
not retain a prematurely filled complete `L_descriptor`. After `S1` closes,
the launch overlay adds the final `semantic_freeze_id`; after gate `R` closes,
it also adds `realization_id`. The submitted bytes are exactly:

```text
TV({descriptor_template: d0,
    semantic_freeze_id: final_S_id,
    realization_id: final_R_id})
```

Those complete submitted bytes and their hash are retained in the run's `L`
evidence. The overlay fields cannot affect trial identity, `B_input_key`, or
the precommitted oracle. The schema rejects an overlay ID that differs from
the manifests actually packaged with the run.

### 4.2 Neutral checkpoint frames

The exact forty-byte frame is:

```text
5a 47 4e 46 01 ss mm ff || trial_digest[32]
```

`ss` is `J0..J5` as `00..05`. `mm` is invariant `00`, reference mechanism
`01`, omitted mechanism `02`, alternate mechanism `03`, or self-cut placement
`04`. `ff` has bit 0 `NO_ACK_REQUIRED` and bit 1 `SELF_CUT_TARGET`; all other
bits are zero. The only continuation acknowledgement is the single byte `c1`.
These bytes report control position and configured branch only. They never
attest that a syscall occurred or succeeded.

Legacy bytes `a000..a005` are not neutral R0.1B frames. Preserve the original
`PROJECT-1` provenance under canonical ID
`LEGACY_A000_DUPLICATE_NEGATIVE`. A separate
`NEUTRAL_FRAME_DUPLICATE_NEGATIVE` duplicates one complete forty-byte frame.
Neither ID or payload may be reused for the other attack.

## 5. Closed status coordinates

Every result contains all of the following enum coordinates plus typed lists
`failure_reasons` and `needed_evidence`. No coordinate is overloaded to stand
for another.

| Namespace | Code table |
|---:|---|
| `01` applicability | `00 APPLICABLE`, `01 CONDITIONAL_ONLY`, `02 NOT_APPLICABLE`, `03 UNSUPPORTED_HERE`, `04 UNKNOWN` |
| `02` execution | `00 NOT_RUN`, `01 COMPLETE`, `02 CONTROL_UNAVAILABLE`, `03 APPARATUS_FAILURE`, `04 TIME_BOUND_EXCEEDED`, `05 STORAGE_BOUND_EXCEEDED` |
| `03` oracle | `00 ASSERTED`, `01 CONDITIONAL_RETAINED`, `02 NOT_DECLARED`, `03 UNKNOWN` |
| `04` full conformance | `00 PASS`, `01 FAIL`, `02 UNKNOWN`, `03 UNSUPPORTED`, `04 NOT_APPLICABLE` |
| `05` behavioral comparison | `00 MATCH`, `01 DIFFER`, `02 UNKNOWN`, `03 NOT_COMPARED` |
| `06` scope | `00 B_PROCESS_KILL`, `01 L_EVIDENCE`, `02 GUEST_REALIZATION`, `03 CONDITIONAL_FUTURE`, `04 PHYSICAL_OR_POWER` |

Each coordinate is tag `0b` with the listed namespace and code. `scope` is a
sorted list of namespace-`06` enums. Missing evidence is a nonempty sorted list
of typed text, not an unknown spelling embedded in another enum.
`failure_reasons` is a sorted list of closed reason enums; it is nonempty iff
full conformance is `FAIL` and empty otherwise.  The literal-oracle registry
freezes every permitted reason code.  A free-form diagnostic stays in the raw
pack and cannot change the reason oracle.

An alternative can therefore retain a conditional oracle while being
unavailable here:

```text
applicability = UNSUPPORTED_HERE
execution = NOT_RUN
oracle = CONDITIONAL_RETAINED
full_conformance = NOT_APPLICABLE
behavioral_comparison = NOT_COMPARED
scope = [CONDITIONAL_FUTURE]
```

`SELECT_ALT_*` rows use those independent coordinates until an applicable
alternative is actually supplied. The conditional required `B` response stays
in the oracle registry; it is not credited as an executed pass. `POWER_GUARD`
is likewise `UNSUPPORTED_HERE` at physical/power scope, never a process-kill
pass.

## 6. Exact control handshakes

### 6.1 Reference and ordinary mechanism variants

For `J0..J5` cuts, the publisher is launched in blocking-control mode:

1. complete the work preceding a checkpoint;
2. write exactly one complete neutral frame to the frame pipe using
   short-write retry;
3. block reading the acknowledgement pipe;
4. for a checkpoint before the armed target, the controller reads and validates
   the frame, writes exactly `c1`, and the publisher continues;
5. at the target, the controller reads and validates the frame and sends
   `SIGKILL` without writing an acknowledgement; and
6. no publisher operation after the target can begin because the publisher was
   blocked before the signal.

A configured operation that fails emits no later checkpoint. A malformed,
missing, duplicate, extra, or out-of-order frame is an apparatus failure and is
retained. Independent operation facts still decide whether an operation was
entered, returned, omitted, or simulated.

For `NORMAL`, the publisher uses declared nonblocking-control mode: each frame
has `NO_ACK_REQUIRED`, is written to a drained frame pipe, and the publisher
never waits for `c1`. Six bounded frames cannot be treated as semantic output.

### 6.2 `DROP_STAGE_CONTROLLER`

For every non-`NORMAL` descriptor, no publisher is launched and execution is
`CONTROL_UNAVAILABLE`; applicability and conformance follow the frozen row in
the future descriptor registry. Loss of the continuation capability is not a
behavioral match. For `NORMAL`, the publisher uses the same nonblocking mode as
all other normal rows. No hidden controller or continuation acknowledgement is
permitted.

### 6.3 `SELF_CUT`

Target selection and stop responsibility move into the publisher and are
charged there. Frames before the target are nonblocking. At the target the
publisher writes a frame with `NO_ACK_REQUIRED|SELF_CUT_TARGET` and sends itself
`SIGSTOP`. A generic lifecycle supervisor, which is not given the target slot
and does not select by frame, observes the stopped child and sends `SIGKILL`.
It then applies the registered reaping policy. `NORMAL` has no self-stop.

Removing the named stage controller while retaining publisher target logic is
EXTERNALIZE, not deletion of the control responsibility.

## 7. Reaping manifests and observer limitation

`REFERENCE` requires the real parent supervisor's successful wait/reap of the
exact publisher before recovery `exec`. The negative attack that forges a
wait-after-recovery ordering is named
`REAP_ORDER_REFERENCE_FORGERY_NEGATIVE` and is applicable only to a descriptor
whose mechanism manifest is `REFERENCE`; its full-conformance oracle is FAIL.

`NO_PRE_RECOVERY_REAP_BEHAVIORAL` is a separate legal deletion case. After
`SIGKILL`, its supervisor may establish termination without reaping using a
registered pidfd/proc observation, starts and completes recovery, then performs
the exact publisher wait/reap. Its behavioral coordinate compares `B` with the
paired reference row. It is not failed merely because wait follows recovery.

A whole-supervisor `strace`/ptrace observer participates in tracee stop/exit
handling and cannot positively establish deletion of every pre-recovery reaping
responsibility. Under that observer the row may execute and yield a `B` match or
difference, but its reaping-mechanism conformance coordinate is `UNKNOWN` with
passive-observer evidence required. A future passive observer must have its own
frozen trace semantics, loss detection, provenance, permissions, and TCB before
it can change that coordinate. Availability of local tracefs is not evidence
that this gate has passed.

## 8. Replay and retained attack identities

The historical negative and new positive futures have different IDs and
initial information:

- `EVIDENCE_HASH_ONLY_NEGATIVE` receives only a digest and index metadata. It
  must fail exact-byte replay because the retained bytes are absent.
- `EVIDENCE_REPLAY_POSITIVE` receives the complete retained envelope plus the
  validated ID/ordinal index. In a fresh process after the producer exits it
  must return the exact selected canonical and raw byte ranges.

A hash match alone is not positive replay. Failure of ID/ordinal,
offset/length, per-record hash, envelope hash, or bounds agreement is a replay
failure. Reusing `EVIDENCE-REPLAY` for either row is forbidden; that historical
collision remains documented in the audit.

Adapter timeout and signal-mapping futures introduced after R0.1 are new
R0.1B registry candidates, not retroactively incorporated R0 faults. Their
applicability and exact observations must be independently frozen before use.

## 9. Trace window, environment, and descriptor allowlist

The trace launcher starts with a future frozen minimal environment before any
traced `exec`; sanitizing only descendants is insufficient. Dynamic-loader,
locale, timezone, path, credential, and inherited-variable behavior not covered
by that allowlist is retained as TCB or structured unknown. Raw traces are
sensitive evidence and receive explicit access, storage, and retention charges.

At publisher `exec`, the only inherited descriptors are:

| FD | Role |
|---:|---|
| `0` | read-only `/dev/null` |
| `1` | captured `B` publisher-result pipe |
| `2` | captured diagnostic pipe |
| `3` | internal neutral-frame write pipe |
| `4` | internal continuation-ack read pipe, closed for modes that cannot use it |

At recovery `exec`, only FDs `0`, `1`, and `2` exist with analogous roles.
Every other descriptor is close-on-exec or closed before `exec`; subsequently
opened descriptors must be assigned, by the raw trace, to an allowed runtime,
bundle-read, authoritative-state, staging-state, or directory role. A socket,
network operation, console/TTY open, unclassified writable path, inherited
descriptor, or uncaptured output invalidates the trial. Supervisor/tracer
descriptors and all permitted read-only runtime paths must be exhaustively
listed in the future realization manifest.

The raw trace window begins before the supervisor's traced `exec` entry and ends
only after publisher and recovery terminal events, required parent waits, EOF
on every captured channel, and tracer completion. An `OBSERVED_ABSENT`
mechanism fact additionally requires:

- a loss-free trace from publisher `exec` through its terminal event;
- a descriptor registered as reaching the attacked slot;
- a trace-resolved object/FD identity;
- no matching syscall entry in that complete eligible window; and
- agreement with the manifest's omitted branch.

Trace buffer loss, attach gaps, undecoded identities, parser disagreement, or
an ineligible/unreached slot yields structured `UNKNOWN`, never absence. The
trace collector cannot measure its own complete syscall/TCB cost without a new
observer; that total remains an explicit unknown rather than starting an
unbounded observer regress.

## 10. Semantic and realization freeze gates

No subject implementation work or trial is permitted until the semantic gate
is closed.

### 10.1 Semantic gate `S`

Gate `S` has two ordered, retained subgates.  No subject implementation starts
until both close.

`S0` freezes exact bytes and hashes for:

- this correction profile and every pinned historical input;
- the five opaque suite positions and adapter semantic specification;
- the complete symbolic case registry and its sorted stream;
- symbolic adapted-mutation recipes that contain no digest-bearing bytes;
- the expanded measurement-path/schema registry;
- the literal symbolic behavioral/applicability/oracle registry;
- this typed codec, control protocol, status tables, environment policy, and
  apparatus limits; and
- every conditional future retained but not executable.

The semantic seed digest is the hash of R0's canonical filename/length/file-byte
manifest construction over exactly those `S0` members. Define:

```text
D_sem = SHA256(ASCII("ZERO-GROUND-R01B-SUITE") || 00 || semantic_seed_digest ||
               LP(P0) || LP(P1) || LP(C) || LP(Y0) || LP(Y1))
H = SHA256(ASCII("ZERO-GROUND-R01B-RECORD") || 00 || D_sem ||
           u64be(length(P)) || P)
record(P) = D_sem || P || H
```

`S1` then mechanically derives from the frozen `S0` bytes and `D_sem`:

- every exact regular/symlink/absent recovery fixture and auxiliary entry;
- the final descriptor-template registry with exact `B` inputs, final trial
  IDs, ordinals, reachability, and comparison partners, but with neither final
  freeze-ID overlay;
- the exact adapted mutation table, including wrong-suite rehashing; and
- the final literal table of exact expected wire bytes and status coordinates.

All `S1` bytes and derivation machinery are retained.  The final
`semantic_freeze_id` hashes the `S0` manifest, `D_sem`, and R0's canonical
manifest over the `S1` files. `D_sem`, row identities, and
descriptor-template bytes explicitly exclude that final ID and the later
realization ID, so no dependency is cyclic. Any `S1` mismatch with the
precommitted symbolic case or oracle is a semantic-gate failure, not an allowed
repair.

### 10.2 Realization gate `R`

After implementation but before the first subject trial, each unlike software
realization freezes a separate implementation manifest and digest `A_real`.
It includes every loaded publisher, recovery, adapter, controller, trace,
normalizer, serializer, replay, verifier, schema-validator, configuration,
test, runtime entrypoint, and dependency byte available for inventory. Missing
runtime/OS/hypervisor bytes are structured unknowns, not omitted members.

`A_real` is retained in `L` evidence and charged to TCB; it is deliberately not
part of `D_sem`. Thus two unlike implementations may preserve the same semantic
record identity while having different realization digests. Any member change
after gate `R` creates a new realization digest and a new run. Actual physical
identity is not inferred from a distinct `A_real`.

At this profile freeze `S0`, `S1`, and `R` are OPEN: no prerequisite registry is
incorporated or credited here, and all subject implementation bytes are absent.

## 11. Required registry gates; none is frozen by this profile

Before gate `S` closes, four canonical registry families must be created and
independently attacked.  Each family has an `S0` symbolic source and, where it
contains `D_sem`-dependent bytes, an `S1` exact materialization.  This section
specifies prerequisites, not their contents or hashes.

### 11.1 Descriptor registry

Its `S0` source must materialize every legal symbolic case, including its
tagged history production, exact paired setup/payload positions or symbolic
recovery recipe, cut reachability, manifest/backend applicability, fault,
repetition, and comparison rule.  Expected answers are deliberately excluded
from case/trial identity and live in the separately authored literal-oracle
registry linked by case ID.  Its
`S1` form must replace every symbolic recovery recipe with the complete exact
fixture and add final trial ID, ordinal, canonical descriptor-template bytes, exact
comparison partner, and exact wire-oracle linkage.  Only registered pairs are legal;
for the base corpus `ABSENT*` pairs with `P0` and `VALID_P0*` with `P1` unless a
separately named attack says otherwise. Expected process-kill rows have exactly
repetitions `0,1,2`; all non-kill, unreachable, control-unavailable, replay, and
conditional-only rows have exactly repetition `0`. Unreachable rows are
materialized with their exact terminal/error oracle rather than silently
dropped.

The registry stores each case ID, derived trial ID, ordinal, canonical
descriptor-template bytes, comparison partner, expected reachability, and literal
oracle linkage.  Case IDs and trial IDs are separately unique and their
recorded derivations are rechecked; neither is imported from the oracle file.
The sorted registry is the union of subject rows and registered `LAB_ONLY`
rows. `LAB_ONLY` rows have no comparison partner unless their specific
apparatus oracle declares one.

### 11.2 Adapted mutation registry

It must derive mutations from the actual `D_sem || P || H` R0.1B bytes and
materialize, for both valid payloads and guest backends:

- every proper-prefix truncation;
- every single-bit flip with byte and bit indexes;
- missing, append-zero, wrong-semantic-suite, and nonregular cases;
- stale-valid and other-valid coherent substitutions; and
- every newly admitted timeout, signal, I/O, attestation, control, or replay
  attack under a distinct provenance and applicability coordinate.

Wrong-suite recomputes `H` with the R0.1B record tag and changed suite value.
Every recovery mutation emits the complete typed `recovery_fixture` used by the
corresponding `B` production. No R0 byte offset, tag, digest, expected record,
fixture entry, or auxiliary target is copied or installed ambiently.

### 11.3 Measurement registry

It must expand every leaf of all fourteen simultaneous dimensions, including
component role/provenance/dependencies, phase timings, raw-evidence storage,
environment, complete TCB, and `where_is_complexity_now`. The historical 144
breaker paths remain retained attack inputs, not a complete schema. Every new
path has a unique typed path, unit, scope, applicability rule, aggregation rule,
and one mechanically generated leaf-deletion mutation. No missing leaf is
accepted; unavailable knowledge uses tag `09` or `0a`.

### 11.4 Literal oracle registry

It must contain exact `B` responses, status coordinates, applicability,
conditional alternatives, expected attack failure, and smallest-witness order.
It may not call the candidate publisher, recovery parser, adapter, normalizer,
or trace interpreter to generate its answer. Common-mode mutation controls and
their expected failures are registry rows.

## 12. Boundary-scoped classification

R0.1B reports two disjoint verdict namespaces:

### `B_STATE`

- `MUST_SURVIVE_B` requires a minimized collision between registered histories
  that an admitted `B` continuation distinguishes.
- `MAY_REBUILD_B` requires an exact recipe from identified surviving `B` state
  plus a retained specification.
- `MAY_FORGET_B` requires exhaustive no-effect in the registered `B` domain.

### `L_EVIDENCE`

- `RETAIN_L` means an admitted `L` audit/replay future needs the exact observed
  bytes.
- `REBUILD_L` means deterministic reconstruction from retained bytes and a
  named codec/normalizer is possible.
- `FORGET_L` means no admitted `L` future can observe deletion.

Actual raw traces, measurements, failures, and channel bytes are `RETAIN_L`
because `EVIDENCE_REPLAY_POSITIVE` can request them. Normalized facts, counts,
quantiles, indexes, and hashes may be `REBUILD_L` only from the retained bytes
and frozen machinery. These are not automatically global target-contract or
`B_STATE` verdicts. No new global `MAY FORGET` claim is made here.

## 13. Exact apparatus bounds

For one complete R0.1B run:

```text
execution_decision_limit = 1,800,000,000,000 monotonic nanoseconds
total_evidence_limit     = 2,147,483,648 bytes
terminal_envelope_reserve = 1,048,576 bytes
raw_and_canonical_budget  = 2,146,435,072 bytes
```

The monotonic interval begins immediately before the first registered subject
trial is launched. At the first observation at or beyond the decision limit,
the apparatus stops launching rows, terminates the declared process group,
drains already-buffered configured channels, and emits a
`TIME_BOUND_EXCEEDED` envelope. Serialization and safe cleanup may finish after
the decision instant; R0.1B makes no claim of external delivery by 30 minutes.

Before accepting a blob that would exceed the raw-and-canonical budget, the
apparatus stops the current process group and retains the exact prefix already
accepted plus the offending field identity and retained partial bytes that fit.
The reserved terminal envelope records `STORAGE_BOUND_EXCEEDED`, all unrun row
IDs, and structured unknowns for bytes that could not be retained. It never
reports a complete corpus or silently truncates a passing stream. If terminal
metadata itself cannot fit its fixed reserve, the envelope is an apparatus
failure and no conformance claim exists.

No timeout or storage overrun is a subject failure, behavioral match, or
minimality result. It is retained failure evidence.

## 14. Simultaneous total-system and unsupported claims

Every executed realization must populate the future expanded registry for all
fourteen dimensions in the same round. There is no scalar score. Deleting a
mechanism recomputes every coordinate and answers “where is the complexity
now?” in persisted state, code/configuration, human procedure, runtime,
operations, external services, and TCB.

The following remain structured `UNKNOWN` or `UNSUPPORTED` at this profile
freeze and cannot be converted to zero cost:

- correctness, completeness, perturbation, privilege, and total cost of any
  future tracer or passive observer;
- `NO_PRE_RECOVERY_REAP` mechanism deletion under ptrace;
- every unbuilt alternative realization and conditional-only oracle;
- actual participant cognition, task error, learnability, and authoring study;
- complete runtime, OS, kernel, hypervisor, host, controller, and physical-media
  byte counts/provenance where unavailable;
- power-loss durability, cold recovery, physical capture/delivery, independent
  physical failure domains, tmpfs backing, and host cache behavior;
- malicious coherent replacement, freshness, writer authority, replay
  prevention, concurrency, and unregistered future observers;
- the actual target contract, global future completeness, a least total system,
  and contract-independent minimality.

`E` and `T` can at most remain unlike guest-kernel realization paths. Distinct
semantic or implementation digests are not evidence of unlike physical media.

## 15. Execution prohibition and next gate

This profile alone is not executable. The next permitted work is to create and
independently freeze the four registries in section 11, verify their canonical
bytes and hashes, close semantic gate `S`, and only then implement candidate
realizations. A passing implementation, if one later exists, remains an
instrument for attacking the registered total candidates; it is never itself
the architecture.
