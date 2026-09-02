# ZERO GROUND R0.1I — Blind Attack Pack

## 0. Purpose and boundary

This is a finite, ontology-independent breaker pack for a history-first total-system contract. It tests only claims visible at a declared system boundary. It makes no assumption about implementation structure.

The pack targets contracts that claim to support bounded observation, interpretation, authoring, querying, explanation of action attempts, evolution, crash/recovery, termination, and more than one permitted viewer or realization.

Each attack starts from the smallest useful pair of boundary histories and adds the shortest continuation that can distinguish a sound account from a conflation. A conforming answer may use any vocabulary, provided the answer is total, bounded, viewer-correct, and supported by the evidence the contract says is authoritative.

## 1. Black-box notation

- `h` is a finite boundary history.
- `h·x` is `h` followed by one boundary occurrence or one controlled physical occurrence `x`.
- `c` is a finite continuation, possibly adaptive: its next step may depend on the preceding boundary answer.
- `F(h)` means the contract's full-history meaning for `h`. It does **not** mean that every viewer may inspect that meaning.
- `P_v(h)` is the projection permitted to viewer `v` at the time of the observation.
- `O(v,r,h,b)` is what viewer `v` can obtain in realization `r` about `h` within declared bound `b`.
- `A` is an action attempt. `occ(A)`, `app(A)`, and `done(A)` name, solely for testing, the distinguishable facts that the attempt occurred, its meaning was applied, and its promised external completion condition happened.
- `crash`, `recover`, and `term` are controlled boundary cuts. A physical power cut, process loss, link partition, and orderly stop are different cuts unless the contract explicitly proves them equivalent.
- `K(h,d)` is the finite contract-permitted carrier set from `h` through remaining depth `d`. For a predicate `q`, `MAY(q)` means an existential claim over that set and `MUST(q)` means a universal claim over that set.
- A “witness” is whatever finite evidence the contract offers for an answer. “Canonical” means only what the contract claims it means; the tests do not impose an ordering.

The notation is experimental shorthand, not a required representation.

## 2. Transformation operators

Every attack names one or more of these mutations.

| Operator | Black-box mutation |
|---|---|
| `DELETE` | Remove exactly one occurrence, permission, dependency, branch, or piece of available evidence. |
| `MERGE` | Force two semantically different cases to share the same visible projection or asserted identity. |
| `DERIVE` | Substitute a computed assertion for directly checkable boundary or physical evidence. |
| `RECOMPUTE` | Ask for the same interpretation or witness again after restart, upgrade, or context loss. |
| `COLLIDE` | Give different causes, schedules, versions, or choices the same public name or claimed canonical result. |
| `FUTURE` | Append the shortest continuation that reveals a latent difference between prefixes. |
| `EXTERNALIZE` | Vary an influencing controller, capture, selector, manifest, specification, or canonicalizer context while holding the claimed in-scope history fixed. |
| `REALIZE` | Repeat a matched experiment in materially unlike permitted realizations. |
| `COGNITION` | Measure the human work and ambiguity required to validate a claimed answer. |
| `TCB` | Perturb an influence whose correctness is necessary to trust the answer. |

## 3. Common execution and evidence rules

### 3.1 Finite execution recipe

For every attack:

1. Fix the contract version, viewer permissions, observation bound, continuation-depth bound, permitted realization class, and claimed nondeterminism policy.
2. Construct the stated adjacent pair of histories. They must differ at only the named boundary cut unless the attack says otherwise.
3. Run the stated continuation from both prefixes. For an adaptive continuation, expose the same prior answers to the driver until the intended divergence point.
4. Ask every named viewer the same semantically matched observation, interpretation, query, authoring, or explanation request.
5. When a physical fact matters, establish it independently of the system answer under test.
6. Repeat only enough to cover the contract's finite declared branches. Sampling cannot prove a universal claim.
7. Reduce any failure by the minimization order below before reporting it.

### 3.2 Global minimization order

Minimize lexicographically:

1. number of boundary occurrences;
2. number of differing occurrences between the paired histories;
3. continuation length;
4. number of viewers;
5. number of realizations;
6. number of nondeterministic choices;
7. amount of external context varied.

Unless an attack says otherwise, the target is two histories differing at one cut, one continuation step, two viewers only when projection is essential, and two realizations only when physical difference is essential.

### 3.3 Three-valued verdict discipline

- **PASS** requires finite positive evidence for every attack-specific obligation. Equality claims need evidence at the declared comparison boundary; universal claims need all members of the declared finite domain; physical claims need physical evidence.
- **FAIL** requires one minimized finite counterexample: a forbidden leak, false conflation, contradiction, unbounded/non-total answer, incorrect quantifier, capability resurrection/loss, or unsupported equivalence.
- **UNKNOWN** is mandatory when a needed branch cannot be induced, a relevant full-history fact or physical fact cannot be independently established, the exploration domain is not finitely bounded, the answer exceeds the bound without a contract-authorized terminal result, or only self-assertion supports the claim.

Silence, timeout, lack of visible contradiction, repeated agreement, and a successful recomputation are not by themselves PASS evidence.

## 4. Attack catalogue

### B00 — Totality envelope at every operation boundary

**Attack map:** `DELETE · FUTURE · COLLIDE`

