# PRE-EXECUTION FEASIBILITY AUDIT R0.1B

## Outcome

The independently frozen R0.1B semantic corpus is internally reproducible, but
the total candidate is not executable as declared.  Required boundary values
and gate-R identities do not have unique byte constructions, and one exact
positive replay fixture contradicts the required result schema.  Therefore no
R0.1B subject conformance trial was launched, no gate-R artifact was created,
and no B-state mechanism verdict was awarded.

This is a failed-candidate result, not an implementation failure and not a
failure of the S0/S1 hash machinery.  A private serializer, manifest format,
checkpoint table, or decoder would merely externalize the missing contract
state into a runner and its TCB.

The audited semantic closure is commit `807f2cc` with:

- semantic seed
  `078acf7c35cf1840b70886dd854f4fffcc0be1a7c5f8b1627d3bd36e148c2ece`;
- semantic-suite digest
  `996ff2afb799721da2a09ac1ae9dea2b6f7f7369c287b049c83fd1e641a482a6`;
- S1 SHA-256
  `fb72f6b36ca3eae284003ee1983e995afb13d3e8ec9d518f0c1afeaca67a9043`;
  and
- semantic freeze ID
  `r01b-semantic-954e2b16b258ceb8869795dbb823a0284a8369ca1cb20481168d7f652d89fcfd`.

An independent reconstruction, without importing the freeze generator or TV
codec, reproduced the 22,660,748-byte S0 manifest, the 28,549,230-byte S1 file,
all 6,318 case/trial identities, 2,010 comparison edges, 64,680 subject check
identities, and 9,870 LAB check identities.  The complete repository suite at
that closure passed 146 tests.  Those facts establish exact frozen bytes; they
do not make an incomplete execution contract complete.
With the fail-closed probes and breaker added, the final Python discovery run
passes 184 tests; the separate Rust crate passes 15 tests.

## Independent roles

The black-box breaker read only frozen S0/S1/contracts/oracles/holdouts.  It did
not inspect or import either builder probe.  It reports
`CONTRACT_DEFECT_UNDECIDABLE`, has no PASS path, and separately classifies
malformed supplied evidence as an implementation failure.  Its retained
8,628-byte report has SHA-256
`77dd3ef14b848135cb9ebbcd62b1c86cd2b1cf60f08d469263fb5f5308ffa9df`,
and its 17 tests pass.

The Python and Rust builders were separately instructed not to inspect breaker
or each other's source.  Both independently stopped at missing exact authority.
They implemented only byte constructions already fixed by the contract and ran
pure/static development tests, not registered S1 subject trials.  Agreement by
these programs is corroboration of constructible fragments, never the
architecture and never permission to fill a specification gap.

## Minimal fatal defects

### F1 — `canonical_records` has no inner grammar

Section 2 fixes the five-member outer envelope and names
`canonical_records` a “typed canonical record stream.”  No frozen clause fixes
an inner record shape, stream framing, event order, case/check linkage, or the
mapping from those bytes to a B observation.

Smallest collision pressure:

```text
left history:  one recovery observation ABSENT, wire 00
right history: one recovery observation REJECT, wire 01
```

Because the contract gives an independent verifier no decoder for
`canonical_records`, the same opaque field bytes can be claimed as either
history.  A later query for the recovery observation distinguishes them.  A
realization-specific decoder, prompt, or operator convention would move the
missing responsibility into external state and TCB.  Exact replay preserves
bytes but does not supply their meaning.

The same omission prevents a unique canonical representation of constituent
checks, per-edge comparison results, operation facts, trace locators, terminal
order, and measurements.  A passing outer-envelope parser would not close this
gap.

### F2 — failure-reason enums lack a namespace

TV tag `0b` is exactly `u16be(namespace) || u16be(code)`.  Section 5 requires
`failure_reasons` to be a list of closed reason enums.  The frozen reason
registry supplies `code`, `label`, and `origins`, but no namespace.

For its first entry, both values below remain unruled:

```text
0b 0007 0000    COMPARATOR_FALSE_MATCH under candidate namespace 7
0b 0008 0000    COMPARATOR_FALSE_MATCH under candidate namespace 8
```

Exact replay distinguishes these five-byte leaves.  The namespace cannot be
derived from any surviving R0.1B authority, so choosing one in serializer code
would externalize required state.

### F3 — gate R and `realization_id` are not constructible

Section 10.2 requires a broader implementation inventory, a digest named
`A_real`, and a final `realization_id`, but fixes none of:

- canonical manifest bytes;
- a digest preimage or domain-separation tag;
- the relation between the manifest and `A_real`; or
- the spelling and derivation of `realization_id`.

For the one-file inventory `[(name=x, bytes=y)]`, at least raw concatenation
`78 79` and R0-style framed bytes
`00000001 78 0000000000000001 79` remain possible and hash differently.  R0's
narrower adapter-bundle manifest is not explicitly adopted for R0.1B's broader
inventory.  Even a guessed digest would not determine the launch-overlay ID.

