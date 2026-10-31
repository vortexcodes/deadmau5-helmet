#!/usr/bin/env python3
# The zoo's sprites: run from the repo root. Rows drawn by hand, half of them mirrored.
import json
BASE = "deadmau5 & Wolfgang Gartner - Animal Rights"
def mirror(rows):      # the left half, mirrored into the right, the last char is the centre column
    return [r + r[-2::-1] for r in rows]
def flip(rows):
    return [r[::-1] for r in rows]
S = {}
# Predator eyes on the dome, drawn on y_lo 40, y_hi 170, x_half 171: 21 x 8, about 16 mm a cell. Fierce: the outer corners high.
S["animal_eyes"] = mirror([
 "...........",
 "...........",
 "..##.......",
 "..####.....",
 "...#####...",
 "....###....",
 "...........",
 "..........."])
S["animal_eyes_wide"] = mirror([
 "...........",
 "..##.......",
 "..####.....",
 "..######...",
 "...#####...",
 ".....##....",
 "...........",
 "..........."])
S["animal_eyes_half"] = mirror([
 "...........",
 "...........",
 "...........",
 "..##.......",
 "...####....",
 "...........",
 "...........",
 "..........."])
S["animal_eyes_shut"] = mirror([
 "...........",
 "...........",
 "...........",
 "...........",
 "...###.....",
 "...........",
 "...........",
 "..........."])
# A second animal's eyes: rounder, set wider and lower, from the same box
S["animal_round"] = mirror([
 "...........",
 "...........",
 "...........",
 "...........",
 ".###.......",
 ".###.......",
 "..#........",
 "..........."])
S["animal_round_shut"] = mirror([
 "...........",
 "...........",
 "...........",
 "...........",
 "...........",
 ".###.......",
 "...........",
 "..........."])
# The second animal crouches low, on the thick ends of the jaw arc: same box as the jaw
S["animal_low"] = mirror([
 "...............",
 "...............",
 ".###...........",
 "..###..........",
 "...............",
 "...............",
 ])
S["animal_low_shut"] = mirror([
 "...............",
 "...............",
 "...............",
 "..###..........",
 "...............",
 "...............",
 ])
# The jaw arc, on y_lo -118, y_hi -40, x_half 171: 29 x 6, about 12 x 13 mm a cell.
# Rows from the top: y -46, -59, -72, -85, -98, -111. A tooth is a block with dark either side.
S["animal_jawO"] = mirror([
 "...............",
 "...............",
 "...............",
 "...............",
 "...##..........",
 "..###..###.##..",
 ])
S["animal_jawS"] = mirror([
 "#..............",
 "#..............",
 "##.............",
 "...##..........",
 "...##.##.......",
 "..###.###.##.#.",
 ])
# The cobra has two fangs and nothing else
S["animal_fangO"] = mirror([
 "...............",
 "...............",
 "...............",
 "...............",
 "...............",
 "....##.........",
 ])
S["animal_fangS"] = mirror([
 "...............",
 "...............",
 "...............",
 "....#..........",
 "....##.........",
 "....###........",
 ])
# Upper fangs along the dome's bottom edge, for a bite: y_lo 40, y_hi 170, x_half 171
S["animal_bite"] = mirror([
 "...........",
 "...........",
 "...........",
 "..#########",
 "...###..###",
 "...###...#.",
 "....#......",
 "....#......",
 ])
# Claw gashes across the dome: three diagonals in turn. 25 x 8 on y_lo 40, y_hi 170, x_half 171.
C = [
 ".......##.......##.......",
 "......##.......##......##",
 ".....##.......##......##.",
 "....##.......##......##..",
 "...##.......##......##...",
 "..##.......##......##....",
 ".##.......##......##.....",
 "##.......##......##......",
]
def gash(n):    # gash n of three, left to right, by which run of the row a cell is in
    out = []
    for i, r in enumerate(C):
        row = ""
        k = -1
        last = False
        # the first row has only two runs, so it starts at the second gash's count
        extra = 0 if r.count("##") == 3 else 0
        for ch in r:
            if ch == "#":
                if not last:
                    k += 1
                row += "#" if k < n else "."
                last = True
            else:
                row += "."
                last = False
        out.append(row)
    return out
for n in (1, 2, 3):
    S["animal_claw%d" % n] = gash(n)
    S["animal_clawR%d" % n] = flip(gash(n))
# A bull's horns, following the dome's edge up to the tips: 21 x 8 on y_lo 40, y_hi 170
S["animal_horns"] = mirror([
 "...#.......",
 "..##.......",
 ".##........",
 ".##........",
 ".##........",
 "..##.......",
 "..#######..",
 "....#####..",
 ])
# A bull's eyes, small, red, set in close
S["animal_bull"] = mirror([
 "...........",
 "...........",
 "...........",
 "...........",
 ".......##..",
 ".......##..",
 "...........",
 "..........."])
# A cobra's eyes, narrow and upright
S["animal_cobra"] = mirror([
 "...........",
 "...........",
 "......#....",
 "......#....",
 "......#....",
 "......#....",
 "...........",
 "..........."])
# The cobra rears: its hood flared round the dome, the two slits inside it
S["animal_hood"] = mirror([
 ".....######",
 "...###.....",
 ".###.......",
 ".##....#...",
 ".##....#...",
 "..###..#...",
 "....###....",
 ".......####",
 ])
S["animal_hood2"] = mirror([
 "...........",
 "....#######",
 "..###......",
 "..##...#...",
 "..##...#...",
 "...###.#...",
 ".....##....",
 ".......####",
 ])
json.dump(S, open("shows/scenes/%s.sprites.json" % BASE, "w"), indent=0)
print(len(S), "sprites")
