# Renders and the film

How the CAD renders and `mau5head_cad_tour.mp4` were made: the STEP files are tessellated into
GLB meshes, a three.js page (`index.html`, `main.js`) poses them frame by frame, headless
Chromium (Playwright) screenshots each frame, and ffmpeg joins them.

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

Scenes live in `renderFrame()` in `main.js`: each is a function of time that places the parts,
the camera, the titles and the labels. WebGL runs on SwiftShader, so no GPU is needed
(about 1.3 s a frame at 1280 × 720).
