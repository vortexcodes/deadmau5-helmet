---
name: phone-camera-lags-a-second
description: "The phone camera behind mau5eye shows the world 1.1-1.5 s late; mau5eye.shot's freshness check does not cover it, so per-LED probes come back one LED late"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 208332e7-8c9f-4c25-bc21-e9a9df98fa1f
  modified: 2026-10-30T08:30:56.608Z
---

Measured 2026-10-30 by toggling a big pattern and timing the first frame
that showed it: a frame *pushed* 1.08-1.54 s after a change is the first
to show it (the page pushes every 0.4 s). `mau5eye.shot(after=t+0.4)` --
which mau5locate uses with `--settle 0.75` -- only guarantees a push
about 0.7-1.2 s after the change, so with this camera most frames show
the previous LED and some catch the dark gap between LEDs. The result
looks like a clean, smoothly progressing scan that is shifted by one
index, plus random "dead" LEDs.

**Why:** it produced a confident wrong conclusion within the hour (a
"one-index shift" that was the camera, mixed with a real one-index cut),
and the old calibration only escaped it because it used a faster camera.

**How to apply:** since 2026-10-30 `mau5eye.shot(lag=...)` and
`mau5eye.measure_lag()` exist and mau5locate measures and waits out the
lag itself; mau5hue, mau5psu and mau5shoot still call shot() without it.
For any other per-LED camera work, measure the lag first and wait for a
frame pushed at least lag + 0.3 s after each change -- 1.8 s worked. A probe that finds LED k where
another finds k+1 is the lag until proven otherwise. Related:
[[camera-page-must-be-started-by-hand]], [[check-geometry-from-the-side]].
