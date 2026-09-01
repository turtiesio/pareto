# REALIZATION CONTRACT R0

## Status and claim boundary

This document freezes a finite, pre-implementation laboratory contract for a
second-round realization experiment. It was specified without importing any
earlier candidate's domain names, state decomposition, transition vocabulary,
or persistence format.

R0 is a **falsification instrument**. The record layout and publication
procedure below are candidate mechanisms to attack; they are not an
architecture and are not presumed minimal. A conforming run can establish only
the observations enumerated here. It cannot establish global minimality,
power-loss durability, physical-media independence, or equivalence for futures
outside the finite R0 suite.

`P0`, `P1`, `C`, `Y0`, and `Y1` below are byte-string positions in a test
manifest. They carry no assumed meaning. Terms such as “payload,” “publish,”
and “continuation” describe byte flow at this laboratory boundary, not a domain
ontology.

## 1. Declared boundary

The system under test consists of exactly:

1. one publisher process;
2. one selected guest filesystem namespace and one otherwise isolated test
   directory in it;
3. one recovery process using the frozen adapter bundle; and
4. the bytes made authoritative at `state.bin` in that directory.

The external supervisor, suite manifest, expected answers, process launcher,
fault injector, measurement collector, and operating environment are outside
that boundary. Their information and code are not free; section 11 charges
them explicitly.

The publisher and recovery process never coexist. After every publisher exit
or kill, the supervisor must reap it before starting recovery. The recovery
process must be a new operating-system process with a new address space and
must receive no publisher memory, file descriptor, pipe contents, or temporary
file path. It receives only:

- the selected directory path;
- the frozen adapter/specification bundle, including the expected 32-byte suite
  digest;
- the single opaque continuation `C`; and
- ordinary inherited operating-system facilities recorded in the TCB ledger.

Recovery must not receive `P0`, `P1`, `Y0`, `Y1`, the selected old/new label,
the kill cut, or the expected observation from the supervisor.

The semantic boundary crossings are:

- supervisor inputs: realization choice, setup choice, publication request,
  cut choice, kill, declared fault intervention, recovery request, and `C`;
- system outputs: publisher stage acknowledgement, publisher process result,
  and the exact recovery observation defined in section 6.

Measurements listed in section 10 are also externally reported. Variable
timings and allocation proxies are measurements, not semantic equality keys.
No unlisted log, cache, temporary file, clock value, filesystem enumeration,
or diagnostic text is an allowed semantic observation.

## 2. Frozen finite suite parameters

One run uses exactly five opaque strings:

```text
P0, P1, C, Y0, Y1 : byte strings of length 0 through 4096 inclusive
P0 != P1
Y0 != Y1
adapter(P0, C) = Y0
adapter(P1, C) = Y1
```

The adapter must be deterministic for these inputs. Any other payload or
continuation is outside the R0 semantic claim, although malformed-record
handling remains in scope.

Define `LP(X) = uint32_be(length(X)) || X`. Define:

```text
Q = SHA256(the exact bytes of this frozen contract)
A = SHA256(the canonical adapter-bundle manifest)
D = SHA256(
      ASCII("ZERO-GROUND-R0-SUITE") || 0x00 ||
      Q || A || LP(P0) || LP(P1) || LP(C) || LP(Y0) || LP(Y1)
    )
```

The canonical adapter-bundle manifest is the concatenation, in ascending
unsigned UTF-8 filename-byte order, of this tuple for every executable or
configuration file loaded by publisher or recovery:

```text
LP(filename_utf8) || uint64_be(file_length) || file_bytes
```

Paths in that manifest are relative, contain neither `..` nor an absolute
prefix, and use `/` as separator. The evidence must publish `Q`, `A`, `D`, the
manifest file list, individual file hashes, and the five opaque values in hex.
This deliberately reveals the laboratory suite; secrecy is not an R0
requirement.

The suite must be frozen before any conformance execution. Selecting the five
values after observing a backend is forbidden.

## 3. Legal history grammar

The following grammar is exhaustive. `E` and `T` are the realization symbols
defined in section 8. `K0` through `K5` and `NORMAL` are defined in section 5.