**Executable pair and continuation:** For each claimed operation—bounded observation, interpretation, authoring, query, action-attempt explanation, evolution, recovery, and termination—run adjacent inputs at: empty, one unit, exact declared bound, one beyond the bound, malformed but deliverable, unknown future version, unauthorized viewer, post-crash, and post-terminal. Pair the last accepted case with the first rejected case. Append one query asking what happened and what remains permitted.

**Minimized-witness target:** One operation, one boundary transition, one request, and its first follow-up query.

**Evidence rule:**

- **PASS:** Every case reaches a contract-defined answer or contract-defined refusal within its bound, and the follow-up explanation agrees with that result.
- **FAIL:** Any case hangs, silently disappears, is accepted beyond the claimed bound, produces an uninterpretable answer, or is later described inconsistently.
- **UNKNOWN:** The relevant bound or accepted domain is not finite and explicit enough to construct the adjacent pair.

### B01 — Full-history difference hidden by one viewer projection

**Attack map:** `MERGE · FUTURE · DERIVE`

**Executable pair and continuation:** Construct `h0` and `h1=h0·x`, where `x` is visible to an authorized full-history fixture or richer viewer `w` but hidden from viewer `v`, so `P_v(h0)=P_v(h1)`. Append the shortest permitted continuation `c` whose full-history meaning depends on `x`. Ask both viewers for the prefix interpretation, the continuation result, and its explanation.

**Minimized-witness target:** Two histories, one hidden occurrence, two viewers, one differentiating continuation.

**Evidence rule:**

- **PASS:** The richer evidence distinguishes the histories; `v` receives equal prefix projections; later answers neither leak `x` nor falsely assert that the full histories were identical; each viewer's explanation remains valid under that viewer's projection.
- **FAIL:** The low viewer learns `x`, a full-history answer conflates the prefixes, or a derived explanation treats projection equality as full-history equality and predicts the continuation incorrectly.
- **UNKNOWN:** No independent authority can establish the full-history difference, or no permitted finite continuation can expose it.

### B02 — Viewer-relative explanation after hidden causation

**Attack map:** `DELETE · DERIVE · COGNITION`

**Executable pair and continuation:** Produce one outcome with a two-occurrence causal chain where viewer `w` may see both occurrences and viewer `v` may see only the second. Compare this with the adjacent history where the hidden occurrence is absent and the outcome therefore does not happen. Ask both viewers “why did this happen?” and “what would make it not happen?”

**Minimized-witness target:** One hidden prerequisite, one visible consequence, two viewers, two explanation questions.

**Evidence rule:**

- **PASS:** `w` can validate the complete explanation; `v` gets an authorized explanation that is still semantically valid rather than a broken redaction, and cannot infer the hidden prerequisite beyond permission.
- **FAIL:** The explanation leaks the prerequisite, cites an invisible fragment that makes the answer unusable, invents a visible cause, or gives `v` a counterfactual contradicted by the adjacent history.
- **UNKNOWN:** Viewer-validity cannot be judged without the hidden fact and no authorized adjudicator is available.

### B03 — Visibility of attempted, denied, applied, and completed action

**Attack map:** `DELETE · MERGE · FUTURE`

**Executable pair and continuation:** Use the same authored action in four adjacent runs: denied before occurrence, attempt occurred but not applied, applied but not completed, and completed. Give viewer `w` permission to see action attempts and viewer `v` permission only for completed effects. After each run, ask what was attempted, what was permitted, what took effect, and why.

**Minimized-witness target:** Reduce any failure to one adjacent pair among the four cuts, one action, two viewers, and one explanation query.

**Evidence rule:**

- **PASS:** Every viewer sees exactly the distinctions permitted to that viewer; an absent attempt is not confused with a hidden attempt; an attempted action is explainable even without completion; completion claims match independent physical evidence.
- **FAIL:** A hidden attempt leaks, an authorized attempt vanishes, denial is described as failure after application, application is described as completion, or completion is asserted without its promised condition.
- **UNKNOWN:** The contract does not expose enough authority to distinguish the adjacent cuts and no independent physical check can do so.

### B04 — Permission change must not rewrite history

**Attack map:** `RECOMPUTE · FUTURE · MERGE`

**Executable pair and continuation:** In `h0`, viewer `v` is permitted to observe `x` when `x` occurs and then loses permission. In `h1`, `v` never had permission; keep the final permission equal. Recompute the same bounded past query after the permission change, then grant the same future permission in both runs and query again.

**Minimized-witness target:** One occurrence, one permission transition, one viewer, and one repeated query.

**Evidence rule:**

- **PASS:** The answers follow the contract's explicitly declared time-of-occurrence versus time-of-query rule, never exceed current authority, and do not conflate the two full histories merely because final permissions match.
- **FAIL:** Permission loss silently rewrites a previously established full-history meaning, permission gain fabricates prior visibility, or equal current permissions force false full-history identity.
- **UNKNOWN:** The contract does not declare which permission time governs and both readings remain observationally possible.

### B05 — Occurrence/application/completion adjacency

**Attack map:** `MERGE · DELETE · REALIZE`

**Executable pair and continuation:** Choose an action for which occurrence, application, and external completion can be induced separately. Compare adjacent prefixes at `¬occ/occ`, `occ/ app`, and `app/done`; place a controlled crash immediately after each cut. Recover where permitted and ask for the action result and explanation.

**Minimized-witness target:** One action, one adjacent phase pair, one crash cut, one recovery query.

**Evidence rule:**

