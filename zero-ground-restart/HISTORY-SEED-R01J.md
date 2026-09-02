# FBH-12/2/3-J: one all-cut finite future-history candidate

## 0. Frozen status and claim boundary

This document is the complete R0.1J candidate specification. It is a finite
history/future contract. It is not an implementation, storage ontology,
database design, run report, physical claim, or conformance result.

The authorities for the candidate are, in order:

1. the exact frozen bytes of this document;
2. the finite transition, projection, closure, and encoding algorithms below;
   and
3. a separately retained falsification manifest, if one is later produced.

The SHA-256 of this document is deliberately not embedded in these bytes. A
manifest records that digest only after this document is frozen, avoiding a
self-referential identity.

R0.1J starts with exact histories and asks which histories every permitted
future can distinguish. It selects no record, journal, table, snapshot, cache,
device, or persistence layout. A behavioral lower bound is never promoted to a
physical persistence claim.

The supported semantic capabilities are bounded observation, ID/NOT authoring
and replacement, retirement, query, immediate state explanation, externally
captured action attempt, one E0-to-E1 evolution, current-engine query, at most
one abstract crash/recovery, and exact FIN/STOPPED termination. Authentication,
privacy, physical completion, power-loss durability, and arbitrary evolution
are outside the finite semantic model and remain UNKNOWN rather than passing by
exclusion.

## 1. Exact full histories and observations

### 1.1 Atomic crossings

A full history is an ordered sequence of atomic crossings on five channels:

| Channel | Direction | Crossing |
|---|---|---|
| C | client to service | one request frame, or typed FIN |
| R | service to client | one reply frame, or typed STOPPED |
| A | service to independent capture peer | one action-attempt frame |
| L | lifecycle observer | typed DOWN or READY |
| F | privileged control/evidence boundary | one exact F frame |

C, R, A, and F frames are nonempty ASCII ending in exactly one LF. FIN, STOPPED,
DOWN, and READY are typed crossings with no frame payload. Fragmentation,
tearing, partial crossing, duplication, reordering, and simultaneous crossings
are unsupported.

The complete F frame grammar is:

    CUT REMAINING=3\n
    CRASH GAP=<canonical-decimal>\n
    SELECT old\n
    SELECT new\n
    RESUME ACTIVE O=<O> P=<P> E=<G>\n
    ALLOWANCE <d>\n
    RESUME FIN_PENDING\n
    RESUME TERMINAL\n

Canonical decimal is `0` or a positive base-ten integer with no leading zero.
`O`, `P`, `G`, and `d` use only the finite tokens defined below. F:CUT is
inserted metadata, not a schedulable crossing. F:CRASH and F:SELECT are
privileged controls. F:RESUME and F:ALLOWANCE are oracle-visible consequences
of the exact history; they prescribe behavior, not a service representation.

### 1.2 Observation scopes

The four ordinary viewer projections retain:

| Viewer | Retained suffix crossings |
|---|---|
| CLIENT | C, R, L |
| CAPTURE | A |
| PUBLIC | C, R, A, L |
| SELECTOR | F |

PRIV is a fifth observation scope. It retains the ordered, label-indexed family
of complete full suffixes before projection or deduplication. PRIV is not made
available to the legal client.

The legal client observes CLIENT only. The capture peer observes A only and
sends no information to the client during a run. The scheduler observes PUBLIC
since the designated cut plus the proposed next crossing. The selector and
PRIV scope are inaccessible to the client.

Observations compared at a cut contain only the suffix after that cut. The
exact prefix remains in the declared history corpus and may remain in a
falsification manifest, but it is not replayed to a suffix viewer. Consequently
an already crossed A can distinguish full evidence histories without being
information needed by the post-cut continuation.

## 2. Finite requests, residuals, and ordinary outputs

### 2.1 Request alphabet

The complete nonempty ordinary request alphabet, in rank order, is:

| Rank | Alias | Exact C frame |
|---:|---|---|
| 0 | O0 | `OBSERVE 0\n` |
| 1 | O1 | `OBSERVE 1\n` |
| 2 | AI | `AUTHOR ID\n` |
| 3 | AN | `AUTHOR NOT\n` |
| 4 | RI | `REPLACE ID\n` |
| 5 | RN | `REPLACE NOT\n` |
| 6 | D | `RETIRE\n` |
| 7 | Q | `QUERY\n` |
| 8 | X | `EXPLAIN\n` |
| 9 | T | `ATTEMPT\n` |
| 10 | E | `EVOLVE\n` |
| 11 | K | `CURRENT\n` |

The notation `\n` in a code span denotes one LF byte. Empty input is not FIN.
Arbitrary programs, callbacks, bytecode, search expressions, plugins, and
unknown request versions are unsupported.

### 2.2 Residual transition function

The semantic residual is

    r = (O,P,G)
    O in {U,0,1}
    P in {EMPTY,ID,NOT}
    G in {E0,E1}.

The value function is:

| P | O | V |
|---|---|---|
| EMPTY | any | NONE |
| ID | U | UNKNOWN |
| ID | 0 | DENY |
| ID | 1 | ALLOW |
| NOT | U | UNKNOWN |
| NOT | 0 | ALLOW |
| NOT | 1 | DENY |

For every residual, every ordinary request has a total transition:

- O0 sets O to 0; O1 sets O to 1.
- AI sets EMPTY to ID and otherwise leaves P unchanged.
- AN sets EMPTY to NOT and otherwise leaves P unchanged.
- RI sets nonempty P to ID and leaves EMPTY unchanged.
- RN sets nonempty P to NOT and leaves EMPTY unchanged.
- D sets nonempty P to EMPTY and leaves EMPTY unchanged.
- E sets E0 to E1 and leaves E1 unchanged.
- Q, X, T, and K leave the residual unchanged.

This tuple is a semantic coordinate. It is not a required stored object.

### 2.3 Failure-free transaction completions

After the C frame of a request crosses, its failure-free completion is:

| Request and precondition | Exact completion crossing or crossings |
|---|---|
| O0 | R:`OK OBSERVE 0\n` |
| O1 | R:`OK OBSERVE 1\n` |
| AI with P=EMPTY | R:`OK AUTHOR ID\n` |
| AI otherwise | R:`ERR ACTIVE\n` |
| AN with P=EMPTY | R:`OK AUTHOR NOT\n` |
| AN otherwise | R:`ERR ACTIVE\n` |
| RI with P nonempty | R:`OK REPLACE ID\n` |
| RI otherwise | R:`ERR EMPTY\n` |
| RN with P nonempty | R:`OK REPLACE NOT\n` |
| RN otherwise | R:`ERR EMPTY\n` |
| D with P nonempty | R:`OK RETIRE\n` |
| D otherwise | R:`ERR EMPTY\n` |
| Q | R:`VALUE <V>\n` |
| X | R:`WHY O=<O> P=<P> E=<G> V=<V>\n` |
| T | A:`TRY O=<O> P=<P> E=<G> V=<V>\n`, then R:`OK ATTEMPTED\n` |
| E with G=E0 | R:`OK ENGINE E1\n` |
| E with G=E1 | R:`OK ENGINE E1 ALREADY\n` |
| K | R:`ENGINE <G>\n` |

Substitutions are finite tokens, not literal angle brackets. Every failed
precondition therefore has an exact reply and an identity transition; there is
no phase-dependent undefined ordinary action.

An A crossing means only that the independent capture peer observed those
exact bytes at that atomic boundary. It does not imply receiver execution,
durability, downstream success, external completion, or exactly-once effect.

## 3. Declared cut-history corpus

### 3.1 Clean histories

For each word w of length zero, one, or two over the twelve ranked messages:

1. start at `(U,EMPTY,E0)`;
2. execute w serially and failure-free, completing every reply;
3. append F:`CUT REMAINING=3\n`; and
4. declare the point after F:CUT a clean cut.

There are exactly

    12^0 + 12^1 + 12^2 = 157

distinct clean full histories.

Write `H(w)` for the clean cut produced by word w, and `H()` for the empty
word.

### 3.2 Recovery histories

Starting from any clean cut, choose a failure-free future word u of length zero
through three, then FIN. The nominal crossing stream is the ordinary C/R
crossings, the additional A of each T, typed FIN, typed STOPPED, and the one
terminal END gap after STOPPED. A crash may replace passage through exactly one
gap. F:CUT is not a gap. Recovery itself cannot crash.

At the selected gap append:

    F:CRASH GAP=<g>\n
    L:DOWN

where `g` is the zero-based ordinal of that gap after F:CUT in the realized
nominal stream. The point immediately after DOWN and before SELECT or RESUME is
a recovery cut. No other point is a declared cut.

The exact recovery-prefix corpus is:

| Derived condition at DOWN | Per clean history | Across 157 histories |
|---|---:|---:|
| idle active | 1,885 | 295,945 |
| non-T request pending | 1,727 | 271,139 |
| T pending before A | 157 | 24,649 |
| T pending after A | 157 | 24,649 |
| FIN pending | 1,885 | 295,945 |
| terminal after STOPPED | 1,885 | 295,945 |
| total recovery cuts | 7,696 | 1,208,272 |

Together with the 157 clean cuts, the one comparison domain contains exactly
1,208,429 declared cut histories. The descriptive rows are derived conditions,
not kind tags and not gates on comparison.

Normalizing recovery histories by only the values used by continuation gives
854 conditions:

| Condition family | Count |
|---|---:|
| idle active `(r,d)` | 68 |
| changing pending non-T | 195 |
| no-op pending non-T | 355 |
| T before A | 50 |
| T after A | 50 |
| FIN-pending sources | 68 |
| terminal sources | 68 |

These counts describe inputs to the relation; they do not prejudge which rows
merge.

### 3.3 Cut authority

A cut's exact prefix is its sole encoded authority. Its residual, allowance,
pending request, T stage, crash budget, and recovery condition are derived by
the fold in Sections 2 and 4. None is repeated in the cut encoding. A prefix
that does not fold uniquely to one of Sections 3.1 or 3.2 is not a declared cut
and receives the exact classifier result in Section 10.

## 4. Total continuation semantics

### 4.1 Occurrence, application, reply, and selection

For an ordinary request:

1. occurrence is its C crossing; it captures pre-residual r and
   `post=delta(r,m)` and consumes one allowance unit;
2. semantic application is atomic with its failure-free R completion, or with
   F:SELECT new after interruption;
3. reply completion is its R crossing; and
4. recovery selection exists only when C crossed and R did not.

F:SELECT old resumes pre and applies nothing. F:SELECT new applies post without
inventing an R and resumes post. Identity transitions and failed preconditions
still have two labeled alternatives; their resumed residuals happen to be
equal. A validated R or SELECT new is applied exactly once by the full-history
fold.

### 4.2 Recovery from every derived condition

Recovery is total and exact:

- Idle active:

      F:RESUME ACTIVE O=<O> P=<P> E=<G>\n
      F:ALLOWANCE <d>\n
      L:READY

- Any pending ordinary request, including either T stage, produces an ordered
  two-branch family. OLD is first and NEW second:

      F:SELECT old\n
      F:RESUME ACTIVE O=<pre O> P=<pre P> E=<pre G>\n
      F:ALLOWANCE <d>\n
      L:READY

      F:SELECT new\n
      F:RESUME ACTIVE O=<post O> P=<post P> E=<post G>\n
      F:ALLOWANCE <d>\n
      L:READY

- FIN pending:

      F:RESUME FIN_PENDING\n
      L:READY
      R:STOPPED

- Terminal:

      F:RESUME TERMINAL\n
      L:READY

Only the pending-request condition admits SELECT. SELECT at idle, FIN-pending,
terminal, after an ordinary R, or after STOPPED is not a legal continuation.
An interrupted request emits no later ordinary R. If T's A crossed before the
crash it remains only in the prefix; recovery does not retract or replay it.

After active READY, ordinary execution resumes with the selected residual and
remaining allowance. After FIN-pending recovery, STOPPED closes the run. After
terminal recovery, READY closes lifecycle observation without reopening C or
R.

### 4.3 Allowance and FIN

