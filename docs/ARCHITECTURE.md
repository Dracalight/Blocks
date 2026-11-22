# Architecture — R2

The `.sb3` is the runtime. `Player` owns input hats, the single game-state variable, timer sampling, fixed-step accumulation, cube physics, world progress, collision decisions, checkpoints, pause/restart and completion. It is the only target that writes shared physics variables. Spike and platform targets only calculate screen positions from `world distance - camera offset`, show/hide, and yield; they never change player state or collision results. Their block graphs are separate and their IDs are globally unique.

The level lane and physics parameters are external build inputs and are serialized into constants/blocks in the project. They are not loaded by the game at runtime. The runtime lane contains six original spike intervals, a platform, a speed change, and a finish distance. Position in the world is independent of camera position; visual targets are transformed by the shared distance offset. The current camera is a fixed player viewport with horizontal world scrolling, not the full SubZero camera choreography.

Scratch-standard blocks implement the runtime. Python generates the project and Node's pinned Scratch VM loads/tests the actual archive; neither replaces runtime physics. A bounded simulation accumulator performs at most 12 logical 1/120-second steps each VM loop, while `wait 0` yields to the interpreter/render scheduler. The game clamps sampled timer gaps to 0.1 s and accumulates the discarded portion in `droppedTime`.

This increment has no audio, custom extensions, external runtime scripts, asset downloads, or third-party game assets.
