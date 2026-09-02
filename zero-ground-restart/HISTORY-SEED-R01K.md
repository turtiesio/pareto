# ZERO GROUND R0.1K — Boundary-History Seed

Status: frozen candidate after the self-audit in §11. It is a contract and a
finite breaker corpus, not an implementation design and not a conformance
report.

## 0. Claim boundary

R0.1K classifies finite histories crossing one declared boundary. It does not
classify objects, rows, messages, logs, snapshots, processes, or machines by
assuming that any of those exist inside the subject. An implementation may use
none, one, or many of them.

The candidate claims only the following:

1. a single future-observable relation is sufficient to say when two complete
   boundary histories may be substituted;
2. a verdict can be retained only when the bytes, scope, and finite support for
   that verdict are retained together;
3. the finite corpus in §6 is sufficient to falsify the specific bounded
   obligations declared here; and
4. an implementation that claims the finite interface in §7 must answer every
   request covered there at every reachable history cut covered there.

It does **not** claim that the corpus is complete for arbitrary systems, that a
passing subject is correct outside the declared envelope, that any vocabulary
here is an internal state decomposition, or that a physical action completed.
Physical claims require the evidence in §10.

No percentage, weight, rank, or aggregate score exists in this candidate.

## 1. Classified bytes and the declared boundary

### 1.1 Boundary occurrence

An occurrence is a finite byte string that one of these crosses makes
available:

- a request crosses into the declared subject boundary;
- an answer crosses out;
- a controlled cut such as expiry, crash, recovery, evolution, or termination
  is made observable at that boundary; or
- an independently captured fact is admitted as evidence under a declared
  authority.

A history is a finite ordered sequence of occurrences:

`h = <x0, x1, ..., xn>`.

Order and multiplicity matter. Silence is not an occurrence. A harness may
turn a bounded wait into an explicit `EXPIRE` occurrence, but may not turn it
into an absent request, an empty capture, a rejection, a crash, or a completed
action.

### 1.2 The seal

A persistent classification is a function only of a **seal**, whose canonical
bytes contain all of the following:

- `RULES`: the exact rule bytes used for the classification;
- `DECL`: the boundary, accepted request alphabet, response bounds, history
  bounds used by the experiment, viewers and permissions, specification bytes,
  branch policy, clock authority, recovery rule, terminal rule, completion
  predicate, and claimed realization scope;
- `HISTORY`: the ordered boundary occurrences being classified;
- `EVIDENCE`: inline evidence bytes, their acquisition interval, authority,
  and adjudication rule, or the literal marker `MISSING` for each required
  item;
- `DEPENDENCIES`: every influence on the verdict, with its exact bytes, or the
  literal marker `UNBOUND`;
- `QUESTION`: the exact obligation and quantifier being decided;
- `SUPPORT`: one support form from §4; and
- `SUPERSEDES`: either `NONE` or the digest of an older, immutable seal.

The canonical transport encoding for a seal is deliberately small. Each item
is UTF-8 or opaque bytes preceded by its unsigned 32-bit big-endian byte
length. A sequence is encoded by concatenating its length-prefixed items.
Maps are sequences sorted by the unsigned lexicographic order of their encoded
key bytes. Integers inside text are decimal ASCII without leading zeroes.
Evidence referenced by a digest must also be inline in `EVIDENCE`; a digest or
public name alone is not evidence.

The encoding is a corpus exchange rule. It says nothing about how the subject
stores or computes anything.

If a locale, clock, scheduler, controller, capture source, selector, manifest,
specification, interpreter, canonicalizer, recovery environment, permission
decision, physical adjudicator, or human judgment can change a verdict, its
decisive bytes belong in `DEPENDENCIES` or `EVIDENCE`. If they are absent, that
obligation is `UNKNOWN`. A display label, version word, object identity, or
hash without available bound content is not a substitute.

Consequently, byte-identical seals have byte-identical persistent verdicts. If
two evaluators produce different verdicts from byte-identical seals, at least
one result is not an R0.1K verdict. This is directly falsifiable; see `K-CLOSE`
in §6.7.

### 1.3 Exact prefix difference

For histories `h` and `g`, let `p` be their unique longest common prefix. Write

`h = p · u` and `g = p · v`.

The exact prefix difference is

`PD(h,g) = <encode(p), encode(u), encode(v)>`.

The suffixes `u` and `v` are ordered sequences, may be empty, and are included
as bytes rather than described by prose. A claim that histories “differ at one
cut” is valid only when one suffix is empty and the other contains exactly one
occurrence, or when the seal names the one controlled replacement and includes
both exact one-occurrence suffixes. Set difference, unordered event difference,
and “same except timing” are not exact prefix differences.

For adaptive branches, `PD` is computed for every compared leaf pair after
shared prefixes have been represented once in the prefix trie described in
§4.3. A convenient single path may not stand in for the other branches.

## 2. The one history equivalence

Let `H` be all finite histories accepted or refused at the declared boundary,
including malformed, unauthorized, crashed, recovered, evolving, terminating,
terminal, and future-version histories. Let an experiment be a finite adaptive
tree of boundary requests: its next request may depend on the exact answer bytes
already returned. Requests outside the advertised vocabulary remain experiments
because the decoder has a bounded refusal.

`Trace(h,e)` is the ordered boundary answer tree obtained by starting experiment
`e` after history `h`. It includes explicit refusal, expiry, unknown, evidence
availability, and terminal answers. It includes every declared viewer by making
viewer authority an input occurrence whose authority bytes are in the seal.

R0.1K defines exactly one equivalence over all histories:

`h ≃ g  iff  for every finite adaptive experiment e, Trace(h,e) = Trace(g,e)`.

This is the all-histories, future-observable equivalence. There is no second
equivalence for storage, projection, viewer, version, phase, replay, schedule,
or realization.

Important consequences follow.

- Equal output for one viewer is not `≃`.
- Equal current output is not `≃`.
- Repeated agreement is not `≃`.
- The same public name, version, scheduler, or canonical witness is not `≃`.
- One distinguishing finite continuation proves `h ≄ g`.
- Exhausting only continuations of depth `d` supports the bounded statement
  “no distinguisher through `d`,” not the unqualified statement `h ≃ g`.
- `UNKNOWN` is an observable answer, but matching `UNKNOWN` answers do not prove
  equivalence unless all future experiments are covered.

The relation is semantic at the boundary. It does not require event sourcing,
a journal, a state record, a transition table, or any other storage shape.

## 3. Simultaneous total-system coordinates

Every corpus leaf fixes all coordinates below at once:

`Ω = <viewer, observation, interpretation, authoring, query,
      attempt/application/completion, capture, explanation, evolution,
      crash/recovery, termination, realization-evidence>`.

These are experiment coordinates, not fields or types that an implementation
must possess. A coordinate may be `NOT-REACHED`, `NOT-APPLICABLE`, or `UNKNOWN`
only when that exact value and its derivation are present in the seal. An
omitted coordinate is not a wildcard.