Every ordinary C occurrence, including a retry, atomically changes `d` to
`d-1`. FIN consumes no ordinary allowance. At d=0 the controller is forced to
choose FIN. FIN is legal at every active idle point and forbids every later C.
Its one completion is typed R:STOPPED, after which no C or R may occur.

A crash before FIN crosses is an idle crash. A crash after FIN and before
STOPPED is FIN-pending. A crash in the terminal END gap after STOPPED is
terminal. Those rules cover every mismatch between intent, FIN occurrence,
and terminal completion.

### 4.4 Phase routing and mismatched actions

One encoded controller and one encoded scheduler are applicable to every
declared cut; legality never depends on a cut kind.

The evaluator first derives the phase from the prefix, then follows this total
router:

| Derived phase | Operation consumed next | Other policy material |
|---|---|---|
| clean active idle | controller chooses a request or FIN; scheduler evaluates its preceding gap | selector material is absent |
| DOWN idle | forced active RESUME/ALLOWANCE/READY, then controller | no selector; scheduler unavailable because crash budget is zero |
| DOWN pending request | both selector labels are enumerated, forced RESUME/ALLOWANCE/READY, then controller | scheduler unavailable |
| DOWN FIN-pending | forced FIN_PENDING recovery and STOPPED | controller, selector, and scheduler are not consulted |
| DOWN terminal | forced TERMINAL recovery and end | controller, selector, and scheduler are not consulted |
| active request pending | its next nominal A or R is proposed to scheduler if the budget remains; otherwise it crosses | controller and selector are not consulted |
| terminal END gap | scheduler is consulted only if the budget remains | controller and selector are not consulted |

An entry not reached on a path is inert, not an error and not a hidden default.
Thus the same total tables remain meaningful when two cuts start in mismatched
phases. Ordinary request/precondition mismatches use the exact ERR or no-op
rules in Section 2. A raw attempt to force CLIENT, SCHEDULER, or SELECTOR outside
the router is not a contract-permitted future and receives
`UNSUPPORTED(PHASE_ACTION)` without adding a crossing. This refusal is fixed;
an implementation may not hang, invent an action, or choose a phase-specific
interpretation.

In particular, `Eval(H,Ctl,Sch)` exists for every declared H and every globally
legal Ctl/Sch pair. A clean/recovery, idle/pending, active/FIN-pending, or
FIN-pending/terminal comparison is never rejected merely because the two sides
consume different policy components first.

## 5. Common finite future grammar

### 5.1 Client controllers

A legal controller acts only at an active idle decision. It observes exactly
the CLIENT suffix since the designated cut and current d. If d is positive it
chooses one of the twelve ordinary messages or FIN. If d is zero it chooses
FIN. It waits for R or post-interruption READY before another decision.

Let D be constructed without referring to controller encodings:

1. seed an exploration frontier with every declared cut;
2. at each active idle node explore every admissible controller action;
3. at every crashable gap explore pass and crash;
4. at every interrupted barrier explore OLD and NEW;
5. apply all forced recovery and terminal crossings;
6. stop after FIN/terminal closure; and
7. record every reached `(d, CLIENT suffix since cut)` at which a controller is
   consulted.

Deduplicate by EncDecisionKey and sort bytewise. This least finite set is D.
It is independent of any particular table, so using D to encode a table is not
circular.

A controller is one action code for every key in D. Entries at d=0 must be FIN.
This contains every deterministic CLIENT-visible adaptive controller within the
finite bound. Random and nondeterministic client controllers are unsupported.

### 5.2 Scheduler policies

At each nominal gap while and only while the crash budget equals one, form:

    (PUBLIC suffix since the designated cut, proposed next crossing or END).

Let G be the sorted unique EncGapKey list encountered by the same policy-free
exploration used for D, but record a key only at a point where the crash budget
is one. After a crash, the scheduler is not invoked and no ignored post-crash
keys enter G. Recovery cuts therefore contribute no scheduler keys of their
own. END occurs only at the terminal gap after STOPPED.

A scheduler is one bit for every key in G: zero passes and one crashes. The
all-zero vector is no-crash. One on the realized key consumes the sole crash
budget; later bits cannot be consulted. A key absent from an adaptive path is
inert on that path. One global vector therefore has exactly one meaning across
all divergent paths and all declared cuts.

### 5.3 Selector alternatives and realization scope

There is at most one selector barrier. Instead of choosing a preferred branch,
the semantic outcome enumerates the complete ordered family OLD then NEW. This
is exact universal coverage of both contract-permitted selector choices; equal
viewer traces may deduplicate only after this family exists.

R0.1J admits one formal semantic realization, `FORMAL`, namely the transition
algorithm in this document. It admits no physical realization. Equivalence
below quantifies every realization admitted by the contract, so its present
realization quantifier contains FORMAL only. Adding a process, device, medium,
or unlike realization requires a new frozen contract and can split classes.
Agreement across physical realizations is UNKNOWN, not a vacuous R0.1J PASS.

The exact numeric sizes of D and G and the counts of their truth tables remain
UNKNOWN until an independent R0.1J enumerator reproduces the closures. Their
finiteness follows from the finite cuts, d in 0..3, one crash, finite frames,
and forced terminal closure.

## 6. Outcomes and the single all-cut relation

### 6.1 Branch families and viewer values

For a declared cut H, controller Ctl, and scheduler Sch, `Family(H,Ctl,Sch)` is
never empty. It contains one complete full suffix if no selector barrier is
reached, or two suffixes ordered OLD then NEW if one is reached. Later adaptive
behavior is evaluated independently within each branch using the same total
Ctl and Sch.

For CLIENT, CAPTURE, PUBLIC, and SELECTOR, `Obs_v` projects each suffix, encodes
the projected trace, deduplicates equal encodings, sorts bytewise, and returns
that exact trace set. `Obs_PRIV` is the encoded ordered full branch family and
does not deduplicate. Branch labels are in their F traces, so old/new
orientation is preserved without a redundant branch field.

This family is the complete finite carrier set for this candidate. R0.1J does
not expose an arbitrary predicate language called MUST. Validation obligations
and applicability are recorded separately as evidence; absence of a carrier is
never presented as an operational guarantee.

### 6.2 One equivalence relation

