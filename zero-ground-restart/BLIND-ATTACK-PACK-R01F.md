# Ontology-Blind Attack Pack

## Collision oracle

Let every \(b_i\) be a distinct opaque byte string. Let \(K(h)\) be whatever bounded state, persisted image, canonical form, identity, or representative the candidate uses to merge history \(h\). Let

\[
\Omega(h,F,\kappa,\rho)
\]

be the complete required observable trace set after future continuation \(F\), under permitted interpreter/policy/viewer/environment state \(\kappa\) and physical realization \(\rho\). Observables include return bytes, rejection/explanation bytes, emitted effects, acknowledgements, identities, versions, and termination.

A collision exists when:

\[
K(h_0)=K(h_1)
\quad\text{but}\quad
\exists F,\kappa,\rho:\Omega(h_0,F,\kappa,\rho)\neq\Omega(h_1,F,\kappa,\rho).
\]

Past observable traces that already differ are an immediate collision; no future is needed. For nondeterminism, compare complete may/must trace sets, correlations, and any contracted distributions—not one sampled run or merely nonempty intersection.

`[BASE]` uses only the named claimed capability.  
`[PERM: …]` requires the contract to allow the stated condition.

---

## 1. Exactly-once uncertain cut

**Gate:** `[PERM: crash may occur after a non-atomic external effect boundary; the receiver offers no contractually conclusive durable resolution of that uncertainty.]`

Common prefix \(p\): request \(b_0\) exists and the same local durable image \(b_P\) has been established.

- \(h_0=p;\ \text{attempt}(b_1)\) does not reach the external effect point; crash with \(b_P\).
- \(h_1=p;\ \text{attempt}(b_1)\) reaches the effect point and produces external effect \(b_2\); crash before any locally durable distinguishing fact, again with \(b_P\).

Future:

- \(F=\text{recover};\) drive \(b_0\) to terminal status; inspect effect multiplicity and reported status/acknowledgement.

Failure witness:

- Re-emission yields one effect from \(h_0\) but two from \(h_1\).
- Suppression yields zero from \(h_0\) but one from \(h_1\).
- A local nondeterministic choice admits a wrong outcome in at least one history.
- Indefinite uncertainty violates any contracted termination/liveness condition.

This is the minimal crossing pair for exactly-once across a crash boundary.

---

## 2. “Emitted” and “acknowledged” cut ambiguity

### 2a. Emission cut

**Gate:** `[PERM: the contract exposes or predicates behavior on a particular emission stage.]`

For every adjacent pair among the contract’s possible stages—intent recorded, bytes handed across a boundary, externally accepted, effect committed—place the crash between them:

- \(h_0=p;\) crash immediately before stage \(c\), with durable image \(b_P\).
- \(h_1=p;\) stage \(c\) occurs for \(b_0\); crash immediately after it but before a distinguishing durable write, also with \(b_P\).

Future:

- \(F=\text{recover};\text{query-status}(b_q)\), or invoke a policy/viewer/action whose result depends on whether \(c\) occurred.

Required result is \(b_{\text{no}}\) versus \(b_{\text{yes}}\). If “emitted” does not select a precise stage, the claim itself has no unique test oracle.

### 2b. Acknowledgement cut

**Gate:** `[PERM: acknowledgement creation, transmission, receipt, or durable receipt is observable or behaviorally significant.]`

Common prefix includes the same external effect.

- \(h_0=p;\) no acknowledgement crosses stage \(a\); crash with \(b_P\).
- \(h_1=p;\ \text{ack}(b_A)\) crosses stage \(a\), but the crash occurs before a locally durable distinguishing write; same \(b_P\).

Future:

- \(F=\text{recover};\text{query-status/explanation}(b_q)\), or invoke acknowledgement-conditioned policy.

Repeat across acknowledgement-created, acknowledgement-sent, acknowledgement-received-volatily, and acknowledgement-recorded-durably. Any two stages the contract distinguishes must not collapse.

---

## 3. Hidden path state missed by shortest representatives

**Gate:** `[PERM: any interpreter, policy, viewer, receiver, realization, or hidden component may retain path-sensitive state.]`

