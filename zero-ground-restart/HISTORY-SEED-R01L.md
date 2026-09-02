# HISTORY-SEED-R01L — zero-ground history/distinguishability seed

## Status, scope, and freeze rule

This is a first-milestone falsification seed, not a kernel, architecture, data model, package, or claim of global minimality. It starts with boundary histories and asks only which past distinctions can change required future boundary behavior.

This draft was reasoned independently under strict quarantine. Before freezing it, the builder did not list, read, search, inspect, hash, or otherwise access the repository, Git, existing workspace files, prior drafts, attacks, counterexamples, archives, or advisors. The only implementation work before the file was created was an in-memory execution of the code printed below; it read and wrote no files. The digest reported outside this document freezes these exact bytes. No later result may silently change the contract, corpus, candidate selector, minimization order, or expected output.

The narrow conclusion is:

> Between executions, enough information must survive to distinguish accepted effect occurrences, their non-derivable operation/target/argument bytes, their multiplicity and required causal placement, branch snapshot correlations, and completed action-key/snapshot correlations. Actor bytes, current views, answers, explanations, envelopes, indexes, and caches can be rebuilt from that information and the frozen behavioral specification. Rejected, invalid, no-change, observation-only, and boot traffic, old output bytes, and ordering between provably independent accepted effects may be forgotten. No dedicated representation follows from these responsibilities.

This statement is exact for contract `ZG-1` below. Completeness outside `ZG-1`, global minimality even inside `ZG-1`, crash durability, human usability, operational fitness, trusted-computing-base minimality, portability, and materially unlike physical realizations remain **UNKNOWN**.

## 1. One declared boundary

There is exactly one declared boundary, `B`: the cut between an environment-controlled harness and a candidate system. All required observations cross `B` as frames. There is no permitted clock, filesystem convention, network service, process environment, prompt, operator memory, or other ambient input. A realization using any such source must declare it as internal implementation state or add it to a later contract; it is not free here.

The harness is the sole authority to send input frames. The candidate is the sole authority to send output frames. The semantic authority named inside a mutating request is exactly byte `A` (`0x41`) or `B` (`0x42`); it is data checked by the contract, not ambient identity.

### 1.1 Exact frame grammar

An input frame is:

```text
0x49 || U16BE(n) || body[n]
```

An output frame is:

```text
0x4f || U16BE(n) || body[n]
```

`U16BE(n)` is exactly two unsigned big-endian bytes, `0 <= n <= 65535`. `||` is byte concatenation. The direction tag is included in the bytes; therefore input, output, an empty body, and content beginning with `I` or `O` cannot collide. A complete transaction is one complete input frame followed by exactly one complete output frame. The harness sends no new input before that output. A partial frame produces no output and is outside a completed history. Mid-frame restart and concurrent input are unsupported by `ZG-1`, not assumed safe.

A history is the complete byte concatenation of every completed input and output frame that crossed `B` so far. Past output is therefore part of a history even when the contract does not require the candidate to persist it.

Every valid request body is one of these fixed byte strings:

```abnf
boot       = %x42                                      ; "B"
write      = %x57 authority branch value               ; "W" a b v
fork       = %x46 authority branch branch              ; "F" a parent child
delegate   = %x44 authority branch authority           ; "D" a b new
interpret  = %x49 authority branch mode                ; "I" a b mode
query      = %x51 branch query-kind                     ; "Q" b k
act        = %x41 authority branch action-key           ; "A" a b j
explain    = %x45 branch explanation-selector           ; "E" b e

authority  = %x41 / %x42                               ; "A" / "B"
branch     = %x30 / %x31                               ; "0" / "1"
value      = %x78 / %x79                               ; "x" / "y"
mode       = %x30 / %x31                               ; "0" / "1"
action-key = %x30 / %x31                               ; "0" / "1"
query-kind = %x72 / %x74 / %x70 / %x6f / %x6d / %x6a ; r,t,p,o,m,j
explanation-selector = %x63 / %x30 / %x31              ; c,0,1
```

Thus `B`, all `Q` and `E` bodies have lengths 1 or 3, and all mutating bodies have length 4. A complete, well-framed input body not in this grammar returns `N5` and has no semantic effect. A frame claiming more bytes remains partial until those bytes arrive; no sentinel or end-of-file convention exists.

### 1.2 Exact response-body grammar

The output envelope is always the frame above. Its body is exactly one of:

```text
K                            accepted boot or accepted changing mutation
N || reason                  no semantic effect
V || U16BE(n) || bytes[n]    raw or interpreted byte sequence
C || one-byte                parent, controller, or mode
J || one-byte bitmap         completed action keys; bit 0 is key 0
! || U16BE(n) || bytes[n]    first action emission and committed value
= || U16BE(n) || bytes[n]    retry receipt; never a second emission
T || U16BE(n) || event[4*n]  exact causal explanation
```

`reason` is exactly one of: `0` missing branch; `1` unauthorized; `2` child collision or parent equals child; `3` requested controller/mode already current; `4` missing action receipt; `5` invalid body; `6` causal-trace capacity reached. The absent parent is byte `0xff`, not a content sentinel. `C0` and `C1` use ASCII bytes `0` and `1`; controller results are `CA` or `CB`.

### 1.3 Behavioral contract by replay, not by storage prescription

The following is a mathematical oracle for required boundary behavior. Its temporary vocabulary is descriptive notation for replay; none of it is a required persisted category.

At the semantic root, branch `0` exists with controller `A`, mode `0`, empty raw bytes, absent parent (`0xff`), and empty causal explanation. Branch `1` does not exist. No action key is completed. A branch explanation is an ordered sequence of accepted four-byte mutation bodies. Its maximum length is 16,000 events.

Process request bodies as follows:

