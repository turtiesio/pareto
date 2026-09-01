# Fresh breaker attack on frozen B0

The breaker read only `FROZEN-B0.md`, after its hash was recorded, and did not
read the archive. No candidate encoding collision was yet demonstrated, but B0
failed as an executable specification in eight places.

## Genuine C0 blockers

1. The oracle did not fully define descriptor bytes, output ports, ACK silence
   and repeat legality, `resume`, disabled attempts, or outbound framing.
2. Quantifying only over jointly legal contexts can hide enabledness. Contexts
   must come from a common universe/union and return `disabled` on the side
   where a step is illegal. Minimal witness: empty history versus `O?`, followed
   by `P(a,0)`.
3. Four-inbound base histories plus two-inbound futures leave the class universe
   during transitions. The executable experiment needs a total-history limit,
   a transition-closed universe, or explicitly horizon-indexed semantics.
4. `UNKNOWN` is not an equivalence value: unequal-to-itself is non-reflexive,
   while equal-to-all is unsound. Any affected quotient is `UNVERIFIED`.
5. One shared oracle for signatures, generated table, and replay creates a
   common-mode failure. Independent transitions, hand goldens, metamorphic
   checks, and mutation detection are required.
6. C0 restart cuts are after completed boundary crossings. Torn persistence,
   delivery/bookkeeping races, and capture failures remain unsupported.
7. Per-instance specification digest necessity is not a C0 history witness
   while C0 fixes one specification. It is a total-system/TCB responsibility
   unless artifact mismatch is admitted as an environment variation.
8. Canonical representative ordering is undefined until exact frame bytes and
   their ordering are specification-bound.

## Smaller witnesses than the provisional table

- Latent rule behavior: `R(u,0,1)` versus `R(u,0,0)`, then `P(a,1);Q`.
- Key association: pending `A(k)` versus pending `A(l)`, then `S(k)`; no ACK is
  needed.
- Owed `O/Q/X` are equal with no content because each owes `EMPTY`; an owed-kind
  witness must first author content.
- Latest order: `P(a,0);P(a,1)` versus its reverse, then `O`.

## Frozen hidden goldens for B1

`?` marks a cut after inbound crossing and before its owed output.

| ID | Histories / continuation | Required relation |
|---|---|---|
| G01 | `O?` / completed `O;EMPTY`; restart, `resume` | emit once / emit nothing |
| G02 | `R(u,0,1)` / `R(u,0,0)`; `P(a,1);Q;resume` | `VAL(1)` / `VAL(0)` |
| G03 | `R(u,0,1)` / `R(v,0,1)`; `P(a,0);X;resume` | WHY labels `u` / `v` |
| G04 | pending `A(k)` captured from `P(a,0)`, then latest `P(a,1)` / pending captured from `P(a,1)`; `S(k)` | frozen descriptors differ |
| G05 | pending action captured from `P(a,0)`, latest changed; repeat `A(k)` | original `DO`, not recomputed descriptor |
| G06 | pending / same history plus `ACK(k)`; `S(k)` | `PENDING` / `DONE` |
| G07 | pending under `k` / pending under `l`; `S(k)` | `PENDING` / `ABSENT` |
| G08 | `A(k)?` / `S(k)?` with no content; restart, `resume` | `NO_DATA` / `ABSENT` |
| G09 | `P(a,1);X?`; restart, `resume` | exact `WHY(a,1,d,1)` |

Required equivalences/deletions:

| ID | Histories | Required relation |
|---|---|---|
| E01 | empty-state `O?`, `Q?`, `X?` | equivalent: all owe `EMPTY` |
| E02 | `P(a,0)` plus any completed O/Q turn | equivalent to `P(a,0)` |
| E03 | `P(a,0);P(b,1)` / `P(b,1)` | equivalent |
| E04 | overwritten rule then `R(v,0,1)` / only `R(v,0,1)` | equivalent |
| E05 | `P(a,0);R(v,0,1)` / reverse | equivalent |
| E06 | empty / completed no-content `A(k);NO_DATA` | equivalent |
| E07 | earlier `NO_DATA` before a later first real action / that action alone | equivalent |
| E08 | one / two completed retries while pending | equivalent |
| E09 | pending state plus completed `S(k)` / pending state | equivalent |

For every computed equal-class pair and every next operation in the union of
enabled operations, B1 must compare enabledness, immediate output, and successor
class. This includes outbound/resume/restart operations.

For each of `EMPTY`, `RAW`, `VAL`, `WHY`, `NO_DATA`, `DO`, `ALREADY`, `ABSENT`,
`PENDING`, and `DONE`, the restart matrix must show: output once after one or
many pre-output restarts; no duplicate after the output crossed; a new inbound
is disabled while output is owed; and a completed read-only output leaves no
durable distinction.

## Fresh-domain adapters actually inside C0

- A calibration console renames `P/R/Q/X` and exercises latent mappings and
  labeled explanations.
- A dispatch boundary renames `A/ACK/S` and exercises frozen decisions, keys,
  retries, and cuts without claiming a physical effect beyond `DO`.
- A recovery terminal renames interrupted `O/Q/X` and exercises owed-versus-
  crossed persistence.

Erasure, confidentiality, authority, time, concurrency, malformed bytes,
capture failures, physical exactly-once effects, split-class evolution, human
budgets, and resource deadlines are outside C0. They remain unsupported, not
passing tests.

## B2 semantic correction after this attack

The attack's word `disabled` is not a newly invented response frame. Final B1
uses it only as the proof oracle's marker that a proposed frame is outside a
history's declared next-crossing domain. A rejected proposal is a non-event and
does not cross the boundary. Equivalence compares the two domains before their
enabled successors, which preserves the union-versus-intersection attack
without smuggling a second, unrecorded observation channel. A realization that
returns an actual refusal message would require a new history grammar and fresh
collision experiment.