An answer about one coordinate is evaluated with every other coordinate held
at its value in the same leaf. For example, the action answer is not evaluated
under an implicit current specification: the viewer, observation coverage,
authoring specification, evolution position, capture availability, recovery
cut, terminal cut, and physical evidence status travel with it. This prevents
separate “correct” subsystems from composing into an unclassified whole.

The per-coordinate verdict vector is retained. Aggregation never erases it.

## 4. Evidence, continuation, witnesses, and verdicts

### 4.1 Retention is not continuation

For a history `h`, define two mathematical observations:

- `Ret(h)`: the evidence occurrences already captured by the external corpus
  boundary and sealed; and
- `Fut(h)`: the boundary answer trees still permitted after `h`.

Neither is an implementation field. `Ret(h)` may remain available to the audit
boundary when `Fut(h)` permits no further semantic action. Conversely, a
subject may continue while a capture item is unavailable. No rule may infer
one from the other.

In particular, if an observation emits `CHUNK:a` and later emits `EXPIRE`, both
occurrences are members of `Ret(h)`. The continuation may be closed, retryable,
crashed, recovered, or terminal; none of those facts deletes either occurrence.
The correct observation result is “captured prefix `a`; observation expired,”
not “empty,” “complete,” or “nothing happened.”

Crash and evolution never rewrite a seal. New evidence produces a new seal with
`SUPERSEDES` pointing to the earlier one. The earlier verdict remains what it
was.

### 4.2 The only persistent support forms

Every persistent `PASS`, `FAIL`, or `UNKNOWN` has one of these finite supports.

**C — minimized collision.** Two exact history prefixes, their `PD`, the claim
that would merge them, and the shortest admitted continuation that returns
different answer bytes. This normally supports `FAIL`, including a false
identity, false absence, false completion, or non-total interface claim.

**D — derivation.** A finite, replayable derivation whose leaves are byte ranges
inside `RULES`, `DECL`, `HISTORY`, `EVIDENCE`, and `DEPENDENCIES`. Every rule
application names its input ranges. A missing required leaf derives `UNKNOWN`,
not a guessed Boolean. A direct contradiction may derive `FAIL`; a fully
discharged finite obligation may derive `PASS`.

**E — equal-future witness.** A complete finite adaptive continuation tree for
the claimed bound, with every branch and answer byte included, showing equality
at every leaf. Its conclusion is explicitly bounded. It never silently proves
the unbounded `≃` relation.

Self-produced text that merely repeats the answer is not support. A recomputed
answer is not independent evidence. A physical proposition cannot be a leaf of
a derivation unless §10 is satisfied.

Every C, D, and E support is minimized. For D, delete each rule node and each
leaf range in turn; for E, delete each admitted branch and shared prefix node in
turn. If a smaller support still proves the same scoped conclusion, the larger
one is not persistent support.

### 4.3 Branch-aggregate minimization

A witness containing branches is represented as a prefix trie. A shared
occurrence is counted once, not once per leaf. Minimization is lexicographic:

1. number of distinct occurrence nodes in the aggregate prefix tries;
2. number of differing occurrence nodes named by all exact `PD` triples;
3. maximum distinguishing-continuation length;
4. number of viewers;
5. number of realization evidence sets;
6. number of controlled nondeterministic choices;
7. number of varied dependency byte ranges; and
8. number of branch leaves, as a final aggregate tie-breaker.

At each position, deletion is tested across the whole branching witness.
Deleting a shared trie node deletes it from every descendant leaf. Deleting a
branch is also tested. The candidate is minimal only if every lexicographically
smaller aggregate either ceases to establish the proposition or is not admitted
by `DECL`. Minimizing each branch separately and then concatenating the results
does not establish aggregate minimality.

For K/1 the global candidate universe is finite: all prefix tries over the exact
direction-tagged occurrence alphabet in §6.1 with no more than five leaves, six
request occurrences per leaf, forty total occurrences per leaf, two viewers,
and the dependency/realization bounds in §5. Minimality enumerates every member
of that universe that is lexicographically smaller, not merely deletion mutants
of the proposed witness. Whole-trie deletion is a necessary reduction check,
not a proof of global minimum by itself.

For a canonical-witness claim, all minimal witnesses in the finite branch tree
are first retained. If more than one remains, the answer is `NONUNIQUE` unless
the exact tie rule and all its influencing bytes are in `DECL`. The R0.1K corpus
uses `NONUNIQUE`; it makes no uniqueness claim.

### 4.4 Three-valued verdicts and non-masking aggregation

Each obligation has exactly one verdict:

- `PASS`: every finite obligation in its declared scope has positive support;
- `FAIL`: at least one minimized finite counterexample or contradiction exists;
- `UNKNOWN`: no counterexample is established, but a required branch, bound,
  authority, dependency, or evidence item is missing or not finitely closed.

For a finite carrier set `K` and predicate `q`:

- `MAY(q)` is true with one positive carrier witness; false only when every
  carrier is negatively decided; otherwise it is `UNKNOWN`.
- `MUST(q)` is false with one negative carrier counterexample; true only when
  every carrier is positively decided; otherwise it is `UNKNOWN`.
- an empty set makes `MAY(q)` false. Formal vacuity, if requested, is reported
  as `VACUOUS`, never as an operational guarantee and never with an invented
  carrier.

The aggregate over obligations or cases is deterministic and unweighted:

1. if any member is `FAIL`, the aggregate is `FAIL` and retains every minimized
   failing member;
2. otherwise, if any member is `UNKNOWN`, the aggregate is `UNKNOWN` and retains
   each missing obligation;
3. otherwise it is `PASS`.

Thus an unrelated `UNKNOWN` can never mask a finite counterexample. Nor may a
`FAIL` be averaged away by passes.

`UNKNOWN` is immutable in its seal. Later evidence may create a superseding
seal with a different verdict, but recovery, repetition, majority agreement,
expiry, silence, or an unrelated success cannot promote the original
`UNKNOWN`. Unknown stays unknown.

## 5. The finite K/1 declaration

The corpus declaration embedded in every K/1 seal fixes this envelope.

