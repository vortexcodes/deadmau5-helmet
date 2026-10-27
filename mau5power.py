#!/usr/bin/env python3
"""mau5power -- keep the helmet cool enough to wear, on the wire.

Three facts set this module's shape.

The board takes 5 A.  622 WS2815 at full white want 11.8 A.  So a frame
that asks for white everywhere is not merely too bright, it is asking
for more than twice what the hardware can deliver, and nothing upstream
of here is obliged to be reasonable.

The LEDs are not all in the same thermal situation.  The 399 on the
shell are held on with hot glue inside a sealed print, and when that
softens they fall off.  The ear tubes hang in free air and have to
shine through a diffuser, so they can take much more.  One global
brightness number cannot express that; a ceiling per region can.

And a WS2815 draws about 1 mA per LED whenever 12 V reaches it, lit or
not.  For this chain that is ~0.6 A, ~7.5 W of heat, before a single
pixel is on.  No setting here touches it.  It is why the helmet gets
warm with everything dark, and the only cure is to cut the supply.

Two mechanisms, in order:

  ceiling   a per-LED cap by region, so the shell can never be driven
            as hard as a tube even by a frame that asks for it.

  governor  if the whole frame still estimates over budget, scale it
            back -- but shed from the shell first and the tubes last,
            so what survives is the part that is both safe and visible.

A frame is never passed through unchanged on trust.
"""

from __future__ import annotations

import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "data", "cal", "power.json")

MA_PER_LED_FULL_WHITE = 19.0      # WS2815 at 12 V
MA_PER_LED_STANDBY = 1.0          # drawn whenever the rail is live


class Region:
    """A span of the chain with its own thermal allowance.

    Two numbers, because they answer different questions.  ``ceiling``
    is per LED: how hard may any single pixel here ever be driven.
    ``budget_ma`` is for the span as a whole: how much current may all
    of them draw at once.  Sparse content stays bright because it never
    reaches the budget; a region asked to go solid white dims itself
    instead of browning out the rest of the helmet.
    """

    def __init__(self, name, lo, hi, ceiling, budget_ma, shed=1.0, floor=0.0):
        self.name, self.lo, self.hi = name, int(lo), int(hi)
        self.ceiling = int(ceiling)        # 0-255, per channel, per LED
        self.budget_ma = float(budget_ma)  # for the whole span
        # The dimmest this region is allowed to be driven while it is
        # being asked for anything at all.  Weighted shedding is right
        # about priority and wrong about the endpoint: a shell with
        # shed 6 is at nothing long before the tubes have given up, so
        # a helmet left running settles into two glowing stripes and
        # stops reading as a helmet.  The floor costs a few milliamps
        # and keeps the shape.  It never lights an LED the preset
        # wanted dark, and it yields entirely if it will not fit.
        self.floor = float(floor)          # 0-255, per LED
        self.shed = float(shed)            # relative give under global pressure

    @property
    def n(self):
        return self.hi - self.lo + 1

    def full_white_ma(self):
        return self.n * MA_PER_LED_FULL_WHITE * self.ceiling / 255.0

    def __repr__(self):
        return ("Region(%s %d..%d ceiling=%d budget=%.0fmA shed=%.1f)"
                % (self.name, self.lo, self.hi, self.ceiling,
                   self.budget_ma, self.shed))



class ThermalBudget:
    """A leaky bucket over delivered energy, so brightness is rationed
    over time instead of only per frame.

    The per-frame guard answers "is this frame too much".  It cannot
    answer "has this been too much for the last four minutes", and that
    is the question that melts hot glue: a helmet survives a bright
    chorus and dies on a bright half-hour.

    So energy above what the helmet can shed accumulates in a bucket of
    size `burst_j`, which is its thermal mass in the only unit that
    matters here.  While there is room, frames pass at full budget.  As
    the bucket fills, the allowance falls towards `sustained_w` -- not
    to zero, because going dark mid-set is worse than going dim.  Quiet
    passages drain the bucket and bank headroom for the next drop.

    The two numbers are deliberately things you can calibrate by hand:
    run it, feel the helmet, and move `sustained_w` until a long set
    stays comfortable.  Nothing here models conduction or airflow; it
    does not need to, because the bucket is measured, not derived.

    What it cannot do is touch standby.  A WS2815 draws about a
    milliamp whenever 12 V reaches it, lit or dark -- roughly 7.5 W
    across this chain -- and that floor is subtracted here before
    anything is rationed, because pretending otherwise would hand out
    headroom that does not exist.
    """

    def __init__(self, sustained_w=11.0, burst_j=900.0, max_w=None,
                 standby_w=0.0, ramp=0.30):
        self.sustained_w = float(sustained_w)
        self.burst_j = float(burst_j)
        self.max_w = float(max_w) if max_w else None
        self.standby_w = float(standby_w)
        self.ramp = float(ramp)
        self.level = 0.0                  # joules banked against us
        self._last = None

    def allowance_w(self):
        """LED watts permitted right now, standby already deducted."""
        head = 1.0 - self.level / max(self.burst_j, 1e-6)
        k = min(max(head / max(self.ramp, 1e-6), 0.0), 1.0)
        sustained_led = max(self.sustained_w - self.standby_w, 0.0)
        top = (self.max_w - self.standby_w) if self.max_w else sustained_led
        return sustained_led + max(top - sustained_led, 0.0) * k

    def update(self, led_watts, now=None):
        """Charge the bucket for the energy just delivered."""
        now = time.monotonic() if now is None else now
        if self._last is None:
            self._last = now
            return self.allowance_w()
        dt = max(0.0, min(now - self._last, 5.0))   # ignore long stalls
        self._last = now
        total = led_watts + self.standby_w
        self.level += (total - self.sustained_w) * dt
        self.level = min(max(self.level, 0.0), self.burst_j)
        return self.allowance_w()

    def state(self):
        return {"level_j": round(self.level, 1), "burst_j": self.burst_j,
                "full_pct": round(100.0 * self.level / max(self.burst_j, 1e-6), 1),
                "allowance_w": round(self.allowance_w(), 2),
                "sustained_w": self.sustained_w, "standby_w": self.standby_w}


