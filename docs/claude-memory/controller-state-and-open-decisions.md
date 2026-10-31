---
name: controller-state-and-open-decisions
description: "Helmet controller as of 2026-10-30 -- now official WLED 16.0.1 (flashed from GLEDOPTO's 0.15.4), binary DDP from the phone, global limiter covers everything, standby button awaiting first use, still drives 622"
metadata:
  node_type: memory
  type: project
  originSessionId: 208332e7-8c9f-4c25-bc21-e9a9df98fa1f
  modified: 2026-10-30T14:28:23.731Z
---

- **Firmware: official WLED 16.0.1 `ESP32_Ethernet`**, flashed over the air
  on 2026-10-30 07:13 with Jones's go-ahead, from GLEDOPTO's own 0.15.4
  build (`repo GLEDOPTO/WLED`, product GLEDOPTO_ETH). Settings carried over
  exactly. Pre-flash cfg backup and `WLED_0.15.4_ESP32_Ethernet.bin` for
  rollback were kept in that session's scratchpad (`scratchpad/fw/`), not
  the repo; re-download from github.com/wled/WLED releases if needed.
- **The phone page sends binary DDP over the WebSocket on 16+** (first byte
  2, packets padded to 1428, push on the last, 'p'/pong pacing, 3 frames in
  flight, filler as binary 0xFF so it takes no JSON lock). It falls back to
  JSON segments + 1 frame in flight if `/json/info` ver is < 16. Measured on
  16.0.1: median 23.5 fps with a 100 ms simulated phone round trip (5-8 on
  0.15.4), no restarts in monitored sweeps. 16.0.1 has ~90 kB free heap at
  idle (0.15.4 had ~118 kB).
- **The page keeps the nightlight off on the binary path.** WLED 16's loop does not
  run the nightlight during realtime, so re-arms do nothing and it fires on the
  first 2.5 s gap in frames, leaving the helmet dark under a running page.
  Reproduced on the helmet 2026-10-30. The page now checks every 5 s that it is
  still on. Never send `on:false` from a test while another device streams.
- **On 0.15.4 more than one frame in flight restarted the controller** (JSON
  parsing + a {"success":true} reply per message). Irrelevant while on 16,
  but do not raise DEPTH on the JSON path.
- **No presets saved as of 2026-10-30 09:00** (`/presets.json` `{"0":{}}`);
  the page switches off on stop. The page's "set up" button next to standby
  glow measures pacifica and saves preset 1 plus the boot preset. Deployed to the
  helmet 2026-10-30, tested against a stand-in only, so check whether it
  has been pressed.
- **WLED 16's limiter is the global `hw.led.maxpwr` (1622), not the per-bus cap.**
  `applyABL` ignores bus caps while the global is non-zero, and it covers phone
  and laptop DDP frames too, so frames above about 0.9 A of LED current get
  scaled (source only, not measured). `mau5offline config/check` and
  `mau5doctor` still assume 0.15's per-bus behaviour.
- **WLED still drives 622** (the chain is 621, mau5slots.CUT). Harmless.

**Why:** device state invisible from the code. **How to apply:** check
`/json/info` `ver`, `release` and `/presets.json` before assuming any of
this. Load-test ONE thing at a time with a monitor; keep headless Chrome's
page visible (`Page.bringToFront`, focus emulation) or timers throttle to
1 Hz; a headless browser that navigated many times keeps several sockets
open on the controller (close it, ws drops to 0).
Related: [[power-budget-conservatism]], [[phone-camera-lags-a-second]].
