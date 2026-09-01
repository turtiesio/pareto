# Independent Rust R0.1B semantic realization

This crate is a dependency-free, independently coded reader/model for the
frozen R0.1B semantics at repository commit `807f2cc`. It does not implement or
claim a gate-R realization, and it must not be used to launch registered
subject trials before that separate gate is authoritatively frozen.

Implemented scope:

- exact tags `01..0b` for the recursive TV encoder/decoder, including strict
  map ordering, distinct signed/unsigned integers, and structured
  unknown/unsupported values;
- an independently implemented SHA-256 and strict lowercase-hex codec;
- exact `D_sem || P || H` record construction and recovery parsing;
- exact closed publication/recovery fixture schemas and the four setup labels;
- final `d0` descriptor decoding and exact trial-ID recomputation;
- strict, zero-copy validation of the frozen canonical-JSON profile;
- interpretation of all S1 record, setup, recovery-recipe, descriptor, literal
  B-component, and comparison-edge vectors;
- exact `publish_result` and `recovery_observation` wire components;
- a pure in-memory model of the declared publication/recovery component
  semantics, checked against every frozen subject literal; and
- exact-file and current-process loaded-object inventory helpers, with
  unavailable platform/physical bytes reported as structured unknowns.

Run offline frozen-vector validation (this does not launch a subject):

```text
cargo test
cargo run --bin r01b-inspect -- validate-s1 ../R01B-S1.json
```

Inspect exact explicit files plus the inspector process's file-backed mappings:

```text
cargo run --bin r01b-inspect -- inventory Cargo.toml Cargo.lock src/lib.rs ../R01B-S1.json
```

The output is diagnostic inventory, not an evidence envelope or realization
ID. See `LIMITATIONS.md` before using the library in a larger apparatus.
