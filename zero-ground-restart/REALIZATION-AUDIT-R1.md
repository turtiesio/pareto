# ZERO GROUND realization/runtime audit R1

Date: 2026-09-01

## Outcome

This round strengthens the conditional B1 milestone in two directions:

1. an ontology-neutral, two-history R0 corpus was executed through ext4 and
   tmpfs with process-kill cuts and a finite corruption campaign; and
2. an independently authored Rust implementation exchanged both complete B1
   encodings bidirectionally with CPython and reproduced every frozen one-step
   behavior.

It does **not** complete the total ZERO GROUND goal. The actual target contract,
physical media experiment, human study, global future completeness, and a least
total implementation remain absent or impossible to infer. The strongest new
positive claims are finite guest-filesystem conformance and finite unlike-runtime
software portability on one host.

This audit preserves two falsifications discovered after the generated evidence
was frozen:

- the R0 operation-deletion harness emits stage acknowledgements for operations
  it skipped, so its `fsync` and exclusive-creation `NO_WITNESS` conclusions are
  not valid under the literal R0 boundary; and
- the held-out runtime suite has 21 portable diagnostic-category failures even
  though all B1-level accept/reject decisions and accepted behaviors match.

## R0 guest-storage result

The frozen contract is `REALIZATION-CONTRACT-R0.md`, SHA-256
`3bdaa119942ef994e4ef0cf1c570d4518a2531bc102505065d967fed08522f15`.
The generated evidence is `REALIZATION-EVIDENCE-R0.json`, SHA-256
`ff63d1a959b0d24c9817a13b3f2ed6ed98fd1d3b8b1c9b69bac3d1aad0c8c341`.

The smallest frozen opaque suite uses:

```text
P0 = empty       P1 = 00
C  = empty
Y0 = empty       Y1 = 00
```

The two payload positions and two output positions each need at least one total
byte to be unequal; the continuation can be empty. The two histories are
separated by the one continuation and exact observations
`02 00000000` versus `02 00000001 00`.

The full run passed 2,468/2,468 declared conformance trials:

| Trial family | Count |
|---|---:|
| publication-cut rows | 84 |
| single-bit mutations | 2,064 |
| proper-prefix truncations | 258 |
| coherent-replacement controls | 6 |
| short-write simulations | 16 |
| injected I/O-error simulations | 20 |

All 1,234 ext4/tmpfs semantic projections matched. The conformance certificate
is `5221b50e8e5e0b18ee818cfdd5b4d5ce303151c35bdbb527017ab6b9334090c0`.
This establishes the exact finite observations only while the guest kernel
remains running. It is not power-loss or physical-media evidence.

### Record deletion result

R0's candidate record was:

```text
D[32] || P || H[32]
```

It did not survive its own attack. An alternate `P || H` encoding passed 595
adapted finite checks, reducing the empty/one-byte records from 64/65 to 32/33
bytes. `H` is still computed using the trusted `D` rebuilt from the frozen
contract, suite, and adapter bundle.

The precise verdict is:

- the redundant **per-record copy** of `D` is MAY FORGET in R0;
- the numeric `D` value is MAY REBUILD only from exact surviving `Q`, `A`, five
  suite values, hash specification, and correct bundle selection;
- suite-identity selection is not deleted—it remains in the recovery bundle,
  generator, deployment selection, and TCB; and
- if wrong-suite rejection is required, the identity responsibility MUST exist
  somewhere in the total system.

The alternate codec/parser attack ran in process. It is not yet a second
fresh-process realization, and its external specification/bundle cost is not
zero.

The separate lookup attack does not reconstruct the historical spelling of
`P`. It retains a distinguishing `H` plus a charged two-entry result map and
reconstructs only required behavior. Raw `P` spelling is MAY FORGET in finite
R0 only if that surviving distinction and behavior map preserve every allowed
observation.

### Mechanism-deletion correction

The frozen R0 contract says a stage frame is emitted only after its named
operation returns successfully. The mutant worker options
`--skip-file-fsync`, `--skip-directory-fsync`, `--skip-replace`, and
`--skip-exclusive-creation` skip an operation but retain the same `a0 03`,
`a0 04`, `a0 05`, or opening-stage protocol. Those bytes falsely attest that
the named operation occurred.

Consequently:

- the ordinary, non-mutant 2,468-trial conformance result remains valid;
- the 112 mechanism-deletion executions are useful projected recovery probes,
  but they are not legal literal-R0 executions for a skipped named operation;