1. `B` returns `K` and changes nothing. Physically, the harness presents it to a newly started execution after the prior execution has ended. `ZG-1` requires later behavior to survive any number of such between-transaction execution changes, but makes no crash-atomicity promise.
2. `W a b v` returns `K`, appends `v` to branch `b`'s raw bytes, and appends the exact request body to that branch's causal explanation iff `b` exists, `a` is its current controller, and its explanation has fewer than 16,000 events. Otherwise it returns `N0`, `N1`, or `N6` and changes nothing.
3. `F a p c` returns `K` iff `p` exists, `a` controls `p`, `c` differs from `p` and does not exist, and the parent explanation has fewer than 16,000 events. The child receives the parent's raw bytes, mode, controller, and complete causal explanation at that exact point; its parent is `p`; the fork body is appended to the child's explanation. The parent is unchanged. Failures return `N0`, `N1`, `N2`, or `N6` and change nothing.
4. `D a b n` returns `K`, makes `n` the controller, and appends the body to `b`'s explanation iff `b` exists, `a` controls it, `n != a`, and capacity remains. It otherwise returns `N0`, `N1`, `N3`, or `N6` and changes nothing.
5. `I a b m` is analogous: an authorized different mode becomes current and its exact body is appended. Equal mode returns `N3`. Mode `0` interprets raw bytes identically; mode `1` swaps every `x` with `y` and every `y` with `x`.
6. `Q b r` and `Q b t` return `V` with raw and currently interpreted bytes. `Q b p`, `Q b o`, and `Q b m` return `C` with parent, controller, and mode. `Q b j` returns `J` with a one-byte bitmap of completed keys on `b`. A missing branch returns `N0`. Queries never change the replay result.
7. `A a b j` first checks existence and current control. If `(b,j)` is already completed, it returns `=` with the originally committed interpreted bytes and changes nothing. Otherwise, if capacity remains, it commits the current interpreted bytes and the exact causal explanation `branch-explanation || action-body`, returns the single emission `!` with those bytes, and makes later authorized calls of the same `(b,j)` return `=`. The action does not enter the branch's current explanation. Failure returns `N0`, `N1`, or `N6` and changes nothing.
8. `E b c` returns `T` with the branch's current exact causal explanation. `E b 0` or `E b 1` returns the explanation committed for that action key. Missing branch returns `N0`; missing receipt returns `N4`. Explanation never changes the replay result.

The capacity makes every response fit `U16BE`: an explanation has at most 16,000 four-byte events and a three-byte header. The two branches and two keys per branch also bound all effectful semantic histories, although no-effect traffic can be unbounded.

The named capabilities have only boundary meanings: `W` is authoring; `Q r` is observation; `I` plus `Q t` is interpretation and semantic evolution; every `Q` is querying; `A` is action with retry behavior; `E` is explanation; `D` is authority-policy evolution; and `F` creates a correlated continuation from an exact snapshot. This does not assert that these toy capabilities are sufficient for an unstated application.

### 1.4 Future-observable equivalence

A permitted future is a finite deterministic policy that supplies valid or invalid complete input frames, may choose its next input from exact output bytes observed since the persistence point, and eventually stops. The policy starts with the same private policy state in both comparisons. It is not allowed to ask the candidate to inspect an environment-held copy of the earlier transcript unless it sends those bytes as future input.

For completed histories `h1` and `h2`:

```text
h1 ≡ZG-1 h2
```

iff every permitted common future policy receives exactly the same future output-frame sequence after `h1` and `h2`. Past outputs may already differ; equivalence concerns the residual boundary transducer. A persistent encoding is sound only if:

```text
encode(h1) = encode(h2)  =>  h1 ≡ZG-1 h2.
```

The conceptual minimum persistent state is the quotient of completed histories by `≡ZG-1`. This sentence does not assume that a quotient class is a record, log, graph, object, or any other shape.

## 2. Candidate encodings, only as collision targets

`SEQ(x1,...,xn)` is `U16BE(n) || U16BE(len(x1)) || x1 || ...`. These candidates are evaluated together; none is predeclared an architecture.

1. `EMPTY`: zero bytes.
2. `LAST`: the last complete input frame.
3. `SET`: `SEQ` of lexically sorted distinct accepted effect bodies.
4. `BAG`: `SEQ` of lexically sorted accepted effect bodies, retaining multiplicity.
5. `SURFACE`: canonical current branch/controller/mode/parent/raw values and action key/value/actor/mode values, but no causal explanations.
6. `ACCEPTED4`: `SEQ` of all accepted changing `W/F/D/I` and first `A` bodies in boundary order. Boot, query, explanation, invalid, denied, equal-value, and retry bodies are absent.
7. `PROJECTED3`: as `ACCEPTED4`, but retain only each accepted body's byte positions 0, 2, and 3. Position 1, the actor, is reconstructed during replay from the then-current controller.
8. `ORACLE`: a canonical serialization of the replay notation, including causal explanations and receipts.
9. `FULL`: the entire alternating input/output transcript.
10. `QUOTIENT-D`: the complete behavior vector over the finite future set `D` below. It is a finite-domain control, not a usable general decoder.

`ACCEPTED4` and `PROJECTED3` are sufficient for all `ZG-1` histories by induction: start from the fixed semantic root; for each accepted triple, derive the actor from the current controller of its target (the parent for `F`), reconstruct the four-byte body, and apply the frozen transition. A corrupt triple that cannot be accepted at that point must fail closed rather than be skipped. Identity transitions were omitted. The induction reconstructs the oracle result; identical reconstructed results have identical future transitions. This is a sufficiency proof, not a minimality proof. `PROJECTED3` still retains unnecessary order between independent effects.

## 3. Simultaneous total-system disposition

No weighted score or sequential optimization is used. Each row is one total-system disposition across every required dimension at once.