class PowerGuard:
    """Clamps a frame to what the helmet can survive."""

    def __init__(self, count, regions, budget_ma, default_ceiling=32,
                 thermal=None):
        self.count = int(count)
        self.thermal = thermal
        self.regions = sorted(regions, key=lambda r: r.lo)
        self.budget_ma = float(budget_ma)
        self.default_ceiling = int(default_ceiling)
        self._ceil = np.full(self.count, float(default_ceiling), np.float32)
        self._shed = np.full(self.count, 4.0, np.float32)
        self._floor = np.zeros(self.count, np.float32)
        for r in self.regions:
            lo, hi = max(0, r.lo), min(self.count - 1, r.hi)
            if hi >= lo:
                self._ceil[lo:hi + 1] = r.ceiling
                self._shed[lo:hi + 1] = r.shed
                self._floor[lo:hi + 1] = min(r.floor, r.ceiling)

    # -- estimates ------------------------------------------------------
    def _per_led_ma(self, out):
        return out.sum(1) / (3.0 * 255.0) * MA_PER_LED_FULL_WHITE

    def frame_ma(self, buf):
        """Estimated LED current for a frame, standby excluded."""
        return float(np.asarray(buf, np.float32).sum()
                     / (3 * 255.0) * MA_PER_LED_FULL_WHITE)

    def standby_ma(self):
        return self.count * MA_PER_LED_STANDBY

    # -- the clamp ------------------------------------------------------
    def apply(self, buf, now=None):
        """Return (clamped frame, report).  Never raises on a bad frame.

        `now` overrides the clock, so the thermal behaviour can be driven
        deterministically in a test instead of in real time.
        """
        out = np.asarray(buf, np.float32).reshape(-1, 3)[:self.count].copy()
        np.clip(out, 0, 255, out)
        asked = self.frame_ma(out)

        np.minimum(out, self._ceil[:, None], out)
        after_ceiling = self.frame_ma(out)

        # -- each region inside its own allowance -----------------------
        hit = []
        for r in self.regions:
            lo, hi = max(0, r.lo), min(self.count - 1, r.hi)
            if hi < lo:
                continue
            seg = out[lo:hi + 1]
            ma = float(seg.sum() / (3 * 255.0) * MA_PER_LED_FULL_WHITE)
            if ma > r.budget_ma and ma > 0:
                seg *= r.budget_ma / ma
                hit.append(r.name)
        after_region = self.frame_ma(out)

        # -- the thermal allowance, if one is in force -------------------
        # The per-frame budget is a ceiling; this is the rolling one.  It
        # is applied before the global scale so the two compose rather
        # than fight: whichever is tighter at this instant wins.
        budget = self.budget_ma
        if self.thermal is not None:
            allowed_ma = self.thermal.allowance_w() / 12.0 * 1000.0
            budget = min(budget, max(allowed_ma, 0.0))

        # -- and the whole frame inside the global one ------------------
        # Scale region g by s**shed_g and solve for the single s that
        # lands on budget.  Monotonic in s, so bisect: a frame that asks
        # for too much comes back dimmer everywhere, weighted, rather
        # than with the low-priority regions amputated.
        #
        # The floor is solved here too, not afterwards.  The governor
        # spends the budget exactly, so a floor applied as a second pass
        # has nothing left to spend and collapses to nothing: the two
        # have to be one equation.  Each LED ends at
        #     max(s ** shed_i, floor_i / level_i)
        # of what survived its region, so the floored LEDs take their
        # few milliamps off the top and everything else sheds around
        # them.  Still monotonic in s, so the bisection stands.
        governed = floored = False
        if after_region > budget and after_region > 0:
            per = self._per_led_ma(out)
            omx = out.max(1)
            amx = np.asarray(buf, np.float32).reshape(-1, 3)[:self.count].max(1)
            lit = (amx > 0) & (omx > 1e-6)
            fs = np.zeros(self.count, np.float32)
            np.divide(self._floor, omx, out=fs, where=lit)
            np.clip(fs, 0.0, 1.0, out=fs)
            if float((per * fs).sum()) > budget:
                fs[:] = 0.0            # the floor does not fit; budget wins
            lo_s, hi_s = 0.0, 1.0
            for _ in range(40):
                mid = (lo_s + hi_s) / 2.0
                if float((per * np.maximum(mid ** self._shed, fs)).sum()) > budget:
                    hi_s = mid
                else:
                    lo_s = mid
            scale = np.maximum(lo_s ** self._shed, fs)
            out *= scale[:, None]
            governed = True
            floored = bool((fs > lo_s ** self._shed).any())

        final = self.frame_ma(out)
        if self.thermal is not None:
            self.thermal.update(final * 12.0 / 1000.0, now=now)
        return np.clip(out, 0, 255).astype(np.uint8), {
            "asked_ma": round(asked, 1),
            "after_ceiling_ma": round(after_ceiling, 1),
            "after_region_ma": round(after_region, 1),
            "sent_ma": round(final, 1),
            "standby_ma": round(self.standby_ma(), 1),
            "total_ma": round(final + self.standby_ma(), 1),
            "amps": round((final + self.standby_ma()) / 1000.0, 2),
            "watts": round((final + self.standby_ma()) * 12 / 1000.0, 1),
            "ceiling_hit": asked > after_ceiling + 0.5,
            "regions_hit": hit,
            "governor_hit": governed,
            "floor_hit": floored,
            "budget_ma": round(budget, 1),
            "thermal": self.thermal.state() if self.thermal else None,
        }

    # -- reporting ------------------------------------------------------
    def describe(self):
        L = ["global budget %.0f mA of LED current" % self.budget_ma,
             "standby        %.0f mA  (%.1f W, drawn whenever 12 V is on -- "
             "nothing here can reduce it)"
             % (self.standby_ma(), self.standby_ma() * 12 / 1000.0)]
        worst = 0.0
        for r in self.regions:
            worst += min(r.full_white_ma(), r.budget_ma)
            L.append("  %-12s %4d..%-4d %4d leds  ceiling %3d/255  "
                     "budget %4.0f mA  (all-white would want %5.0f)  shed %.0f"
                     % (r.name, r.lo, r.hi, r.n, r.ceiling, r.budget_ma,
                        r.full_white_ma(), r.shed))
        held = min(worst, self.budget_ma)
        L.append("  every region at its own limit at once: %.0f mA" % worst)
        if self.thermal:
            t = self.thermal
            L.append("  thermal: sustains %.1f W (of which %.1f W is standby), "
                     "bursts to %.1f W on %.0f J of thermal mass"
                     % (t.sustained_w, t.standby_w, t.max_w or 0, t.burst_j))
            L.append("           full brightness for about %.0f s before it eases off"
                     % (t.burst_j / max((t.max_w or 0) - t.sustained_w, 0.1)))
        L.append("  the global governor holds that to %.0f mA -> %.2f A "
                 "with standby, %.1f W"
                 % (held, (held + self.standby_ma()) / 1000.0,
                    (held + self.standby_ma()) * 12 / 1000.0))
        return "\n".join(L)


