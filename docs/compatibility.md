# Compatibility matrix — R2

| Surface | Status | Evidence / limit |
|---|---|---|
| Scratch VM 5.0.300 load | PASS | `vm.loadProject()` read the actual `.sb3`; Scratch Storage 4.0.0 resolved all costume bytes. |
| Scratch VM gameplay | PASS | Headless VM executed state and input scenarios through completion and practice reset. No renderer was attached. |
| Scratch-standard blocks | PASS for generated opcodes | No TurboWarp-only extension or external runtime dependency is embedded. |
| TurboWarp editor import and rendering | TURBOWARP_RUNTIME_UNVERIFIED | Not opened in browser during this run. |
| iPad Safari/touch | UNVERIFIED | Stage-click is implemented as standard Scratch event; device input mapping was not tested. |
| Windows PC / 1080p | UNVERIFIED | No visual hardware run or frame-time capture. |
| Cadence check | PASS, functional only | Scratch VM compatibility 30 vs default 60; see `reports/r2-rate-parity.json`. Not an FPS benchmark. |
