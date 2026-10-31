# Handoff: finishing the Halloween show

Written 2026-10-31 at about 13:15 PDT, when the first person ran out of usage. The shows have to be
ready tonight. Everything below is on branch `halloween-handoff`. `main` is untouched.

## Set up

1. Clone, then `git checkout halloween-handoff`.
2. **Get the MP3s from the owner's Mac, which serves them on the home Wi-Fi:**
   `python3 tools/showkit/get_songs.py http://192.168.10.225:8799`. They land in `shows/`, ignored by
   git. Never commit or host them, because the repo is public. Compiling, previews and tests work from
   the committed analyses; measuring a grid and serving songs need the MP3s.
3. `python3 test_mau5.py`: 131 pass at this commit.

## What is done

- **Play Music:** a big button at the top of the page plays every song on the device, in the order of
  `shows/scenes/playlist.json`, with skip, back and shuffle. It uses one audio element so phones allow
  the next song to start without a tap.
- **Song-stopping fixes:** a covered laptop window no longer stops the helmet (worker clock); a poor
  link can reconnect (the 1.5 s connect limit made that impossible until a reload); a socket gone silent
  is replaced after 6 s; a song copy of the wrong size is fetched again; a pause from a media key or
  headphones now says so instead of freezing silently; a song that fails is skipped.
- **Engine, on both laptop and phone:** per-song sprite sheets (`shows/scenes/<song>.sprites.json`),
  moving and flip-book sprites, `orb`, `twinkle`, regions `jaw rim1 rim2 tubes1 tubes2`.
- **Eyes:** a finger on the preview steers them on the `eyes` preset. The controller has no gyroscope,
  and a plain http page gets no motion data from a phone.
- **Grid fixes** for beneath and Ghosts n Stuff are in. Analysis files for new songs run at 10 Hz so
  all sixteen fit on the controller.

## What is not done: the ten new shows are unreviewed first drafts

All ten compile, pass lint and match between laptop and phone. Each author was cut off while
re-judging against the fixed preview tool, and **no reviewer ever ran**. Nobody has seen most of them
on the helmet (six songs' openings have played there, with earlier drafts of the new ones).

| Song | Concept | Mean W |
|---|---|---|
| FN Pig | neon pig snout, flapping ears, hazard stripes | 12.4 |
| Moar Ghosts n Stuff | Pac-Man after dark, power pellet drops | 14.4 |
| Raise Your Weapon | candlelit ballad, then blade slashes | 12.5 |
| Some Chords | chord organ, stained glass | 11.3 |
| Some Chords (Radio Edit) | tuning an old radio, VU-meter ears | 13.5 |
| Animal Rights | zoo breakout, a different animal per drop | 13.1 |
| The Veldt | savanna sun, then the nursery glitches | 11.6 |
| Strobe (Special Features Remix) | cinema, film leader, sepia to technicolor | 13.4 |
| I Remember | memory, slow afterimages | 15.2 |
| Harder Better Faster Stronger | robot visor, title words scroll | 13.6 |

Target is 11.5 W or less, never above 12.5 W. Back to back, heat fills after about 20 to 40 minutes and
then hits get flattened. **Never raise a power limit;** make scenes darker instead. Most urgent: I
Remember, Moar Ghosts, Harder Better.

For each song, as a reviewer: read `tools/showkit/BRIEF.md` first. Then check the bar line on the first
and last drop (`grid.py check`, `grid.py fold`), the marks against `spectro.py`, the look with `sheet.py`
(it goes through the real power guard, so big hits with loud ears can leave the shell nearly black),
and power with `power.py`. Generators are in `tools/showkit/songs/<short>/`; edit and rerun rather than
hand-patching, and write the scene JSON with `python3 mau5scene.py compile "<song>"`. Some generators
may name old scratch paths or read scratch files that were not copied.

Each builder's commands and results are in `tools/showkit/notes/<short>.md`: grid measurements, song maps,
power runs. The short names are the folders in `tools/showkit/songs/`.

## Other open items, most important first

1. **Test on a real phone:** Play Music past the first song, with sound, on iPhone or Pixel. Reusing one
   wired audio element is only proven in desktop Chrome.
2. **Test on the helmet's own Wi-Fi (4.3.2.1).** So far only against a stand-in in Chrome at that address.
3. **Firmware, needs the owner's OK:** `firmware/` holds a built patch so the access point stops dropping
   phones about every 5 minutes when home Wi-Fi is out of range (read from source, not seen on the
   helmet). A second fix is **not in it yet**: in `wled00/network.cpp`, on AP client disconnect, add
   `&& !Network.isConnected()` to the `forceReconnect` line, because a phone leaving the AP cuts a
   healthy home connection for an estimated 10 to 20 s. Until then, keep phones off `WLED-AP` when
   running over IP.
4. Review findings not yet fixed, all small: `AudioContext` has no statechange handling (use
   `state !== 'running'` in `_ctx`, plus a resume on the next tap, for iOS `interrupted`); warn when
   `currentTime` stops moving; retry when a start fails while a song plays; retry `_relayout` when its POST
   fails; on the binary path use the short `owedQuiet`, since 1 s + 1.5 s equals the 2.5 s realtime
   timeout; `clock.onerror` should reschedule; IndexedDB connection loss (`db.onclose`); a resume button
   after a reload; blur buttons after clicks so a stray space bar cannot stop the song; `comeBack` should
   not start while another device streams.
5. `mau5offline.py deploy` can leave a truncated page if the upload dies, so **only deploy at good signal
   and with nothing streaming**. The helmet's signal was -85 to -91 dBm for a while today on the far access
   point.
6. Branch `claude/eloquent-franklin-40e988` (pushed) has a better tempo and bar-line estimator, not merged:
   one known conflict in `mau5song.analyse`, and re-analysing a shipped song moves its grid.

## Deploying

```bash
python3 mau5drive.py
python3 mau5offline.py deploy --host 192.168.10.172
python3 -u mau5offline.py songs --host 192.168.10.172
```

The last one serves the songs to phones on home Wi-Fi and must keep running. Reload the page on every
device afterwards. Rules: one hardware test at a time, and never send `on:false` from a test while
somebody else is streaming. Storage was 839 of 983 kB at the last deploy; keep about 64 kB free.