```text
backend       ::= E | T
setup         ::= ABSENT | VALID_P0
publication   ::= P0 | P1
case          ::= CREATE | UPDATE
cut           ::= K0 | K1 | K2 | K3 | K4 | K5 | NORMAL

CREATE        ::= setup(ABSENT), request_publish(P0)
UPDATE        ::= setup(VALID_P0), request_publish(P1)

publish_trial ::= select(backend), case, arm(cut),
                  publisher_stage*, (kill_and_reap | normal_exit_and_reap),
                  start_recovery(C), recovery_observation

record_fault_trial
               ::= select(backend), setup(valid_record), mutate(fault),
                   start_recovery(C), recovery_observation

io_fault_trial ::= select(backend), case, inject(io_fault),
                  publisher_stage*, publisher_result,
                  start_recovery(C), recovery_observation

history       ::= publish_trial | record_fault_trial | io_fault_trial
```

`CREATE` permits only publication of `P0`; `UPDATE` permits only publication of
`P1`. A legal R0 corpus contains every backend × case × cut publication trial,
every record fault in section 7 for both valid records on both backends, and
every I/O fault in section 7 for both cases on both backends. There is no union
or implicit extension of this grammar.

A history is the complete ordered list of the crossings above, including the
exact input bytes, stage acknowledgements, wait status, recovery bytes, and
measurement records. Two histories may be merged semantically only when every
legal remaining R0 cut, fault, recovery, and continuation yields the same exact
semantic observation. Nondeterministic measurement samples do not by
themselves split semantic classes, but their distributions and static counts
must still be reported separately.

## 4. Candidate persistent record

The sole authoritative pathname is the literal relative name `state.bin`.
The sole staging pathname is `.state.tmp`. The setup directory initially
contains neither pathname for `ABSENT`, and contains only a valid `state.bin`
for `VALID_P0`. Concurrent writers, readers during publication, symlinks, hard
links, and additional directory entries are outside R0 and must cause the
supervisor to abort the trial rather than silently broaden the claim.

For an opaque payload `P`, the exact candidate record is:

```text
offset  length       bytes
0       32           D
32      length(P)    P
32+n    32           H

n = length(P)
H = SHA256(
      ASCII("ZERO-GROUND-R0-RECORD") || 0x00 ||
      D || uint64_be(n) || P
    )
```

The file length must be exactly `64 + n`, with `0 <= n <= 4096`. `D` and `H`
are raw 32-byte values, not 64-character hexadecimal text. There is no padding,
version byte, generation, timestamp, authority identifier, filename encoding,
or trailing data.

The record therefore has exactly 64 logical bytes of in-band overhead. The
directory entry, inode, filesystem allocation, staging copy, expected digest in
the recovery bundle, and adapter/specification bytes remain additional state
and must be measured or charged externally.

SHA-256 is used only as an accidental-corruption detector under the explicit
assumption that none of the finite mutations tested here produces a collision.
Resistance to malicious coherent replacement is unsupported.

## 5. Candidate publication procedure and kill cuts

Each directory is private to one trial. The publisher performs these operations
in order. Every stage acknowledgement is written to the supervisor control pipe
only after the named operation has returned successfully.

```text
K0  publisher started; no open or mutation of .state.tmp has occurred
    acknowledgement bytes: a0 00

K1  .state.tmp was opened as a new regular file with exclusive creation and
    exactly floor(length(new_record) / 2) prefix bytes were written
    acknowledgement bytes: a0 01

K2  all new-record bytes were written with short-write retry; no file fsync
    has begun
    acknowledgement bytes: a0 02

K3  fsync(.state.tmp) returned success and its descriptor was closed; rename
    has not begun
    acknowledgement bytes: a0 03

K4  atomic replace of .state.tmp onto state.bin in the same directory returned
    success; directory fsync has not begun
    acknowledgement bytes: a0 04

K5  fsync(the open test-directory descriptor) returned success
    acknowledgement bytes: a0 05

NORMAL  publisher closed all descriptors and exited with status 0 after K5
```

At a selected `K0` through `K5`, the supervisor reads exactly the two-byte
acknowledgement, sends `SIGKILL`, records the wait status, and waits until the
publisher is reaped. A missing, duplicate, out-of-order, or extra stage frame
fails the trial. For `NORMAL`, no kill is sent and exit status must be zero.

Recovery ignores `.state.tmp`; its presence and size are recorded only as
operational measurements. Recovery opens `state.bin` without following a
symlink and accepts only a regular file.

