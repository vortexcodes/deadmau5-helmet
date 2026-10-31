---
name: wled16-tears-down-its-access-point
description: Official WLED 16.0.1 drops every phone on its AP every 5 min while home Wi-Fi is out of range; only reproduces away from home
metadata:
  type: project
---

Read in the v16.0.1 source on 2026-10-30, not measured on the helmet. While the
controller's home network is out of range, `handleConnection()` retries it every
18 s with nobody on the AP and every 300 s with somebody on it. `initConnection()`
now calls `WiFi.mode(WIFI_MODE_NULL)`, which tears down the AP (0.15 did not;
upstream `main` still does). Jones reported "randomly disconnects" and "turns off
after about 5 minutes" on the AP after the flash I did that morning.

**Why:** it can't be reproduced at home, where the controller stays joined to home
Wi-Fi, so a clean test on home Wi-Fi proves nothing about it. A stream from the
laptop's Chrome ran 10 minutes at home with no cut-out.

**How to apply:** `firmware/` in the repo has the patch and a build. Check
`/json/info` and ask before assuming it is flashed; it needs Jones's go-ahead.
Testing it needs the helmet away from home, or a phone on the AP with the STA down.
Other things that look similar: the screen locking (page stops) and the heat limit
fading whole-helmet effects to a third between minutes 5 and 7 (by design). Related:
[[controller-state-and-open-decisions]], [[power-budget-conservatism]].