Every subject submission requires that overlay.  Thus gate R cannot close and
the first registered subject trial is prohibited.

### F4 — the exact positive replay envelope violates the prose schema

Frozen LAB case
`r01b-case-42ae315f4fd5286123fde985e90ee1b755470b06855f00b8cfafb174012689ef`
contains a 365-byte exact envelope with SHA-256
`23ef24df0532a76909d23ce60bb77660db2a15cd60091bf6a948f07780c3c271`.
Its `status_coordinates` map has only:

```text
applicability, behavioral_comparison, execution,
full_conformance, oracle, scope
```

Section 5 says every result also contains `failure_reasons` and
`needed_evidence`, and section 2 calls the envelope member the complete
coordinates.  Deleting either required empty list is already a smallest
witness.  The exact positive fixture must therefore be accepted for its frozen
replay oracle and rejected for its frozen schema.  No implementation can
satisfy both.

### F5 — the behavioral byte functions have no closed container shape

Section 1 defines `BH`, `B_input_key`, and `B_response` using `typed(...)`, but
does not say whether the arguments form a list, map, sequence of records, or
another closed TV value.  A TV list of components and a TV map with named
components are both self-framing and unequal.

Structural comparison of the exact declared component wires is possible and
was used for static oracle checks.  Claiming canonical bytes for any of the
three functions is not.  This blocks exact behavioral record emission even
apart from F1.

### F6 — neutral-frame `mm` meanings have no descriptor/slot assignment

Section 4.2 fixes five byte meanings (`INVARIANT`, `REFERENCE`, `OMITTED`,
`ALTERNATE`, and `SELF_CUT`) but no total function from descriptor and slot to
that byte.  For example, the `SELF_CUT` target frame could use code `04`, or
could use the slot operation's ordinary code and express self-cut only through
`SELF_CUT_TARGET`.  Likewise an omitted file-fsync manifest does not say
whether unrelated checkpoints report a manifest-wide `OMITTED` code or their
slot-local invariant/reference code.

The two frames differ by one `mm` byte and the control verifier has no frozen
answer.  Passing an explicit `mm` into a frame codec is constructible; deriving
it from a registered descriptor is not.

### F7 — a permitted future exposes an unspecified text-list order

Section 5 calls `needed_evidence` a sorted text list without identifying the
sort key.  Current frozen lists have at most one member, so this is latent rather
than a current-row collision.  A contract-permitted future list containing
`z` and `aa` has two different canonical candidates:

```text
unsigned UTF-8 order: aa, z
raw TV byte order:    z, aa   # the one-byte text length sorts first
```

Exact envelope replay distinguishes them.  The previously unanticipated
continuation therefore demonstrates that the current one-member corpus cannot
justify silently choosing a future ordering rule.

## Constructible fragments used only for falsification

The fail-closed Python probe independently revalidated all 6,318 S1 rows,
rederived all 3,028 subject trial IDs, validated every literal B wire, and
purely evaluated all 2,344 recovery-only fixtures.  Its tests also cover every
proper prefix and 1,032 single-bit flips of the two base records, coherent
wrong-suite records, publisher-result wires, explicit neutral frames, and
mocked slot/deletion behavior.  Its `execute` command always returns
`NOT_RUN`; it does not create a private gate R.
The three Python probe/test files occupy 60,129 source bytes and pass 21 tests.

The unlike Rust probe independently implements SHA-256, strict TV and JSON,
record/recovery parsing, fixture interpretation, and S1 inventory checks.  It
also refuses to serialize `BH`, evidence records, or a gate-R identity without
authority.  Distinct language and source bytes establish unlike software
paths only.  They do not establish unlike physical media, failure domains, or
physical observation.
Its 20 retained source/configuration/test/documentation files occupy 127,720
bytes and pass 15 Rust tests with clippy warnings denied; generated `target/`
bytes are not retained in the handoff.

These fragments identify exactly where implementation can proceed from frozen
bytes and where it cannot.  They are charged as semantic machinery, runtime,
storage, operations, and TCB.  They are not subject evidence.

## Persistence classification from this failed round

These are boundary-scoped information responsibilities, not fields or layers.

### MUST SURVIVE

- Exact B input and response crossing bytes must survive somewhere.  Deleting
  the recovery-observation byte merges `ABSENT=00` with `REJECT=01`; the next
  recovery query distinguishes them.
- Every exact raw trace, measurement, inventory, diagnostic, scratch spelling,
  timestamp, and partial byte that crossed L and is used by an admitted
  exact-replay claim must survive.  The frozen hash-only and retained-envelope
  replay futures distinguish absence from retained bytes.  Moving those bytes
  to a service is EXTERNALIZE, not deletion.
- Semantic-profile and implementation-selection responsibility must survive
  whenever later interpretation depends on it.  R0.1B demonstrates this need
  but fails to provide a valid gate-R encoding for it.
- The specification that maps persisted bytes to observations must remain
  identified and available.  Without the missing F1/F2/F3/F5/F6 rules, equal
  stored bytes do not determine required future behavior.