The required live-kernel atomic visibility matrix is:

| Cut | `CREATE`: old `ABSENT`, new `P0` | `UPDATE`: old `P0`, new `P1` |
|---|---|---|
| `K0` | `ABSENT` | `OK(Y0)` |
| `K1` | `ABSENT` | `OK(Y0)` |
| `K2` | `ABSENT` | `OK(Y0)` |
| `K3` | `ABSENT` | `OK(Y0)` |
| `K4` | `OK(Y0)` | `OK(Y1)` |
| `K5` | `OK(Y0)` | `OK(Y1)` |
| `NORMAL` | `OK(Y0)` | `OK(Y1)` |

Thus every cut must expose exactly the old publication or exactly the new
publication, never a partial or mixed record. This matrix describes process
kill while the guest kernel and filesystem remain running. It makes no claim
about guest reset, host reset, controller cache loss, or power removal.

`fsync` calls are part of this candidate procedure, but R0 does not predeclare
them minimal. The mechanism-deletion variants in section 12 must test whether
R0's process-kill observations witness their necessity. No power-loss argument
may be used to manufacture a witness outside the declared grammar.

## 6. Recovery algorithm and exact observations

Recovery performs, in order:

1. If `state.bin` does not exist, emit `ABSENT`.
2. Open it without symlink following and verify that it is a regular file.
3. Reject a size below 64 or above 4160 bytes.
4. Split the bytes as `D_file || P || H_file`, using the first and last 32
   bytes.
5. Compare `D_file` with the expected suite digest from the frozen recovery
   bundle.
6. Recompute the record hash and compare it byte-for-byte with `H_file`.
7. Ask the adapter to interpret `P` and apply exactly `C`. A parse failure,
   nondeterministic result, exception, signal, timeout, or output over 4096
   bytes is rejection.
8. Emit the one permitted observation and then EOF.

The recovery process's entire semantic stdout is exactly one of:

```text
ABSENT  = 00
REJECT  = 01
OK(Y)   = 02 || uint32_be(length(Y)) || Y
```

There is no reason code, recovered payload, backend label, cut label, checksum
value, path, timestamp, or diagnostic in the semantic output. Standard error
must be empty for a conforming semantic trial; implementation diagnostics are
captured separately and make that trial fail rather than becoming an added
observation channel.

For valid `P0` and `P1`, the only permitted `OK` values are respectively `Y0`
and `Y1`. The external verifier compares the exact observation bytes. It does
not reuse the candidate record parser or adapter to compute expected answers.

## 7. Finite fault-injection domain

### 7.1 Post-publication record faults

For each backend and each normally published valid record `R(P0)` and `R(P1)`,
the supervisor runs all of these mutations in a fresh copied trial directory:

| Fault | Exact mutation | Required observation |
|---|---|---|
| `MISSING` | remove `state.bin` before recovery | `ABSENT` |
| `TRUNCATE(j)` | retain the first `j` bytes, for every `0 <= j < length(R)` | `REJECT` |
| `FLIP(i,b)` | toggle bit `b`, for every byte `0 <= i < length(R)` and every `0 <= b < 8` | `REJECT`, subject to the stated SHA-256 finite-collision assumption |
| `APPEND_ZERO` | append exactly byte `00` | `REJECT` |
| `WRONG_SUITE` | toggle the high bit of `D[0]` and recompute `H` coherently | `REJECT` because the expected suite digest differs |
| `NONREGULAR` | replace `state.bin` with a symlink to a valid record | `REJECT` |

Two coherent-replacement attacks are diagnostic negative controls, not required
successes of this format:

| Attack | Exact mutation | Required report |
|---|---|---|
| `STALE_VALID` | after a normal `UPDATE`, replace `state.bin` with the complete valid `R(P0)` | recovery is `OK(Y0)` and evidence records `UNDETECTED_STALE` |
| `OTHER_VALID` | replace either valid record with the other complete valid record | recovery follows the substituted payload and evidence records `UNDETECTED_COHERENT_REPLACEMENT` |

Those controls prevent checksum validation from being misreported as freshness,
authorization, or malicious-tamper protection.

### 7.2 Publisher I/O faults

These are deterministic wrapper-level simulations, not physical failures:

- `SHORT_WRITE(s)`: for each `s` in `{1, 2, 7, 31}`, every write accepts at
  most `s` bytes; retry must still reach `NORMAL` and expose the new record.
- `WRITE_ERROR_BEFORE_HALF` and `WRITE_ERROR_AFTER_HALF`: the selected write
  raises `ENOSPC`; publisher result is `PUBLISH_ERROR(WRITE)` and recovery is
  old.
- `FILE_FSYNC_ERROR`: the temporary-file fsync raises `EIO`; result is
  `PUBLISH_ERROR(FILE_FSYNC)` and recovery is old.
- `REPLACE_ERROR`: atomic replace raises `EIO`; result is
  `PUBLISH_ERROR(REPLACE)` and recovery is old.
- `DIRECTORY_FSYNC_ERROR`: directory fsync raises `EIO` after successful
  replacement; result is `PUBLISH_ERROR(DIRECTORY_FSYNC)` and live-kernel
  recovery is new, while restart durability remains unknown.

Here “old” and “new” expand using the table in section 5. A simulated error must
exit nonzero after emitting exactly `af || code`, where codes are `01` write,
`02` file fsync, `03` replace, and `04` directory fsync. The supervisor records
the wrapper configuration so simulated failures cannot be presented as backend
failures.

No disk-full event, bad block, memory error, kernel crash, guest reboot, host
reboot, torn sector, controller reordering, wear, or power failure is injected
by R0.

## 8. The two available guest-level realizations

R0 uses two actually available but only guest-level realization boundaries:

| Symbol | Base directory | Required guest filesystem | Candidate storage path |
|---|---|---|---|
| `E` | `/tmp` | ext4, `statfs` magic `0xEF53` | VFS → ext4 → guest block stack |
| `T` | `/dev/shm` | tmpfs, `statfs` magic `0x01021994` | VFS → tmpfs → guest VM memory/swap machinery |

For every run the supervisor creates a new exclusive child directory below the
resolved base, verifies the filesystem magic, records `/proc/self/mountinfo`,
device major/minor, mount options, `statvfs`, kernel release, virtualization
facts, and block-device topology visible to the guest, then refuses to run if
the declared type is not present. The test directory and staging file must be
on the same mount as `state.bin`.

These are materially unlike guest kernel storage implementations: one traverses
ext4 and a guest block device; the other traverses tmpfs and the guest memory
manager. That is the largest supported realization claim.

They are **not demonstrated unlike physical substrates**. The observed host is
a virtual machine; the ext4 block device is virtual, host media are undisclosed,
and tmpfs pages may be swapped to a swapfile on the same guest virtual disk.
Consequently ext4 and tmpfs may converge on the same unknown physical media.
Loopback files, another directory on the same ext4 mount, the read-only virtual
optical device, firmware NVRAM without a safe scratch allocation, and boot
partitions are not accepted as second physical substrates.

## 9. Conformance execution

For each backend, conformance requires:

1. every `CREATE` and `UPDATE` cut row in section 5;
2. the normal valid `P0` and `P1` recoveries;
3. every exhaustive post-publication mutation in section 7.1;
4. both coherent-replacement negative controls;
5. every publisher simulation in section 7.2;
6. at least three clean repetitions of each publication cut with a fresh
   directory and fresh publisher/recovery processes; and
7. a cross-backend comparison of exact semantic observations.

Ordering is generated from a recorded deterministic seed, but each trial uses
a fresh directory. Expected semantic bytes come from a separately coded
literal suite table in the verifier. The candidate parser/adapter must never be
called by that expected-output path. At least one deliberate record-table or
parser mutation must be shown to make the verifier fail; this is common-mode
defense, not proof of oracle independence.

The evidence certificate hashes canonical length-prefixed deterministic records
containing suite digest, backend identity, trial parameters, exact input record
or mutation, stage/wait result, exact recovery observation, and verdict. Wall
times, CPU times, environment timestamps, random directory names, and inode
numbers are measurement-only and excluded from that deterministic certificate.

## 10. Simultaneous non-scalar measurement schema

Every candidate/backend report must contain every row below. There is no
weighted score and no permitted aggregate “total score.” A missing measurement
is represented as `{"status":"UNKNOWN","reason":...}`; an unavailable
capability is `{"status":"UNSUPPORTED","reason":...}`. Neither is a pass.

