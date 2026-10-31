#!/usr/bin/env python3
"""Draws the world of Moar Ghosts n Stuff and writes the sprite sheet. Run from the repo root."""
import json
P = "moar_"
S = {}
def add(name, rows):
    w = {len(r) for r in rows}
    assert len(w) == 1, (name, w)
    S[P + name] = rows

# --- small ghost, 8 x 8 cells: looks right / left / ahead, two skirts
def small(eyes, hem):
    return ["..XXXX..",
            ".XXXXXX.",
            eyes,
            eyes,
            "XXXXXXXX",
            "XXXXXXXX",
            "XXXXXXXX",
            hem]
HEM_A = "X.XX.XX."
HEM_B = ".XX.XX.X"
add("gR_a", small("XXX.XX.X", HEM_A))
add("gR_b", small("XXX.XX.X", HEM_B))
add("gL_a", small("X.XX.XXX", HEM_A))
add("gL_b", small("X.XX.XXX", HEM_B))
add("gF_a", small("XX.XX.XX", HEM_A))
add("gF_b", small("XX.XX.XX", HEM_B))
# just the eyes of a small ghost (for the eaten ghost, and white eyes over a body)
def small_eyes(eyes):
    return ["........", "........", eyes, eyes, "........", "........", "........", "........"]
add("eR", small_eyes("..XX.XX."))
add("eL", small_eyes(".XX.XX.."))
add("eF", small_eyes(".XX..XX."))
# white eyes for the holes: one ghost, or four in a train, all in one sprite
add("ewR", small_eyes("...X..X."))
add("ewL", small_eyes(".X..X..."))
add("trainR", ["." .join([r] * 4) for r in small_eyes("...X..X.")])
add("trainL", ["." .join([r] * 4) for r in small_eyes(".X..X...")])
# --- frightened small ghost: little eyes, a squiggle for a mouth
def fright(hem, mouth):
    return ["..XXXX..",
            ".XXXXXX.",
            "XX.XX.XX",
            "XXXXXXXX",
            mouth,
            "XXXXXXXX",
            "XXXXXXXX",
            hem]
add("f_a", fright(HEM_A, "X.X.X.XX"))
add("f_b", fright(HEM_B, "XX.X.X.X"))
# four frightened ghosts in a row, one sprite, 35 cols: they hunt side to side together
def row(sp):
    rows = S[P + sp]
    return ["." .join([r] * 4) for r in rows]
add("row_a", row("f_a"))
add("row_b", row("f_b"))
# just the face of each, to be drawn over the row in another colour
def faces(mouth):
    r = ["........", "........", "..X..X..", "........", mouth, "........", "........", "........"]
    return ["." .join([x] * 4) for x in r]
add("rowface_a", faces(".X.X.X.."))
add("rowface_b", faces("..X.X.X."))
# Pac-Man himself, 8 x 8: open, half, shut, facing right and left
pac_o = ["..XXXX..",
         ".XXXXXX.",
         "XXXXXX..",
         "XXXX....",
         "XXXX....",
         "XXXXXX..",
         ".XXXXXX.",
         "..XXXX.."]
pac_h = ["..XXXX..",
         ".XXXXXX.",
         "XXXXXXXX",
         "XXXXX...",
         "XXXXX...",
         "XXXXXXXX",
         ".XXXXXX.",
         "..XXXX.."]
pac_c = ["..XXXX..",
         ".XXXXXX.",
         "XXXXXXXX",
         "XXXXXXXX",
         "XXXXXXXX",
         "XXXXXXXX",
         ".XXXXXX.",
         "..XXXX.."]
for nm, r in (("o", pac_o), ("h", pac_h), ("c", pac_c)):
    add("pacR_" + nm, r)
    add("pacL_" + nm, [x[::-1] for x in r])
# --- the giant: the whole shell is the ghost. 17 x 17, y_lo -108, y_hi 166, x_half 171.
# Dome = head and eyes; sides = body; jaw arc = the skirt.
def giant(e1, e2, e3, skirt1, skirt2):
    return ["....XXXXXXXXX....",
            "..XXXXXXXXXXXXX..",
            ".XXXXXXXXXXXXXXX.",
            e1,
            e2,
            e3,
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXXXX",
            skirt1,
            skirt2]
SK1_A = "XXX...XXX...XXX.."
SK2_A = "XXX...XXX...XXX.."
SK1_B = "..XXX...XXX...XXX"
SK2_B = "..XXX...XXX...XXX"
def sockets(s):
    return (s, s, s)