- file `fsync`, directory `fsync`, and exclusive creation are **UNKNOWN under
  literal R0 deletion**, not MAY FORGET and not proven unnecessary;
- if stage frames are prospectively redefined as cut labels independent of the
  skipped calls, the recovery-only projection found no split across 28 rows for
  each of those mechanisms; that is a different contract; and
- deleting replace produced 12 recovery differences even under that projection,
  showing that an old/new atomic publication-selection responsibility is
  needed. This does not privilege the `rename` syscall as the only possible
  mechanism.

This is also a TCB witness: a stage supervisor can emit contract-shaped bytes
while lying about the operation they certify. Correct attestation/capture logic
cannot be credited as zero complexity.

## Unlike-runtime result

The Rust/std-only implementation read the five attested language/evidence files
listed in `rust-realizer/INDEPENDENCE.md` and no Python implementation or table.
It independently enumerated 83,352 reachable boundary cuts, 10,420 quiescent
states, and 82,584 stable boundary classes.

The complete cross-runtime results are:

| Candidate | State bytes / SHA-256 | One-step records / SHA-256 |
|---|---|
| ordinal | 3,716,290 / `253cb73a89dce87bee4ed1c5c4bc22eddffbd848e3a805037d00fd71c16740ec` | 1,403,928 / `293cca6b94d8dd0e727c6ecf9d55ac0aac0dae8707a365206bf762049056aaa3` |
| representative | 18,053,209 / `5aa508e648df5a43fd6cea5ff0552daed5faa1e9903e6841e3fde657755ef2f5` | 1,403,928 / `4ff1ba87a2f2f30bc1c93678e9d00a61aa3ce37a4b3dd04e65052a976b62dec6` |

Python-produced bytes were consumed by Rust; after that producer exited, Rust-
produced bytes were consumed by Python. Both consumers recovered all 82,584
unique classes. The two producers' files compare byte-for-byte equal for both
candidates. This is unlike-runtime/software evidence, not unlike physical
realization: the runs share one Linux kernel, x86-64 CPU, filesystem, host,
artifact identifier, comparator expectations, and SHA-256 assumption.

### Late wire-specification discovery

The old B3 JSON named transition fields but did not specify the exact header,
tags, membership sentinel, or list-item framing. The Rust implementation matched
both complete state streams before receiving those missing bytes, but could not
derive B3's transition digest from the published inputs alone.

`TRANSITION-WIRE-R1.md` now declares the exact `ZGTR` grammar. This is a late
amendment, not evidence that B3 was already self-specifying. The wire grammar is
MAY REBUILD machinery only from an exact available specification and correct
codec; otherwise interpretation has merely moved into private source code or
convention.

## Held-out runtime attack

The breaker committed to canonical JSON length 13,666 and SHA-256
`85741dda1ed537ef5225a1514d0947d277f4ee552b5234ea038fb6c8551e2e97`
before implementation completion. The materialized object matches that
commitment.

The first runner execution passed its three test methods and established:

- 140/140 accept-or-reject decisions across Python and Rust;
- 30/30 locale/environment logical checks;
- 85/85 exact transition comparisons for all 17 operations at ranks
  `0, 1, 4, 66051, 82583`;
- coherent rank-0 to rank-1 substitution is accepted by both runtimes and
  changes the required `resume` behavior; and
- all five capture/publication profiles remain unclaimed and
  `UNSUPPORTED_BY_B1_B3`.

However, the committed breaker object calls `expect.code` a portable category.
The runner recorded but deliberately did not assert those categories. Strictly
evaluating the committed object gives:

```text
portable category conformance: 119 / 140
category failures:              21
Python category failures:        6
Rust category failures:         15
```

Python collapses several truncation/trailing distinctions. Rust additionally
collapses unknown-tag versus selector mismatch, several representative failure
classes, and transport versus recovery phase. Rust has no explicit one-mebibyte
payload guard; the committed oversized vector is rejected through a generic
length mismatch. Thus:

- frozen B1 semantic portability passes;
- the stronger held-out portable error-taxonomy contract fails;
- transport-versus-recovery phase conformance is unsupported, not merely a
  differently worded success; and
- no retrospective weakening of the committed suite is used to turn that
  failure into a pass.