| Required dimension | Mandatory R0 fields and units |
|---|---|
| Information/distinction preservation | total legal trials; pass/fail counts by kind; exact semantic collision list; `P0/P1` separating witness `C,Y0,Y1`; old/new cut matrix; mutation coverage; common-mode mutation result |
| Persistent state | `state.bin` logical bytes; `.state.tmp` logical bytes; peak simultaneous logical bytes; `st_blocks * 512`; inode and directory-entry counts; suite digest bytes; external expected-digest bytes; filesystem allocation caveat |
| Semantic machinery | contract, manifest, publisher, recovery, adapter, verifier, supervisor, and injector file lists; SHA-256 per file; source bytes; physical lines; logical lines; generated-table cells and bytes |
| Human cognition | number of operator choices and commands; required concepts and failure labels; instruction words; observed human error study or explicit `UNKNOWN`; no inference from LOC alone |
| Authoring burden | hand-authored/generated file counts, bytes, logical lines, manifest entries, parameters, fixtures, and distinct manual decisions |
| Query/navigation burden | continuation count and bytes; recovery opens/reads; adapter invocations; lookup/table steps; transcript bytes; absence of search/index infrastructure stated explicitly |
| Runtime | per trial and aggregate monotonic wall and process CPU nanoseconds; process-launch, publication, fsync, replace, recovery, adapter, verification phases; sample count; min/median/p95/max; timing declared measurement-only |
| Storage | logical and allocated bytes for authoritative file, staging peak, directory, evidence, code/spec bundle, interpreter/runtime proxy, and filesystem delta; state which totals remain incomplete or shared |
| Operations | process count; privilege/namespace requirements; syscall counts by name; fsync/replace/open/read/write/close counts; setup/cleanup steps; retries; failed operations; recovery actions |
| Trusted computing base | every common and backend-specific component in section 11 with version, source where knowable, bytes where measurable, and `UNKNOWN` for unavailable implementation size |
| Evolution | compatible derived-observer probe; split-extension collision result; format/version/generation support status; migration inputs and bytes; rollback/freshness result |
| Portability | exact observation equality across `E` and `T`; OS/kernel/filesystem prerequisites; backend-specific branches and lines; failed/untested platforms; physical portability `UNKNOWN` |
| Explainability | recovery tag, smallest failing trial record, exact expected/actual bytes, causal stage/fault label, explanation bytes/steps; human comprehension `UNKNOWN` absent a study |
| Information-loss risk | count and outcome of every truncation/bit/error case; undetected coherent replacements; unsupported fault classes; hash assumption; recovery false-accept/false-reject counts in the finite suite |

The compatible evolution probe adds the observer
`G(Y) = SHA256(ASCII("ZERO-GROUND-R0-DERIVED") || 0x00 || LP(Y))`. It must be
rebuildable for both payload positions from existing `OK(Y)` without changing
the persisted record. This is evidence for exactly one observer that factors
through R0's old observation.

A split extension is not supported: if a future contract assigns different
required answers to two predecessor histories that both produced the same R0
record bytes, no deterministic migration from those bytes can select the right
answer. The minimal witness is one identical input record and two required new
outputs. R0 must report this as `UNSUPPORTED_SPLIT_WITHOUT_EXTERNAL_INFORMATION`,
not as successful evolution.

## 11. TCB and externalization ledger

No omitted component receives zero cost.

