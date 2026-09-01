# Independence record

The implementation was written from the frozen normative contract family and
the exact `R01B-S1.json` artifact at commit `807f2cc`. It has no third-party
crate dependencies and implements SHA-256, TV, canonical JSON, record parsing,
fixture interpretation, and semantic modeling directly in Rust.

The author did not read or copy the Python builder/generator implementations,
Python breaker implementations or outputs, or any file beneath the pre-existing
`rust-realizer` directory. The existing implementation was observed only as an
excluded pathname while enumerating the repository. Frozen S0/closure indexes
were read for their published hashes and IDs; neither they nor S1 were edited.

The shipped code does not invoke Python, Node, or another candidate parser.
During development, Node's standard JSON parser was used only for concise
counts and shape inspection of the authoritative S1 bytes. Those diagnostics
were not used as runtime machinery and are not a gate-R trial or dependency.
