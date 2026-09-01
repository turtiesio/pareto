# A tiny model for retaining something before we understand it

Storing something does not make it true, valid, or understood. It only means we retained evidence.

Remember three questions:

1. **What exact trace did we retain?** Keep the original bounded bytes. A decoded or cleaned-up view may be useful, but it cannot replace them.
2. **Which occurrence was this?** The same trace can arrive twice. Each arrival remains distinct even if storage deduplicates the bytes.
3. **What capture evidence did we retain?** Keep what the acquisition mechanism actually recorded about source, clock, completeness, or transformation. If it recorded nothing, say nothing; do not invent it.

Later, an identified interpreter may say what the trace means. That interpretation points back to the retained occurrence. Another interpreter may disagree, and a future interpreter may understand a format that is unknown today. None may rewrite the original trace.

Canonical example: the payment channel presents the bytes `{"order":17,"paid":true}` twice. The archive may store one physical copy of those bytes, but it records two occurrences and each occurrence’s available channel evidence. A parsed payment view is a later interpretation. The bytes alone do not prove that the provider sent them, that Order 17 is paid, or that any refund is allowed.

The boundary is honest: if the acquisition mechanism never measured a fact, the archive cannot recover it. The answer is unknown, not false and not guessed.