| Responsibility | Where it resides in R0 | Required charge or limitation |
|---|---|---|
| Choosing the five suite strings and expected distinction | external frozen suite/verifier | manifest bytes, literal-table bytes, authoring steps, and common-mode risk |
| Interpreting opaque payload and continuation | adapter/specification bundle | all code/configuration hashes, bytes, LOC, dependencies; must be identical across backends |
| Remembering the expected suite identity | recovery bundle's trusted 32-byte `D` | external duplicate state plus configuration-selection risk |
| Encoding and parsing the record | publisher/recovery code | full code and test inventory; bounds and byte order are TCB |
| Accidental-corruption detection | SHA-256 implementation and collision assumption | library/version/implementation; malicious replacement unsupported |
| Old/new publication selection | pathname, atomic replace, VFS and selected filesystem | path validation, syscall code, kernel/filesystem versions and semantics |
| Ordering publication steps | publisher and supervisor stage protocol | stage code/configuration and pipe/process-control correctness |
| Killing and isolating processes | supervisor, kernel scheduler/signals/wait, process launcher | versions, calls, privileges; not a power cut |
| Backend selection and type proof | configured paths, path resolver, `statfs`, mount inspection | selector/validator code and mount metadata |
| `E` storage behavior | VFS, ext4, guest block layer, virtual controller, hypervisor, unknown host storage/cache | guest facts measured; hypervisor/host/physical implementation and sizes `UNKNOWN` |
| `T` storage behavior | VFS, tmpfs, VM subsystem, swap subsystem, hypervisor memory, possible swap backing | guest facts measured; physical RAM/swap/host behavior `UNKNOWN` |
| Expected-answer comparison | separately coded external verifier | verifier code/table is TCB; mutation check required |
| Fault placement | supervisor/injector/wrapper | injection code and exact parameters; simulated faults labeled |
| Metrics and evidence | clocks, `/proc`, `statfs`, `statvfs`, syscall counter/tracer, serializer, hasher | collector code/version; measurement error and shared-resource gaps disclosed |
| Temporary-file cleanup | supervisor outside semantic boundary | operations and code charged; recovery must not rely on cleanup |
| Freshness, generation, writer authority, replay prevention | nowhere in the candidate record | `UNSUPPORTED`; coherent-replacement controls expose this absence |
| Power-loss persistence and physical independence | nowhere observable in R0 | `UNKNOWN`/`UNSUPPORTED`; may not be inferred from process-kill passes |

## 12. Mandatory deletion, merge, derivation, and collision attacks

The implementation must generate variants mechanically where possible and
answer each question with the smallest R0 history/continuation witness or with
`NO_WITNESS_IN_R0`. A surviving witness establishes a responsibility, not a
field, layer, or architectural primitive.

### DELETE

- Delete all persisted bytes: do `P0` and `P1` collide despite `Y0 != Y1`?
- Delete or zero the payload region: do valid `P0` and `P1` collide under `C`?
- Delete `D`: can the coherent wrong-suite record be distinguished from the
  correct suite without moving `D` into trusted external configuration?
- Delete `H`: does a one-bit mutation become observationally identical to an
  accepted record?
- Delete temporary-file fsync, directory fsync, replace, exclusive creation,
  or process reaping one at a time: which declared process-kill row first
  differs? If none does, report no R0 necessity witness rather than importing a
  power-loss future.
- Delete adapter, verifier table, backend validator, or stage supervisor: is
  required work gone, or merely externalized into convention or an unmeasured
  runtime?

### MERGE

- Merge `P0` and `P1`: the required minimal future witness is `C`, with exact
  outputs `Y0` and `Y1`.
- Merge pre-replace cuts `K0..K3` with post-replace cuts `K4..K5`: use the
  smallest `CREATE` or `UPDATE` recovery that changes old to new.
- Merge `ABSENT`, `REJECT`, and `OK`: identify the shortest missing, malformed,
  and valid record histories requiring distinct one-byte tags.
- Merge correct-suite and wrong-suite records: identify whether expected-digest
  state still exists somewhere and charge that location.
- Merge the `E` and `T` realization labels: semantic behavior may merge if all
  finite outputs match, but TCB, operations, storage allocation, runtime, and
  physical-claim status remain separate report coordinates.
- Merge a normal update with `STALE_VALID`: show that this candidate cannot
  distinguish them after coherent replacement and report the unsupported
  freshness responsibility.

### DERIVE AND RECOMPUTE

- `H` is mechanically recomputable from `D` and `P`, but ask whether a freshly
  recomputed value can detect corruption of the persisted source without an
  independently surviving comparison value.
- `D` is recomputable from the exact contract, adapter manifest, and five suite
  strings; identify which of those must survive outside the record and include
  their total cost.
- `Y0` and `Y1` are recomputable only through the identified adapter/specification
  and `C`; the verifier's literal expectations remain an independent test oracle
  and are not credited as free.
- Stage labels and expected cut outcomes may be regenerated from this contract;
  the parser/generator and exact contract bytes remain TCB.

### RECOMPUTE, FUTURE, EXTERNALIZE, REALIZE, COGNITION, AND TCB

