# mau5head CAD

Everything needed to print the helmet, in its current state (generator **v18**, Nov 2026).
The CAD is code: `source/mau5head_hat.py` builds every part from about 150 named numbers,
so a change is an edit and a 90-second rerun, not a session of clicking.

- **How it was designed, and why it looks the way it does:** [`docs/cad-design.md`](../docs/cad-design.md)
- **How it goes together, step by step:** [`docs/build-guide.md`](../docs/build-guide.md)
- **The walkthrough, with the exploded view:** [on the website](https://vortex1.dev/project.html?p=mau5head-v2) (2:06). `render/film.py` builds it.
- **The older film:** [`docs/img/cad/mau5head_cad_tour.mp4`](../docs/img/cad/mau5head_cad_tour.mp4) (40 s). GIF excerpts are beside it.

![turntable](../docs/img/cad/turntable.gif)

> The CAD shell has 948 LED windows on a 68-channel grid. The helmet as built uses the
> front ones only (see *The helmet as built* in the main README), so the wiring files
> in `reference/` are the original plan, not the truth.

## What is where

```
cad/
  source/       the generators — rerun these, don't hand-edit the STEPs
    mau5head_hat.py     the whole helmet (shell, ears, visor, pivots, hat frame, tray…) → STEP
    visor_perforate.py  even hole field on the visor + one mesh boolean → 3MF  (~10 s)
    wall_mount.py       the wall mount (bracket, cradle, post, dome) → STEP + STL
    chain_plan.py       LED strip chaining plan for the original 948-pixel wiring
  parts/        one file per printed part, already in its own place
  visor/        the perforated visor in five hole patterns (3MF: open in PrusaSlicer)
  assembly/     everything in place: helmet, ears, wall mount, hard-hat envelope (two zipped)
  reference/    pixel map, original wiring plan and BOM, xLights model
  render/       the three.js + Playwright pipeline that made the renders and the film
```

## Print list

PETG throughout. Prusa XL (360 × 360 × 360). Every part fits with margin.

| File | Qty | Colour | Orientation | Notes |
|---|---|---|---|---|
| `parts/shell_half_TOP.step` + `shell_half_TOP_supports.step` | 1 | natural / white | cut face down, crown up | load the supports as a second part; they are designed break-away columns with a 0.25 mm gap |
| `parts/shell_half_BOTTOM.step` | 1 | same | neck ring down | |
| `parts/ear_half_top.step` | 2 | clear | cut face down | low infill (10 % gyroid) so the blades light the whole ear |
| `parts/ear_half_bottom.step` | 2 | clear | cut face down | **height-range modifier from 125 mm to the top: 100 % infill, 6 perimeters** (the peg carries the ear) |
| `visor/visor_A_…_RECOMMENDED.3mf` | 1 | **black** | standing on its bottom edge | Arachne, 2 perimeters, slow outer wall, **no supports inside the holes** |
| `parts/pivot_cap.step` | 2 | black | flat face down | |
| `parts/seam_plate.step` | 6 | black | flat | one per seam pad |
| `parts/hat_crown_frame.step` | 1 | black | outer (curved) face down, on supports | 4+ perimeters, 30 % infill |
| `parts/hat_spacers.step` | 1 set | black | as laid out | 4 each of 2 / 4 / 8 / 16 mm |
| `parts/hat_drill_template.step` | 1 | any | flat | 1.2 mm, flexes onto the hat |
| `parts/electronics_tray.step` | 1 | black | flat | |
| `parts/wallmount_bracket.stl` | 1 | any | on its side (large flat face down) | 4 perimeters, 30 % infill |
| `parts/wallmount_cradle.stl` | 1 | any | flat, pads up | 4 perimeters, 30 % infill |
| `parts/wallmount_post.stl` | 1 | any | standing | |
| `parts/wallmount_dome.stl` | 1 | any | flat base down | 10 % infill, 3 walls |

### Visor hole patterns

| File | Holes | Spacing | Open area | |
|---|---|---|---|---|
| `visor_orig-spacing_2.0mm-holes_3.6-pitch.3mf` | Ø2.0 | 3.6 | 28 % | the original helmet's spacing — hard to see through once printed |
| `visor_open_2.5mm-holes_3.6-pitch.3mf` | Ø2.5 | 3.6 | 44 % | |
| `visor_B_2.5mm-holes_3.4-pitch.3mf` | Ø2.5 | 3.4 | 51 % | tighter, hides you best |
| **`visor_A_2.9mm-holes_3.8-pitch_RECOMMENDED.3mf`** | **Ø2.9** | **3.8** | **55 %** | big holes, thin 0.85 mm webs |
| `visor_C_3.3mm-holes_4.2-pitch.3mf` | Ø3.3 | 4.2 | 58 % | easiest to see through |

Any other pattern: `python3 source/visor_perforate.py --hole 3.0 --pitch 3.9 --out my_visor.3mf`.

![hole patterns](../docs/img/cad/visor_mesh_compare.png)

## Hardware

| Item | Qty | Where |
|---|---|---|
| 10-32 brass heat-set inserts (6.4 mm pilot, ~7 mm long) | 34 | seam pads 12 · ear pegs 8 · crown bosses 4 · hat pads 4 · tray 2 · pivot pins 2 · wall bracket 2 |
| 10-32 × 3/8" socket cap | 20 | seam plates 12 · crown frame → shell 4 · tray 2 · pivot caps 2 |
| 10-32 × 1/2" | 8 | ear pegs |
| 10-32 × ½"–1½" assortment + 4 fender washers | 4 | hard hat → frame (length ≈ spacer stack + 10 mm) |
| 10-32 × 5/8" | 2 | wall cradle → bracket |
| #10 × 2½" wood screws | 3 | wall bracket → one stud |
| 1/4"-20 × 2½" bolt + nut | 1 | wall-mount post height pin |
| 1" OD × 3/4" ID clear polycarbonate tube, 36" | 2 | per ear: centre 13 3/8", 2 × side 9 3/4" |
| 6 × 3 mm N42 disc magnets | 6 | visor 2, shell 4 (closed + open) |
| 1.75 mm filament offcuts, 16 mm | 12 | seam alignment stubs |
| self-adhesive felt | 4 pads | wall-mount cradle |
| 3M SecureFit H-700 hard hat | 1 | the mount |

## Regenerating

```bash
pip install cadquery numpy scipy trimesh manifold3d
cd cad/source
python3 mau5head_hat.py              # everything → out/   (~90 s)
python3 mau5head_hat.py visor        # visor, ears, hat parts only (~25 s)
python3 visor_perforate.py           # → visor_perforated.3mf (variant A)
python3 wall_mount.py                # → out/wallmount_*.step/.stl
```

Frame for every file: origin at the sphere centre, +Z up, −Y the face, ±X the visor's pivot
axis, millimetres. The shell halves, visor, crown frame, tray and wall-mount parts are
exported where they sit on the helmet, so they line up when imported together. The ear
halves (in their own frame, peg tip at the origin), seam plate, pivot cap, spacers and drill
template are exported flat, ready to print; `assembly/` has the ears in place.
