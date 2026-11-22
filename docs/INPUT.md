# Input status

The prototype polls Scratch's `key [space] pressed?` sensor in its loop. This provides basic keyboard input but is level-triggered, not edge-triggered; hold/release semantics, up arrow, mouse, pause, touch, and measured input-to-render latency are not implemented or validated. Safari on a physical iPad has not been tested.
