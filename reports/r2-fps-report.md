# R2 performance measurements

No browser-render FPS or frame-time benchmark was run. Scratch VM's headless runner has no renderer attached, so its scheduling rate is not treated as a device/browser FPS result. Frame p95/p99, memory, input-to-render latency, PC hardware and iPad Safari are all **not measured**.

The rate parity test runs the same SB3 in Scratch VM's 30-FPS compatibility setting and the default (60-FPS) setting. It reports simulation distance normalized by project timer; this is functional cadence evidence only. It does not establish 60 FPS.
