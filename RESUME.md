# Where things stand (2026-10-29, 02:00)

## The shows follow the music now

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

## The ears are wrong by three LED pitches, and now it is measured

Independent of any triangulation, and the cleanest number yet. Solve
each camera against the shell, project the map's own positions, and
compare with where that camera actually saw each LED. One LED pitch
is 16.7 mm:

| | shell | ear1 | ear2 |
|---|---|---|---|
| pose 1 (the view the ears were fitted from) | 0.5 mm | 13.2 mm | 10.4 mm |
| pose 2 (had no part in making the map) | **4.7 mm** | **47.4 mm** | **59.5 mm** |

Pose 1 cannot fail on the ears, because they were derived from it,
and it is still off by most of a pitch. Pose 2 never saw the map
being made: the shell comes back to a third of a pitch and the ears
to **three pitches**. That is the "ears are funky" complaint, with a
number on it.

It agrees with the triangulation, which independently put the ears
50-60 mm from where the map has them. Two methods, same magnitude.
The *direction* is still not measurable -- see below.

`python3 mau5stereo.py --pose2 data/cal/led_positions_pose4.csv`
prints this table every time now.

## The camera angle I need next: from the side

Two poses now exist -- the old low one and last night's high, close
one -- and `mau5stereo.py` triangulates every LED seen from both,
with no model of the ear anywhere in it. It works: the shell, whose
positions are CAD-exact, comes back to **4.8 mm median** against a
16.7 mm LED pitch.

It still cannot measure the ear tilt, and the tool now says so
itself. Solving both cameras twice -- once from the even shell LEDs,
once from the odd -- and triangulating with each gives:

    ear1 tilt: +30.4 from one half, -35.5 from the other  -> DISAGREE by 66 deg
    ear2 tilt: -23.3 from one half, +19.7 from the other  -> DISAGREE by 43 deg

That is not a measurement. The reason is geometric and no amount of
care fixes it: **both poses look at the helmet from the front.**
Triangulating depth needs a baseline across the line of sight, and
two front-on views have almost none, so depth -- and therefore the
tilt of a disc, which is depth against x -- is unconstrained.

**So: one pose from the side.** Forty-five degrees or more off the
face, either side, roughly helmet height, with both ears still in
frame. That single photograph set is what turns `DISC_TILT_DEG` from
a guess into a number. Nothing else is blocked on it.

What *is* established, and did not need the tilt:

- Both ears are flat. Plane rms came out 5-10 mm on every variant
  tried, which is well under an LED pitch.
- The map's flat `y = 30.0` for every ear LED is wrong. Measured
  depth spans tens of millimetres however the cameras are solved.
- The two ears tilt in **opposite** directions, so a single global
  `DISC_TILT_DEG` cannot be right whatever its value.

Nothing has been written into the map. `data/cal/ears_stereo.csv`
has the triangulated positions for inspection.

### Two traps in here, both of which caught me

`mau5locate` aborted twice saying the camera had drifted 200+ px. It
had not. The fiducial was a single LED and its centroid occasionally
landed on something else. Three fiducials and a similarity fit
(`--track`) ran all 622 LEDs with 1 px of correction.

Dropping the worst-fitting quarter of the calibration points,
twice, walks the survivors onto a patch -- and a **coplanar** point
set fits a 3x4 DLT *exactly*. Residual 0.000 px on 224 points, a
beautiful-looking camera, and a shell check that reproduced the
shell to 1.9 mm while proving nothing, because it was the same plane
answering itself. There is now a spread guard that refuses to go
there.

## The ear "line" is four lines, and they are the tubes

Photographed at low level in a dark room: lighting the right ear
alone shows four bright diagonal stripes with dark bands between
them. That is the LED tubes showing through the diffuser, not a
mapping fault -- every LED on the ear is lit in that photograph, so
the pattern is purely where they physically are. Software cannot
even it out; more distance between tube and diffuser, or a second
diffuser layer, would.