- **PASS:** The contract either preserves each physically meaningful distinction or explicitly proves the selected phases equivalent for this action; post-recovery answers agree with the induced cut.
- **FAIL:** An occurrence is reported as application, application as completion, absence as an attempt, or two cuts are merged despite a distinguishing permitted continuation or physical fact.
- **UNKNOWN:** The selected action does not permit the phase cuts to be established independently.

### B06 — Crash after physical completion but before answer

**Attack map:** `MERGE · FUTURE · REALIZE`

**Executable pair and continuation:** In `h0`, crash immediately before the promised physical completion; in `h1`, permit physical completion and crash before the boundary answer reaches the caller. Make the caller-visible prefixes equal. Recover, retry the identical action once, then ask what happened on both attempts.

**Minimized-witness target:** Two histories, one shifted crash cut, one retry, one physically countable effect.

**Evidence rule:**

- **PASS:** The retry behavior satisfies the contract's declared guarantee in both histories, the explanation distinguishes uncertainty from absence, and the count of physical effects matches the claim.
- **FAIL:** The first completion is denied, duplicate completion violates the guarantee, an effect is lost, or identical caller projections are used to assert identical full histories.
- **UNKNOWN:** Physical completion cannot be independently counted or the retry guarantee is not stated precisely enough to test.

### B07 — Rejected, failed, no-op, and successful attempts collide

**Attack map:** `COLLIDE · DERIVE · DELETE`

**Executable pair and continuation:** Author the same action against four minimal contexts that make it respectively rejected before attempt, attempted then failed, valid but no-op, and successful. Arrange for the same superficial result text wherever the boundary permits. Ask for cause, application, completion, and remaining capability.

**Minimized-witness target:** One adjacent pair of outcome classes and one explanation request.

**Evidence rule:**

- **PASS:** The contract distinguishes every class that changes future behavior, capability, or physical effect, even if the human-facing wording is similar.
- **FAIL:** Two classes collide and a one-step continuation exposes a wrong explanation, wrong retry decision, or wrong remaining capability.
- **UNKNOWN:** The contract intentionally equates the selected classes and no permitted continuation or physical fact distinguishes them.

### B08 — Observation truncation versus historical absence

**Attack map:** `DELETE · MERGE · EXTERNALIZE`

**Executable pair and continuation:** Let `h0` contain no matching occurrence. Let `h1` contain one matching occurrence immediately outside viewer `v`'s bounded observation window. Make the returned bounded observation equal, then ask whether the occurrence never happened, was not found in the observed portion, or is unknown. Repeat with the capture influence unable to supply one in-window occurrence.

**Minimized-witness target:** One occurrence just across one bound, one viewer, one yes/no/unknown query.

**Evidence rule:**

- **PASS:** The answer distinguishes absence in the observed portion from absence in full history and from unavailable evidence; the bound is honored.
- **FAIL:** Empty bounded output becomes proof of full-history absence, capture loss becomes non-occurrence, or the query exceeds the declared bound without a terminal answer.
- **UNKNOWN:** The observation window or capture availability cannot be controlled.

### B09 — Declared branch label versus hidden nondeterminism

**Attack map:** `DELETE · COLLIDE · DERIVE`

**Executable pair and continuation:** From the same prefix and request, induce two permitted branches with different one-step consequences. First delete the branch distinction from the viewer-visible explanation; then force both branches to share the same declared branch name. Query the selected branch and predict the next bounded result.

**Minimized-witness target:** One branch point, two branches, one shared prefix, one differentiating continuation.

**Evidence rule:**

- **PASS:** Either the branch distinction is exposed to every viewer entitled to rely on it, or the contract demonstrates that the branches are equivalent at the claimed boundary; predictions are branch-correct.
- **FAIL:** Divergent branches are presented as deterministic, one public branch identity covers incompatible consequences without disclosed scope, or the explanation derives a false replay claim.
- **UNKNOWN:** Both branches cannot be induced within the finite declared branch domain.

### B10 — Repetition cannot certify determinism

**Attack map:** `FUTURE · DELETE · COLLIDE`

**Executable pair and continuation:** Repeat a prefix/request enough times to cover every branch the contract declares reachable at the chosen bound. If only one branch appears, append the shortest adversarial continuation or environment choice allowed by the contract. Compare a determinism claim with a claim of currently unobserved nondeterminism.

**Minimized-witness target:** One shared prefix, one request, one late branch, and one-step distinguishing future.

**Evidence rule:**

- **PASS:** Determinism is supported by an exhaustive finite domain or by a contract-valid proof whose trusted influences survive B34–B35; otherwise the answer explicitly remains non-universal.
- **FAIL:** Finite repeated agreement alone is promoted to a universal determinism claim and one permitted continuation produces a contrary branch.
- **UNKNOWN:** Reachable choices are not finitely bounded or cannot be exhaustively controlled.

### B11 — Scheduler identity on divergent adaptive paths

**Attack map:** `MERGE · COLLIDE · FUTURE · EXTERNALIZE`

**Executable pair and continuation:** Run an adaptive driver that chooses its next action from the preceding result. Use two schedules that keep the initial viewer projection equal but change which result reaches the driver before its next choice. Give the schedules the same public scheduler identity, then append the adaptive next step and request an explanation of why that step was selected.

**Minimized-witness target:** Two enabled occurrences, one ordering difference, one adaptive choice, one shared scheduler identity.

**Evidence rule:**