| Item | K/1 value |
|---|---|
| viewers | `audit` and `limited` |
| versions | exact inline specifications `s0` and `s1` |
| observations | exactly one of seven sequences: `a+EXPIRE`, `b+EXPIRE`, `a+b+EXPIRE`, `n+EXPIRE`, empty+`EXPIRE`, empty+`UNAVAILABLE`, or `a+COMPLETE` |
| viewer rule | `audit` may see exact tokens and phase cuts; `limited` sees only authorized generic outcomes |
| authored requests | one request `R`, authored under the interpretation version named in its answer |
| carrier branches | exactly five end-to-end leaves: `a`, `b`, `ab`, `n`, `u`; query selectors may choose the full set, the empty set, or singleton `a` for the explicit breakers in §7.3 |
| carrier depth | at most six delivered request occurrences after the common query root; controlled answers and cuts do not consume request depth |
| action phases admitted | no request, requested, denied-before-occurrence, occurred, captured, applied, application-unresolved-at-missing-capture, and completion-evidence-expired |
| physical completion | no positive or negative physical completion claim in the uninstantiated corpus |
| evolution | at most one request from `s0` to `s1`; application is an explicit occurrence |
| crash/recovery | at most one controlled crash and one recovery request per leaf |
| termination | one request, one application occurrence, one boundary-terminal occurrence, then bounded post-terminal probes |
| request size | at most 256 octets; the decoder reads at most 257 before `OVERSIZE` |
| ordinary answer bound | at most three answer occurrences and at most three declared driver-progress steps after delivery; otherwise the harness emits `EXPIRE:operation` |
| witness future bound | at most two adaptive requests per collision or equal-future witness |
| trace size | at most 40 boundary occurrences per corpus leaf |
| realization scope | abstract boundary only unless a seal satisfies §10 |

The exact `s0` rule bytes say: token `a` or token `b` independently authorizes
the same authored request `R@s0`; token `n` authorizes none; an unavailable
token yields `UNKNOWN`. The exact `s1` rule bytes change the spelling of new
authorizations but say that already-authored `R@s0` retains its `s0` meaning.
An unqualified interpretation query is refused as `TIME-SCOPE-REQUIRED`.

The exact recovery rule says that a captured occurred-but-not-applied attempt
may resume once after recovery without minting a second occurrence; a captured
applied attempt may not be applied again; and a missing application cut remains
unknown. This is a boundary continuation rule, not a claim about stored phase.

### 5.1 Literal declaration payload

`DECL:K/1` is one occurrence whose payload is the canonical map encoding from
§1.2 of the following exact ASCII key/value pairs. The displayed quotes are not
part of the value.

```text
id="ZERO-GROUND-K/1"
viewer.audit="tokens,ordered-cuts,evidence-bytes,dependency-status"
viewer.limited="generic-result,no-token-identity,no-evidence-identity"
spec.s0="a=>grant-a;b=>grant-b;n=>no-grant;grant-a|grant-b=>AUTHOR:R@s0;opaque=>UNKNOWN"
spec.s1="a1=>grant-a1;b1=>grant-b1;n=>no-grant;R@s0=>meaning:s0;unqualified-time=>TIME-SCOPE-REQUIRED"
observation.sequences="a+EXPIRE,b+EXPIRE,a+b+EXPIRE,n+EXPIRE,EXPIRE,UNAVAILABLE,a+COMPLETE"
branch.full="a,b,ab,n,u"
branch.query-selectors="full,empty,singleton-a"
depth.unit="delivered-request-occurrence"
depth.full="6"
answer.progress-source="corpus-driver"
answer.progress-limit="3"
answer.occurrence-limit="3"
evidence.rule="unavailable-authority=>UNKNOWN;absence-without-closed-capture=>UNKNOWN"
recovery="occurred+captured=>resume-once;applied=>no-reapply;missing-apply-capture=>UNKNOWN"
terminal="TERM-DONE=>audit-only;semantic-action=>TERMINAL-REFUSAL"
completion.predicate="external-condition-phi"
completion.evidence="MISSING"
canonical-witness="NONUNIQUE"
realization="abstract-boundary-only"
```

The permission values are exhaustive. The specifications are content, not
names resolved elsewhere. The corpus driver's progress records and every
dependency status are also inline in a seal. If an implementation needs a
different rule byte, it is a different declaration rather than an ambient
override of K/1.

The branch predicate is:

`q := the application fact Apply(R@s0) occurred before boundary termination`.

An authorized `APPLIED:R@s0` boundary occurrence is finite positive evidence
for `q`. A captured denial in a declared closed carrier is finite negative
evidence. If the capture authority at the application cut is missing, absence
of `APPLIED` is not negative evidence and `q` is `UNKNOWN`. This is a semantic
fact adjudicated from boundary evidence, not external physical completion.

The declared carrier outcomes are `a:+`, `b:+`, `ab:+`, `n:-`, and `u:?`.
The `u` branch contains an action occurrence followed by a crash at the
application cut with the application capture marked `MISSING`. Therefore its
truth value is `UNKNOWN`; it is not negative.

## 6. Small bounded end-to-end corpus

### 6.1 Occurrence notation

Names below denote exact ASCII occurrence payloads in the length-prefixed
encoding from §1.2. A colon separates fixed words from bound values. A script
operator expands to the listed occurrences; it is not an implementation API.

Every abbreviation expands to one of four direction-tagged payload forms:

```text
REQ|<viewer>|<scope>|<operation>|<arguments>
ANS|<viewer>|<scope>|<operation>|<status>|<payload>
CUT|<authority>|<kind>|<payload>
EVD|<authority>|<kind>|<payload>
```

The tables use `audit` unless they explicitly say `limited`. `scope` is `s0`
until an `EVOLVED:s1` cut and `s1` afterward; an authored token additionally
retains its literal `R@s0`. Request-vocabulary words expand to `REQ`; words
`INTERPRETED`, `AUTHORED`, `REJECTED`, `TRUE`, `FALSE`, `UNKNOWN`, `CAPTURED`,
`EXPLAINED`, `RECOVERED`, `DENIED-BEFORE-OCCURRENCE`, and
`TERMINAL-REFUSAL` expand to `ANS` for their preceding request. `CHUNK` and a
terminal observation `COMPLETE`/`EXPIRE`/`UNAVAILABLE` also expand to `ANS` for
the unmatched observation request. `OCCURRED`, `APPLIED`, `CRASH`, `EVOLVED`,
`TERM-APPLIED`, and `TERM-DONE` expand to `CUT`. A completion-observer
`EXPIRE` with no unmatched request is `CUT|completion-observer|EXPIRE|...`.
Missing or admitted independent capture facts expand to `EVD`. The operation
and payload are the exact colon-separated words shown in the tables.

For example, the first two observation abbreviations in leaf `a` are exactly:

```text
REQ|audit|s0|OBSERVE|-
ANS|audit|s0|OBSERVE|CHUNK|a
```

`DECL:K/1` expands to `CUT|corpus-driver|DECL|` followed by the canonical map
bytes in §5.1. A seal containing an untagged direction, an omitted viewer, an
omitted scope, or prose such as “current version” is malformed.

The request vocabulary is:

`OBSERVE, INTERPRET, AUTHOR, QUERY, ATTEMPT, CAPTURE, EXPLAIN, EVOLVE, RECOVER,
TERMINATE`.

Non-request answer, cut, and evidence words are:

`CHUNK, COMPLETE, EXPIRE, UNAVAILABLE, OCCURRED, CAPTURED, APPLIED,
APPLICATION-UNRESOLVED, CRASH, RECOVERED, EVOLVED, TERM-APPLIED, TERM-DONE`.

