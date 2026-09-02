# FBH-12/2/3-I: a total finite boundary-history candidate

## 0. Status, authority, and claim boundary

This document is the R0.1I candidate specification. It replaces ambiguous
R0.1H semantics; it does not report an implementation, a run, a storage
layout, a physical fact, or an attack result.

Its authorities are, in order:

1. the exact bytes in this document;
2. the exact finite algorithms and encodings below; and
3. a future manifest produced from those algorithms.

The earlier R0.1H candidate, fresh break, mathematical audit, conditional
recovery quotient, final falsifier semantics, and feasibility audit were attack
inputs only. No earlier storage proposal is adopted.

The supported capabilities remain bounded observation, ID/NOT authoring and
replacement, retirement, query, immediate explanation, externally captured
action attempt, one E0-to-E1 evolution, current-engine query, one crash, and
explicit FIN/STOPPED termination.

The words history, residual, phase, class, and responsibility below are
mathematical. They do not name fields, records, files, journals, tables,
devices, or storage locations.

## 1. Full exact histories and viewer projections

### 1.1 Atomic crossings

A full exact history is an ordered sequence of atomic crossings on five
channels:

| Channel | Direction | Crossing |
|---|---|---|
| C | client to service | one request frame, or typed FIN |
| R | service to client | one reply frame, or STOPPED newline |
| A | service to independent capture peer | one action-attempt frame |
| L | lifecycle observer | typed DOWN or READY |
| F | privileged manifest/control boundary | one exact F frame |

C, R, A, and F frames are nonempty ASCII and end in one LF. FIN, DOWN, and
READY are typed crossings without frame bytes. C, R, and A fragmentation,
partial crossing, tearing, duplication, and reordering are unsupported.

No two crossings are atomic together. The semantic application rule in
Section 4 says which single crossing changes the residual.

The exact F frames are:

    CUT REMAINING=3\n
    CRASH GAP=<canonical decimal ordinal>\n
    SELECT old\n
    SELECT new\n
    RESUME ACTIVE O=<O> P=<P> E=<G>\n
    ALLOWANCE <d>\n
    RESUME FIN_PENDING\n
    RESUME TERMINAL\n

Canonical decimal is zero or a base-ten positive integer with no leading zero.
Substitutions use only tokens defined in this document.

F:CUT is inserted at the designated clean cut. It is not a schedulable
crossing. F:CRASH and F:SELECT are privileged controls. F:RESUME and
F:ALLOWANCE are privileged oracle records derived from the exact history and
specification. They expose semantic behavior to the conformance harness without
requiring any particular service representation.

### 1.2 Full record is not a viewer trace

The full exact history retains the interleaving of all five channels, the cut
descriptor, and the semantic validation ledger derived in Section 4. A viewer
trace is a typed projection of that full record:

| Viewer | Retained crossings |
|---|---|
| CLIENT | C, R, L |
| CAPTURE | A |
| PUBLIC | C, R, A, L |
| SELECTOR | F |

No viewer projection is the full exact record. In particular, concatenating
PUBLIC and SELECTOR projections does not reconstruct their interleaving unless
the full manifest also survives.

The legal client controller observes CLIENT only. It never observes A or F.
The independent capture peer observes A only and sends no information to the
client during a run. The scheduler observes the current PUBLIC suffix and the
proposed next crossing. The selector is privileged and inaccessible to the
client.

All four projections are contractual. In addition, the label-indexed
privileged branch record before projection and deduplication is contractual.
Thus old/new orientation is required at an interrupted request barrier even
when two public traces later deduplicate.

## 2. Complete client alphabet and clean corpus

The message rank order and exact bytes are:

| Rank | Alias | Bytes |
|---:|---|---|
| 0 | O0 | OBSERVE 0 newline |
| 1 | O1 | OBSERVE 1 newline |
| 2 | AI | AUTHOR ID newline |
| 3 | AN | AUTHOR NOT newline |
| 4 | RI | REPLACE ID newline |
| 5 | RN | REPLACE NOT newline |
| 6 | D | RETIRE newline |
| 7 | Q | QUERY newline |
| 8 | X | EXPLAIN newline |
| 9 | T | ATTEMPT newline |
| 10 | E | EVOLVE newline |
| 11 | K | CURRENT newline |

Each phrase “newline” above denotes exactly one LF byte. These twelve frames
are the entire nonempty legal request alphabet. Empty input is unsupported and
is not FIN. Arbitrary programs, source, bytecode, callbacks, search expressions,
and plugins are unsupported.

For every word w of length zero, one, or two over the ranked alphabet:

1. start fresh at (U,EMPTY,E0);
2. execute w failure-free and serially;
3. complete every reply;
4. append F:CUT REMAINING=3; and
5. designate the point after that F crossing as the clean cut.

The C crossings make the 157 words produce 157 distinct full clean histories:

    12^0 + 12^1 + 12^2 = 157.

## 3. Clean residual semantics and exact outputs

### 3.1 Residual coordinate

