---
name: power-budget-conservatism
description: Peaks may go up for effects and shows; nothing may stay raised for ten minutes or more
metadata:
  type: feedback
---

Jones, 2026-10-29, superseding the earlier blanket "always be really
conservative": **"we can raise power for effects and shows, just as
long as it won't be sustained for 10+ min."**

That is a leaky bucket, which `power.json` already models. The lever
is `thermal.burst_j`, not the region ceilings and not `budget_ma`.
It is now 3000 J (was 900).

**Why:** the ten-minute rule has to be checked against *worst-case*
content, not an assumed average. 5100 J looked right on paper -- it
is exactly (19.5 - 11.0) W x 600 s -- and breaks the rule, because
full-bright starts near 25 W and the allowance eases down rather than
stepping, so at ten minutes it is still drawing 14.3 W. 4000 J is the
real limit; 3000 J takes all the measurable benefit with margin.

**How to apply:** `python3 mau5tune.py` scores every show for how
well its current tracks the music. The change took the mean follow
from +0.23 to +0.43 and Strobe from +0.02 to +0.42, at 522 -> 700 mA
mean. Any further rise needs re-checking at ten minutes with
`test_mau5.py power`, and the next lever after that is `budget_ma`
(every peak is pinned at 1000 mA), which also needs the controller's
per-bus ABL raised to match -- see
[[offline-mode-is-unverified-on-hardware]].

Still true: never raise a ceiling *just* because an effect looks dim,
and the thermal numbers are hand-calibrated. Feel the helmet after a
long show.
