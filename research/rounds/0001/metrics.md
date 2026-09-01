# Metrics plan

## Semantic / information loss

Count retained distinctions and minimized collisions. Count the expressive burden of any metadata/context format rather than treating `bytes` as free semantics.

## Runtime / storage

Measure hashing, capture append, verification, export/import, authoritative payload bytes, occurrence overhead, acquisition bytes, and encoding overhead at feasible scales. Analytically project to `10^3`, `10^6`, and `10^9` captures, explicitly separating unique-content ratio and mean payload/context sizes.

## Trusted base

Count nonblank/noncomment source lines in the experimental encoder, decoder, verifier, and hash reference. Record that Python, SHA-256, JSON, and Base64 implementations remain external trust dependencies.

## Cognitive

After the formal result is frozen, give a fresh reviewer only a one-page explanation. Ask whether duplicate deliveries, unknown data, normalization, absent context, and later interpretation remain distinguishable.

Results are pending execution.