The semantic residual is:

    r = (O,P,G)
    O in {U,0,1}
    P in {EMPTY,ID,NOT}
    G in {E0,E1}

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

The transition delta(r,m) is:

- O0 sets O to 0; O1 sets O to 1.
- AI sets EMPTY to ID and otherwise leaves P unchanged.
- AN sets EMPTY to NOT and otherwise leaves P unchanged.
- RI sets a nonempty P to ID and leaves EMPTY unchanged.
- RN sets a nonempty P to NOT and leaves EMPTY unchanged.
- D sets a nonempty P to EMPTY and leaves EMPTY unchanged.
- E sets E0 to E1 and leaves E1 unchanged.
- Q, X, T, and K leave the residual unchanged.

This coordinate is derived semantic behavior, not a representation prescription.

### 3.2 Failure-free transaction bytes

For pre-request residual r, C first crosses the exact request. Completion then
crosses:

| Request and precondition | Completion |
|---|---|
| O0 | R:OK OBSERVE 0 newline |
| O1 | R:OK OBSERVE 1 newline |
| AI with P=EMPTY | R:OK AUTHOR ID newline |
| AI otherwise | R:ERR ACTIVE newline |
| AN with P=EMPTY | R:OK AUTHOR NOT newline |
| AN otherwise | R:ERR ACTIVE newline |
| RI with P nonempty | R:OK REPLACE ID newline |
| RI otherwise | R:ERR EMPTY newline |
| RN with P nonempty | R:OK REPLACE NOT newline |
| RN otherwise | R:ERR EMPTY newline |
| D with P nonempty | R:OK RETIRE newline |
| D otherwise | R:ERR EMPTY newline |
| Q | R:VALUE <V> newline |
| X | R:WHY O=<O> P=<P> E=<G> V=<V> newline |
| T | A:TRY O=<O> P=<P> E=<G> V=<V> newline, then R:OK ATTEMPTED newline |
| E with G=E0 | R:OK ENGINE E1 newline |
| E with G=E1 | R:OK ENGINE E1 ALREADY newline |
| K | R:ENGINE <G> newline |

Angle-bracket substitutions are finite tokens, not literal brackets. X is the
same transaction's immediate boundary completion. No wall-clock bound follows.

An A crossing means only that the independent capture peer observed that exact
frame at the defined atomic boundary. It does not imply receiver execution,
receiver durability, downstream success, or exactly-once effects.

## 4. Occurrence, application, completion, and recovery

### 4.1 Four distinct notions

For an ordinary request:

1. Occurrence happens exactly when its C frame crosses. It consumes one unit of
   future allowance and captures pre-residual r and post-residual delta(r,m).
2. Semantic application happens either:
   - atomically with the ordinary R completion in a failure-free transaction; or
   - atomically with F:SELECT new after an interrupted transaction.
3. R completion happens exactly when that request's R frame crosses.
4. Recovery selection happens only if C crossed and R did not.

F:SELECT old does not semantically apply the interrupted request and resumes r.
F:SELECT new semantically applies delta(r,m) without inventing an R completion
and resumes delta(r,m).

The full-history residual fold therefore processes:

- a validated ordinary R as one application of its pending request;
- F:SELECT new as one application of its pending interrupted request;
- F:SELECT old as no application.

It never equates “semantic application” with “ordinary R crossed.” This makes
the residual a total function of the full F-bearing exact history while public
projections may remain nondeterministic.

Identity transitions and failed preconditions still admit both old and new
labels at an interrupted barrier. Their selected residuals are equal, but their
privileged label-indexed branch records remain distinct.

### 4.2 Crash phases and recovery sequences

There is at most one crash. It occurs only at a gap between nominal atomic
crossings. F:CUT is metadata and is not a gap. No crash occurs during recovery.

At a crash, append:

    F:CRASH GAP=<g>\n
    L:DOWN

This point, after DOWN and before SELECT or RESUME, is the one and only object
called a recovery cut in R0.1I.

If an ordinary C crossed and its R did not, both branches are required:

    F:SELECT old\n
    F:RESUME ACTIVE O=<old O> P=<old P> E=<old G>\n
    F:ALLOWANCE <d>\n
    L:READY

and

    F:SELECT new\n
    F:RESUME ACTIVE O=<new O> P=<new P> E=<new G>\n
    F:ALLOWANCE <d>\n
    L:READY

The interrupted transaction then emits no A and no R. For T interrupted after
A, the already crossed A remains in the prefix; no second A is emitted for that
interrupted occurrence.

At an idle crash there is no SELECT:

    F:RESUME ACTIVE O=<O> P=<P> E=<G>\n
    F:ALLOWANCE <d>\n
    L:READY

SELECT is forbidden at idle, after an ordinary R, during FIN recovery, and
after STOPPED. This fixes the former clean-gap old/new ambiguity.

### 4.3 FIN and terminal boundary

FIN is a typed C occurrence, consumes no ordinary-message allowance, and
forbids every later C crossing. Its completion is exactly one
R:STOPPED newline.

