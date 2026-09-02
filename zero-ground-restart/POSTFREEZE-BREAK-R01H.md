# POSTFREEZE BREAK R0.1H

## Scope, provenance, and verdict convention

This is a fresh, ontology-independent audit of only the frozen seed
HISTORY-SEED-R01H.md.

- Required SHA-256:
  4954ed2a9612ea8a7e95041b689b549a1b9636e2d7457bf003d7d2c056958658
- Observed SHA-256 before reading:
  4954ed2a9612ea8a7e95041b689b549a1b9636e2d7457bf003d7d2c056958658
- Hash verdict: PASS
- No implementation, manifest, prior candidate, audit, archive, other repository
  file, or version-control history was inspected.
- The frozen seed was not edited.

Verdicts below mean:

- PASS: follows from the frozen mathematical clauses without an additional
  semantic choice, or is independently verified arithmetic.
- FAIL: a minimized counterexample or mutually inconsistent clauses exist.
- UNKNOWN: the text does not choose enough semantics, or the claim requires an
  unrealized or unobserved experiment.

## Method

I reconstructed the model from the boundary alphabet upward, independently
folded all words of length zero through two, and checked the resulting
continuation coordinates and pair arithmetic. I then performed a symbolic
one-crash bisimulation check, tried to make every oracle input single-valued,
minimized collisions by prehistory length and future-message count, audited the
gap arithmetic including both phases of ATTEMPT, and read each empirical attack
as an obligation rather than as evidence.

The principal methods were:

1. exhaustive finite folding of the 157 prehistory words;
2. direct distinguishability by the exact EXPLAIN reply;
3. same-coordinate induction over remaining depth, request phase, and crash
   budget;
4. adversarial construction of equal observable prefixes with unlike hidden
   residuals;
5. separate accounting of nominal schedules and padded selector executions;
6. an ambiguity audit of controller observation, adaptive scheduler identity,
   STOP termination, must propositions, and canonical serialization.

## Reconstructed contract

At a failure-free cut, the continuation behavior is intended to be summarized
by the derived coordinate (O,P,G), with 3 observation values, 3 program values,
and 2 engine values. A future controller submits at most three ordinary
messages, then performs FIN/STOPPED. A scheduler chooses no crash or one crash
at a nominal crossing gap. If a request input crossed but its reply did not,
recovery may select the residual immediately before the request or the residual
after applying its transition. The selector is hidden from the observable
trace. May is the deduplicated set of complete traces over all valid selector
branches; must is intended to contain fixed propositions true on all branches.

At clean cuts, this is a finite Mealy-style quotient. During recovery, however,
the text also requires a hidden residual/phase coordinate. That coordinate is
not derivable from the observable exact prefix after SELECT has been erased.
This distinction is the main break below.

## Primary break: exact observable history is not a total residual key

### Minimized program witness

Start at H(). Send AUTHOR ID and crash in the sole gap after its C crossing and
before its R crossing. After DOWN and READY, the exact observable prefix is the
same under both selections:

    C:"AUTHOR ID\n"
    L:DOWN
    L:READY

There has been no completed AUTHOR reply. The definition of P as a fold over
completed configuration commands therefore gives P=EMPTY. The recovery rule,
however, requires the new branch to continue with P=ID. Retrying AUTHOR ID
separates the two required residuals:

    old -> R:"OK AUTHOR ID\n"
    new -> R:"ERR ACTIVE\n"

This is minimal in future-message count. One state-changing message is needed
to create the collision; with no later ordinary message, coordinate-independent
STOP cannot expose it; one later message suffices.

The two-result may behavior is intentional nondeterminism and is not itself a
contradiction. The contradiction is the simultaneous claim that P is a
single-valued function of the exact completed observable prefix. The displayed
prefix has one value under that definition and two required continuation
residuals under crash recovery.

### The same collision on the other axes

Observation:

    H(); C:"OBSERVE 0\n"; crash before its reply; DOWN; READY

The old branch has O=U and the new branch must have O=0. A subsequent EXPLAIN
must say respectively:

    R:"WHY O=U P=EMPTY E=E0 V=NONE\n"
    R:"WHY O=0 P=EMPTY E=E0 V=NONE\n"

