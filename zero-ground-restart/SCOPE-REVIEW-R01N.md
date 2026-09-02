# ZERO GROUND R0.1N — byte-gated scope review

Status: **FIRST MILESTONE FAIL / NOT ACHIEVED**

This is a scope and promotion audit of the committed R0.1N bundle. It does
not repair the candidate, select a representation, propose an architecture,
or turn executable agreement into physical or subject evidence.

## 0. Byte gates and process provenance

The review began with no-edit SHA-256 gates. All six supplied identities
matched before semantic conclusions were drawn:

| admitted artifact | verified SHA-256 |
|---|---|
| `HISTORY-SEED-R01N.md` | `10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7` |
| `POSTFREEZE-BREAK-R01N.md` | `f00a9841cc9baaa349ff9300f85a8b6a68293e91af560452cf7c2d463bd9773a` |
| `r01n_history_audit.py` | `afb21585f1b9523f16f6fb4d3d647eadac5c461d30de8cda92f19ecd40f18f49` |
| `EXPERIMENT-RESULT-R01N.md` | `c02d41b50c2a700d93ccfaf4f0807c18ac6e2897296763db24a566e5f1df4c41` |
| `PERSISTENCE-COLLISION-LEDGER-R01N.md` | `04dcc1d1206807c6e90fb4f1d906431047b3b9a857a3ea49a53f4735157cd7fd` |
| `ARCHIVE-REPLAY-R01N.md` | `732893924525a58416401a783da64dd55bfb4db737e88921447ba4fd85bbbc81` |

The first pass read only those six artifacts and modified nothing. This file
is being materialized afterward under an explicit request; none of the six
inputs is changed. The reviewer is different from the clean candidate builder
but is not memory-clean and is not a hidden-suite breaker. Hash and repository
chronology establish bytes and ordering, not private cognition, authorship
independence, or physical correctness. This report is not committed here.

## 1. C01 — fixed roots and mechanisms are outside the history quotient

The correct separation is already stated in
`PERSISTENCE-COLLISION-LEDGER-R01N.md:24-36`, `:119-137`, `:243-277`, and
`:467-504`:

- quotient-derived information is, at most, the exact occurrence sequence
  under the conditional raw-audit antecedent;
- the C01/P01 specification, direction convention, decoder selection,
  canonical ULEB rules, capture grammar, and E01 rules are fixed external
  specification and TCB machinery; and
- a containing byte-string extent or EOF is a representation/container
  mechanism, not another C01 history fact.

`ARCHIVE-REPLAY-R01N.md:325-330` mixes those categories by placing the outer
extent, actual nondeterministic or physical results, and governing
specification under a `MUST SURVIVE` heading. The integrated verdict must not
repeat that promotion. Specification and extent remain charged total-system
responsibilities, but no current pair of permitted histories makes their
fixed identity quotient-derived state.

R0.1N instantiates no model, clock, random source, service, or human producer
as a separate semantic occurrence. If nondeterministically selected bytes do
cross, those bytes are already occurrences covered by exact-sequence
preservation. Producer provenance or causal meaning is not additionally
forced unless its own bytes cross. The general warning at
`HISTORY-SEED-R01N.md:174` must not become a separately evidenced persistence
category.

## 2. C02 — normalize F02 as wording and externalization, not collision

`r01n_history_audit.py:328-338` establishes:

```text
encode(e) || encode(e) = encode(e || e)
```

for the one-occurrence empty-payload history `e`. It does **not** establish
`encode(h1) = encode(h2)` for two different histories. Equality of finite byte
strings already includes their extent, and P01's decoder explicitly repeats
until the supplied input end (`HISTORY-SEED-R01N.md:107-118`). With that extent
supplied, canonical parsing is injective.

F02 therefore has two exact consequences:

1. it falsifies the history-level descriptions “one self-delimiting history
   word” and “self-delimiting candidate representation” at
   `HISTORY-SEED-R01N.md:207` and `:738`; and
2. it exposes a required container-extent/EOF mechanism, as correctly bounded
   by `PERSISTENCE-COLLISION-LEDGER-R01N.md:262-277` and
   `ARCHIVE-REPLAY-R01N.md:160-163`.

