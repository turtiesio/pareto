# Independent finite-mathematics audit of FBH-12/2/3

## Scope and integrity

This audit was performed against the frozen file `HISTORY-SEED-R01H.md` with SHA-256

```text
4954ed2a9612ea8a7e95041b689b549a1b9636e2d7457bf003d7d2c056958658
```

It checks finite arithmetic and the conditions needed for the claimed quotient. It does not repair the frozen seed, implement either proposed realization, or supply physical evidence.

## Results in one view

| Claim | Verdict | Reason |
|---|---|---|
| 157 pre-cut histories | PASS | `1 + 12 + 144 = 157` and independent enumeration agrees. |
| Fourteen cut classes and stated size multiset | PASS | Independent transition folding gives the exact stated table and multiset. |
| 2,351 same-class and 9,895 unequal unordered pairs | PASS | Recomputed from the class sizes and `C(157,2) = 12,246`. |
| One-message `X` separates every unequal coordinate; empty future does not | PASS | `X` prints `O`, `P`, and `G`; FIN/STOP behavior is coordinate-independent. This is length minimal, not a verified canonical serialization. |
| Same-coordinate histories survive all depth-three adaptive/crash futures | CONDITIONAL | The state-transition induction works, but the seed does not completely identify an adaptive scheduler or the internal data over which `Must` is quantified. |
| Exact author crash/retry may set | PASS | Old leaves `P=EMPTY`, so retry succeeds; new leaves `P=ID`, so retry returns `ERR ACTIVE`; neither interrupted occurrence receives a reply. |
| Two visible attempts after an `A`-then-crash retry | PASS | The first crossed `A` cannot be retracted and the retry crosses a second `A`; no receiver effect follows. |
| 18,965 linear word/schedule cases and 2,977,505 history cases | PASS | The per-word no-crash-plus-gap formula is arithmetically correct. |
| 3,838,493 padded old/new slots | **FAIL** | A `T` request has two interrupted-request gaps, but the formula adds only one selector slot for it. |
| J and Q agree with H | UNKNOWN | These are conditional proposed obligations; this audit has no J, Q, or H evidence. |
| Software tests do not prove the excluded physical/security properties | PASS | This is a correct non-inference, not evidence about those properties. |

One false finite prediction is enough to reject the frozen prediction set as written. It does not by itself refute the fourteen-class cut quotient.

## Recomputed cut quotient

Folding all words of length zero through two from `(U,EMPTY,E0)` gives these class sizes:

```text
(U,EMPTY,E0)  59
(0,EMPTY,E0)  17
(1,EMPTY,E0)  17
(U,ID,E0)     16
(U,NOT,E0)    16
(U,EMPTY,E1)  16
(0,ID,E0)      2
(0,NOT,E0)     2
(0,EMPTY,E1)   2
(1,ID,E0)      2
(1,NOT,E0)     2
(1,EMPTY,E1)   2
(U,ID,E1)      2
(U,NOT,E1)     2
```

They sum to 157. The same-class calculation is

```text
C(59,2) + 2*C(17,2) + 3*C(16,2) + 8*C(2,2)
= 1711 + 272 + 360 + 8
= 2351.
```

Therefore `12,246 - 2,351 = 9,895` distinct unordered pairs are between classes.

Under the abstract oracle, `(O,P,G)` is Markov-sufficient: every failure-free output is a function of that coordinate and the next request; every transition is likewise a function of them; old/new recovery chooses the pre- or post-transition coordinate; action bytes depend only on the same coordinate; FIN behavior is coordinate-independent. This supports induction over future depth once controllers and schedulers are given precise common semantics.

`X` is injective in `(O,P,G)` because its exact reply contains all three tokens. The no-message continuation only executes FIN/STOP and therefore cannot distinguish two cut coordinates. Thus one message is the minimum separator length for every unequal pair.

This establishes fixed-pair separator length. It does not establish the seed's claimed *canonical* witness order, because that order is not completely serialized.

## Linear schedule arithmetic

For a word with `n` messages and `t` occurrences of `T`, the nominal trace has `2n+t+2` crossings. Its gaps number `2n+t+3`; adding no-crash gives `2n+t+4` schedules. Aggregation is:

| `n` | words | total `T` occurrences | schedules |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 4 |
| 1 | 12 | 1 | 73 |
| 2 | 144 | 24 | 1,176 |
| 3 | 1,728 | 432 | 17,712 |
| **total** | **1,885** | **457** | **18,965** |

