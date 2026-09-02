# R0.1B RUN-BOUNDARY FEASIBILITY SUPPLEMENT

## Outcome and independence

This supplement preserves two fatal R0.1B defects discovered after
`FEASIBILITY-AUDIT-R01B.md` was frozen.  The breaker derived and froze the
findings below from the immutable R0.1B contract, S0/S1 corpus, holdouts, and
measurement registry before reading any R0.1C proposal.  R0.1C may answer
these attacks; it cannot reinterpret them into R0.1B passes.

The result remains `CONTRACT_DEFECT_UNDECIDABLE`.  No gate-R artifact was
created and no subject or LAB trial was launched.

## F8 -- the run/evidence topology is not constructible

R0.1B requires exactly one five-field evidence envelope for every submitted
descriptor.  The frozen measurement registry instead declares six run-scoped
evidence streams:

```text
apparatus_failures
canonical_records
inventory_pack
raw_measurement_pack
raw_trace_pack
replay_index
```

The envelope has fields for only the middle four.  It has no closed placement
or ownership rule for `apparatus_failures` or `replay_index`, no run
container, and no inner framing for raw channels, files, or canonical
records.

Smallest topology witness: take comparison-linked descriptors A and B.  If
A's sole envelope crosses L immediately, its edge aggregate can be invalidated
when B later finishes.  If A's envelope is deferred until B finishes, an
interruption before B leaves a submitted descriptor without the sole envelope
R0.1B requires.  The contract fixes neither behavior.

Smallest raw-framing collision:

```text
left:  stdout = 61,   stderr = 6263
right: stdout = 6162, stderr = 63
```

Unframed concatenation makes both `616263`; a later source-specific replay
query distinguishes them.  A private pack decoder would move the missing
distinction into implementation state and TCB.

A timeout after the first B crossing creates another uncovered history.  It
is neither either complete B production nor `CONTROL_UNAVAILABLE`, and R0.1B
defines no partial-B production or exact terminal/offending-field record.
Timeout and storage-exhaustion precedence is also unspecified.

Finally, the alleged positive replay fixture's `inventory_pack` is only the
18 bytes `ASCII("holdout-inventory") || 00`.  It cannot simultaneously be the
section-2 pack of exact contracts, registries, sources, hashes, and versions.
This contradiction is independent of the missing status lists recorded as F4.

The minimum correction responsibility is an explicitly framed run crossing,
closed ownership of run- and trial-scoped values, exact shared inventory bytes
once, framed per-trial records and raw sources, and closed partial and terminal
values.  Those are responsibilities forced by the witnesses, not proposed
architectural layers.

## F9 -- replay addressing is not constructible

The frozen `replay_selector_record` schema omits a stream coordinate, while
both replay holdouts add one.  It also fixes no run/envelope namespace or
offset origin.

The positive fixture selects trial
`r01b-dad8b571816d3bfc75f28a217e81ce5985cde623ec3502d52f2f07f888a5362e`
at ordinal zero.  That trial ID occurs in none of the 6,318 S1 rows.  Global
S1 ordinal zero instead names
`r01b-0000d590...`; a fixture-private index maps local ordinal zero to the
absent `r01b-dad8...` identity.  Local and global interpretations therefore
remain simultaneously possible.

Because trial identity also excludes realization and run identity, the same
tuple can address different raw bytes in repeated runs.  A hash detects a
wrong selected range only after a candidate range has been chosen; it does not
choose the run, envelope, pack, or stream.

The minimum correction responsibility is a closed address namespace that
binds the retained run, envelope, registered trial ID, global ordinal, pack,
stream ID, payload-relative offset, length, and selected-byte digest.  Every
non-fixture selector must resolve in the effective registry.  Exact target
bytes must remain available; the digest is not their replacement.

## Quantified storage collision

The frozen corpus contains:

| item | count |
|---|---:|
| all rows | 6,318 |
| subject rows | 3,028 |
| publication rows | 684 |
| recovery-only rows | 2,344 |
| LAB-only rows | 3,290 |
| comparison edges | 2,010 |

The twelve S0 member payloads contain 22,660,311 bytes; their canonical framed
manifest contains 22,660,748 bytes.  S1 contains 28,549,230 bytes.  One exact
semantic inventory therefore needs at least 51,209,541 member bytes, or
51,209,978 bytes when the already-frozen S0 framing is retained.

Literal per-descriptor duplication requires at least:

```text
51,209,541 * 6,318 = 323,541,880,038 bytes
```

That is about 301.322 GiB and 150.735 times R0.1B's 2,146,435,072-byte
raw/canonical budget.  Only 41 copies fit, before any descriptor, result,
trace, measurement, index, or terminal byte.  Physical block deduplication
does not change the required envelope bytes and therefore does not repair the
contract.

The frozen descriptor-template values alone contain 4,867,023 bytes.  Even
with an empty realization ID, complete overlays plus a single raw 32-byte hash
per row require at least 6,092,715 bytes.

The all-unrun TV list of the 6,318 fixed-width trial IDs alone needs 492,813
bytes of the inherited 1 MiB terminal reserve.  That fact does not prove the
reserve sufficient: framing, status, loss, offending-field, index, and
terminal values were not closed in R0.1B.

## Persistence consequences

### MUST SURVIVE

- The exact semantic and realization inventory member bytes required by later
  interpretation or replay survive at least once per retained run.  A digest,
  remote locator, filesystem deduplication, or operator convention is not a
  substitute.
- The exact accepted bytes of every raw source survive together with enough
  source/range responsibility to reject the `a|bc` versus `ab|c` collision.
- Actual partial B crossings, stopping cause, accepted prefix, and unrun-row
  responsibility survive whenever a later completeness or replay query may
  distinguish them.
- Run and address selection responsibility survives wherever the same trial
  identity can occur in more than one retained run.

### MAY REBUILD

Given those exact bytes and a complete identified specification, hashes,
lengths, byte offsets, indexes, aggregate status, normalized facts, and human
renderings may be regenerated.  Regeneration still charges code,
configuration, compute, operations, and TCB.

### MAY FORGET

This supplement establishes no new unconditional `MAY FORGET` item.
Information that never crossed a declared boundary is not persisted history;
that does not license deletion of a byte accepted inside an exact-replay pack.

## Mandatory attack ledger

- **DELETE:** remove one selected raw or inventory byte while retaining its
  hash; exact replay distinguishes the histories.
- **MERGE:** concatenate separately named sources; `a|bc` collides with
  `ab|c`.
- **DERIVE / RECOMPUTE:** hashes and indexes rebuild from exact targets; target
  bytes do not rebuild from their hashes.
- **COLLIDE:** reuse `(trial_id, ordinal, offset, length, hash)` across streams
  or runs; the selector no longer determines one range.
- **FUTURE:** admit simultaneous timeout and storage pressure; R0.1B gives no
  unique terminal status.
- **EXTERNALIZE:** a blob service, private decoder, deduplicator, or out-of-band
  replay index retains the missing state and must be included in operations
  and TCB.
- **REALIZE:** inline inventory violates the bound; an unstated shared object
  silently changes the boundary contract.
- **COGNITION:** an operator otherwise must guess pack ownership, ordinal
  namespace, partial-stream identity, and status precedence.
- **TCB:** framing, pack ownership, shared-object validation, indexing, and
  bound enforcement are nonzero mechanisms wherever implemented.

## Unaffected unknowns

These defects do not establish apparatus correctness, participant cognition,
power-loss durability, cold recovery, physical capture or delivery, complete
runtime/OS provenance, or unlike physical realizations.  Those remain
`UNKNOWN` or `UNSUPPORTED`.
