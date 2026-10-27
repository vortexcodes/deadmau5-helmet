# Build prompt — mau5head show-control software suite

Copy everything below the line into Claude Code (or a fresh Claude chat) as the opening
message. Attach `mau5head_shell.xmodel`, `wiring_chained.csv` and `pixel_map.csv` from the
CAD folder so the tools have the real geometry.

---

I'm building the software for a wearable LED helmet (a deadmau5-style mau5head) and I want
you to write it as a small suite of programs. Read this whole spec before writing code, then
propose a file layout and confirm it with me before you start.

## The hardware, exactly as built

- **Shell:** 948 addressable pixels (WS2815, 12 V, 60/m) recessed into a sphere of radius
  177.17 mm. Pixels sit on 68 vertical channels x up to 22 rows. Channel pitch 16.37 mm,
  row pitch 16.67 mm (5.51 deg). Not a full rectangle: there are holes for the mouth
  opening, the two ear mounts, the visor pivots, and the seam pads, plus reduced density
  above 54 deg (every 2nd channel to 65 deg, every 4th to 76 deg).
- **Two WLED outputs:** output 1 = 549 LEDs (back half, "chain A"), output 2 = 399 LEDs
  (front, "chain B") plus accessories chained after it.
- **Accessories on output 2, in order:** right ear rim strip (~59), right ear blades
  ETR1/2/3 (~44/62/44), visor top light-pipe VT01 (~20), visor bottom VB01 (~20), left ear
  rim (~59), left ear blades ETL1/2/3 (~44/62/44). These counts are estimates until the
  strips are cut; make them configurable.
- **Controller:** ESP32 running WLED, joined to a Raspberry Pi's WiFi access point at a
  static IP, receiving DDP.
- **Player:** Raspberry Pi 4 on the wearer's body running Falcon Player (FPP). It plays the
  audio out its 3.5 mm jack into a Bluetooth speaker's AUX input (wired, for zero latency)
  and streams pixel data to the controller over its own hotspot. No internet at shows.
- **Control surface:** an Android phone joined to the Pi's hotspot.

Attached: `mau5head_shell.xmodel` (xLights custom model), `wiring_chained.csv` (every strip
segment with its LED range, data direction, and what it feeds from/into),
`pixel_map.csv` (channel, row, azimuth, elevation, xyz for all 948 shell pixels), and
`mau5head_sim_backdrop.glb` — a decimated 57k-triangle mesh of the shell, ears and visor
in their assembled positions, for use as the 3D backdrop in the simulator.

Important: the backdrop mesh is **scenery only**. Never derive pixel positions from it —
they come from `pixel_map.csv`, which is authoritative. The mesh and the CSV share the same
coordinate frame (origin = sphere centre, +Z up, -Y front, ±X the visor pivot axis), so
pixels drawn at their CSV xyz land exactly on the shell surface. Load the GLB once at
startup with trimesh or pygltflib; do not load STEP files.

## What I want you to build

### 1. `mau5sim` — a desktop simulator (Python)

The point is to author and preview shows without the helmet on my desk.

- Load `pixel_map.csv` and render the helmet in 3D (matplotlib 3D is fine, or pyvista if
  you prefer) — each pixel as a small square on the sphere at its real position, plus the
  ear rims, ear blades, and visor light-pipes as separate geometry.
- Also render an "unwrapped" 2D view (the 68 x 22 matrix) side by side, because that's
  what xLights shows.
- Play an audio file and drive the simulated pixels in sync, so I can watch a show before
  I load it on the helmet.
- Accept input in three forms: (a) an FSEQ file (the format xLights exports and FPP
  plays), (b) a live DDP stream on UDP 4048 so I can point real WLED/xLights output at the
  simulator, (c) a Python effect function I write myself, called once per frame with the
  frame index and given a pixel array to fill.
- Frame rate 40 fps to match FPP's default.
- Export a preview to MP4 so I can check a show on my phone.

Get the FSEQ parsing right: FSEQ v2 has a header with a variable-length offset to the
channel data, optional compression (zstd or zlib), and a fixed frame size. Read the spec
from the FPP source rather than guessing, and tell me if you need me to fetch it.

### 2. `mau5build` — a show packager (Python CLI)

- Takes an audio file plus either an FSEQ or my own effect function, and produces the
  files FPP needs: the sequence, the media, and a playlist JSON.
- Uploads them to the Pi over its REST API and creates the playlist, so I never have to
  touch the FPP web UI to add a song.
- Verifies the LED counts in the sequence match the helmet's configuration and refuses to
  upload a mismatch (this is the failure mode I actually expect).

### 3. Effect library (Python)

A small set of effects written against the helmet's real geometry, not a generic matrix:

- Sprite/bitmap playback on the 68 x 22 grid (this is how the classic mau5head faces work
  — X eyes, smiles, arrows).
- Scrolling text with a small pixel font, wrapping around the sphere.
- Sweeps and pulses driven by azimuth or elevation, so they follow the head's real shape.
- Ear blade effects treated as 1D strips (they're lightsaber-style tubes).
- Visor edge glow, treated as two 1D strips.
- A beat-synced mode that takes a beat list (from librosa or a hand-tapped file) rather
  than doing live audio analysis — my shows are pre-programmed.

### 4. `mau5remote` — an Android app (later, but design for it now)

For now, keep the existing single-file web page working. Then build a native app:

- Lists the playlists on the Pi, big touch targets, one tap to start.
- Shows what's playing with a progress bar; stop / stop-gracefully; volume.
- Works entirely on the Pi's hotspot with no internet.
- Caches the playlist list so the UI is populated instantly on connect.
- Keeps the screen awake while a show plays and survives being backgrounded.
- Kotlin + Jetpack Compose, talking to FPP's REST API.

### 5. Setup scripts

- A script that configures a fresh FPP install: WiFi hotspot on, audio output to the 3.5 mm
  jack, DDP output to the controller's IP with the right channel count.
- A WLED config JSON I can import: two outputs with the right LED counts and pin
  assignments, static IP, DDP receive on, ABL set to 8 A.
- Both should be idempotent and safe to re-run.

## Constraints and preferences

- Python 3.11+, standard library where possible. numpy is fine. Avoid heavy frameworks.
- Everything must work with no internet at showtime.
- Prefer one file per tool over a deep package tree; I'd rather read one 400-line file than
  ten 40-line ones.
- Copy-paste-ready output: complete files, not fragments.
- Config in one `helmet.toml` — LED counts, IPs, pin numbers, frame rate — read by every
  tool, so there's a single source of truth.
- Tell me when something can't work the way I've described it rather than building a
  workaround silently.

## Order of work

Start with the simulator and the effect library, since those are what let me build shows
before the hardware is finished. Then the packager. Then the setup scripts. The Android app
last — the web page covers me until then.

Before you write anything, tell me the file layout you propose and any part of this spec
you think is wrong.