- **PASS:** The scheduler claim binds every choice necessary to explain the divergent adaptive path, or clearly limits identity to a weaker property that does not promise replay; the next-step explanations match the actual delivered results.
- **FAIL:** A scheduler name or configuration is treated as path identity while relevant choices differ, the adaptive cause is hidden, or replay is promised but diverges.
- **UNKNOWN:** Ordering cannot be controlled or the scheduler identity claim has no testable behavioral meaning.

### B12 — Scheduler recovery with lost adaptive context

**Attack map:** `RECOMPUTE · EXTERNALIZE · FUTURE`

**Executable pair and continuation:** Stop both runs after the same adaptive prefix. In `h0`, recover with the influencing scheduler/controller context preserved; in `h1`, recover without exactly one prior adaptive distinction while keeping the system-visible prefix equal. Allow one next choice, then query schedule identity and remaining alternatives.

**Minimized-witness target:** One adaptive distinction, one crash/recovery, one next choice.

**Evidence rule:**

- **PASS:** A changed next choice is attributed to the changed context and scoped accordingly, or the claimed recovery semantics makes both next choices equivalent; no stronger identity is asserted.
- **FAIL:** The same replay/scheduler identity is asserted across divergent choices, loss of context is invisible, or recovery invents a past choice.
- **UNKNOWN:** The adaptive context cannot be varied independently or the next choice is not observable.

### B13 — MAY and MUST separate on two carriers

**Attack map:** `MERGE · DERIVE · FUTURE`

**Executable pair and continuation:** Construct a prefix with exactly two permitted carriers through depth `d`: `k+` satisfies `q`, and `k−` violates `q`. Ask `MAY(q)` and `MUST(q)`, request one witness or counterexample as appropriate, then execute each carrier once.

**Minimized-witness target:** One prefix, depth one if possible, two carriers, one predicate with opposite results.

**Evidence rule:**

- **PASS:** `MAY(q)=true`, `MUST(q)=false`; the existential witness and universal counterexample execute as claimed for the authorized viewer.
- **FAIL:** The answers coincide, a preferred carrier is substituted for all carriers, a derived witness does not execute, or projection merging hides the violating carrier from a viewer entitled to the universal claim.
- **UNKNOWN:** The carrier set is not finite/closed at the declared depth or either carrier cannot be executed.

### B14 — Empty-carrier vacuity

**Attack map:** `DELETE · DERIVE · COGNITION`

**Executable pair and continuation:** Start with one permitted carrier and delete it so `K(h,d)` is empty. Ask `MAY(q)`, `MUST(q)`, “is `q` guaranteed?”, and “show a carrier.” Repeat with `q` and its negation.

**Minimized-witness target:** One prefix, one deleted carrier, zero executable continuations, two opposite predicates.

**Evidence rule:**

- **PASS:** Existential answers are false; any formally vacuous universal truth is explicitly distinguishable from an operational guarantee; no carrier is fabricated; `q` and its negation do not both become actionable guarantees.
- **FAIL:** Emptiness is advertised as substantive success, a witness is invented, MAY becomes true, or a human-facing guarantee hides vacuity.
- **UNKNOWN:** The contract leaves “guaranteed” undefined and offers no testable relation to MAY/MUST.

### B15 — Carrier collision under a viewer projection

**Attack map:** `MERGE · COLLIDE · FUTURE`

**Executable pair and continuation:** Choose two full-history-distinct carriers that have equal projection for viewer `v` through the current bound, but one later satisfies `q` and the other violates it. Force the same public carrier name or canonical presentation, then extend by the one distinguishing step.

**Minimized-witness target:** Two carriers, one hidden difference, one viewer, one future step.

**Evidence rule:**

- **PASS:** Viewer-relative MAY/MUST answers quantify over the contract-declared authorized carrier domain without silently collapsing full-history alternatives; the future step is explained without leakage.
- **FAIL:** Projection equality removes a relevant carrier, one name is treated as one behavior, or MUST is returned because the violating hidden carrier was merged away.
- **UNKNOWN:** The contract does not define the viewer-relative carrier domain.

### B16 — Exact remaining-depth boundary

**Attack map:** `DELETE · FUTURE · DERIVE`

**Executable pair and continuation:** Construct `h0` where the first satisfying carrier for `q` has length exactly `d`, and `h1` where one required final step is unavailable. Ask MAY/MUST at `d−1`, `d`, and `d+1`; then execute the exact-length carrier.

**Minimized-witness target:** Smallest positive `d`, one missing final step, one predicate.

**Evidence rule:**

- **PASS:** Answers change only at the justified depth boundary, the claimed witness has the stated length, and execution agrees.
- **FAIL:** Off-by-one acceptance, a witness longer than the bound, hidden unbounded work, or an unavailable final step is derived into existence.
- **UNKNOWN:** Depth accounting is not defined at the boundary or the witness cannot be executed.

### B17 — Remaining capability across phase-specific crash

**Attack map:** `RECOMPUTE · MERGE · EXTERNALIZE`

**Executable pair and continuation:** Give both runs exactly one remaining use of a bounded capability. In `h0`, crash just before the attempt occurs; in `h1`, crash just after occurrence, application, or completion, testing each adjacent cut separately. Recover and attempt one use; query remaining capability and the reason for any refusal.

**Minimized-witness target:** One capability, one action, one adjacent phase cut, one recovery, one retry.

**Evidence rule:**

- **PASS:** Consumption follows the contract's declared phase rule consistently before and after recovery; external controller context cannot silently change the count.
- **FAIL:** Recovery mints a use, loses an unconsumed use, counts a different phase than claimed, or explanation contradicts retry behavior.
- **UNKNOWN:** The consumption phase is unspecified or no independent experiment distinguishes it.