The runner's phrase that it does not test “an independent implementation”
should be read as “does not prove authorship/input independence.” Its output key
`physical_case_probes` names one-host runtime/environment probes and is not
physical evidence. The original runner and first-run hash are preserved; this
audit corrects the interpretation rather than rewriting the instrument.

## Information classification after R1

These remain verdicts about responsibilities, not fields or constructors.

### MUST SURVIVE

- Under B1, enough information to select the future-behavior class. The prior
  11/17-bit lower bounds and eight direct pressures remain unchanged.
- Under R0, a distinction between the committed `P0` and `P1` behaviors. Exact
  payload bytes may be replaced by another collision-free code plus identified
  decoding machinery.
- Under R0's admitted finite corruption observers, independently surviving
  redundancy/comparison responsibility sufficient to distinguish an accepted
  codeword from each required rejected mutation. This does not force `H` or
  SHA-256 specifically.
- Under R0's wrong-suite observer, suite identity/selection somewhere in the
  total system. Its in-band duplicate is not necessary.
- Under R0's old/new cut matrix, an atomic authoritative-publication selection
  responsibility. The experiment does not force a particular syscall, file, or
  storage layer.

### MAY REBUILD

- The numeric `D` value from the identified contract, adapter bundle, suite,
  hash specification, and trusted selector. The redundant per-record copy may
  instead be forgotten within R0.
- `H` at publication from `D`, payload length, payload, and the record tag. To
  detect later corruption, an independent comparison value or code constraint
  must still survive; recomputing from only corrupted source bytes is not
  detection.
- B1 ranks, representatives, transition/output maps, the `ZGTR` transcript,
  and compatible derived observers from exact surviving class information and
  identified specifications.
- Equivalent runtime machinery may be rebuilt or independently reimplemented.
  Bit-identical executable rebuild is UNKNOWN because reproducible builds were
  not tested.

### MAY FORGET

- Raw `P` spelling within finite R0 if a surviving state distinction and
  charged mapping preserve every permitted behavior; this is behavior
  preservation, not mechanical recovery of `P`.
- A duplicate cross-runtime test-stream copy only if the evidence contract
  permits certificate retention and the exact bytes remain deterministically
  regenerable from frozen specification plus identified machinery. A hash alone
  cannot reconstruct it.
- Runtime-specific diagnostic spelling under B1, which does not observe it.
  It is **not** forgettable under the stronger breaker taxonomy that failed.
- The prior B1 forgettability results remain scoped exactly as before; R0/R1 do
  not broaden them.

### UNSUPPORTED IF ADMITTED LATER

- coherent valid-state integrity, freshness, rollback prevention, writer
  authority, and bundle substitution without an independent surviving anchor;
- migration for an observer that splits an old B1 equivalence class;
- capture of an accepted crossing across a failure before publication;
- exactly-once physical output delivery across a delivery/publication gap; and
- power-loss recovery or independent physical-medium failure.

## Simultaneous total-system ledger

No scalar score is used.

| Dimension | R0/R1 evidence and remaining limit |
|---|---|
| information/distinction preservation | R0 passes 2,468 declared trials; B1 Python/Rust exchange covers every class and one-step future; portable diagnostic categories fail 21/140; fresh futures remain unsupported |
| persistent state | R0 candidate 64/65 bytes is falsified by a 32/33-byte alternate; B1 remains 3 ordinal payload bytes or 0-236 representative bytes plus envelope; external bundle/identity/redundancy are charged |
| semantic machinery | R0 implementation/spec/test inventory is 126,591 bytes; Rust source/docs are 56,207 bytes; Python sources, wire spec, codecs, compilers, adapters, verifiers, and selectors remain machinery |
| human cognition | no participant role/task/error study; `UNKNOWN`; opaque-rank tooling and synthetic-representative confusion remain risks |
| authoring burden | source/line/fixture counts are measured; manual decisions, learnability, and author error rate remain `UNKNOWN` |
| query/navigation burden | one R0 continuation and no search infrastructure; exhaustive verifier scans all classes; deployed candidate lookup/replay trade-off remains |
| runtime | R0 has 2,580 child samples; cross-runtime has only one sample per role/candidate; Rust was locally faster with comparable/higher RSS, so no dominance claim follows |
| storage | logical/allocated record proxies, a measured 646,312-byte Rust binary, sources, dynamic libraries, build tree, test streams, optional transcripts, runtime/OS/media all remain separate and non-additive |
| operations | fresh processes, stage frames, kills/reaps, simulated errors, compilation, exact format coordination, bundle selection, cleanup, and evidence generation are charged; whole-process syscall totals remain unknown |
| TCB | common contract, expected answers, wire amendment, SHA assumption, Linux/CPU/filesystem; R0 adds stage truth, adapter, supervisor and fault injector; Python and Rust add distinct language machinery but still share many lower layers |
| evolution | compatible factor-through observer passes; known class-splitting extension remains impossible without lost external information; no format/generation/rollback protocol |
| portability | ext4/tmpfs guest semantics and CPython/Rust software exchange pass; other OS/architecture/host and physical portability remain untested/unknown |
| explainability | exact trial IDs, bytes, cuts and transition hashes exist; false stage attestation and collapsed error categories show remaining explanatory TCB; human comprehension unknown |
| information-loss risk | finite bit/truncation faults reject under SHA non-collision assumption; coherent valid substitutions are undetected; physical faults, malicious replacement, wrong common specification and capture gaps remain |

