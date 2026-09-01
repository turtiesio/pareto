# Independent formal audit of the B1/B2 experiment

Date: 2026-09-01

This audit checks what the executable experiment establishes. It neither treats
the implementation as an architecture nor extends any result beyond the frozen
finite B1 contract and the stated history/future bounds.

## Boundary semantics

Let `A` be B1's frozen proposal alphabet and `L` its prefix-closed language of
actual boundary crossings. At history `h`, define the next-crossing domain

```text
D(h) = {a in A | h;a is in L}.
```

The harness values `enabled` and `disabled` are proof markers for membership in
`D(h)`. They are not emitted response frames. A rejected proposal is therefore
not silently omitted from history; it is a conformance-test non-event that never
crossed the boundary. Equivalence requires equal domains and then equal output
and successor behavior on their members. This union-domain comparison prevents
an intersection-only test from hiding different enabled continuations.

If a physical realization instead returns a refusal message, that message is a
crossing. Its attempt/result protocol, intermediate cuts, and any refusal state
must be added to history and re-experimented; the present counts do not apply.

## Exhaustiveness inside the declared bounds

`generate_histories(4)` is exhaustive by induction over legal B1 prefixes. From
a quiescent cut it tries every member of the finite input alphabet and retains
every accepted crossing. From an owed-output cut the only next crossing is the
exact owed output. It retains the cut after every crossing and stops only after
four accepted inbound crossings. This produces 62,528 histories and 1,192 raw
oracle snapshots.

`future_contexts(2)` enumerates zero, one, or two proposals and every normalized
placement of `resume` around them, producing 2,114 proof contexts. Commonly
rejected proposals are non-events and consecutive quiescent resumes are
idempotent, so their redundant repetitions can be normalized away.

For this deterministic oracle, static and adaptive bounded contexts induce the
same partition. If an adaptive strategy separates two histories, take its path
up to the first unequal domain marker or output. Both sides made the same prior
choices, so that finite static prefix is already a separator. Every static word
is conversely an adaptive strategy that ignores observations. This statement is
specific to the declared deterministic, bounded setting.

The executable bounded strategy tree and all 2,114 static observation vectors
agree on the 1,192-class corpus partition. No `UNKNOWN` cell participates in
equivalence.

## Transition closure

A separate finite-domain Mealy refinement closes the complete reachable
quiescent turn machine under all sixteen frozen inputs. Its refinement sequence
is 8,735 classes, then 10,420, then the same 10,420; every reachable quiescent
state is behaviorally distinct in this finite grammar.

An owed-output cut is exactly classified by the pair

```text
(exact owed frame, settled quiescent class after that frame crosses).
```

Only `resume` can advance such a cut; it emits the exact first component and
lands in the second. Conversely, unequal owed frames differ immediately and
unequal settled classes differ after the common owed crossing. This lifting is
therefore exact, not a candidate ontology. It yields 82,584 complete
boundary-phase classes. Exhaustive one-step differential checks establish
right-congruence over this frozen domain.

## All-pair merge certificate

There are 709,836 unordered pairs among the 1,192 corpus classes. For every
pair, the certificate searches all contexts at increasing proposal depth and
selects the first separating depth. Within that depth it minimizes the first
differing `Observation.flattened()` coordinate and then the context token. The
flattened coordinate groups proof-domain markers, client outputs, and action
outputs; it is a deterministic tie-break, not chronological order.

The earliest-separator distribution is:

| Proposal depth | Separated pairs | Pairs still equal afterward |
|---:|---:|---:|
| 0 | 596,382 | 113,454 |
| 1 | 113,306 | 148 |
| 2 | 148 | 0 |

For each class the search retains every corpus history with the minimum number
of crossings: 1,824 histories in total, at most four per class. For each pair it
then exhaustively minimizes Levenshtein distance and lexical history tie-breaks
over those complete minimum-length sets. Thus every proposed merge has an
executed bounded separator and minimized corpus endpoints, not merely unequal
class identifiers. The emitted triangular uint16 context map permits separator
reconstruction; its SHA-256 is a commitment and not the semantic proof.

## Direct deletion verdicts

The ten-coordinate falsification grammar has 1,024 projections and four sound
masks. Its single inclusion-minimal kept set contains eight responsibilities:

```text
current_source, current_bit,
rule_label, rule_on_1,
action_k, action_l,
owed_kind, owed_arguments.
```

Each of the eight direct deletions has a globally minimized collision within
the four-crossing history corpus, two-proposal future grammar, and declared
witness order. This proves a persistence responsibility, not a field or
constructor. The other two coordinates have exhaustive full-universe rebuild
recipes: `rule_on_0` is the B1 constant `0`; `owed_port` is `action` exactly for
`DO`, `client` for every other owed kind, and absent when no output is owed.

Projection irreducibility does not prove minimum program description length or
irreducibility under every possible recoding. The quotient cardinality supplies
an information lower bound; the candidate machinery and total-system costs are
separate.

## Evolution criterion

For an old encoder `E` and new observer `N`, deterministic migration exists on
a supplied domain exactly when `N` is constant on every fiber of `E` there. The
positive executable result covers only `current_b1_observer` on the 62,528
enumerated histories. The negative result is conclusive for its explicit pair:
two histories share the old encoding but have different authored-crossing
counts, so no deterministic function of that encoding can recover the count.

No positive conclusion follows for an unenumerated observer or history domain.
Any contract extension that splits an old equivalence class needs additional
surviving information or must be reported unsupported.

## Remaining proof limits

- The actual target contract is not concretely declared; no B1 name or bit is
  universal.
- Fresh values, malformed frames, concurrency, reordering, time, audit,
  authorization, privacy, physical effects, and resource bounds are outside B1.
- The oracle, generator, candidates, verifier, CPython runtime, and host retain
  common-mode risk despite literal goldens and mutation tests.
- The quotient is the conceptual information minimum for B1 behavior, not a
  least total implementation under the non-scalar cost order.
- Human cognition and unlike physical media remain unmeasured.

