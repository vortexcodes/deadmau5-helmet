# Working on the helmet

Start with `HANDOFF.md`, then `tools/showkit/BRIEF.md` for making a show. What the earlier sessions learned:
`docs/claude-memory/`, `docs/why-songs-stop-review.md`, and per song `tools/showkit/notes/<song>.md` with
`tools/showkit/songs/<song>/`. Paths in those notes that start `(scratch)` were temp files and are gone.

- **This repo is public.** Never commit MP3s or other music (`*.mp3` is ignored), Wi-Fi names or passwords,
  TLS keys, `data/cal/spotify.json` or the relay token files. Scan staged diffs for them first.
  Don't use `git add -A`, because `.claude/` is only partly ignored.
- **Never raise a power limit** for sustained use. The owner's rule: power can go up for effects and shows as
  long as it isn't sustained for 10+ minutes. Make scenes lighter.
- **The helmet is real hardware.** One hardware test at a time, check `/json/info` `live` and `lip` first, and never send
  `on:false` from a test while somebody else is streaming. Deploy only at good signal with nothing streaming.
- A firmware flash needs the owner's say-so. Moving the laptop onto `WLED-AP` cuts its internet.
- Text on the helmet is a song's title words only, never other lyrics.
