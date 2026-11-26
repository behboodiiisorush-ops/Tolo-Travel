"""
Sound effects + ambience for «پناهگاه ۳ — اتوبوس نجات» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (the film + the card, 48 kHz stereo); post.py / mix_voices.py put it under the video.
"""

import math
import os
import wave

import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captions import END, KEY_OF, CARD_SECONDS  # noqa: E402
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = END + CARD_SECONDS
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


def growl(length, pitch=1.0):
    """A zombie growl: low buzzing noise through a moving formant, rough and uneven."""
    n = int(length * SR)
    tt_ = tt(n)
    f0 = (70 + 25 * np.sin(2 * np.pi * 1.3 * tt_) + 10 * rng.standard_normal(n).cumsum() / SR) * pitch
    buzz = np.sign(np.sin(2 * np.pi * np.cumsum(f0) / SR)) * 0.6 + band(noise(n), 100, 1200)
    form = band(buzz, 200, 900) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 2.1 * tt_)))
    return norm(form) * env(n, 0.15, 0.4)



def bark(pitch=1.0):
    n = int(0.28 * SR)
    t = tt(n)
    f = (380 - 520 * t) * pitch
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + band(noise(n), 300, 2500)
    return norm(band(x, 150, 3000)) * env(n, 0.005, 0.12)


def howl(length=2.5, pitch=1.0):
    n = int(length * SR)
    t = tt(n)
    f = (330 + 200 * np.sin(np.pi * t / length) - 60 * t / length) * pitch
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return norm(x * (1 + 0.04 * np.sin(2 * np.pi * 5 * t))) * env(n, 0.3, 0.8)


def static(length):
    n = int(length * SR)
    x = band(noise(n), 900, 6000) * (0.6 + 0.4 * (rng.random(n) > 0.997).cumsum() % 2)
    return norm(x) * env(n, 0.02, 0.05)


