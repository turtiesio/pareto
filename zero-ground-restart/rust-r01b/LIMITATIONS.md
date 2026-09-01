# Scope and authority gaps

The following are deliberately not filled with private conventions:

- The contract states `BH`, `B_input_key`, and `B_response` with `typed(...)`
  notation but does not freeze an exact enclosing map/key byte schema. This
  crate retains and compares the separately declared exact component bytes; it
  does not serialize a guessed enclosing value.
- The envelope prefix and five high-level members are declared, but a complete
  closed schema for the canonical record stream, raw packs, inventory pack, and
  all verifier records is not available here. No private envelope or canonical
  trial-record serializer is provided.
- No exact canonical gate-R manifest construction, digest domain, or
  realization-ID rule is declared in the inputs used here. Inventory helpers
  retain hashes and unknowns but do not mint an ID.
- Actual filesystem publication, checkpoint control, process kill/reap,
  tracing, passive observation, evidence replay, and measurement collection
  are not implemented. The pure service model makes no OS, persistence,
  power-loss, or physical claim.
- Registered LAB-only attacks are decoded as opaque typed inputs and are never
  executed by this crate.
- A continuation other than the frozen empty `C`, an unregistered payload,
  cut, setup, mechanism, or fault, and unavailable OS/physical evidence are
  rejected or returned as unsupported/unknown; they are never assigned a
  fabricated passing value.

Consequently, the crate supports cross-realization comparison of exact declared
B components after an external apparatus has established comparability and
complete execution. It does not itself establish those apparatus facts.
