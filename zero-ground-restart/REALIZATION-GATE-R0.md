# REALIZATION GATE R0

Date: 2026-09-01

## Verdict before implementation

The available machine exposes two writable guest-level storage implementations,
but not two defensibly identified physical substrates. Any local execution can
test process isolation, unlike runtimes, VFS/ext4 versus VFS/tmpfs behavior,
framing, recovery, and live-kernel fault cuts. It cannot establish physical
media independence, power-loss durability, or cold recovery.

This gate was stated before the R0 conformance implementation was written. The
pre-implementation contract is `REALIZATION-CONTRACT-R0.md`, SHA-256
`3bdaa119942ef994e4ef0cf1c570d4518a2531bc102505065d967fed08522f15`,
committed as `83097e5`.

The builder, breaker, and formal auditor assessed the environment independently
and converged on the same physical limitation. Their agreement is process
provenance recorded by the supervising run; the repository hashes the resulting
documents, not the agents' private observation histories.

## Measured guest facts

Read-only inspection produced these facts:

| Probe | Observed value |
|---|---|
| virtualization | `kvm` |
| workspace mount | `/dev/sda1`, ext4, `rw`, `commit=30` |
| `/tmp` mount | the same `/dev/sda1` ext4 mount as the workspace |
| workspace and `/tmp` device number | both `2049` |
| `/dev/shm` mount | tmpfs, device number `26` |
| guest block model/vendor | `QEMU HARDDISK` / `QEMU` |
| guest block cache | `write back` |
| force-unit-access flag | `1` |
| stable-writes flag | `0` |
| swap | 8,589,930,496-byte `/swapfile` on the guest filesystem; active |
| other exposed medium | read-only 4 MiB `QEMU DVD-ROM`; not authorable |

No writable MTD, DAX, PMEM, NVMe-class device, removable medium, or network
filesystem is exposed. Loop devices would only re-encode a file on an already
counted backing store. Firmware NVRAM has no identified safe scratch allocation
and is excluded to avoid risking the guest.

Consequently:

- ext4 and tmpfs are unlike guest kernel storage paths;
- tmpfs is not proven to remain only in physical RAM because swap is active;
- the ext4 device is virtual and its host controller, cache, medium, and flush
  behavior are undisclosed; and
- both guest paths may ultimately depend on the same physical failure domain.

## Small conditional collision witnesses

These witnesses do not silently broaden B1 or R0. Each becomes binding only if
the stated future is admitted by a later contract.

| Responsibility omitted | Histories made identical | Smallest distinguishing future |
|---|---|---|
| accepted-boundary capture | an accepted crossing followed by failure before capture / no crossing followed by the same failure | recover, then issue the continuation whose result depends on that crossing |
| physical output-delivery accounting | output delivered, then failure before recording delivery / failure before delivery | recover: suppress versus emit to obtain exactly-once delivery |
| acknowledged power-loss durability | acknowledged write of new state / no acknowledged write, both recovering the old state after loss of volatile cache | cold recovery must return new versus old |
| integrity against valid-state corruption | valid state `q1` changed into the complete valid codeword for `q2` / legitimate `q2` | the minimized continuation separating `q1` and `q2` |
| freshness selection | latest `q1` with stale `q0` selected / genuinely latest `q0` | a continuation separating `q1` from `q0` |
| writer authority | unauthorized coherent publication / authorized publication of identical bytes | an authority-sensitive observer or audit query |
| bundle/version binding | complete state, bundle, and digest substitution / legitimate substituted system | an independently anchored version or policy query |
| physical failure independence | two same-device copies / one copy, both lost by one virtual-device failure | recovery after that admitted device failure |

Checksums do not resolve coherent valid substitution. Replication on one virtual
disk does not establish independent failure survival. A pathname, parent-held
hash, deployment prompt, operator memory, or remote service can carry a needed
distinction, but that is externalized persistent state and TCB rather than a
deletion.

## Minimum gate for a physical-realization claim

A later experiment may advance the physical claim only if it records all of:

1. a contract-level definition of what makes the two realizations unlike and
   the exact nominal and fault continuations permitted;
2. substrate and controller provenance below the virtualization boundary;
3. exclusive, safe writable regions on each medium;
4. declared capture, commit, acknowledgement, delivery, corruption, and
   recovery cuts;
5. write completion followed by producer/source removal and independent
   readback, excluding page-cache-only survival where durability is claimed;
6. controlled power interruption and every admitted medium-specific fault cut;
7. cold recovery and the same observation comparator on both realizations; and
8. a ledger of common TCB, common failure domains, and any external trust
   anchor.

Candidate examples would be two independently controlled media technologies,
such as a dedicated NVMe namespace and removable flash or optical/WORM media,
with known controller paths. Merely using two formats, processes, directories,
loop devices, or filesystems on the present guest does not pass this gate.

## Honest local work still available

Two attacks remain executable and useful without crossing the gate:

- the finite R0 ext4/tmpfs publication, process-kill, truncation, corruption,
  stale-replacement, simulated-I/O, TCB, operations, and measurement round; and
- bidirectional exchange with an independently authored Rust implementation of
  the frozen B1 language contract, removing CPython and Python-generated tables
  from one side of the comparison.

The first can establish only unlike guest-storage behavior while the kernel
remains live. The second can establish only unlike-runtime/software
portability. Both must report physical realization as `UNKNOWN`, and neither
can substitute for the unavailable gate above.

