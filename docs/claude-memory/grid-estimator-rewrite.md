---
name: grid-estimator-rewrite
description: "estimate_tempo and downbeat_phase were rewritten on 2026-10-30; check whether it landed, because re-analysing a shipped song now moves its grid"
metadata:
  node_type: memory
  type: project
  originSessionId: 676de54f-49c6-4ea1-aa76-7dda3317ac1d
  modified: 2026-10-31T19:27:48.970Z
---

On 2026-10-30 `mau5song.estimate_tempo` became a comb at the beat, 8th, triplet and
16th plus the kick band, and `downbeat_phase` became kick weight plus where the music
turns. `mau5scene.py compile` warns on low `lock` and low `bar_lock`. Committed on
2026-10-31 as `f485ffd` on `claude/eloquent-franklin-40e988`, not merged or pushed.
Check `git log -- mau5song.py` before assuming it is in main: see
[[check-a-songs-grid-before-choreographing]], whose notes on the old estimator stop
applying once it is.

**Why:** the estimator getting better is what makes old analyses dangerous. Shipped
marks were written against the old grids, and Dimension and leavemealone's `.25` marks
compensate for bars a beat off ([[shipped-grid-audit-2026-10-30]]).

**How to apply:**
- Never bump `CACHE_V` or delete a shipped `.analysis.npz` to pick up the new estimator.
  Re-analysing moves the bar line, so fix a shipped grid with `.beats` and its marks.
- A song on a `.beats` grid is safe to rebuild: beneath, Ghosts and TIKI TIKI came back
  byte-identical through the merged code on a snapshot of main, 2026-10-31. Dimension
  and leavemealone are the ones it would break.
- `lock` means two things: shipped analyses hold the comb at the beat alone, new ones
  the strongest harmonic scaled down when another tempo comes level. `LOCK_MIN` 0.18
  separates both, but the numbers are not comparable across them.
- `bar_lock` is only on new analyses, so compile cannot doubt a shipped bar line.
- `bar_lock` is a weak signal: over 750 excerpts 3 percent of bar lines over 0.25 were
  still wrong, mostly half-bar slips in sections with no kick.
