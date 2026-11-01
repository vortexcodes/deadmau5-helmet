#!/usr/bin/env python3
"""reel.py -- all sixteen shows, a stretch of each, as they come out of the guard.

Each stretch is the real scene engine and the real power guard, warmed up on the
seconds before it. The website version plays score.follow, a stand-in built from
the song's grid and band curves, because the songs can't be hosted. --real uses
the MP3s instead; that file stays in data/cal/, which git ignores.

    python3 tools/film/reel.py                   # data/cal/shows.mp4
    python3 tools/film/reel.py --real            # data/cal/shows_real_audio.mp4
    python3 tools/film/reel.py --only 0 3 --sheet out.png
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import time

import numpy as np

from common import E, F, FPS, H, HelmetView, OUT, ROOT, SHOWS, Image, ImageDraw, Song, W, encoder, send, strip
import score

# (base, short title, from bar, to bar, what the ears, dome and jaw do, caption)
REEL = [
    ("TIKI TIKI - Slowed", "Tiki Tiki", 37, 43,
     "torches: kick on the rims, clap up the tubes", "an idol's brow and eyes, burning", "the idol's teeth",
     "This is the one every other show had to live up to. The idol first burns at bar 39."),
    ("deadmau5 - Strobe", "Strobe", 212, 219,
     "spinning rims, then a ladder of blades", "16 sparks that are the arpeggio", "dark until the drop",
     "Everything pulls away at bar 213. The one full white in the song is the drop at bar 217."),
    ("deadmau5 - Strobe (Dimension Remix)", "Strobe (Dimension Remix)", 76, 84,
     "the breakbeat: kick on both ears, 1 and the and of 3", "Strobe's 16 sparks, pink snare left then right", "part of the same snare halves",
     "Each phrase restart has a one-beat hole in the bass, and the helmet goes dark for that beat."),
    ("Fred again.. & Baby Keem - leavemealone", "leavemealone", 44, 52,
     "the drums: kick on the rims, snare up the tubes", "8 warm sparks are the vocal chop", "rings of heat in the hooks",
     "The track keeps stopping dead, and the helmet goes dark on those stops."),
    ("beneath (with raxaj)", "beneath", 46, 52,
     "surge from the base on the off-beat bass", "the pool rises until the face is molten", "a magma pool, throbbing on the kick",
     "A 3.5-beat silence at bar 48, then the drop at 49, and the pool in the jaw comes up into the face."),
    ("deadmau5 - Ghosts n Stuff (Nero Remix)", "Ghosts n Stuff (Nero Remix)", 61, 67,
     "kick on the rims", "ghosts drift by when the track empties, snare on 3", "lights with the dome on the snare",
     "Half time drop at bar 64. The bar line was half a bar off at first, so these marks used to fire late."),
    ("deadmau5 - FN Pig", "FN Pig", 232, 238,
     "alarm beacons, twitching on the snorts", "nostrils, a snout, then the whole furious pig", "a conveyor belt",
     "Starts as two nostrils breathing in the dark. The entire pig doesn't show up until bar 234."),
    ("deadmau5 - Moar Ghosts n Stuff", "Moar Ghosts n Stuff", 38, 44,
     "dots being eaten, clap in a ghost's colour", "maze and ghosts, a power pellet on the forehead", "more dots along the chin",
     "Pac-Man after dark. The pellet swells at 40, one dark beat, then everything turns frightened blue."),
    ("deadmau5 - Raise Your Weapon", "Raise Your Weapon", 128, 134,
     "shields being struck, far ear flares on the slash", "a blade drawn across the brow", "an army marching",
     "Eight minutes and a real tempo change, 128 up to 140. The drop puts a crimson slash on each snare."),
    ("deadmau5 - Some Chords", "Some Chords", 50, 56,
     "organ pipes, dark here on purpose", "stained glass, colour set by the chord", "the pedal: it follows the bass",
     "A chord organ. G#m is cobalt, E is ruby, F# is gold. This flood at bar 52 belongs to the shell."),
    ("deadmau5 - Some Chords (Radio Edit)", "Some Chords (Radio Edit)", 26, 32,
     "VU meters: kick on the left, chords on the right", "a dial with a needle, which becomes a mast", "the speaker",
     "An old radio being tuned. One dark beat at 27.75, then rings leave the mast on every beat."),
    ("deadmau5 & Wolfgang Gartner - Animal Rights", "Animal Rights", 46, 52,
     "claws: three horn stabs slash up the tubes", "a tiger, then a different animal each drop", "the fangs",
     "A zoo breakout. A cage slams at 32 and the tiger comes through at 48."),
    ("deadmau5 - The Veldt", "The Veldt", 44, 50,
     "the chord loop: each chord fires a tube", "a lion rising a row every two bars", "grass, sun, one roar",
     "The nursery from the Bradbury story. The eyes ignite at bar 45."),
    ("deadmau5 - Strobe (Special Features Remix)", "Strobe (Special Features Remix)", 62, 68,
     "two film reels, rims are the sprocket holes", "the history of cinema, one film at a time", "a film strip running past",
     "The picture is silver until the drop at bar 64, where colour shows up for the first time."),
    ("Kaskade feat. deadmau5 - I Remember", "I Remember", 100, 106,
     "they breathe and never strobe, colour is the chord", "a sepia photo, two figures", "part of the same photo",
     "Slow on purpose: ears rose, lavender, sea glass and amber with the chords. Sunrise at bar 102."),
    ("deadmau5 - Harder Better Faster Stronger", "Harder Better Faster Stronger", 90, 96,
     "a drum machine: rims kick, tubes riff, clap, hats", "a visor, then a test card, then an equaliser", "a voice box, as wide as the voice is loud",
     "A robot booting up. White at bar 92 splits into a rainbow equaliser."),
]

INTRO_WEB = ["These aren't the real songs. I can't host those on a public site.",
             "What you're hearing is a little synth playing each song's measured beat grid",
             "and its bass, mid and high curves, so the kicks are where the song's kicks are.",
             "The lights are exactly what the helmet would do with the real track."]
INTRO_REAL = ["Sixteen shows. Each one was written against its song, bar by bar.",
              "This is the show engine and the power guard, drawn on the helmet's LED map.",
              "Simulated, not filmed."]
CROSSFADE = 0.25


def card(lines):
    im = Image.new("RGB", (W, H), F.PAPER)
    d = ImageDraw.Draw(im)
    d.text((70, 150), "Sixteen songs", font=F.F_BIG, fill=F.INK)
    for k, s in enumerate(lines):
        d.text((74, 300 + k * 36), s, font=F.F_BODY, fill=F.INK2)
    return im


def panel(d, r, song, title, t, bar_from, label, rep, ears, dome, jaw, bpm):
    """The column to the right of the helmet: what each part of the helmet is doing."""
    x, y, w = 900, 26, 356
    d.rectangle([x - 20, 0, W, H - F.FOOT], fill=(17, 20, 24))
    if d.textlength(title, font=F.F_MID) < w:
        d.text((x, y), title, font=F.F_MID, fill=(232, 235, 238))
        y += 74
    else:
        for ln in title_lines(d, title, w):
            d.text((x, y), ln, font=F.F_TITLE, fill=(232, 235, 238))
            y += 42
        y += 8
    beat = song.beat_of(t)
    bar = beat / 4
    d.text((x, y), "%.0f BPM   bar %d  beat %d" % (bpm, int(np.floor(bar)), int(np.floor(beat)) % 4 + 1),
           font=F.F_BODY, fill=(170, 178, 186))
    y += 42
    for i in range(4):
        on = int(np.floor(beat)) % 4 == i
        fr = (beat % 1)
        c = (222, 170, 90) if on and fr < 0.5 else (58, 64, 72)
        d.ellipse([x + i * 26, y, x + i * 26 + 14, y + 14], fill=c)
    y += 38
    for name, text in (("EARS", ears), ("DOME", dome), ("JAW", jaw)):
        d.text((x, y), name, font=F.F_SMALL, fill=(222, 170, 90))
        y += 24
        for ln in wrap(d, text, w):
            d.text((x, y), ln, font=F.F_BODY, fill=(232, 235, 238))
            y += 27
        y += 16
    d.text((x, H - F.FOOT - 60), "scene: %s" % (label or "-")[:30], font=F.F_SMALL, fill=(130, 138, 146))
    d.text((x, H - F.FOOT - 34), "%4.0f mA to the LEDs after the guard" % rep["sent_ma"],
           font=F.F_SMALL, fill=(130, 138, 146))


def title_lines(d, text, w):
    out, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=F.F_TITLE) > w and cur:
            out.append(cur)
            cur = word
        else:
            cur = t
    return out + [cur]


def wrap(d, text, w):
    out, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=F.F_BODY) > w and cur:
            out.append(cur)
            cur = word
        else:
            cur = t
    return out + [cur] if cur else out


def bpm_of(song):
    return 60.0 / song.spb


def audio_for(songs, entries, real):
    """One long stereo track, each stretch crossfaded into the next, starting after
    the title card."""
    parts = []
    for k, (song, e) in enumerate(zip(songs, entries)):
        t0, t1 = song.t_of_bar(e[2]), song.t_of_bar(e[3])
        if real:
            parts.append(load_mp3(song.base, t0, t1 + CROSSFADE))
        else:
            p = score.follow(t0, t1 + CROSSFADE, song.spb, lambda s, g=song: g.t_of_beat(s / 4.0),
                             song.bands(), song.punch(), song.rate, root=song.root(t0, t1),
                             prog=("drift", "lift", "night")[k % 3], seed=100 * k)
            parts.append(p)
    return parts


def load_mp3(base, t0, t1):
    path = os.path.join(SHOWS, base + ".mp3")
    if not os.path.exists(path):
        path = os.path.join(ROOT, base + ".mp3")
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t0, "-t", "%.3f" % (t1 - t0), "-i", path,
                        "-f", "f32le", "-ac", "2", "-ar", str(score.SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).astype(float) * 0.8


def stitch(parts, lead):
    """Crossfade the parts end to start. Each part overlaps the next by CROSSFADE."""
    n = int(lead * score.SR)
    ov = int(CROSSFADE * score.SR)
    total = n + sum(len(p) - ov for p in parts) + ov
    out = np.zeros((total, 2))
    i = n
    ramp = np.linspace(0, 1, ov)[:, None]
    for p in parts:
        p = p.copy()
        p[:ov] *= ramp
        p[-ov:] *= ramp[::-1]
        out[i:i + len(p)] += p
        i += len(p) - ov
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--real", action="store_true", help="the real songs, for keeping locally")
    ap.add_argument("--only", nargs="*", type=int)
    ap.add_argument("--sheet", help="just save a contact sheet of mid-stretch frames here")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = a.out or os.path.join(OUT, "shows_real_audio.mp4" if a.real else "shows.mp4")
    entries = [REEL[k] for k in a.only] if a.only is not None else REEL
    M = F.Model()
    h = E.Helmet()
    view = HelmetView((0, 0, 880, H - F.FOOT), M, h)
    songs = [Song(e[0], h) for e in entries]

    if a.sheet:
        cols = 4
        tiles = []
        for song, e in zip(songs, entries):
            t0, t1 = song.t_of_bar(e[2]), song.t_of_bar(e[3])
            song.warm(t0)
            t = t0
            best = t0 + (t1 - t0) * 0.62
            while t < best:
                res, label, rep = song.frame(t)
                t += 1 / FPS
            im = Image.new("RGB", (W, H), F.DARK)
            d = ImageDraw.Draw(im)
            view.draw(im, res)
            panel(d, None, song, e[1], t, e[2], label, rep, e[4], e[5], e[6], bpm_of(song))
            strip(im, e[1], e[7])
            tiles.append(im.resize((480, 270)))
        rows = (len(tiles) + cols - 1) // cols
        o = Image.new("RGB", (cols * 480, rows * 270))
        for k, im in enumerate(tiles):
            o.paste(im, ((k % cols) * 480, (k // cols) * 270))
        o.save(a.sheet, quality=90)
        print(a.sheet)
        return

    lead = 7.0
    parts = audio_for(songs, entries, a.real)
    x = stitch(parts, lead)
    if not a.real:
        # the card plays over a pad at the first stretch's tempo, then the reel takes over
        spb = songs[0].spb
        pad = score.free(lead + 0.4, 60.0 / spb, [(0, 0, 0.45, 0.15)], root=songs[0].root(0, 60), prog="drift")
        m = min(len(pad), len(x))
        x[:m] += pad[:m] * np.linspace(1, 1, m)[:, None]
    x = x / (np.abs(x).max() + 1e-9) * 0.72
    x[:int(0.3 * score.SR)] *= np.linspace(0, 1, int(0.3 * score.SR))[:, None]
    x[-int(0.8 * score.SR):] *= np.linspace(1, 0, int(0.8 * score.SR))[:, None]
    tmp = tempfile.mkdtemp(prefix="mau5reel")
    wav = os.path.join(tmp, "a.wav")
    score.write_wav(wav, x)
    print(score.loudness(wav))

    enc = encoder(out, audio=wav)
    title = card(INTRO_REAL if a.real else INTRO_WEB)
    for _ in range(int(lead * FPS)):
        send(enc, title)
    started = time.time()
    done = 0.0
    for song, e in zip(songs, entries):
        t0, t1 = song.t_of_bar(e[2]), song.t_of_bar(e[3])
        song.warm(t0)
        bpm = bpm_of(song)
        n = int(round((t1 - t0) * FPS))
        # keep picture and sound together when stretches don't land on a whole frame
        n = int(round((done + (t1 - t0)) * FPS)) - int(round(done * FPS))
        done += t1 - t0
        for i in range(n):
            t = t0 + i / FPS
            res, label, rep = song.frame(t)
            im = Image.new("RGB", (W, H), F.DARK)
            view.draw(im, res)
            d = ImageDraw.Draw(im)
            panel(d, None, song, e[1], t, e[2], label, rep, e[4], e[5], e[6], bpm)
            strip(im, e[1], e[7])
            send(enc, im)
        print("  %-34s %5.1f s  %.0f s elapsed" % (e[1], t1 - t0, time.time() - started), flush=True)
    enc.stdin.close()
    enc.wait()
    print("wrote %s  %.1f MB" % (out, os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