Every answer carries its viewer and version scope. Tables abbreviate those
bytes only for readability; a seal may not omit them.

### 6.2 Common observation/interpretation/authoring prefix

Each leaf begins with the same `DECL:K/1` and the common queries in §6.3, then
one of these exact bounded prefixes.

| leaf | observation occurrences | interpretation | authoring |
|---|---|---|---|
| `a` | `OBSERVE`, `CHUNK:a`, `EXPIRE` | `INTERPRET:s0:a`, `INTERPRETED:grant-a:partial-expired` | `AUTHOR:R`, `AUTHORED:R@s0` |
| `b` | `OBSERVE`, `CHUNK:b`, `EXPIRE` | `INTERPRET:s0:b`, `INTERPRETED:grant-b:partial-expired` | `AUTHOR:R`, `AUTHORED:R@s0` |
| `ab` | `OBSERVE`, `CHUNK:a`, `CHUNK:b`, `EXPIRE` | `INTERPRET:s0:a+b`, `INTERPRETED:grant-a+grant-b:partial-expired` | `AUTHOR:R`, `AUTHORED:R@s0` |
| `n` | `OBSERVE`, `CHUNK:n`, `EXPIRE` | `INTERPRET:s0:n`, `INTERPRETED:no-grant:partial-expired` | `AUTHOR:R`, `REJECTED:no-grant` |
| `u` | `OBSERVE`, `CHUNK:a`, `EXPIRE` plus `EVIDENCE:observation-authority:MISSING` | `INTERPRET:s0:a`, `UNKNOWN:observation-authority` | `AUTHOR:R`, `UNKNOWN:authoring-basis` |

Every row contains both the captured prefix and expiry. `partial-expired` does
not mean that token interpretation is false; it limits claims about everything
outside the captured prefix. The adjacent no-chunk mutant is `OBSERVE, EXPIRE`
and derives no token.

### 6.3 Query over all five carrier histories

Immediately after the common `DECL:K/1`, before any leaf-specific observation,
the corpus asks the same two queries over continuations from that one exact
root history. The exact carrier set is `{a,b,ab,n,u}`:

1. `QUERY:MAY:q:depth=6` returns `TRUE:witness=a`;
2. `QUERY:MUST:q:depth=6` returns `FALSE:counterexample=n`.

Depth is the number of delivered request occurrences after the query root and
before the proposition is decided. It counts `OBSERVE`, `INTERPRET`, `AUTHOR`,
`EVOLVE`, `ATTEMPT`, `CAPTURE`, and `RECOVER` when present. It does not count
answers or controlled cuts, though those remain in the witness. The first
positive depths are: `a=6`, `b=6`, and `ab=5`; `n` is negatively closed by
depth six; `u` is unresolved at depth six. The query request that names the
bound is not counted inside its own future.

The `u:?` carrier is retained in both evidence carriers. It does not mask the
positive witness for `MAY` and does not mask the negative counterexample for
`MUST`. If `a` were removed, `b` would still witness MAY. If `n` were removed,
MUST would become `UNKNOWN`, not true, because `u` remains. These are derivable
predictions, not scores.

For the proposition `why-admitted(ab)`, the declared candidate authorization
witnesses have exact decisive leaves `<CHUNK:a,OCCURRED:R>` and
`<CHUNK:b,OCCURRED:R>`, with the K/1 rule bytes and evidence authority as shared
derivation leaves. The token supplies an authorization basis; `OCCURRED`
establishes admission of this attempt. The aggregate candidate contains shared
rule/evidence leaves once and both branch leaves. Deleting the sole token from
the single-token branch reaches the exact no-chunk expiry mutant, whose basis is
unknown; deleting the occurrence leaves no admitted attempt; deleting `a` from
`ab` leaves the independent `b` candidate, and deleting `b` leaves the
independent `a` candidate. These are necessary irreducibility checks. A
persistent result is issued only after the runner enumerates every
lexicographically smaller trie in the finite universe from §4.3. If both
candidates remain globally minimal, the answer is
`WITNESSES:[a,b]:NONUNIQUE`; otherwise the result follows the smaller witness,
or is `UNKNOWN` when enumeration is incomplete. A process-local tie preference
cannot invent a canonical winner.

### 6.4 Action, capture, evolution, and recovery suffixes

The branches then execute these ordered suffixes. `X` is the full audit
explanation request and answer appropriate to the prefix. Each branch later
uses the common terminal tail in §6.5.

| leaf | ordered suffix before `X` | boundary decision for `q` |
|---|---|---|
| `a` | `ATTEMPT:R@s0`, `OCCURRED:R`, `CAPTURE`, `CAPTURED:attempt-prefix`, `CRASH:after-capture-before-apply-evidence`, `RECOVER`, `RECOVERED:captured-application-not-yet-evidenced`, `APPLIED:R@s0`, `EXPIRE:completion-observation`, `EVOLVE:s1`, `EVOLVED:s1`, `QUERY:q`, `TRUE:applied` | true by the explicit `APPLIED` occurrence; physical completion unknown |
| `b` | `EVOLVE:s1`, `EVOLVED:s1`, `ATTEMPT:R@s0`, `OCCURRED:R`, `CAPTURE`, `CAPTURED:attempt-prefix`, `APPLIED:R@s0`, `CRASH:after-apply-before-completion-evidence`, `RECOVER`, `RECOVERED:applied-completion-evidence-unavailable`, `EXPIRE:completion-observation`, `QUERY:q`, `TRUE:applied` | true; already-authored meaning is bound to `s0`; physical completion unknown |
| `ab` | `ATTEMPT:R@s0`, `OCCURRED:R`, `CAPTURE`, `CAPTURED:attempt-prefix`, `APPLIED:R@s0`, `EXPIRE:completion-observation`, `EVOLVE:s1`, `EVOLVED:s1`, `CRASH:after-apply-and-evolution`, `RECOVER`, `RECOVERED:applied-completion-evidence-unavailable`, `QUERY:q`, `TRUE:applied` | true; two authorization witnesses remain nonunique; physical completion unknown |
| `n` | `EVOLVE:s1`, `EVOLVED:s1`, `ATTEMPT:R@s0`, `DENIED-BEFORE-OCCURRENCE:no-grant`, `CAPTURE`, `CAPTURED:request-and-denial`, `CRASH:after-denial`, `RECOVER`, `RECOVERED:no-occurrence`, `QUERY:q`, `FALSE:no-application` | false by the captured denial and absence of any admitted occurrence in this closed branch |
| `u` | `ATTEMPT:R@s0`, `OCCURRED:R`, `CAPTURE`, `CAPTURED:attempt-prefix`, `CRASH:at-apply-cut`, `RECOVER`, `RECOVERED:application-evidence-missing`, `APPLICATION-UNRESOLVED:capture-missing`, `EVOLVE:s1`, `EVOLVED:s1`, `QUERY:q`, `UNKNOWN:application-evidence` | unknown; occurrence is not application and missing capture is not non-application |