| Candidate | Information/distinction preservation and loss risk | Persistent state, storage, runtime, query/navigation | Semantic machinery, operations, TCB, evolution | Human cognition, authoring, explainability, portability/realization |
|---|---|---|---|---|
| `EMPTY`, `LAST`, `SET`, `BAG`, `SURFACE` | **FAIL** with concrete collisions in section 4; demonstrated information-loss risk is decisive regardless of their low byte counts | Low persistence merely moves missing distinctions elsewhere; `SURFACE` makes ordinary reads cheap but explanations unsound | Filtering/materialization still requires semantics; `SURFACE` adds update and recovery paths; none has a valid evolution story after collision | Authoring bytes are simple, but a person/service would have to remember lost multiplicity, order, receipts, or causes; portability cannot repair a semantic collision |
| `FULL` | Passes bounded search and is trivially injective on past transcripts; lowest deletion risk but retains non-influential distinctions | Unbounded storage under no-effect traffic; replay/query cost grows with all traffic; navigation is linear because no search facility exists | Small ingestion selector, larger parser/replay/recovery burden; transcript migrations and privacy/retention operations are costly; TCB includes full parser and replay | Easy to explain what crossed the boundary, hard to discover what matters; no extra authoring burden; physical portability and realization remain UNKNOWN |
| `ACCEPTED4` | Passes bounded search and has the full-contract induction proof; retains redundant actor and independent order, so is not the quotient | Exactly `2 + 6n` bytes under `SEQ` for `n` accepted effects; rebuild/query is linear without indexes; storage is bounded by effect caps | Correct acceptance filtering moves into ingestion TCB; replay/specification are correctness-critical; evolution requires a new versioned contract, never reinterpretation by ambient code | Low wire authoring burden; human review must follow causal order; `E` provides exact machine explanation; portability and physical realization remain UNKNOWN |
| `PROJECTED3` | Passes the greedy bounded attack; full-contract actor reconstruction proof; independent order is still redundant; fresh/global minimality UNKNOWN | Exactly `2 + 5n` bytes for the simple global-order encoding; linear rebuild and query; no search/navigation infrastructure | Actor reconstruction moves work to replay and expands TCB; corrupt sequence validation is mandatory; later grammar changes can invalidate the derivation and therefore require a new explicit version | One fewer persisted byte per event increases reviewer inference; tools must render actors and causes; authoring unchanged; cross-realization claims UNKNOWN |
| `ORACLE` | Passes bounded search; preserves distinctions but duplicates values derivable from explanations | Faster direct queries; more bytes from copied fork traces and materialized views; update, atomicity, and cache consistency costs appear | Larger write/recovery TCB and migration surface; every denormalized value needs verification | Easier local inspection, harder invariant verification; realization-neutrality is only syntactic and remains UNKNOWN physically |
| `QUOTIENT-D` | Exactly collision-free only for finite `D`; 269 observed classes need at least 9 label bits, but no completeness follows | A 9-bit label would require an external 7,240-history/655-future mapping and decoder; the script instead stores the full vector; lookup can be fast only with that machinery | Semantic complexity, future enumeration, decoder storage, evolution invalidation, and trust move into the table generator; highest silent-loss risk outside `D` | Opaque to authors and reviewers; weak explanation without reverse maps; no evidence of portability or material realization |

There is no declared winner. `PROJECTED3` is the smallest simple sufficient seed found here; `ORACLE` trades storage and update risk for reads; `FULL` trades storage for low filtering risk; the conceptual quotient may dominate them but has no complete construction. Search, indexing, compiler generation, verification, cache invalidation, crash recovery, and trust are not counted as zero merely because this milestone omits them.

## 4. Deterministic finite collision experiment

### 4.1 Authorities, roots, corpus, and branch correlations

The experiment authority is the exact frozen code block below. The behavioral authority is contract `ZG-1` in this file. The only semantic authorities are bytes `A` and `B`. The enumeration root is the one-request history `(B)` evaluated from the semantic root branch `0`; there is no other implicit seed.

Let the ordered history alphabet be exactly:

```text
B, WA0x, WA0y, WB0x, WA1x, FA01, FB01, DA0B, DB0A,
IA01, IA00, IB01, AA00, AA01, AB00, Q0r, Q1p, E00, E0c
```

The corpus contains `(B) || tail` for every tail of length 0, 1, 2, or 3 over that ordered alphabet: exactly `1 + 19 + 19^2 + 19^3 = 7,240` histories. Enumeration is depth first by length, then product order. Outputs are generated by replay and included in each history. `F` copies the parent's exact prefix at its position; later parent and child effects are independent. A first `A` binds its key to its exact branch prefix. These are the only branch correlations.

Let the ordered future-command alphabet be exactly:

```text
B, WA0x, WA0y, WB0x, WA1x, FA01, FB01, DA0B, DB0A,
IA01, IA00, IB01, Q0r, Q0t, Q0o, Q0m, Q0p, Q1r, Q1p,
AA00, AA01, AB00, E00, E01, E0c
```

The future set first contains every length-1 sequence, then every length-2 product sequence: `25 + 25^2 = 650`. It then contains these five two-step adaptive policies, in order. `prefix` is tested against the first unframed response body; the selected second request is then issued.

```text
first  prefix  if true  if false
Q0o    CA      WA0x     WB0x
Q0m    C0      IA01     IA00
Q1p    C0      Q0r      Q1r
AA00   !       AA00     E00
E00    T       AA00     WA0x
```

Thus `D` has exactly 655 futures. All output comparisons use complete output-frame bytes. A bounded equivalence signature is the ordered vector of all 655 output sequences.

### 4.2 Collision and minimization rule

For each candidate, group histories by exact encoding bytes. A collision survives iff two members have unequal bounded signatures. Among all surviving pairs choose the lexicographically least key:

```text
(sum of tail lengths,
 max tail length,
 lexically smaller complete transcript,
 lexically larger complete transcript)
```

For that pair, the witness is the first distinguishing future in the declared future order. This is the exact meaning of “minimized” in this experiment; it does not claim an absolute minimum under a different grammar or cost metric.

Deletion begins with ordered accepted four-byte bodies. It attempts byte positions in fixed order `1, 0, 2, 3`; after each successful deletion it restarts. It then tries conversion to `BAG` and `SET`. A deletion is retained only if no bounded collision exists. When no deletion succeeds, the script prints the smallest witness for deleting each survivor and for losing order/multiplicity.

### 4.3 Executable reference

Run with CPython 3 in isolated mode by supplying this block to `python3 -I -`. It imports nothing, reads no files, writes no files, uses no randomness, locale, time, network, environment variable, hash table iteration order for emitted ordering, or external selector.

