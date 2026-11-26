# 04_FACIAL_ANIMATION — `11_PYTHON_TOOLS/setup_face.py`

One control bone `FACE_CTRL` with sliders (custom properties) drives everything through drivers that use Blender's
*simple expressions* (they run without "Auto Run Python Scripts").

| folder | how |
|---|---|
| EYE_TRACKING | `EYES_TARGET` bone (child of the head control); both eye bones Damped-Track it |
| BLINKING | `blink_L/R` -> lid bone rotation; `auto_blink()` keys natural blinks (2 closing, 1 closed, 3 opening frames, random gaps, sometimes one eye a frame late) |
| EYEBROWS | `brow_up_L/R`, `brow_angle` -> brow bone tilt + lift |
| JAW_CONTROL | `jaw_open` -> mouth `open` shape key (the cartoon mouth has no jaw bone; the shape key is the jaw) |
| LIP_SYNC | `lip_sync_from_audio()`: per-frame loudness -> jaw, spectral brightness -> wide vs. round — a light viseme approximation, **not** phoneme-accurate |
| EXPRESSIONS | presets `happy, sad, angry, surprise, fear` (sliders that drive brows, lids and mouth together) + actions `UHS_FACE_*` |