Yet the prefix contains no completed observation reply, so the stated O(prefix)
definition returns U on both.

Evolution:

    H(); C:"EVOLVE\n"; crash before its reply; DOWN; READY

The old branch has E0 and the new branch must have E1. Retrying EVOLVE must say:

    old -> R:"OK ENGINE E1\n"
    new -> R:"OK ENGINE E1 ALREADY\n"

Yet no successful evolution completion crossed, so the stated G(prefix)
definition returns E0 on both.

Consequences:

- “O, P, and G are mathematical functions of the exact completed prefix”:
  FAIL for legal post-crash prefixes.
- “These history functions cover every legal prefix”: FAIL.
- The operational old/new relation can still be total if its state is changed
  to (observable prefix, selected residual, pending phase), or equivalently if
  selector history is retained in the semantic state even though projected out
  of public traces.
- The clean-cut quotient and its arithmetic are not refuted by this collision.
  They concern failure-free prehistory cuts, where no request is pending.

## Other minimized collisions and ambiguities

### Intended same-class collision

The smallest distinct prehistory collision is H() versus H(RI). The latter has
the exact prehistory crossings

    C:"REPLACE ID\n"
    R:"ERR EMPTY\n"

but both cuts have (U,EMPTY,E0). Their empty-future suffix is FIN/STOPPED, and,
under the repaired residual semantics, every supported future is identical.
This is an intended quotient merge, not a contradiction.

The smallest unequal-coordinate pair that collides under an empty future is
H() versus H(O0). Both produce only the coordinate-independent STOP suffix.
EXPLAIN separates them in one ordinary message. Thus “no empty separator” and
“one message suffices” are genuinely minimal at clean cuts.

### STOP-after-terminal ambiguity

With H(), zero ordinary future messages, and the scheduled gap after STOPPED,
the text admits two readings:

    C:FIN
    R:"STOPPED\n"

or

    C:FIN
    R:"STOPPED\n"
    L:DOWN
    L:READY

The schedule count explicitly includes the gap after the last crossing, and
the crash rules discuss a crash after STOPPED. But a trace is called complete
once the controller has terminated and the FIN obligation has completed. The
text does not say whether the scheduled post-terminal lifecycle crossings
belong to that complete suffix. This changes exact May traces and the READY
must verdict. It does not change the syntactic number of named gap schedules.

The between-FIN-and-STOPPED trace is unambiguous and correct:

    C:FIN
    L:DOWN
    L:READY
    R:"STOPPED\n"

### Adaptive scheduler identity ambiguity

For adaptive controllers there need not be one common nominal crossing
sequence on two histories. For example, let the first request be EXPLAIN; send
ATTEMPT next only if the reply says P=EMPTY, and otherwise FIN. A scheduler
described as “crash after the A of the second request” is valid from H() but has
no such gap from H(AI).

The equivalence quantifier uses the same symbol S on both histories but does
not choose among:

- a static ordinal in each run's independently generated nominal trace;
- a request/phase predicate that may be absent on one branch;
- an adaptive scheduler policy that chooses no crash when its target is absent;
- comparison only over schedules valid on both sides.

Those choices yield different quantified domains. Therefore the claimed
equivalence relation is not fully defined for adaptive controllers as written.
Once a common scheduler-policy semantics is supplied, same-coordinate
bisimulation is straightforward.

### Controller observation ambiguity

A is sent to an independent capture peer, while the legal controller may choose
from the “entire observed suffix.” It is not stated whether the client receives
capture-peer observations. This matters after a crash between A and R: a
capture-aware controller can avoid retrying because it saw A; a client-only
controller cannot use A unless another channel is introduced. The fixed retry
witness is valid because that controller ignores A, but the claimed complete
adaptive controller domain is ambiguous.

The later algorithm mentions deterministic adaptive controllers, while the
legal-controller definition does not explicitly exclude randomized or
nondeterministic controllers. This is another domain choice, although it does
not threaten the clean deterministic quotient.

### Must ambiguity and lack of independent force

The fixed must vocabulary is mostly imposed as an oracle invariant. Under a
conditional reading (“if recovery occurs, it reaches READY”), all six
propositions are true for every valid oracle case and Must adds no partitioning
power beyond May. Under an occurrence reading, “recovery reaches READY” is
false or inapplicable on a no-crash run. The seed does not specify vacuous truth
or an inapplicable value.