It is not a P01 encoder collision and is not an independent candidate
functionality failure once a finite byte-string value with extent is supplied.
The committed `6 PASS / 3 FAIL / 11 UNKNOWN` remains the exact runner output;
an integrated semantic verdict must label F02 as a wording/externalization
finding and charge the containing extent rather than count it as a third P01
failure.

## 3. C03 — the quotient and persistence classes are conditional

The unconditional identity-quotient wording at
`HISTORY-SEED-R01N.md:96-100`, `:738`, and `:746-749` exceeds the frozen
contract. Typed requests and responses must themselves become occurrences,
but their bytes, directions, capture order, and snapshot-resolution timing are
not fixed. The executable `LENGTH` function also omits the snapshot parameter;
`r01n_history_audit.py:294-322` shows that its `(0,1)` result on `()` and
`((0,empty),)` is not produced by one fixed snapshot-bearing request before
capture.

The correct result is the conditional lower bound in
`PERSISTENCE-COLLISION-LEDGER-R01N.md:127-193`. If one fixed future semantics
provides:

- one common snapshot-bearing request for both histories;
- exact request/response serialization, directions, capture order, and
  snapshot timing; and
- total byte-exact extent and indexed observations on their declared domains,

then unequal finite histories are distinguishable and enough information to
reconstruct the exact ordered occurrence sequence is `MUST SURVIVE`. Count,
offsets, and named deterministic folds may rebuild from that sequence plus an
identified specification. Transient nonhistory machinery may forget only
after its exposure window closes.

Without those antecedents, complete captured-traffic equivalence,
execution-level `MUST SURVIVE`, and operational `MAY FORGET` remain UNKNOWN.
F01 is a contract/harness correspondence failure, not a P01 collision and not
a refutation of the conditional identity argument.

## 4. C04 — exact scope of the finite-state impossibility theorem

The pigeonhole construction at `ARCHIVE-REPLAY-R01N.md:105-152` is valid only
under all five antecedents below:

1. The closed total realization, including every persistent side service,
   carrier, organization-held state, and restart influence, has a fixed finite
   number `Q_R` of durably distinguishable restart states.
2. Every finite `CROSS(d,p)` in the stated domain is mandatory and succeeds;
   capacity-dependent filtering is not silently treated as an “unaccepted”
   continuation.
3. No refusal, exhaustion, reset, loss, or resource-failure outcome is
   permitted in place of the required append and later response.
4. After restart, one total common byte-exact observation must recover and
   distinguish the accepted occurrence under completed capture/snapshot
   semantics.
5. The caller or environment does not retain the payload as an undeclared
   survivor; if a service, person, or medium can influence the later answer,
   its state is inside the closed total realization counted by `Q_R`.

Under those antecedents, define

```text
m_R = min { m >= 0 : 2 * 256^m > Q_R }.
```

There are more one-occurrence `(direction,payload)` histories of length `m_R`
than durable states. Pigeonhole therefore forces either a merged durable state
or refusal/nonresponse on a mandatory input. This is a parametric theorem for
closed finite-state realizations. It is not empirical physical evidence, not a
P01 codec collision, and not a fixed numeric witness until `Q_R` is supplied.

If “accepted continuation” permits an arbitrary capacity rejection, C01 does
not define that refusal's boundary behavior and is underdefined instead. The
E01 extension is further conditional on completing a program grammar that can
actually express the advertised unbounded integers, literals, lists, traces,
and buffers. No exact E01 program witness exists while that grammar is absent.

Accordingly the unqualified physical-FAIL formulations at
`ARCHIVE-REPLAY-R01N.md:139`, `:152`, `:247`, `:284`, `:318`, and `:350` must
be carried into feasibility only as this conditional all-domain
finite-state-impossibility result. Physical durability, recovery, and unlike
realizations remain UNKNOWN.

## 5. C05 — packed coding and the thirteen-history corpus stay bounded

The packed-code check in `r01n_history_audit.py:175-220` establishes only the
recorded bounded facts over 742 corpus instances:

- bounded round-trip and injectivity;
- 10,594 aggregate bytes versus P01's 12,566;
- strictly smaller encoding for 740 instances; and
- no larger encoding among the tested instances.

`PERSISTENCE-COLLISION-LEDGER-R01N.md:283-300` correctly withholds total
dominance. The result is a storage counterexample to any literal P01-byte
minimality claim in that domain. It does not select the packed code, prove
full-domain behavior, compare corruption/runtime/cognition/TCB jointly, or
establish an architecture. The frozen candidate had already withheld
byte-minimality.

