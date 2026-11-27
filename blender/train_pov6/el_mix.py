"""Mix the ElevenLabs voices + ElevenLabs sound effects of «واگن آخر ۶ — سیگنال» (files in el/).
    out/sfx.wav     effects only
    out/voiced.wav  voices + effects
Voices (voices.py): Me = "amir" pitched up 3 st, Lena = "Sara" pitched up 5 st (ElevenLabs will not design
child voices), Rahim + Mom = voices designed and saved for this series.  Mom is heard through the radio.
Each line starts at its caption start (the lips are rendered there).
"""
import os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, END, KEY_OF  # noqa: E402
import part6_times as P  # noqa: E402
EL, OUT = os.path.join(HERE, "el"), os.path.join(HERE, "out")
SR = 48000
TOTAL = END + 4.0
FX = {"Me": "rubberband=pitch=1.19:formant=preserved",
      "Lena": "rubberband=pitch=1.335",
      "Rahim": "anull",
      "Mom": "highpass=f=350,lowpass=f=3200,acompressor=threshold=-20dB:ratio=6,volume=1.6"}
GAIN = {"Me": 1.0, "Lena": 0.95, "Rahim": 0.9, "Mom": 0.85}


def load(name, af=None, trim=True):
    flt = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse") if trim else "anull"
    if af:
        flt += "," + af
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(EL, name + ".mp3"), "-af", flt,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def put(buf, x, t, gain=1.0, pan=0.0, length=None, fade=0.05):
    if length is not None:
        x = x[:int(length * SR)]
    x = x * gain
    nf = min(len(x) // 2, int(fade * SR))
    if nf:
        x[:nf] *= np.linspace(0, 1, nf)
        x[-nf:] *= np.linspace(1, 0, nf)
    i = int(t * SR)
    j = min(buf.shape[0], i + len(x))
    if j <= i or i < 0:
        return
    buf[i:j, 0] += x[:j - i] * (1 - max(0, pan))
    buf[i:j, 1] += x[:j - i] * (1 + min(0, pan))


def loop(x, length):
    n = int(length * SR)
    return np.tile(x, int(np.ceil(n / len(x))) + 1)[:n]


def voices(buf):
    windows = []
    for key, who, _ in LINES:
        a, b = KEY_OF[key]
        x = load(key, FX[who])
        put(buf, x, a, GAIN[who], {"Me": 0, "Lena": -0.15, "Rahim": 0.2, "Mom": 0.1}[who])
        windows.append((a, a + len(x) / SR))
        print(f"{key:7s} {who:6s} {a:6.2f}s {len(x) / SR:5.2f}s (window {b - a:.2f}s)")
    return windows


def env(n, pts):
    """piecewise-linear gain curve from [(t, g), ...]"""
    ts = np.arange(n) / SR
    return np.interp(ts, [p[0] for p in pts], [p[1] for p in pts]).astype(np.float32)


def effects(buf, duck=()):
    n = buf.shape[0]
    # train rumble: full until the brakes, gone after the stop
    tr = loop(load("sfx_train", trim=False), n / SR)
    g = env(n, [(0, 0.5), (P.BRAKE0, 0.5), (P.BRAKE1, 0.0), (TOTAL, 0.0)])
    d = np.ones(n, np.float32)
    for a, b in duck:
        d[max(0, int((a - 0.2) * SR)):int((b + 0.2) * SR)] = 0.6
    d = np.convolve(d, np.ones(4800) / 4800, mode="same").astype(np.float32)
    put(buf, tr * g * d, 0.0, 1.0, fade=1.0)
    # helicopter: far, then loud overhead while it hovers, then away
    he = loop(load("sfx_heli", trim=False), n / SR)
    g = env(n, [(0, 0.15), (4, 0.3), (P.CURTAIN0 + 1, 0.15), (P.SEARCH_T - 1, 0.25), (P.DESC0, 0.35),
                (P.DESC1, 0.75), (P.LEAVE_T, 0.7), (P.LEAVE_T + 8, 0.0), (TOTAL, 0.0)])
    put(buf, he * g * d, 0.0, 1.0, -0.3, fade=1.0)
    put(buf, load("sfx_curtain"), P.CURTAIN0, 0.7, -0.2)
    put(buf, load("sfx_curtain"), P.OPEN0, 0.6, -0.4)
    click = load("sfx_click")
    for b in P.BLINKS:
        put(buf, click[:int(0.25 * SR)], b - 0.03, 0.8, 0.1)
    put(buf, load("sfx_search"), P.SEARCH_T - 0.05, 0.9, -0.3)
    put(buf, load("sfx_bag"), P.GRAB_T - 1.0, 0.85, -0.2)
    st = load("sfx_static", trim=False)
    put(buf, st, P.RADIO_T + 0.2, 0.35, 0.1, length=min(len(st) / SR, 6.0), fade=0.3)
    for k in ("mom1", "mom2", "mom3"):
        a, b = KEY_OF[k]
        put(buf, st, a - 0.4, 0.14, 0.1, length=(b - a) + 0.8, fade=0.2)
    put(buf, st, P.DEAD_T - 0.2, 0.45, 0.1, length=1.2, fade=0.1)         # the radio dies
    put(buf, load("sfx_brake"), P.BRAKE0 - 0.2, 1.0, 0.0)
    rv = loop(load("sfx_river", trim=False), n / SR)
    g = env(n, [(0, 0.0), (P.BRAKE0, 0.0), (P.BRAKE1, 0.5), (TOTAL, 0.5)])
    put(buf, rv * g, 0.0, 1.0, fade=1.0)


def write(path, buf):
    buf = buf / max(1e-9, np.abs(buf).max()) * 0.89
    tail = int(1.5 * SR)
    e = int(END * SR)
    buf[e:e + tail] *= np.linspace(1, 0, min(tail, len(buf) - e))[:, None]
    buf[e + tail:] = 0
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((buf * 32767).astype("<i2").tobytes())
    print(path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    n = int(TOTAL * SR)
    v = np.zeros((n, 2), np.float32)
    win = voices(v)
    fx = np.zeros((n, 2), np.float32)
    effects(fx)
    write(os.path.join(OUT, "sfx.wav"), fx.copy())
    fx2 = np.zeros((n, 2), np.float32)
    effects(fx2, win)
    write(os.path.join(OUT, "voiced.wav"), fx2 * 0.75 + v)