### B18 — Empty recovery cycles must not drift depth

**Attack map:** `RECOMPUTE · FUTURE · DELETE`

**Executable pair and continuation:** From the same prefix with remaining depth `d`, run zero crash/recovery cycles in `h0` and one empty cycle in `h1`; if equal, compare one versus two cycles. Perform no authored or action attempt between cuts. Query remaining depth, MAY/MUST, and then execute a boundary-length carrier.

**Minimized-witness target:** One empty crash/recovery cycle and one exact-depth continuation.

**Evidence rule:**

- **PASS:** Empty cycles preserve or consume depth exactly as explicitly declared, and the boundary-length continuation agrees; the explanation names the relevant crash rule.
- **FAIL:** Depth drifts without a declared cause, repeated recovery mints capability, or recomputation changes MAY/MUST while the claimed semantic history is unchanged.
- **UNKNOWN:** Recovery itself is declared nondeterministic but its finite branches cannot be covered.

### B19 — Recovery at exhausted capability

**Attack map:** `FUTURE · RECOMPUTE · COLLIDE`

**Executable pair and continuation:** In `h0`, stop one step before exhausting the final capability/depth unit. In `h1`, consume it and crash at the first later cut. Recover both, issue the same action, and ask whether the action was attempted, why it was accepted/refused, and what remains.

**Minimized-witness target:** One final unit, one consumption, one crash, one post-recovery attempt.

**Evidence rule:**

- **PASS:** Only the unexhausted history permits the final use, subject to the declared phase rule; exhausted recovery does not resurrect capacity and refused actions remain explainable.
- **FAIL:** Prefixes collide after recovery, exhausted capacity returns, unexhausted capacity disappears, or refusal is confused with an absent attempt.
- **UNKNOWN:** Exhaustion cannot be established independently.

### B20 — Graceful termination phase cuts

**Attack map:** `MERGE · DELETE · FUTURE`

**Executable pair and continuation:** Induce termination request occurrence, application, and externally completed termination as separate cuts. Compare every adjacent pair, crashing immediately after the earlier or later cut. Where recovery is permitted, recover once; in all cases, issue one query and one action attempt after the cut.

**Minimized-witness target:** One adjacent termination cut, one crash placement, one post-cut request.

**Evidence rule:**

- **PASS:** Intended, applied, and completed termination are not conflated where future behavior differs; post-cut requests receive the contract-defined bounded result; recovery follows the declared terminal rule.
- **FAIL:** A request is treated as completed termination, completed termination resumes silently, post-terminal work executes contrary to the contract, or the system becomes non-total at the boundary.
- **UNKNOWN:** No permitted observer remains able to obtain the contract-defined result after the cut.

### B21 — Crash is itself the terminal occurrence

**Attack map:** `REALIZE · DELETE · TCB`

**Executable pair and continuation:** In a controlled realization, induce a crash for which the declared test conditions rule out any further execution or recovery. Pair it with a recoverable crash having the same pre-crash viewer projection. Attempt the same bounded observation and external action after each, using an observer outside the failed realization where the contract permits one.

**Minimized-witness target:** One crash-property difference, one external observer, one post-crash attempt.

**Evidence rule:**

- **PASS:** The irrecoverable case is covered by an explicit terminal outcome within the observer's bound, the recoverable case is not falsely terminal, and the physical premise comes from a trusted influence named by the contract.
- **FAIL:** Permanent non-execution is reported as pending recovery, the recoverable case is declared final, or lack of answer is treated as proof without the physical premise.
- **UNKNOWN:** Irrecoverability cannot be established finitely or no authorized observation boundary survives.

### B22 — No semantic continuation after terminal history

**Attack map:** `FUTURE · DELETE · COLLIDE`

**Executable pair and continuation:** Take the shortest history the contract calls terminal. Append, one at a time, an observation request, interpretation request, authored action, query, recovery request, and second termination request. Pair each with the same request just before terminality.

**Minimized-witness target:** One terminal occurrence and one appended request of the first failing class.

**Evidence rule:**

- **PASS:** Every appended request has the declared post-terminal treatment; no semantic action continuation occurs where forbidden; observation or explanation remains available only if expressly part of the terminal contract.
- **FAIL:** A forbidden continuation changes the terminal meaning, post-terminal requests vanish without bounded classification, or pre- and post-terminal requests collide despite different promised behavior.
- **UNKNOWN:** “Terminal” has no operationally testable boundary meaning.

### B23 — Two incomparable minimal canonical witnesses

**Attack map:** `COLLIDE · RECOMPUTE · DERIVE`

**Executable pair and continuation:** Construct a diamond: either of two independent, equally minimal histories suffices for the same answer, and a third history contains both. Ask for the canonical witness repeatedly, after crash/recovery, and from two permitted viewers whose projections preserve both alternatives.

**Minimized-witness target:** Two one-step sufficient witnesses, one combined history, one repeated query.

**Evidence rule:**

- **PASS:** The answer either chooses consistently under the contract's declared canonical scope or explicitly reports non-uniqueness; every offered witness validates and minimality is checked by deleting each member in turn.
- **FAIL:** Canonical claims alternate with unchanged scope, a non-witness is selected, one alternative is silently erased, or self-consistency is substituted for minimality.
- **UNKNOWN:** The canonical ordering/scope is unspecified, making multiple outputs equally compatible.