In addition, “every recovery residual is an old/new alternative” is an internal
claim not recoverable from the deduplicated public trace set. Two internal
choices can serialize to the same trace. Must can be evaluated only if the
harness retains a branch-to-trace relation in addition to the stated set.

Thus reflexivity would follow from equality once May and Must are functions,
but the current Must function is not uniquely defined.

### Canonical minimization is not yet canonical

The proposed ordering has the right categories but is not a complete
reproducible serialization:

- |F| is undefined for a branching controller with paths of different lengths;
- a scheduler gap can be absent or have a different phase on adaptive branches;
- tag byte values, integer encoding, byte-length encoding, and exact history
  encoding are unspecified;
- observed-block and complete controller/scheduler serialization grammars are
  unspecified;
- branch order says how to order children, but not the complete tree grammar.

Accordingly, the one-message minimality theorem for EXPLAIN passes, while the
claim of a complete bytewise canonical witness order fails. Two fresh
canonicalizers can lawfully emit different “canonical” witnesses.

## Independent quotient and pair arithmetic

The clean-cut fold gives exactly these grouped counts:

- (U,EMPTY,E0): 1 + 7 + 51 = 59.
- (0,EMPTY,E0) and (1,EMPTY,E0): 1 + 16 = 17 each.
- (U,ID,E0), (U,NOT,E0), and (U,EMPTY,E1): 1 + 15 = 16 each.
- The eight reachable two-axis combinations listed in the seed: 2 each.

Therefore:

    59 + 2*17 + 3*16 + 8*2 = 157

and the independently obtained class-size multiset is:

    {59,17,17,16,16,16,2,2,2,2,2,2,2,2}

The pair arithmetic also checks:

    C(157,2) = 12,246
    C(59,2) + 2*C(17,2) + 3*C(16,2) + 8*C(2,2)
      = 1,711 + 272 + 360 + 8
      = 2,351
    12,246 - 2,351 = 9,895

EXPLAIN includes O, P, G, and the value derived from O and P, so it separates
every two different clean-cut coordinates. The empty future exposes none of
them. This establishes one-message minimal separation at the model level
without establishing the incomplete canonical byte ordering.

## Schedule and selector arithmetic

For a fixed word with n messages and t ATTEMPT occurrences, the nominal
crossing and schedule formulas are correct:

    crossings = 2n + t + 2
    gaps = 2n + t + 3
    schedules including no-crash = 2n + t + 4

Independent aggregation gives:

| n | Words | T occurrences | Word/schedule cases |
|---:|---:|---:|---:|
| 0 | 1 | 0 | 4 |
| 1 | 12 | 1 | 73 |
| 2 | 144 | 24 | 1,176 |
| 3 | 1,728 | 432 | 17,712 |
| Total | 1,885 | 457 | 18,965 |

Thus:

    157 * 18,965 = 2,977,505

That is a count of syntactic linear history/word/schedule cases, not executions
or unique traces.

### Padded old/new count: FAIL

The seed obtains its padded number by adding one extra selector run per future
message:

    total future-message occurrences
      = 1*12 + 2*144 + 3*1,728
      = 5,484
    18,965 + 5,484 = 24,449
    157 * 24,449 = 3,838,493

That arithmetic is correct for the narrower rule “one padded selector slot per
request.” It is not correct for the stated crash semantics plus the statement
that every collapsing selector slot is exercised.

Every non-T request has one in-flight crash gap, C-to-R. Every T has two:
C-to-A and A-to-R. Section 3.3 applies old/new whenever C crossed and R did
not; T's alternatives collapse, but the padding expressly includes collapsing
slots. The aggregate number of extra in-flight gaps contributed by T is the
already reported 457 T occurrences. Therefore exhaustive per-gap padding is:

    in-flight gap slots = 5,484 + 457 = 5,941
    padded cases per prehistory = 18,965 + 5,941 = 24,906
    padded cases across 157 prehistories
      = 157 * 24,906
      = 3,910,242

The reported value is short by:

    457 * 157 = 71,749

