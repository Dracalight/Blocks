# Physics — R2

## Runtime integration

- Scratch `timer` supplies elapsed monotonic project time; actual input observation is limited by the VM event/update cadence.
- Each visual loop computes a nonnegative `dt`, caps it at 0.1 s, adds it to `accumulator`, and executes up to 12 conditional substeps at `1/120` s. Any elapsed time above the cap is added to `droppedTime`; the substep remainder stays in `accumulator`.
- Each substep applies gravity, vertical position, world distance, floor/platform resolution, and hazard checks. Simulation is performed in the Player target only.
- Fixed-step simulation is tested in Scratch VM at 30-FPS compatibility and default cadence. 120 visual updates per second and target-browser input latency are not measured.

## Collision model

The ground uses a vertical crossing clamp. The authored platform uses a previous/current vertical crossing test while the player's world position overlaps its interval. Each triangular-looking hazard uses a rectangular world-distance interval plus a vertical center threshold; the artwork is not consulted by collision code. The 1/120 steps at the tuned maximum speed bound per-step world travel to about 1.84 units, far smaller than the 60-unit hazard interval. This is a bounded discrete sweep strategy for the current lane; it is not a general swept-AABB/triangle collision library.

## Tuning values

`engine/physics/parameters.json` is the source of units and prototype tuning. Current jump speed, gravity, scroll speed, platform thresholds and hazard intervals are original test values. They are not measured Geometry Dash parameters. The set is calibrated for this original test lane by VM playthrough, not reference-level capture. Runtime visual rotation, ceiling contact, arbitrary AABB entities, and true triangular collision are pending.
