# NEXUS BLOCKS — Keyboard Arcade

A native Scratch 3 falling-block game for computers and landscape iPads with physical keyboards.

- [Download the Scratch project (.sb3)](https://github.com/Dracalight/Blocks/raw/refs/heads/main/NEXUS-BLOCKS-ENDLESS.sb3)
- [Download the complete repository (.zip)](https://github.com/Dracalight/Blocks/archive/refs/heads/main.zip)

Open the [official Scratch editor](https://scratch.mit.edu/projects/editor/), choose **File → Load from your computer**, and select the SB3. Use full screen, click the green flag, choose **1 / 2 / 3**, then press **Enter**. Keep the stage focused so it receives keyboard input.

## Modes

| Mode | Initial gravity | Progression |
| --- | --- | --- |
| **1 — NORMAL** | 0.65 seconds / row | Balanced; faster every 10 lines. |
| **2 — HARD** | 0.30 seconds / row | Faster immediately; stronger level acceleration. |
| **3 — CHAOS** | 0.23 seconds / row | Accelerates with levels and survival; S/Z windows, speed bursts and warned garbage attacks. |

The original three modes are endless. Gravity runs without keyboard input. The technical minimum is 0.07 seconds / row; this is a configured floor, not an iPad performance guarantee. Pieces lock after 0.35 seconds on a surface. Pause freezes gravity, lock delay and Chaos deadlines.

This development branch also contains an **unfinished NIGHTMARE** mode. Press **4** in the menu, then press **4** again to switch between ENDLESS and TRIALS. Trials uses five waves with lock goals of 20, 25, 30, 35 and 40 pieces, with scripted threats; it keeps the board between waves and waits for committed threats to finish. Glitch Protocol is an initial five-pattern dodge challenge; audiovisual polish, visual QA and playtesting remain incomplete. See [development status](docs/NIGHTMARE_PROGRESS.md); this branch is not ready to merge.

## Keyboard

| Key | Action |
| --- | --- |
| Left / Right Arrow | Move; hold to repeat |
| Down Arrow | Soft drop; hold to repeat |
| Up Arrow | Rotate clockwise with wall kicks |
| Space | Hard drop |
| C | Hold / swap once per piece |
| P | Pause / resume |
| R | Restart the selected mode |
| 1 / 2 / 3 | Select Normal / Hard / Chaos outside active play; returns to a fresh menu |
| Enter | Start from menu / Game Over |

No touch controls remain. See [controls](docs/CONTROLS.md), [architecture](docs/ARCHITECTURE.md), [test evidence and limits](docs/TESTS.md), [changelog](CHANGELOG.md), and the [versioning and release rule](docs/VERSIONING.md). Physical iPad keyboard / Safari acceptance remains pending; desktop browser import and gameplay have been exercised.

## Rebuild and verify

```sh
python tools/build_sb3.py
python tools/validate_sb3.py
python tools/test_sb3.py
npm ci --ignore-scripts
npm test
```

Python 3 builds and validates the game. Node.js and pinned npm packages are only for the separate official Scratch VM scheduler test (20 seconds per mode). No JavaScript is packaged in the game. The source of truth is tools/build_sb3.py: native Scratch blocks, SVG artwork and synthesized WAV sounds.
