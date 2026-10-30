#!/usr/bin/env python3
"""mau5power -- keep the helmet cool enough to wear, on the wire.

Three facts set this module's shape.

The board takes 5 A.  622 WS2815 at full white want 11.8 A.  So a frame
that asks for white everywhere is not merely too bright, it is asking
for more than twice what the hardware can deliver, and nothing upstream
of here is obliged to be reasonable.

The LEDs are not all in the same thermal situation.  The 398 on the
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
import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "data", "cal", "power.json")

MA_PER_LED_FULL_WHITE = 19.0      # WS2815 at 12 V
MA_PER_LED_STANDBY = 1.0          # drawn whenever the rail is live

# How fast the governor may give light back, as a factor on its scale
# per second (PowerGuard.apply has the measurements).  Taking light away
# is never slowed: that is what keeps every frame inside the budget.
# GOV_MIN_DT is the step a call counts as when the clock does not move
# -- mau5ctl's preview holds it still on purpose, and the scale must
# still be able to come back -- and GOV_FROM the lowest scale the ramp
# starts from, so a governor driven to zero can climb out at all.
GOV_RISE = 1.0
GOV_MIN_DT = 1.0 / 40.0
GOV_FROM = 0.01


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
        # NaN plus anything is NaN and the clamp below keeps it, so one
        # bad reading used to switch the ramp off for good (the phone's
        # twin did exactly that).  A reading that is not a number is not
        # a reading: skip it and keep the level we had.
        if not (math.isfinite(led_watts) and math.isfinite(now)):
            return self.allowance_w()
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
                 thermal=None, link_ma=0.0):
        self.count = int(count)
        self.thermal = thermal
        self.regions = sorted(regions, key=lambda r: r.lo)
        self.budget_ma = float(budget_ma)
        # What the weakest connector between the supply and the strips
        # can carry, continuously, in total.  The budget above is about
        # heat in the helmet and headroom at the supply; neither is the
        # real ceiling if the current has to cross a contact that
        # cannot take it.  A Dupont pin is rated about an amp, and this
        # helmet was being allowed 1.5 A of LED current on top of 0.6 A
        # of standby.  Two amps through a one amp contact trips nothing
        # -- it just gets hot, and the first sign is a melted housing.
        self.link_ma = float(link_ma or 0.0)
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
        # The ceiling is a soft knee (see apply).  It starts to bend at
        # _klo and has _kw left above that before the ceiling.  The bend
        # is placed so that full drive, 255, is four widths past it:
        # e**-4 short of the ceiling, under 2%, so the top end the
        # ceilings were tuned for is where it was.  On a ceiling of 255
        # it never bends -- a tube is not dimmed by a ceiling it cannot
        # reach -- and on a rim at 160 only the top 20% does.
        c = self._ceil.astype(np.float64)
        self._klo = np.minimum(np.maximum((4.0 * c - 255.0) / 3.0, 0.0), c)
        self._kw = c - self._klo
        self._gov_s = 1.0          # the governor's scale on the last frame
        self._gov_t = None         # and when that was

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
    def link_limit_ma(self):
        """LED current the weakest connector leaves room for, or None.

        Standby crosses the same joint, so it comes off the top.
        """
        if not self.link_ma:
            return None
        return max(0.0, self.link_ma - self.standby_ma())

    def apply(self, buf, now=None, gain=1.0):
        """Return (clamped frame, report).  Never raises on a bad frame.

        `now` overrides the clock, so the thermal behaviour can be driven
        deterministically in a test instead of in real time.

        `gain`, at most 1, is applied after every limit.  It is how a show
        pulses on the beat: anything brighter on the beat than off it,
        applied before the guard, is exactly what the ceilings and the
        governor exist to take away again, so on loud material the pulse
        vanished.  Dimming the result can only stay inside the limits.
        """
        now = time.monotonic() if now is None else now
        with np.errstate(over="ignore", invalid="ignore"):
            out = np.asarray(buf, np.float32).reshape(-1, 3)[:self.count].copy()
        # Only the LEDs both the frame and the profile have: a frame
        # shorter than the profile used to fail on the ceiling below,
        # and the phone's twin read past its end into NaN.
        m = len(out)
        # Anything that is not a number is dark, and infinity is full.
        # np.clip passes NaN through untouched, and the phone guard's
        # clamp did the same: one NaN frame made its current NaN, which
        # no budget compares greater than, and its thermal level NaN for
        # good -- governor and thermal ramp off until the page reloaded.
        np.nan_to_num(out, copy=False, nan=0.0, posinf=255.0, neginf=0.0)
        np.clip(out, 0, 255, out)
        asked = self.frame_ma(out)
        amx = out.max(1)               # what was asked of each LED, for the floor

        # -- the ceiling, as a soft knee ---------------------------------
        # It was min(v, c), a clip, and presets render up to 255 against
        # a shell ceiling of 64.  Everything above a quarter of full came
        # out the same, so a soft shape became a flat disc: the eyes
        # draw a gradient, and 80% of their lit LEDs left here at 90% of
        # the frame's maximum or more, popping on and off at the edge as
        # they moved instead of fading.  Saturated colours suffered the
        # same way -- orange (255, 128, 0) clipped to yellow.
        #
        # Below _klo nothing changes.  Above it the value bends towards
        # the ceiling, with slope one at the bend so there is no kink:
        #     lo + w * (1 - exp(-(v - lo) / w))
        # which is below both v and the ceiling for every v, so it can
        # only take current away.  On the shell, a quarter of full, the
        # bend starts at zero -- c * (1 - exp(-v / c)) -- so its dim
        # colours come out a little dimmer as well (20 -> 17, 64 -> 40),
        # and its full ones 2% dimmer.  The eyes now leave about 40% of
        # their lit LEDs in that top tenth instead of 80%, and through
        # the phone's twin the shell's frame-to-frame jitter on eq and
        # the Dimension Remix eq cue fell by 35-60%.
        v = out.astype(np.float64)
        lo, w = self._klo[:m, None], self._kw[:m, None]
        bent = v > lo
        if bent.any():
            wd = np.where(w > 0, w, 1.0)       # no room to bend: a hard clip
            with np.errstate(over="ignore", invalid="ignore"):   # LEDs below lo
                soft = np.where(w > 0, lo - w * np.expm1(-(v - lo) / wd), lo)
            out[:] = np.where(bent, soft, v)
        after_ceiling = self.frame_ma(out)

        # -- each region inside its own allowance -----------------------
        hit = []
        for r in self.regions:
            lo, hi = max(0, r.lo), min(m - 1, r.hi)
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
        link = self.link_limit_ma()
        if link is not None:
            budget = min(budget, link)
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
        #
        # And s gives light back slowly.  Solved afresh every frame, it
        # moved with whatever the ears were doing, and the shell, at
        # s ** 6, moved six times as far the other way: eq bars or a
        # sparkle overlay on the tubes pumped the shell frame to frame.
        # So s may never be more than GOV_RISE e-folds per second above
        # the last frame's -- a compressor's slow release -- while a
        # smaller s still applies at once.  Never above the s solved for,
        # so never over budget; and it runs on frames under budget too,
        # or the climb back would be one jump.  Measured through the
        # phone's twin with the test suite's music drive, at 15 and 40
        # fps, where the governor binds -- blades, spectrum, the Dimension
        # Remix blades cue, beneath's split under a sparkle overlay -- it
        # took a further 3-17% off the shell's frame-to-frame jitter on
        # top of the soft ceiling, for 2-6% of their current.  A rate per
        # region, so the shell climbs no faster than the tubes, lost 30%
        # of the light on that split and made it jitter more: one frame
        # over budget then held the shell down for two seconds.  Half
        # this rate cost up to 15%.
        cap = 1.0
        if self._gov_s < 1.0:
            dt = (now - self._gov_t
                  if self._gov_t is not None and math.isfinite(now) else 0.0)
            cap = min(1.0, max(self._gov_s, GOV_FROM)
                      * math.exp(GOV_RISE * min(max(dt, GOV_MIN_DT), 5.0)))
        over = after_region > budget and after_region > 0
        governed = floored = False
        scale = 1.0
        if over or cap < 1.0:
            per = self._per_led_ma(out)
            omx = out.max(1)
            lit = (amx > 0) & (omx > 1e-6)
            fs = np.zeros(m, np.float32)
            np.divide(self._floor[:m], omx, out=fs, where=lit)
            np.clip(fs, 0.0, 1.0, out=fs)
            if float((per * fs).sum()) > budget:
                fs[:] = 0.0            # the floor does not fit; budget wins
            shed = self._shed[:m]
            lo_s = 1.0
            if over:
                lo_s, hi_s = 0.0, 1.0
                for _ in range(40):
                    mid = (lo_s + hi_s) / 2.0
                    if float((per * np.maximum(mid ** shed, fs)).sum()) > budget:
                        hi_s = mid
                    else:
                        lo_s = mid
            scale = min(lo_s, cap)
            if scale < 1.0:
                base = scale ** shed
                out *= np.maximum(base, fs)[:, None]
                governed = after_region > 0
                floored = bool((fs > base).any())
        self._gov_s = scale
        if math.isfinite(now):
            self._gov_t = now

        g = min(max(float(gain), 0.0), 1.0)
        if g < 1.0:
            out *= g
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
            "link_ma": self.link_ma or None,
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
def timid(count):
    """The guard to use when there is no measured profile.

    Every LED at an eighth of full drive, 300 mA of LED current in all
    and a thermal bucket a tenth the size of the measured one.  Dim, but
    nothing it can be asked to show will hurt the helmet, which is the
    point: this used to return None, every caller took None to mean "no
    guard", and a missing file therefore meant an unlimited helmet.
    """
    return PowerGuard(count, [Region("all", 0, count - 1, 32, 300.0)], 300.0,
                      default_ceiling=32,
                      thermal=ThermalBudget(9.0, 300.0, 12.0, count * 0.012, 0.30))


def load(path=DEFAULT, count=None):
    """Read a power profile.  Missing file -> a deliberately timid one.

    A file that is there but unreadable is an error, raised, not a
    reason to fall back: the fallback is dimmer than any real profile,
    so a typo would look like a dull helmet rather than a broken file.
    """
    if not os.path.exists(path):
        import sys
        print("mau5power: no profile at %s -- using a deliberately timid one"
              % path, file=sys.stderr)
        return timid(count or 621)
    try:
        d = json.load(open(path))
        regions = [Region(r["name"], r["lo"], r["hi"], r["ceiling"],
                          r["budget_ma"], r.get("shed", 1.0), r.get("floor", 0.0))
                   for r in d["regions"]]
    except (ValueError, KeyError, TypeError) as e:
        raise ValueError("power profile %s is unreadable (%s): fix it rather "
                         "than run without one" % (path, e)) from e
    th = None
    if d.get("thermal"):
        t = d["thermal"]
        th = ThermalBudget(t.get("sustained_w", 11.0), t.get("burst_j", 900.0),
                           t.get("max_w"), t.get("standby_w", 0.0),
                           t.get("ramp", 0.30))
    return PowerGuard(count or d["count"], regions, d["budget_ma"],
                      d.get("default_ceiling", 32), thermal=th,
                      link_ma=d.get("link_ma", 0.0))


def save(guard, path=DEFAULT):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    th = guard.thermal
    # Every field load() reads, or a round trip quietly drops it: this
    # used to lose each region's floor and the connector limit.
    json.dump({"count": guard.count, "budget_ma": guard.budget_ma,
               "default_ceiling": guard.default_ceiling,
               "thermal": ({"sustained_w": th.sustained_w, "burst_j": th.burst_j,
                            "max_w": th.max_w, "standby_w": th.standby_w,
                            "ramp": th.ramp} if th else None),
               "regions": [{"name": r.name, "lo": r.lo, "hi": r.hi,
                            "ceiling": r.ceiling, "budget_ma": r.budget_ma,
                            "shed": r.shed, "floor": r.floor}
                           for r in guard.regions],
               "link_ma": guard.link_ma},
              open(path, "w"), indent=1)
    return path


if __name__ == "__main__":
    g = load()
    if g is None:
        raise SystemExit("no profile at %s -- run mau5power_init" % DEFAULT)
    print(g.describe())