Multiplying the total once by 157 gives 2,977,505. This count includes the gap after STOPPED. Its arithmetic is exact, although the terminal-gap trace should be made explicit in a total executable oracle.

## Minimized padded-selector counterexample

The shortest counterexample is the one-message word `[T]`. Its nominal crossings are

```text
C:T, A:TRY, R:OK, C:FIN, R:STOPPED.
```

It has six gaps plus no-crash, hence seven base schedules. Both of these are interrupted-request gaps under Section 3.3:

1. after `C:T` and before `A:TRY`;
2. after `A:TRY` and before `R:OK`.

Forcing old and new at every applicable gap requires one additional execution at each of those two gaps, even though `T` changes no residual state and the alternatives later deduplicate. The padded count for `[T]` is therefore nine, while `3n+t+4` gives eight.

Across all words, the correct formula for the stated “every selector slot, even when collapsing” interpretation is

```text
3n + 2t + 4
```

because a non-`T` message has one interval after its request crossing and before its reply, while `T` has two. The corrected aggregates are:

| `n` | corrected padded slots |
|---:|---:|
| 0 | 4 |
| 1 | 86 |
| 2 | 1,488 |
| 3 | 23,328 |
| **total per prehistory** | **24,906** |

Across 157 prehistories this is 3,910,242, which is 71,749 more than the frozen prediction. If the intended plan deliberately exercises only one selected interrupted phase per request, the smaller number can be retained only by narrowing the prose; it is not the count described by the current seed.

## Definitions that block an unconditional adaptive proof

### Scheduler identity

For a linear word, a gap ordinal is exact. For an adaptive controller, different observed replies can select continuations with different crossing shapes—especially when one branch chooses `T` and another chooses a two-crossing request. The seed does not say whether `S` is:

- a numeric gap in the failure-free trace;
- a request/phase label;
- a strategy over observed prefixes; or
- a separate path-specific schedule.

It also does not state how the same `S` is applied when two compared histories induce different controller branches. Until that is fixed, `forall C,S` has no single operational domain and prediction 5 cannot receive an unconditional executable verdict.

### Must carrier and truth conditions

`May` is a deduplicated set of observable traces. The proposition “every recovery residual is one of the oracle's old/new alternatives” refers to hidden residuals that are not members of those traces. Deduplication can erase two distinct hidden residuals when the controller immediately closes. Consequently, `Must` cannot be reconstructed solely from the declared `May` value.

The oracle can still define `Must`, but it must retain an explicit internal outcome carrier or separately define proposition truth over selector assignments. It must also say whether recovery propositions are vacuously true in no-crash schedules. Without this, exact set equality and reflexivity are stated more clearly than in the preceding round but are not yet fully executable.

### Terminal crash trace

The schedule arithmetic includes the gap after `R:STOPPED`. The seed says this crash cannot produce another client reply, but it does not print the complete observable trace for the case. If every crash emits `L:DOWN` and recovery emits `L:READY`, the natural result is STOPPED followed by DOWN and READY; if completion ends observation at STOPPED, the schedule is observationally erased. The oracle should freeze one reading.

None of these ambiguities supplies a counterexample to state-coordinate sufficiency under the intended reading. They do prevent a claim that the adaptive crash oracle is already an exact executable total function.

## Canonical minimization is not yet completely encoded

Section 5.1 names the pieces of a total order, but it does not assign:

- crossing tag and direction byte values;
- integer widths, byte order, or variable-length rules for lengths and cardinalities;
- an exact encoding of typed FIN and lifecycle crossings;
- a complete adaptive-controller serialization;
- a complete scheduler serialization; or
- the meaning of `|H|` and `|F|` in the distribution tuple when messages, crossings, and bytes differ.

Different conforming implementers can therefore choose different bytewise tie-breaks. The length-one `X` existence/minimality result survives, but “canonical” minimized witnesses remain UNKNOWN until these encodings are frozen.

## Persistence-verdict consequence

The finite calculation conditionally supports a fourteen-way cut responsibility, not a particular field, atom, byte layout, or log. It also conditionally permits exact distinctions between histories in one class to be forgotten when some other surviving representation preserves the continuation class.

It does not yet calculate the quotient over all interrupted and terminal phases. In particular, the seed mentions pending completion, old/new authority, and FIN responsibility without enumerating their future-equivalence classes or minimizing each with a collision. Therefore this round cannot yet make the requested exhaustive `MUST SURVIVE / MAY REBUILD / MAY FORGET` statement for the total between-execution state.