### MAY REBUILD

Given exact surviving source/observation bytes and an identified, complete
specification:

- S0 manifest indexes and hashes, `D_sem`, S1, the semantic freeze ID, case
  IDs, trial IDs, ordinals, indexes, and display IDs regenerate
  deterministically;
- normalized operation facts, per-edge comparisons, constituent-check
  statuses, aggregate coordinates, counts, and quantiles may regenerate from
  retained exact B/raw observations plus the frozen normalizer, comparator,
  oracle, and aggregation rules; and
- publication/recovery fixture bytes regenerate from S0 symbolic recipes,
  `D_sem`, and the frozen record/TV formulas.

This does not make regeneration free.  Source specifications, codecs,
normalizers, verifiers, dependencies, compute time, and correct version
selection remain charged.  Items whose required rule is one of F1–F7 are not
awarded MAY REBUILD until that rule is actually frozen.

### MAY FORGET

This failed candidate establishes no new unconditional MAY FORGET item.  A
value that never crossed either declared boundary is not a persisted history
item, while a spelling or timestamp that did cross inside an exact-replay raw
pack cannot be forgotten under the current L contract.  The earlier bounded
B1 MAY FORGET results remain scoped to B1 and are neither widened nor revoked
by this audit.

## Simultaneous total-system result

No weighted scalar is used.

| Dimension | R0.1B result in this round |
|---|---|
| information/distinction preservation | undecidable for required L records and realization identity; no PASS |
| persistent state | semantic corpus measured; no subject/evidence corpus exists |
| semantic machinery | S0/S1 plus generators, two probes, breaker, codecs, schemas, and missing rules; not zero |
| human cognition | UNKNOWN; an operator currently must guess the missing decoder/encoding rules |
| authoring burden | at least the 6,318-row corpus and seven missing exact authorities; no participant study |
| query/navigation | static registry lookup works; independent evidence queries are blocked by F1 |
| runtime | static checks measured; subject runtime NOT_RUN |
| storage | 22,660,748-byte S0 manifest and 28,549,230-byte S1 file, plus charged code/tests; no run evidence |
| operations | exact freeze/version coordination works; gate-R/run/replay operations are blocked |
| TCB | hash/codec/freeze/breaker/probe code plus Python/Rust/runtime/OS; guessed rules would enlarge it |
| evolution | the two-member needed-evidence future already splits the unspecified current rule |
| portability | unlike Python/Rust parsing fragments only; physical portability UNKNOWN |
| explainability | minimized defects explain the stop; canonical trial evidence cannot yet explain itself |
| information-loss risk | high/undecidable if a private decoder, namespace, manifest, ID, or frame table is assumed |

The S0/S1 bytes are substantial cached derivations, not a claim that their
shape is minimal.  S1 is mechanically rebuildable from S0 and its identified
derivation specification.  Conversely, deleting exact S0 contract/oracle
information and retaining only hashes would make later reconstruction and
interpretation impossible.

## Where the complexity is now

- Outer-envelope simplicity moved record meaning into an absent inner grammar.
- Omitting a failure namespace moved one required enum coordinate into
  serializer convention.
- Naming `A_real` without a formula moved realization selection into deployment
  and verifier code.
- Compact neutral frames moved descriptor-to-branch interpretation into an
  absent table.
- Calling lists “sorted” moved future ordering into host-language behavior.
- Exact raw replay forces observed incidental bytes to remain stored; it does
  not disappear because a digest is also present.
- Refusing to run moves no capability to zero: controller, tracer, evidence
  serializer, replay process, schema validator, gate-R builder, runtime, OS,
  physical medium, and human procedure remain missing or charged.

## Required next correction

Any successor must preserve R0.1B and this audit as immutable attack inputs,
not edit them into a pass.  Before another subject implementation or registered
trial, it must independently freeze and attack at least:

1. a closed TV schema and framing for every canonical record and its exact
   relation to B, checks, edges, operations, waits, measurements, and raw-pack
   locators;
2. a failure-reason namespace and all list ordering rules;
3. canonical gate-R manifest bytes, digest domain/preimage, realization-ID
   spelling, and launch-overlay validation;
4. closed TV shapes for `BH`, `B_input_key`, and `B_response`;
5. a total descriptor/slot/flags-to-`mm` table;
6. a corrected positive replay envelope with both required status lists and a
   newly derived case identity; and
7. fresh negative controls for every former ambiguity.

Only after a new semantic gate closes may its implementations be adapted,
frozen under its gate R, and used for trials.  A later passing run would remain
a bounded falsification instrument, not a global architecture.

## Unaffected unknowns

The actual target contract is still undeclared.  Participant cognition,
complete authoring/error burden, power-loss and cold recovery, malicious
replacement, freshness, concurrency, physical capture/delivery, and unlike
physical realization remain `UNKNOWN` or `UNSUPPORTED`.  Different Python and
Rust source, semantic hashes, filesystems, or guest paths do not establish
independent physical media or failure domains.
