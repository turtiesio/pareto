# B1 transition wire amendment R1

Date: 2026-09-01

## Status

This is a late public byte-level amendment for the B3 transition transcript.
`PROCESS-RESTORE-B3.json` declared the logical record fields and their order,
but did not declare the header, field tags, membership sentinel, or list-item
tag. An independent implementation could regenerate the B1 quotient, both
complete state streams, and all semantic transitions from the previously
published language contract, but it could not derive the advertised transition
SHA-256 from those materials alone.

The missing bytes were supplied to the Rust implementer only after it had
matched both complete state-stream hashes. This document makes that late input
auditable. It does not retroactively make the original B3 evidence
self-specifying.

All integers below are unsigned big-endian. `LP(X)` is
`uint32(length(X)) || X`. Tokens are their exact B1 UTF-8 bytes.

## Header

The transcript begins with exactly:

```text
ASCII("ZGTR")
uint8(1)
uint8(candidate_tag)             # ordinal = 1; representative = 2
artifact_digest[32]              # raw bytes, not hexadecimal text
uint32(state_count)
uint32(operation_count)
ASCII("proof-domain-membership-v1") || 00
LP(operation_0)
...
LP(operation_16)
```

The operation order is `resume` followed by the sixteen exact inbound tokens
listed in `PROCESS-RESTORE-B3.json`.

## One transition record

For every state envelope in stream order and every operation in the declared
order, append exactly:

```text
ASCII("S") || LP(current_state_envelope)
ASCII("O") || LP(operation_token)
ASCII("M") || LP(membership)
ASCII("C") || uint32(client_output_count) || client_items
ASCII("A") || uint32(action_output_count) || action_items
ASCII("N") || LP(next_state_envelope)
```

`membership` is the single ASCII byte `N` for `resume`, or exact ASCII
`enabled` / `disabled` for proof-level inbound-domain membership. It is not a
physical output frame.

Each client or action item is:

```text
ASCII("V") || LP(exact_output_token)
```

There is no padding, terminator, EOF marker, or newline. SHA-256 covers the
entire header and every record byte in order.

## Responsibility verdict

These framing choices are not history information and need not be persisted in
every instance. They are **MAY REBUILD** only from an exact available wire
specification plus a correct encoder/decoder. The specification bytes,
implementation, version selection, and hash implementation remain semantic
machinery, operations, and TCB. Omitting them externalizes interpretation into
private source code or convention and makes independent reconstruction
unsupported.

