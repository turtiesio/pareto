# ZERO GROUND R0.1N — Pinned experiment result

Status: **6 PASS / 3 FAIL / 11 UNKNOWN; FIRST MILESTONE FAIL / NOT
ACHIEVED.**

This records the exact output of a post-freeze falsifier. It is not a subject,
physical realization, architecture, quotient proof, or repair of the frozen
candidate.

## 0. Artifact gate

| artifact | commit | SHA-256 |
|---|---|---|
| `HISTORY-SEED-R01N.md` | `0ba35affe0a587d0d80ca4ba28a26602d8e269ba` | `10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7` |
| `r01n_history_audit.py` | `807b0fd243f645fc8c2a11a51cdad072da9b9148` | `afb21585f1b9523f16f6fb4d3d647eadac5c461d30de8cda92f19ecd40f18f49` |
| deterministically extracted candidate block | derived from the first artifact by the pinned extractor | `c3659cd33f5ab71ae5fef05604d1dd2bb1366070b0d0c23f2fda9c7a8d74af39` |

The independent builder's reported candidate hash and size were mechanically
verified before the candidate was semantically opened. The audit script pins
that hash and fails before execution on mismatch.

## 1. Execution environment and command

- interpreter: `/usr/bin/python3` -> `/usr/bin/python3.12`, Python 3.12.3;
- interpreter SHA-256:
  `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118`;
- Unicode database reported by the program: 15.0.0;
- operating system: Ubuntu 24.04.4 LTS;
- kernel: Linux 6.8.0-137-generic x86_64;
- libc: glibc 2.39;
- locale: `C.UTF-8`.

Command, executed once from `/root/pareto` and once from `/tmp`:

```sh
/usr/bin/python3 /root/pareto/zero-ground-restart/r01n_history_audit.py
```

Both runs produced:

- exit status 1, intentionally fail-closed because three claims are FAIL;
- empty stderr, SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- one-line, 7,254-byte stdout, SHA-256
  `536fe90528116883e0d32dc5f1ca90f392794b7393b6e5cd0b09c249afc1ecb9`.

Measured resources:

| working directory | user s | system s | wall s | max RSS KiB | exit |
|---|---:|---:|---:|---:|---:|
| `/root/pareto` | 2.05 | 0.02 | 3.03 | 18,688 | 1 |
| `/tmp` | 1.96 | 0.01 | 2.79 | 18,816 | 1 |

The timings characterize this falsifier on this environment only.

## 2. Complete audit stdout