If the intended selector exists at only one distinguished commit barrier per
request, that barrier must be specified and Section 3.3 must stop assigning an
old/new choice to the other in-flight T gap. Under that repair, 3,838,493 is a
valid deliberately padded plan, but it is not the exhaustive per-gap plan
currently described.

The separate 2,304 symbolic-configuration number is UNKNOWN as a conservative
bound. The listed sixteen phases omit explicit stopped/selector/recovering
phases, and no transition-system encoding proves that those can be eliminated
without losing an observable DOWN/READY boundary or branch association.

## Claim audit

| Subject | Verdict | Fresh result |
|---|---|---|
| Twelve-message alphabet and 157 clean cuts | PASS | Closed finite enumeration is exact. |
| Failure-free O/P/G fold and reply table | PASS | It is single-valued at clean and failure-free prefixes. |
| O/P/G cover every legal prefix | FAIL | The minimized post-crash collisions above require two residuals for one exact observable prefix. |
| Behavioral oracle totality | FAIL | Literal prefix functions conflict with old/new recovery; adaptive S and post-terminal completion also lack unique semantics. |
| Meta-oracle total classifier | UNKNOWN | No syntax for an arbitrary “description” or deterministic UNSUPPORTED reason precedence is defined. |
| May as an outcome set | UNKNOWN | The union/dedup idea is sound, but its exact scheduler and controller domains are not fixed. |
| Must as a subset of six propositions | UNKNOWN | Vacuity/inapplicability and internal branch association are undefined; under one natural reading it is constant. |
| Equivalence is an equivalence relation | UNKNOWN | Equality would be reflexive, symmetric, and transitive after functions and a common C,S domain exist; that domain is incomplete now. |
| Same-coordinate crash bisimulation | UNKNOWN | It passes a symbolic induction under the selected-residual repair, but is not a theorem of the inconsistent literal oracle. |
| Different coordinates separated by X | PASS | Exact X bytes injectively expose all three coordinates. |
| No empty-future separation | PASS | Defined STOP behavior is coordinate-independent. |
| Author crash may set | FAIL | It has exactly two traces under Section 3.3, but only the old value under the literal completed-prefix P function; the seed requires both rules. |
| Failure-free evolution/current identity | PASS | E0 to E1 and idempotent E1 replies are coherent. |
| Interrupted evolution selection | FAIL | The new E1 residual contradicts G defined only by completed successful evolutions. |
| Action-attempt retry crossing counts | PASS | At the precise C-A and A-R gaps the stated one- and two-A traces follow; receiver effects remain outside the claim. |
| FIN-to-STOP crash obligation | PASS | The explicit witness follows the special STOP rule. |
| Crash after STOPPED trace | UNKNOWN | It is counted but its lifecycle suffix inclusion is unspecified. |
| Canonical one-message separator length | PASS | Zero cannot expose a coordinate and X does in one. |
| Complete canonical witness order | FAIL | Essential controller, scheduler, and byte serialization details are missing. |
| Fourteen clean-cut quotient classes | PASS | Independent folding reproduces all sizes. |
| Same/unequal pair totals | PASS | Independent combinatorics gives 2,351 and 9,895. |
| Linear schedule totals | PASS | 18,965 and 2,977,505 follow from the stipulated gap count. |
| Padded selector total | FAIL | Per-gap padding gives 3,910,242, not 3,838,493. |
| 2,304 conservative symbolic bound | UNKNOWN | Phase sufficiency is not demonstrated. |
| Exact-history interpreter theorem | UNKNOWN | It is valid only if Encode is explicitly injective; no encoding is supplied. It is outside the supported language either way. |
| Boundary need to distinguish unequal cut classes | PASS | X supplies a direct behavioral lower bound, with no implication about storage location or bytes. |
| Same-class distinctions behaviorally irrelevant | UNKNOWN | Conditional pass under the repaired common-scheduler semantics; no unconditional result under the literal text. |
| Reply/action bytes may be rebuilt | PASS | At a clean request boundary they derive from residual, request, and frozen byte table; recovery additionally needs phase. |
| Physical absence, durability, media, privacy, authority | UNKNOWN | Correctly unsupported; no physical conclusion follows. |
| Externalized token candidate conforms | UNKNOWN | Authentication, authority, and source availability are outside the model. |
| J, Q, and H realizations | UNKNOWN | They are unbuilt obligations, not evidence. |
| Human/cognitive factoring | FAIL | A fresh reader cannot reproduce one exact oracle/canonicalizer without choosing the ambiguities enumerated here. Actual hidden human state remains UNKNOWN. |
| TCB perturbation | UNKNOWN | No runtime, OS, transport, serializer, compiler, cache, hook, peer, oracle, canonicalizer, or build experiment exists. |

