# AO-R01-v1 breaker object

`R01-BREAKER-OBJECT.json` is the canonical materialization of the independently drafted R0.1 held-out attack design.

- Byte length: `22945`
- SHA-256: `99f81a9a4d4f4bf55109a9f43b7cd361c887c9b0b7255a22d009767238e79dfa`
- Encoding: UTF-8 without BOM, insignificant whitespace, or trailing newline; object keys are ordered by ascending unsigned UTF-8 bytes; arrays preserve declared order; binary values are lowercase hexadecimal.

The comparator has two views. `RECOVERY` compares exact recovery bytes only. `FULL` additionally includes the declared mutation, exact stage stream, truthful operation facts, kill/wait/reap ordering, effective environment, all mandatory measurement leaves, and evidence availability. A case passes only when `FULL` passes; a matching recovery projection cannot override an invalid or incomplete full history.

The design was drafted independently from histories and distinguishability using only `ground.md`, `REALIZATION-CONTRACT-R0.md`, `REALIZATION-AUDIT-R1.md`, and `REALIZATION-GATE-R0.md`; the breaker did not consult or communicate with the builder while drafting it. This materialized object **postdates the frozen builder candidate**. It must not be cited as a hidden-before-builder commitment; it is frozen for subsequent runner/implementation work and may not be weakened after outcomes are observed.

The object is an attack instrument, not a system architecture. Prospective stale-collision, marker-only, power-loss, recovery-fault, environment, measurement, and evidence-availability profiles do not retroactively broaden literal R0 claims.
