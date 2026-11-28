"""Sound of «واگن آخر ۷ — اون طرف آب»: the user's recording (voices/clips, cut + coloured by cut_voices.py) and
real ElevenLabs sound effects (sfx_el/, prompts in sfx_el/PROMPTS.md), each placed on its frame.
    out/sfx.wav     effects only
    out/voiced.wav  voices + effects (effects ducked about -13 dB under every line)
"""
import os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, END, KEY_OF  # noqa: E402
import beats as B  # noqa: E402
FX_DIR, OUT = os.path.join(HERE, "sfx_el"), os.path.join(HERE, "out")
SR = 48000
TOTAL = END + 4.0
PAN = {"Me": 0.0, "Lena": -0.15, "Rahim": 0.2, "Mom": 0.1}


def load(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", af]
    raw = subprocess.run(cmd + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def fx(name, af="loudnorm=I=-18"):
    return load(os.path.join(FX_DIR, name + ".mp3"), af)


def put(buf, x, t, gain=1.0, pan=0.0, length=None, fade=0.05):
    if length is not None:
        x = x[:int(length * SR)].copy()
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


def env(n, pts):
    ts = np.arange(n) / SR
    return np.interp(ts, [p[0] for p in pts], [p[1] for p in pts]).astype(np.float32)


def voices(buf):
    windows = []
    for key, who, _ in LINES:
        a, b = KEY_OF[key]
        x = load(os.path.join(HERE, "voices", "clips", key + ".wav"))
        put(buf, x, a, 0.9, PAN[who])
        windows.append((a, a + len(x) / SR))
    return windows


def effects(buf, duck=()):
    n = buf.shape[0]
    d = np.ones(n, np.float32)
    for a, b in duck:
        d[max(0, int((a - 0.15) * SR)):int((b + 0.2) * SR)] = 10 ** (-13 / 20)
    d = np.convolve(d, np.ones(5760) / 5760, mode="same").astype(np.float32)
    # the river: far below at the bank, loud on the bridge
    rv = loop(fx("5_river"), n / SR)
    g = env(n, [(0, 0.35), (B.CUT2 - 0.1, 0.35), (B.CUT2, 0.6), (B.WALK0, 0.6), (B.WALK0 + 3, 0.8), (TOTAL, 0.8)])
    put(buf, rv * g * d, 0.0, 1.0, fade=1.5)
    # the helicopter coming down across the river, rotor running, then winding down
    land = fx("1_heli_landing")
    run_len = B.WIND0 + 1.0
    hel = np.concatenate([land, loop(land[int(15 * SR):], max(0.1, run_len - len(land) / SR))])[:int(run_len * SR)]
    g = env(len(hel), [(0, 0.55), (B.LAND1, 0.75), (B.CUT2, 0.75), (run_len, 0.75)])
    put(buf, hel * g * d[:len(hel)], 0.0, 1.0, -0.3, fade=1.0)
    put(buf, fx("8_heli_winddown"), B.WIND0, 0.7, -0.3, fade=0.8)
    # over the radio: the door, the break-up, three knocks
    put(buf, fx("2_heli_door_radio"), B.DOOR_T, 0.75, 0.1)
    cut = fx("3_radio_cutoff")
    put(buf, cut, B.DEAD_T - 0.2, 0.9, 0.1, length=min(len(cut) / SR, 4.0), fade=0.4)
    hiss = cut[-int(2.5 * SR):]
    for k in ("mom1", "mom2", "mom3"):
        a, b = KEY_OF[k]
        put(buf, loop(hiss, (b - a) + 0.8), a - 0.4, 0.25, 0.1, fade=0.2)
    put(buf, loop(hiss, 6.0), B.DEAD_T + 3.5, 0.18, 0.1, fade=1.0)            # Lena keeps pressing the button
    put(buf, fx("4_three_knocks"), B.KNOCK0, 1.0, 0.1)
    # out on the rails: the plank, the horn behind us
    put(buf, fx("6_plank_break"), B.PLANK_T - 0.25, 1.0, -0.1)
    put(buf, fx("7_train_horn"), B.HORN_T, 0.95, 0.0, fade=0.3)
    # everything fades to black with the picture
    buf *= env(n, [(0, 1), (B.BLACK_T, 1), (B.BLACK_T + 1.5, 0), (TOTAL, 0)])[:, None]


def write(path, buf):
    buf = buf / max(1e-9, np.abs(buf).max()) * 0.89
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
    e = np.zeros((n, 2), np.float32)
    effects(e)
    write(os.path.join(OUT, "sfx.wav"), e)
    e2 = np.zeros((n, 2), np.float32)
    effects(e2, win)
    write(os.path.join(OUT, "voiced.wav"), e2 * 0.6 + v)
