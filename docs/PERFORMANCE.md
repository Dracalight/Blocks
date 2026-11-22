# Performance — R2

No 60-FPS claim is made. The Scratch VM project tick and headless test durations are not a browser FPS benchmark. Average/min FPS, frame-time p95/p99, memory, clone counts in TurboWarp, and input-to-render latency are unmeasured. The current scene uses eight simple visual targets, no particle system, no cloning, and `wait 0` yields in each visual script.

A 30-FPS-compatibility versus default Scratch VM test compares normalized world speed and ground position. This checks simulation behavior; it does not establish the requested frame-time targets or device performance. See `reports/r2-runtime-test.json` for measured test output once populated by the final test run.
