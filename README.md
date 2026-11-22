# NEXUS Geometry Dash: SubZero rebuild V1

An original Scratch 3 rebuild project. This first published increment is an **ENGINE_READY prototype**, not a completed SubZero recreation. It contains a native `.sb3` with original vector art and Scratch blocks for a simple auto-scrolling obstacle interaction. No commercial music, extracted game assets, or proprietary source are included.

## Build

Requires Python 3.10+ and uses only the standard library:

```sh
python tools/build.py
python -m unittest discover -s tests -v
```

The output is `dist/Geometry-Dash-SubZero-NEXUS-V1.sb3`. The project is playable as a small jump-and-obstacle prototype; level sequencing and full feature coverage are pending. Open the `.sb3` in Scratch or TurboWarp to inspect/run it. The repository does not claim Scratch VM/TurboWarp compatibility validation until those players are exercised.

## Current status

- M1 architecture and licensing boundaries: documented in `docs/`.
- M2 native `.sb3` prototype: generated; structural tests are supplied.
- Press Start, Nock Em, Power Trip parity and complete playable levels: pending.
- Device QA, latency, frame-time, and 30/60 FPS equivalence: pending.

This branch is intentionally separate from the previous game files. Its first commit is anchored to the repository's existing history because the connected GitHub interface only creates commits with a parent; the branch tree itself contains only this new project.
