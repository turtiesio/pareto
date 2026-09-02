# R0.1L executable finite-history experiment result

## Frozen inputs and executable identity

| Artifact | Identity |
|---|---|
| Candidate | `HISTORY-SEED-R01L.md`, commit `6db0c31f096d6c93f343e920b0618b6d7c39da4b`, SHA-256 `0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb` |
| Post-freeze break | `POSTFREEZE-BREAK-R01L.md`, commit `a6b3289018132235f71066e8c0c8282da5e9ba54`, SHA-256 `0744f495f0a229715e1f088c99d96bbbe0b409aaef522e54fb2a8fc516461b9a` |
| Falsifier | `r01l_history_experiment.py`, commit `232053605ec4ea794143b1aa03ba8c254ecfd972`, SHA-256 `ce064d9bdf0cd3f80c395d4772837fb2b427d231b2cdd5a8273a300f9e98757a` |

The falsifier fails closed unless the candidate hash matches. It extracts the
candidate's frozen Python block, checks that block's digest, captures and
compares its complete stdout, independently audits its pair minimizer, runs the
declared post-freeze D1 domain, checks actor reconstruction, and exercises the
long-history ORACLE boundary found by the breaker.

It is an oracle/falsification instrument. It is not a subject implementation,
persistent realization, architecture, proof of the complete quotient, or
evidence about physical survival.

## Evidence environment

| Item | Observed value |
|---|---|
| Python command | `/usr/bin/python3`, symlink target `/usr/bin/python3.12` |
| Executable SHA-256 | `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118` |
| Interpreter | Python `3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]` |
| OS | Ubuntu 24.04.4 LTS |
| Kernel/architecture | Linux `6.8.0-137-generic`, `x86_64` |
| C library | glibc 2.39 |
| Locale | `C.UTF-8` for `LANG` and every `LC_*` category |
| Embedded block SHA-256 | `a7fe34a112919b319739fc79dc37f8c9c0ed036a4e73ae2a33081df55a3e4d84` |
| Embedded reference stdout SHA-256 | `f6b53a0777363a7173c703fd34397bc3f770905705d3f35f08b4279e30009587` |

The wrapper imports Python standard-library modules and reads the pinned
candidate. The embedded block itself imports nothing and receives no time,
randomness, network, locale, environment-variable, or external selector input.
This manifest identifies the measured execution; it does not close the Python,
OS, hardware, extraction, or evidence-capture TCB.

## Reproduction runs

Two post-commit runs used the same frozen source from different working
directories. Both emitted one newline-terminated JSON line of 3,312 bytes,
exited one, and had empty program stderr.

| Measure | Artifact-directory run | Parent-directory run |
|---|---:|---:|
| Exit status | 1 | 1 |
| PASS / FAIL / UNKNOWN | 5 / 1 / 7 | 5 / 1 / 7 |
| Whole-stdout SHA-256 | `69e9c3d96e20f68338a005c694bb69e616512425faf968b8d427faa51c80b630` | `69e9c3d96e20f68338a005c694bb69e616512425faf968b8d427faa51c80b630` |
| Wall time | 28.76 s | 28.65 s |
| User CPU | 28.30 s | 28.18 s |
| System CPU | 0.45 s | 0.46 s |
| Maximum resident set | 385,700 KiB | 385,788 KiB |

The first row of measurements was taken immediately before the final source
commit from bytes identical to that commit; the second was taken after commit
from `/root/pareto`. A further post-commit run from the artifact directory
confirmed the same stdout digest, exit, line count, and byte count. Identical
hashes establish deterministic report bytes for these runs, not correctness
beyond their explicit checks.

## Complete program stdout

