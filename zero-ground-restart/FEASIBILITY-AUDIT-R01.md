# PRE-IMPLEMENTATION FEASIBILITY AUDIT R0.1

## Outcome

The independently frozen R0.1 candidate must not be implemented literally.
It contains specification collisions that make its central deletion comparator
either vacuous or non-constructible.  This is a failed candidate result, not a
failed implementation and not evidence for or against any storage mechanism.

Audited retained inputs:

- `REALIZATION-CONTRACT-R01.md`, SHA-256
  `0e28b0e99c1429aabfb13806c296bb2b4fb678dde7e6bcb183057ea5d392b820`;
- `R01-BREAKER-OBJECT.json`, SHA-256
  `99f81a9a4d4f4bf55109a9f43b7cd361c887c9b0b7255a22d009767238e79dfa`;
- `REALIZATION-SUPPLEMENT-R01A.md`, SHA-256
  `9dce6a442af1002b7e280944fedbed5ba0800d18644d45b8bf3d67e0f51f74e1`.

The base candidate and breaker draft were produced independently.  The
supplement and this audit were not: both were written after their authors had
access to frozen attacks.  Retained hashes prove bytes, not private reading
histories or epistemic independence.

## Minimal fatal collisions

### F1 — selector inputs make every candidate pair unequal

R0.1 section 1.1 makes this the first `B` crossing:

```text
select(backend, mechanism_manifest)
```

Section 4 then requires a reference/deletion pair to have different manifests
and requires their complete ordered `B` histories to compare byte-for-byte.
The smallest attempted file-fsync pair is therefore already:

```text
left  = [select(E, REFERENCE)]
right = [select(E, NO_FILE_FSYNC)]
```

They differ before either publisher exists.  The same one-crossing witness
defeats every mechanism comparison.  Likewise the required cross-backend
comparison begins `[select(E,m)]` versus `[select(T,m)]` and can never be byte
equal.  A runner could only report a vacuous difference, silently project the
selector, or violate the comparator.  None tests deletion.

The narrow repair is to place realization/backend configuration in the
complete `L` trial descriptor rather than the subject service port `B`, while
retaining and charging it at `L`.  An alternative is an exact predeclared input
renaming relation, but no such relation exists in R0.1.

### F2 — successful `L` evidence cannot cross its declared boundary

Section 1.2 permits one successful outer crossing:

```text
evidence(exact_canonical_trial_record_bytes)
```

and says that record contains the complete trace and measurements.  Section 7
forbids PIDs, inode values, temporary path spellings, timestamps, and other raw
measurements from that record and moves them into separately retained raw
streams.  No grammar production carries those streams across `L`.

The smallest witness is one otherwise valid trial with one raw trace byte that
is not in the canonical record.  Either that byte crosses an undeclared output
channel, or the successful evidence is incomplete.  A hash in the record does
not carry the byte and fails the already frozen exact-replay future.

The narrow repair is one self-framing success envelope containing the canonical
record, raw trace pack, raw measurement pack, and inventory as distinct opaque
byte fields.  Canonical serialization and deterministic content must not be
conflated: raw fields can be canonically framed while retaining variable
observations.

### F3 — `B`-only classification contradicts an `L` replay future

Section 7 classifies raw records and traces as mandatory retention for the
R0.1 evidence claim.  Section 9 permits an information verdict only from a
minimized `B` collision.  Two trials can have identical `B` histories while
differing by one raw operation-fact byte whose later exact replay is required
at `L`.

Deleting that byte produces no `B` collision but does produce an `L` collision.
Thus the two rules assign incompatible scopes to the same responsibility.  A
repair must report subject-state verdicts relative to `B` and laboratory
evidence-retention verdicts relative to `L`; neither is automatically a global
MUST/MAY verdict for a future target contract.

### F4 — the frozen breaker and base schema disagree on `UNKNOWN`

R0.1 section 8 permits an unknown measurement only as:

```json
{"status":"UNKNOWN","reason":"...","needed_evidence":"..."}
```

The frozen `MEASURE-UNKNOWN(path)` attack replaces exactly one leaf with:

```json
{"status":"UNKNOWN","reason":"nonempty"}
```

and expects schema completeness.  One omitted `needed_evidence` member is the
smallest conflict.  Under the base contract it must fail; under the breaker
oracle it must remain schema-valid.  The supplement's conflict rule therefore
makes the conjunction undecidable by implementation.

A corrected profile must preserve this conflict as a result, reject the
two-member object under the base schema, and add a distinct three-member
structured-unknown control that is schema-valid but never a measurement pass.