`X` expands to four exact occurrences: an `audit` explanation request and
answer followed by a `limited` explanation request and answer. The audit
payload is respectively `q=true;support=APPLIED`, `q=false;support=DENIAL`, or
`q=UNKNOWN;support=MISSING-APPLY-CAPTURE`. The limited payload is respectively
`applied;basis=HIDDEN`, `not-applied;basis=HIDDEN`, or
`attempted;application=UNKNOWN`. It never includes token `a` or `b`, and it
never asserts that the full histories are equal.

The `a`, `b`, and `ab` leaves deliberately expire while trying to observe the
external completion condition. That establishes only that the prefix was
captured and the observation bound expired. Their completion verdict remains
`UNKNOWN`. The application proposition `q` remains separately established.

### 6.5 Termination and retained post-terminal evidence

Every branch ends with the exact tail:

`TERMINATE, TERM-APPLIED, TERM-DONE,
 CAPTURE, CAPTURED:retained,
 EXPLAIN:terminal, EXPLAINED:terminal,
 ATTEMPT:R@s0, TERMINAL-REFUSAL`.

`TERM-DONE` means only that this boundary entered its declared terminal
semantics. It does not claim that a process halted, power disappeared, a packet
was delivered, or physical motion ceased.

The post-terminal `CAPTURED:retained` answer includes the original observation
chunks **and** their `EXPIRE` marker, plus available attempt/capture evidence.
The post-terminal explanation is bounded. The final action request is refused
and itself remains observable. No semantic action continuation occurs after
`TERM-DONE`.

### 6.6 The exact finite leaf set and dimension coverage

The end-to-end leaf set is exactly `{a,b,ab,n,u}`. The collision audit also
uses exact prefix cuts, two one-occurrence observation mutants
`OBSERVE,EXPIRE` and `OBSERVE,UNAVAILABLE`, one completed-observation mutant
`OBSERVE,CHUNK:a,COMPLETE`, and the capture mutant
`CAPTURE,UNAVAILABLE:capture`. These mutants are not additional carrier leaves
and cannot affect MAY/MUST. The finite set is not a sample from a larger
claimed branch domain.

| leaf | obs | interpretation/authoring | MAY/MUST | action/capture | evolution | crash/recovery | terminal | physical completion |
|---|---|---|---|---|---|---|---|---|
| `a` | prefix+expiry | grant-a / authored | T/F | occur, capture, recover, apply | after apply | before apply | done+probes | unknown |
| `b` | prefix+expiry | grant-b / authored | T/F | occur, capture, apply | before attempt | after apply | done+probes | unknown |
| `ab` | two prefixes+expiry | two grants / authored | T/F | occur, capture, apply | after apply | after answer | done+probes | unknown |
| `n` | prefix+expiry | no grant / rejected | T/F | denied and captured | before attempt | after denial | done+probes | not applicable |
| `u` | prefix+expiry+missing authority | unknown / unknown | T/F | occur, capture prefix, apply unknown | after recovery | at apply cut | done+probes | unknown |

No cell is implicit. The same leaves jointly exercise observation,
interpretation, authoring, querying, action attempt and capture, explanation,
evolution, crash/recovery, and termination.

After direction expansion and both viewer explanations, the exact occurrence
counts are `a=38`, `b=38`, `ab=39`, `n=36`, and `u=38`. Each is within the
declared forty-occurrence limit.

The lower-bound defense for five carriers is structural: two different
positive leaves and their combined leaf are needed to expose branching-witness
nonuniqueness; a decided negative leaf is needed to refute `MUST`; and a
distinct unresolved leaf is needed to show that this counterexample survives
an unrelated `UNKNOWN`. Sharing the prefixes and the terminal tail avoids
duplicating further histories.

### 6.7 `K-CLOSE`: unbound-context closure experiment

Run the classifier twice on one byte-identical seal while changing exactly one
process-external influence, such as locale, default specification search path,
clock setting, map iteration order, or canonicalizer preference. The result is
conditional on the seal itself:

- if the influence is bound in `DEPENDENCIES`, verdict and support bytes are
  identical in both runs; and
- if the influence is marked `UNBOUND`, both runs return exactly
  `UNKNOWN:UNBOUND-DEPENDENCY`.

Different persistent verdicts are a collision and a `FAIL` of byte closure.
The changed process context may be included in the *collision witness* that
documents the faulty evaluators, but it may not retroactively become an
unstated input to either classified seal.

## 7. Total request routing, with an exact withdrawal

### 7.1 Scope of the interface claim

R0.1K claims one finite interface: classify a request payload against a K/1
history prefix. It claims no network availability, UI route, RPC endpoint,
storage method, or general action vocabulary.

The decoder is total for delivered bytes: at most 256 octets are decoded; byte
257 produces `OVERSIZE`; a nonconforming payload produces `MALFORMED`; a
well-formed unknown operation produces `UNSUPPORTED`. Delivery itself and the
elapsed-time source require evidence and are not physically guaranteed here.

For the ten well-formed request classes, reachable prefixes are partitioned by
the first matching history predicate in this order:

1. `terminal`: contains `TERM-DONE`;
2. `term-applied`: contains `TERM-APPLIED` after the last recovery but no
   `TERM-DONE`;
3. `term-requested`: contains the corresponding termination request but no
   `TERM-APPLIED`;
4. `recovery-pending`: the most recent `CRASH` has no following `RECOVERED` and
   a following `RECOVER` request has no terminal recovery answer;
5. `crashed`: the most recent `CRASH` has no following `RECOVERED` and no
   unanswered `RECOVER`, regardless of intervening audit requests;
6. `evolution-pending`: contains an evolution request with no `EVOLVED`;
7. `action-applied`: the latest attempt has `APPLIED` but its bounded completion
   observation has no terminal marker;
8. `action-occurred`: the latest attempt has `OCCURRED` but no `APPLIED`,
   captured denial, or `APPLICATION-UNRESOLVED` close;
9. `action-requested`: the latest attempt request has neither `OCCURRED` nor a
   captured denial;
10. `observation-open`: the latest observation request has no `COMPLETE`,
   `EXPIRE`, or `UNAVAILABLE`, with zero, one, or two chunks;
11. `synchronous-pending`: the latest `INTERPRET`, `AUTHOR`, `QUERY`, `CAPTURE`,
    or `EXPLAIN` request has no corresponding terminal answer; and
12. `open`: every other admitted prefix, including recovered prefixes.

These predicates label whole history cuts solely to make coverage auditable.
They do not infer an internal state variable or phase type.

### 7.2 Coverage matrix

The following abbreviations are complete answer constructors:

- `A(h,r)`: a viewer-scoped audit answer derived from retained bytes, possibly
  `UNKNOWN` with its first missing evidence item;
