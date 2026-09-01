# B1 harness scope and claim ledger

The executable harness is a falsification instrument for the frozen C0 finite
contract. It is not the architecture and does not establish global minimality.

## What the run establishes inside B1

- Every legal boundary prefix with at most four inbound crossings is generated;
  cuts after every completed crossing are retained.
- Union-admission residual behavior covers every normalized scheduler placement
  around at most two inbound attempts. `disabled` is observable; `UNKNOWN` is
  excluded from equivalence.
- Admission is observed before crossing: rejected attempts do not join history.
  The selector and admission observation mechanism are charged to the TCB.
- A separate stable right congruence closes the entire finite-value quiescent
  turn machine and its one-output cut states.
- Ordinal and canonical-representative encodings survive in-process
  encode/recover at every generated cut and differentially match the independent
  raw-trace oracle. No process restart is exercised.
- A clean second enumeration/refinement/table build reproduces the exact
  artifact digest, rank ordering, and canonical representatives.
- All 1,024 projections of the declared ten-component falsification grammar are
  checked. Each direct deletion has either a globally minimized bounded witness
  or an explicit derivability/redundancy verdict.
- Every unordered pair of corpus quotient classes is enumerated into a
  deterministic certificate. The certificate proves branch coverage; it does
  not claim a separately materialized minimized witness for every pair.
- Fresh G01--G09 separations, E01--E09 equivalences, and the ten-output-kind
  restart matrix are literal goldens.
- A quotient-compatible observer is rebuildable for both encodings. An added
  observer that distinguishes E03 cannot be migrated deterministically from
  either old encoding. `R` remains in-band interpretation selection, not
  contract evolution.

The emitted witness core is deduplicated and fixed-point 1-deletion-minimal
relative to retaining the exact named endpoints plus one collision for every
unsound direct component deletion. It is not claimed to be the globally
smallest corpus under a different coverage definition.

## What remains unknown or unsupported

Fresh values and operations, malformed framing semantics, concurrency,
reordering, time, audit, authorization, privacy, capture/torn-write failures,
physical output-delivery races, effects beyond crossing `DO`, resource
deadlines, unbounded key growth, human cognition/error, physical-media
interchangeability, and class-splitting contract evolution are unsupported.
Actual process restart/restore is also unsupported: every current encode/recover
check executes inside one CPython process with already-constructed code and
artifacts.

The software differential test is not a cross-physical-realization test.
Benchmark timings are measurement-only and are excluded from deterministic
evidence. SHA-256 collision resistance is an assumption. The per-instance
digest is only a same-runtime artifact-mismatch guard, not a portability
mechanism or C0 history-witnessed `MUST SURVIVE` item in a singleton
fixed-specification deployment. It is currently 64 UTF-8 hex characters; 32
bytes describes only theoretical binary packing.

## Common-mode risk

The raw oracle imports no quotient or candidate code. Literal goldens,
metamorphic equivalences, an exhaustive logical-cut matrix, differential tests, and
a deliberate transition-table mutation provide independent pressure. However,
the oracle, quotient, candidates, and tests still share the B1 reading, frame
values, CPython runtime, standard library, and one host. Correlated
specification/runtime defects remain possible.

## Commands

```sh
python3 -m unittest -v zero-ground-restart/test_b0.py
python3 zero-ground-restart/run_b0.py --deterministic
python3 zero-ground-restart/run_b0.py
```
