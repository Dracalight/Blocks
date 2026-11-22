# Architecture — increment 1

The runtime is a native Scratch 3 project. Player movement, gravity, jump input, obstacle movement, and contact handling are Scratch blocks inside the `.sb3`; Python only constructs and validates the archive. The first increment is a proof of packaging and core interaction, not the requested final architecture.

Planned full runtime: fixed-step 120 Hz accumulator, independent renderer, level-data interpreter, swept collision checks, camera/world separation, bounded effect pool, deterministic restart state, and audio clock. None of those are claimed complete here. The prototype uses Scratch's frame loop and is not yet frame-rate independent.
