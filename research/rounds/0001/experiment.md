# Experiment

## Minimal corpus

1. arbitrary octets including invalid UTF-8 and empty content;
2. identical payload delivered twice under different acquisition context;
3. no acquisition artifact versus an acquired zero-length artifact;
4. JSON documents that parse equally but differ in whitespace;
5. JSON with duplicate keys versus the single surviving key;
6. unknown future fields and an unknown context format;
7. export tampering and duplicate occurrence addresses.

## Apparatus

`model/round0001.py` implements:

- `ArtifactOnlyArchive`, the deletion candidate;
- `AcquisitionTranscript`, separating deduplicated exact artifacts from occurrence records;
- `normalized_json`, a deliberately lossy parsed-only competitor;
- deterministic experimental export/import with explicit hash algorithm, exact size, duplicate-field rejection, and integrity verification.

The format is test apparatus. Its JSON/Base64 choice is not a longevity decision.

## Falsifiable properties

- Every byte sequence presented at the payload/context boundary is recoverable exactly.
- Repeated equal payloads remain distinct occurrences while content may deduplicate.
- Missing and present-but-empty acquisition artifacts do not collapse.
- Adding interpretation never requires mutating retained evidence.
- Corruption of stored bytes is detected by the declared integrity algorithm.
- Unknown meaning is accepted as uninterpreted evidence, not declared valid or actionable.

## Deletion/merge/derivation trials

- Delete occurrence identity: replay duplicate delivery.
- Merge occurrence identity with content identity: replay same bytes from two contexts.
- Delete exact bytes after parsing: replay formatting/signature and duplicate-key cases.
- Merge missing with empty: replay a later format in which zero-length is a meaningful acquisition record.
- Derive occurrence from stable ledger position: evaluate whether explicit occurrence identity can later be deleted.
- Treat acquisition context as one opaque artifact: count the capture protocol/specification as hidden complexity and test whether current queries require understood fields.

