# Counterexamples sought

## C1 — multiplicity collision

- World A: one delivery of bytes `p`.
- World B: two deliveries of bytes `p`.
- Required later behavior: an idempotency investigation must distinguish one delivery from a duplicate.
- Expected collision: a set keyed only by content hash.

## C2 — origin collision

- World A: bytes `p` acquired from the authenticated payment channel.
- World B: bytes `p` loaded from an unauthenticated local replay.
- Required later behavior: the first may become evidence for provider behavior; the second may not.
- Expected collision: payload without acquisition transcript.

## C3 — parse normalization collision

- World A: signed bytes `{"a":1}`.
- World B: signed bytes `{ "a": 1 }`.
- Required later behavior: signatures and forensic reconstruction differ.
- Expected collision: parsed map-only storage.

## C4 — duplicate-field collision

- World A: `{"status":"pending","status":"paid"}`.
- World B: `{"status":"paid"}`.
- Required later behavior: a later security audit diagnoses ambiguous producer behavior only in A.
- Expected collision: conventional object parsing with last-key-wins.

## C5 — absent/empty collision

- World A: no acquisition context artifact was retained.
- World B: a zero-length context artifact was retained.
- Required later behavior: a future context format assigns a defined meaning to its empty document.
- Expected collision: null/empty conflation.

## Non-counterexample boundary

Two worlds differing only in an unmeasured physical fact cannot justify a representation primitive: they delivered the same acquisition transcript. The honest answer is that the fact was not observed.