# ----------------------------------------------------------------------
def load(path=DEFAULT, count=None):
    """Read a power profile.  Missing file -> a deliberately timid one."""
    if not os.path.exists(path):
        return None
    d = json.load(open(path))
    regions = [Region(r["name"], r["lo"], r["hi"], r["ceiling"],
                      r["budget_ma"], r.get("shed", 1.0), r.get("floor", 0.0))
               for r in d["regions"]]
    th = None
    if d.get("thermal"):
        t = d["thermal"]
        th = ThermalBudget(t.get("sustained_w", 11.0), t.get("burst_j", 900.0),
                           t.get("max_w"), t.get("standby_w", 0.0),
                           t.get("ramp", 0.30))
    return PowerGuard(count or d["count"], regions, d["budget_ma"],
                      d.get("default_ceiling", 32), thermal=th)


def save(guard, path=DEFAULT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    th = guard.thermal
    json.dump({"count": guard.count, "budget_ma": guard.budget_ma,
               "default_ceiling": guard.default_ceiling,
               "thermal": ({"sustained_w": th.sustained_w, "burst_j": th.burst_j,
                            "max_w": th.max_w, "standby_w": th.standby_w,
                            "ramp": th.ramp} if th else None),
               "regions": [{"name": r.name, "lo": r.lo, "hi": r.hi,
                            "ceiling": r.ceiling, "budget_ma": r.budget_ma,
                            "shed": r.shed}
                           for r in guard.regions]},
              open(path, "w"), indent=1)
    return path


if __name__ == "__main__":
    g = load()
    if g is None:
        raise SystemExit("no profile at %s -- run mau5power_init" % DEFAULT)
    print(g.describe())