```python
def u16(n): return bytes((n >> 8, n & 255))
def frm(d,b): return d+u16(len(b))+b
def seq(xs): return u16(len(xs))+b''.join(u16(len(x))+x for x in xs)
def init(): return (((48,65,48,255,b'',()),),())
def maps(s):
    bs={x[0]:list(x) for x in s[0]};rs={(x[0],x[1]):list(x) for x in s[1]}
    for x in bs.values():x[5]=list(x[5])
    for x in rs.values():x[5]=list(x[5])
    return bs,rs
def canon(bs,rs):
    B=[]
    for k in sorted(bs):
        x=bs[k];x[5]=tuple(x[5]);B.append(tuple(x))
    R=[]
    for k in sorted(rs):
        x=rs[k];x[5]=tuple(x[5]);R.append(tuple(x))
    return tuple(B),tuple(R)
def step(s,c):
    bs,rs=maps(s)
    def no(x):return s,b'N'+x
    if c==b'B':return s,b'K'
    if len(c)==4 and c[0]==87 and c[1] in b'AB' and c[2] in b'01' and c[3] in b'xy':
        a,b,v=c[1],c[2],c[3]
        if b not in bs:return no(b'0')
        if bs[b][1]!=a:return no(b'1')
        if len(bs[b][5])>=16000:return no(b'6')
        bs[b][4]+=bytes((v,));bs[b][5].append(c);return canon(bs,rs),b'K'
    if len(c)==4 and c[0]==70 and c[1] in b'AB' and c[2] in b'01' and c[3] in b'01':
        a,p,ch=c[1],c[2],c[3]
        if p not in bs:return no(b'0')
        if bs[p][1]!=a:return no(b'1')
        if ch in bs or ch==p:return no(b'2')
        if len(bs[p][5])>=16000:return no(b'6')
        q=bs[p];bs[ch]=[ch,q[1],q[2],p,q[4],q[5]+[c]];return canon(bs,rs),b'K'
    if len(c)==4 and c[0]==68 and c[1] in b'AB' and c[2] in b'01' and c[3] in b'AB':
        a,b,n=c[1],c[2],c[3]
        if b not in bs:return no(b'0')
        if bs[b][1]!=a:return no(b'1')
        if n==a:return no(b'3')
        if len(bs[b][5])>=16000:return no(b'6')
        bs[b][1]=n;bs[b][5].append(c);return canon(bs,rs),b'K'
    if len(c)==4 and c[0]==73 and c[1] in b'AB' and c[2] in b'01' and c[3] in b'01':
        a,b,m=c[1],c[2],c[3]
        if b not in bs:return no(b'0')
        if bs[b][1]!=a:return no(b'1')
        if m==bs[b][2]:return no(b'3')
        if len(bs[b][5])>=16000:return no(b'6')
        bs[b][2]=m;bs[b][5].append(c);return canon(bs,rs),b'K'
    if len(c)==4 and c[0]==65 and c[1] in b'AB' and c[2] in b'01' and c[3] in b'01':
        a,b,j=c[1],c[2],c[3]
        if b not in bs:return no(b'0')
        if bs[b][1]!=a:return no(b'1')
        if (b,j) in rs:
            v=rs[(b,j)][3];return s,b'='+u16(len(v))+v
        if len(bs[b][5])>=16000:return no(b'6')
        q=bs[b];v=q[4].translate(bytes.maketrans(b'xy',b'yx')) if q[2]==49 else q[4]
        t=tuple(q[5]+[c]);rs[(b,j)]=[b,j,a,v,q[2],t];return canon(bs,rs),b'!'+u16(len(v))+v
    if len(c)==3 and c[0]==81 and c[1] in b'01' and c[2] in b'rtpomj':
        b,k=c[1],c[2]
        if b not in bs:return no(b'0')
        q=bs[b]
        if k==114:v=q[4];return s,b'V'+u16(len(v))+v
        if k==116:
            v=q[4].translate(bytes.maketrans(b'xy',b'yx')) if q[2]==49 else q[4];return s,b'V'+u16(len(v))+v
        if k==112:return s,b'C'+bytes((q[3],))
        if k==111:return s,b'C'+bytes((q[1],))
        if k==109:return s,b'C'+bytes((q[2],))
        mask=sum(1<<(x[1]-48) for x in rs.values() if x[0]==b);return s,b'J'+bytes((mask,))
    if len(c)==3 and c[0]==69 and c[1] in b'01' and c[2] in b'c01':
        b,j=c[1],c[2]
        if b not in bs:return no(b'0')
        if j==99:t=bs[b][5]
        else:
            if (b,j) not in rs:return no(b'4')
            t=rs[(b,j)][5]
        return s,b'T'+u16(len(t))+b''.join(t)
    return no(b'5')
def run(st,cmds):
    outs=[]
    for c in cmds:st,o=step(st,c);outs.append(frm(b'O',o))
    return st,tuple(outs)
def transcript(cmds,outs):return b''.join(frm(b'I',c)+o for c,o in zip(cmds,outs))
def accepted(cmds):
    st=init();a=[]
    for c in cmds:
        ns,o=step(st,c)
        if ns!=st:a.append(c)
        st=ns
    return tuple(a)
def surf(st):
    B=[bytes((b,c,m,p))+u16(len(r))+r for b,c,m,p,r,t in st[0]]
    R=[bytes((b,j,a,m))+u16(len(v))+v for b,j,a,v,m,t in st[1]]
    return b'B'+seq(B)+b'R'+seq(R)
def oracle(st):
    B=[bytes((b,c,m,p))+u16(len(r))+r+seq(t) for b,c,m,p,r,t in st[0]]
    R=[bytes((b,j,a,m))+u16(len(v))+v+seq(t) for b,j,a,v,m,t in st[1]]
    return b'B'+seq(B)+b'R'+seq(R)
H=(b'B',b'WA0x',b'WA0y',b'WB0x',b'WA1x',b'FA01',b'FB01',b'DA0B',b'DB0A',b'IA01',b'IA00',b'IB01',b'AA00',b'AA01',b'AB00',b'Q0r',b'Q1p',b'E00',b'E0c')
F=(b'B',b'WA0x',b'WA0y',b'WB0x',b'WA1x',b'FA01',b'FB01',b'DA0B',b'DB0A',b'IA01',b'IA00',b'IB01',b'Q0r',b'Q0t',b'Q0o',b'Q0m',b'Q0p',b'Q1r',b'Q1p',b'AA00',b'AA01',b'AB00',b'E00',b'E01',b'E0c')
tails=[()];level=[()]
for depth in range(1,4):level=[p+(c,) for p in level for c in H];tails+=level
hist=[]
for tail in tails:
    cmds=(b'B',)+tail;st,outs=run(init(),cmds);hist.append((cmds,outs,st,accepted(cmds),transcript(cmds,outs)))
futs=[('N',(c,)) for c in F]+[('N',(a,b)) for a in F for b in F]
ads=((b'Q0o',b'CA',b'WA0x',b'WB0x'),(b'Q0m',b'C0',b'IA01',b'IA00'),(b'Q1p',b'C0',b'Q0r',b'Q1r'),(b'AA00',b'!',b'AA00',b'E00'),(b'E00',b'T',b'AA00',b'WA0x'))
futs += [('A',x) for x in ads]
def feval(st,f):
    if f[0]=='N':return run(st,f[1])[1]
    first,pref,yes,no=f[1];ns,o=step(st,first);c=yes if o.startswith(pref) else no
    ns2,o2=step(ns,c);return frm(b'O',o),frm(b'O',o2)
states=[];sid={}
for h in hist:
    if h[2] not in sid:sid[h[2]]=len(states);states.append(h[2])
sigs=[tuple(feval(st,f) for f in futs) for st in states]
sig_to_eq={};eq=[]
for x in sigs:
    if x not in sig_to_eq:sig_to_eq[x]=len(sig_to_eq)
    eq.append(sig_to_eq[x])
def eempty(h):return b''
def elast(h):return frm(b'I',h[0][-1])
def eset(h):return seq(sorted(set(h[3])))
def ebag(h):return seq(sorted(h[3]))
def eaccept(h):return seq(h[3])
def esurf(h):return surf(h[2])
def eoracle(h):return oracle(h[2])
def efull(h):return h[4]
def equot(h):return seq([seq(x) for x in sigs[sid[h[2]]]])
cands=(('empty',eempty),('last',elast),('set',eset),('bag',ebag),('surface',esurf),('accepted',eaccept),('oracle',eoracle),('full',efull),('quotient-D',equot))
def hkey(i,j):
    a,b=hist[i],hist[j];la=len(a[0])-1;lb=len(b[0])-1
    return la+lb,max(la,lb),min(a[4],b[4]),max(a[4],b[4])
def fwit(i,j):
    si=sigs[sid[hist[i][2]]];sj=sigs[sid[hist[j][2]]]
    for z,(a,b) in enumerate(zip(si,sj)):
        if a!=b:return z
def collision(fn):
    groups={};best=None
    for i,h in enumerate(hist):
        k=fn(h);q=eq[sid[h[2]]]
        if k not in groups:groups[k]={q:i};continue
        if q not in groups[k]:
            for oq,j in groups[k].items():
                p=hkey(i,j),j,i,fwit(j,i)
                if best is None or p[0]<best[0]:best=p
            groups[k][q]=i
    return best
print('histories',len(hist),'states',len(states),'futures',len(futs),'equivalence_classes',len(sig_to_eq))
for n,fn in cands:
    z=collision(fn)
    if z is None:print(n,'PASS')
    else:
        _,i,j,w=z
        print(n,'FAIL',[x.decode() for x in hist[i][0]],[x.decode() for x in hist[j][0]],'future',futs[w],'outs',sigs[sid[hist[i][2]]][w],sigs[sid[hist[j][2]]][w])
def proj(mask,mode):
    def f(h):
        ev=[bytes(c[k] for k in range(4) if k in mask) for c in h[3]]
        if mode=='bag':ev=sorted(ev)
        if mode=='set':ev=sorted(set(ev))
        return seq(ev)
    return f
mask=(0,1,2,3);mode='ordered';deleted=[];changed=True
while changed:
    changed=False
    for k in (1,0,2,3):
        if k not in mask:continue
        m=tuple(x for x in mask if x!=k)
        if collision(proj(m,mode)) is None:
            mask=m;deleted.append('byte'+str(k));changed=True;break
    if changed:continue
    for md in ('bag','set'):
        if md==mode:continue
        if collision(proj(mask,md)) is None:
            mode=md;deleted.append('structure->'+md);changed=True;break
print('greedy_projection',mask,mode,'deleted',deleted)
for k in range(4):
    if k in mask:
        z=collision(proj(tuple(x for x in mask if x!=k),mode));print('delete_survivor',k,'witness',[x.decode() for x in hist[z[1]][0]],[x.decode() for x in hist[z[2]][0]],'future',futs[z[3]])
if mode=='ordered':
    for md in ('bag','set'):
        z=collision(proj(mask,md));print('delete_order_as',md,'witness',[x.decode() for x in hist[z[1]][0]],[x.decode() for x in hist[z[2]][0]],'future',futs[z[3]])
```