SOCK_R = sockets("XXXXX....XX....XX")
SOCK_L = sockets("XX....XX....XXXXX")
SOCK_F = sockets("XXX....XXX....XXX")
for d, s in (("R", SOCK_R), ("L", SOCK_L), ("F", SOCK_F)):
    add("G_%s_a" % d, giant(*s, SK1_A, SK2_A))
    add("G_%s_b" % d, giant(*s, SK1_B, SK2_B))
# what fills the sockets: the white of the eye, with the pupil left dark on the side it looks
def whites(top, low):
    e = "................."
    return [e, e, e, top, low, low] + [e] * 11
add("Gw_R", whites(".....XXXX..XXXX..", ".....XX....XX...."))
add("Gw_L", whites("..XXXX..XXXX.....", "....XX....XX....."))
add("Gw_F", whites("...XXXX...XXXX...", "...X..X...X..X..."))
# the giant frightened ghost: a solid blue body, and a face that hunts side to side on it
solid = "XXXXXXXXXXXXXXXXX"
add("F_a", giant(solid, solid, solid, SK1_A, SK2_A))
add("F_b", giant(solid, solid, solid, SK1_B, SK2_B))
def gface(m1, m2):
    b = "................."
    return [b, b, "....XX.....XX....", "....XX.....XX....", b, m1, m2] + [b] * 10
add("Fface_a", gface("...XX..XX..XX....", "....XX..XX..XX..."))
add("Fface_b", gface("....XX..XX..XX...", "...XX..XX..XX...."))
# BOO: the 5 x 7 letters held still on the dome. y_lo 50, y_hi 160, x_half 128
add("boo", ["XXXX...XXX...XXX.",
            "X...X.X...X.X...X",
            "X...X.X...X.X...X",
            "XXXX..X...X.X...X",
            "X...X.X...X.X...X",
            "X...X.X...X.X...X",
            "XXXX...XXX...XXX."])
# The maze: walls on the dome and sides. Same frame as the giant.
add("maze", ["....XXXXXXXXX....",
             "..XX....X....XX..",
             ".X..XXX.X.XXX..X.",
             ".X..XXX.X.XXX..X.",
             "X...............X",
             "X.XX.X.XXX.X.XX.X",
             "X.XX.X..X..X.XX.X",
             "X....XX.X.XX....X",
             "X...............X",
             "X...............X",
             "X...............X",
             "X...............X",
             "X...............X",
             "X...............X",
             "X...............X",
             "X...............X",
             "................."])
# Pac-Man big on the dome, for the intermission: 15 x 8, y_lo 48, y_hi 170, x_half 128
bp = {"o": ["....XXXXXXX....",
            "..XXXXXXXXXXX..",
            "XXXXXXXXXXXX...",
            "XXXXXXXXX......",
            "XXXXXXX........",
            "XXXXXXXXX......",
            "XXXXXXXXXXXX...",
            "..XXXXXXXXXXX.."],
      "h": ["....XXXXXXX....",
            "..XXXXXXXXXXX..",
            "XXXXXXXXXXXXXXX",
            "XXXXXXXXXXXX...",
            "XXXXXXXXX......",
            "XXXXXXXXXXXX...",
            "XXXXXXXXXXXXXXX",
            "..XXXXXXXXXXX.."],
      "c": ["....XXXXXXX....",
            "..XXXXXXXXXXX..",
            "XXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXX",
            "XXXXXXXXXXXXXXX",
            "..XXXXXXXXXXX.."]}
for k, r in bp.items():
    add("bpR_" + k, r)
    add("bpL_" + k, [x[::-1] for x in r])
# his death, the whole helmet: a wedge opening from straight up until there is nothing left
import math
BODY = ["....XXXXXXXXX....", "..XXXXXXXXXXXXX..", ".XXXXXXXXXXXXXXX."] + ["XXXXXXXXXXXXXXXXX"] * 11 + [".XXXXXXXXXXXXXXX.", "..XXXXXXXXXXXXX..", "....XXXXXXXXX...."]
for i, th in enumerate((14, 38, 62, 84, 106, 128, 150, 168)):
    rows = []
    for r in range(17):
        row_ = ""
        for c in range(17):
            ang = math.degrees(math.atan2(abs(c - 8), (4.5 - r)))
            row_ += "X" if BODY[r][c] == "X" and ang > th else "."
        rows.append(row_)
    add("die%d" % i, rows)
# two pairs of eyes either side of the pellet, watching it
add("watch", ["................",
              "................",
              ".XX.XX....XX.XX.",
              ".XX.XX....XX.XX.",
              "................",
              "................",
              "................",
              "................"])
json.dump(S, open("shows/scenes/deadmau5 - Moar Ghosts n Stuff.sprites.json", "w"), indent=0)
print(len(S), "sprites")
