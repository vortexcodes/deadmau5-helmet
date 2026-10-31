---
name: shipped-grid-audit-2026-10-30
description: "What each shipped show's grid measured against its audio on 2026-10-30, and the fixes applied to beneath and Ghosts on 2026-10-31; uncommitted, so check for a .beats file before assuming one is still there"
metadata:
  node_type: memory
  type: project
  originSessionId: 6511c3df-78a7-4bba-89a6-b9c3e7df41f4
  modified: 2026-10-31T19:27:05.253Z
---

Measured from the audio on 2026-10-30. The beneath and Ghosts fixes went into the main
checkout's working tree on 2026-10-31, uncommitted and not deployed, so look for
`shows/scenes/<song>.beats` to see whether they are still there. See
[[check-a-songs-grid-before-choreographing]] for the method.

- **beneath (with raxaj):** shipped 126.417, really 126.000, and the outro is 122.000
  from 255.1 s (bar 133.25). The kick sat on the off-beat in both drops, ERUPT fired
  251 ms late, WHITE 214 ms early. The user approved the fix and it was applied on
  2026-10-31, uncommitted and not deployed: 573-beat `.beats` from 1.275 s, 126 to beat
  533 at 255.085 s then 122; `pickup` 48.75 to 48.875 and that hit's `beats` to 0.5;
  every other mark kept its number. Measured after: the kick reads +21 to +22 ms in all
  eight 2-bar blocks of the drops, ERUPT and WHITE fire 22 ms ahead of it with the clap
  and mids within 2 ms, and the outro's low notes read +22 ms on 37 beats. A +22 ms
  kick is the band's slow attack, so don't chase it.
- **deadmau5 - Strobe:** right. 128.000 from the first kick at bar 125 (236.13 s),
  shipped 128.003, about 15 ms of creep over the song. Left alone. Its intro is not on
  this grid: 176.000 BPM to about 120 s, then no pulse to 236 s. A 128 grid cannot
  follow it, because holds cannot speed a grid up.
- **Ghosts n Stuff:** tempo and phase fine, bar line half a bar off (`downbeat_phase`
  took the snare). True first downbeat 0.129 s, shipped 0.986 s, so big marks fired
  about 860 ms late. Keeping every number would have been wrong: seven marks were
  written against the old bar holding the event. The user approved the fix and it was
  applied on 2026-10-31 to the main checkout's working tree, uncommitted and not
  deployed: `.beats` 970 beats from 0.128932 s at 140, `kick` 7.5, `void` 48, `rise`
  60, `drop2` 64, `stabs` 136, `build3` 150, `suck3` 158, `suck3` out 2; the other 17
  kept their numbers. Measured after: in the drops the kick is on step 0 (100 against
  22 on step 8) and the snare on step 8 (100 against 57 on step 0).
- **Strobe (Dimension) and leavemealone:** bars a beat off, but their marks sit at
  `.25` and land, so moving the downbeat would break them. leavemealone is about
  174.006 against 174.022, which is the 18 ms the user saw.

**Why:** these are the numbers a future grid or choreography change should start from,
and none of them can be read off the repo.

**How to apply:** re-measure before relying on any figure here if the song file or its
analysis has changed. Nothing here has been seen on the helmet or checked by ear.
