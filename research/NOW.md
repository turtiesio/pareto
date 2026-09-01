# Current research state

As of: 2026-09-01, before completion of Round 0001.

## Current best candidate(s)

None has survived a complete round. The active comparison is between exact opaque preservation, preservation with a separate capture envelope, generic parsed structure, and statement-like normalization.

## Irreducible concepts currently surviving

None yet. Even byte sequence, occurrence identity, framing, and acquisition context are candidates under test rather than accepted semantic primitives.

## Human mental model currently surviving

None yet. Provisional recovery questions for testing are: “What was actually retained?”, “What interpretation, if any, was added?”, and “What evidence would be lost if this record were normalized?”

## Human chunking/navigation model

Unresolved. A bounded view is required; no hierarchy, scope, module, graph, or lens has yet survived.

## Current trusted computing base

Research harness only. No semantic guarantee is currently claimed. Round 0001 will measure exact-byte hashing, framing/serialization, and verifier code separately.

## Known hidden complexity

- An “opaque blob” pushes boundaries, source, time, occurrence, and completeness into an unstated capture convention.
- A generic map/list tree pushes semantics into keys and parsers and may erase syntax, duplicate keys, order, or exact numbers.
- A universal statement payload may conceal an entire expression language.

## Current physical realization model

None. The first experiment uses an in-memory/file-scale evidence archive only to falsify preservation claims; it is not a proposed universal storage model.

## Current Pareto frontier

Unmeasured initial candidates: opaque artifact only; artifact plus lossless capture envelope; raw artifact plus derived parsed projection; normalized statement representation.

## Known semantic failures

- Content-only storage is expected to collapse repeated occurrences and acquisition context.
- Parsed-only storage is expected to lose distinctions that later parsers may need.
- No current candidate yet expresses admitted truth, derivation, action, authority, or time semantics.

## Known cognitive failures

No blind test has yet run. Internal names must not be treated as evidence of comprehensibility.

## Known performance/storage bottlenecks

Exact raw preservation duplicates bytes unless content and occurrence are separated physically. Provenance and history overhead are not yet measured.

## Known evolution/core-edit failures

Not yet tested.

## Unsupported guarantees

All semantic guarantees beyond lossless capture are currently unsupported.

## Next highest-information experiment

Minimize the pair of observable worlds that an artifact-only archive collapses, and test whether an occurrence envelope preserves the difference without smuggling a semantic language into metadata.

