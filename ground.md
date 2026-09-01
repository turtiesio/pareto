# ZERO GROUND — RESTART

Forget every architecture, primitive, layer, and conclusion from prior work.

Do not assume objects, facts, events, claims, evidence, rules, graphs, state, storage, programs, actors, queries, proofs, packages, maps, or any other previously proposed structure.

The goal is not to minimize one layer of a system.

The goal is to discover the smallest **total system** that preserves exactly the distinctions required by its externally declared contract, while supporting future observation, interpretation, authoring, querying, action, explanation, evolution, and unlike physical realizations.

## Fundamental method

Start from histories and distinguishability.

Let a history be everything that has crossed the declared system boundary so far.

Two histories may be merged only if no allowed future continuation can require them to behave differently.

Conceptually:

`h1 ≡ h2`

iff for every permitted future continuation, query, interpretation, action, policy, viewer, and realization required by the contract, the required externally observable behavior is identical.

A persistent representation is valid only if:

`encode(h1) = encode(h2)  =>  h1 ≡ h2`

Whenever deleting or merging information causes two non-equivalent histories to collide, produce the smallest witness. That witness establishes a persistence distinction, not automatically a field, record type, layer, or primitive.

The conceptual minimum persistent state is the quotient of histories by this future-observable equivalence. Search for representations of that quotient; do not assume its shape.

## Do not optimize dimensions sequentially

Do not run separate research phases that first freeze preservation, then semantics, then reasoning, then cognition, then navigation, then storage.

That ordering can create path dependence.

Every candidate must be evaluated as a total system in the same round.

For every candidate measure simultaneously:

* information/distinction preservation;
* persistent state;
* semantic machinery;
* human cognition;
* authoring burden;
* query/navigation burden;
* runtime;
* storage;
* operations;
* trusted computing base;
* evolution;
* portability;
* explainability;
* information-loss risk.

No weighted scalar score.

## Mandatory attacks

For every persisted item or mechanism ask:

**DELETE** — If it is not persisted, can every required future behavior still be reconstructed?

**MERGE** — Can it be merged with another item without collapsing distinguishable histories?

**DERIVE** — Can it always be reconstructed mechanically from smaller surviving information?

**RECOMPUTE** — Is persistence necessary, or is deterministic regeneration sufficient?

**COLLIDE** — Find the smallest pair of histories that the simplification makes identical.

**FUTURE** — Does a previously unanticipated but contract-permitted continuation distinguish them?

**EXTERNALIZE** — Did the apparent deletion merely move required state into an external service, runtime, prompt, human convention, or organization?

**REALIZE** — Can two unlike physical implementations preserve the same observable contract without silently weakening it?

**COGNITION** — Did machine simplification increase what a human must remember, discover, author, or verify?

**TCB** — Where did the code/configuration that must be correct move?

After every apparent simplification ask:

**Where is the complexity now?**

## Persistent-state classification

Do not predeclare any category.

After attacks, classify discovered information only as:

**MUST SURVIVE**
Deleting it merges histories that some permitted future can distinguish.

**MAY REBUILD**
It can be deterministically reconstructed from MUST SURVIVE information plus an identified specification.

**MAY FORGET**
Deleting it cannot affect any permitted future observable behavior.

These are verdicts, not primitive types.

## Research discipline

Use builder and breaker agents independently.

The breaker must not inherit the builder's ontology.

Implementation is only a falsification instrument.

A passing implementation is never itself the architecture.

A named abstraction survives only when deletion or merging produces a minimized collision.

A distinction surviving does not imply that a dedicated constructor survives.

Never credit missing compiler, verifier, index, selector, cache invalidator, recovery mechanism, or trust mechanism as zero complexity.

Unknown capability is reported as unknown or unsupported, never silently assumed.

## Prior research quarantine

Do not read previous ZERO GROUND conclusions while generating initial candidates.

Freeze all previous work as an adversarial archive.

After a new candidate has been independently specified and frozen, replay prior counterexamples against it without revealing the old proposed solutions.

Prior work contributes attacks, not inherited ontology.

## First experiment

Do not build search/navigation infrastructure.

Construct the smallest end-to-end history corpus that permits deletion and collision testing.

For each candidate persistent representation:

1. enumerate small histories;
2. enumerate a bounded but diverse set of allowed future continuations;
3. compute which histories those futures distinguish;
4. search automatically for representation collisions between distinguishable histories;
5. minimize each collision;
6. delete every persisted element that has no surviving witness;
7. repeat until no deletion/merge succeeds in the searched domain.

Then attack the candidate with fresh-domain and previously hidden counterexamples.

The first milestone is not a kernel.

It is a defensible statement of:

**what information must survive between executions, what may be rebuilt, what may be forgotten, and exactly which future-observable distinction forces each surviving bit of responsibility.**
