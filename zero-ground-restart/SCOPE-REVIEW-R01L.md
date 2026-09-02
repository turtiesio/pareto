# ZERO GROUND R0.1L — Independent scope correction

Status: **the R0.1L first milestone remains FAIL / NOT ACHIEVED.**

This artifact corrects promotions in the first persistence ledger and
feasibility audit. It does not alter the frozen candidate, breaker report,
ledger, experiment, result, or archive replay. It does not propose a
representation or architecture.

## 0. Provenance and evidence gate

The scope reviewer was a different agent from the clean builder. It was asked
after the feasibility audit had been committed to compare the complete R0.1L
bundle, identify overclaims and smaller witnesses, and make no edits. It was
not memory-clean and is not a hidden-suite breaker. Its review is an audit of
recorded bytes, not evidence of private cognitive isolation.

| artifact reviewed | SHA-256 |
|---|---|
| `HISTORY-SEED-R01L.md` | `0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb` |
| `POSTFREEZE-BREAK-R01L.md` | `0744f495f0a229715e1f088c99d96bbbe0b409aaef522e54fb2a8fc516461b9a` |
| `PERSISTENCE-COLLISION-LEDGER-R01L.md` | `43fb010a3d100ceec54ed3388636c89252635b14b59398b4f4a8680e9652ba30` |
| `r01l_history_experiment.py` | `ce064d9bdf0cd3f80c395d4772837fb2b427d231b2cdd5a8273a300f9e98757a` |
| `EXPERIMENT-RESULT-R01L.md` | `22b6c24990902573b8c6f50755c06fefc3182745d31bf57ada9f306aa6406238` |
| `ARCHIVE-REPLAY-R01L.md` | `217efe1524c1ffab09e8b7a2b2e6412833a8562e64abd444e279fc9e0a0ed64a` |
| pre-correction `FEASIBILITY-AUDIT-R01L.md` | `cf84f94ec8a8a9d5b79abaf1abbb10117e610aec25cb82e35f09e63b92cddeda` |

The root auditor reproduced the two executable observations below by
deterministically extracting the candidate's Python block. The extracted
bytes had the already-recorded SHA-256
`a7fe34a112919b319739fc79dc37f8c9c0ed036a4e73ae2a33081df55a3e4d84`.
This is still the candidate's oracle, not an independent subject.

## 1. C01 — archive/D1 attribution

The pre-correction feasibility audit says that the corrected archive replay
declared D1 unrun or absent. It did not. The archive says only that no R0.1L
experiment-result work was read or used. Its text is silent about D1.

The temporal distinction is instead:

- the frozen seed declared D1 but supplied no retained D1 run evidence;
- the frozen breaker therefore described D1 as not executed in the evidence
  then available to it;
- the later pinned falsifier/result executed D1; and
- the archive replay did not consume that later result and made no D1 claim.

This is an attribution correction. It does not change any D1 count or verdict.

## 2. C02 — the contract is not a quotient-derived history item

The first ledger's R3 row compares the same survivor bytes under ZG-1 swap
semantics and an identity interpretation that ZG-1 forbids. That is not a pair
of permitted ZG-1 histories. It therefore cannot witness a collision in the
ZG-1 quotient of histories.

Correct disposition:

- the exact ZG-1 grammar, semantic root, transition relation, capacity rule,
  response grammar, and version identity are an identified external
  reconstruction specification and TCB binding;
- deleting or changing that authority makes reconstruction undefined or
  changes the contract, so its availability and exact binding remain charged
  to the total system;
- it is not, on current evidence, a history-derived **MUST SURVIVE**
  distinction alongside R1 and R2; and
- if a future contract admits version selection, contract replacement, or
  conversion as boundary occurrences, histories may force version/binding
  distinctions. ZG-1 admits no such evolution boundary, so that persistence
  classification is **UNKNOWN**, not imported from the cross-interpreter
  example.

The correction does not make the specification free. All positive
**MAY REBUILD** verdicts remain conditional on the exact specification being
identified, available, correctly bound, and correctly executed. Parser,
selector, replay, formatter, version/deployment binding, and verification stay
in the TCB.

## 3. C03 — D1 reconstruction did not test corrupt projections

R05 reconstructs the accepted projection of each valid enumerated D1 history
and compares the result with that history's oracle state. It reports no
failure over those valid inputs.

It does not inject a corrupt projection, a nonaccepted effect body, a wrong
actor reconstruction, a malformed relation, or a damaged persisted encoding.
Fail-closed checks exist in inspected candidate/runner code, but their behavior
was not exercised by R05. Therefore:

- valid D1 actor reconstruction: bounded **PASS**;
- corrupt/nonaccepted projection rejection in this run: **UNKNOWN**; and
- subject decoding, damaged persistence, and physical recovery: **UNKNOWN**.

## 4. C04 — the stated commutation family was not exhaustive

The first ledger's condition for forgetting relative chronology was too
narrow if read as an exact or exhaustive predicate. A smaller positive merge
exists directly from the semantic root:

```text
h1 = AA00, AA01
h2 = AA01, AA00
```

The extracted oracle produced, for both histories:

```text
O 0003 21 0000
O 0003 21 0000
```

