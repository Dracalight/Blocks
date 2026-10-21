# Changelog — NEXUS BLOCKS

## Firma y efectos de sonido — 2026-10-21

- Added the small Japanese creator signature to both stage backdrops, with a vector thumbs-up for reliable Scratch rendering.
- Added only approved WAV effects 07–13 and mapped line clears, Chaos warnings, level increases and game starts to their events.
- Restored the documented level progression at every 10 cleared lines while preserving the level multiplier for the boundary-clearing move.
- Added structural and functional checks for the assets, sound selection, one-shot warning and level progression.

## Keyboard overhaul — 2026-10-19

- Removed all touch sprites, click handlers, old difficulty selection, Relax and Sprint.
- Added a minimal English stage, keyboard menu and stamped HUD without variable monitors.
- Centralized automatic gravity, paused game time, surface lock delay and keyboard edge/repeat handling.
- Normal / Hard / Chaos start at 0.65 / 0.30 / 0.23 seconds per row, with progressive acceleration.
- Chaos adds S/Z windows, warned garbage, speed bursts and escalating event frequency.
- Preserved classic mechanics; added collision checks after hold swaps and garbage.
- Added official Scratch VM scheduler tests and browser import/gameplay checks.

## Previous second stage — 2026-10-19

Added the original Chaos, Sprint, line effects and eight synthesized sounds. Validation covered structure and isolated procedures. This version used touch controls and Spanish UI. Source and SB3 remain recoverable through Git history.

## Previous first stage — 2026-10-19

Introduced the native Scratch Pen renderer, 10x20 board, seven pieces, geometry tables, wall kicks, ghost, hold, line clearing, four difficulties and touch/keyboard controls.