A crash between FIN and STOPPED yields:

    C:FIN
    F:CRASH GAP=<g>\n
    L:DOWN
    F:RESUME FIN_PENDING\n
    L:READY
    R:STOPPED\n

There is no SELECT. The FIN obligation survives until STOPPED crosses.

STOPPED is the client-protocol terminal boundary. No C or R may follow it.
The scheduler must nevertheless evaluate the one terminal gap after STOPPED.
If it crashes there, the full complete suffix is:

    C:FIN
    R:STOPPED\n
    F:CRASH GAP=<g>\n
    L:DOWN
    F:RESUME TERMINAL\n
    L:READY

READY here closes lifecycle recovery observation; it does not reopen the client
protocol. A run with a terminal crash is complete after this READY. A run
without it is complete after the scheduler passes the terminal gap.

## 5. Remaining allowance and controller grammar

### 5.1 Allowance

The clean cut begins with d=3. Every nonempty ordinary C occurrence, including
a retry, atomically changes d to d-1. FIN does not. No ordinary C is legal at
d=0.

In a full clean-cut run the client derives d from its initial 3 and its own C
occurrences. The full manifest derives the same value. At an active recovery,
F:ALLOWANCE records it before READY. A cut-local recovery experiment supplies d
as an explicit controller parameter.

Thus the allowance responsibility is charged to the controller and privileged
manifest/evaluator, not silently to the service. If either is severed or reset,
conformance is not established. Once FIN crosses, the unused numeric allowance
has no future role and F:ALLOWANCE is not emitted.

### 5.2 Legal deterministic controllers

A controller acts only at an idle decision point. It observes the exact CLIENT
suffix since the designated experiment cut and its current d:

- if d>0, it chooses one of the twelve messages or FIN;
- if d=0, FIN is forced;
- after sending an ordinary C, it waits for that request's R or for READY after
  interruption;
- after FIN it has no action.

Client randomness and nondeterminism are unsupported. Adaptive choice is
otherwise unrestricted over the finite CLIENT suffix.

For reproducibility, let D be the least finite set of all syntactically legal
decision keys (d, CLIENT suffix) reachable from any declared cut when every
legal action, crash choice, and selector branch is explored. Compute D by
breadth-first closure of the transition rules, deduplicate by the canonical key
encoding in Section 10, then sort bytewise.

A controller is a total truth table over D. Each entry is one action code.
Entries with d=0 must encode FIN. This grammar includes every deterministic
adaptive controller in the bounded domain and gives the same table meaning on
divergent paths.

## 6. One common scheduler-policy grammar

At each nominal gap before the crash budget is used, form the scheduler key:

    (exact PUBLIC suffix since the designated cut,
     exact proposed next crossing or END)

The proposed next crossing distinguishes, for example, a gap before a chosen C
from a gap before FIN. END names only the terminal gap after STOPPED.

Let G be the least finite set of all such keys reachable from every declared
cut under all controller actions and both selector branches. Generate it by the
same exhaustive closure as D, deduplicate by canonical encoding, and sort
bytewise.

A scheduler policy is one bit for every key in G:

- zero passes the gap;
- one causes the crash if the crash budget is still one;
- after the first crash the budget is zero and every later bit is ignored.

The all-zero vector is no-crash. A bit whose key is absent from one adaptive
path simply does nothing on that path. The same total vector is therefore
well-defined across divergent controller paths; there is no path-specific gap
ordinal or invalid scheduler.

The actual F:CRASH frame records the zero-based ordinal of the realized nominal
gap after F:CUT. The scheduler observes PUBLIC, including A, so it can target
the post-A/pre-R gap. The legal client still cannot observe A.

The numeric sizes of D and G are finite but not derived in this document.
Their exact values and the resulting numbers of controller/scheduler tables are
UNKNOWN until an independent enumerator emits them. Finiteness follows from
d in 0..3, crash budget in 0..1, finite phases, finite frames, and terminal
closure.

## 7. Complete branch records, May, Must, and equivalence

### 7.1 Branch records before deduplication

For a cut H, controller Ctl, and scheduler policy Sch, the oracle first emits a
nonempty ordered branch-record list:

- one record with branch NONE if no interrupted selector barrier occurs;
- two records ordered OLD then NEW if one occurs, even when their projected
  traces are equal.

Each branch record contains:

1. the complete full F-bearing suffix;
2. branch key NONE, OLD, or NEW;
3. the validated semantic application fold and selected residual/phase;
4. the starting and ending allowance;
5. its branch-local truth evidence for every Must proposition below; and
6. all four viewer projections.

No branch record is discarded or deduplicated.

The ordered branch family additionally carries the family-level truth values
whose predicates mention both OLD and NEW. The final ten-bit truth mask is
computed for the family and copied identically into every encoded branch record
so that no record can be detached from the verdict it helped establish.

For viewer v:

    May_v(H,Ctl,Sch)

is the set of complete v-projected traces from the branch records. Equal
projected traces are deduplicated only here.

The privileged conformance value Priv is the ordered complete branch-record
list. Equality of Priv is required in addition to every May_v equality. This
choice makes old/new label behavior contractual while preserving hidden labels
for CLIENT, CAPTURE, and PUBLIC.