- For every deleted byte or call, state exactly where the necessary distinction
  is reconstructed and what code/configuration must be correct.
- Apply the contract-permitted next cut, mutation, recovery, and `C` after every
  proposed merge; do not use an undeclared future to save or reject it.
- Record whether state moved to the manifest, expected-digest constant,
  directory name, filesystem metadata, supervisor, adapter, verifier, human
  procedure, kernel, hypervisor, or host.
- Do not call `E` and `T` unlike physical realizations. Report only the observed
  guest-level difference and list the physical evidence still missing.
- For each machine simplification, report changed operator choices, concepts,
  instructions, and verification steps. Actual cognitive load remains
  `UNKNOWN` without a human study.
- Recompute the complete TCB/externalization ledger after each variant; deletion
  from the record does not delete a responsibility from the total system.

### Minimal named collision set

The run must at least materialize and minimize these finite collisions:

| Collision caused by simplification | Left history | Right history | Distinguishing continuation/observation |
|---|---|---|---|
| payload deletion/merge | normal valid `P0` | normal valid `P1` | `C`: `OK(Y0)` versus `OK(Y1)` |
| integrity deletion | normal valid record | smallest accepted corruption after deleting `H` checking | `OK` versus required `REJECT` |
| suite-identity deletion | correct suite | coherent `WRONG_SUITE` | accepted result versus required `REJECT` |
| publication-step deletion | smallest pre-replace cut whose outcome changes | corresponding post-replace cut | old versus new recovery observation |
| absence/rejection merge | missing file | zero-length file | `ABSENT` versus `REJECT` |
| freshness omission | normal `UPDATE` | `STALE_VALID` after update | collision is **not** separated by R0; required report is unsupported freshness |
| physical-realization claim | matching `E` run | matching `T` run | no physical distinction is observed; claim remains `UNKNOWN` despite different guest TCBs |

Collision minimization order is: total number of boundary crossings, then total
input bytes, then fault parameter numeric value, then unsigned lexical order of
the complete canonical history record. Search must examine all legal candidates
at the winning first two coordinates before selecting lexically.

## 13. Provisional information classification discipline

R0 does not pre-award a verdict to a named record component. After executing
the attacks, each information responsibility receives exactly one verdict:

- **MUST SURVIVE** only when deletion or merging produces a minimized collision
  between histories that a legal R0 future distinguishes;
- **MAY REBUILD** only with an exact deterministic recipe from identified
  surviving bytes plus an identified specification, both charged to the total
  system; or
- **MAY FORGET** only when exhaustive R0 enumeration finds no affected legal
  observation, with the verdict explicitly scoped to R0.

`NO_WITNESS_IN_R0` is not proof for a larger contract. In particular, the
candidate's file and directory fsync calls may lack process-kill witnesses while
remaining relevant to an untested power-loss contract. Conversely, passing the
finite checksum faults does not create freshness or authority information that
the record does not contain.

After every apparent simplification, the report must answer: **Where is the
complexity now?**

## 14. Explicit unsupported and unknown claims

The following are outside R0 and must never be inferred from a passing run:

- behavior after guest reboot, host reboot, hypervisor failure, controller
  reset, power loss, or loss of volatile caches;
- identification, independence, endurance, or error behavior of the physical
  media beneath either guest filesystem;
- proof that tmpfs pages remained in physical RAM or did not traverse swap;
- proof that ext4 flushes reached nonvolatile physical media;
- resistance to SHA-256 collisions, malicious coherent rewriting, rollback,
  replay, unauthorized writers, or path-namespace compromise;
- concurrent readers/writers, distributed replication, backup, restoration,
  long-term retention, wear, resource exhaustion beyond simulated calls, or
  recovery after kernel corruption;
- semantic behavior for any payload, continuation, or future not in the frozen
  finite suite;
- actual human comprehension or error rate;
- equivalence of total costs across the two realizations; and
- existence of two unlike physical realizations.

Evidence needed to advance the final physical claim includes at least two
identified and independently controlled physical media/controller paths,
exclusive safe scratch regions, documented flush/barrier semantics, controlled
power interruption at enumerated cuts, cold recovery after power restoration,
independent readback, and recorded media/controller failure models. None is
available in the present guest environment.