- `N(h,r)`: the normal bounded operation answer from the inline K/1 rules;
- `BUSY:x`, `CRASHED`, `TERMINATING`, and `TERMINAL` are bounded refusals that
  also retain the request occurrence;
- `ALREADY:x` is a bounded idempotent answer, not a new semantic occurrence;
- `RECOVERED` appends the recovery result; `NOT-CRASHED` does not.

Constructor selection is itself total and byte-bound. After the decoder cases,
an unauthorized viewer gets `DENIED`; a version other than inline `s0` or `s1`
gets `UNSUPPORTED-VERSION`; and a known operation with arguments outside K/1
gets `OUT-OF-ENVELOPE`. For admitted arguments, `N(h,r)` is the unique result
specified by the exact K/1 branch bytes; if no transition is listed it is
`REFUSED:NOT-ADMITTED`. `A(h,r)` returns one authorized `CAPTURED` or audit
answer, or the first missing-evidence `UNKNOWN`; only `OBSERVE` uses the seven
multi-occurrence sequences declared in §5. `EXPIRE:operation` is emitted by the
harness, not invented by `A`. `A` audits an already sealed history and never
creates a post-terminal semantic action. Recovery returns `RECOVERED` exactly
when bound recovery evidence satisfies the inline rule and otherwise returns
the named `UNKNOWN`.

The progress bound is operational rather than a count of output items. A
delivered request starts at driver step zero. The bound authority named in the
seal advances at most three controlled progress opportunities. A terminal
answer at or before step three closes the operation; otherwise the harness
appends `EXPIRE:operation` at step three while retaining every earlier answer
prefix. If the progress authority cannot be evidenced, the timing obligation is
`UNKNOWN`, even though the captured prefix remains evidence. No wall-clock or
network-liveness claim is inferred.

| history predicate | OBSERVE | INTERPRET | AUTHOR | QUERY | ATTEMPT | CAPTURE | EXPLAIN | EVOLVE | RECOVER | TERMINATE |
|---|---|---|---|---|---|---|---|---|---|---|
| `open` | `N` | `N` | `N` | `N` | `N` | `A` | `A` | `N` | `NOT-CRASHED` | `N` |
| `observation-open` | `N:resume` | `A` | `BUSY:observation` | `A` | `BUSY:observation` | `A` | `A` | `BUSY:observation` | `NOT-CRASHED` | `BUSY:observation` |
| `action-occurred` | `A` | `A` | `BUSY:action` | `A` | `BUSY:action` | `A` | `A` | `BUSY:action` | `NOT-CRASHED` | `BUSY:action` |
| `action-applied` | `A` | `A` | `BUSY:completion` | `A` | `BUSY:completion` | `A` | `A` | `BUSY:completion` | `NOT-CRASHED` | `BUSY:completion` |
| `action-requested` | `A` | `A` | `BUSY:action-request` | `A` | `BUSY:action-request` | `A` | `A` | `BUSY:action-request` | `NOT-CRASHED` | `BUSY:action-request` |
| `evolution-pending` | `A` | `A` | `BUSY:evolution` | `A` | `BUSY:evolution` | `A` | `A` | `ALREADY:evolving` | `NOT-CRASHED` | `BUSY:evolution` |
| `crashed` | `A` | `A` | `CRASHED` | `A` | `CRASHED` | `A` | `A` | `CRASHED` | `RECOVERED` or `UNKNOWN:recovery-evidence` | `CRASHED` |
| `recovery-pending` | `A` | `A` | `CRASHED` | `A` | `CRASHED` | `A` | `A` | `CRASHED` | `BUSY:recovery` | `CRASHED` |
| `term-requested` | `A` | `A` | `TERMINATING` | `A` | `TERMINATING` | `A` | `A` | `TERMINATING` | `NOT-CRASHED` | `ALREADY:terminating` |
| `term-applied` | `A` | `A` | `TERMINATING` | `A` | `TERMINATING` | `A` | `A` | `TERMINATING` | `TERMINATING` | `ALREADY:applied` |
| `terminal` | `A` | `A` | `TERMINAL` | `A` | `TERMINAL` | `A` | `A` | `TERMINAL` | `TERMINAL` | `ALREADY:terminal` |
| `synchronous-pending` | `BUSY:request` | `BUSY:request` | `BUSY:request` | `BUSY:request` | `BUSY:request` | `A` | `A` | `BUSY:request` | `NOT-CRASHED` | `BUSY:request` |

Every reachable predicate/request pair has a result constructor. `A` is not a
promise that evidence exists; it is total because missing evidence returns an
explicit bounded `UNKNOWN`.

Controlled `CRASH`, `TERM-APPLIED`, `TERM-DONE`, `EVOLVED`, `APPLIED`, and
observation terminal markers are harness occurrences, not routed requests.
The matrix therefore makes no routing claim for them. Request classes beyond
the ten named classes receive `UNSUPPORTED`; semantic support for them is
expressly withdrawn.

### 7.3 Finite decoder and depth breakers

For every claimed operation, the router audit includes delivered payloads of
length zero, one, exactly 256, and 257 octets; one malformed encoding; one
well-formed unknown operation; one unknown version; one unauthorized viewer;
and the same valid request at crashed and boundary-terminal prefixes. These are
finite decoder cases, not sampled claims. The audit also withholds a terminal
subject answer once for each of the ten operations, forcing the driver-step
three `EXPIRE:operation`; the observation case first emits its declared chunk.

The query audit additionally includes an empty carrier set and a singleton
`a` carrier cut immediately before its recovery request. On the empty set,
`MAY(q)` is false, `MUST(q)` is reported as `VACUOUS`, and no carrier is
offered; the matched request for `MUST(not-q)` is also `VACUOUS`, so neither is
presented as an operational guarantee. For the singleton recovery carrier,
`MAY(q)` is false through request depth five and true at depths six and seven,
when recovery admits the explicit length-six `APPLIED:R@s0` continuation. A
witness longer than the asked depth is a finite failure.

## 8. Complete reachable phase-collision ledger

### 8.1 Ledger rule

Let `P_K` be the exact finite set obtained by expanding all five direction-tagged
scripts, the finite mutants in §§6.6 and 7.3, and the prefix after every single
occurrence. Shared prefixes occur once. Let `Pairs(X)` mean every unordered pair
of distinct members of finite set `X`.

The master collision ledger is the following intensional finite set:

`L_K = { <h,g,PD(h,g),c,Trace(h,c),Trace(g,c)> |
         {h,g} in Pairs(P_K),
         c is the shortest admitted continuation of at most two requests
         whose answer trees differ }`.

Every distinct K/1 prefix is available to `audit` through the sealed-history
`CAPTURE` operation, so a one-request capture distinguishes different retained
occurrence bytes. The second request in the bound is reserved for the named
semantic discriminator when captured projections are intentionally equal. If
neither request distinguishes a pair, the pair receives a minimized bounded E
witness instead of being silently merged. This bounded ledger does not assert
the unbounded `≃` relation.