### 4.4 Exact expected output and evidence boundary

```text
histories 7240 states 285 futures 655 equivalence_classes 269
empty FAIL ['B'] ['B', 'AA00'] future ('N', (b'AA00',)) outs (b'O\x00\x03!\x00\x00',) (b'O\x00\x03=\x00\x00',)
last FAIL ['B'] ['B', 'AA00', 'B'] future ('N', (b'AA00',)) outs (b'O\x00\x03!\x00\x00',) (b'O\x00\x03=\x00\x00',)
set FAIL ['B', 'WA0x'] ['B', 'WA0x', 'WA0x'] future ('N', (b'Q0r',)) outs (b'O\x00\x04V\x00\x01x',) (b'O\x00\x05V\x00\x02xx',)
bag FAIL ['B', 'IA01', 'AA00'] ['B', 'AA00', 'IA01'] future ('N', (b'E00',)) outs (b'O\x00\x0bT\x00\x02IA01AA00',) (b'O\x00\x07T\x00\x01AA00',)
surface FAIL ['B'] ['B', 'DA0B', 'DB0A'] future ('N', (b'E0c',)) outs (b'O\x00\x03T\x00\x00',) (b'O\x00\x0bT\x00\x02DA0BDB0A',)
accepted PASS
oracle PASS
full PASS
quotient-D PASS
greedy_projection (0, 2, 3) ordered deleted ['byte1']
delete_survivor 0 witness ['B', 'FA01'] ['B', 'AA01'] future ('N', (b'WA1x',))
delete_survivor 2 witness ['B', 'FA01', 'WA0x'] ['B', 'FA01', 'WA1x'] future ('N', (b'Q0r',))
delete_survivor 3 witness ['B', 'AA00'] ['B', 'AA01'] future ('N', (b'AA00',))
delete_order_as bag witness ['B', 'DA0B', 'AB00'] ['B', 'AA00', 'DA0B'] future ('N', (b'E00',))
delete_order_as set witness ['B', 'WA0x'] ['B', 'WA0x', 'WA0x'] future ('N', (b'Q0r',))
```

The builder's in-memory run matched this output. That establishes only reproducibility on one undeclared CPython realization, not completeness or portability. A conforming evidence run must capture: the frozen draft digest; exact extracted code bytes; interpreter executable digest and version; complete stdout/stderr; exit status; and machine manifest. Any exception, output mismatch, omitted candidate, unenumerated case, output truncation, unverifiable extraction, or absent artifact is **FAIL/UNKNOWN**, never a pass. The code, Python byte semantics, extraction procedure, OS process, and captured evidence chain are in the experiment TCB. A passing finite run means only “no collision was found in `D`.”

### 4.5 Post-freeze fresh and hidden attacks

The seed freezes at its externally reported digest before any breaker result may be read.

The deterministic fresh-domain suite `D1` is:

* histories `(B) || tail` for all tails of exactly length 4 over the same 19-command history alphabet (`19^4 = 130,321` new histories), plus all `D` histories;
* all one- and two-step `D` futures plus all 125 three-step products over the ordered subset `(B, DA0B, IA01, FA01, AA00)` followed by `(WA0x, Q0r, Q0t, E0c, AA00)` followed by that same second set;
* seven depth-3 adaptive policies obtained by taking the five declared policies and, after their second response, issuing respectively `E0c`, `Q0r`, `Q0t`, `AA00`, `Q0o`, then two additional policies: `FA01; if K then WA1x else Q1p; then Q1r`, and `DA0B; if K then AB00 else AA00; then E00`.

The same exact collision/minimization rule applies. `D1` has not been run as evidence in this seed; its result is **UNKNOWN**. The induction proof predicts no `PROJECTED3` collision, but a prediction is not evidence.

A hidden bundle is admissible only if an independent breaker fixed its bytes before receiving this draft, publishes a pre-reveal SHA-256 commitment, and later reveals complete in-contract histories and finite adaptive policies with all oracle outputs. The harness must first validate every frame against `ZG-1`, recompute oracle outputs, and reject the entire bundle on the first mismatch. A hidden collision outranks every finite pass and must be minimized under the same key. Breaker independence, precommit timing, and identity are external evidence requirements and currently **UNKNOWN**. Out-of-contract examples may motivate `ZG-2`, but cannot be relabeled as `ZG-1` failures or successes.

## 5. Mandatory attack ledger

The following attacks apply to each proposed surviving responsibility or correctness mechanism. “Move” names where complexity goes after simplification.

### 5.1 Accepted effect occurrence and non-derivable bytes

* **DELETE / MERGE / COLLIDE:** deleting an accepted occurrence merges `(B)` with `(B,WA0x)`; future `Q0r` returns `V 0000` versus `V 0001 x`. Deleting operation byte 0 merges `(B,FA01)` with `(B,AA01)` under the projection; future `WA1x` returns `K` versus `N0`. Deleting target byte 2 merges `(B,FA01,WA0x)` with `(B,FA01,WA1x)`; future `Q0r` returns `x` versus empty. Deleting argument byte 3 merges `(B,AA00)` with `(B,AA01)`; future `AA00` returns `=` versus `!`. These are the script's exact minima.
* **DERIVE / RECOMPUTE:** the actor byte is derivable from the prior controller and was deleted. Operation, target, argument, and occurrence are not derivable from the remaining accepted projection; the witnesses show why deterministic regeneration cannot supply them.
* **FUTURE:** a future query, write, retry, or explanation distinguishes each collision without asking for a past transcript.
* **EXTERNALIZE:** omission would require a service, operator, prompt, or old transcript to remember the lost byte. None is inside `B`; relying on it would change the contract. Filtering only accepted effects moves parsing, authorization, capacity checks, and acknowledgement-before-persist ordering into the ingestion TCB.
* **REALIZE:** bytes can be represented many ways in principle, but no unlike physical pair has been evidenced. Result: **UNKNOWN**.
* **COGNITION:** dropping actor bytes saves storage but makes a reviewer replay controller changes. A renderer must reconstruct them; otherwise human verification burden rises.
* **TCB:** correctness rests on the parser, accepted/no-effect selector, actor reconstruction, replay, framing, and durable acknowledgement discipline. None is zero complexity.

### 5.2 Multiplicity and required causal placement

* **DELETE / MERGE / COLLIDE:** converting to a set merges `(B,WA0x)` and `(B,WA0x,WA0x)`; `Q0r` returns `x` versus `xx`. Converting to a bag merges `(B,IA01,AA00)` and `(B,AA00,IA01)`; `E00` returns `T 0002 IA01 AA00` versus `T 0001 AA00`. Swapping `(B,WA0x,WA0y)` and `(B,WA0y,WA0x)` is distinguished by `Q0r` (`xy` versus `yx`).
* **DERIVE / RECOMPUTE:** neither duplicate count nor causal position is a deterministic function of the unordered distinct bytes. Required order can be reduced to a causal partial order, but no complete minimal encoding of that relation is claimed.
* **FUTURE:** raw query, current explanation, action explanation, and retry behavior can expose multiplicity or placement after arbitrarily many boots.
* **EXTERNALIZE:** a queue service, timestamp authority, human convention, or source-file order would merely hold the relation elsewhere. None is permitted ambient state.
* **REALIZE:** materially unlike implementations of the same ordering relation are plausible but unevidenced: **UNKNOWN**.
* **COGNITION:** removing explicit global order can reduce irrelevant chronology but requires a person/tool to understand the exact causal relation and canonical explanation order.
* **TCB:** a partial-order realization moves correctness into relation construction, topological rendering, concurrent update, and recovery code. `PROJECTED3` deliberately pays redundant global-order storage to avoid claiming that machinery free.

### 5.3 Branch snapshot and lineage correlation

* **DELETE / MERGE / COLLIDE:** `(B)` and `(B,FA01)` collide if child existence/fork information is deleted; `Q1p` returns `N0` versus `C0`. More sharply, `(B,WA0x,FA01,WA0y)` and `(B,WA0x,WA0y,FA01)` differ only in the fork's causal placement relevant here; future `Q1r` returns `x` versus `xy`.
* **DERIVE / RECOMPUTE:** a dedicated parent field and copied child surface are derivable by replay. The fork occurrence plus its exact attachment point is not derivable from unrelated surviving effects.
* **FUTURE:** child query, child action, current explanation, or later child authoring distinguishes the snapshot.
* **EXTERNALIZE:** naming conventions such as “branch 1 came from 0,” a VCS, or operator memory move the correlation outside `B` and are not accepted substitutes.
* **REALIZE:** pointer sharing, copied bytes, and paper cross-references could realize the behavior, but no verified unlike pair exists: **UNKNOWN**.
* **COGNITION:** eliminating copied views reduces storage but forces navigation through lineage; `E1c` is the mechanical explanation path. Search remains linear.
* **TCB:** snapshot capture, replay, capacity enforcement, and any deduplication are correctness-critical. Copy-on-write or content addressing would add uncredited trust and recovery mechanisms.

### 5.4 Completed action key and committed-snapshot correlation