Worth knowing: the app icon, which is drawn from the LED map, renders
the ears as radiating spokes. The photograph shows parallel stripes.
Those disagree, and the stereo work above is what will settle it --
from the side.

## Reading the strip back: one warning

`mau5peek` is only as good as the quiet around it. A browser tab left
open on the player streams frames continuously and will overwrite
anything a script writes between the write and the look. That cost an
hour and produced two confident, wrong conclusions about the wire
protocol, both of which evaporated when the tab was closed. Before
believing a reading, check `ws` in `/json/info` -- it is the number of
WebSocket clients, and it should be 1 (yours).

## Shows run offline now

The five cue lists are on the controller (27 kB). The analyses are not
-- two megabytes against nine hundred kilobytes free -- and turn out
not to be needed: they existed to say where the beats and bands were,
and the phone measures that from whatever it can hear.

So: pick a show, start the track on whatever is playing it, tap
**start** on the first beat. The cue list drives which effect is on
screen; the room drives the brightness, the pulse and the overlays.
The ported player matches `mau5show.Player` to **0.0005 counts out of
255** across all five shows.

What is lost is the clock -- nothing on the phone knows where in the
track you are, so it is started by hand, which is how a lighting desk
works anyway. If it drifts, tap stop and start again on a downbeat.

## The track plays, and you can turn it up

A show with no sound was half a show. The page now plays the track
itself: tap **play the track** in the show panel, pick the mp3 off the
phone, and the audio element becomes the clock, the volume control and
the scrub bar at once. Picking a file called "deadmau5 - Strobe.mp3"
selects the Strobe show by itself.

The clock is read from the audio element rather than from a wall clock
started by hand, so it cannot drift from what the room hears, and
pause and seek work for nothing. Verified: pause holds the show at
0:02 across three seconds, resume advances it, volume takes.

The five tracks have to be *on the phone* -- 61 MB of mp3 will not fit
on a controller with 900 kB. Copy them across once.

## Audio from another app

There is no way for a web page to tap another app's audio on a phone.
No browser offers one, on Android or iOS. What works is the
**microphone hearing the speaker** -- which does follow Spotify, and
is what the page offers.

The microphone needs a secure origin and the controller cannot be
one. Two ways round it, both now in the page's own text:

- **Android Chrome:** put `http://192.168.10.172` (and the AP address)
  into `chrome://flags/#unsafely-treat-insecure-origin-as-secure`,
  restart Chrome. Then the microphone works on the offline page.
- **With the laptop there:** `python3 mau5offline.py serve --host
  192.168.10.172 --tls` serves the same page over https and forwards
  the pixels. Verified working and reaching the helmet.

On a desktop there is also **what's playing**, which uses
`getDisplayMedia` to follow a shared tab. Phones do not offer it.

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

## Not done -- the camera never came back up

The camera page stopped pushing at about 08:00 and was still stale at
17:30, so none of the camera work happened:

- the second pose (the new high, close one) to validate the shell
  correction non-circularly and measure `DISC_TILT_DEG`
- re-running `mau5baralign.py`
- the ears

To restart it: open `http://192.168.10.225:8752/` on whichever device
the camera is and tap START CAMERA. Then `curl -s
http://127.0.0.1:8752/api/status` should show an age of a second or
two rather than hours.

**One camera question is now sharper than it was.** The brightness
limiter does not clamp pixels painted into a frozen segment -- that
rests on `/json/info` reporting a flat idle 120 mA while the page
paints a full rainbow, which is strong but indirect. Photographing
the same frame at a bus cap of 1622 and of 400 settles it in one
shot.

## Still open from before

The GPIO 18 relay: 622 WS2815s draw ~0.6 A whenever 12 V reaches
them, whatever the data line says. `link_ma` is still 0, waiting on
what replaced the Duponts.

The access point is still `WLED-AP` with an 8-character password,
which is very likely WLED's default. Only the length comes back over
the API so nothing here can tell. At a show that is the password to
the helmet:

    python3 mau5offline.py config --host 192.168.10.172 --ap-ssid mau5head --ap-psk '<pick one>' --apply