There is also a smaller self-conflict in the base sentence that forbids any
string “containing the word `UNKNOWN`”: the mandatory structured object's
`status` value is exactly that string.  The only coherent reading is “no bare
placeholder string in lieu of the structured object,” but that reading is not
literal and needs a new freeze.

### F5 — one replay identifier denotes opposite initial states

The frozen breaker row `EVIDENCE-REPLAY` deletes raw certificate records and
retains only a digest; its exact outcome is failure unless the deleted bytes
can somehow be returned.  The supplement reuses `EVIDENCE-REPLAY` for a
positive replay process that receives the retained stream and index.  One case
ID therefore has both `raw_certificate_records=ABSENT` and a supplied retained
stream.

The repair must preserve the original negative as
`EVIDENCE_HASH_ONLY_NEGATIVE` and create a separately named
`EVIDENCE_REPLAY_POSITIVE`.  Reusing an ID or editing the frozen breaker object
would erase the collision.

## Non-unique encodings and incomplete freeze

### E1 — promised canonical evidence has no unique byte encoding

The base defines a flat field framing but not the value encoding for nested
maps, lists, signed values, verdict objects, measurements, quantiles, trial
identifiers, or checkpoint frames.  Two serializers can therefore emit
different bytes for the same declared record while both follow the prose.  An
exact evidence stream, stream hash, and replay oracle cannot be constructed
uniquely.

The repair must freeze a complete typed value codec, exact trial-ID derivation,
exact frame bytes, map/list ordering, integer widths, and quantile rules before
subject outcomes are observed.

### E2 — verdict spellings violate the closed unknown schema

The contract separately uses `UNKNOWN(reason, needed_evidence)`, mechanism
`UNKNOWN`, `UNKNOWN_UNEXECUTABLE`, `CONTROL_UNAVAILABLE`, and string-valued
unknown/unsupported prose.  Section 8 says no key may contain a string unknown
and supplies only two legal structured status shapes.  These verdicts need a
separate typed verdict grammar or must use the exact structured objects; a
runner cannot guess which spelling is normative.

The three fsync non-witness labels also differ byte-for-byte across base,
supplement, and breaker.  `POWER-GUARD` needs an unsupported applicability
result although the declared `full_conformance` grammar has only PASS, FAIL,
and UNKNOWN.  A correction needs independent typed coordinates for execution
applicability, full conformance, behavioral comparison, scope, and needed
evidence rather than one overloaded string.

### E3 — implementation-dependent bundle cannot be frozen before it exists

`A` and hence `D` depend on exact implementation bundle bytes, while section
11 requires that bundle to be frozen before implementation and section 0 says
no implementation existed at freeze time.  The member list, source bytes, and
digest are not present in the candidate.  Including expected result tables in
the same digest can also create an avoidable specification/oracle dependency.

The narrow repair separates two gates: freeze contracts, suite, bundle member
names, descriptor grammar, and literal oracle before coding; then freeze exact
implemented source bytes and `A/D` after coding but before the first subject
trial.  Any code change after that gate creates a new bundle digest and run.

### E4 — checkpoint progress is underspecified

The base says workers emit checkpoints and the coordinator cuts them, but does
not freeze whether the worker blocks, self-stops, or can advance.  It also
requires `DROP_STAGE_CONTROLLER` at `NORMAL`; a worker that self-stops at every
checkpoint cannot finish without relocating control.  Conversely a worker
that never blocks can pass selection before a nominal pre-selection cut.

A repair must freeze an exact control handshake.  One viable bounded profile
uses a dedicated frame/acknowledgement pipe for non-normal cuts, blocks the
worker after each frame until the controller continues or kills it, and lets a
declared `NORMAL` worker emit nonblocking frames.  `SELF_CUT` must be separately
charged because target choice and signal logic move into the worker.

### E5 — incorporated fault recipes do not identify R0.1 bytes

The base says to rerun R0's record faults “exactly,” but R0.1 changes the
contract digest, bundle digest, suite tag, record tag, and hence every valid
record byte.  `WRONG_SUITE`, coherent replacement, bit indexes, and proper
prefixes therefore need an explicitly adapted R0.1 mutation table.  Referring
to an old recipe is not enough to determine the new bytes or expected rows.

### E6 — the exhaustive descriptor domain is not materialized

The grammar exposes setup and requested payload separately, while the prose
corpus describes only paired CREATE and UPDATE cases and uses “every checkpoint
each can reach” for early failures.  Repetition treatment for unreachable
checkpoints is also unstated.  At least two generators can produce different
trial counts while following those sentences.  A corrected profile must retain
the complete sorted descriptor stream and literal expected table before the
first subject outcome.

### E7 — held-out case identities and applicability are overloaded