def build():
    E = json.load(open(os.path.join(HERE, "out", "events.json")))
    T = KEY_OF
    t = tt(N)
    go, stop, bang, dogs = E["T_GO"], E["T_STOP"], E["T_BANG"], E["T_DOGS"]
    forest, door, out_ = E["T_FOREST"], E["T_DOOR"], E["T_OUT"]
    arr0, arr1 = E["T_ARRIVE"]
    t_in = E["T_IN"]
    # where we are: inside the shelter (0) / outside (1); inside the bus muffles the outside
    outside = curve([(0, 0), (door, 0), (door + 1.0, 1), (END + 20, 1)])
    in_bus = curve([(0, 0), (t_in - 0.1, 0), (t_in, 1), (END + 20, 1)])
    # shelter: the ventilation hum, the lantern buzz
    hum = norm(band(noise(N), 60, 300)) * 0.5 + np.sin(2 * np.pi * 50 * t) * 0.3
    put(norm(hum) * 0.05 * (1 - outside), 0, 1.0)
    # coughs in the shelter
    for k in range(int(T["resc1"][0] / 3.1)):
        n2 = int(0.4 * SR)
        put(band(noise(n2), 400, 3500) * env(n2, 0.1, 0.2), 4 + k * 3.1, 0.035, rng.uniform(-0.6, 0.6))
    # the loudspeaker: a crackle and a feedback whine before the voice
    put(static(1.2) * 0.5, T["resc1"][0] - 1.4, 0.25)
    put(tone(1850, 1.0, 0.2), T["resc1"][0] - 1.2, 0.25)
    # the bus coming closer (engine), stopping (brakes, door hiss)
    speed = np.zeros(N)
    vmax = 10.0
    speed += curve([(0, 0), (go, 0), (go + 4, vmax), (forest - 2, vmax), (forest + 2, vmax * 0.8), (dogs + 0.5, vmax * 0.8),
                    (dogs + 2.5, vmax * 1.15), (bang, vmax * 1.15), (stop, 0), (END + 20, 0)])
    rpm = 30 + speed * 6 + curve([(0, 0), (arr0, 0), (arr0 + 0.5, 25), (arr1, 0), (END + 20, 0)])
    ph = 2 * np.pi * np.cumsum(rpm) / SR
    engine = np.sin(ph) + 0.5 * np.sin(2 * ph + 1) + 0.3 * np.sign(np.sin(3 * ph)) + band(noise(N), 40, 300) * 0.5
    eng_gain = curve([(0, 0), (arr0 - 3, 0), (arr1, 0.6), (go, 0.6), (go + 3, 0.9), (stop, 0.9), (stop + 1.5, 0),
                      (END + 20, 0)])
    eng_gain = eng_gain * (0.35 + 0.65 * np.clip(outside + in_bus, 0, 1))
    put(norm(band(engine, 30, 900)) * eng_gain * 0.3, 0, 1.0)
    put(norm(band(noise(int(1.2 * SR)), 1500, 6000)) * env(int(1.2 * SR), 0.05, 0.6), arr1 - 0.6, 0.15)    # brakes
    put(norm(band(noise(int(0.6 * SR)), 2000, 8000)) * env(int(0.6 * SR), 0.01, 0.3), arr1 + 0.3, 0.12)    # door hiss
    put(norm(band(noise(int(0.6 * SR)), 2000, 8000)) * env(int(0.6 * SR), 0.01, 0.3), go - 0.8, 0.12)
    # road noise grows with speed
    road = norm(band(noise(N), 80, 1500)) * (speed / vmax) * 0.12
    put(road, 0, 1.0)
    # the steel door: wheel creak, grind, gust of outside air
    nn = int(1.3 * SR)
    grind = np.sin(2 * np.pi * np.cumsum(np.linspace(140, 95, nn)) / SR) * 0.5 + band(noise(nn), 80, 900)
    put(norm(grind) * env(nn, 0.2, 0.4), door - 0.2, 0.3)
    wind = norm(band(noise(N), 120, 1300)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t))
    put(wind * outside * (1 - 0.6 * in_bus) * curve([(0, 0.1), (forest, 0.1), (forest + 2, 0.05), (END + 20, 0.05)]), 0, 1.0, -0.2)
    # footsteps to the bus, and on the bus floor
    footsteps(out_ + 0.2, T["old1"][0] - 1.0, 4.0, 0.12, 0.1)
    footsteps(t_in, T["lena3"][0] - 0.5, 3.0, 0.1)
    # the dead city: far fires crackling, a far siren once
    crack = np.zeros(N)
    for k in range(int((forest - go) * 30)):
        i = int((go + rng.uniform(0, forest - go)) * SR)
        if i + 200 < N:
            crack[i:i + 200] += rng.standard_normal(200) * np.exp(-np.arange(200) / 40)
    put(norm(band(crack, 800, 6000)) * 0.08, 0, 1.0, 0.3)
    put(siren(5.0) * 0.03, T["n4"][0] + 1.0, 1.0, -0.6)
    # dusk -> night: crickets in the forest, an owl
    cr = np.sin(2 * np.pi * 4200 * t) * (np.sin(2 * np.pi * 28 * t) > 0.6) * (np.sin(2 * np.pi * 0.9 * t) > -0.2)
    put(cr * curve([(0, 0), (forest - 1, 0), (forest + 1, 0.02), (dogs, 0.02), (dogs + 0.3, 0), (stop + 4, 0),
                    (stop + 7, 0.015), (END + 20, 0.015)]), 0, 1.0, 0.4)
    # the radio: static under the voices
    for a, b in (T["radio1"], T["radio2"]):
        put(static(b - a + 0.8), a - 0.4, 0.1)
    put(static(0.6), T["me1"][0] + 0.3, 0.06)
    put(static(0.5), T["me4"][0] + 0.1, 0.06)
    put(static(0.5), T["me6"][0] + 0.1, 0.06)
    # eyes in the trees: a low growl; then the dogs: growls, barks, paws
    put(band(growl(2.4, 0.7), 60, 600), T["lena5"][0] - 0.6, 0.25, -0.5)
    put(howl(2.6), T["old3"][0] + 0.8, 0.2, 0.6)
    for k in range(int((stop - dogs) * 3.2)):
        put(bark(rng.uniform(0.85, 1.25)), dogs + k / 3.2 + rng.uniform(0, 0.2), 0.3 * rng.uniform(0.6, 1.0),
            rng.uniform(-0.8, 0.8))
    for k in range(int((stop - dogs) / 1.2)):
        put(growl(1.0, rng.uniform(1.2, 1.5)), dogs + k * 1.2, 0.25, rng.uniform(-0.6, 0.6))
    # chewing the tyre: rubber squeaks
    for k in range(int((bang - T["me5"][0]) * 6)):
        n2 = int(0.07 * SR)
        put(norm(band(noise(n2), 700, 3000)) * env(n2, 0.005, 0.04), T["me5"][0] - 0.4 + k / 6, 0.15, -0.3)
    # the tyre bursts: bang, hiss, flapping rubber, the skid
    put(explosion(1.2, 0.4), bang, 0.9, -0.2)
    put(norm(band(noise(int(2.5 * SR)), 2000, 9000)) * env(int(2.5 * SR), 0.01, 1.5), bang + 0.05, 0.25, -0.3)
    flap = np.zeros(int((stop - bang) * SR))
    for k in range(int((stop - bang) * 12)):
        i = int(k / 12 * SR)
        flap[i:i + 400] += band(noise(400), 80, 900) * np.exp(-np.arange(400) / 80)
    put(norm(flap) * curve([(0, 1), (stop - bang, 0.2)], len(flap)), bang + 0.1, 0.4)
    put(norm(band(noise(int((stop - bang) * SR)), 500, 3500)) * env(int((stop - bang) * SR), 0.2, 0.6), bang + 0.4, 0.2)
    # stopped: claws on the metal all around, slow growls, then quiet
    for k in range(14):
        n2 = int(0.45 * SR)
        sc_ = band(noise(n2), 2500, 9000) * np.abs(np.sin(2 * np.pi * 7 * tt(n2)))
        put(norm(sc_) * env(n2, 0.05, 0.1), stop + 0.8 + k * 0.75 + rng.uniform(0, 0.3), 0.12, rng.uniform(-1, 1))
    for k in range(5):
        put(growl(1.8, rng.uniform(0.8, 1.0)), stop + 1.0 + k * 2.2, 0.2, rng.uniform(-0.8, 0.8))
    # the far car: an engine starting far away
    nn = int(4 * SR)
    far = np.sin(2 * np.pi * np.cumsum(np.linspace(35, 60, nn)) / SR) + band(noise(nn), 40, 300)
    put(norm(far) * env(nn, 1.0, 1.0), E["T_LIGHTS"] - 0.6, 0.12)
    # heartbeat in the forest, a low pad under it all
    heartbeat(T["lena5"][0], END, 112, 0.25)
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.03), (T["resc1"][0], 0.03), (T["resc1"][0] + 0.5, 0.0), (go, 0.0), (go + 3, 0.035),
                           (forest, 0.05), (dogs, 0.08), (stop, 0.1), (END - 0.3, 0.08), (END, 0), (END + 20, 0)]), 0, 1.0)
    put(wind * curve([(0, 0), (END - 0.2, 0), (END, 0.05), (END + CARD_SECONDS - 0.6, 0.05), (END + CARD_SECONDS, 0)]), 0, 1.0)
    fade = curve([(0, 1), (END + CARD_SECONDS - 0.4, 1), (END + CARD_SECONDS - 0.1, 0), (END + 20, 0)])
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