### 7.2 Exact Must vocabulary and vacuity

The fixed proposition order is:

1. every F:CRASH is followed by exactly one DOWN and, after zero or one valid
   SELECT, exactly one READY;
2. exactly one FIN and exactly one STOPPED occur, FIN precedes STOPPED, and no
   later C or R occurs;
3. an ordinary request interrupted before R receives no later R completion;
4. every A occurs while T is pending;
5. every failure-free completed T has exactly one A before its R;
6. every interrupted request has exactly one SELECT old and one SELECT new
   branch record, with selected residuals r and delta(r,m);
7. non-interrupted, FIN-pending, and terminal crashes have no SELECT;
8. allowance starts as declared, decrements exactly on ordinary C, never goes
   negative, and agrees with every F:ALLOWANCE;
9. every F:RESUME token equals the residual or special phase derived from the
   full history;
10. an A crossing already in a prefix is never retracted or replayed by
    recovery.

Each is a universal implication. If its antecedent never occurs, it is true
vacuously. There is no inapplicable third value.

Must(H,Ctl,Sch) is the subset of these ten names whose branch-local clauses are
true in every complete branch record and whose family-level clauses are true
of the ordered branch family. It is evaluated before projection or May
deduplication. A conforming supported oracle case has all ten.

### 7.3 Equivalence

Only cuts with the same cut kind and live allowance contract are compared.
Future equivalence is:

    H equivalent H'

iff, for every legal controller table and the same legal scheduler bit vector:

- Priv values are exactly equal;
- May_CLIENT, May_CAPTURE, May_PUBLIC, and May_SELECTOR are exactly equal; and
- Must sets are exactly equal.

The exact prefix before a cut is not appended to the compared suffix. It
remains part of the full history corpus and manifest evidence. This permits
different histories to share a continuation while preserving their past
crossing differences.

The common controller and scheduler truth-table domains make reflexivity,
symmetry, and transitivity ordinary equality properties rather than
path-dependent assumptions.

## 8. Total finite clean and recovery-cut corpus

### 8.1 Unique exact recovery prefixes

For each of the 157 clean histories, let u be a completed failure-free future
word. F:CUT fixes the prehistory/future split, so two different splits cannot
collapse into one full exact history.

Every unique first-crash recovery prefix is one of:

| Recovery prefix phase | Choices per clean history |
|---|---:|
| Idle after completed u, length 0..3 | 1+12+144+1728 = 1,885 |
| Non-T pending after u of length 0..2 | 11*(1+12+144) = 1,727 |
| T after C and before A | 1+12+144 = 157 |
| T after A and before R | 1+12+144 = 157 |
| FIN-pending after completed u, length 0..3 | 1,885 |
| Terminal after STOPPED for u, length 0..3 | 1,885 |
| Total | 7,696 |

Every prefix is realizable by some controller truth table and a scheduler bit
set on that exact PUBLIC-prefix/next-crossing key.

Across all clean histories:

| Phase | Unique exact recovery prefixes |
|---|---:|
| Idle | 295,945 |
| Non-T pending | 271,139 |
| T pre-A | 24,649 |
| T post-A | 24,649 |
| FIN-pending | 295,945 |
| Terminal | 295,945 |
| Total recovery prefixes | 1,208,272 |

The total cut corpus therefore contains:

    157 clean cuts + 1,208,272 recovery cuts = 1,208,429 exact cut histories.

These are unique exact prefixes, not word/schedule structures counted with
duplicate shared prefixes and not executions.

### 8.2 Normalized reachable recovery conditions

After zero, one, two, and three completed future messages, the numbers of
reachable residuals are respectively:

    14, 18, 18, 18.

Normalizing exact recovery histories by residual, remaining allowance, request,
and phase gives:

| Condition family | Count |
|---|---:|
| Idle active (r,d) | 68 |
| Interrupted changing non-T | 195 |
| Interrupted no-op non-T | 355 |
| T pre-A | 50 |
| T post-A | 50 |
| FIN-pending source conditions | 68 |
| Terminal source conditions | 68 |
| Total | 854 |

The interrupted non-T total is 550. At d=2 its fourteen source residuals give
57 changing and 97 no-op conditions. At d=1 and d=0 each full eighteen-state
source set gives 69 changing and 129 no-op conditions.

## 9. Predicted quotients

### 9.1 Clean quotient

The 157 clean histories have exactly the fourteen reachable coordinates and
class sizes:

    {59,17,17,16,16,16,2,2,2,2,2,2,2,2}.

X injectively exposes O, P, and G. An empty future exposes only
coordinate-independent FIN/STOP behavior. Therefore every unequal clean pair
has a one-message X separator and no empty separator.

The same residual and allowance determine every later output, transition,
selector map, F:RESUME, action frame, controller observation, and scheduler
key. Induction over d and crash budget therefore predicts unconditional
same-coordinate congruence under the R0.1I grammars.

The unordered pair counts remain:

    same class: 2,351
    unequal: 9,895
    total: 12,246.

