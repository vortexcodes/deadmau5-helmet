# Where things stand (2026-10-29, afternoon)

## The map is built from the CAD now

The side view was wrong, and the reason was worse than the ears. The
shell positions labelled `cad` were not the CAD: an earlier fix had
slid every LED along the sphere onto its own front-camera ray, which
fits that camera to 0.02 px by construction and put most LEDs between
slots, up to 113 mm off at the edges. The ears were one flat sheet.

`mau5slots.py` replaces all of it. Positions only come from the CAD;
the two camera poses decide which slot. It aligns the chain to the
CAD's wiring order allowing empty slots and never reusing one, and
from the CAD alone it gets:

- 398 shell LEDs in 398 distinct slots, one empty (top of B04)
- the strips at both ear mounts wired out of CAD order, mirror images
- each camera alone, start to finish: the same 398 slots
- 2 px error where a camera sees an LED square-on (was 15)
- 67 of 68 strip boundaries exactly where the hand walk put them

The shell is **398** LEDs, not 399, and the left ear starts at 398.
`power.json`, the docs and the tests all say so now. The ears sit
where the CAD puts them -- a daylight photo from the high pose lines
up with the CAD outline -- and the cameras only choose where along
which tube each LED is.

Rebuild with `python3 mau5slots.py` after any new camera run.
Superseded and removed: `mau5fitmap`, `mau5stereo`, `mau5gaps`.

## Start plays the song

Starting a show used to light the helmet in silence. Now it plays the
song: the first time, it asks for the file and keeps it in the
browser's IndexedDB under the show's name; after that, start just
plays it. "Lights only" runs a show silently on purpose. The website
simulator does the same.

**Not on the controller yet.** Deploy when on the home network:

    python3 mau5offline.py deploy --host 192.168.10.172

## The simulator matches the website

Restyled with the site's own tokens and title blocks, and it draws
the helmet's CAD around the LEDs. Built by `python3 mau5web.py --into
<site checkout>`.

## The film

`python3 mau5film.py` renders a ninety-second explanation of the
localisation from the data, in the site's style, to
`data/cal/localisation.mp4` (not committed -- it is 15 MB and
regenerable). It is on the project page.

## Power guard: no more silent "no guard"

A missing `power.json` used to mean an unguarded helmet: `load()`
returned None and every caller read that as "no limit". A missing file
now gives a deliberately timid guard (300 mA, an eighth of full
drive), and a broken one raises instead of being ignored.

## One camera angle would still help

The photo suggests the left ear is turned a few degrees further than
the CAD. The cameras cannot settle that -- they are calibrated on the
shell and the ear glows are diffuse -- but a pose from the side,
45 degrees or more off the face, would. Nothing is blocked on it.

## The shows follow the music

Jones lifted the power rule: peaks may go up for effects and shows,
as long as nothing stays raised for ten minutes or more. That is a
leaky bucket, which `power.json` already models, so the lever is
`thermal.burst_j` and nothing else -- not the region ceilings, not
`budget_ma`.

`mau5tune.py` is new and measures what was wrong. It renders a show
end to end through the real engine and the real guard and reports
how well the helmet's current tracks the track's loudness:

| | follow | swing | mean |
|---|---|---|---|
| 900 J (before) | +0.23 | 0.71 | 522 mA |
| 3000 J (now) | **+0.43** | 0.72 | 700 mA |

Strobe went from **+0.02 to +0.42** -- from not tracking the music at
all to tracking it properly.

**Swing was never the problem.** An earlier run said it was, and that
was a bug in the scoring tool: one power guard shared across all five
shows, so each arrived with the previous show's thermal bucket
already full and read as flat. Fresh guard per show.

### Sizing it, and why the obvious number is wrong

5100 J is exactly (19.5 - 11.0) W x 600 s and it **breaks the rule**.
Full-bright content starts near 25 W, and the allowance eases towards
sustained rather than stepping to it, so at ten minutes it is still
drawing 14.3 W. Measured: 4000 J is the limit, 3000 J has margin.
The rule is now a test -- `t_thermal_never_exceeds` asserts the draw
at ten minutes of worst-case content, plus the energy invariant
(delivered <= sustained x T + one bucket), which cannot rot the way
the old hard-coded twenty-minute average did.

### The next lever

Every show peaks at exactly 1000 mA, which is `budget_ma`, not the
thermal bucket. Raising it needs the controller's per-bus ABL raised
to match, so it waits for hardware access.

## The ear "line" is four lines, and they are the tubes

Photographed at low level in a dark room: lighting the right ear
alone shows four bright diagonal stripes with dark bands between
them. That is the LED tubes showing through the diffuser, not a
mapping fault -- every LED on the ear is lit in that photograph, so
the pattern is purely where they physically are. Software cannot
even it out; more distance between tube and diffuser, or a second
diffuser layer, would.

The rebuilt map agrees with the photograph now: three tubes per ear,
each run up and back, which is the parallel stripes.

## Reading the strip back: one warning

`mau5peek` is only as good as the quiet around it. A browser tab left
open on the player streams frames continuously and will overwrite
anything a script writes between the write and the look. That cost an
hour and produced two confident, wrong conclusions about the wire
protocol, both of which evaporated when the tab was closed. Before
believing a reading, check `ws` in `/json/info` -- it is the number of
WebSocket clients, and it should be 1 (yours).

## Frame rate

Two lossless improvements, both measured:

- **Black is never sent.** The write blanks the segment, so an LED
  nobody mentions is already off. Worth 0-49% of a frame, and it moves
  `alignbar`, `eyes`, `pinwheel` and `text` onto the websocket.
- **Two HTTP requests in flight** instead of one: 7.3 whole frames a
  second becomes 9.7.

Things that were measured and rejected: global colour quantisation
(13 to 17 of 37 presets, at a visible cost), tolerant run-merging
(same), and websocket fragmentation -- the firmware does not
reassemble a fragmented message, so a 6 kB frame sent in six frames
lands as nothing.

## Manual line calibration

    python3 mau5lines.py --host 192.168.10.172

Lights one line at a time and draws, beside it, where the map thinks
those LEDs are. Across / up / depth sweeps, plus one strip or one
chain run at a time. Mark a line good or bad, and correct a span four
ways: **move** it in millimetres, **shift** it when LEDs were cut out
of a run, **reverse** a strip wired backwards, **relabel** a run
filed under the wrong surface.

Corrections go to `data/cal/adjust.json`, which `mau5map.load()`
applies on top of the measured map. Nothing edits `pixel_map.csv`, so
re-running the localisation cannot silently discard them. Verified:
the tool lights exactly the LEDs it claims, corrections reach the
map, and undo restores it byte-exactly.

## Still open from before

The GPIO 18 relay: 622 WS2815s draw ~0.6 A whenever 12 V reaches
them, whatever the data line says. `link_ma` is still 0, waiting on
what replaced the Duponts.

The access point is still `WLED-AP` with an 8-character password,
which is very likely WLED's default. Only the length comes back over
the API so nothing here can tell. At a show that is the password to
the helmet:

    python3 mau5offline.py config --host 192.168.10.172 --ap-ssid mau5head --ap-psk '<pick one>' --apply

