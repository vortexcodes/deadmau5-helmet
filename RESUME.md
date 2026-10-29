# Where things stand (2026-10-28, evening)

Both of the things that were asked for on the day are done and were
checked against the helmet, not against a simulator.

## Offline mode works, and four things about it were wrong

`mau5peek.py` is new and is why. It opens WLED's own live-preview
socket and reports the colour of every LED as the strip is driving
it -- no camera, no dark room, nothing to calibrate. Every claim
below was measured with it.

- **An `i` write blanks the rest of the segment.** Deltas were
  therefore a frame with most of the helmet switched off. Every frame
  now goes whole, in one message.
- **A websocket message over one TCP segment is dropped in silence.**
  1428 bytes lands, 1448 does not. The player's limit was 3000. HTTP
  has no such limit, so the transport is now chosen by frame size:
  15 of 37 presets fit the websocket and run at 60 fps, the rest go
  by POST at about 10.
- **WLED does not echo an `i` write**, so the ack-based pacing had
  two messages permanently outstanding and sat at 4 fps.
- **The brightness limiter was set on the wrong key.** `hw.led.maxpwr`
  is accepted and ignored by 0.15; the per-bus one is enforced and
  reserves a milliamp per LED, so the cap is the budget including
  standby. It does **not** cover the phone -- the estimator does not
  count pixels painted into a frozen segment. What actually holds is
  that the region ceilings sum to 1950 mA against a supply proven to
  2200.

Verified end to end: a frame sent by the page's own JavaScript, read
back off the strip, 622 of 622 LEDs exact on both transports.

    python3 mau5offline.py check --host 192.168.10.172

## Audio from the phone

The page can play a track you pick and drive the presets off it:
loudness with its own auto-gain, log-spaced bands, chroma for pitch,
a spectral centroid, onsets and a tempo, all on a 50 Hz clock of
their own. Three presets show it off -- `spectrum`, `pitchwheel`,
`bloom` -- written in Python and ported, cross-checked like the rest.

**The microphone only works where the page is a secure context.** On
the page the controller serves it is not: plain http means
`navigator.mediaDevices` is absent, not blocked. The page says so and
offers the two ways round it. A track off the phone needs none of
this and is the thing that works at a show.

**The controller has its own microphone.** `/json/info` reports
`Audio Source: PDM digital`, `Sound Processing: running`, AGC 3.14x.
Nobody has checked whether it actually hears the room. If it does,
WLED's own sound-reactive effects work with no phone at all -- worth
ten minutes.

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