### 9.2 Public recovery quotient

If F and label-indexed Priv are ignored and only PUBLIC continuation is
compared, the active classes by allowance are:

| d | Public active classes | Reason |
|---:|---:|---|
| 3 | 14 | clean idle residuals |
| 2 | 59 | 18 singleton residuals plus 41 unordered changing edges |
| 1 | 63 | 18 singleton residuals plus all 45 unordered changing edges |
| 0 | 1 | no ordinary message remains; every active condition proceeds to FIN |

FIN-pending and terminal add two, giving 139 PUBLIC recovery classes.
This is a projection quotient only; it is not the contractual total quotient.

The 41 at d=2 is the full 45-edge graph minus four edges that have no source
among the fourteen clean coordinates: the two 0-to-1 observation edges at
P=ID/NOT,G=E1 and the two ID-to-NOT program edges at O=0/1,G=E1.

### 9.3 Contractual privileged recovery quotient

SELECTOR sees RESUME and ALLOWANCE, and Priv preserves branch labels before
deduplication. The active class counts are:

| d | Classes |
|---:|---:|
| 3 | 14 clean, no-selector residual classes |
| 2 | 18 clean + 14 equal old/new + 57 directed changing = 89 |
| 1 | 18 clean + 18 equal old/new + 69 directed changing = 105 |
| 0 | 18 clean + 18 equal old/new + 69 directed changing = 105 |

F:RESUME makes the selected residual contractual even at d=0. FIN-pending and
terminal each form one class across all dead allowance/source values.

The predicted contractual recovery quotient is therefore:

    14 + 89 + 105 + 105 + 1 + 1 = 315 classes.

The quotient of the 854 normalized conditions has the class-multiplicity
histogram:

| Raw conditions per class | Number of classes |
|---:|---:|
| 1 | 263 |
| 8 | 9 |
| 9 | 27 |
| 10 | 14 |
| 68 | 2 |

The check is:

    263 + 9 + 27 + 14 + 2 = 315 classes
    263 + 9*8 + 27*9 + 14*10 + 2*68 = 854 conditions.

Every exact recovery prefix maps to one of these conditions and every class is
reachable, so the same contractual class count 315 is predicted for the
1,208,272 exact recovery histories. Their full class-size multiset is not
printed here and remains UNKNOWN until an independent exact-history enumerator
emits it.

No clean and recovery class counts are added together as if their cut kinds
were comparable.

## 10. Fully specified canonical bytes and witness order

### 10.1 Primitive codec

All integers are unsigned big-endian. U8 is one byte. U16 is two bytes. U64 is
eight bytes. Bytes(x) is U64(length of x) followed by x. List(x1..xn) is
U64(n) followed by Bytes(Enc(x1)) through Bytes(Enc(xn)).

Crossing tags are:

| Tag | Crossing | Payload in encoding |
|---:|---|---|
| 1 | C frame | exact frame bytes |
| 2 | typed C:FIN | empty |
| 3 | R frame | exact frame bytes |
| 4 | R:STOPPED newline | empty |
| 5 | A frame | exact frame bytes |
| 6 | L:DOWN | empty |
| 7 | L:READY | empty |
| 8 | F frame | exact frame bytes |

EncCrossing is U8(tag) followed by Bytes(payload). Empty typed payloads still
encode Bytes(empty). EncTrace is List of EncCrossing in crossing order.

Residual token codes are:

    O: U=0, 0=1, 1=2
    P: EMPTY=0, ID=1, NOT=2
    G: E0=0, E1=1

EncResidual is the three U8 codes. Alias action codes are rank plus one; FIN is
zero. Viewer codes are CLIENT=0, CAPTURE=1, PUBLIC=2, SELECTOR=3.

Cut-kind codes are CLEAN=0, IDLE_RECOVERY=1, PENDING_NON_T=2, T_PRE_A=3,
T_POST_A=4, FIN_PENDING=5, TERMINAL=6. EncCut is U8(kind), U8(d or 255 if
dead), optional EncResidual, optional U8(alias), then EncTrace(full prefix).
Presence is determined uniquely by kind.

### 10.2 Controller and scheduler encoding

EncDecisionKey is U8(d) followed by Bytes(EncTrace(CLIENT suffix)).
The canonical D list is the sorted unique EncDecisionKey list from the
breadth-first closure in Section 5.

EncController is:

    U8(1 version), U64(number of D keys), then one U8 action per D key

in canonical D order. No keys are repeated in the controller bytes because D
is specification-derived. A non-FIN action at a d=0 key makes the description
UNSUPPORTED(CONTROLLER_D0).

EncGapKey is Bytes(EncTrace(PUBLIC suffix)) followed by
Bytes(EncCrossing(next)) or one byte 255 for END. The canonical G list is its
sorted unique closure.

EncScheduler is:

    U8(1 version), U64(number of G keys), then ceil(N/8) policy bytes

Bits are packed most-significant first in G order. Unused low bits in the final
byte must be zero. A wrong count or nonzero padding is unsupported.