Let \(p\) reach claimed representative \(K\). Let \(\ell\) be the shortest nonempty cycle returning the candidate to the same \(K\).

- \(h_0=p\).
- \(h_1=p;\ell\).

During \(\ell\), a permitted hidden/external state changes from \(b_X\) to \(b_Y\), although all outputs selected by shortest-representative testing may coincide.

Future:

- \(F=\text{call/query/interpret}(b_q)\), chosen so state \(b_X\) yields \(b_0\) and \(b_Y\) yields \(b_1\).

The minimal witness is a one-event self-loop; otherwise use the shortest nonempty cycle. Testing only the shortest path to each representative cannot discharge this attack.

Also test two-step futures when the hidden distinction is correlation rather than a one-step output difference.

---

## 4. Persisted encoding attacks

### 4a. Valid/malformed decoder collapse

**Gate:** `[PERM: malformed, truncated, extended, corrupted, or adversarial recovery bytes may be presented.]`

- \(h_0=\text{genuine-persist}(b_V);\text{crash}\), where \(b_V\) is contract-valid.
- \(h_1=\text{place}(b_M);\text{crash}\), where \(b_M\neq b_V\) must be rejected.

Choose \(b_M\) as the smallest insertion, deletion, substitution, truncation, extension, concatenation, or reordering that the candidate maps to the same recovered state as \(b_V\).

Future:

- \(F=\text{recover};\text{query/use/explain}(b_q)\).

Required observables differ: normal recovery for \(h_0\), rejection with contracted provenance/offset for \(h_1\).

### 4b. Byte-identical counterfeit provenance

**Gate:** `[PERM: the contract requires genuine and counterfeit persisted images with identical bytes to be distinguished.]`

- \(h_0=\text{candidate genuinely writes }b_P;\text{crash}\).
- \(h_1=\text{counterfeit placement of the identical }b_P;\text{crash}\).

All recovery-visible bytes are identical.

Future:

- \(F=\text{recover};\text{query/use/explain}(b_q)\).

If genuine must be accepted and counterfeit rejected, but no other permitted observation differs, the requirement is impossible. This is a provenance indistinguishability witness, not merely a parser bug.

### 4c. Replay/rollback of a once-valid image

**Gate:** `[PERM: rollback/replay is possible and freshness, retirement, or monotonic version history is observable.]`

- \(h_0=\text{write}(b_P);\text{crash}\).
- \(h_1=\text{write}(b_P);\text{advance}(b_1);\text{restore old }b_P;\text{crash}\).

The visible recovery image is identical.

Future:

- \(F=\text{recover};\text{query-version/identity}(b_q)\), apply an update, or perform an action whose permission changed during \(b_1\).

Required results differ if the contract distinguishes current from replayed state.

---

## 5. Rejection provenance through replacement

**Gate:** `[PERM: rejection explanation exposes authorship, ancestry, replacement history, source bytes, or source-relative locations.]`

Choose histories with the same current bytes \(b_C\):

- \(h_0=\text{author}(b_C)\).
- \(h_1=\text{author}(b_0);\text{replace}([i,j),b_1)\rightarrow b_C\).

Future:

- \(F=\) the shortest continuation \(b_q\) that requires rejecting a byte or span of \(b_C\), followed by explanation query/view.

The current rejected bytes may be identical, but required provenance is “direct” in \(h_0\) and replacement-derived in \(h_1\). A candidate retaining only \(b_C\), a digest of \(b_C\), or the shortest authoring path collides.

Extend minimally to two different replacement chains only if direct-versus-replaced provenance is not exposed.

---

## 6. Rejection offset and precedence collision

**Gate:** `[PERM: the contract defines source-relative offsets, replacement-relative offsets, or deterministic precedence among multiple rejection causes.]`

Construct the same current byte string \(b_C\) with two rejecting spans and two provenance maps:

- \(h_0\): source/provenance order requires \(b_X\) at offset \(i\) to win over \(b_Y\) at \(j\).
- \(h_1\): replacements shift, collapse, or swap ancestry so the required order makes \(b_Y\) win, while current bytes remain \(b_C\).

Future:

- \(F=\text{validate/use}(b_C);\text{request-explanation}(b_q)\).