The candidates remain partially ordered. R0's smaller record moves suite identity
into trusted external machinery. Rust reduces one common runtime assumption but
adds a second implementation, compiler provenance, dynamic dependencies, and
coordination burden. Nothing here establishes one candidate no worse on every
dimension.

### Compact-evidence schema limitation

R0's compact JSON contains all fourteen dimension names, but it does not
instantiate every mandatory field promised by contract section 10. Missing or
incomplete items include instruction-word/concept counts, hand-authored versus
generated splits, several phase timings, directory/inode/evidence and runtime
storage, whole-process syscall/retry/setup/cleanup totals, and complete
component versions/bytes. The contract required an explicit
`{"status":"UNKNOWN","reason":...}` for a missing value; several fields are
simply absent. The compact measurement artifact is therefore partial, not full
section-10 conformance. The fuller generator ledger was not frozen as evidence.

The worker launcher also copies the ambient `os.environ` rather than a declared
allowlist, while the exact inherited environment is not recorded. Python `-I`
narrows import influence but does not remove loader or OS environment effects;
this remains unrecorded TCB. Recovery timeouts and signalled workers are not
converted by the supervisor into the contract's exact `REJECT` observation;
they escape or fail the trial. Frozen finite inputs did not trigger those
paths, so the broader recovery clauses are untested/unsupported.

Certificate streams are retained as hashes, not raw records. Reproduction
depends on the exact generator, inputs, serialization specification, runtime
assumptions, and sufficient resources continuing to exist; a hash alone cannot
reconstruct them.

## Provenance and operations incidents

- The independent Rust input quarantine is attested in
  `rust-realizer/INDEPENDENCE.md`; hashes prove resulting content, not private
  observation histories.
- Shared staging caused root commit `131a0e6` to include early builder and Rust
  files together with the hidden-suite commitment. External message chronology
  precedes completion, but Git history alone cannot prove hidden-before-builder
  ordering.
- A later commit `8650d3c` appeared in the shared repository while multiple
  actors used the same index. Its tree contains the final R0/Rust/hidden files.
  The frozen contract and evidence source hashes are unchanged, but authorship
  and commit coordination are operational/provenance TCB rather than clean
  evidence of agent independence.
- The held-out JSON commitment is still content-valid despite that chronology
  limitation.

## Full-goal status

The finite B1 quotient, R0 guest-storage run, and R1 unlike-runtime run are
defensible bounded milestones. They do not identify a contract-independent
smallest total system. The original full goal remains open because:

- no concrete real target contract instantiates the broad future observer,
  policy, viewer, actor, and realization language;
- global program/description minimality and a least element under a non-scalar
  partial order are not established;
- actual human cognition and authoring error are unmeasured;
- no unlike physical media, controlled power loss, cold recovery, physical
  delivery, or boundary-capture experiment is available; and
- several TCB mechanisms were attacked only through common code or invalid
  projected deletion variants.

The exact physical gate and its conditional collision witnesses remain in
`REALIZATION-GATE-R0.md`. Unknown capability remains `UNKNOWN` or
`UNSUPPORTED`; it is not credited as zero complexity.

The highest-value next local experiment is an R0.1 deletion round that freezes
truthful operation attestations separately from projected scheduling markers
and emits the full mandatory measurement schema. That would repair an
experiment boundary; it would not satisfy the unavailable physical or
cognition gates.
