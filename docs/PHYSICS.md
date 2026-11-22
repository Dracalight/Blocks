# Physics status

Prototype: automatic leftward spike movement and vertical jump/gravity are encoded in Scratch blocks. Values in the first experiment (jump impulse 13, gravity −0.8 per Scratch loop, floor y=−95, obstacle speed −5 per loop) are **provisional tuning constants**, not measured SubZero values. They vary with runtime frame rate and therefore fail the final fixed-timestep requirement. Collision is Scratch sprite touching, not explicit/swept geometry. Rebuild this subsystem before acceptance.
