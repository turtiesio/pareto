# Independence record

## Semantic inputs read

The implementation used exactly these pre-existing files:

1. `../FROZEN-B0.md`
2. `../CONTRACT-B1.md`
3. `../SCOPE-B1.md`
4. `../PROCESS-RESTORE-B3.json`
5. `../FIRST-MILESTONE.md`

No `c0_*.py`, `test_*.py`, generated Python transition table, or
`REALIZATION-*` / `RUNTIME-BREAKER-*` artifact was read. The implementation
does not import, invoke, or translate Python. It uses Rust's standard library
only and has no crate or network dependency.

After the semantic machine, quotient, representatives, envelopes, and both
state streams were independently complete, a direct parent instruction
declared a late public wire amendment for the transition transcript. It
supplied the `ZGTR` header and the `S/O/M/C/A/N/V` record tags. That message was
not a file and supplied no state, representative, transition, or expected
behavior table. The amendment was necessary: the allowed B3 JSON names the
record fields but does not specify this header or these tags, so its published
transition SHA-256 values cannot be derived from the five files alone. The
implementation records this as a specification-provenance limitation rather
than pretending the missing framing was inferred.

The system `sha256sum` executable was used only to cross-check byte streams
created by this Rust program while debugging the local SHA-256 implementation.
It supplied no semantic input. Cargo and `rustc` were used to format, compile,
and test the new crate.

## Provenance note

Because all agents shared one worktree, the root agent accidentally included
an early, incomplete version of the new Cargo files in an unrelated commit
before this implementation was finished. No reset or staging operation was
performed here. A hidden-suite commitment reportedly predates completion, but
no hidden-suite content or result was disclosed. Git commit chronology alone
therefore does not demonstrate this implementation's independence; the input
quarantine above is the relevant claim.

## Limitations

- This realizes only the frozen, finite B1 laboratory machine. It says nothing
  about fresh values, malformed application frames, concurrency, time,
  authorization, privacy, deadlines, or contract evolution that splits an old
  class.
- Rust is an unlike software runtime relative to the reported CPython B3 run,
  but this is still one host and ordinary filesystem/process environment. It
  is not a power-loss, torn-write, physical-media, or physical-effect test.
- The external artifact digest selects the semantic bundle. As in B3, it does
  not integrity-bind an individual rank or representative payload.
- Canonical representatives are synthetic behavioral class names, never
  historical provenance.
- Transition chunk digests are not implemented; the public amendment declared
  them unnecessary for this independent result. The exact global transcript
  and its SHA-256 are implemented.