### 10.3 Branch, outcome, and witness encoding

Branch codes are NONE=0, OLD=1, NEW=2. The ten Must truths are a U16 mask whose
bits 0 through 9 follow Section 7.2; bits 10 through 15 must be zero.

EncBranchRecord is:

    U8(branch), U8(start d or 255), U8(end d or 255),
    U8(residual-present), optional EncResidual,
    U16(truth mask), Bytes(EncTrace(full suffix)).

Branch records are ordered NONE alone or OLD then NEW. EncTraceSet first
deduplicates encoded traces, sorts them bytewise, and applies List.

EncOutcome is:

    List(branch records),
    EncTraceSet(CLIENT),
    EncTraceSet(CAPTURE),
    EncTraceSet(PUBLIC),
    EncTraceSet(SELECTOR),
    U16(Must mask).

EncWitness is:

    ASCII bytes FBH-R01I-WITNESS followed by one zero byte,
    U8(viewer code),
    Bytes(EncCut(left)),
    Bytes(EncCut(right)),
    Bytes(EncController),
    Bytes(EncScheduler),
    Bytes(EncOutcome(left)),
    Bytes(EncOutcome(right)).

Unordered pairs are oriented by bytewise EncCut order. A separating witness is
ordered by the following lexicographic tuple:

1. maximum ordinary C count among all complete branch suffixes;
2. sum of ordinary C counts across all branch records;
3. sum of pre-cut ordinary C counts;
4. left pre-cut C count;
5. right pre-cut C count;
6. total branch-record count;
7. total F:CRASH count;
8. byte length of EncWitness;
9. EncWitness bytes.

Every component is exact. The controller and scheduler universes are finite,
natural-number prefixes are well-founded, and byte strings of fixed length are
totally ordered. Hence every separable finite pair has one reproducible
canonical witness. No wall-clock timing or implementation-local hash
participates.

## 11. Minimized witnesses

### 11.1 Clean distinction and merge

The smallest unequal clean pair is H() versus H(O0). Empty futures both perform
FIN/STOPPED. One X says O=U versus O=0.

The smallest intended same-class pair is H() versus H(RI). RI returns ERR EMPTY
and leaves (U,EMPTY,E0). Every R0.1I future suffix is predicted equal.

### 11.2 Selected application

Start H(), send AI, and crash at the gap after C. Both exact prefixes contain
C:AUTHOR ID, F:CRASH, and DOWN. Their continuations are:

    SELECT old; RESUME O=U P=EMPTY E=E0; ALLOWANCE 2; READY
    SELECT new; RESUME O=U P=ID E=E0;    ALLOWANCE 2; READY

The new SELECT, not an absent ordinary R, semantically applies AI. A later X or
retry separates public continuations. The exact full histories already differ
in F.

O0 and E give the same minimized application witness on O and G.

### 11.3 Hidden public merger versus privileged orientation

Interrupted AI from EMPTY to ID and interrupted D from ID to EMPTY have the
same unordered PUBLIC May endpoints. SELECTOR/Priv distinguishes their
old/new maps immediately through SELECT and RESUME, without spending a client
message. They are distinct contractual classes.

A clean recovery at r and an interrupted no-op at r have the same PUBLIC
continuation. Priv distinguishes no selector from two label-indexed branches.

Different no-op request identities at the same r,d merge: no interrupted reply
occurs and their OLD/NEW RESUME records are identical.

### 11.4 ATTEMPT phases

T interrupted before A and T interrupted after A have identical recovery
continuations and merge at fixed r,d. Their exact prefixes do not merge: the
post-A history contains the captured A.

Because CLIENT cannot observe A, the fixed retry-on-READY controller retries in
both cases. The pre-A case exposes one A total; the post-A case exposes two.
Neither count implies receiver effects.

### 11.5 FIN and terminal

FIN-pending owes STOPPED after READY. Terminal owes no C or R and ends after
READY. They are separated with zero client messages and must never merge.

### 11.6 Smallest selector-padding witness

For future word T, nominal crossings are C,T action,R,FIN,STOPPED. It has six
gaps plus no-crash. Both C-to-A and A-to-R are interrupted selector barriers.
Exercising OLD and NEW at every barrier requires nine slots, not eight.

## 12. Linear schedule and selector counts

For a fixed word with n messages and t T occurrences:

    nominal crossings = 2n+t+2
    gaps = 2n+t+3
    no-crash plus gap probes = 2n+t+4
    per-gap OLD/NEW padded probes = 3n+2t+4.

For all words of length zero through three:

| n | Words | T occurrences | Base probes | Padded probes |
|---:|---:|---:|---:|---:|
| 0 | 1 | 0 | 4 | 4 |
| 1 | 12 | 1 | 73 | 86 |
| 2 | 144 | 24 | 1,176 | 1,488 |
| 3 | 1,728 | 432 | 17,712 | 23,328 |
| Total | 1,885 | 457 | 18,965 | 24,906 |

Across 157 clean histories:

    base conceptual structures = 2,977,505
    padded per-gap branch slots = 3,910,242.

