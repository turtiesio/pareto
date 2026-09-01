# B1 Rust realizer

This crate is a Rust-standard-library-only realization of the frozen finite B1
turn machine. It enumerates reachable boundary cuts, computes the stable right
congruence, derives shortest lexical boundary representatives, and implements
both B3 persistence candidates.

Build and inspect the derived universe:

```sh
cargo build --release
./target/release/b1-realizer inspect
```

Produce or consume an exact B3 state stream (`-` means standard input/output):

```sh
./target/release/b1-realizer produce ordinal ordinal.zgps
./target/release/b1-realizer produce representative representative.zgps
./target/release/b1-realizer consume ordinal ordinal.zgps
./target/release/b1-realizer consume representative representative.zgps
```

`consume` strictly decodes every envelope and computes all 1,403,928 one-step
records. To emit the exact `ZGTR` transcript bytes as well as its digest:

```sh
./target/release/b1-realizer transcript ordinal ordinal.zgps ordinal.zgtr
```

Run focused tests, then the deliberately explicit exhaustive digest test:

```sh
cargo test
cargo test --release exhaustive_transition_digests_match_b3 -- --ignored
```

See `INDEPENDENCE.md` for the input quarantine and the late transition-wire
amendment limitation.
