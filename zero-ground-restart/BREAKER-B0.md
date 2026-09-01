# ZERO GROUND restart — ontology-free breaker freeze B0

Freeze date: 2026-09-01

This suite was produced independently of the builder candidate and without
reading `../ground.md`. Every row is gated by a contract clause. An absent gate
means `unsupported`, not an invented requirement.

## Oracle case shape

Each hidden case records: case id; contract-clause ids; kind (forced separation,
required equivalence, restart, resource, cross-realization, or impossibility);
two opaque boundary histories where applicable; an adaptive continuation;
viewer/authority/environment/realization; required observation relation;
failure assumptions; shrink rules; and targeted attacks.

A forced persistence witness is the minimized tuple `(clause, h0, h1,
continuation, required split, bounded-minimality certificate)`. Nondeterministic
behavior is compared by the contract's declared trace sets, distributions, or
strategies—never one sample. An unresolved comparison is `UNKNOWN`.

## Frozen hidden families

| ID | Contract gate | Minimal distinguishing pressure |
|---|---|---|
| B01 | any past boundary bit may be inspected | different accepted bits, later ask for the bit |
| B02 | accepted presence matters | empty history versus one accepted crossing |
| B03 | accepted values remain distinct | accepted `0` versus `1`, later conditional request |
| B04 | multiplicity matters | one versus two accepted equal crossings |
| B05 | order matters | accepted `a,b` versus `b,a` |
| B06 | correlation matters | same atoms under opposite associations |
| B07 | grouping/atomicity is observable | one declared group versus two, then undo/recover |
| B08 | surface bytes are exportable/signed/reinterpretable | normalized-equal bytes, exact export |
| B09 | absence states differ | missing versus explicitly empty, then default/explain |
| B10 | undo/audit/path explanation exists | `a;b` versus only `b`, then undo/path query |
| B11 | attempts/failures affect future | never attempted versus failed attempt |
| B12 | durable acceptance is promised | durable versus rejected, then restart |
| B13 | erasure is permanent | different erased contents must become equivalent |
| B14 | erasure proof/replay prevention exists | erased identifier versus never existed |
| B15 | source affects authority/attribution | same payload from two sources |
| B16 | viewer-specific privacy exists | public equality but privileged distinction |
| B17 | grant/revoke history matters | grant-then-revoke versus never granted |
| B18 | threshold time matters | one tick before versus after |
| B19 | age/expiry matters | same input at two times, continue at fixed time |
| B20 | interpretation choice is selectable | same input under two selections |
| B21 | historical interpretation is reproducible | same input under two versions |
| B22 | omission and explicit default evolve differently | omitted versus explicit old default under new version |
| B23 | forward reinterpretation/round-trip promised | ignored extension bit differs, install allowed reader |
| B24 | migration preserves historic distinction | two old forms coalesced by migration, later export |
| B25 | chosen nondeterministic result is reusable | same request, different crossed results |
| B26 | reproducible random stream promised | histories differ by one acknowledged draw |
| B27 | external response is replayable | same request, dependency returned different values |
| B28 | ambient mode persists | locale/rounding/policy bit differs, later divergent input |
| B29 | concurrent tie-break is visible | equal crossings with opposite declared order relation |
| B30 | action lifecycle controls retry | requested/dispatched/failed/confirmed cuts |
| B31 | endpoint deduplication exposed | equal action payload, different discriminator |
| B32 | exact rationale/provenance explainable | same outcome through different policy/rationale |
| B33 | unsupported differs from empty | operation absent versus supported empty result |
| B34 | a human later edits/verifies meaning | same scalar with different declared unit/label |
| B35 | human mapping evolves | same opaque mark under different glossary versions |
| B36 | cold-start deadline exists | delete accelerator, restart at maximal history |
| B37 | offline/degraded operation exists | rebuild dependency unavailable or changed |
| B38 | unlike realizations are interchangeable | differential run under one adaptive continuation |

## Impossibility probes

- Different unexpressed intentions with identical complete transcripts cannot be
  separated by any history representation.
- If an action may have completed outside the boundary before a crash and there
  is neither status query nor idempotent endpoint, exactly-once recovery is
  impossible regardless of stored bits.
- A visible durability acknowledgment emitted before actual durability is a
  recovery/TCB violation, not a missing logical history distinction.
- Required time-dependent behavior with no boundary clock or quantified stable
  reference is underdetermined.

## Attack rules

- DELETE/MERGE/COLLIDE: mutate, cold-start, and search all gated forced splits.
- DERIVE: demand a total deterministic recipe, inputs, versioned specification,
  availability assumptions, and losslessness proof.
- RECOMPUTE: clean restart under maximal history, outage, deadline, and version
  variation.
- FUTURE: test only the declared extension grammar; arbitrary past predicates
  activate B01 and collapse equivalence toward exact history.
- EXTERNALIZE: remove undeclared memory, caches, files, services, prompts,
  clocks, locale, operator memory, and conventions.
- REALIZE: compare Unicode, numeric, clock, ordering, concurrency, randomness,
  resource, and atomic-write differences where declared.
- COGNITION: use a declared `(role, initial knowledge, allowed artifacts, goal,
  time/error/step budget)`; otherwise report `UNKNOWN`.
- TCB: inventory capture, framing, normalization, rebuild, version resolution,
  migration, indexing, authorization, action recovery, dependencies, UI,
  documentation, and human procedure wherever correctness moved.

The suite tests required equivalences as well as separations. Retaining erased
content can violate a privacy contract even though it preserves more ordinary
query information.