These are canonical linear probe-plan counts, not executions and not the
number of truth-table scheduler policies.

## 13. Simultaneous mandatory attack gate

Any future candidate realization is evaluated at one frozen revision and one
manifest identity. All attacks run before any implementation classification is
credited:

| Attack | Required operation and rejection criterion |
|---|---|
| DELETE | Remove one named responsibility, cold-start every cut family, and reject any changed Priv, May, or Must result. |
| MERGE | Force two candidate continuation conditions together and run their canonical witness; reject any differing outcome. |
| DERIVE | Remove target material and rebuild it only from named surviving responsibilities plus this exact specification; record all machinery and cost. |
| RECOMPUTE | Restart without the target form, reconstruct from named inputs, and measure replay/evaluation work and recovery dependencies. |
| COLLIDE | Compare canonical bytes for every distinct reachable condition; force equal implementation hashes and reject whenever canonical bytes or futures differ. |
| FUTURE | Exhaustively refine every cut through all controller tables, the common scheduler grammar, both selector labels, every viewer, branch records, and Must truths. |
| EXTERNALIZE | Move a responsibility to a named controller, capture peer, manifest, build input, or service; sever it during recovery and record the result as movement, not deletion. |
| REALIZE | Build two unlike post-quotient realization families and an independent oracle without shared transition/recovery code; compare all declared cases. |
| COGNITION | Give a fresh implementer only this frozen specification and exact manifests; record choices, time, errors, and any undocumented knowledge. |
| TCB | Enumerate and perturb runtime, OS, transport, serializer, compiler, caches, fault hook, capture peer, selector, manifest, oracle, canonicalizer, specification, and build inputs. |

DELETE, DERIVE, RECOMPUTE, EXTERNALIZE, REALIZE, COGNITION, and TCB have not
been executed for R0.1I. The finite candidate makes them runnable; it supplies
no pass evidence.

## 14. Behavioral responsibility classifications

Only the following three labels are used. They are total-system behavioral
labels, never physical deletion or storage claims.

| Responsibility | Classification | Scope |
|---|---|---|
| Distinguish fourteen clean classes | MUST SURVIVE | X gives the unconditional clean lower bound. |
| Distinguish the contractual recovery branch/phase/allowance classes | MUST SURVIVE | Priv and SELECTOR require the 315-class behavior before allowed mergers. |
| Exact specification identity and application rules | MUST SURVIVE | Required to interpret C, R, SELECT, RESUME, and bytes. |
| Controller allowance and continuation policy during a full run | MUST SURVIVE | Charged to the client/controller side and manifest validation. |
| Selector authority and OLD/NEW branch association | MUST SURVIVE | Required at every interrupted request barrier, including no-ops and both T gaps. |
| Complete branch records before May dedup | MUST SURVIVE | Required for privileged conformance and Must. |
| FIN-pending exactly-one STOPPED responsibility | MUST SURVIVE | Until STOPPED crosses. |
| Terminal no-more-C/R responsibility | MUST SURVIVE | Through optional terminal recovery. |
| An A crossing that already occurred | MUST SURVIVE | As an immutable capture/full-history fact; it must not be replayed. |
| Canonical codec and closure-domain identity | MUST SURVIVE | Needed for reproducible controllers, schedulers, outcomes, and witnesses. |
| Exact reply, A, RESUME, and ALLOWANCE bytes | MAY REBUILD | From surviving semantic responsibilities plus the frozen specification; machinery and cost remain charged. |
| Clean residual coordinate | MAY REBUILD | From a validated full application history plus this specification. |
| Remaining d before FIN | MAY REBUILD | From initial 3 and exact ordinary C occurrences. |
| Viewer May sets and Must mask | MAY REBUILD | From complete branch records and the canonicalizer. |
| Exact pre-cut distinctions within one proved clean class | MAY FORGET | Only while all contractual futures remain equal. |
| Interrupted ordinary R completion | MAY FORGET | More strongly, it must not remain as an owed reply. |
| Interrupted request identity after SELECT | MAY FORGET | When selected residual, allowance, special phase, and manifest branch fact agree. |
| Pre-A versus post-A service continuation | MAY FORGET | The crossed-A history fact still MUST SURVIVE externally. |
| Unused allowance after FIN | MAY FORGET | FIN forbids later ordinary C. |
| Old/new alternative not selected in one realized branch | MAY FORGET | Only after the complete two-branch conformance record has been produced and retained where required. |

No representation family is selected here. A future representation hypothesis
may be introduced only after reproducing the quotients above, and receives no
credit until the simultaneous attack gate passes.

## 15. Non-scalar total-system accounting

