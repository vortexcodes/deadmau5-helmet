# mau5head

Software for my deadmau5 helmet: 622 WS2815 LEDs on one chain into a
WLED controller -- 398 in the slots of a printed PETG shell and 224 in
the two ears -- driven from a phone with no laptop and no network.

The write-up, with a film of how the LEDs were located, is on
[vortex1.dev](https://vortex1.dev/project.html?p=mau5head-v2), and the
whole effect engine runs in a browser in the
[simulator](https://vortex1.dev/mau5-simulator.html).

## Five minutes, no helmet needed

```bash
python3 -m pip install numpy pillow matplotlib
python3 test_mau5.py                    # 41 checks, all offline
python3 mau5web.py --serve              # the simulator, on this machine
python3 mau5offline.py serve            # the phone player, against a fake helmet
python3 mau5doctor.py --offline         # what is set up and what is not
```

Python 3.9 or later.  `ffmpeg` is only needed for the films.

## What is where

```
the map
  mau5slots.py      builds data/cal/pixel_map.csv: every LED in a CAD slot or
                    ear tube, with two camera views deciding which
  mau5map.py        reads the map, applies hand corrections from adjust.json
  mau5locate.py     measures one camera view: each LED lit alone, centroid
  mau5walk.py       walks the chain by hand from a phone
  mau5lines.py      checks the map by eye, line by line, and records fixes
  mau5hue.py        finds LEDs wired in a different colour order
  mau5film.py       the localisation film; mau5lapse.py, the timelapses

effects and shows
  mau5engine.py     37 presets written against geometry, not a grid
  mau5song.py       analyses a track; mau5show.py builds and plays a show
  mau5tune.py       scores how well a show follows its music

output and power
  mau5wled.py       the controller: JSON API, DDP, colour-order correction
  mau5power.py      the guard: per-region ceilings, budgets, thermal bucket
  mau5ctl.py        a controller page served from the laptop
  mau5peek.py       reads back what the strip is actually showing
  mau5fake.py       a controller that is not there, for tests

the phone
  mau5offline.py    builds the player that lives on the controller
  remote/offline/   that player: the engine, guard and show player in JS
  mau5spotify.py    lets the player follow Spotify

from somewhere else
  mau5relay.py      one token-guarded door to the helmet and the camera
  mau5eye.py        a camera page any device can be

the website
  mau5web.py        builds the simulator for vortex1.dev from remote/web/
```

The first version of this suite targeted a different helmet -- 1406
LEDs, two chains and a Raspberry Pi running Falcon Player. Those tools
still run and are described in
[docs/original-design.md](docs/original-design.md); nothing on the
current path uses them.

## How the map is built

The print has a slot for every shell LED, 948 of them, and three tubes
and a rim in each ear. `mau5slots.py` keeps every position from the
CAD and uses two camera views only to decide which slot each LED is
in: the chain is aligned to the CAD's wiring order by dynamic
programming, skipping empty slots, never using one twice, trusting a
camera less the more edge-on it sees an LED. From the CAD alone it
converges to 398 shell LEDs in 398 distinct slots with one empty, and
each camera on its own reaches the same answer.

```bash
python3 mau5locate.py --from 0 --to 622                     # one view
python3 mau5locate.py --from 0 --to 622 --out data/cal/led_positions_pose4.csv
python3 mau5slots.py                                         # the map
```

The ears stay where the CAD puts them; the cameras say where along
which tube each LED sits. Corrections somebody makes by eye go in
`data/cal/adjust.json` and survive a rebuild.

# The helmet as built

The hardware changed: LEDs on the front half only, along the ear rims and
inside the ears, nothing on the back; all of it on **one chain**; ear rims are
a thinner pre-diffused strip wired in a different colour order. The wiring
diagram is no longer the truth and most of the strip is now covered, so the
map is **measured with a camera** instead of described.

```
mau5wled.py   the controller, directly: JSON API + DDP out with per-LED
              colour-order correction
mau5walk.py   walk the chain from your phone, one LED at a time, and record
              the sections as you go  (+ remote/walk.html)
mau5locate.py one camera view, one LED at a time
mau5slots.py  the map: CAD slots, chosen by two camera views
mau5cal.py    the first camera tool (probe / live / order / scan / solve),
              kept for its colour-order and latency probes
data/cal/     the walk session, what the cameras saw, the map
data/cad/     948 LEDs read out of mau5head_PRINT_ASSEMBLYfinal.step
```

## Why orange went green on the ears

A colour-order mismatch, and the arithmetic matches the symptom exactly. WLED
reorders each pixel to its bus setting on the way out. With the bus set to GRB
and orange `(255, 110, 0)` requested, it emits bytes `[110, 255, 0]`. A strip
actually wired RGB reads that as `R=110, G=255, B=0` — yellow-green.

One bus setting cannot be right for two differently-wired strips on one chain,
so the correction happens in software: `Pixels` applies a per-LED channel
permutation before transmitting, and one DDP stream drives mixed strips
correctly. `mau5hue.py` finds which LEDs need it by asking each one for red
and then for green and comparing how much red comes back -- a single red
photograph is not enough, because the camera's white balance drifts between
shots by more than the effect. The answer lives in `data/cal/strips.json`:
LEDs 492-529, both ear rims.

## Calibrating: walking the chain by hand

Getting a camera to see every LED at once is awkward, and lighting the whole
helmet to find out where things are will cook it. So the primary method is a
phone app that walks the chain one LED at a time.

```bash
python3 mau5walk.py --host <wled-ip>
```

It prints an address; open that on the phone. Both devices just have to be on
the controller's network.

Light one LED, look at it, tap NEXT. When the light jumps somewhere physically
different, you have found a boundary -- tap **IT JUMPED — NEW SECTION**, name
it, carry on. Press and hold NEXT to run. Tap any finished section in the list
to light it on its own for a photo. The session is written to
`data/cal/walk_session.json` as you go, so there is nothing to transcribe.

**Heat is a hard limit, enforced in the server where the page cannot get past
it.** All 948 at full white is roughly 18 A; the default cap is 120 LEDs lit
and brightness 128/255, about 14 W. Ask for brightness 255 and you get 128;
ask for a 268-LED section and you get the most recent 120, with the cap shown
on screen. It also blanks itself after ten minutes of no input. Both limits
move with `--max-lit` and `--max-bri` if you are standing over it.

Why a server and not a page talking straight to the controller: per-LED
control means DDP and a browser cannot send UDP; WLED reverts to its own
effect about 2.5 s after a stream stops, so something has to hold the frame;
and the power cap belongs somewhere a UI bug cannot reach.

A true WLED plugin would be a usermod, which means rebuilding and reflashing
firmware. This gets the same result with no reflash.

## Calibrating: the camera

Two runs of `mau5locate.py` from two camera positions, then
`mau5slots.py`. Each run lights every LED alone at a low level, so the
glow stays small, and records the centroid of what changed against a
dark frame; three reference LEDs are re-measured as it goes and a
similarity fit takes out any nudge to the camera. About three seconds
an LED, and it resumes if interrupted.

The two positions want a real angle between them. The pair in
`data/cal` are about 34 degrees apart, front and high-right, which is
enough to triangulate the shell to a third of a millimetre of the CAD
sphere -- the check that says the cameras can be trusted before
anything is built on them.

`mau5cal.py` was the first attempt at this. It placed LEDs straight
from one view, which is the approach that turned out to be wrong; its
colour-order and camera-latency probes are still useful.

## Running shows off the phone

The phone is the player. It opens a page the controller serves from
its own filesystem, and that page runs the engine, the power guard
and the show player itself -- see "Offline mode" below. Starting a
show plays its song out of the phone; the first time, the page asks
for the file and keeps it.

## Reading the strip back

Everything else that drives the helmet is open loop: a frame goes out
and whether it arrived is a matter of belief, or of pointing a camera
at it and hoping the room is dark. WLED will simply tell you. Its web
UI has a live preview fed by a WebSocket, and `mau5peek.py` asks the
same question from a script:

```bash
python3 mau5peek.py --host 192.168.10.172 --watch 10
```

It returns the colour of every LED as the strip is driving it. No
camera, no dark room, nothing to calibrate. Four separate things
about offline mode turned out to be wrong the first time it ran on
real hardware, and none of them could have been found any other way:
each one failed by sending successfully and changing nothing.

## Checking the map by eye, line by line

The map knows what the CAD knows and what two cameras could see.
Neither knows about a part assembled differently from the drawing --
an ear bolted on a few degrees off, a strip moved to clear a magnet --
and that is invisible to a solver and obvious to somebody standing in
front of the helmet.

```bash
python3 mau5lines.py --host 192.168.10.172
```

Open the printed address on a phone. It lights one line at a time --
a vertical band across the face by default, or horizontal, or by
depth, or one strip or one chain run -- and draws, next to it, where
the map thinks those LEDs are. Two pictures of the same claim, one on
the helmet and one in your hand. Where they disagree, the
disagreement is the finding.

Four corrections, which between them cover everything that has
actually been wrong here:

| | what it means |
|---|---|
| move | the span sits somewhere else: nudge it in millimetres |
| shift | LEDs were cut out of this run, so everything after the cut is a pitch or more further along than the map believes |
| reverse | the strip is wired the other way round |
| region | this run is not on the surface it was filed under |

They are written to `data/cal/adjust.json`, which `mau5map.load()`
applies on top of the measured map. Nothing edits `pixel_map.csv`:
re-running the localisation must not quietly discard what somebody
saw, and what was measured should stay told apart from what was
judged by eye. Undo removes the last correction and puts the map back
exactly.

## Working on it from somewhere else

The helmet, the camera and whatever is driving them all live on one
home network, and the person working on it usually does not. That is
the main reason a change used to take a day to try.

`mau5relay.py` runs on a machine at home that can see all three, and
puts one door in front of them:

```bash
python3 -c "import secrets;print(secrets.token_urlsafe(24))"   # a key
python3 mau5relay.py --token <that> --host 192.168.10.172
```

| route | what it is |
|---|---|
| `/` | a dashboard: the live camera, helmet status, a link to the player |
| `/cam.jpg` | the newest camera frame |
| `/status` | camera age, frame count, helmet name, power, on/off |
| `/helmet/json/...` | the controller's own API, proxied |
| `/app/mau5.htm` | the player, served from here and pointed at `/helmet` |

Every route needs `?t=<token>` or an `X-Mau5-Token` header, and it
refuses to start without a token unless you insist: it proxies a
controller that has no authentication of its own, so the token is the
only thing in the way.

### Getting to it from outside the house

**Tailscale cannot work from the school network, and it is blocked
twice over.** Measured both ways on the same machine:

| | `tailscale.com` | `controlplane` |
|---|---|---|
| Cloudflare WARP off | reset | reset |
| Cloudflare WARP on | 200 | 302 |

With WARP off, every `*.tailscale.com` host completes the TCP
handshake and is reset the moment the TLS ClientHello names it —
DERP relays included — while github.com and example.com are fine.
SNI filtering of the whole domain, and `controlplane` is the
coordination server, so there is nothing to configure around it.

With WARP on the hosts come back, and Tailscale still does not work:
both are whole-device VPNs and macOS will not give them the same
machine. The symptom is specific and worth recognising — the client
reports `BackendState: Running`, `InNetworkMap: true`, a valid key
and `Online: false`, with `InMagicSock: false`, `InEngine: false` and
"unable to connect to the coordination server". The login is fine;
the data plane never comes up.

Tailscale works normally from a phone hotspot, if it is ever wanted.

Cloudflare is open from the same network, so that is the route:

```bash
brew install cloudflared                      # on the machine at home
python3 mau5relay.py --token <...> --host 192.168.10.172 --tunnel
```

It prints a `https://<words>.trycloudflare.com` URL and leaves a copy
in `data/cal/relay_url.txt`. The certificate is real, which also
means the player installs as a proper app from that address — the one
thing the controller could never offer.

Two things to know about a quick tunnel. The hostname is **random and
changes every restart**, so it is not an address to memorise; a named
tunnel on a domain you own is, and wants a Cloudflare account. And
the URL is **public the moment it exists** — the relay's token is the
only thing in front of a controller with no authentication of its
own, so make it long, and treat the URL as a secret.

Verified end to end from the school network: 403 with no token, 403
with a wrong one, 200 with the right one, certificate verified
without `-k`.

## Keeping it as an app, and what happens when you close it

The page carries a manifest and icons drawn from the LED map itself,
so "Add to Home screen" gives a real icon and a window with no
address bar rather than a bookmark.

It is not a full PWA and cannot be while the controller serves it: an
installable app needs a service worker, a service worker needs a
secure origin, and WLED speaks plain http. The page does not need one
— it is already wholly on the controller — but the install banner
will not appear, and you add it from the browser menu instead.

**Closing the page used to stop the lights**, which read as a fault
and was in fact the safety design: a frozen segment holds its last
frame for ever, so the player arms a dead man and the helmet goes
dark a minute after the phone stops talking.

Now it hands back instead:

```bash
python3 mau5offline.py standby --host X --fx pacifica --bri 96 --apply
```

That saves a WLED preset and makes it the boot preset. Let go of the
page — close it, lock the phone, walk off — and the controller picks
up one of its own effects and keeps running with no phone, no laptop
and no network. Plug the helmet in with nothing else around and it
comes up in the same thing. The brightness limiter *does* cover that
path; it is blind only to pixels painted into a frozen segment, which
is the player's route, not this one. The page has a **keep glowing**
switch if you want the old behaviour back.

## Offline mode: the helmet with no network and no laptop

At a show there is no house WiFi worth trusting and no reason to be carrying
the laptop. The helmet brings up its own access point, the phone joins it,
opens one page, and all 37 animations run with nothing else involved.

```bash
python3 mau5offline.py build              # make the page, no hardware needed
python3 mau5offline.py serve              # drive it against a fake controller
python3 mau5offline.py config --host X --ap-psk '…' --apply
python3 mau5offline.py deploy --host X    # upload it, then read it back
python3 mau5offline.py check  --host X    # is it actually ready
```

Then: join **mau5head-AP**, open **http://4.3.2.1/mau5.htm**.

### Why the page lives on the controller

Every other place it could live is ruled out, which is worth writing down
because each of them looks reasonable until you try it.

* A browser cannot open a UDP socket, so DDP is not available to a phone and
  the pixels have to go over the controller's own HTTP API.
* An `https://` page cannot make requests to a plain-`http` 192.168 address.
  That rules out hosting it anywhere with a certificate — GitHub Pages
  included, and with it the whole installable-PWA idea.
* A plain-`http` page is not a secure context, so no service worker will
  cache it. The laptop cannot serve it either, because then the laptop has to
  be there.

Exactly one HTTP server is on that network with nothing else to do, so the
player is uploaded to WLED's own filesystem: 76 kB gzipped, same origin as the
API it drives, nothing to install on the phone, and it works from anybody's
phone for as long as the helmet boots.

### What runs where

```
phone                                   controller
  mau5engine, ported to JS      ──┐
  the power guard, ported         ├──  WLED, segment frozen
  the colour-order correction   ──┘    automatic brightness limiter
  a preview of what it is sending      nothing else
```

The presets and the guard are **ports, not reimplementations**: the same
parameter names, the same order, the same arithmetic. `test_mau5.py offline`
renders every preset in both languages at seven times and compares — worst
disagreement 0.0002 of a count out of 255 — and drives both power guards with
the same frames and the same clock, where the currents come out identical.

The geometry is not ported at all. `Helmet`'s derived arrays are exported from
Python and read back as typed arrays, so the port cannot disagree about where
an LED is, only about what colour to paint it, which is the part that is
tested.

### The wire, as measured

WLED's individual-LED syntax, `{"seg":{"i":[…]}}`, with runs of one colour
collapsed to a range. **One message per frame, always the whole helmet.**

That shape is forced, and it was arrived at the hard way: the first version
sent deltas, split frames across messages and paced itself on
acknowledgements, and every one of those was wrong about this firmware
without once failing visibly. `mau5peek.py` is what found it, by reading the
strip back instead of trusting the send. On WLED 0.15.4:

* **An `i` write blanks the rest of the segment.** Write LEDs 0–99 and then
  100–199 and only the second hundred is lit. A delta is therefore not an
  optimisation, it is a frame with the rest of the helmet switched off.
* **A WebSocket message that does not fit one TCP segment is dropped in
  silence.** 1428 bytes lands, 1448 does not, and the MSS is 1436. The send
  succeeds and the pixels never change.
* **An HTTP POST has no such limit.** A whole 622-LED frame goes in one 6.2 kB
  request and arrives exactly — at the cost of a round trip.
* **WLED does not echo an `i` write.** 665 pixel messages drew about six bytes
  each back, so a credit window built on those replies stalls at two
  outstanding messages and pins the player at 4 fps.

So the transport is chosen by how big the frame came out. Fifteen of the 37
presets encode under 1400 bytes and go by WebSocket, where frames apply
correctly at **60 fps**; the rest go by POST at about **10**. Quantising
colour to force more of them under the limit was measured too — it buys four
presets for a visible cost, and was not taken.

Because every frame is whole, a dropped message costs one frame and the next
one is right again. There is no resync, and no belief about the controller's
state left to go stale.

Sending `i` puts the segment in WLED's freeze state, which is what stops the
running effect painting over the frames — and means **the last frame stays
lit forever** if the phone goes away. Hence the dead man below.

### Power, with the laptop gone

On the house network the guard in `Pixels.send` is the only clamp, and that is
fine because every frame goes through it. Offline the frames come from a
browser tab, so there are three:

1. **The same guard, in JavaScript**, reading the same `data/cal/power.json`:
   regions, ceilings, shed weights, floors and the thermal bucket. Watch
   `heat` climb on the page and the current ration itself down from 1622 mA to
   about 1040 mA after a couple of minutes of something bright — that is the
   bucket filling, exactly as it does on the laptop.
2. **WLED's own brightness limiter**, set by `mau5offline.py config` to
   `budget + standby` mA at 19 mA per LED — on the *bus*, which is the one
   0.15 enforces; the global `hw.led.maxpwr` is accepted and ignored.

   It does **not** cover the phone. WLED's current estimator does not count
   pixels painted into a frozen segment — `/json/info` reports a flat idle
   120 mA while the page paints a full rainbow — so the limiter it drives
   does not clamp them either. It still covers everything the controller
   renders itself, which is what a stray tap in WLED's own UI produces.

   What actually holds the phone is the guard above it, and this: the region
   ceilings sum to 1950 mA of LED current, against a supply the ramp test
   took to 2200 mA with no fault. Even a pathological frame cannot ask for
   more than the wiring has already been shown to give.
3. **A dead man's handle.** The segment latches, so the player re-arms WLED's
   nightlight — instant mode, one minute — every twenty seconds. If the phone
   is dropped, locked or out of battery the helmet goes dark about a minute
   later. The page also blanks the helmet on stop and on `pagehide`, which
   covers everything except the phone dying outright.

### Testing it without a helmet

`mau5fake.py` answers like the controller does and is deliberately strict
where the firmware is strict: it refuses individual LED writes unless the
segment is frozen, **blanks the segment on every `i` write**, **drops a
WebSocket message that would not fit one TCP segment**, and stays quiet on
pixel writes the way WLED does. The first three of those were added after
the real controller disagreed with it — the fake modelled none of them, and
that is precisely why a player that showed a fifth of each frame passed
every test. `--lag`, `--max-json`, `--no-ws`, `--no-ws-echo` and
`--no-freeze` make the remaining failures happen on purpose.

```bash
python3 mau5fake.py --lag 35 --max-json 3072   # a slow controller
python3 mau5fake.py --no-freeze                # a build older than 0.13
python3 mau5fake.py --host 192.168.10.172      # the real one, via the laptop
```

`/fake/view` draws the pixel buffer it was sent, which is the closest thing to
looking at the helmet.

### Audio from the phone

The page can listen and drive the presets from what it hears.

Pick a track with **play a track** and the phone plays it out loud and taps it
on the way past, so the helmet reacts to exactly what the room hears with no
latency to guess at. **listen** does the same from the microphone, where the
browser allows one.

What it measures, on a 50 Hz clock of its own so the numbers stay right when
the link drags the render rate down: loudness with an auto-gain that tracks
its own loud and quiet ends, log-spaced bands each normalised against its own
history, a chroma circular mean for pitch, a spectral centroid, onsets by
spectral flux and a tempo from the gaps between them.

Two FFT windows, because the two questions want opposite things. Onsets want
a short one; pitch wants a long one. At 44.1 kHz a 2048-point FFT has 21.5 Hz
bins and a semitone at middle C is 15 Hz — measured, a 262 Hz tone spread
across five pitch classes and read two semitones flat. 8192 points resolves a
semitone down to about 90 Hz, at a window harmony does not move inside.

Three presets are built to show it, and the older reactive ones (`eq`, `vu`,
`beatpulse`, `heartbeat`) pick it up for free:

| | |
|---|---|
| `spectrum` | bars across the face from the bands, hue from the pitch, and a peak cap that falls — the cap is what makes it readable, because a held peak is a *moving* edge and movement survives the diffusion where a gradient does not |
| `pitchwheel` | the ears as a pitch wheel, one turn per octave, with the shell on the same hue |
| `bloom` | rings running outward on the beat, hue from pitch pushed round as the spectrum brightens |

### What offline mode does not do

**Shows.** The animations are all there; the five music shows are not. A show
needs the track playing on the phone as the clock and its analysis — band
energies at 40 Hz — as the drive, which is 250 to 670 kB a song before any
quantising. The cue lists themselves are 13 kB and would go straight over.
Nothing about the design prevents it; it is the next piece, not a limitation.

**Anything with no phone at all.** Join the AP without opening the page and
you get WLED's own effects, which still work and are a reasonable fallback.
This controller also reports a PDM microphone of its own with sound
processing running, so WLED's sound-reactive effects may work with no phone
in the loop at all — nobody has checked whether it actually hears the room.

**Live microphone on the page the controller serves.** `getUserMedia` needs a
secure context and plain http is not one, so `navigator.mediaDevices` is
absent rather than blocked. A track picked off the phone needs none of that
and is the thing that works at a show; the page explains the two ways round
it for the microphone.

### The thing most likely to go wrong at a show

Android does not like a WiFi network with no internet on it, and will quietly
keep mobile data as the default route or offer to switch away from the AP
altogether. Requests to `4.3.2.1` normally still go over WiFi because that
subnet is directly connected, but if the page will not load, that is the first
thing to check: tell Android to stay connected, and turn off "switch to mobile
data automatically".
