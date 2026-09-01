# REALIZATION SUPPLEMENT R0.1A — POST-BREAKER CONTROLS

## 0. Status and provenance

This supplement does not modify or retroactively enlarge the independently
written candidate in `REALIZATION-CONTRACT-R01.md`.  That file was retained
first with SHA-256
`0e28b0e99c1429aabfb13806c296bb2b4fb678dde7e6bcb183057ea5d392b820`.

An ontology-blind breaker independently specified `AO-R01-v1` before any
R0.1 implementation existed.  The root agent wrote this supplement only after
reading both drafts.  Therefore R0.1A is an attack-informed repair profile,
not an independent candidate.  Results must identify whether a row was
required by the original R0.1 contract, by the breaker object, or by this
supplement.  Hashes can establish retained bytes, but cannot by themselves
prove authorship or epistemic independence.

The effective R0.1A experiment contract is the conjunction of:

1. the frozen R0.1 contract above;
2. the exact retained `R01-BREAKER-OBJECT.json` bytes and its separately
   published SHA-256; and
3. this exact supplement.

If the three sources disagree, the trial is `UNKNOWN(CONTRACT_CONFLICT, ...)`.
No implementation choice resolves a specification conflict silently.

## 1. Full-history comparator controls

The following breaker rows are mandatory held-out comparator inputs.  They do
not change the service boundary `B`.  They attack the complete laboratory
record at `L`.

- `ATT-F`, `ATT-D`, `ATT-R`, and `ATT-X` inject an absent manifest branch and
  independently observed absent kernel call together with a forged legacy
  success acknowledgement or forged `SELF_REPORT`.  The full verdict must
  fail for false success attestation even when recovery bytes match.
- `PROJECT-1` duplicates one neutral checkpoint.  Exact ordered control
  comparison must fail; a recovery-only pass is a comparator defect.
- `KILL-EXIT` requires an observed normal exit rather than a causal kill.
  `KILL-OVERRUN` requires independent evidence that selection occurred beyond
  the armed cut.  Both must fail in the full view.
- `REAP-ORDER` starts recovery before the exact publisher is reaped.  Matching
  recovery bytes cannot make that laboratory history conforming.
- `SELECT-OMIT` reaches the post-selection slot without any old/new selection
  and must expose the missing new observation.

The old `a000` through `a005` bytes in the breaker object are adversarial
legacy inputs, not R0.1 neutral frames and never `B` crossings.  A conforming
normal R0.1 producer emits only the neutral frames in the base contract.  The
held-out comparator must nevertheless reject a submitted laboratory record
that tries to use a legacy byte as proof of an operation.

The full comparator input includes the exact declared mutation, exact ordered
checkpoint stream, normalized operation facts, signal request and result,
wait/reap identity and order, recovery-process identity and output, every
required measurement leaf, and exact evidence availability.  It emits two
separate verdicts:

```text
recovery_projection = MATCH | DIFFERENT | NO_OBSERVATION
full_conformance     = PASS | FAIL(reason) | UNKNOWN(reason, needed_evidence)
```

`recovery_projection=MATCH` never overrides a non-`PASS` full verdict.

## 2. Live deletion and stale-entry controls

`SYNC-F-LIVE` and `SYNC-D-LIVE` run the exact 28 clean rows each: two guest
backends, two clean cases, and seven cuts.  The deleted operation is truthfully
`OBSERVED_ABSENT` and the neutral frame says `branch=ABSENT`.  Exact equality
of all 28 `B` histories permits only
`NO_BEHAVIORAL_WITNESS_IN_R01_LIVE_KERNEL_PROFILE`.  It does not support
`MAY_FORGET`, restart durability, or a power-loss conclusion.

`STALE-EMPTY` begins with exactly one zero-length regular `.state.tmp` and no
`state.bin`.  The reference exclusive branch must refuse with the actual
`EEXIST` path, leave the entry byte-for-byte unchanged, and recover `ABSENT`.
The nonexclusive branch may demonstrate a behavioral collision, but the
surviving responsibility is stale-collision discrimination/refusal, not the
name of an `open` flag or syscall.

The smallest live replacement witness remains one empty CREATE history at the
post-selection cut: selected reference recovery is `OK(empty)` and omitted
selection recovery is `ABSENT`.  It forces an old/new authoritative-selection
responsibility, not `rename(2)` specifically.

## 3. Adapter and recovery attribution futures

These futures make explicit behavior already stated for the incorporated R0
recovery algorithm:

- `ADAPTER-TIMEOUT` launches the selected adapter in a separately identified
  child, enforces a frozen monotonic deadline of 250,000,000 ns after input is
  completely delivered, kills and reaps it on expiry, and requires the
  recovery process itself to emit exactly `REJECT=01` followed by EOF with
  empty semantic stderr.
- `ADAPTER-SIGNAL15` causes that adapter child to terminate by signal 15 and
  requires the same exact recovery-process observation.
- `RECOVERY-SIGNAL9` kills the recovery process itself before an observation.
  The only valid outer verdict is `FAIL(NO_RECOVERY_OBSERVATION)`.  A
  supervisor-generated `01` fails source attribution.

Raw control and wait records must identify adapter, recovery, and supervisor
as distinct symbolic processes.  An escaped timeout, generic launcher error,
or unattributed semantic byte does not satisfy these rows.

## 4. Ambient-environment pair

For `ENV-PAIR`, the outer launcher's ambient environments differ only by the
absence versus presence of the exact entry `X=`.  The selected environment for
publisher, recovery, and adapter subjects is exactly:

```text
LANG=C
LC_ALL=C
PATH=/usr/bin:/bin
```

in unsigned UTF-8 key order, with no other inherited entry.  Subject
executables use absolute paths.  A canary adapter returns `Y0` when `X` is
absent and `Y1` when it is visible.  Both recovery observations must be
`OK(Y0)`.  The exact effective environment and launcher construction are
retained evidence.  Passing this pair establishes only exclusion of this one
declared entry; loader, locale implementation, kernel, and all untested ambient
channels remain TCB or `UNKNOWN`.

## 5. Measurement deletion and structured-unknown attacks

Before the first subject trial, R0.1A freezes an exact machine-readable list of
atomic required measurement paths.  `MEASURE-DELETE(path)` is generated once
for every path and must fail schema validation with that exact missing path.
`MEASURE-UNKNOWN(path)` replaces a value with a well-formed `UNKNOWN` or
`UNSUPPORTED` object and must remain schema-valid while leaving the associated
claim unknown or unsupported.  Such an object is never counted as a measured
pass.

The list must expand every prose group in R0.1 section 8, including every
runtime phase, every source/component inventory field, hand-authored versus
generated splits, directory/inode/raw-evidence/runtime storage, whole-process
syscall/retry/setup/cleanup totals, and every TCB component's version, source,
bytes, role, and dependency status.  Freezing only fourteen top-level names is
nonconforming.

## 6. Exact evidence replay future

Before execution, every trial descriptor receives a canonical `trial_id` and
an exact framed-stream ordinal.  The retained replay index is a deterministic
map from those selectors to `(offset, length, SHA256(record_bytes))`.

`EVIDENCE-REPLAY` runs after the producing process exits.  A fresh replay
process that imports no producer, subject, oracle, or normalizer code receives
only the retained stream, retained index, and frozen selector.  It must return
the exact canonical record bytes and separately verify the retained hash.
Hash equality without bytes is `FAIL(EVIDENCE_UNAVAILABLE)`.  Regeneration is
not replay and can support `MAY REBUILD` only when the complete generator,
inputs, selected environment, serialization specification, and machinery are
identified and reproduce the bytes exactly.

## 7. Guarded unsupported profiles

`POWER-GUARD` must yield `UNSUPPORTED_PHYSICAL_GATE` in the present guest.  It
may not be substituted with process kill, sync success, VM restart, or a second
guest filesystem.  Physical capture, delivery, cold recovery, independent
failure domains, and fsync necessity under power loss remain `UNKNOWN`.

`SELECT-ALT-PRE` and `SELECT-ALT-POST` describe a prospective opaque
alternative realization absent from R0.1's frozen manifest set.  R0.1A records
them as `UNSUPPORTED_ALTERNATIVE_REALIZATION`; it must not fail them merely for
lacking a named replacement syscall.  A later contract can admit such a pair
only by freezing its boundary markers and oracle before execution.

## 8. Permitted conclusions

Passing R0.1A can establish bounded laboratory conformance, truthful deletion
observations, exact retained-evidence replay, and scoped live-kernel witnesses
or non-witnesses.  It cannot establish global minimality, physical durability,
unlike physical realization, participant cognition, concurrency, freshness,
writer authority, malicious integrity, or futures outside the frozen corpus.
Those entries remain structured `UNKNOWN` or `UNSUPPORTED`, never zero.
