---
name: offline-mode-is-unverified-on-hardware
description: Superseded — offline mode has now been run against the helmet; what that found, and what the simulator must model
metadata:
  type: project
---

Offline mode was run against the real controller on 2026-10-28 and
four of its assumptions were wrong. All four failed by *sending
successfully and changing nothing*, so none could have been caught
without reading the strip back — which is what `mau5peek.py` is for.

On WLED 0.15.4 (GLEDOPTO_ETH):

- a `seg.i` write **blanks the rest of the segment**, so deltas and
  split frames are invalid; one whole frame per message
- a WebSocket message over one TCP segment (1436 B) is **dropped in
  silence**; 1428 lands, 1448 does not. HTTP POST has no such limit
- WLED **does not echo** an `i` write, so pacing on acknowledgements
  stalls
- `hw.led.maxpwr` is accepted and ignored; the **per-bus** limiter is
  the enforced one, and it does not see frozen-segment pixels at all

**Why:** these are firmware behaviours, not design choices, and the
next person to touch the wire will reach for deltas again.

**How to apply:** before trusting any change to `remote/offline/`,
check it against `mau5peek`, and make `mau5fake.py` model the
behaviour first — the fake modelled none of these, which is exactly
why the tests passed on a broken player. See [[repo-is-public]] and
[[power-budget-conservatism]].
