# Test report — R2

`npm test` runs two Python structural/reproducibility tests, then Scratch VM E2E, then Scratch VM cadence comparison. E2E uses the actual `.sb3` bytes with `vm.loadProject` and `scratch-storage`, starts the real VM threads, sends keyboard input through its keyboard I/O device, and checks observable target/variable states. It does not use a separate game simulation to stand in for the SB3.

E2E covers: project and costumes load; MENU → PLAYING; distance movement; world-to-screen spike coordinate; jump/landing; PAUSED freeze/resume; unavoided collision → DEAD; R restart and cleared progress; six input-timed obstacle crossings → COMPLETE; V practice start; pause/resume of practice; first practice collision rewind; zero runtime exceptions.

Structural checks cover ZIP integrity, reproducible bytes, JSON, asset digests, unique IDs, target-isolated block graphs, all parents/next/input references, valid variable IDs, native runtime opcodes, and absence of bundled audio. Runtime test uses Scratch VM 5.0.300 and Scratch Storage 4.0.0 from the lockfile.

This headless VM run loads costume asset bytes but has no renderer attached. Therefore it does not establish correct rendered pixels, TurboWarp import, iPad touch, or hardware performance. Test results are captured in `reports/` when the final run completes.
