# REALIZATION CONTRACT R0.1 — PRE-IMPLEMENTATION DRAFT

## 0. Status and claim boundary

This is a bounded, pre-implementation falsification contract. It repairs one
defect in R0: an implementation that omitted an operation was able to emit the
same externally visible frame that R0 defined as proof that the operation had
succeeded. No R0.1 implementation or result exists at freeze time.

The byte record, pathnames, calls, checkpoints, controller, tracer, and
comparators below are candidate mechanisms to attack, not an architecture.
Passing R0.1 cannot establish global minimality, power-loss durability, human
comprehension, or unlike physical realization.

R0.1 retains R0's smallest opaque positions:

```text
P0 = empty       P1 = 00
C  = empty       Y0 = empty       Y1 = 00
adapter(P0,C)=Y0                 adapter(P1,C)=Y1
```

The controlled reference record remains `D || P || H`, exactly as in R0 except
that `D` binds this contract and its R0.1 bundle. This reuse isolates the
operation-attestation question. It does not revive the falsified claim that the
in-band copy of `D` is necessary.

The incorporated R0 specification is the exact file with SHA-256
`3bdaa119942ef994e4ef0cf1c570d4518a2531bc102505065d967fed08522f15`;
only its explicitly cited record and fault definitions are incorporated. Let
`LP(X)=u32be(length(X))||X`, `Q=SHA256(this exact R0.1 file)`, and `A` be the
SHA-256 of R0's canonical length-prefixed bundle-manifest construction applied
to the frozen R0.1 bundle. Then:

```text
D = SHA256("ZERO-GROUND-R01-SUITE" || 00 || Q || A ||
           LP(P0) || LP(P1) || LP(C) || LP(Y0) || LP(Y1))
H = SHA256("ZERO-GROUND-R01-RECORD" || 00 || D || u64be(length(P)) || P)
record(P) = D || P || H
```

The only authoritative and staging names are `state.bin` and `.state.tmp`.
The manifest bytes, file ordering, filenames, individual hashes, `Q`, `A`, and
`D` are mandatory retained evidence.

## 1. Two boundaries; no unnamed projection

R0.1 declares two different systems and never calls both of them “the
history.”

### 1.1 Behavioral interface `B`

`B` is the explicitly declared service port of the publisher/recovery subject,
not a name for the whole laboratory perimeter. The cut coordinator, reaping
logic, operation observer, and their control channels are placed on the inside
of the outer laboratory boundary `L` below. Crossings of the `B` service port
are, exhaustively and in order:

```text
select(backend, mechanism_manifest)
setup(ABSENT_CLEAN | VALID_P0_CLEAN |
      ABSENT_TMP | VALID_P0_TMP)
arm(J0 | J1 | J2 | J3 | J4 | J5 | NORMAL)
request_publish(P0 | P1)
[publish_result]
request_recover(C)
recovery_observation
```

`publish_result` is absent when the publisher is killed. Otherwise it is
exactly one of:

```text
COMPLETE                         = 10
ERROR(slot, source, errno)       = 11 || u8(slot) || u8(source) || i32be(errno)
```

Slot codes are acquisition `01`, write `02`, file-fsync `03`, replacement
`04`, directory-fsync `05`, and control `06`. `source=00` means an observed
kernel return and `source=01` means a declared wrapper simulation that did not
enter the named kernel call. `errno` is the positive Linux errno number. The
recovery observation is exactly R0's `ABSENT=00`, `REJECT=01`, or
`OK(Y)=02 || u32be(length(Y)) || Y`.

No checkpoint, operation receipt, pipe byte, trace line, timing, diagnostic,
or verifier verdict uses the `B` service port. Those channels are internal to
`L` and are exported only in the complete `L` evidence crossing below. Any
implementation that also sends one to the service observer has changed `B`;
the bytes must then be added to the behavioral history and the contract
refrozen.

### 1.2 Laboratory boundary `L`

`L` encloses `B`, the launcher, independent syscall observer, literal oracle,
normalizer, collector, and serializer. Its complete crossing history is:

```text
submit(exact_trial_descriptor_bytes),
one of {
  evidence(exact_canonical_trial_record_bytes),
  apparatus_failure(wait_status, exact_stdout, exact_stderr,
                    exact_partial_artifact_bytes),
  apparatus_timeout(exact_stdout, exact_stderr,
                    exact_partial_artifact_bytes)
}
```