* **DELETE / MERGE / COLLIDE:** `(B)` and `(B,AA00)` collide if completion is deleted; future `AA00` emits `!` versus receipt `=`. Key deletion merges `(B,AA00)` and `(B,AA01)` with the same witness. Snapshot deletion merges `(B,WA0x,AA00,WA0y)` and `(B,WA0x,WA0y,AA00)` under a “current value only” encoding; future `AA00` returns committed `x` versus `xy`.
* **DERIVE / RECOMPUTE:** response framing and committed interpreted bytes are replayable from the action occurrence and its attached branch prefix. The fact that the first emission occurred and which prefix/key it used cannot be recomputed from the current branch surface.
* **FUTURE:** retry and `E` are explicit future observers. An unanticipated in-contract sequence of later writes, mode changes, delegation, boots, and retry still observes the original receipt.
* **EXTERNALIZE:** relying on an action target's deduplication, payment provider, message broker, operator checklist, or caller-held receipt changes the boundary and TCB; `ZG-1` requires the candidate's own later `=` behavior.
* **REALIZE:** no physical exactly-once realization or independent unlike pair has been tested. Logical response semantics do not prove physical effect uniqueness: **UNKNOWN**.
* **COGNITION:** durable keys reduce operator retry uncertainty; explaining snapshot attachment is still a cognitive cost. Removing it pushes reconciliation to people.
* **TCB:** atomic persist-before-`!`, crash recovery, device ordering, and external effect delivery are absent from the logical experiment and remain **UNKNOWN**, not zero.

### 5.5 Frozen specification and replay mechanism

* **DELETE / MERGE / COLLIDE:** the same survivor bytes under identity versus swap semantics produce different `Q t` and action output; the specification cannot disappear. Merging contract versions without a version authority is unsound.
* **DERIVE / RECOMPUTE:** responses and materialized views are recomputed only from survivors **plus this exact `ZG-1` specification**. The specification is an identified reconstruction source, not derivable from histories.
* **FUTURE:** later interpretation, explanation, invalid-input handling, and capacity behavior depend on exact semantics even when a small visible corpus does not reach them.
* **EXTERNALIZE:** embedding semantics in Python, firmware, a prompt, a service, or a person's convention moves rather than deletes it. The selected implementation and version binding enter the TCB.
* **REALIZE:** a realization must bind the same contract bytes/identifier to its decoder. No evidence shows two unlike mechanisms do so: **UNKNOWN**.
* **COGNITION:** a compact event projection increases the amount of specification a human must consult. Generated views can reduce that cost only by adding trusted code.
* **TCB:** parser, transition logic, actor derivation, version binding, explanation rendering, and corruption rejection are correctness-critical. A missing compiler/verifier is an absent capability, not zero complexity.

### 5.6 Exact complexity-movement ledger

| Simplification | What was removed | Where the complexity moved |
|---|---|---|
| `FULL -> ACCEPTED4` | boot, query, explanation, invalid, denied, no-change, retry, and all old output frames | ingestion must decide acceptance exactly before acknowledgement; replay and evidence can no longer audit forgotten traffic |
| `ACCEPTED4 -> PROJECTED3` | actor byte | replay derives actor from prior controller; corruption validation, renderer logic, TCB, and reviewer effort increase |
| materialized surface -> replay | current raw/interpreted/controller/mode/parent/bitmap/value views | linear runtime at boot/query, replay code, capacity checks, and operational latency |
| global order -> causal order (allowed, not implemented) | chronology between independent effects | relation storage, dependency construction, canonical rendering, concurrency/recovery logic, and cognitive navigation |
| persisted answers/explanations -> regeneration | response bytes and display forms | exact formatter and versioned specification in TCB; repeated compute cost |
| indexes/caches omitted | fast lookup/navigation | linear scans, user waiting, operational observability, and human discovery burden; no search capability is claimed |
| quotient label | representation bytes | complete equivalence oracle, decoder table, future-set authority, evolution invalidation, and opaque explanation |
| external action target dedup omitted | physical delivery state | logical contract stops at `!`/`=` boundary; real-world exactly-once behavior remains UNKNOWN |

## 6. Post-attack non-overlapping persistence verdicts

The classification scope is information needed **between completed executions for future `ZG-1` boundary behavior**. Each item appears once at this scope. A field used to materialize an item is not the item itself.

### 6.1 MUST SURVIVE

1. **Accepted effect occurrence, operation, target, and final argument.** Exact minimized forcing witnesses are the script's deletion witnesses: `FA01` versus `AA01` then `WA1x` for operation; `FA01,WA0x` versus `FA01,WA1x` then `Q0r` for target; `AA00` versus `AA01` then `AA00` for argument; empty versus `WA0x` then `Q0r` for occurrence. Each deletion makes non-equivalent histories collide.
2. **Multiplicity and the causal order/attachment required by replay and explanation.** Exact minimized witnesses are one versus two `WA0x` then `Q0r`, and `IA01,AA00` versus `AA00,IA01` then `E00`. The stronger fork-placement witness is `WA0x,FA01,WA0y` versus `WA0x,WA0y,FA01` then `Q1r`.
3. **Branch creation/snapshot correlation.** Exact forcing witness is empty versus `FA01` then `Q1p`; exact snapshot-point witness is the fork-placement pair above. This requires a distinction, not a parent field or a graph constructor.
4. **Completed action key and its committed causal prefix.** Exact minimized occurrence/key witnesses are empty versus `AA00` then `AA00`, and `AA00` versus `AA01` then `AA00`. Exact prefix witness is `WA0x,AA00,WA0y` versus `WA0x,WA0y,AA00` then `AA00`.

These responsibilities can share bits in an encoding; they are not required record types. They survive only while the referenced branch/receipt remains future-observable. `ZG-1` has no delete operation, so every accepted branch and receipt remains observable.

### 6.2 MAY REBUILD

1. **Actor byte of each accepted effect.** Source: the surviving `(operation,target,argument)` causal sequence plus `ZG-1`. Reconstruction: take the target's then-current controller (the parent's controller for `F`), emit that byte in position 1, validate acceptance, then apply. A failure is corruption and must stop. The bounded greedy deletion and the induction both support this verdict.
2. **Current branch existence, raw bytes, interpreted bytes, controller, mode, parent, explanation, action-key bitmap, receipt value, and receipt explanation.** Source: all MUST SURVIVE distinctions plus the initial semantic root and transition rules in sections 1.2–1.3. Replay is deterministic. This verdict covers materialized views only, not their forcing causes.
3. **All valid output frames, accepted input envelopes, and response length/count fields needed in a future execution.** Source: reconstructed replay result plus the exact frame/response grammar. Tags and lengths are deterministic; no past-output audit is in the contract.
4. **Indexes, caches, query plans, navigation views, and bounded future signatures.** Source: reconstructed replay result plus an explicitly identified index/view algorithm or the declared 655-future list. No such production algorithm is supplied; therefore performance and verification remain UNKNOWN even though deterministic rebuilding is possible in principle.
5. **A canonical ordering for independent surviving effects, if a partial-order encoding is later chosen.** Source: the surviving causal relation plus an explicitly frozen canonical topological-sort specification. No such representation is selected here.

