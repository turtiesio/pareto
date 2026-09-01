# B1 harness scope and claim ledger

The executable harness is a falsification instrument for the frozen C0 finite
contract. It is not the architecture and does not establish global minimality.

## What the run establishes inside B1

- Every legal boundary prefix with at most four inbound crossings is generated;
  cuts after every completed crossing are retained.
- Union-domain residual behavior covers every normalized scheduler placement
  around at most two proposed inbound crossings. Equivalence compares the exact
  next-crossing domain before comparing enabled successors; `UNKNOWN` is
  excluded from equivalence.
- `enabled` and `disabled` are proof-oracle markers for membership in that
  domain, not emitted observations. A rejected proposal is a non-event outside
  boundary history. The domain selector is charged to the TCB.
- A separate stable right congruence closes the entire finite-value quiescent
  turn machine and its one-output cut states.
- Ordinal and canonical-representative encodings call their public `persist`
  and `recover` paths in-process for all 82,584 generated boundary classes.
  `resume` and all sixteen input-domain proposals are differentially checked
  against the independent raw-trace oracle at every class (1,403,928 checks).
- `PROCESS-RESTORE-B3.json` separately persists all 82,584 classes in a
  producer that exits, then reconstructs them and checks all 1,403,928 one-step
  behaviors in two fresh consumer processes per candidate against the
  independent raw oracle.
- A clean second enumeration/refinement/table build reproduces the exact
  artifact digest, rank ordering, and canonical representatives.
- The two sound direct deletions have exact exhaustive rebuild checks:
  `rule_on_0` is the B1 constant `0`; `owed_port` is `-` when quiescent,
  `action` exactly for owed kind `DO`, and `client` otherwise.
- All 1,024 projections of the declared ten-component falsification grammar are
  checked. Each direct deletion has either a globally minimized bounded witness
  or the explicit `MAY_REBUILD` classification and checked recipe above.
- Every unordered pair of corpus quotient classes has an executed, hashed
  minimized bounded witness. Selection exhausts every corpus history at each
  class's minimum crossing length and all contexts through the winning depth.
  The big-endian uint16 winning-context map is emitted as zlib+base64 data, not
  only as a hash commitment.
- Fresh G01--G09 separations, E01--E09 equivalences, and the ten-output-kind
  logical-cut matrix are literal goldens.
- The sole positive evolution probe is `current_b1_observer` over the enumerated
  corpus, where it factors through both encodings. An added observer that
  distinguishes E03 cannot be migrated deterministically from either old
  encoding. No general positive evolution result is claimed; `R` remains
  in-band interpretation selection, not contract evolution.

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
B3 exercises fresh-process reconstruction using distinct newly-created
directories on one host/runtime. It does not establish power-loss,
crash/torn-write, or physical durability semantics, cross-runtime portability,
or unlike physical realization; mount and network isolation are not enforced.
The artifact digest does not integrity-bind a state's payload, so protection
outside B3's parent stream-hash comparison remains an operational responsibility.

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
python3 -m unittest -v zero-ground-restart/test_process_probe.py
python3 zero-ground-restart/run_b0.py --deterministic
python3 zero-ground-restart/run_b0.py
python3 zero-ground-restart/c0_process_probe.py orchestrate
```