The launcher captures every byte on every configured output descriptor. An
unconfigured descriptor, network report, inherited control channel, or visible
console output invalidates the run. Thus no external report is silently
reclassified as instrumentation.

The canonical `L` record contains the complete ordered `B` history plus the
complete control, operation, wait, trace, and measurement records. Two deletion
variants normally have different full `L` histories. R0.1 never merges those
histories. It separately asks whether both realize the same required relation
at `B`, while charging their different `L` evidence and all fourteen total-
system coordinates. Equality of a `B` projection is not a claim that the full
laboratory histories are equivalent or that a mechanism is free.

## 2. Neutral slot program

The reference publisher has these ordered slots:

| Slot | Work before the neutral checkpoint |
|---|---|
| `J0` | publisher exists; no staging open or mutation |
| `J1` | acquisition slot ended and exactly half the new bytes were written |
| `J2` | all new bytes were written with short-write retry |
| `J3` | pre-selection stabilization slot ended; staging descriptor closed |
| `J4` | authority-selection slot ended |
| `J5` | namespace-stabilization slot ended |
| `NORMAL` | all configured work ended and publisher exited |

An internal checkpoint frame says only
`SLOT_END(trial_id, Jn, branch=PRESENT|ABSENT)`. `PRESENT` means the manifest
selected the mechanism; it is not a claim that an operation occurred or
succeeded. A failed configured operation emits no later checkpoint. The frame
is consumed by the internal cut coordinator and is retained in the `L` record.
It is never a `B` crossing.

In the reference manifest the acquisition slot uses exclusive creation,
`J3` uses file `fsync`, `J4` uses same-directory atomic replacement, and `J5`
uses directory `fsync`. In a deletion manifest the corresponding slot is an
explicit no-op and emits `branch=ABSENT`. Therefore an omitted call can never
emit a success attestation for that call.

At an armed `J0..J5`, the coordinator receives the neutral frame, sends
`SIGKILL`, observes termination, and—unless the reaping attack says otherwise—
successfully reaps the publisher before recovery starts. `NORMAL` sends no
signal. All cuts are process-kill cuts with the same running guest kernel and
mounted filesystem.

## 3. Truthful operation facts

For exclusive open, file `fsync`, replacement, directory `fsync`, `SIGKILL`,
reaping, and recovery `exec`, the evidence contains all three of:

1. the frozen mechanism manifest (`PRESENT` or `ABSENT`);
2. the component's self-report, explicitly labeled `SELF_REPORT`; and
3. an independently collected syscall/control trace with entry, normalized
   object identity, return value/errno, and ordering.

The normalizer must track pathname and descriptor identity rather than count
unrelated calls made by the runtime. A fact receives exactly one value:

```text
OBSERVED_SUCCESS
OBSERVED_KERNEL_ERROR(errno)
SIMULATED_ERROR_WITHOUT_KERNEL_ENTRY(errno)
OBSERVED_ABSENT
UNKNOWN(reason, needed_evidence)
```

`OBSERVED_ABSENT` requires a complete trace window and a manifest selecting the
absent branch. A missing/incomplete trace is `UNKNOWN`, never absence. A
self-report alone cannot yield `OBSERVED_*`. A disagreement among manifest,
self-report, neutral frame, and trace makes the trial fail and all affected
facts `UNKNOWN`; it may not be retried out of the evidence.

Injected wrapper failures are not called filesystem failures. Successful guest
`fsync` return is not called physical persistence. Reaping is observed only by
a successful wait operation for the exact publisher identity. Stage-control
occurrence is the ordered receipt of a neutral checkpoint followed by the
declared signal/control action; a contract-shaped byte alone is not proof.

For the reference manifest, the required live-kernel recovery matrix is old at
`J0..J3` and new at `J4`, `J5`, and `NORMAL`. In `ABSENT_CLEAN`, old is
`ABSENT` and new is `OK(Y0)`; in `VALID_P0_CLEAN`, old is `OK(Y0)` and new is
`OK(Y1)`. An occupied-staging exclusive-open error preserves old. A simulated
write, file-fsync, or replacement error preserves old; a simulated directory-
fsync error occurs after selection and live-kernel recovery is new. These are
process-kill observations only.

## 4. Candidate manifests and deletion comparison

The mandatory manifests are:

```text
REFERENCE
NO_FILE_FSYNC
NO_DIRECTORY_FSYNC
NO_EXCLUSIVE_CREATE       # uses create/truncate in the acquisition slot
NO_REPLACE                # authority-selection slot is a no-op
NO_PRE_RECOVERY_REAP      # reap only after recovery exits, for cleanup
DROP_STAGE_CONTROLLER     # no replacement cut mechanism
SELF_CUT                  # cut responsibility moved into the publisher
```

`SELF_CUT` is an EXTERNALIZE control, not a deletion: checkpoint selection,
signal logic, and their TCB have moved. `DROP_STAGE_CONTROLLER` must return an
`evidence` record whose exact `trial_status` is `CONTROL_UNAVAILABLE` for any
non-`NORMAL` descriptor before claiming a comparable trial; inability to
execute a future is `UNKNOWN`, not a pass and not `NO_WITNESS`.

For every other manifest, the comparator:

1. uses identical suite, backend, setup, requested payload, cut, recovery
   continuation, repetition index, and injected-fault descriptor;
2. verifies from the independent trace that the reference operation occurred
   where required and the deleted operation did not occur;
3. compares the complete ordered `B` histories byte-for-byte;
4. retains both complete, deliberately unequal `L` records; and
5. recomputes every total-system coordinate for each manifest.

A differing `B` history is minimized by crossings, input bytes, cut ordinal,
fault ordinal, then unsigned lexical canonical record. If all enumerated `B`
histories match, the result is `NO_BEHAVIORAL_WITNESS_IN_R01`, never
`MAY_FORGET` outside R0.1. A missing trace, unreachable cut, or noncomparable
failure is `UNKNOWN`. A difference establishes only a responsibility capable
of preserving the distinction, never the named syscall or process.

## 5. Exhaustive bounded corpus

`ABSENT_TMP` and `VALID_P0_TMP` contain an existing zero-length regular
`.state.tmp`; that is the smallest occupied-staging setup. All directories are
otherwise private, contain no symlink or hard link, and start on one mount.

For both available guest backends `E=ext4(/tmp)` and `T=tmpfs(/dev/shm)`, the
corpus contains:

- `REFERENCE`, `NO_FILE_FSYNC`, `NO_DIRECTORY_FSYNC`, `NO_EXCLUSIVE_CREATE`,
  `NO_REPLACE`, and `NO_PRE_RECOVERY_REAP` for both clean cases (`ABSENT_CLEAN`
  publishing `P0`; `VALID_P0_CLEAN` publishing `P1`) at all seven cuts;
- `REFERENCE` and `NO_EXCLUSIVE_CREATE` for both occupied-staging setups at
  `NORMAL` and at every checkpoint each can reach;
- `DROP_STAGE_CONTROLLER` and `SELF_CUT` for both clean cases at all seven
  cuts;
- normal success plus separately declared synthetic `EIO` at file-fsync,
  replace, and directory-fsync slots; the trace must distinguish simulated
  return from kernel entry;
- the actual `EEXIST` exclusive-open path in each occupied setup;
- at least three fresh-process repetitions of every process-kill row; and
- exact cross-backend comparison of the `B` histories, with runtime/storage/TCB
  coordinates kept separate.

The incorporated R0 section 7.1 bit-flip, every proper-prefix truncation,
append-zero, wrong-suite, nonregular, stale-valid, and other-valid controls are
rerun exactly for `REFERENCE`; otherwise a mechanism-only pass could conceal a
regression in the controlled record. Expected observations and mutation order
come from that pinned file, not ambient source code. No search/navigation
infrastructure is introduced.

## 6. Required smallest-pair searches

The following are seeds for exhaustive minimization, not pre-awarded verdicts:

| Responsibility attacked | Smallest declared left/right prefix | Smallest future and required comparison |
|---|---|---|
| file `fsync` | `ABSENT_CLEAN`, empty `P0`, `REFERENCE` / `NO_FILE_FSYNC`, through `J3` | kill, reap, recover with empty `C`; compare `B`, while `L` must report success / absence |
| directory `fsync` | same pair through `J5` | kill, reap, recover; compare `B`, while `L` must report success / absence |
| exclusive creation | `ABSENT_TMP`, empty `P0`, reference / no-exclusive, arm `NORMAL` | await first publisher result: reference `ERROR(acquire,kernel,EEXIST)` versus deletion completion if no other fault; then recover |
| authoritative replacement | `ABSENT_CLEAN`, empty `P0`, reference / no-replace, through `J4` | kill, reap, recover: reference `OK(empty)` versus deletion `ABSENT` |
| pre-recovery reaping | `ABSENT_CLEAN`, empty `P0`, reference / no-pre-reap, through `J0` | recover with empty `C`; compare `B`; full `L` order must be wait-before-exec / no-wait-before-exec, and actual overlap is a separately observed fact |
| stage supervision | first clean `arm(J0)` under reference / drop-controller | deletion cannot realize the continuation, so verdict is `UNKNOWN_UNEXECUTABLE`; `SELF_CUT` tests relocation and must charge publisher-side control logic |

Because the manifest selector and trace are visible at `L`, the full laboratory
histories are already distinct. The table searches for the first additional
behavioral distinction at `B`; it is not a claim that the full histories
collide. In particular, process reaping and stage control may be required for a
trustworthy experiment even if no bounded persisted-state distinction appears.

## 7. Deterministic evidence: retain versus rebuild

The run must retain, not merely hash:

- exact frozen contract and adapter/specification bundle bytes;
- exact suite, manifests, literal expected table, generator inputs, seed, and
  trial descriptors;
- every canonical per-trial record and their complete framed stream;
- every raw operation/control trace used to justify an `OBSERVED_*` fact;
- every apparatus failure/timeout record, including exact captured bytes; and
- the serializer, normalizer, verifier, and source inventory used.

The deterministic stream is:

```text
ASCII("ZGR01-EVIDENCE-1") || 00 || u64be(record_count) ||
for trial_id in unsigned-UTF8 order: u64be(record_length) || record
```

A record is `u32be(field_count)` followed by fields in unsigned-UTF8 key order;
each field is `u32be(key_length)||key||u64be(value_length)||value`. Integers in
values use the widths declared here; sets are sorted; there are no host floats,
timestamps, PIDs, inode numbers, temporary path spellings, or locale-derived
strings. Those belong to a separately retained raw-measurement stream. Symbolic
process, descriptor, and object IDs are assigned by first occurrence. Evidence
publishes byte length and SHA-256 for every retained stream and file.

Hashes alone cannot reconstruct evidence. Actual traces, actual observations,
failures, and measurements are **MUST RETAIN for the R0.1 evidence claim**.
Counts, quantiles, verdict tables, normalized maps, and stream digests are
**MAY REBUILD** only by the identified deterministic algorithms from retained
records. Expected rows are MAY REBUILD from the frozen contract/suite/literal
oracle. Random scratch names and wall-clock dates are MAY FORGET only after no
claim refers to them. A rerun is new evidence, not reconstruction of the old
run.

## 8. Simultaneous fourteen-coordinate report

Every backend × manifest report contains all keys below in the same run. There
is no weighted or aggregate score. Every named leaf is either a typed value or
exactly:

```json
{"status":"UNKNOWN","reason":"...","needed_evidence":"..."}
```

An impossible/out-of-contract capability uses:

```json
{"status":"UNSUPPORTED","reason":"..."}
```

No key may be absent, null, an empty placeholder, or a string containing the
word `UNKNOWN`. Schema validation failure invalidates the evidence.

1. **information_distinction_preservation:** trial totals by family; pass,
   fail, unknown, and unsupported counts; exact collision list; minimized
   witnesses; old/new matrix; all corruption and common-mode controls.
2. **persistent_state:** authoritative/staging logical and allocated bytes;
   simultaneous peak; inode/directory-entry counts; in-band/external digest
   bytes; manifest and selector state; lower bound status.
3. **semantic_machinery:** contract, publisher, recovery, adapter, controller,
   tracer, normalizer, oracle, comparator, injector, serializer, schema, and
   tests—files, hashes, bytes, physical/logical lines, generated cells, and all
   dependencies.
4. **human_cognition:** roles; choices; commands; concepts; failure labels;
   instruction words; task time, errors, participant count, and study protocol.
5. **authoring_burden:** hand-authored/generated files, bytes and lines;
   manifest entries; fixtures; parameters; distinct manual decisions; review
   and correction counts.
6. **query_navigation_burden:** continuation count/bytes; opens, reads, adapter
   calls, table/lookup steps, transcript bytes; search/index machinery count.
