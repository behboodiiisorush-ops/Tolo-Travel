"""
Sound effects + ambience for «واگن آخر ۳ — در بسته شد» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (81.6 s, 48 kHz stereo); post.py / mix_voices.py put it under the video.
"""

import math
import os
import wave

import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captions import END, KEY_OF  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = 81.6
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


# ---------------------------------------------------------------- helpers

def tt(n):
    return np.arange(n) / SR


def noise(n):
    return rng.standard_normal(n)


def band(x, lo, hi):
    """Band-pass by zeroing FFT bins (fine for offline sound design)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def env(n, a=0.01, r=0.3):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m > 0 else x


def put(x, t0, gain=1.0, pan=0.0):
    """Mix x at time t0 (s). pan -1 = left, +1 = right."""
    i = int(t0 * SR)
    if i >= N:
        return
    x = x[: N - i]
    gl, gr = gain * math.sqrt((1 - pan) / 2), gain * math.sqrt((1 + pan) / 2)
    L[i:i + len(x)] += x * gl
    R[i:i + len(x)] += x * gr


def curve(points, n=N):
    """Piecewise-linear automation from [(t, value), ...]."""
    ts, vs = zip(*points)
    return np.interp(tt(n), ts, vs)


# ---------------------------------------------------------------- sounds

def explosion(length=3.0, size=1.0):
    n = int(length * SR)
    boom = band(noise(n), 20, 400) * np.exp(-tt(n) * 1.6 / size)
    crack = band(noise(n), 400, 5000) * np.exp(-tt(n) * 9)
    sub = np.sin(2 * np.pi * 45 * tt(n)) * np.exp(-tt(n) * 2.5)
    return norm(boom * 1.0 + crack * 0.35 + sub * 0.6) * env(n, 0.005, 0.8)


def whistle(length=1.6):
    n = int(length * SR)
    t = tt(n)
    tone = sum(np.sin(2 * np.pi * f * t) / (k + 1) for k, f in enumerate((587, 740, 880)))
    breath = band(noise(n), 1500, 6000) * 0.15
    vib = 1 + 0.05 * np.sin(2 * np.pi * 6 * t)
    return norm((tone + breath) * vib) * env(n, 0.06, 0.4)


def siren(length=6.0):
    n = int(length * SR)
    t = tt(n)
    f = 450 + 350 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 2.4))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.3 * np.sin(2 * ph)
    return norm(x) * env(n, 0.8, 0.8)


def jet(length=1.6):
    n = int(length * SR)
    t = tt(n)
    roar = band(noise(n), 60, 3000)
    e = np.exp(-((t - length * 0.45) / (length * 0.22)) ** 2)
    return norm(roar) * e


def clack_track(speed):
    """Wheel clacks: two quick knocks per rail joint, rate follows train speed (m/s array)."""
    out = np.zeros(N)
    pos = np.cumsum(speed) / SR
    joints = np.floor(pos / 18.0)
    idx = np.nonzero(np.diff(joints) > 0)[0]
    k = band(noise(int(0.06 * SR)), 80, 1800) * np.exp(-tt(int(0.06 * SR)) * 60)
    for i in idx:
        for d in (0.0, 0.11 * 8.0 / max(speed[i], 1.0)):
            j = i + int(d * SR)
            if j + len(k) < N:
                out[j:j + len(k)] += k
    return norm(out)


def heartbeat(t0, t1, bpm, gain):
    beat = np.sin(2 * np.pi * 55 * tt(int(0.12 * SR))) * np.exp(-tt(int(0.12 * SR)) * 30)
    t = t0
    while t < t1:
        put(beat, t, gain)
        put(beat * 0.7, t + 0.22, gain)
        t += 60.0 / bpm


def footsteps(t0, t1, rate, gain, pan=0.0):
    step = band(noise(int(0.08 * SR)), 60, 2500) * np.exp(-tt(int(0.08 * SR)) * 45)
    t = t0
    while t < t1:
        put(step, t, gain * rng.uniform(0.7, 1.0), pan)
        t += 1.0 / rate


def tone(freq, length, gain=1.0):
    n = int(length * SR)
    return np.sin(2 * np.pi * freq * tt(n)) * env(n, 0.01, 0.02) * gain


def build():
    t = tt(N)
    T = KEY_OF
    stop = T["rahim1"][0] - 1.0
    border0, border1 = T["sol1"][0] - 1.3, T["lena3"][0] - 0.9
    door_open = T["n5"][0] - 0.6
    hush0, hush1 = T["n3"][1], T["n4"][0]          # the two seconds with only Lena's breath
    speed = np.interp(t, [0, stop - 2.5, stop, END + 10], [2.4, 2.0, 0, 0])
    in_train = ((t < border0) | (t >= border1)) & (t < door_open)
    duck = curve([(0, 1), (hush0 - 0.3, 1), (hush0 + 0.2, 0.25), (hush1 - 0.1, 0.25), (hush1 + 0.6, 1), (END + 10, 1)])
    third = ((t >= border0) & (t < border1)).astype(float)
    pov = 1 - third

    # the door slams shut, a muffled train from then on
    slam = band(noise(int(0.5 * SR)), 60, 2500) * np.exp(-tt(int(0.5 * SR)) * 14)
    put(norm(slam), 3.05, 0.9)
    put(norm(band(noise(int(0.9 * SR)), 800, 4000)) * env(int(0.9 * SR), 0.05, 0.3), 2.1, 0.12)  # sliding
    muffle = np.where(t < 3.1, 1.0, 0.6)
    rumble = norm(band(noise(N), 25, 200)) * (0.05 + 0.12 * speed) * duck * pov * muffle
    put(rumble, 0, 1.0)
    clacks = clack_track(np.maximum(speed, 0) * 4) * np.clip(speed / 2.4, 0, 1) * 0.4 * duck * pov * muffle
    put(clacks, 0, 1.0, 0.2)
    # mum's scream reaches us through the closed door (voice is in the recording; a little wind here)
    wind_out = norm(band(noise(N), 150, 1500)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * t))
    put(wind_out * curve([(0, 0.1), (3.1, 0.1), (3.2, 0.02), (door_open, 0.02), (door_open + 0.4, 0.12),
                          (border0, 0.12), (border0 + 0.01, 0.05), (border1, 0.05), (border1 + 0.01, 0.12),
                          (END, 0.12), (END + 8, 0.14)]), 0, 1.0, -0.1)

    # breathing: Lena's quick breaths through the ride, alone in the silence
    bt = 6.0
    while bt < door_open:
        n = int(0.35 * SR)
        g = 0.06 if not (hush0 <= bt < hush1) else 0.16
        put(band(noise(n), 500, 4000) * env(n, 0.08, 0.2), bt, g, 0.25)
        bt += 0.9 if hush0 - 6 < bt < hush1 + 4 else 1.4

    # brakes, the stop, the door opening onto the empty track
    n = int(2.4 * SR)
    sq = np.sin(2 * np.pi * np.cumsum(np.linspace(2900, 2300, n)) / SR) * env(n, 0.3, 0.5)
    put(sq + 0.3 * band(noise(n), 2000, 7000) * env(n, 0.3, 0.5), stop - 2.4, 0.1)
    clunk = band(noise(int(0.6 * SR)), 30, 500) * np.exp(-tt(int(0.6 * SR)) * 9)
    put(norm(clunk), stop, 0.7)
    put(band(noise(int(1.5 * SR)), 2000, 9000) * env(int(1.5 * SR), 0.02, 1.0), stop + 0.2, 0.1, 0.3)
    footsteps(stop + 0.3, T["rahim1"][0] + 0.2, 3.0, 0.15, 0.4)   # Rahim through the inner door
    put(norm(band(noise(int(0.9 * SR)), 800, 4000)) * env(int(0.9 * SR), 0.05, 0.3), door_open, 0.15)
    put(norm(band(noise(int(0.4 * SR)), 40, 3000)) * np.exp(-tt(int(0.4 * SR)) * 14), T["n6"][0] - 0.2, 0.5)  # jump down
    put(band(noise(int(0.5 * SR)), 1500, 6000) * env(int(0.5 * SR), 0.05, 0.3), T["n6"][0] + 0.5, 0.08)  # cloth

    # meanwhile at the border: crowd, a siren far off, soldiers' boots, the floodlight hum
    crowd = norm(band(noise(N), 250, 1800)) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.6 * t)))
    put(crowd * third * 0.09, 0, 1.0, -0.4)
    put(siren(border1 - border0) * 0.5, border0, 0.12, 0.6)
    footsteps(border0, T["sol1"][0] + 0.9, 3.4, 0.2, -0.3)
    footsteps(T["sol2"][1] - 0.2, border1, 3.0, 0.22, 0.0)
    hum = np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.2
    put(hum * third * 0.02, 0, 1.0)
    put(tone(200, 0.1, 0.25) * np.exp(-tt(int(0.1 * SR)) * 25), border0, 1.0)   # cut thump
    put(tone(200, 0.1, 0.25) * np.exp(-tt(int(0.1 * SR)) * 25), border1, 1.0)

    # the empty track: a faint, far hollow clatter of a wagon that is not there
    far = band(clack_track(np.full(N, 5.0)), 100, 1500)
    put(norm(far) * curve([(0, 0), (door_open + 1.0, 0), (door_open + 2.5, 0.05), (border0, 0.05),
                           (border0 + 0.01, 0), (END + 10, 0)]), 0, 1.0, -0.2)

    # heartbeat under the last line, then the card: no music, only wind and the rail
    heartbeat(T["n7"][0], END, 84, 0.3)
    rail = np.sin(2 * np.pi * 57 * t) * 0.3 + band(noise(N), 2000, 6000) * 0.4
    put(norm(rail) * curve([(0, 0), (END - 0.5, 0), (END, 0.04), (END + 7.4, 0.04), (END + 8, 0)]), 0, 1.0)

    # a low drone through the story, gone on the card
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.0), (2, 0.04), (hush0, 0.05), (hush0 + 0.5, 0.0), (hush1 + 1, 0.05),
                           (door_open, 0.07), (T["n7"][0], 0.09), (END - 0.3, 0.09), (END, 0), (END + 10, 0)]),
        0, 1.0)

    fade = curve([(0, 1), (END + 7.6, 1), (END + 7.9, 0), (END + 10, 0)])
    out = np.stack([L * fade, R * fade], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out




def write(path, data):
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "sfx.wav")
    write(p, build())
    print(p)