### B24 — Canonicalizer context outside the claimed history

**Attack map:** `EXTERNALIZE · RECOMPUTE · COLLIDE · TCB`

**Executable pair and continuation:** Hold the full boundary history and viewer fixed. Change exactly one influencing canonicalizer context—version, tie preference, locale, or available alternative—outside the scope the canonical claim says determines its result. Recompute before and after crash and request the same witness.

**Minimized-witness target:** One history with two valid alternatives and one external canonicalizer-context change.

**Evidence rule:**

- **PASS:** Either the result remains canonical under the claimed scope, or the changed context is expressly part of the scope and both results are labeled accordingly; the trusted influence is accounted for.
- **FAIL:** An undeclared outside influence changes a supposedly history-determined canonical result, or two different results collide under one canonical identity.
- **UNKNOWN:** The influencing context cannot be isolated or the contract makes no uniqueness/stability claim.

### B25 — Evolution must not silently reinterpret the past

**Attack map:** `RECOMPUTE · FUTURE · EXTERNALIZE`

**Executable pair and continuation:** Produce the same pre-evolution history under specification versions `s0` and `s1`, where one boundary phrase or action has deliberately different meaning. In one run evolve after the action; in the other evolve before it. Query the old action under “meaning then,” “meaning now,” and an unqualified request, then append one consequence-sensitive action.

**Minimized-witness target:** Two versions, one changed meaning, one evolution cut, one future discriminator.

**Evidence rule:**

- **PASS:** Time-scoped meanings are stable and distinguishable, the unqualified request has a defined rule, and the future action follows the selected interpretation.
- **FAIL:** Upgrade silently rewrites prior application/completion, old and new meanings collide, or recomputation produces a new past without an explicit reinterpretation claim.
- **UNKNOWN:** Version semantics or the query's time scope is not specified.

### B26 — Authored under one version, applied under another

**Attack map:** `FUTURE · MERGE · RECOMPUTE · EXTERNALIZE`

**Executable pair and continuation:** Author action `A` under `s0`. In `h0`, apply it before evolution to `s1`; in `h1`, evolve first and then present the same authored action. Crash once between authoring and application and once between application and completion. Query which meaning governed each phase and retry where permitted.

**Minimized-witness target:** One authored action, one evolution boundary, one adjacent crash cut.

**Evidence rule:**

- **PASS:** Authoring, application, and completion meanings obey an explicit version rule across both crash placements; retries and explanations agree with physical effects.
- **FAIL:** The authored meaning floats silently, application is confused with authoring, recovery selects a different version without disclosure, or the same visible answer hides different physical obligations.
- **UNKNOWN:** The contract does not define cross-version authored actions.

### B27 — Future extension unknown to an older interpreter

**Attack map:** `FUTURE · DELETE · DERIVE`

**Executable pair and continuation:** Extend a valid history by exactly one future-version occurrence that an older interpreter does not understand. Ask the older interpreter for a bounded observation, a query unaffected by the extension, a query dependent on it, and an action explanation. Compare with the prefix lacking the extension.

**Minimized-witness target:** One future occurrence, one older interpreter, one unaffected and one affected query.

**Evidence rule:**

- **PASS:** Unaffected answers remain valid; dependent answers explicitly preserve unknown/unsupported status rather than deleting the occurrence; no fabricated interpretation drives an action.
- **FAIL:** Unknown becomes absent, the whole history becomes non-total, an affected query is answered as if the future occurrence were understood, or the occurrence leaks to a viewer without permission.
- **UNKNOWN:** The contract excludes all future-version input rather than claiming total handling of it.

### B28 — Externalized adaptive controller context

**Attack map:** `EXTERNALIZE · MERGE · FUTURE`

**Executable pair and continuation:** Hold the claimed system history and current viewer projection fixed. Give an adaptive controller two different prior observation contexts that lead it to choose different next authored actions. Ask the contract to explain each choice and to state whether replay from the claimed history determines it.

**Minimized-witness target:** One differing prior observation, one adaptive branch, two next actions.

**Evidence rule:**

- **PASS:** The controller influence is within the stated determination scope or the replay/explanation claim is explicitly conditional on it; each choice is explained from authorized evidence.
- **FAIL:** Different actions are both claimed to be determined by an identical in-scope history, or hidden controller context is omitted from a causal/canonical claim.
- **UNKNOWN:** The controller behavior cannot be held apart from the system prefix.

### B29 — Externalized capture omission

**Attack map:** `EXTERNALIZE · DELETE · MERGE`

**Executable pair and continuation:** Run the same physically established boundary history twice. In one run, the contract's capture influence can expose every occurrence within bound; in the other, remove exactly one causally relevant occurrence from what that influence can provide. Ask whether the occurrence happened, why the later action happened, and whether the history is complete for the query.

**Minimized-witness target:** One omitted occurrence, one dependent action, one bounded query.

**Evidence rule:**

- **PASS:** Unavailability is distinguished from non-occurrence, dependent explanations become appropriately conditional/unknown, and completeness is not asserted beyond evidence.
- **FAIL:** Capture omission rewrites physical history, a later action receives a fabricated cause, or equal captured projections are called equal full histories.
- **UNKNOWN:** The physical history cannot be independently established.

### B30 — Externalized selector choice

**Attack map:** `EXTERNALIZE · COLLIDE · DERIVE`