| Dimension | Contractual work and charged location | Present evidence |
|---|---|---|
| Boundary behavior | Exact C/R/A/L/F histories and four projections | Finite specification only |
| Clean continuation | Fourteen classes and exact outputs | Derived prediction |
| Recovery | Application fold, branch map, RESUME, allowance, READY | Derived prediction |
| Controller | Deterministic CLIENT-visible truth table; no A/F visibility | External responsibility charged; no implementation |
| Scheduler | One PUBLIC-prefix/next-crossing bit vector across all paths | Grammar frozen; D/G sizes UNKNOWN |
| Selector | Both labels at every interrupted gap, no clean selector | Privileged responsibility charged |
| Capture | Atomic A fact, isolation from client, retained history | Boundary semantics only; availability/durability untested |
| Manifest | Exact F interleaving, branch records, allowance, outcome evidence | Required; no writer built |
| Termination | FIN-pending versus terminal and terminal recovery | Exact traces specified |
| Specification | Transition, bytes, codec, closures, reason precedence | Must remain an exact authority |
| Canonicalizer | D/G closure, encodings, ordering, projection and dedup | Fully specified; independently unimplemented |
| Cognition | Reproduce the same finite objects without undocumented choices | Charged; no human trial |
| TCB | Runtime through build inputs, peer, selector, oracle, and codec | Unperturbed |
| Runtime and operations | Enumeration cost, cold start, fault injection, monitoring | UNKNOWN |
| Externalization | Controller, peer, manifest, specification availability | No severing experiment |
| Evolution | E0-to-E1 clean and interrupted SELECT semantics | Finite contract only |
| Physical system | Media, power loss, caches, corruption, rollback | Unsupported and unevidenced |

Reducing one representation measure cannot discharge another row. Complexity
moved to the controller, capture peer, selector, manifest, specification,
canonicalizer, build, or human remains charged there.

## 16. Total classifier and unsupported space

The oracle parser applies this reason priority and returns the first matching
typed result:

1. UNSUPPORTED(ENCODING) for a noncanonical binary description;
2. UNSUPPORTED(VIEWER) for an unknown viewer;
3. UNSUPPORTED(PREHISTORY_DEPTH) beyond two;
4. UNSUPPORTED(REQUEST) for any nonalphabet request or empty frame;
5. UNSUPPORTED(ALLOWANCE) beyond three ordinary future occurrences;
6. UNSUPPORTED(CONTROLLER) for an invalid D table;
7. UNSUPPORTED(SCHEDULER) for an invalid G vector;
8. UNSUPPORTED(CRASH) for more than one crash or crash during recovery;
9. UNSUPPORTED(CONCURRENCY) for multiple clients or in-flight concurrency;
10. UNSUPPORTED(SCOPE) for every other outside-domain description.

Within the canonical finite domain, closure evaluation terminates. Outside it,
the classifier returns one reason and no invented trace.

Explicitly unsupported are partial/torn frames; arbitrary authoring,
interpreters, search or navigation infrastructure; more than two pre-cut or
three post-cut messages; randomness; concurrency; more than one crash; crash
during recovery; failed recovery; power loss; corrupt or rolled-back media;
arbitrary migrations; receiver effects; authentication, authorization,
privacy, billing, tenancy, clocks, resource exhaustion, fairness, backup,
restore, and any OS/runtime/hardware property not established by TCB attacks.

Q, X, and K are direct finite operations. No search index, discovery service,
navigation system, arbitrary query language, or implementation is claimed.

## 17. Falsifiable predictions and nonclaims

1. The clean corpus has exactly 157 exact histories and fourteen contractual
   classes with the stated size multiset.
2. It has exactly 2,351 same-class and 9,895 unequal unordered pairs.
3. Every unequal clean pair has a one-message X separator and no empty
   separator.
4. Under the frozen controller and scheduler grammars, no future of allowance
   three and no one-crash branch splits equal clean coordinates.
5. The exact recovery-prefix corpus has 1,208,272 histories in the six stated
   phase totals; clean plus recovery has 1,208,429 cuts.
6. The normalized recovery corpus has exactly 854 conditions.
7. PUBLIC recovery projection has 139 classes; contractual Priv/SELECTOR
   recovery behavior has exactly 315.
8. The 315-class normalized multiplicity histogram is exactly
   263x1, 9x8, 27x9, 14x10, and 2x68.
9. Interrupted AI old/new records differ exactly by SELECT, RESUME, later
   behavior, and semantic application; neither invents the interrupted R.
10. A post-A T crash plus the defined client-blind retry exposes two A
    crossings; a pre-A crash exposes one.
11. FIN-pending emits exactly one STOPPED after READY; terminal recovery emits
    none and ends after READY.
12. Linear probes total 18,965 per clean residual plan and per-gap padded probes
    total 24,906; across 157 clean histories the values are 2,977,505 and
    3,910,242.
13. Independently generated canonical D and G lists and every canonical
    witness byte string will agree across conforming implementations.
14. Every supported complete branch record satisfies all ten Must
    propositions under the stated vacuity rule.

The numeric sizes of D and G, full exact recovery class-size multiset, actual
execution counts, runtime, memory use, realization agreement, DELETE/DERIVE/
RECOMPUTE/EXTERNALIZE/REALIZE/COGNITION/TCB outcomes, storage volume, physical
persistence, power-failure behavior, capture durability, privacy, authority,
and downstream exactly-once effects are UNKNOWN. They are not silently
predicted.