The canonical states and ORACLE bytes were identical; their common ORACLE
SHA-256 was
`e25e4eb4ac84029c51fc11617a54c98fd999b5f8bbe62da2803222b924eece17`.
Because ZG-1 is deterministic from canonical state, every common future has
identical output. Thus the relative order of these two distinct-key first
actions is **MAY FORGET**, even though both snapshot the same branch and the
ledger's written predicate would reject the merge.

This is not a PROJECTED3 collision: PROJECTED3 preserves the two orders as
different encodings. It is evidence that PROJECTED3 and a global event order
retain at least one redundant distinction.

The corrected claim is deliberately weaker:

- the individual same-lineage, fork-placement, and action-placement witnesses
  already recorded force those particular causal distinctions;
- any relative order may be forgotten only after an exact all-future
  equivalence or commutation proof for that family;
- distinct-key first actions from the unchanged semantic root are one proved
  forgettable family; and
- no complete commutation relation, causal quotient, canonical relation
  encoding, or globally minimum partition has been established.

## 5. C05 — smaller ORACLE history, unchanged effect threshold

The experiment actually initializes the semantic root and then applies 9,362
`WA0x` requests. It does not execute a preceding `B`; only its report label
described one. Direct reproduction gave:

```text
history prefix: none
9,361 accepted WA0x effects: nested item length 65,535; ORACLE encodes
9,362 accepted WA0x effects: nested item length 65,542; ORACLE raises ValueError
```

The smaller history is therefore `WA0x` repeated 9,362 times from the semantic
root. The accepted-effect threshold is unchanged and no future request is
needed. The boot-prefixed form is also a valid witness, but it is not smallest
by request count. Likewise, the candidate's B-prefixed collision witnesses are
minima only inside its forced-B bounded corpus unless separately proved under
another metric.

No earlier accepted-effect-count ORACLE overflow and no PROJECTED3 collision
was found by the scope review.

## 6. Corrected persistence statement

The evidence supports only this non-architectural statement:

### MUST SURVIVE

- Accepted changing occurrences and their operation, target, final
  argument/key, and multiplicity, where the recorded collision pairs force
  those distinctions.
- The particular causal placements/orderings forced by the recorded
  same-lineage, fork-snapshot, explanation, and first-action-snapshot
  witnesses.
- Complete evidence artifacts conditionally, when a bounded empirical PASS is
  retained as a claim.

These are local responsibility witnesses. They do not prove that R1 plus an
already-known exact R2 relation is the global quotient or smallest persistent
representation.

### MAY REBUILD

- Actor spelling and the enumerated logical branch/action/query/explanation
  views from the forced effect/placement distinctions plus the exact,
  identified ZG-1 reconstruction specification, under the mathematical
  induction.
- The finite D signature from its exact sources and ordered future list.

These do not establish acceptable runtime, availability, a physical decoder,
or fail-closed behavior on corruption.

### MAY FORGET

- Completed identity traffic, old outputs, and redundant framing under the
  residual ZG-1 contract and its identity-transition induction.
- Relative chronology only for a family with an exact all-future proof. The
  distinct-key first-action pair above is one such family.

### Not promoted

The exact contract is a fixed parameter of the current equivalence relation,
not a demonstrated history item. Index/navigation artifacts, canonical
partial-order bytes, the complete quotient, the exhaustive commutation
relation, contract evolution, subject conformance, response progress, physical
persistence/recovery, operations, human cognition, TCB closure, portability,
and unlike physical realizations remain **UNKNOWN** or unsupported.

## 7. Mandatory attacks and complexity transfer

| attack | corrected result | where the complexity is now |
|---|---|---|
| DELETE / MERGE / COLLIDE | R1 and local R2 losses retain exact witnesses. The R3 comparison is rejected as out-of-contract. The action-order pair is an exact successful merge, not a collision. | equivalence boundary, witness minimization, causal/commutation proof |
| DERIVE / RECOMPUTE | Valid logical views derive only with an exact external ZG-1 specification. Corrupt-input rejection and physical reacquisition were not exercised. | specification custody, replay, validation, runtime, recovery |
| FUTURE | Recorded Q/E/A futures force local distinctions; identical canonical states prove all-future equality for the action-order merge. Cross-version, viewer, search, progress, and physical futures are absent. | contract expansion and evolution authority |
| EXTERNALIZE | Removing R3 from the history quotient leaves it charged as external specification/TCB machinery. | deployment binding, parser/selector/replay/formatter/verifier |
| REALIZE | No subject, medium, failure run, second runtime, or unlike realization exists. | physical implementation and independent evidence roots |
| COGNITION | The narrower relation can increase explanation/navigation burden; no human task evidence exists. | renderers, navigation, reviewers, measurement |
| TCB | Exact rules and their binding are not persistent history bits, but all rebuild claims trust them. | code/configuration custody, version selection, evidence extraction |

After the apparent simplification, complexity has moved into specification
custody, exact equivalence/commutation proof, causal reconstruction, validation,
and deployment binding. It has not disappeared.

## 8. Final scope verdict

**FIRST MILESTONE: FAIL / NOT ACHIEVED.**

R0.1L supplies useful local MUST/MAY witnesses and a bounded reconstruction
result. It does not supply a complete quotient, an exact global persistence
partition, a total ORACLE, a subject, a physical realization, a human result,
or two materially unlike implementations. The scope corrections narrow the
surviving result; they do not repair the frozen candidate.