The construction at `r01n_history_audit.py:221-290` and
`PERSISTENCE-COLLISION-LEDGER-R01N.md:343-369` produces a 13-history union that
retains a witness for the 21 listed public attacks and reproduces the supplied
redundant-bundle fixed point. Thirteen is an upper bound. It is not a minimum
corpus, a complete quotient test, a hidden suite, coverage of unlisted
representations, or total-system adequacy.

## 6. C06 — minimization, freshness, and evidence qualifications

The following scope restrictions are mandatory:

- The frozen minimizer is exact only under its disclosed bounded history,
  representation, pair, and future order. Equal-metric bucket ties retain
  enumeration order; no global history/program/crash/physical minimum follows
  (`POSTFREEZE-BREAK-R01N.md:108-151` and
  `PERSISTENCE-COLLISION-LEDGER-R01N.md:54-70`).
- Empty history plus one `LENGTH(0)` request is minimal only in the leading
  missing-capability coordinates `(initial occurrences, future requests) =
  (0,1)`. Exact argument-byte and lexical minimality cannot be computed because
  the request serializer is the missing mechanism. The broader “smallest
  decisive witness” wording at `POSTFREEZE-BREAK-R01N.md:153-164` and `:358`
  must be qualified accordingly.
- The finite-state family has no fixed numerical smallest witness without a
  particular `Q_R`. `ARCHIVE-REPLAY-R01N.md:286-289` is correct only for fixed
  finite witnesses already in scope, not for the parametric family.
- The candidate's 157-history “fresh” corpus and expected result coexist in
  one file (`HISTORY-SEED-R01N.md:715-733`). Section order is not a precommit or
  independent hidden reveal. The breaker discloses this at
  `POSTFREEZE-BREAK-R01N.md:237-239`.
- The breaker-generated 343 histories are report-contained, mechanically
  reproducible post-freeze evidence (`POSTFREEZE-BREAK-R01N.md:263-321`), but
  they are not part of the pinned audit stdout, not a pristine hidden suite,
  and not independent subject conformance.
- The candidate, alternate encoder path, expected assertions, and later audit
  share semantic code and authority. Reproduction proves bounded consistency,
  not independent correctness. The archive correctly limits this at
  `ARCHIVE-REPLAY-R01N.md:169-171`.

All artifact hashes matched, and the recorded runner counts and bounded byte
counts are internally consistent. Process chronology is useful evidence of
freeze order, but it does not prove private file isolation or cognitive
independence.

## 7. P01 collision disposition

No P01 collision is established.

- Given a valid finite byte-string value with supplied extent, shortest ULEB
  parsing recovers one unique occurrence sequence.
- F02 compares concatenated containers with one extended history; it does not
  equate two P01 encodings of different histories.
- `0000 -> 0100` is a valid-to-valid corruption transition, not an encoding
  collision.
- The finite-state theorem concerns a closed realization's durable states or
  refusal, not mathematical P01 byte equality.
- The digest, sorting, deduplication, normalization, deletion, and other
  supplied mutants do collide; none is P01.

The bounded searches add negative evidence, while the parsing argument gives
mathematical injectivity only for already-supplied finite byte strings with an
identified codec and extent. Neither result establishes a complete executable
C01 quotient or a physical carrier.

## 8. Final scope verdict

```text
FIRST MILESTONE: FAIL / NOT ACHIEVED.
```

The defensible positive result is conditional and narrow: with a fixed exact
capture/snapshot grammar and a supplied finite byte-string extent, the raw
audit observations force exact ordered occurrence-sequence information, and
P01 is mathematically injective for that abstract domain.

The frozen total system still fails because boundary request/response capture
and required E01/RUN behavior are incomplete. F02 is an external-extent and
wording finding, not a P01 collision. Literal all-domain conformance is
impossible for a closed finite-state realization only under the five stated
antecedents. The packed and 13-history results remain bounded falsification
facts.

The complete captured-traffic quotient, global minimum, subject conformance,
physical durability/recovery, integrity, human cognition/authoring,
query/navigation service levels, TCB closure, evolution, portability, and
materially unlike realizations remain UNKNOWN or unsupported. No surviving
distinction selects a field, record, log, graph, storage medium, program,
layer, package, or architecture.
