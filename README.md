# NEXUS Geometry Dash — SubZero rebuild R2

R2 turns the R1 packaging sample into a Scratch 3 project with a native-block runtime and an original acceptance lane. The lane is **not Press Start** and contains no copied Geometry Dash art, level layout, code, fonts, or soundtrack.

## Current status

**ENGINE_READY for the original R2 acceptance lane.** The `.sb3` loads in Scratch VM 5.0.300 and the automated VM scenario starts, runs, jumps, lands, pauses, resumes, collides, dies, restarts, uses practice checkpoint recovery, and completes the six-spike test lane. This does not mean any SubZero level is implemented.

- Scratch VM import and headless gameplay: tested.
- TurboWarp editor/rendering: not yet verified (`TURBOWARP_RUNTIME_UNVERIFIED`).
- Native visual rendering, browser screenshot, iPad/Safari touch, and physical PC QA: pending.
- FPS/frame-time and p95/p99: not measured. 30/60 VM cadence parity is a functional simulation check, not a performance benchmark.
- The six-spike collision profile and movement parameters are original provisional values, not measured Geometry Dash values.

## Build and test

Requires Python 3.10+ and Node.js. Runtime validator versions are pinned in `package-lock.json`.

```sh
npm ci
npm test
```

`npm test` rebuilds `dist/Geometry-Dash-SubZero-NEXUS-V1.sb3`, validates its ZIP/project graph, loads and plays it through Scratch VM, then compares normalized speed in Scratch VM 30-FPS compatibility and default cadence. Python only generates/inspects the archive and runs auxiliary checks. Game physics and state transitions are Scratch blocks inside the `.sb3`.

## Controls

- Space or Up Arrow: start, jump, or restart from the menu/death/completion state.
- Stage click: start or jump; this is the intended basic touch adaptation, not iPad validation.
- P: pause/resume while preserving normal or practice mode.
- R: restart a dead or completed run.
- V: start practice mode from the menu.

The jump uses press events and is not buffered in midair. The game samples keyboard events at the effective Scratch VM event cadence.

## Source layout

- `tools/build.py`: deterministic native `.sb3` builder.
- `engine/physics/parameters.json`: provisional units, timestep, clamp, and hit tolerances.
- `levels/runtime_acceptance/level.json`: data for the original acceptance lane.
- `tests/`: structural archive checks and Scratch VM E2E/cadence tests.
- `docs/` and `reports/`: architecture, limitations, and evidence.

Recreating Press Start, Nock Em, and Power Trip remains future work. This branch is a runtime foundation only.