**Executable pair and continuation:** Present the same finite set of permitted alternatives twice while varying exactly one selector influence outside the claimed determination scope, causing different alternatives to be chosen. Give both choices the same selection identity if the boundary allows it. Query why the alternative was selected and whether it is canonical or merely permitted.

**Minimized-witness target:** Two alternatives, one selector-context change, one choice.

**Evidence rule:**

- **PASS:** Choice is attributed to the selector scope, “permitted” is not inflated to “canonical/necessary,” and public identity does not imply false equality.
- **FAIL:** An outside selector determines an allegedly history-determined choice, two choices collide as one, or a derived justification is contradicted by the alternative run.
- **UNKNOWN:** Selection and admissibility cannot be observed separately.

### B31 — Manifest/specification identity collision

**Attack map:** `COLLIDE · EXTERNALIZE · FUTURE · TCB`

**Executable pair and continuation:** Use two materially different permitted manifests or specifications that share the same public name or version text. Run the same prefix whose next legal action differs between them. Ask which contract governs, request MAY/MUST for that action, and attempt it.

**Minimized-witness target:** One shared public identity, one semantic difference, one action.

**Evidence rule:**

- **PASS:** The governing context is unambiguous at the claimed boundary, MAY/MUST and action behavior match it, and the source of trust is within the declared TCB.
- **FAIL:** The collision yields inconsistent answers under one asserted identity, one context is silently selected, or a manifest/specification outside scope controls legality.
- **UNKNOWN:** The governing context cannot be independently distinguished.

### B32 — Human-local validation burden

**Attack map:** `COGNITION · DELETE · EXTERNALIZE`

**Executable pair and continuation:** Give a permitted human reviewer exactly the bounded material the contract claims is sufficient to validate an observation, MAY/MUST answer, action explanation, and canonical witness. Create an adjacent case differing by one hidden or external fact that flips correctness while leaving the supplied material equal. Measure against the contract's stated time, step, expertise, and access limits.

**Minimized-witness target:** One answer, one omitted decisive fact, one reviewer task, one claimed resource bound.

**Evidence rule:**

- **PASS:** Reviewers can decide correctness within every stated burden bound, or the contract correctly declines local verifiability; equal supplied material never supports opposite decisive judgments.
- **FAIL:** A claimed locally checkable answer requires undisclosed access, unbounded search, special knowledge beyond the claim, or guesswork between the adjacent cases.
- **UNKNOWN:** No human-burden claim or measurable bound is stated, or the study lacks enough controlled trials to assess that claim.

### B33 — MAY/MUST and vacuity cognition trap

**Attack map:** `COGNITION · MERGE · DERIVE`

**Executable pair and continuation:** Present matched human-facing answers for B13's mixed carrier set and B14's empty carrier set, varying only MAY/MUST and vacuity wording. Ask authorized reviewers to choose whether an action is possible, guaranteed across carriers, or impossible, then let them request the offered witness.

**Minimized-witness target:** Two cases, one quantifier distinction, one decision, one witness request.

**Evidence rule:**

- **PASS:** Under the contract's claimed comprehension burden, reviewers distinguish existential, universal, and vacuous results and do not authorize action from a nonexistent carrier.
- **FAIL:** Presentation merges the quantifiers, hides vacuity, or systematically induces an action contrary to the executable carrier evidence.
- **UNKNOWN:** The contract makes no human interpretability claim or the reviewer population/bound is unspecified.

### B34 — TCB closure under one-at-a-time perturbation

**Attack map:** `TCB · EXTERNALIZE · COLLIDE`

**Executable pair and continuation:** For the finite trusted influences named by the contract and for each known boundary influence in this pack—viewer authorization, physical adjudication, clock/bound source, scheduler/controller, capture, selector, manifest/specification, interpreter, canonicalizer, recovery environment, and human adjudication—perturb one at a time while holding the claimed history fixed. Re-run one safety-critical answer and its witness.

**Minimized-witness target:** One answer, one influencing dependency, one perturbation that changes trustworthiness.

**Evidence rule:**

- **PASS:** Every perturbation that can invalidate the answer is inside the declared TCB or causes the answer to lose/limit its trust claim; non-influencing perturbations do not spuriously change a history-determined answer.
- **FAIL:** An undeclared influence can change a trusted answer or make a false answer validate, or two trust contexts collide under one assurance claim.
- **UNKNOWN:** The declared TCB or the finite perturbation surface is unavailable; passing tested members alone does not prove global closure.

### B35 — Circular self-validation

**Attack map:** `TCB · DERIVE · COLLIDE`

**Executable pair and continuation:** Create two matched runs with the same boundary behavior: in one, the answer and validation agree and are correct under an independent oracle; in the other, perturb their shared trusted influence so they agree on the opposite result. Ask for validation, canonical witness, and TCB claim.

**Minimized-witness target:** One proposition, one shared influence, one jointly wrong agreement.

**Evidence rule:**

- **PASS:** The assurance level is explicitly conditional on the shared influence or an independent trusted check rejects the jointly wrong run.
- **FAIL:** Mutual agreement or self-produced evidence is presented as independent correctness, or the shared influence is absent from the TCB.
- **UNKNOWN:** No independent oracle can establish which run is correct.

### B36 — Materially unlike permitted realizations

**Attack map:** `REALIZE · MERGE · TCB`