- `NO_PRE_RECOVERY_REAP` makes wait-after-recovery a legal deletion variant,
  while `REAP-ORDER` calls that same order a full failure without naming its
  manifest.  The attack must be bound to a forged `REFERENCE` row; the legal
  deletion gets a different ID and comparison status.
- Breaker `PROJECT-1` duplicates literal legacy byte `a000`; the supplement
  both calls it a duplicated neutral checkpoint and later says all `a000..a005`
  bytes are legacy.  Preserve the legacy attack and add a distinct neutral
  frame duplication attack.
- `SELECT-ALT-*` has a conditional behavioral oracle in the breaker and an
  unsupported execution status in the supplement.  These can coexist only as
  separate coordinates: the oracle is retained, but it was not executed.
- Adapter timeout and signal mapping are new supplement futures.  The base
  incorporated only explicitly cited R0 record/fault definitions, so calling
  them already incorporated is false provenance.

### E8 — trace windows and replay selectors are not closed

The configured descriptor allowlist and exact trace-window start/end events
are absent, so “unconfigured output” and `OBSERVED_ABSENT` are undecidable.
Replay also names both a `trial_id` and ordinal without requiring them to agree.
One ID/ordinal mismatch can select two records.  A corrected registry must make
IDs unique, define their canonical construction, set ordinal equal to position
in sorted-ID order, validate offsets/lengths/hashes, and fail any disagreement.

### E9 — the breaker measurement domain is not the R0.1 domain

The frozen attack object has 144 paths derived from R0.  It does not expand
R0.1's per-component role/provenance/dependency fields, new phase timings,
raw-evidence storage, environment, `where_is_complexity_now`, or the complete
new TCB.  Those 144 paths remain a retained attack input, not a complete
R0.1 schema.  A new fully expanded path registry and one deletion mutation per
expanded path are required before implementation.

## Trace and environment feasibility

Independent tracing is locally feasible with the trial supervisor executed
under `strace -f`: the trace can cover supervisor control syscalls and its
publisher, recovery, and adapter descendants while ordinary parent/child wait
ownership remains intact.  A publisher-only attachment would not observe the
supervisor's kill, wait, or recovery `exec`, so it cannot satisfy the contract.

Tracing an `execve` can itself retain the complete environment.  Therefore the
tracer must be launched with a frozen minimal environment before tracing
begins; sanitizing only descendant workers is too late and risks retaining
ambient credentials.  The raw trace remains sensitive evidence and must be
scoped, access-controlled, and charged in storage/TCB.  One canary pair does
not prove independence from all ambient or loader influences.

A whole-supervisor ptrace observer is not a neutral oracle for the
`NO_PRE_RECOVERY_REAP` attack: the observer itself participates in tracee
stop/exit handling.  A passive kernel observer, or a separately declared
`/proc` zombie/pidfd observation, would add more apparatus and TCB.  Without a
refrozen meaning of “reaped” and an observer that can establish it, that
deletion row must be `UNKNOWN`, even if recovery bytes happen to match.

The apparatus exists locally (`strace` 6.8 and writable tracefs with
`trace-cmd` 3.2), but availability is not zero complexity or permission to
infer correctness.  A preliminary feasibility estimate is roughly 3,000
fresh-process trials, 8–12 minutes under full syscall tracing, and 100–400 MB
of raw evidence.  A corrected contract should freeze a conservative 30-minute,
2-GiB apparatus bound and retain an overrun as failure evidence rather than
silently truncating the corpus.

## Classification of this failed candidate

- **MUST SURVIVE for a corrected deletion experiment:** the paired realization
  configuration somewhere at `L`; exact subject inputs/outputs at `B`; exact
  operation/control truth needed to reject false attestations; and any raw
  evidence promised by an admitted exact-replay future.  Each is a
  responsibility verdict at a named boundary, not a proposed field or layer.
- **MAY REBUILD:** normalized facts, counts, quantiles, indexes, and hashes only
  from retained raw bytes plus a frozen deterministic codec/normalizer and its
  complete inputs.
- **MAY FORGET:** no new item is awarded this verdict by this audit.  A
  malformed candidate cannot establish exhaustive no-effect.

The complexity exposed by rejecting implementation remains in boundary
selection, comparator semantics, evidence packaging, serializer/schema code,
trace completeness, environment isolation, operator review, and the trusted
specification.  It did not disappear with the unbuilt runner.

## Remaining gates unaffected by a repair

Even a corrected R0.1 runner would remain a bounded guest-process experiment.
The actual target contract is still undeclared; no participant cognition study
or independent physical failure domain is available; power-loss/cold-recovery,
concurrency, freshness, writer authority, malicious integrity, and global
minimum claims remain structured `UNKNOWN` or `UNSUPPORTED`.