Required rejection identity, provenance, or reported offset differs. Test each contracted precedence axis separately:

- original-source versus current-byte offset;
- carried-through versus replacement-created bytes;
- earliest offset versus outer/inner failure;
- first authored versus first discovered failure.

If the contract specifies only current-byte offsets and a history-independent precedence rule, provenance-dependent variants are gated out.

---

## 7. Update, version, and identity self-description

### 7a. Same update under different bases

**Gate:** `[PERM: update interpretation, acceptance, identity, or result may depend on the active predecessor version.]`

- \(h_0=\text{activate}(b_{V0})\).
- \(h_1=\text{activate}(b_{V1})\).

Assume the candidate merges them at the tested boundary.

Future:

- \(F=\text{apply-update}(b_U);\text{query-version/identity/explanation}(b_q)\).

Choose \(b_U\) for which the contract requires different acceptance, interpretation, resulting identity, or rejection provenance under \(b_{V0}\) and \(b_{V1}\).

### 7b. Self-description bootstrap collision

**Gate:** `[PERM: identical persisted bytes can be interpreted by unlike permitted spec/interpreter states.]`

- \(h_0=(b_P,\text{ external spec/interpreter state }b_{S0});\text{crash}\).
- \(h_1=(b_P,\text{ external spec/interpreter state }b_{S1});\text{crash}\).

Future:

- \(F=\text{recover};\text{query active version/identity}(b_q)\), then apply \(b_U\).

If \(b_P\) self-identifies only through rules whose selection already depends on \(b_{S0}\) versus \(b_{S1}\), required outputs differ despite identical local recovery bytes.

### 7c. Content identity versus lineage identity

**Gate:** `[PERM: byte-identical authored contracts may retain distinct identities or retirement lineages.]`

- \(h_0=\text{author}(b_C)\rightarrow b_{I0}\).
- \(h_1=\text{author}(b_C)\rightarrow b_{I1}\), with \(b_{I0}\neq b_{I1}\).

Future:

- \(F=\text{retire/update/query}(b_{I0})\).

A content-only merger collides if the contract requires lineage-sensitive results. Test the inverse polarity as well when distinct byte encodings are contractually one stable identity.

### 7d. Update acknowledgement crash cut

**Gate:** `[PERM: update acceptance/version change and its acknowledgement are independently externally observable.]`

- \(h_0=\) update \(b_U\) not committed; no acknowledgement; crash with \(b_P\).
- \(h_1=\) update \(b_U\) externally acknowledged as committed, but crash leaves the same \(b_P\).

Future:

- \(F=\text{recover};\text{query version};\text{reapply }b_U\).

Any required distinction between external commitment belief and recovered active version exposes the collision.

---

## 8. Nondeterministic recovery outcome sets

**Gate:** `[BASE if recovery is nondeterministic; otherwise any second outcome is a direct deterministic-contract failure.]`

For merged histories \(h_0,h_1\), use:

- \(\Omega(h_0,\text{recover};F)=\{b_0\}\)
- \(\Omega(h_1,\text{recover};F)=\{b_0,b_1\}\)

A sampled run producing \(b_0\) in both histories proves nothing. The distinguishing continuation is the scheduler/seed/realization that admits \(b_1\) only from \(h_1\).

Also test correlations with the smallest two-step future:

- \(h_0\) permits \(\{(b_0,b_0),(b_1,b_1)\}\).
- \(h_1\) permits \(\{(b_0,b_1),(b_1,b_0)\}\).

Their one-step marginals are identical; two observations distinguish them. Compare may-outcomes, must-outcomes, termination/fairness obligations, and contracted probability measures separately.

---

## 9. Externalized interpreter, spec, receiver, policy, and viewer state

**Gate:** `[PERM: the named external state may vary while the candidate-local state remains fixed.]`

Use identical candidate-local history and persisted bytes, differing only in one external byte-state:

| External owner | Crossing pair | Smallest future |
|---|---|---|
| Interpreter | same interpreter reference/code bytes; internal state \(b_{X0}\) vs \(b_{X1}\) | interpret \(b_q\) |
| Spec registry | same reference \(b_R\) resolves to \(b_{S0}\) vs \(b_{S1}\) | interpret/query version of \(b_q\) |
| Receiver | effect/dedup/ack state \(b_{R0}\) vs \(b_{R1}\) | resend or status-query \(b_q\) |
| Policy | policy state/version \(b_{P0}\) vs \(b_{P1}\) | authorize/action \(b_q\) |
| Viewer | viewer state/version \(b_{W0}\) vs \(b_{W1}\) | render/query \(b_q\) |

Any differing required output defeats a merge based only on candidate-local bytes.

For every claimed TCB assumption, repeat after the smallest permitted restart, rollback, replacement, identity reuse, state loss, or version change of that external owner. In particular:

- receiver remembers \(b_0\) versus receiver loses that memory while the physical effect remains;
- spec/interpreter reference remains byte-identical while its resolution changes;
- acknowledgement state survives versus disappears across receiver recovery.

A proof that silently fixes one of these states has proved only the corresponding restricted contract.

---

## 10. Unlike physical realizations

**Gate:** `[PERM: more than one physical realization, persistence model, transport behavior, or failure schedule is in scope.]`

Take the same logical history \(h\) and claimed logical merge state under \(\rho_0\) and \(\rho_1\). Place one crash at the shortest boundary where their permitted physical behaviors differ.

- \(h_0=(h,\rho_0);\text{crash at }c\).
- \(h_1=(h,\rho_1);\text{crash at }c\).

Future:

- \(F=\text{recover};\text{query/action}(b_q)\).

Compare complete trace sets for durability, ordering, duplication, torn/counterfeit recovery bytes, acknowledgement timing, and external effect multiplicity. If the contract requires realization-independent behavior, any difference is a witness. If it permits realization-specific outcome sets, compare against those exact sets rather than one favored realization.

---

## 11. Exact-history-interpreter theorem

**Gate:** `[PERM: a future-selected interpreter may inspect exact prior history and may emit distinguishable bytes based on it.]`

Let \(h_0\neq h_1\). By permission, select an interpreter encoded by opaque bytes \(b_J\) whose only relevant property is:

\[
J(h_0)=b_0,\qquad J(h_1)=b_1,\qquad b_0\neq b_1.
\]

Use the identical future:

\[
F=\text{select/install}(b_J);\text{invoke/query}(b_q).
\]

Then:

\[
\Omega(h_0,F)\neq\Omega(h_1,F),
\]

so \(h_0\) and \(h_1\) may not merge.

Smallest history pair:

- \(h_0=\epsilon\), \(h_1=[b_H]\); or
- if empty history is not permitted, \(h_0=[b_0]\), \(h_1=[b_1]\).

Therefore, if every exact-history separator is permitted, observational equivalence is exact-history equality, modulo only distinctions no permitted interpreter can inspect. If total candidate-relevant state has \(N\) possible merge keys and the contract admits \(N+1\) distinct histories, pigeonhole gives a colliding pair and the separator above supplies its future witness. Shortest-representative testing cannot evade this theorem.

---

## Frozen-candidate execution checklist

- Identify every explicit or implicit merge: same recovery image, canonical bytes, digest, identity, abstract state, shortest representative, or “equivalent” outcome.
- Instantiate each pair with the shortest opaque byte strings and shortest common prefix.
- Cut crashes immediately before and after every externally meaningful emission, effect, acknowledgement, update, and persistence boundary.
- Compare full observable trace sets across every permitted continuation, interpreter, policy, viewer, external-state evolution, scheduler, and realization.
- Treat identical sampled output as insufficient when outcome sets or correlations differ.
- Exercise the shortest nonempty cycle into every merge state, not only its shortest representative.
- Present valid, minimally mutated, byte-identical counterfeit, and replayed persisted images.
- Preserve separate oracles for rejection identity, provenance, source/current offsets, and precedence.
- Demand the exact contract clause that closes each `[PERM: …]` gate; undefined terms such as “emitted,” “acknowledged,” “current,” “same identity,” or “version” do not close it.
- Apply the exact-history-interpreter theorem before accepting any bounded merge whenever future exact-history interpretation remains permitted.
