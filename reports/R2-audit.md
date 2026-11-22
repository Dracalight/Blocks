# R2 initial defect audit

Baseline inspected: `3a03556486d9668b6226366c20a2d6da50af8203`, before the R2 edits.

| Defect | Severity | Evidence in R1 | R2 treatment |
|---|---|---|---|
| R2-001 shared Player/hazard block map | Critical | `player_blocks = blocks` retained an alias, then hazard blocks were appended into the same map. | Separate per-target block builders; global-ID and single-parent checks in tests. |
| R2-002 iteration-scaled motion | Critical | Gravity, jump impulse and obstacle speed changed once per forever-loop, tied to interpreter cadence. | Timer-driven 1/120 s bounded substeps; source values are parameterized. |
| R2-003 rounded floor equality | Critical | Floor support used equality after rounding, with no penetration correction. | Floor crossing clamp and platform top crossing resolution. |
| R2-004 incomplete states/restart | Critical | Old code used menu/play/dead and could not leave dead; no pause or practice state. | MENU, PLAYING, DEAD, PAUSED, COMPLETE, PRACTICE with explicit key transitions and restart cleanup. |
| R2-005 structural-only test | Critical | One ZIP/JSON/opcode test did not load Scratch VM. | Pinned Scratch VM/Storage harness loads the actual SB3 and runs scripted gameplay. |
| R2-006 false README status | High | README labeled prototype ENGINE_READY before runtime validation. | Status corrected and backed by runtime E2E; scope is explicitly only the original acceptance lane. |

Residual risks: no TurboWarp browser render/import test; no iPad or physical-PC QA; no performance benchmark; spike geometry is a conservative rectangular interval/vertical gate, not triangle math; no visual rotation, ceiling collision, or external-level data interpreter. R2 does not implement Press Start, Nock Em, or Power Trip.
