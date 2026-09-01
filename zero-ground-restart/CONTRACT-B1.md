# C0 executable-contract amendment B1

This file resolves executable ambiguities found after `FROZEN-B0.md` was
frozen. It does not amend the frozen file or broaden its claims. Where B1
chooses among meanings that B0 did not uniquely determine, results are labeled
`B1`; the alternative remains unsupported rather than silently rejected.

## Exact choices

- The frozen action descriptor is exactly
  `(source, authored-bit, interpretation-label, interpreted-bit)`. The two
  interpretation-table bits are not copied into an action descriptor.
- `P`, `R`, and a legal `ACK` are silent. Every other legal inbound frame owes
  exactly one outbound frame.
- An `ACK(key)` is legal only while that same key is pending, after its `DO`
  frame has crossed. Missing-key, wrong-key, and already-done acknowledgements
  are outside the declared next-crossing domain and change no state.
- Client requests and responses cross the `client` port. `DO` and `ACK` cross
  the `action` port. Let `A` be the common frozen set of proposed inbound
  frames. For each legal crossing history `h`, the next-crossing domain is
  `D(h) = {a in A | h;a is a legal crossing history}`. A proposal is a
  conformance-test choice, not itself a system interaction. The proof oracle
  records `enabled` when a proposal belongs to `D(h)` and `disabled` otherwise;
  these are domain-membership markers, not emitted frames or a second boundary
  channel. Only a member of `D(h)` crosses and joins history. Exact client-port
  traces, action-port traces, and equality of `D(h)` are compared. The selector
  enforcing `D` is part of the TCB rather than free boundary behavior.
- The protocol is serial. While an output is owed, no inbound frame is a legal
  next boundary crossing. `resume` is a scheduler operation, not a boundary
  frame. It crosses the one owed output, or crosses nothing when quiescent.
  Restarts are also not boundary frames and do not alter state or observations.
- Future comparison uses **union-domain proof enumeration**: every proposal
  from `A` is checked on both sides. The proof marker is `disabled` when the
  proposal is outside a side's domain; no operational attempt, response, or
  boundary event is thereby asserted. Equivalence first requires equal domains,
  so differing enabled continuations cannot be hidden by intersecting only the
  two sides' jointly enabled futures.
- At every cut, the proof context may choose `resume` or query whether an
  inbound frame is in the next-crossing domain. While output is owed every such
  frame is outside that domain; the proof query does not silently resume first.
  The bounded enumerator includes zero, one, or two domain proposals and every
  normalized placement of `resume` before, between, and after them. Continuing
  after a common `disabled` marker is proof-level normalization: the rejected
  proposal was a non-event and can be deleted. A first unequal marker already
  separates the histories. Consecutive quiescent resumes are observationally
  idempotent and have one representative. For this deterministic oracle,
  enumerating these words covers adaptive contexts of the same bounds: every
  adaptive branch has one determined path.
- Bounded residual signatures use at most two inbound proposals. Separately, a
  stable right congruence is computed over the complete finite-domain,
  quiescent turn machine and its one-output cut states. This is a finite-domain
  strengthening, not evidence about fresh values or omitted capabilities.
- The raw-trace replay oracle is in `c0_oracle.py`. Quotient construction and
  candidates import it, but the oracle imports no candidate or quotient code.
- `UNKNOWN` is reserved for operations outside the executable B1 grammar. No
  pair containing `UNKNOWN` is placed in an equivalence class and no survival
  or forgettability claim is derived from it.
- Witness ordering calls the tuple produced by `Observation.flattened()` the
  "first-divergence" coordinate. That tuple contains all proof-level domain
  markers first, then client-port frames, then action-port frames. Its index is
  a stable tie-break only; it is explicitly **not** a temporal position in an
  interleaved boundary trace.

## Frozen frame bytes and canonical order

The executable self-delimiting spelling is UTF-8 text
`direction:port:kind` followed, when arguments exist, by `(`, comma-separated
arguments, and `)`. The only direction strings are `in` and `out`; the only port
strings are `client` and `action`; C0 atoms contain none of `:(),;`. A boundary
history joins frame spellings with `;`; the empty history is the empty byte
string. Parsing any other byte string is outside B1 and returns `UNKNOWN`, not
`disabled`.

Canonical representatives minimize boundary-crossing count first and then the
tuple of these exact UTF-8 frame spellings in ordinary bytewise lexical order.
Class ordinals are ordered by the same representative key.

The SHA-256 string stored by the executable candidates is only a same-runtime
artifact-mismatch guard for this experiment. It is not evidence of general
portability, durable specification discovery, or cryptographic collision
proof. The current representation is 64 UTF-8 hexadecimal characters; 32 bytes
is only its theoretical binary packing.

## Explicitly unsupported

B1 does not decide malformed byte framing, new labels/bits/keys/rules,
concurrency, input reordering, time, audit, authorization, resource deadlines,
capture failure, an unacknowledged output at a physical device boundary, or
physical effects beyond crossing `DO`. These require new contract choices and
fresh experiments.
