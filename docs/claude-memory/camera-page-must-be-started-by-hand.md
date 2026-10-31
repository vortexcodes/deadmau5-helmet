---
name: camera-page-must-be-started-by-hand
description: mau5eye's server keeps running after the browser stops pushing, so a stale frame looks like a working camera
metadata:
  type: project
---

`mau5eye.py` is two halves: a Python server and a browser page that
pushes frames to it. The server survives the page closing, keeps
serving the last frame it got, and `/latest` returns it happily. On
2026-10-28 that frame was 9.6 hours old and from the previous camera
position, so every camera-dependent task was blocked for a whole
session without an error anywhere.

**Why:** a stale frame is indistinguishable from a live one unless
you look at the age, and the failure is silent on both sides.

**How to apply:** check `curl -s http://127.0.0.1:8752/api/status`
and look at `age` before using the camera for anything — it should be
a second or two. To restart: open `http://<laptop-lan-ip>:8752/` on
whichever device holds the camera and tap START CAMERA.
