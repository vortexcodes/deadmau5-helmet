# Renders and the films

Two pipelines live here. Both tessellate the STEP files and pose them in three.js, frame by frame.

## The CAD walkthrough (1920 x 1080, 30 fps, silent, about 2 minutes)

`export_walkthrough.py` turns the committed STEP files into meshes, `walkthrough.js` is the film
(every frame is a pure function of time, `renderAt(t)`), and `film.py` drives it in Chrome and collects the
frames. It runs on the real GPU (ANGLE on Metal, about 0.05 s a frame with the PNG write on an M4 Pro).
The output and the meshes are git-ignored.

```bash
python3 -m venv VENV                     # python 3.9 works: cadquery-ocp has a cp39 arm64 wheel
VENV/bin/pip install cadquery trimesh networkx lxml playwright
export MAU5_CAD_BUILD=$PWD/build         # or anywhere else; holds mesh/, scene.json, node_modules/
mkdir -p build && (cd build && npm init -y && npm install three@0.160.0)

# The "a change is a rerun" shot needs one real rerun of the generator with thicker ears, in a copy:
cp -r ../source /tmp/thick && cd /tmp/thick
sed -i '' 's/^EAR_T, EAR_RIM_T = 60.0, 26.0/EAR_T, EAR_RIM_T = 90.0, 26.0/' mau5head_hat.py
VENV/bin/python mau5head_hat.py          # writes out/ there, nothing in the repo
cd -

VENV/bin/python export_walkthrough.py build --thick /tmp/thick/out    # meshes and scene.json
VENV/bin/python film.py info                       # chapter times, caption reading speed
VENV/bin/python film.py check                      # every frame's labels: overlaps, crossings, off screen
VENV/bin/python film.py stills out 12,40,90        # single frames
VENV/bin/python film.py verify out                 # assembled, from every side and in section
VENV/bin/python film.py video frames               # all frames as PNGs, about 7.5 GB
ffmpeg -framerate 30 -i frames/%05d.png -c:v libx264 -preset slow -crf 18 -x264-params aq-mode=3 \
  -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p" -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -movflags +faststart ../../data/cal/cad_walkthrough_silent.mp4
```

`check_placement.py` proves the placements against the CAD: ears and seam plates against the assembly STEPs,
the volume each placed part shares with its neighbours, and the LED map against the ears.

Worth knowing:

- Meshes come from `cad/parts` and `cad/assembly`, as committed. The parts that exist only flat (ear halves, pivot
  cap, seam plate, spacers) are placed with the generator's own variables: the export runs its placement code in a temp
  folder and writes `scene.json`.
- On CadQuery 2.5.2 (the newest with a Python 3.9 wheel) a rerun of the generator at the committed `EAR_T = 60` writes
  broken ear files (`ear_L.step` invalid, `ear_half_top.step` empty). The other parts match the committed STEPs.
  At `EAR_T = 90` the ears come out valid, so the film's thick ears are a real output. The docs name CadQuery 2.8.
- The LEDs are the as-built map, `data/cal/pixel_map.csv`: 398 on the shell, 186 in the tubes, 37 on the rims.
- A negative `globalAlpha` is ignored by canvas, even -1e-16, and the last alpha stays. That gave one-frame text flashes
  until `ss()` was clamped.

## The older tour (1280 x 720, 40 s): `docs/img/cad/mau5head_cad_tour.mp4`

`export_meshes.py` and `scene_data.py` make `glb/`, `main.js` and `index.html` pose it, and `shoot.py` shoots it on
SwiftShader (about 1.3 s a frame).

```bash
pip install cadquery trimesh fast-simplification playwright
npm install three@0.160.0
python3 export_meshes.py ../source/out/ ../source/out/    # STEP → glb/*.glb  (run mau5head_hat.py and wall_mount.py first)
python3 scene_data.py ../source/out/                      # ear tubes, LED positions → glb/scene.json
python3 shoot.py stills turntable:4 exploded:6.5          # single frames → stills/
python3 shoot.py video turntable exploded visor wallmount # every frame → frames_<scene>/
for s in turntable exploded visor wallmount; do
  ffmpeg -framerate 30 -i frames_$s/%05d.jpg -c:v libx264 -crf 20 -pix_fmt yuv420p $s.mp4; done
```