```json
{"artifact":"r01l-history-experiment","candidate_sha256":"0040a376061933663356db0fb2ec3c5eefad158bdb6fa1ae4b0f190ef2cabaeb","input_gate":"PASS","overall":"FAIL","results":[{"claim":"The embedded reference block and exact expected stdout reproduce.","details":{"code_sha256":"a7fe34a112919b319739fc79dc37f8c9c0ed036a4e73ae2a33081df55a3e4d84","stdout_matches_frozen_text":true,"stdout_sha256":"f6b53a0777363a7173c703fd34397bc3f770905705d3f35f08b4279e30009587"},"id":"R01","verdict":"PASS"},{"claim":"The reference collision routine returns the declared exact pair minimum.","details":{"audited_encoders":15,"mismatches":[]},"id":"R02","verdict":"PASS"},{"claim":"PROJECTED3 has no collision in the frozen D1 history/future domain.","details":{"collision":null,"equivalence_classes":1381,"futures":787,"histories":137561,"states":1526},"id":"R03","verdict":"PASS"},{"claim":"ACCEPTED4 has no collision in the frozen D1 history/future domain.","details":{"collision":null},"id":"R04","verdict":"PASS"},{"claim":"Actor reconstruction reaches the oracle state for every D1 history.","details":{"first_failures":[]},"id":"R05","verdict":"PASS"},{"claim":"ORACLE is a total canonical serialization for every valid ZG-1 history.","details":{"all_9362_writes_accepted":true,"branch_item_length_at_9361":65535,"branch_item_length_at_9362":65542,"oracle_at_9361":"encoded","oracle_at_9362":"ValueError: bytes must be in range(0, 256)","u16_maximum":65535,"witness":{"future_needed":[],"history":"B followed by 9,362 WA0x requests"}},"id":"F01","verdict":"FAIL"},{"claim":"complete_future_observable_quotient is not established by this executable.","details":{"reason":"Only the frozen D and D1 future domains were enumerated."},"id":"U01","verdict":"UNKNOWN"},{"claim":"global_minimality is not established by this executable.","details":{"reason":"No complete candidate-representation universe or all-smaller search exists."},"id":"U02","verdict":"UNKNOWN"},{"claim":"subject_conformance is not established by this executable.","details":{"reason":"The reference replay is an oracle/falsifier, not a subject execution."},"id":"U03","verdict":"UNKNOWN"},{"claim":"physical_durability is not established by this executable.","details":{"reason":"No fault set, persistent substrate, or independent physical evidence was run."},"id":"U04","verdict":"UNKNOWN"},{"claim":"human_cognition is not established by this executable.","details":{"reason":"No authoring, comprehension, navigation, or verification study was run."},"id":"U05","verdict":"UNKNOWN"},{"claim":"tcb_closure is not established by this executable.","details":{"reason":"No complete influence inventory, perturbation surface, or independent oracle exists."},"id":"U06","verdict":"UNKNOWN"},{"claim":"materially_unlike_realizations is not established by this executable.","details":{"reason":"No pair of physical realizations or independently rooted evidence sets exists."},"id":"U07","verdict":"UNKNOWN"}],"scope":{"fresh_domain":"137,561 histories and 787 futures","not_established":["complete future-observable quotient","global minimality","subject conformance","physical durability","human cognition","TCB closure","materially unlike realizations"],"reference_domain":"7,240 histories and 655 futures"},"summary":{"FAIL":1,"PASS":5,"UNKNOWN":7},"version":1}
```

The Python process wrote no stderr bytes. The `Command exited with non-zero
status 1` line and resource measurements shown by `/usr/bin/time -v` belong to
the measurement wrapper, not program stderr.

## Five finite passes

1. `R01` reproduces the exact embedded reference output. On D, that means
   7,240 histories, 285 distinct replay states, 655 futures, and 269 bounded
   equivalence classes, with the displayed candidate collisions and bounded
   no-collision results.
2. `R02` compares the reference minimizer against an exhaustive
   per-length/per-equivalence-class representative search for fifteen encoders:
   the nine displayed candidate encoders and six projection/deletion/order
   cases. Every declared D minimum and first future agrees.
3. `R03` executes D1: all D histories plus 130,321 exact length-four tails,
   for 137,561 histories total; 1,526 distinct replay states; the 655 D futures
   plus 125 fixed three-step futures and seven depth-three adaptive policies,
   for 787 futures total; and 1,381 bounded equivalence classes. No
   `PROJECTED3` collision is found.
4. `R04` finds no `ACCEPTED4` collision on the same D1 domain.
5. `R05` reconstructs every D1 history from the accepted `(operation, target,
   argument)` projection and reaches its exact oracle replay state. Actor
   reconstruction fails closed on any non-accepted reconstruction.

These are finite/replay facts. D1 is larger than D but is not the universe of
histories or adaptive futures. The full-contract sufficiency argument for
`PROJECTED3` remains an induction in the candidate, not a consequence of D1
alone.

## One executable failure

`F01` executes one valid ZG-1 history: boot followed by 9,362 accepted `WA0x`
requests. For `e` such writes, ORACLE's nested branch item has length
`8 + 7e`. At 9,361 writes it is exactly 65,535 bytes and encodes. At 9,362 it
is 65,542 bytes, while its containing `SEQ` uses U16 item lengths. The frozen
`u16` function receives a high byte value of 256 and raises
`ValueError: bytes must be in range(0, 256)`.

No distinguishing future or second history is needed: this is total-function
failure on a contract-valid history, not a pairwise representation collision.
It falsifies the advertised full-domain ORACLE encoding. It does not falsify
the separate `PROJECTED3` sufficiency induction. The finite D/D1 passes cannot
mask it.

## Seven executable UNKNOWNs

- `U01`: D and D1 do not construct the complete future-observable quotient.
- `U02`: no complete representation universe or all-smaller search establishes
  global minimality.
- `U03`: the oracle and falsifier are not a subject conformance run.
- `U04`: no persistent substrate, fault set, crash recovery, or physical
  durability evidence exists.
- `U05`: no human authoring, comprehension, navigation, or verification study
  exists.
- `U06`: no complete influence inventory, perturbation surface, or independent
  adjudicator closes the TCB.
- `U07`: no materially unlike realization pair or independently rooted
  evidence set exists.

The executable does not evaluate the breaker's separate analytic findings
about the seed's missing conforming evidence at freeze time or its conditional,
unspecified MAY REBUILD entries. Those remain document-level findings in
`POSTFREEZE-BREAK-R01L.md`, not hidden executable passes.

## Result

The experiment materially strengthens the bounded evidence: the frozen D
output reproduces; the declared D minima survive an independent minimizer; and
the larger, previously unrun D1 domain finds no causal-projection collision.
It also reproduces the breaker’s smallest full-domain encoder failure.

Accordingly, the frozen document is **FAIL**, while the causal projection has
narrow positive support. No representation is selected, no passing code is
treated as architecture, and no missing physical, operational, cognitive,
portability, or trust mechanism is counted as zero complexity. The first
milestone is not achieved by this executable result.