The reconstruction specification itself is exactly the frozen `ZG-1` bytes and must be bound by a realization; it is not classified as mutable history information.

### 6.3 MAY FORGET

1. **Invalid, missing-branch, unauthorized, capacity-rejected, equal-controller/mode, and action-retry input occurrences after their response crossed `B`.** Exact non-influence argument: every such transition returns the identical replay result it received; induction on any common future therefore yields identical future outputs. The contract contains no past-traffic query.
2. **Boot, query, and explanation input occurrences after their responses crossed `B`.** The same identity-transition induction applies. Boot only marks an execution boundary; execution count is not queryable.
3. **All old output-frame bytes.** They were externally observed, no request can ask the candidate to reproduce the full old transcript, and future outputs are a deterministic function of the surviving replay distinction and future inputs. Keeping them outside does not satisfy any candidate obligation; an environment's private memory is not silently treated as system state.
4. **Framing bytes of forgotten traffic and redundant framing around accepted four-byte bodies.** For forgotten traffic they have no future influence. For accepted bodies, `I`, length `0004`, and future output envelopes are deterministic reconstruction rather than this category.
5. **Relative global order of adjacent independent accepted effects.** Exact non-influence condition: the effects touch different existing branch lineages and different action keys; neither creates, controls, interprets, writes, or snapshots a branch touched by the other; and neither's explanation includes the other. Under that condition the two transition functions commute, produce the same per-branch explanations/receipts, and every common future has the same outputs. If any condition fails, order remains MUST SURVIVE. This is why the simple `PROJECTED3` global sequence is sufficient but not minimal.

No item above is also labeled MUST SURVIVE or MAY REBUILD at this scope.

## 7. Evidence, TCB, evolution, and fail-closed limits

The evidence boundary contains only exact boundary bytes, frozen contract/code bytes, deterministic run artifacts, and declared physical measurements. Prose plausibility, a passing unit test, an implementation name, an operator assertion, or absence of a counterexample is not evidence of completeness.

The logical TCB for `PROJECTED3` includes frame parsing, request validation, authorization and capacity decisions, persist-before-success ordering, extraction of accepted triples, durable encoding/decoding, actor reconstruction, replay, output formatting, contract-version binding, and fail-closed corruption handling. The experiment additionally trusts CPython byte/tuple/dict behavior, the extraction procedure, process execution, artifact capture, and comparison. Crash recovery, media behavior, concurrency, compiler correctness, supply chain, and hardware are outside the evidence obtained and remain **UNKNOWN**.

Evolution is permitted only by declaring a new exact boundary contract such as `ZG-2`, a total conversion relation from old survivor distinctions, and witnesses that the conversion does not merge histories that the new future set distinguishes. Loading new semantics from ambient code or reinterpreting old bytes in place is forbidden. If conversion cannot prove a required distinction, the capability is unsupported; it is not repaired by a default, sentinel, or human convention.

## 8. Physical and materially unlike realization rules

Logical trace equivalence is not physical evidence. A realization claim must instantiate all relevant predicates:

* `BOUNDARY-COMPLETE(R)`: instrumentation shows every permitted input and output byte crosses only `B`; undeclared clocks, files, services, prompts, and operators are disabled or included in a manifest.
* `EXECUTION-SEPARATED(R)`: between two `B` transactions, all volatile computation from the prior execution is destroyed or made inaccessible; only a declared persistent substrate can influence the next execution.
* `DURABLE-ACK(R,F)`: for every fault in an exact published fault set `F`, each returned `K` or first `!` is recoverable with its required distinction and no unacknowledged effect is falsely reported as committed. `ZG-1` has not declared such an `F`, so this is currently **UNKNOWN**.
* `TRACE-CONFORMANT(R,S)`: realization `R` matches specification `S` on the visible corpus, independently committed hidden corpus, fresh corpus, and property/fault tests, with complete artifacts. Finite matches do not prove universal conformance.
* `PORTABLE(R1,R2,S)`: two independently built realizations both satisfy `TRACE-CONFORMANT`, exchange the same canonical survivor bytes or a proved lossless conversion, and match after alternating execution ownership.
* `MATERIALLY-UNLIKE(R1,R2)`: (a) their persistence substrates have independently documented, non-overlapping primary physical state mechanisms and failure modes; (b) their transition engines share no executable, runtime, generated decoder, storage service, or correctness-critical library; (c) their implementations were produced from `S` by independent teams without sharing implementation artifacts; and (d) an independent evaluator reproduces cross-realization traces and fault tests. Different brands, languages on the same runtime, two wrappers over one service, or two files on one storage engine do not qualify.

Required independent evidence is: full bills of materials; source/build hashes; substrate and failure-mode documentation from separate authorities; instrumented boundary traces; volatile-destruction evidence; fault-injection logs; survivor-byte exchange logs; hidden-suite precommit and reveal; and independent evaluator signatures whose identity chain is itself declared. Evidence must be independently rooted—two reports generated by the same code, service, organization, or measurement path count as one root.

No such realization artifacts exist in this seed. Therefore `BOUNDARY-COMPLETE`, `EXECUTION-SEPARATED`, `DURABLE-ACK`, universal `TRACE-CONFORMANT`, `PORTABLE`, `MATERIALLY-UNLIKE`, physical minimality, operational fitness, human-scale cognition, and whole-system TCB size are all **UNKNOWN**. The byte-neutral contract is only an opportunity for unlike realization, not evidence of one. Narrowing the physical scope or calling an external service does not convert UNKNOWN into success.

## 9. Explicit nonclaims

This seed does not claim a universal information system, an application data model, semantic completeness, discovery/search, concurrency, deletion, privacy, confidentiality, authentication of real people, physical action delivery, crash consistency, availability, performance, compiler/verifier availability, automatic migration, global minimality, minimal code, minimal TCB, minimal human effort, or any production readiness. It does not infer a constructor from a witness. It does not count an external service, runtime, prompt, person, convention, organization, recovery process, cache invalidator, selector, or trust mechanism as zero complexity.

The only defended milestone is the non-overlapping survival/rebuild/forget partition above, under exact contract `ZG-1`, with finite falsification results and explicit proof obligations. Every uninstantiated wider capability remains **UNKNOWN** or unsupported.