```json
{"candidate":"HISTORY-SEED-R01N.md","candidate_sha256":"10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7","code_sha256":"c3659cd33f5ab71ae5fef05604d1dd2bb1366070b0d0c23f2fda9c7a8d74af39","python":"3.12.3","results":[{"claim":"The frozen candidate bytes match the declared artifact.","evidence":{"candidate_sha256":"10b048ed7434fc1ca540e3fd497cd58904f5a481aa27da8fc4520f1151bd63f7"},"id":"R01","status":"PASS"},{"claim":"The embedded bounded experiment executes without an assertion or exception.","evidence":{"code_sha256":"c3659cd33f5ab71ae5fef05604d1dd2bb1366070b0d0c23f2fda9c7a8d74af39","exception":null,"stdout_bytes":3157,"stdout_lines":31,"stdout_sha256":"1368c181cd2116c1e60fef6ab59a86145d1956a3b29394a51e8e08865b450f74"},"id":"R02","status":"PASS"},{"claim":"P01 is injective and round-trips over the two frozen bounded corpora.","evidence":{"fresh_encodings":157,"fresh_histories":157,"public_encodings":585,"public_histories":585,"roundtrip":true},"id":"R03","status":"PASS"},{"claim":"P01 round-trips selected ULEB tier boundaries.","evidence":{"cases":[{"direction":0,"encoded_length":2,"payload_length":0,"roundtrip":true,"uleb_hex":"00"},{"direction":1,"encoded_length":2,"payload_length":0,"roundtrip":true,"uleb_hex":"00"},{"direction":0,"encoded_length":3,"payload_length":1,"roundtrip":true,"uleb_hex":"01"},{"direction":1,"encoded_length":3,"payload_length":1,"roundtrip":true,"uleb_hex":"01"},{"direction":0,"encoded_length":4,"payload_length":2,"roundtrip":true,"uleb_hex":"02"},{"direction":1,"encoded_length":4,"payload_length":2,"roundtrip":true,"uleb_hex":"02"},{"direction":0,"encoded_length":129,"payload_length":127,"roundtrip":true,"uleb_hex":"7f"},{"direction":1,"encoded_length":129,"payload_length":127,"roundtrip":true,"uleb_hex":"7f"},{"direction":0,"encoded_length":131,"payload_length":128,"roundtrip":true,"uleb_hex":"8001"},{"direction":1,"encoded_length":131,"payload_length":128,"roundtrip":true,"uleb_hex":"8001"},{"direction":0,"encoded_length":132,"payload_length":129,"roundtrip":true,"uleb_hex":"8101"},{"direction":1,"encoded_length":132,"payload_length":129,"roundtrip":true,"uleb_hex":"8101"},{"direction":0,"encoded_length":16386,"payload_length":16383,"roundtrip":true,"uleb_hex":"ff7f"},{"direction":1,"encoded_length":16386,"payload_length":16383,"roundtrip":true,"uleb_hex":"ff7f"},{"direction":0,"encoded_length":16388,"payload_length":16384,"roundtrip":true,"uleb_hex":"808001"},{"direction":1,"encoded_length":16388,"payload_length":16384,"roundtrip":true,"uleb_hex":"808001"},{"direction":0,"encoded_length":16389,"payload_length":16385,"roundtrip":true,"uleb_hex":"818001"},{"direction":1,"encoded_length":16389,"payload_length":16385,"roundtrip":true,"uleb_hex":"818001"}]},"id":"R04","status":"PASS"},{"claim":"A direction-in-length coding is another bounded injective candidate and uses no more bytes on every tested history.","evidence":{"fresh_encodings":157,"interpretation":"storage counterexample only; corruption detection, cognition, runtime, and TCB prevent a total-system dominance claim","never_larger":true,"p01_total_bytes":12566,"packed_total_bytes":10594,"public_encodings":585,"roundtrip":true,"strictly_smaller_histories":740},"id":"R05","status":"PASS"},{"claim":"A deterministic union of the frozen minimum pairs reproduces every listed public mutant witness and bundle deletion with 13 histories.","evidence":{"attacks_covered":21,"attacks_total":21,"bundle_fixed_point":["transcript"],"full_public_corpus":585,"histories":["()","(0:)","(1:)","(0:00)","(0:01)","(0:,0:)","(0:,1:)","(1:,0:)","(0:,0:00)","(0:00,0:01)","(0:,0:,0:)","(0:,0:,1:)","(0:,0:,0:00)"],"minimality":"not proved; 13 is an upper bound and already shows 585 was not necessary for the listed witnesses","witness_union_corpus":13},"id":"R06","status":"PASS"},{"claim":"The executable LENGTH witness is one common snapshot-bearing C01 continuation.","evidence":{"boundary_capture_timing":"undefined by C01","fixed_snapshot_outputs_before_request_capture":{"0":[0,0],"1":["REJECTED",1],"2":["REJECTED","REJECTED"]},"harness_outputs":[0,1],"histories":["()","(0:)"],"same_fixed_request_matches":false,"type":"contract/harness correspondence failure, not a P01 collision"},"id":"F01","status":"FAIL"},{"claim":"P01 is a self-delimiting history word without an external container extent.","evidence":{"concatenation_equals_two_occurrences":true,"one_occurrence_hex":"0000","two_occurrence_hex":"00000000","type":"externalized representation-boundary responsibility, not an injectivity collision when byte-string extent is supplied"},"id":"F02","status":"FAIL"},{"claim":"Physical corruption is detectable and recoverable.","evidence":{"both_valid":true,"corrupted_decodes_to":"(1:)","corrupted_hex":"0100","original_decodes_to":"(0:)","original_hex":"0000","reason":"P01 has no retained integrity reference; candidate correctly leaves corruption detection/recovery unspecified"},"id":"U01","status":"UNKNOWN"},{"claim":"The frozen total contract and bounded experiment execute the declared RUN/view/interpretation/action/explanation behavior.","evidence":{"opcode_table_in_executable":false,"reason":"E01's normative opcode table and binary grammar are explicitly incomplete; test futures are direct Python projections rather than encoded E01 programs","run_request_in_executable":false,"snapshot_parameter_in_make_futures":false,"type":"unsupported required capability, not a P01 collision"},"id":"F03","status":"FAIL"},{"claim":"complete_history_equivalence_under_exact_captured_request_response_semantics","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U02","status":"UNKNOWN"},{"claim":"global_minimum_total_system","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U03","status":"UNKNOWN"},{"claim":"independently_committed_hidden_suite","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U04","status":"UNKNOWN"},{"claim":"subject_conformance","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U05","status":"UNKNOWN"},{"claim":"physical_durability_and_recovery","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U06","status":"UNKNOWN"},{"claim":"human_cognition_and_authoring","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U07","status":"UNKNOWN"},{"claim":"query_navigation_service_levels","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U08","status":"UNKNOWN"},{"claim":"TCB_closure","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U09","status":"UNKNOWN"},{"claim":"contract_evolution_and_migration","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U10","status":"UNKNOWN"},{"claim":"materially_unlike_realizations","evidence":{"reason":"not established by the frozen candidate or this logical falsifier"},"id":"U11","status":"UNKNOWN"}],"summary":{"FAIL":3,"PASS":6,"UNKNOWN":11},"unicode_database":"15.0.0","verdict":"FIRST MILESTONE FAIL / NOT ACHIEVED"}
```