## Required attack battery status

These statuses do not turn unexecuted implementation attacks into model passes.

| Attack | Verdict | Result |
|---|---|---|
| DELETE | UNKNOWN | There is no implemented responsibility to remove or cold-start. |
| MERGE | UNKNOWN | Symbolically, X rejects every cross-coordinate merge; no realization was forced to merge labels. |
| DERIVE | UNKNOWN | The byte table supports the derivability claim, but no target bytes were deleted and rebuilt. |
| RECOMPUTE | UNKNOWN | No replay/table realization or measured recovery machinery exists. |
| COLLIDE | FAIL | If exact observable history is used as the residual key, the AUTHOR, OBSERVE, and EVOLVE prefixes above collide while requiring distinguishable continuations. Adding selected residual state repairs it. |
| FUTURE | UNKNOWN | The repaired finite model supports induction through depth three, but exact exhaustive refinement is blocked by scheduler, controller-observation, Must, and STOP ambiguities. |
| EXTERNALIZE | UNKNOWN | No dependency was moved and severed; the token proposal is unsupported. |
| REALIZE | UNKNOWN | Neither unlike family nor the independent harness exists. |
| COGNITION | FAIL | The frozen text alone does not determine one post-crash state function, adaptive scheduler domain, Must evaluator, or canonical serializer. |
| TCB | UNKNOWN | Nothing was enumerated or perturbed empirically. |

## Prediction-by-prediction verdicts

| # | Verdict | Reason |
|---:|---|---|
| 1 | PASS | Exactly 1 + 12 + 144 = 157 distinct pre-cut histories follow from retained request crossings. |
| 2 | PASS | Independent clean-cut folding gives fourteen classes and the stated multiset. |
| 3 | PASS | The class multiset gives exactly 2,351 same-class and 9,895 unequal unordered pairs. |
| 4 | PASS | X exposes O, P, and G in one failure-free reply; an empty future exposes none. |
| 5 | UNKNOWN | Same-coordinate bisimulation works after adding selected residual/phase state and a common scheduler policy, but the literal oracle and quantified S domain are not well-defined. |
| 6 | FAIL | Section 3.3 gives the stated two traces, while P(prefix) over completed commands gives only EMPTY after the interrupted first AUTHOR. Both cannot be the total oracle simultaneously. |
| 7 | PASS | A crash specifically after A and before R leaves the first A in the trace; the specified retry emits a second A, with no receiver-effect inference. |
| 8 | PASS | The linear syntactic schedule arithmetic is exactly 18,965 and 2,977,505. |
| 9 | FAIL | Exercising both branches at every in-flight crash gap requires 3,910,242 slots; 3,838,493 omits the second T gap. |
| 10 | UNKNOWN | J, Q, and H do not exist. If “conform” is defined as matching H, the statement is circular; if it means conforming independently to this text, the ambiguities permit mismatch. |
| 11 | PASS | Defined software-boundary tests cannot establish any of the expressly unsupported physical, privacy, authority, or downstream-effect properties. |

## Bottom line

The clean, failure-free cut quotient is strong: fourteen classes, the class
sizes, pair counts, universal one-message X separator, action crossing example,
and linear schedule arithmetic all survive fresh reconstruction.

The seed is not yet a total exact-history oracle. Erasing SELECT creates legal
observable-prefix collisions whose continuations differ, directly contradicting
the claim that O, P, and G are functions of every exact completed prefix. The
smallest repair is to make selected residual and pending phase explicit semantic
oracle state while keeping them hidden from public trace projection. Exact
adaptive scheduler semantics, capture-peer visibility, Must vacuity, terminal
crash completion, and canonical serialization also need freezing. Finally, the
padded selector prediction must either change to 3,910,242 or explicitly adopt
one selector barrier per request and remove old/new padding at T's other
in-flight gap.