For each phase family below, the named labels denote whole reachable history
prefixes. The family index contains every member of `Pairs(S)`, and `L_K`
additionally contains every future-distinct pair assigned the same label. Thus
a phase label cannot hide different crash placements, branch histories, or
viewer-authorized futures.

For a pair, the stored collision witness contains both exact histories, their
`PD`, and the first discriminator shown below. The discriminator is asked as
`audit`. If a supposedly merged pair returns the same answer, the next request
shown after `/` is used. If all declared futures are equal, an E witness
replaces the collision and records only bounded equality. No implementation
field or type is inferred from a ledger label.

### 8.2 Exhaustive families in K/1

| family | complete reachable label set `S` | first finite discriminator for every forced pair |
|---|---|---|
| observation | `{none, requested, chunk, empty+expiry, chunk+expiry, chunk+complete, unavailable}` | `CAPTURE / QUERY:observation-completeness` |
| interpretation | `{not-requested, requested, value, no-grant, unknown}` | `EXPLAIN:interpretation / AUTHOR:R` |
| authoring | `{not-requested, requested, authored, rejected, unknown}` | `EXPLAIN:authoring / ATTEMPT:R` |
| query | `{not-requested, requested, true, false, unknown}` | `QUERY:witness / QUERY:counterexample` |
| action | `{not-requested, requested, denied-before-occurrence, occurred, captured, applied, application-unresolved, completion-expired}` | `EXPLAIN:action-cuts / QUERY:q` |
| capture | `{not-requested, requested, prefix-returned, unavailable}` | `CAPTURE / EXPLAIN:capture-coverage` |
| response closure | `{pending@op, answered@op, expired@op | op ∈ {OBSERVE, INTERPRET, AUTHOR, QUERY, ATTEMPT, CAPTURE, EXPLAIN, EVOLVE, RECOVER, TERMINATE}}` | `EXPLAIN:operation-result / CAPTURE` |
| evolution | `{s0} ∪ {requested@p, s1-applied@p | p ∈ {before-attempt, after-application, after-application-unresolved}}` | `QUERY:meaning-time / ATTEMPT:R@s0` |
| recovery | `{live-at-cut} ∪ {crashed@p, recovery-requested@p, recovered@p | p ∈ {captured, applied, applied+evolved, denied, apply-evidence-missing}}` | `RECOVER / EXPLAIN:recovery` |
| explanation | `{not-requested, requested, answered, unknown}` | `EXPLAIN:repeat / CAPTURE:support` |
| termination | `{live, requested, applied, boundary-terminal}` | `ATTEMPT:R / QUERY:terminal-cut` |

The sets are complete for the declared corpus. For example, the action row
expands to all twenty-eight pairs, including not-requested/requested,
requested/denied, denied/applied,
denied/completion-expired, occurred/applied, occurred/completion-expired,
captured/applied, and applied/completion-expired—not just consecutive cuts. A
full-audit explanation returns the last established boundary occurrence and any
missing next evidence; therefore each future-forced distinction has a
one-request witness.

A physically established `completed` label is intentionally absent. It becomes
reachable only in a seal containing §10 evidence. Such an instantiated corpus
must extend the action set with `completed`, add all eight new unordered pairs to
the ledger, and rerun the router audit before claiming coverage. Merely adding a
field called `completed` is neither required nor sufficient.

### 8.3 Completeness check

The ledger-generation check is finite:

1. expand the five scripts, every controlled prefix cut, and every finite
   mutant to obtain `P_K`;
2. enumerate `Pairs(P_K)` and record exact `PD` bytes for every pair;
3. run `audit` capture and, where necessary, the stated semantic discriminator
   from both prefixes within two requests;
4. populate `L_K` with a minimized C witness for unequal futures or retain an E
   witness for the exact bounded equal tree;
5. assign each prefix to every applicable family label using only occurrence
   bytes and enumerate `Pairs(S)` for each family; and
6. fail the audit if a reachable pair has neither C nor E support, or if two
   future-distinct prefixes remain hidden under one unindexed label.

This check makes “all phase distinctions” an enumerable claim for K/1 rather
than an intuition. A new reachable label changes `S` and invalidates the frozen
ledger until its pairs are supplied.

## 9. Verdict ledger for the bounded corpus

This document does not contain execution evidence from a subject. It therefore
does not declare that a subject passes. It declares the expected classification
rules below; a run fills their evidence slots.

| obligation | expected support and result when instantiated |
|---|---|
| partial observation | D: `CHUNK` and `EXPIRE` byte ranges derive `prefix-retained + expired`; deleting either range changes the result |
| full-history absence after empty output | D: cannot be derived; result `UNKNOWN` unless a closed capture authority is bound |
| MAY over five carriers | D: executed `a` (or `b`) derives true |
| MUST over five carriers | C/D: executed `n` is a finite negative counterexample, so false even while `u` is unknown |
| application on `a`, `b`, `ab` | D: exact `APPLIED` occurrence derives true for boundary proposition `q` |
| application on `n` | D: closed declared branch plus captured denial derives false |
| application on `u` | D: missing apply-cut evidence derives `UNKNOWN` |
| physical completion | D: `MISSING` physical evidence derives `UNKNOWN` |
| authored-version meaning | D/E: inline `s0`/`s1` rules plus bounded `a`/`b` executions support the scoped result; no whole-history equivalence is claimed |
| nonunique witness on `ab` | aggregate D: after exhaustive enumeration of every smaller admissible trie, the `a` and `b` branch tries each suffice; result `NONUNIQUE`, otherwise `UNKNOWN` |
| recovery | C/D: each adjacent crash cut must agree with its post-recovery explanation; missing recovery adjudication is `UNKNOWN` |
| terminal behavior | C/D: `TERM-DONE` followed by audit answers and action refusal establishes only boundary-terminal semantics |
| byte closure | C: two different verdicts for one identical seal are a minimized collision |
| total router | D plus exhaustive finite matrix execution; one hang, omitted cell, or contradictory follow-up is `FAIL` |

A runner reports the entire vector. It then applies §4.4. For example, an
incorrect `MUST(q)=true` answer is a suite `FAIL` because the sealed `n`
counterexample executes negatively, even if the unrelated physical-completion
obligation is `UNKNOWN`. The physical unknown remains visible but cannot hide
the counterexample.

## 10. Physical realization rule

R0.1K makes no physical realization claim for its uninstantiated scripts.
Words such as occurrence, application, crash, recovery, and terminal refer to
declared boundary cuts unless a seal additionally contains all of:

1. the exact realization description bytes, not only a product or version
   name;
2. the external completion or failure predicate and observation interval;
3. raw, inline evidence from an independently declared physical observer;
4. the clock/bound evidence used to close that interval;
5. the finite derivation from raw evidence to the physical proposition;
6. the permissions and projection under which the evidence is shown;
7. every shared trusted influence between subject answer and adjudicator; and
8. realization-specific crash, recovery, and terminal evidence when those
   physical properties are claimed.