7. **runtime:** wall and process-CPU nanoseconds by launch, write, each slot,
   kill, wait, recovery, adapter, trace, verify, and total; samples and
   min/median/p95/max; perturbation caveat.
8. **storage:** logical/allocated bytes for authoritative, staging, directory,
   raw evidence, normalized evidence, source/spec, runtime/interpreter, OS,
   hypervisor, and physical backing; shared/unattributable totals.
9. **operations:** processes; privileges; namespace/setup/cleanup steps;
   complete syscall counts by name; retries; failures; signals; waits; trace
   actions; recovery actions; inherited environment allowlist.
10. **trusted_computing_base:** every common and variant component, version,
    provenance, code/config bytes, role, common-mode dependency, kernel,
    filesystem, runtime, tracer, normalizer, oracle, hash implementation,
    hypervisor, host, controller, and media.
11. **evolution:** compatible factor-through observer; class-splitting probe;
    format/version/generation/migration/rollback/freshness support; inputs and
    bytes; external information required.
12. **portability:** exact `E`/`T` behavioral comparison; OS/kernel/filesystem
    prerequisites; backend/variant branches and lines; tested/failed platforms;
    runtime, host, and physical portability status.
13. **explainability:** exact smallest trial; expected/actual bytes; manifest,
    slot, operation source/result, trace locator, causal steps, explanation
    bytes; human comprehension study.
14. **information_loss_risk:** false accepts/rejects; truncation, bit, append,
    I/O, attestation-disagreement, controller, overlap, stale/coherent replace,
    hash/collision, malicious, process-kill, power-loss, and physical fault
    counts/status.

The schema also requires `where_is_complexity_now` for every deletion variant:
changed persisted bytes, code/config, operator concepts, verification work,
runtime, operations, TCB, and unsupported futures. A zero is permitted only
when directly measured and its scope is stated.

## 9. Verdict discipline and mandatory attacks

For each persisted item and each candidate mechanism, R0.1 runs DELETE, MERGE,
DERIVE, RECOMPUTE, COLLIDE, FUTURE, EXTERNALIZE, REALIZE, COGNITION, and TCB.
Information receives MUST SURVIVE, MAY REBUILD, or MAY FORGET only from a
minimized `B` collision and identified future, deterministic reconstruction
recipe, or exhaustive no-effect result respectively. Mechanism results use the
more precise `BEHAVIORAL_WITNESS_IN_R01`, `NO_BEHAVIORAL_WITNESS_IN_R01`, or
`UNKNOWN`; they do not turn a syscall name into a primitive or an architectural
verdict.

Deleting the controller, comparator, tracer, reaper, selector, or verifier must
name the replacement location. Loss of the ability to execute or validate a
trial is not behavioral equivalence. Simplifying machine state must report all
changed human concepts and verification steps; absent participant evidence,
cognition remains the required UNKNOWN object.

## 10. Process kill is not power loss or physical evidence

Every R0.1 cut uses `SIGKILL` while the guest kernel, mounts, VFS, filesystem,
virtual controller, hypervisor, and host continue running. `fsync` success
means only that the guest call returned success. A process reap establishes
only guest-OS termination/reaping order. Neither fact establishes cache flush,
nonvolatile capture, cold recovery, physical delivery, or media independence.

`E` and `T` remain unlike guest-kernel paths only. Physical identity,
independence, power interruption, flush/barrier reach, cold restart, host/cache
failure, and tmpfs swap behavior are mandatory UNKNOWN or UNSUPPORTED objects.
No power-loss or physical continuation appears in the R0.1 grammar, so none may
be imported to manufacture an `fsync` witness. Conversely, absence of a
process-kill witness cannot classify either `fsync` responsibility as
forgettable under a later durability contract.

Advancing that claim requires a separately frozen history grammar with two
identified independent physical paths, declared commit/capture cuts,
controlled power interruption, cache assumptions, cold recovery, independent
readback, fault models, and external-anchor/TCB accounting. R0.1 supplies none
of those facts.

## 11. Freeze rule

Before implementation, retain this exact file, publish its SHA-256, freeze the
bundle manifest and every descriptor/expected row, and attest that builder and
breaker drafts were independent. Any changed boundary, channel, slot meaning,
variant, comparator, suite value, expected output, evidence schema, or unknown
policy creates a new contract hash. Implementation is only an attempt to
falsify that frozen contract.
