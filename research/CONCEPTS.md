# Concept ledger

No entry is a commitment to a final primitive.

## Exact artifact

- **Meaning:** a bounded, exactly retained sequence of octets together with enough algorithm identification to verify its content address.
- **Why proposed:** decoded or normalized values may erase distinctions needed by future interpretation.
- **Smallest witness:** UTF-8 JSON byte sequences `{"a":1}` and `{ "a": 1 }` are semantically equal to one current parser but are different signed or forensically relevant evidence.
- **Can it be derived?** Exact original octets cannot in general be derived from a normalized parse.
- **Can it be merged?** Under test with occurrence and context.
- **Exposure:** machine-level; humans see an appropriate rendering plus access to raw evidence.
- **Kind:** preservation candidate, not yet a universal semantic primitive.
- **Runtime/storage cost:** O(bytes) ingest and storage before deduplication; hashing O(bytes).
- **Cognitive cost:** one distinction: evidence is not its interpretation.
- **Status:** candidate.

## Occurrence identity

- **Meaning:** a stable way to distinguish two captures even when their exact payload bytes match.
- **Why proposed:** repeated observations can have different sources, times, authority, or operational consequences.
- **Smallest witness:** the same webhook payload received once versus received twice.
- **Can it be derived?** Not from content alone. It may be derived from a lossless enclosing ledger position if that position is stable and specified.
- **Can it be merged?** Under test with the capture record address.
- **Exposure:** normally machine-only; visible in history/proof views.
- **Kind:** preservation candidate.
- **Runtime/storage cost:** one identifier or stable position per capture plus indexes.
- **Cognitive cost:** “same content” differs from “same occurrence.”
- **Status:** candidate.

## Framing

- **Meaning:** preservation of boundaries among opaque components or records.
- **Why proposed:** concatenation otherwise collapses `[a, bc]` with `[ab, c]`.
- **Smallest witness:** those two byte sequences require different later parsing.
- **Can it be derived?** Only if boundaries already exist in retained bytes or externally specified lengths.
- **Can it be merged?** Likely a format property rather than a semantic concept; under test.
- **Exposure:** machine-only.
- **Kind:** interchange/realization candidate.
- **Runtime/storage cost:** length/tag overhead.
- **Cognitive cost:** none in ordinary work.
- **Status:** candidate.

## Acquisition context

- **Meaning:** retained evidence about how, where, and under what capture conditions an artifact was obtained, without treating that evidence as the artifact’s interpreted domain meaning.
- **Why proposed:** identical bytes from different origins or incomplete captures must not be silently equivalent.
- **Smallest witness:** a payment-provider response and an unauthenticated local replay containing identical bytes.
- **Can it be derived?** Not from payload content.
- **Can it be merged?** It may be another exact artifact associated by a framed capture record; under test.
- **Exposure:** summarized for humans, raw on demand.
- **Kind:** preservation/provenance candidate.
- **Runtime/storage cost:** variable metadata; indexes only for understood fields.
- **Cognitive cost:** “where did this come from?”
- **Status:** candidate.

## Interpretation

- **Meaning:** a versioned, inspectable proposal that some retained evidence denotes a structure or meaning.
- **Why proposed:** future understanding must be addable without mutating original evidence.
- **Smallest witness:** an unknown payload captured today and decoded after its format is published.
- **Can it be derived?** A particular interpretation may be mechanically derived by an identified parser, but the evidence-to-parser association and parser identity must remain inspectable.
- **Can it be merged?** Must be tested against observation and admitted truth; premature in Round 0001.
- **Exposure:** human-facing when relevant.
- **Kind:** semantic candidate for later rounds.
- **Runtime/storage cost:** parser execution, versioning, and optional cached projection.
- **Cognitive cost:** “what do we think it means?”
- **Status:** candidate, not exercised until Round 0002.