For any two declared cuts H and H', including clean/recovery and every derived
phase pairing:

    H ==J H'

if and only if, for every legal controller Ctl, every legal scheduler Sch (the
same encoded Ctl and Sch being applied to both cuts), every observation scope

    v in {CLIENT, CAPTURE, PUBLIC, SELECTOR, PRIV},

and every contract-admitted realization rho, the exact encoded values

    Obs_v(rho,H,Ctl,Sch) and Obs_v(rho,H',Ctl,Sch)

are equal.

There is no cut-kind, phase, pending-alias, live-allowance, prefix-length, or
realization-name gate. Different phases may merge only when the total router
and every permitted future yield equal observations. Equality of finite byte
functions makes `==J` reflexive, symmetric, and transitive.

The exact prefix is not concatenated to the compared suffix. Prefix differences
remain evidence facts, not automatic continuation distinctions.

For reporting only, `PUBLIC-image count` means the number of distinct functions
`(Ctl,Sch) -> Obs_PUBLIC`. It is a projection image, not a second contractual
equivalence rule. The contractual quotient always uses all five scopes.

## 7. Finite quotient and separator predictions

All values in this section are falsifiable formal predictions. They are not
implementation evidence.

### 7.1 Clean histories

The 157 clean histories reach exactly fourteen residuals, with class sizes:

    {59,17,17,16,16,16,2,2,2,2,2,2,2,2}.

The unordered clean-pair counts are 2,351 same-class, 9,895 unequal, and
12,246 total. Same-residual histories are predicted congruent under every
R0.1J future.

Every unequal clean pair has:

- a zero-ordinary-C SELECTOR and PRIV separator: choose FIN and crash in the
  initial gap before FIN; idle recovery's F:RESUME exposes all of `(O,P,G)`;
  and
- a one-ordinary-C PUBLIC separator: issue X and pass its completion.

No zero-ordinary-C PUBLIC suffix exposes the residual. Thus X is smallest only
for PUBLIC; it is not the smallest contractual separator.

The smallest distinct intended clean merger is H(empty word) versus H(RI).
RI replies `ERR EMPTY` and leaves `(U,EMPTY,E0)`, and all suffix outcomes are
predicted equal.

### 7.2 Recovery and combined quotients

With no comparison gate, the 854 normalized recovery conditions are predicted
to have:

- 139 distinct PUBLIC outcome functions; and
- 315 contractual all-scope classes.

The 315-class normalized multiplicity histogram is:

| Recovery conditions per class | Classes |
|---:|---:|
| 1 | 263 |
| 8 | 9 |
| 9 | 27 |
| 10 | 14 |
| 68 | 2 |

The arithmetic closes at 315 classes and 854 conditions. T-before-A,
T-after-A, and the matching non-T no-op pending conditions may merge because
the all-cut relation permits the comparison and their future suffixes agree.
Idle recovery does not join them: its one NONE branch differs from their two
label-indexed selector branches in SELECTOR/PRIV.

No clean class joins a recovery class. With FIN chosen and no crash requested,
a recovery suffix has its mandatory READY (and privileged RESUME), whereas a
clean suffix begins with FIN. Therefore the whole 1,208,429-cut domain is
predicted to have:

    PUBLIC-image count = 14 + 139 = 153
    contractual classes = 14 + 315 = 329.

On the normalized 14-clean-coordinate plus 854-recovery-condition domain, the
contractual multiplicity histogram is

    277x1, 9x8, 27x9, 14x10, 2x68.

The full exact-history class-size multiset is UNKNOWN pending independent
R0.1J enumeration.

### 7.3 Minimized behavioral examples

The following use the witness order in Section 8.7.

| ID | Exact pair and continuation | Prediction |
|---|---|---|
| Q1 | clean H() vs H(O0); controller FIN; crash before FIN | zero-ordinary-C SELECTOR/PRIV difference in RESUME |
| Q2 | same pair; controller X then FIN; no crash | one-ordinary-C PUBLIC difference; no zero-C PUBLIC separator |
| Q3 | clean H() vs H(RI) | equal for every future and scope |
| Q4 | pending AI from EMPTY->ID vs pending D from ID->EMPTY, same d; inspect OLD/NEW | PUBLIC endpoint sets equal; SELECTOR/PRIV orientation differs with zero post-cut ordinary C |
| Q5 | completed no-op RI then idle crash vs RI interrupted before R, same r,d | PUBLIC suffixes can agree; NONE versus OLD/NEW separates SELECTOR/PRIV |
| Q6 | T interrupted immediately before A vs immediately after A, same r,d | exact prefixes differ by A; every post-cut outcome agrees |
| Q7 | any clean cut vs any recovery cut; choose FIN and pass | mandatory recovery READY/RESUME separates with zero ordinary C |

Q4 is admissible as a SELECTOR witness; it may not be encoded with CLIENT,
CAPTURE, or PUBLIC merely because a lower viewer code would sort first.

## 8. Exact noncircular canonical bytes

### 8.1 Primitive codec

All integers are unsigned big-endian. U8, U16, and U64 occupy one, two, and
eight bytes. `Block(x)` is U64 byte length followed by x. `Seq(x1..xn)` is U64
count followed by `Block(x1)` through `Block(xn)`. No integer may overflow its
width. No trailing bytes, alternate normalization, or omitted empty block is
allowed.

Crossing tags and payloads are:

| Tag | Crossing | Required payload |
|---:|---|---|
| 1 | C frame | exact nonempty frame bytes |
| 2 | typed C:FIN | empty |
| 3 | R frame | exact nonempty frame bytes other than STOPPED |
| 4 | typed R:STOPPED | empty |
| 5 | A frame | exact nonempty frame bytes |
| 6 | L:DOWN | empty |
| 7 | L:READY | empty |
| 8 | F frame | exact nonempty F bytes |

`EncCrossing = U8(tag) || Block(payload)`. Typed crossings must encode an empty
Block; frame crossings must encode a nonempty Block. `EncTrace` is `Seq` of
EncCrossing values in crossing order. Tags, frame grammars, and contextual
ordering are all validated; a syntactically encoded but context-invalid trace
is not a declared cut.

Residual codes, used only inside algorithms and never repeated in EncCut, are:

    O: U=0, 0=1, 1=2
    P: EMPTY=0, ID=1, NOT=2
    G: E0=0, E1=1.

Action codes are FIN=0 and ordinary aliases rank-plus-one, so O0=1 through
K=12. Scope codes are PUBLIC=0, CLIENT=1, CAPTURE=2, SELECTOR=3, PRIV=4.

### 8.2 Cut encoding

There are no optional or repeated semantic fields:

    EncCut = ASCII `FBH-R01J-CUT`, one zero byte,
             Block(EncTrace(the complete exact prefix through the cut)).

The prefix determines every derived condition. CLEAN, pending aliases,
residuals, allowance, and phases have no bytes in EncCut. Therefore there is no
trace-versus-field authority fork and no presence map to guess.

EncCut is admissible exactly when its trace is one of Section 3's 1,208,429
declared prefixes and every CRASH ordinal equals the ordinal derived from that
trace. Two cuts are oriented by bytewise EncCut order; equality is not a pair.

### 8.3 Decision and gap keys

    EncDecisionKey = U8(d) || Block(EncTrace(CLIENT suffix)).

Every D key has d in 0..3. The suffix starts immediately after the designated
cut and includes all later CLIENT crossings before the decision.

For a scheduler key, next-kind is 0 for a crossing and 1 for END:

    EncGapKey = Block(EncTrace(PUBLIC suffix)) || U8(next-kind)
                || Block(next-payload).

For next-kind 0, next-payload is exactly one EncCrossing. For next-kind 1 it is
empty. Every other kind, an empty crossing payload, or a nonempty END payload
is invalid. G includes exactly the budget-one keys selected in Section 5.2.

### 8.4 Controller and scheduler encodings

Let N be the derived length of sorted D and M the derived length of sorted G.

    EncController = ASCII `FBH-R01J-CTL`, zero byte,
                    U64(N), then exactly N U8 action codes.

The actions correspond positionally to sorted D. Every code is 0..12. Entries
whose key has d=0 must be zero. Wrong N, missing or extra entries, unknown code,
or non-FIN at d=0 is invalid; there is no per-cut partial table.

    EncScheduler = ASCII `FBH-R01J-SCH`, zero byte,
                   U64(M), then exactly ceil(M/8) policy bytes.

Bits are most-significant first in sorted G order. Unused low bits of the last
byte are zero. Wrong M, wrong byte count, or nonzero padding is invalid. Keys
after a crash do not exist in G rather than existing with ignored bits.

### 8.5 Outcome encodings

`EncTraceSet` deduplicates EncTrace values, sorts bytewise, then applies Seq.
For the four projected viewers:

    EncObs_v = EncTraceSet(project_v(each full suffix)).

For PRIV:

    EncObs_PRIV = Seq(EncTrace(full suffix 1), ...).

The formal PRIV sequence contains exactly one suffix without a selector
barrier, or exactly two ordered OLD then NEW when a barrier occurs. In the
two-suffix case, the respective trace contains the exact F:SELECT label; in the
one-suffix case no SELECT occurs. No branch code, residual, allowance, fold,
phase, truth mask, or projection is repeated. Those values are either present
in the trace or derived from cut plus trace. A purported *formal outcome* with
wrong count, order, label, or transition fold is invalid rather than a
competing authority. Section 9 deliberately uses a separate raw observation
encoding so that those same defects remain representable as falsification
evidence.

### 8.6 Separator encoding and admissibility

    EncWitness = ASCII `FBH-R01J-WITNESS`, zero byte,
                 U8(scope),
                 Block(EncCut(left)), Block(EncCut(right)),
                 Block(EncController), Block(EncScheduler).

The left/right order must be the bytewise EncCut order. Scope must be 0..4 and
must actually separate:

    EncObs_scope(left,Ctl,Sch) != EncObs_scope(right,Ctl,Sch).

A nonseparating scope is inadmissible even when another scope separates. There
is no implicit generic viewer and no code chosen solely because it sorts first.
Outcomes are excluded from EncWitness because they are deterministic derived
values. Validation recomputes them from the two cuts, the frozen specification,
and the two total policies.

A PUBLIC witness is a witness whose scope byte is exactly zero. A contractual
witness may use any admissible scope. This makes Q1 beat Q2 contractually while
Q2 remains the smallest PUBLIC witness.

### 8.7 Unique witness order

For a fixed unordered pair, order all admissible witness candidates by this
lexicographic tuple, whose counts are derived over both complete branch
families:

1. maximum number of post-cut ordinary C crossings in any suffix;
2. sum of post-cut ordinary C crossings over all suffixes;
3. maximum total post-cut crossing count in any suffix;
4. sum of total post-cut crossing counts;
5. total number of suffixes in both branch families;
6. total number of F:CRASH crossings in those suffixes;
7. scope code;
8. byte length of EncWitness; and
9. EncWitness bytes.

For a PUBLIC canonical witness first restrict candidates to scope zero. For a
contractual canonical witness use all admissible scopes. The policy universes
are finite and fixed, natural-number prefixes are well-founded, and equal-length
byte strings are totally ordered. Every separable pair therefore has one exact
canonical witness. A pair with no candidate is equivalent under `==J`.

The canonical witness bytes themselves, including the numeric D/G-dependent
table lengths, remain UNKNOWN until an independent enumerator emits them. The
algorithm selecting them is nevertheless complete and noncircular.

### 8.8 Total witness-byte classifier

For any purported EncWitness byte string, dispatch by its witness magic, apply
the following precedence, and return the first result:

1. `UNSUPPORTED(ENCODING)` for bad magic, integer width/overflow, impossible
   Block or Seq length, premature end, or trailing bytes;
2. `UNSUPPORTED(CROSSING)` for an unknown tag, wrong empty/nonempty payload,
   non-ASCII frame, missing/excess LF, or frame outside the exact grammar;
3. `UNSUPPORTED(CUT)` when the trace is not exactly a declared cut prefix, has
   an incorrect CRASH ordinal, or has an invalid semantic fold;
4. `UNSUPPORTED(CONTROLLER)` for wrong D count, action count/code, or d=0 entry;
5. `UNSUPPORTED(SCHEDULER)` for wrong G count, byte count, or padding;
6. `UNSUPPORTED(VIEWER)` for an unknown scope code;
7. `UNSUPPORTED(PAIR_ORDER)` for equal or incorrectly oriented cuts;
8. `UNSUPPORTED(NOT_SEPARATOR)` when the named scope outcomes are equal;
9. `NONCANONICAL(WITNESS)` when a valid separator is not the minimum under
   Section 8.7; and
10. `SUPPORTED` otherwise.

The only top-level binary object types are EncCut, EncController, EncScheduler,
EncWitness, and EncManifest; their magic strings are distinct. An unknown magic
returns `UNSUPPORTED(ENCODING)`. A standalone EncCut applies items 1-3 and then
returns SUPPORTED; a standalone EncController applies items 1 and 4; a
standalone EncScheduler applies items 1 and 5. EncManifest dispatches to the
separate total evidence classifier in Section 9.1. EncObs,
EncEvidenceObservation, and EncEvidenceCase have no top-level magic and are
legal only in their stated derived or nested positions; presented alone they
return `UNSUPPORTED(ENCODING)`. Thus no parser guesses an object type from
optional fields or context.

For a raw operational description rather than one of these encodings, a clean
prehistory deeper than two is `UNSUPPORTED(PREHISTORY_DEPTH)`, an ordinary
frame outside the alphabet is `UNSUPPORTED(REQUEST)`, more than three ordinary
future occurrences is `UNSUPPORTED(ALLOWANCE)`, more than one crash or a
recovery crash is `UNSUPPORTED(CRASH)`, concurrent in-flight clients are
`UNSUPPORTED(CONCURRENCY)`, and an out-of-router role invocation is
`UNSUPPORTED(PHASE_ACTION)`. The precedence among these operational reasons is
PREHISTORY_DEPTH, REQUEST, ALLOWANCE, CRASH, CONCURRENCY, PHASE_ACTION, then
`UNSUPPORTED(SCOPE)` for everything else. Every refusal is terminal for that
description and adds no invented boundary trace.

## 9. Falsification evidence is not persistent necessity

### 9.1 Exact evidence carrier

A falsification manifest is an external research artifact produced after this
specification is frozen. Unlike a formal outcome, it must be able to carry a
wrong, missing, duplicated, malformed, or nonterminating observation.

For evidence only, define:

    EncRawCrossing = U8(observed tag) || Block(raw payload)
    EncRawTrace = Seq(EncRawCrossing values in observed order)
    EncRawFamily = Seq(EncRawTrace values in observed branch order).

Every U8 tag and every finite payload is structurally valid evidence, including
unknown tags, non-ASCII bytes, wrong typed payloads, duplicate traces, and an
empty family. Evidence encoding records what was captured; it does not bless it
as a contractual crossing. Define:

    EncEvidenceObservation = U8(result-kind) || Block(body).

For result-kind 0, body is exactly one EncRawFamily. For result-kind 1, meaning
the declared observation bound expired before a complete family was captured,
body is empty. Other kinds, a nonempty kind-1 body, or trailing bytes are
invalid evidence encoding.

The minimal canonical case encoding is:

    EncEvidenceCase = U8(origin),
                      Block(EncCut),
                      Block(EncController),
                      Block(EncScheduler),
                      Block(EncEvidenceObservation).

`origin=0` means a suffix family generated from the formal transition rules;
`origin=1` means a suffix family captured from a candidate realization. No
other origin is valid.

    EncManifest = ASCII `FBH-R01J-FALSIFY`, zero byte,
                  32 raw bytes SHA256(frozen specification),
                  U64(case count),
                  Block(EncEvidenceCase 1) ...

Cases are sorted bytewise and duplicates are forbidden. Every field is
mandatory. The manifest contains observed/generated suffix evidence; it does
not repeat projections, residuals, phases, quotient labels, or verdicts.
Those are recomputed by an independently identified evaluator. Tool identity,
build identity, runtime, environment, human protocol, and TCB perturbations
belong in a separately signed experiment envelope and are charged in Section
11; they are not guessed into this minimal semantic manifest.

Lift a formal EncObs_PRIV into EncRawFamily by retaining the same tags, payloads,
trace order, and family order. Origin 0 requires result-kind 0. Its raw family
is checked against the formal generator: inequality is
`FAIL(GENERATOR_DISAGREEMENT)`. Equality shows only that those valid traces were
generated consistently. **Generated valid traces are not a verifier test**:
they do not exercise rejection of malformed traces, an independent parser,
negative histories, or a physical implementation.

Origin 1 permits either result kind. A kind-0 raw family is compared bytewise
with the independently generated lifted family. Any wrong count, tag, payload,
order, duplicate, missing crossing, or semantic fold remains well-formed
evidence and yields `FAIL(CONFORMANCE)` rather than a parse rejection. Equality
is evidence only for the captured boundary case and does not establish physical
completion, durability, or TCB closure. Kind 1 yields
`UNKNOWN(OBSERVATION_BOUND)` unless the separately signed experiment envelope
establishes that expiry violated a contract-authorized bound, in which case it
yields `FAIL(NON_TOTAL)`.

The manifest evidence classifier returns the first applicable result in this
order: `UNSUPPORTED(EVIDENCE_ENCODING)` for bad manifest/case structure,
lengths, sorting, duplicate cases, origin, or result-kind;
`UNSUPPORTED(SPEC_DIGEST)` when its 32 bytes are not the SHA-256 of these frozen
bytes; the ordinary CUT, CONTROLLER, or SCHEDULER reason for an invalid input;
`FAIL(GENERATOR_DISAGREEMENT)` for an origin-0 inequality;
`UNKNOWN(OBSERVATION_BOUND)` or `FAIL(NON_TOTAL)` for kind 1 as just defined;
`FAIL(CONFORMANCE)` for an origin-1 inequality; and `SUPPORTED_EVIDENCE`
otherwise. Raw observation defects never trigger UNSUPPORTED(CROSSING).

### 9.2 Retention boundary

The manifest must be retained if someone wishes to audit the corresponding
falsification or conformance claim. Deleting it destroys evidence for that
claim. It need not survive between service executions to preserve any R0.1J
continuation: two executions with equal cut information and policies but
different manifest retention have identical `Obs_v` values. Evidence retention
and behavioral persistence are therefore separate ledgers.

No R0.1J manifest or experiment envelope has yet been produced. Enumeration,
negative verification, realization observation, and evidence retention status
are UNKNOWN.

## 10. Responsibility classifications with smallest witnesses

### 10.1 Witness order for classifications

The labels in this section apply only when an exact witness is listed. Witnesses
are minimized lexicographically by: post-cut ordinary C count, post-cut total
crossings, total pre-cut ordinary C count across the pair, number of differing
prefix crossings, the ranked alias sequences of the differing ordinary words,
and then oriented EncCut bytes. This order makes the first identity-transition
request at EMPTY, RI, the minimum such request. `MUST SURVIVE` means only that
enough information to preserve the named behavioral distinction must remain
somewhere in the declared total system across the stated execution boundary.
It does not require a field or a service-local copy.

`MAY REBUILD` means the target bytes/coordinate can be deleted as a separate
form and recovered by the exact named function from named surviving inputs.
The inputs and reconstruction machinery remain charged. `MAY FORGET` means the
named distinction lies within one proved `==J` class for the stated scope.

### 10.2 MUST SURVIVE

| Responsibility | Exact smallest deletion/merge collision |
|---|---|
| Active O across recovery | **S1-O:** idle recovery cut obtained from clean H() versus the matching cut from clean H(O0), both crashing before FIN with d=3. Deleting O makes the first forced F:RESUME collide. Zero post-cut ordinary C is minimal, and O0 is the lowest-ranked request that changes a residual. |
| Active P across recovery | **S1-P:** the same construction using clean H() versus H(AI). Deleting P collides `P=EMPTY` with `P=ID` in the first RESUME. AI is the lowest-ranked one-request word changing P. |
| Active G across recovery | **S1-G:** the same construction using clean H() versus H(E). Deleting G collides `E=E0` with `E=E1` in the first RESUME. E is the only request changing G. |
| Remaining live allowance across active recovery | **S2:** idle recovery after immediate pre-FIN crash at H() has d=3; idle recovery after completed no-op RI then pre-FIN crash has the same residual and d=2. Deleting d collides exact F:ALLOWANCE 3 and 2 before any post-cut ordinary C. |
| Idle versus interrupted-selector recovery obligation | **S3:** complete no-op RI then crash in the next idle gap versus crash immediately after RI's C, at the same residual and d=2. Deleting the pending barrier collides a one-suffix NONE family with the required OLD/NEW family; SELECTOR/PRIV separate at zero post-cut ordinary C. |
| Directed pre/post association until selection | **S4:** from clean H(), interrupt AI after C; from clean H(AI), interrupt D after C. Both cuts have d=2 and unordered endpoints EMPTY/ID. Their PUBLIC endpoint sets agree, but OLD and NEW F:RESUME associations reverse. Deleting direction causes a zero-post-cut-C SELECTOR/PRIV collision. This is the lowest-ranked reachable reversed nonidentity edge pair. |
| FIN-pending versus terminal obligation | **S5:** from H(), crash immediately before STOPPED versus immediately after STOPPED. Deleting the phase collides a suffix owing exactly one STOPPED with one forbidding every later C/R; their first RESUME already differs and no ordinary C is possible. |

These are information lower bounds only. Whether the information is held by a
service, controller, selector, manifest, process image, or medium is UNKNOWN.

### 10.3 MAY REBUILD

| Derived material | Exact smallest reconstruction witness |
|---|---|
| Exact RESUME and ALLOWANCE frame bytes | **R1:** the S1 H() idle-recovery side. Delete pre-serialized frames; apply the Section 4 templates to derived `(U,EMPTY,E0),d=3`; the exact first two F frames are restored. No ordinary post-cut action is needed. |
| Non-default semantic residual tuple as a separate cached form | **R2:** clean H(O0). Delete the cached tuple, fold its single completed transaction from `(U,EMPTY,E0)`, and reproduce X's exact `O=0 P=EMPTY E=E0 V=NONE` reply. O0 is the lowest-ranked one-request word reaching a non-default residual, so R2 is the exact smallest non-default reconstruction witness. |
| Noninitial live d as a separate cached form | **R3:** from clean H(), complete no-op RI and crash in the following idle gap. Delete cached d, count ordinary C occurrences after F:CUT from initial 3, and reproduce d=2 and its ALLOWANCE bytes. RI is the lowest-ranked identity transition at EMPTY. |
| Viewer projections and trace-set ordering | **R4:** H() with controller FIN and no crash. Delete every stored projection/set, project the generated FIN/STOPPED full suffix by Section 1, sort by Section 8, and reproduce all four projected values. This is the smallest nonempty complete suffix. |

R1-R4 do not say their source inputs survive physically. If a named input or
the frozen specification is absent, reconstruction is not established.

### 10.4 MAY FORGET

| Distinction | Exact smallest merger witness |
|---|---|
| Exact clean prehistory within one residual class | **F1:** H() versus H(RI). They are the shortest distinct clean histories with equal residual and every future outcome equal. |
| Pending no-op request identity | **F2:** from H(), interrupt RI versus RN immediately after C. Both are no-ops at `(U,EMPTY,E0)`, have d=2, emit the same two recovery suffixes, and remain equal under every future. |
| T pre-A versus post-A continuation phase | **F3:** from H(), interrupt T immediately before A versus immediately after A. The latter prefix has one extra A, but both cuts have the same r,d and identical OLD/NEW suffix families for every policy. The crossed A remains manifest/capture evidence, not continuation state. |
| Active residual and unused d after FIN | **F4:** FIN-pending recovery from H() versus from H(O0) forgets residual; FIN-pending recovery from H() versus after one completed no-op RI forgets d. Each pair has the same forced FIN_PENDING/READY/STOPPED suffix for all policies. One differing completed ordinary transaction is minimal. |
| Source residual and unused d after STOPPED | **F5:** append STOPPED to each F4 source and crash in END. Every pair has the same TERMINAL/READY suffix and no later C/R. |

No other responsibility receives one of the three labels. In particular,
specification identity, canonicalizer availability, manifest retention,
controller survival, capture durability, selector durability, and physical
media are charged but unclassified because the necessary deletion experiments
or cross-version futures have not been run.

## 11. Non-scalar total-system accounting

No row can compensate for another and no scalar score is defined.

| Dimension | Responsibility and charged location | R0.1J evidence/status |
|---|---|---|
| Boundary behavior | C/R/A/L/F histories, atomicity, exact projections | finite formal specification only |
| Future distinction | all-cut `==J`, five scopes, total phase router | 329-class prediction; unenumerated independently |
| Client/controller | external CLIENT-visible total truth table and live d input | grammar exact; availability/severing UNKNOWN |
| Scheduler | external PUBLIC/next-crossing vector over budget-one G | grammar exact; G size and recovery reconstruction UNKNOWN |
| Selector | external OLD/NEW authority at every interrupted barrier | both formal branches enumerated; external perturbation UNKNOWN |
| Capture peer | external atomic A observation isolated from client | semantic crossing only; omission/durability UNKNOWN |
| Manifest | external observed/generated suffix evidence and spec digest | format exact; no manifest produced |
| Canonicalizer | D/G closure, codecs, projection, sorting, witness search | algorithm specified; independent implementation UNKNOWN |
| Specification | exact interpretation and template authority | required input to rebuilding; collision/availability untested |
| Recovery | abstract DOWN/RESUME/READY and selected application | formal transition only; process/power recovery UNKNOWN |
| Termination | FIN-pending versus terminal obligations | finite formal distinction only |
| Evolution | one semantic E0->E1 transition | no meaning-changing version migration |
| Runtime/operations | closure cost, enumeration, fault injection, monitoring | UNKNOWN |
| Cognition | fresh implementer/reviewer time, errors, expertise, access | charged to experiment envelope; no study, UNKNOWN |
| TCB | runtime, OS, transport, serializer, compiler, capture, selector, oracle, canonicalizer, spec, build, human adjudication | no perturbation or closure evidence, UNKNOWN |
| External services | controller, scheduler, capture peer, selector, manifest store, spec distribution | moving work is not deletion; severing not run, UNKNOWN |
| Security/authority | authentication, authorization, privacy, tenancy | unsupported and UNKNOWN |
| Physical realization | media, caches, corruption, rollback, power loss, receiver effect, physical completion | no permitted physical realization; UNKNOWN |
| Cross-realization | materially unlike implementations and failure domains | none built; UNKNOWN |

## 12. Simultaneous attack gate and limits

A future realization receives no classification from generated traces alone. At
one frozen spec digest and one build/manifest identity it must face, at least:

| Attack | Required evidence |
|---|---|
| DELETE/MERGE | remove one S1-S5 distinction or force its pair together; run the listed smallest witness and reject any collision |
| DERIVE/RECOMPUTE | remove each R1-R4 target, cold-start from exactly the named inputs, measure machinery and work, and compare exact bytes |
| FUTURE/COLLIDE | exhaust every declared cut under common D/G policies and all five scopes; force implementation identifiers to collide only where `==J` does |
| EXTERNALIZE | sever controller, scheduler, capture, selector, manifest, specification, and canonicalizer one at a time; record movement versus actual loss |
| REALIZE | use two materially unlike physical realizations and independent physical adjudication; do not reuse one realization's evidence for the other |
| COGNITION | give fresh reviewers only the claimed sufficient artifacts; measure bounded time, choices, errors, expertise, and access |
| TCB | enumerate and perturb every influence named in Section 11; use an oracle that does not share the perturbed transition/recovery code |

No such campaign has run for R0.1J. DELETE, DERIVE, RECOMPUTE, FUTURE,
COLLIDE, EXTERNALIZE, REALIZE, COGNITION, TCB, and their composite outcomes are
UNKNOWN. Formal predictions remain falsifiable, but they are not inherited
PASS evidence.

Explicitly unsupported are partial/torn frames; empty ordinary requests;
arbitrary authoring or query languages; prehistory deeper than two; more than
three post-cut ordinary occurrences; randomness; concurrent clients or
requests; more than one crash; crash during or failure of recovery; arbitrary
versions/migrations; clocks, fairness, resource exhaustion, billing, backup,
restore, authentication, authorization, privacy, corruption, rollback, power
loss, and receiver effects.

## 13. Frozen predictions and nonclaims

R0.1J predicts, subject to independent falsification:

1. exactly 157 clean and 1,208,272 recovery cut histories, all compared by one
   relation;
2. fourteen clean classes with the stated multiset and 2,351/9,895 pair split;
3. a zero-ordinary-C privileged separator for every unequal clean pair;
4. a one-ordinary-C X separator and no zero-ordinary-C separator for every
   unequal clean pair in PUBLIC;
5. congruence of every equal-residual clean pair under all finite policies;
6. 139 recovery PUBLIC outcome functions and 315 recovery contractual classes
   under the no-gate relation;
7. 153 PUBLIC outcome functions and 329 contractual classes over all declared
   cuts;
8. the combined normalized histogram
   `277x1,9x8,27x9,14x10,2x68`;
9. correct OLD/NEW directed application with no invented interrupted R;
10. one total captured A after pre-A T interruption and client-blind retry,
    versus two after post-A interruption and retry, without any receiver-effect
    conclusion;
11. exactly one STOPPED after FIN-pending recovery and none after terminal
    recovery; and
12. byte-for-byte agreement of independently implemented codecs, D/G closures,
    outcomes, and canonical witnesses under Sections 5 and 8.

The exact D/G sizes, controller/scheduler counts, exact-history class-size
multiset, canonical witness byte strings, enumeration runtime and memory,
negative-verifier behavior, implementation agreement, manifest production,
external-service availability, cognition burden, TCB closure, storage volume,
physical persistence, power-failure behavior, capture durability, privacy,
authority, physical action completion, exactly-once effects, and agreement
between unlike realizations are UNKNOWN.

These bytes freeze only the R0.1J candidate. Any repair, implementation
assumption, new realization, or added observation changes the future relation
and requires a new candidate rather than an informal interpretation.
