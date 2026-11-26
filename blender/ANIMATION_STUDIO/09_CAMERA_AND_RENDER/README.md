# 09_CAMERA_AND_RENDER — `11_PYTHON_TOOLS/render_shorts.py`

- CAMERA_9_16: `camera()`, `aim()`, `follow()` (smoothed tracking), 1080x1920 (tests 540x960)
- LIGHTING: `stage()` — sky colour, one soft sun, test floor with a 0.5 m grid (foot sliding is visible on it)
- EEVEE: supported by `setup_engine("EEVEE")`; this container has no GPU — EEVEE/Workbench run on Mesa's software
  OpenGL (`libegl1`, `libgl1-mesa-dri`), slowly; Cycles is the default (the approved puppet look)
- OUTPUT: frames -> mp4 with ffmpeg (`render()` skips frames that exist, so renders resume)