The authoritative exact stdout is the committed script's deterministic output
identified by its byte count and SHA-256. The code fence is provided for
inspection and is not an independent byte container.

## 3. Complete embedded candidate stdout

The audit captured the candidate block's stdout before emitting its own JSON.
It contained 31 lines and 3,157 bytes, SHA-256
`1368c181cd2116c1e60fef6ab59a86145d1956a3b29394a51e8e08865b450f74`:

```text
public corpus: histories=585 futures=33
PASS R01N_P01: no distinguishable collision
FAIL DELETE_DIRECTION: classes=84; min=(0:) <> (1:); repr=b'\x00'; witness=AT(0); results=(0, b'') <> (1, b'')
FAIL DELETE_PAYLOAD: classes=14; min=(0:) <> (0:00); repr=b'\x00'; witness=AT(0); results=(0, b'') <> (0, b'\x00')
FAIL DELETE_FRAMING: classes=156; min=(0:00) <> (0:,0:); repr=b'\x00\x00'; witness=AT(0); results=(0, b'\x00') <> (0, b'')
FAIL MERGE_ORDER_BY_SORT: classes=140; min=(0:,1:) <> (1:,0:); repr=b'\x00\x00\x01\x00'; witness=AT(0); results=(0, b'') <> (1, b'')
FAIL MERGE_MULTIPLICITY_BY_DEDUP: classes=92; min=(0:) <> (0:,0:); repr=b'\x00\x00'; witness=LENGTH; results=1 <> 2
FAIL KEEP_COUNTS_ONLY: classes=9; min=(0:) <> (0:00); repr=(1, 1); witness=AT(0); results=(0, b'') <> (0, b'\x00')
FAIL KEEP_LAST_ONLY: classes=8; min=(0:) <> (0:,0:); repr=(0, b''); witness=LENGTH; results=1 <> 2
FAIL KEEP_TAIL_TWO: classes=64; min=(0:,0:) <> (0:,0:,0:); repr=b'\x00\x00\x00\x00'; witness=LENGTH; results=2 <> 3
FAIL DELETE_FIRST: classes=73; min=() <> (0:); repr=b''; witness=AT(0); results=('ABSENT',) <> (0, b'')
FAIL DELETE_LAST: classes=73; min=() <> (0:); repr=b''; witness=AT(0); results=('ABSENT',) <> (0, b'')
FAIL MERGE_PAYLOAD_01_INTO_00: classes=174; min=(0:00) <> (0:01); repr=b'\x00\x01\x00'; witness=AT(0); results=(0, b'\x00') <> (0, b'\x01')
FAIL REPLACE_WITH_DIGEST8: classes=176; min=(0:) <> (0:00,0:01); repr=b'\x96'; witness=AT(0); results=(0, b'') <> (0, b'\x00')
FAIL DELETE_EVENT_AT_0: classes=73; min=() <> (0:); repr=b''; witness=AT(0); results=('ABSENT',) <> (0, b'')
FAIL DELETE_DIRECTION_AT_0: classes=292; min=(0:) <> (1:); repr=b'\x00\x00'; witness=AT(0); results=(0, b'') <> (1, b'')
FAIL DELETE_PAYLOAD_AT_0: classes=146; min=(0:) <> (0:00); repr=b'\x00\x00'; witness=AT(0); results=(0, b'') <> (0, b'\x00')
FAIL DELETE_EVENT_AT_1: classes=72; min=(0:) <> (0:,0:); repr=b'\x00\x00'; witness=LENGTH; results=1 <> 2
FAIL DELETE_DIRECTION_AT_1: classes=288; min=(0:,0:) <> (0:,1:); repr=b'\x00\x00\x00\x00'; witness=AT(1); results=(0, b'') <> (1, b'')
FAIL DELETE_PAYLOAD_AT_1: classes=144; min=(0:,0:) <> (0:,0:00); repr=b'\x00\x00\x00\x00'; witness=AT(1); results=(0, b'') <> (0, b'\x00')
FAIL DELETE_EVENT_AT_2: classes=64; min=(0:,0:) <> (0:,0:,0:); repr=b'\x00\x00\x00\x00'; witness=LENGTH; results=2 <> 3
FAIL DELETE_DIRECTION_AT_2: classes=256; min=(0:,0:,0:) <> (0:,0:,1:); repr=b'\x00\x00\x00\x00\x00\x00'; witness=LAST; results=(0, b'') <> (1, b'')
FAIL DELETE_PAYLOAD_AT_2: classes=128; min=(0:,0:,0:) <> (0:,0:,0:00); repr=b'\x00\x00\x00\x00\x00\x00'; witness=LAST; results=(0, b'') <> (0, b'\x00')
DELETE bundle component without witness: count
DELETE bundle component without witness: last
DELETE bundle component without witness: direction_0_count
bundle deletion fixed point: ('transcript',)
fresh corpus: histories=157 futures=28
PASS R01N_P01_FRESH: no distinguishable collision
FAIL FRESH_UTF8_NFC_NORMALIZATION: classes=38; min=(0:c3a9) <> (0:65cc81); repr=b'\x00\x02\xc3\xa9'; witness=AT(0); results=(0, b'\xc3\xa9') <> (0, b'e\xcc\x81')
E-R01N-1 bounded result: PASS for P01; all listed mutants falsified
```