**Executable pair and continuation:** Execute the same boundary script in two contract-permitted realizations that differ materially in implementation technology or physical failure domain, not merely configuration. Include one action with an externally checkable completion condition, one crash/recovery cut, and one terminal cut. Compare the claimed histories and explanations.

**Minimized-witness target:** Two unlike realizations, one action, one failure cut, one differing physical fact.

**Evidence rule:**

- **PASS:** Cross-realization equivalence is limited to the actually demonstrated boundary properties; realization-specific physical evidence supports completion, recovery, and termination in each case; differences are not erased.
- **FAIL:** Evidence from one realization is reused as proof for the other, unlike physical outcomes are merged into one full history, or a shared name is treated as shared behavior.
- **UNKNOWN:** The two runs are not materially unlike, or physical evidence is available for only one realization.

### B37 — Simulated success versus physical non-completion

**Attack map:** `REALIZE · COLLIDE · DERIVE · FUTURE`

**Executable pair and continuation:** In one permitted realization, make an action reach its declared completion condition. In an unlike physical realization, accept and apply the matched action but induce a physical jam, partition, or loss before completion. Keep boundary acknowledgments equal if possible, then query and retry once.

**Minimized-witness target:** Two realizations, one action, one completion difference, one retry.

**Evidence rule:**

- **PASS:** Completion follows realization-specific physical evidence; the non-completing run is not promoted from application to completion; retry/explanation obey the declared guarantee.
- **FAIL:** A simulated or derived success certifies physical completion elsewhere, equal acknowledgment forces false equality, or the jam is omitted from action-attempt explanation.
- **UNKNOWN:** The physical completion condition is not independently observable.

### B38 — Cross-realization canonical witness ambiguity

**Attack map:** `REALIZE · RECOMPUTE · COLLIDE · EXTERNALIZE`

**Executable pair and continuation:** Arrange two unlike permitted realizations whose boundary outcomes satisfy the same abstract query but whose minimal physical evidence differs. Ask for a canonical witness in each, then recompute each answer in the other realization's interpretation/canonicalizer context.

**Minimized-witness target:** Two realizations, one query, two distinct minimal physical witnesses, one context swap.

**Evidence rule:**

- **PASS:** Canonicality is explicitly realization-scoped or a cross-realization rule validly chooses among both; every witness remains tied to the physical facts it can establish.
- **FAIL:** One realization's witness is claimed to prove the other's physical fact, context swapping silently changes canonicality, or distinct physical evidence collides under a stronger identity than demonstrated.
- **UNKNOWN:** The contract makes no cross-realization canonical claim or the physical witnesses cannot be independently validated.

## 5. Required composite runs

Single-axis success is insufficient where the contract composes guarantees. Run these finite combinations after the individual attacks:

| Composite | Required sequence | Primary attacks |
|---|---|---|
| `C1 Projection × action × crash` | hidden attempt → application → crash before completion → recovery → viewer-relative explanation | B01, B03, B05, B06 |
| `C2 Nondeterminism × scheduler × evolution` | branch → adaptive scheduler choice → specification evolution → replay query | B09, B11, B12, B25 |
| `C3 MAY/MUST × depth × recovery` | two carriers → consume final depth on one → crash → recover → repeat quantifier query | B13, B16, B17, B19 |
| `C4 Terminal × physical realization` | apply action → physical completion differs → terminal crash → post-terminal query | B21, B22, B36, B37 |
| `C5 Canonical × viewer × external context` | diamond witness → projection difference → canonicalizer context change → recompute | B02, B23, B24 |
| `C6 Human × TCB × vacuity` | empty carrier → human guarantee decision → perturb shared trusted influence | B14, B33, B34, B35 |

For each composite, use the same PASS/FAIL/UNKNOWN discipline as the component attacks. Minimize first by deleting whole axes; if the failure disappears only when all named axes remain, report the smallest cross-axis history and continuation.

## 6. Coverage ledger

| Required pressure | Direct attacks |
|---|---|
| Full history versus viewer projection | B01–B04, B08, B15 |
| Occurrence/application/completion | B03, B05–B07, B17, B20, B26, B37 |
| Labeled versus hidden nondeterminism | B09–B10 |
| Scheduler identity on divergent adaptive paths | B11–B12 |
| Action visibility and attempt explanation | B02–B07, B19–B20 |
| MAY/MUST carrier and vacuity | B13–B15, B33 |
| Remaining capability/depth across recovery | B16–B19 |
| Terminal crashes and post-terminal totality | B20–B22 |
| Canonical witness ambiguity | B23–B24, B38 |
| Evolution | B25–B27, B31 |
| External controller/capture/selector/manifest/specification/canonicalizer context | B12, B24, B28–B31 |
| Human burden | B14, B32–B33 |
| Trusted computing base | B21, B24, B31, B34–B36 |
| Materially unlike physical realization evidence | B05–B06, B21, B36–B38 |
| Total and bounded handling | B00, B08, B16, B20–B22, B27 |

## 7. Stop conditions

An attack campaign stops with one of three outcomes:

- **PASS for this finite pack:** every applicable individual and composite attack has PASS evidence under the fixed contract scope.
- **FAIL:** at least one minimized finite counterexample remains reproducible. One FAIL dominates any number of passes.
- **UNKNOWN:** no FAIL was established, but at least one applicable obligation lacks the finite independent evidence required for PASS. UNKNOWN must not be marketed as conformance.

Passing this pack establishes only resistance to these finite attacks at the declared bounds, viewers, versions, schedules, and realizations. It does not establish correctness outside that scope.
