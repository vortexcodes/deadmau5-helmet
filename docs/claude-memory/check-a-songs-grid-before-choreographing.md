---
name: check-a-songs-grid-before-choreographing
description: "The tempo estimate and bar line can be wrong on any song, shipped ones included; fit per half and fold before trusting a grid, and scattered readings do not rule out a tempo error"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6511c3df-78a7-4bba-89a6-b9c3e7df41f4
  modified: 2026-10-31T19:29:02.686Z
---

On TIKI TIKI (2026-10-30), `mau5show build` said 137.871 BPM where the track is
137.98, which is over a 16th out by bar 116. The bar line was also half a bar from
where the phrases turn, and the track has a splice where the music comes back
197 ms late. None of this shows in `mau5scene.py bars`. The same day an audit found
the same errors on shows already shipped: [[shipped-grid-audit-2026-10-30]].

**Why:** a show written against the estimate looks right at the start and slips
later, and the drops land late. Nothing warns about it: `lock` below `LOCK_MIN` is
not read when scenes compile, and integer marks look fine on a wrong grid.

**How to apply:**
- Measure the phase of the onsets per 8 bars (flat within about 10 ms) and fold them
  into 16 steps per section. Fix with `shows/scenes/<song>.beats`, then write marks.
- Scatter that is not monotonic is not evidence against drift. This note used to say
  the reverse, and beneath's 0.33% error looked exactly like "off-beat content": a
  tempo error wraps on 8ths and 16ths. Test it by fitting a line from strong onsets
  per half with no seed from the grid, then seeing whether the readings collapse on it.
- Score tempo at the 16th (a comb at 4x the beat). At the beat, off-beats cancel the
  true tempo, and two strong bursts t seconds apart make a false peak 60/t BPM away.
- A busy sub fills the low band with 70-90 ms tremolo onsets, so the whole-song kick
  fit is noise. Fit the kick only in the sections where it is clear.
- Check the bar line apart from the phase: does a drop's first kick land on step 0?
  `downbeat_phase` takes the beat with most flux, which is the snare in half-time music.
- Moving the bar line does not keep marks right at the same number. A mark written
  against the old bar holding the event can need the next number up, so read each one
  against the audio. A windowed change score misses a big kick after a pickup bar, so
  compare onset strength there too.
- A `.beats` grid leaves the lock confidence NaN, so `show.lock` goes false and the
  cue-list fallback stops beat-locking. Scenes do not read `lock`.
- A section can have its own pulse, so scan wide per window. `.beats` can slow a grid
  (each beat over 5 ms late becomes a hold, 15 ms each is invisible) but not speed it up.
- In a worktree `mau5offline._song_files(None)` finds nothing: the MP3s live in the
  main checkout. Do not call `mau5song.decode` or `mau5show.Music` there to measure,
  because they write caches; run ffmpeg to stdout and load the `.analysis.npz` directly.
- A fix that has to land in the main checkout hits a guard from a worktree session, so
  say so when proposing it: [[worktree-guard-blocks-main-checkout-edits]].