## 4. Evidence-bounded interpretation

The six positive results establish only artifact integrity, exact reproduction
of the candidate block, bounded P01 injectivity/round-trip, selected ULEB tier
round-trips, a bounded packed alternative, and a 13-history witness-union
corpus. The packed code is not a total-system winner: accepting all header
values changes corruption behavior, and cognition/runtime/TCB were not
compared. The 13-history corpus is an upper bound, not a proof of the minimum.

The failures are different kinds and must not be conflated:

- F01 is a contract/harness correspondence failure. It is not a P01 collision.
- F02 exposes dependence on the containing byte string's extent/EOF. It does
  not break injectivity once that external boundary is supplied.
- F03 is a required-capability failure: no exact E01 opcode grammar or RUN
  execution exists, and the Python projections do not substitute for it.

The coherent direction-byte mutation `00 00 -> 01 00` demonstrates why
round-trip tests are not corruption detection. Both values decode to valid but
different histories; the candidate correctly leaves physical integrity and
recovery UNKNOWN.

The candidate's in-file “fresh” corpus was not independently precommitted or
revealed. Its section-order assertion is not a cryptographic or organizational
freeze. This run reproduces it but does not promote it to hidden evidence.

No result here establishes an exact captured request/response transition,
complete quotient, global minimum, subject, physical persistence, human
outcome, query service level, TCB closure, migration, portability, or a pair of
materially unlike realizations.

**FIRST MILESTONE: FAIL / NOT ACHIEVED.**
