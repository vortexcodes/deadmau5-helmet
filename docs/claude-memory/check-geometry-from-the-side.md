---
name: check-geometry-from-the-side
description: "Validate any map or geometry change from the side and against the CAD, never only from the camera that produced it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 208332e7-8c9f-4c25-bc21-e9a9df98fa1f
  modified: 2026-10-29T20:13:48.500Z
---

Jones caught a wrong map in two seconds by turning the simulator
side-on ("the front looks good but the sides are wrong"), after it had
been reported as correct for days. The map had been fitted to the
front camera, so it matched that camera to 0.02 px and nothing else.

**Why:** a fit always agrees with the data it was built from; only a
view it never saw can say it is wrong. The CAD is the ground truth for
positions -- Jones guarantees every LED sits in a CAD slot or ear tube,
though not every slot is populated -- and the cameras are trustworthy
only where they are calibrated (the shell), not out at the ears.

**How to apply:** before calling a geometry change done, render front,
side and top views against the CAD mesh (and the daylight photo from
the high pose), and quote a number from an independent view: the other
camera, the hand walk in walk_session.json, or the photo outline. A
residual near zero against the source camera is a warning, not a
result. Related: [[offline-mode-is-unverified-on-hardware]],
[[camera-page-must-be-started-by-hand]].