Missing any item yields `UNKNOWN` for the physical proposition. Evidence from a
simulator cannot establish a physical fact in a different realization. Evidence
from one machine cannot be transferred by shared name to another. Agreement
between an answer and a validator that share an undeclared influence is not
independence.

If two materially unlike realizations are claimed equivalent, each supplies
its own evidence and the claimed scope is limited to the boundary properties
actually compared. Otherwise cross-realization equivalence remains `UNKNOWN`.

### 10.1 Precise nonclaims

The finite corpus does not acquire coverage by implication. These wider claims
are withdrawn:

| topic | K/1 scope |
|---|---|
| permission history | two fixed viewer authorities; no permission-change semantics |
| determinism, replay, scheduler identity | no claim; the five branch labels are explicit finite alternatives, not samples or schedules |
| adaptive controller or selector identity | no history-determined choice claim unless its exact context is bound in `DEPENDENCIES` |
| failed and no-op action classes | not admitted; only the action cuts in §5 are covered |
| consumable capability or crash-counted remaining depth | no such capability exists in K/1; query depth is only the explicit request count |
| irrecoverable or physically terminal crash | no claim; `CRASH` and `TERM-DONE` are boundary occurrences |
| unique canonical witness | expressly withdrawn; `NONUNIQUE` is the declared result after finite minimality proof |
| human-local verification burden | no time, expertise, cognition, or access claim |
| TCB closure | not presumed from a dependency list; an incomplete perturbation domain remains `UNKNOWN` |
| materially unlike realizations | none in the base corpus; every physical or cross-realization statement follows §10 |

An implementation that advertises any withdrawn property enlarges `DECL` and
must add the corresponding finite histories, collision pairs, dependencies,
and evidence before that property can receive a verdict.

## 11. Pre-freeze self-audit

The following audit was applied to this candidate before changing its status
from draft to frozen candidate.

| audit question | result |
|---|---|
| Is the primitive a boundary history rather than an assumed storage object? | yes; §1 defines only occurrences and explicitly rejects storage inference |
| Is there exactly one all-histories future-observable equivalence? | yes; `≃` in §2; bounded E support is expressly not a second equivalence |
| Are total-system coordinates simultaneous? | yes; every leaf has the complete vector in §6.6 |
| Does every persistent verdict have C, D, or E support? | yes; §4.2 and §9; unsupported subject claims remain unissued/unknown |
| Are retained evidence and permitted continuation separated? | yes; §4.1 and the post-terminal capture in §6.5 |
| Does prefix+expiry retain both facts? | yes; every observation leaf and post-terminal capture do so |
| Can an unrelated unknown mask a finite counterexample? | no; §4.4 and the `n`/`u` carrier pair make FAIL/false dominate locally |
| Can unbound external context affect a verdict? | no valid verdict; seal closure and `K-CLOSE` make divergence falsifying |
| Are all reachable future-forced phase distinctions ledgered? | yes for K/1 via `Pairs(S)`; physical completion is precisely withdrawn until evidenced |
| Is every claimed request covered at every reachable history predicate? | yes; decoder cases plus the 12-by-10 matrix; wider routing claims are withdrawn |
| Is branching witness minimality aggregate and is prefix difference exact? | yes; §§1.3 and 4.3 count shared trie nodes and retain every leaf |
| Does unknown remain unknown across retry, recovery, and recomputation? | yes; seals are immutable and only superseding evidence can change a later seal |
| Is a weighted score used? | no |
| Is any physical completion, stop, or cross-realization claim made without evidence? | no; §§6.4, 6.5, and 10 keep those claims unknown or boundary-scoped |
| Is the corpus bounded and end-to-end? | yes; §5 fixes finite bounds and all five leaves traverse every required operation or its bounded refusal |
| Do MAY/MUST carriers continue one common prefix with exact depth accounting? | yes; both queries occur at `DECL:K/1` and §6.3 counts every delivered request through depth six |
| Are occurrence direction, viewer, version scope, and rule content byte-instantiable? | yes; §§5.1 and 6.1 give literal declaration values and direction-tagged expansion forms |
| Is response latency bounded rather than only output size? | yes; §7.2 closes each delivered request by driver step three or emits an explicit expiry |

Freeze condition: changing the request vocabulary, a semantic rule, a branch,
a reachable phase label, a bound, or a dependency invalidates this audit and
requires a new candidate identifier. Editorial changes that alter bytes also
require a new file digest, even when they do not change semantics.

## 12. Falsifiable predictions

An implementation of the K/1 contract makes these concrete predictions.

1. After `CHUNK:a` followed by `EXPIRE`, every later authorized retained-evidence
   answer includes both facts; a crash, recovery, evolution, or terminal cut
   does not turn the result into an empty observation.
2. For carrier outcomes `{+,+,+,-,?}`, `MAY(q)` is true and `MUST(q)` is false.
   Removing the negative carrier changes MUST to `UNKNOWN`, not true.
3. Reclassifying the same seal under a different unbound locale, clock default,
   selector order, or canonicalizer preference cannot change the persistent
   verdict. A changed verdict is a reproducible byte-closure failure.
4. `OCCURRED:R` without `APPLIED:R` never establishes `q`; recovery cannot
   promote it unless new bound evidence creates a superseding seal.
5. `APPLIED:R` followed by completion-observation expiry establishes application
   but leaves physical completion `UNKNOWN`.
6. The old authored request `R@s0` has the same scoped meaning whether `s1` is
   applied immediately before or immediately after its attempt; an unqualified
   “meaning now or then” request is refused.
7. `audit` can distinguish every pair generated by the phase sets in §8 within
   two requests. If any pair needs a longer continuation or cannot be decided,
   the frozen collision ledger is false.
8. `limited` never learns whether `a` or `b` supplied authorization, yet its
   explanation remains compatible with both full histories and never asserts
   that those histories are identical.
9. After `TERM-DONE`, a capture or explanation receives a bounded audit answer,
   while `ATTEMPT:R` receives `TERMINAL-REFUSAL` and causes no semantic action
   occurrence.
10. Adding a physically completed branch without eight new action-family ledger
    pairs and §10 evidence invalidates the coverage claim; a label alone cannot
    extend it.
11. Repeating or recomputing the `u` branch without new evidence leaves its
    application result `UNKNOWN`.
12. Any delivered request of 257 octets is classified `OVERSIZE` after at most
    257 octets are read; any well-formed unknown operation is `UNSUPPORTED`.
13. In the singleton `a` depth breaker, `MAY(q)` is false at depth five and true
    at depths six and seven with the same exact length-six witness.

Any single minimized counterexample falsifies the corresponding prediction.
An unexecuted branch, missing authority, missing physical observation, or
unclosed finite domain yields `UNKNOWN`, not presumed success.
