# Input — R2

Scratch edge-activated `when key pressed` hats handle Space, Up Arrow, P, R, and V. Space/Up start a normal run from MENU, jump only when `grounded`, and restart after DEAD/COMPLETE. V starts PRACTICE. P toggles PAUSED while storing/restoring the prior mode. R restarts a dead/completed run. Stage-click starts or jumps and is the intended pointer/touch adaptation.

The jump is press-triggered, not hold-repeat or buffered. No artificial delay is inserted before input handling; a fixed-step update may observe an event only when the Scratch VM next processes its event queue. The browser's touch-to-stage-click mapping, physical iPad Safari behavior, and input-to-render latency remain unverified.
