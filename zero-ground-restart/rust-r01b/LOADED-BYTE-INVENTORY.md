# Loaded-byte inventory boundary

This is a pre-gate inventory design, not a gate-R manifest or ID.

Available realization bytes to retain include `Cargo.toml`, `Cargo.lock`, all
files under `src/`, `tests/frozen_s1.rs`, and this crate's documentation. The
offline frozen-vector test additionally loads the exact adjacent
`R01B-S1.json`. Normative authoring inputs are the four realization contract
files plus the S0 and semantic-closure indexes. The crate has zero third-party
Cargo packages.

At execution, `current_process_inventory()` hashes the exact current executable
and each readable absolute file-backed mapping from `/proc/self/maps`.
`observe_files()` hashes every explicitly supplied regular file in unsigned
pathname order. Both retain full byte lengths and SHA-256 values rather than
substituting a hash for bytes in an evidence claim; the caller remains
responsible for retaining the files themselves.

The following cannot be completely inventoried from this guest process and are
always reported as unknown: kernel/configuration bytes, OS bytes not surfaced
as mappings, Rust standard-library source/provenance beyond compiled executable
bytes, hypervisor/host bytes, storage controller/firmware bytes, and physical
media state/behavior. Build-time Cargo/rustc and authoring-time diagnostic tool
bytes are process inputs to those separate workflows, not silently included in
a future execution claim; a later freeze must retain their exact versions and
bytes if it builds or tests inside the credited run.

Observed development tool versions were `rustc 1.98.0
(88d9e12ae 2026-08-18)` and `cargo 1.98.0 (797e8a9bc 2026-08-05)`. This version
text is informational and is not a replacement for exact toolchain bytes.
