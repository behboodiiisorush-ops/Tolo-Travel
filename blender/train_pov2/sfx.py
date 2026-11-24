"""
Sound effects + ambience for «واگن آخر ۲ — برگشت» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (71 s, 48 kHz stereo); post.py / mix_voices.py put it under the video.
"""

import math
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = 71.0
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


# ---------------------------------------------------------------- the mix

def gravel_steps(t0, t1, rate, gain, pan=0.0):
    n = int(0.11 * SR)
    t = t0
    while t < t1:
        crunch = band(noise(n), 900, 7000) * np.exp(-tt(n) * 30) + band(noise(n), 80, 600) * np.exp(-tt(n) * 50)
        put(crunch, t, gain * rng.uniform(0.7, 1.0), pan)
        t += 1.0 / rate * rng.uniform(0.9, 1.1)


def knock(t0, gain=0.6):
    n = int(0.25 * SR)
    x = band(noise(n), 60, 900) * np.exp(-tt(n) * 28)
    ring = sum(np.sin(2 * np.pi * f * tt(n)) for f in (190, 410, 690)) * np.exp(-tt(n) * 18)
    put(norm(x + 0.3 * ring), t0, gain)


def scrape(t0, length, gain, lo=1200, hi=5000):
    n = int(length * SR)
    t = tt(n)
    f = 900 + 400 * np.sin(2 * np.pi * 3 * t) + rng.standard_normal(n).cumsum() * 0.02
    sq = np.sin(2 * np.pi * np.cumsum(f) / SR)
    put(norm(sq * 0.4 + band(noise(n), lo, hi)) * env(n, 0.05, 0.2), t0, gain)


def build():
    t = tt(N)
    # train speed (m/s), the same timing as part_wagon.py
    speed = np.interp(t, [0, 16, 18.5, 24.8, 26.6, 52.5, 56, 71], [0, 0, 9, 9, 0, 0, 8, 8])
    in_car = curve([(0, 1), (27.0, 1), (27.01, 0), (51.2, 0), (51.4, 1), (71, 1)])
    outside = 1 - in_car

    rumble = norm(band(noise(N), 25, 220)) * (0.04 + 0.02 * speed) * (speed > 0.05)
    clacks = clack_track(np.maximum(speed, 0.0)) * np.clip(speed / 9, 0, 1) * 0.32
    put(rumble, 0, 1.0)
    put(clacks, 0, 1.0)
    # idling engine hum while the train stands
    idle = sum(np.sin(2 * np.pi * f * t) for f in (48, 96, 144)) * 0.3 + band(noise(N), 40, 160)
    put(norm(idle) * curve([(0, 0.05), (16, 0.05), (17, 0.0), (27, 0.0), (27.01, 0.08), (52.5, 0.08),
                            (54, 0.0), (71, 0)]), 0, 1.0)

    # the border: crowd behind the fence, dogs, floodlight hum (first 16 s)
    crowd = norm(band(noise(N), 250, 1800)) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.6 * t)))
    put(crowd * curve([(0, 0.08), (15, 0.07), (17, 0.0), (71, 0)]), 0, 1.0, -0.6)
    hum = np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.2
    put(hum * curve([(0, 0.03), (16, 0.03), (17, 0), (71, 0)]), 0, 1.0, -0.4)
    for tb in (1.4, 1.75, 8.6, 14.2):
        nb = int(0.18 * SR)
        f = np.linspace(520, 300, nb)
        bark = np.sin(2 * np.pi * np.cumsum(f) / SR) * band(noise(nb), 300, 2500) * env(nb, 0.01, 0.1)
        put(norm(bark), tb, 0.12, -0.8)

    # hook: heartbeat and breathing
    heartbeat(0.0, 3.2, 100, 0.55)
    breath = band(noise(int(0.5 * SR)), 300, 3000) * env(int(0.5 * SR), 0.15, 0.3)
    for k in range(5):
        put(breath, 0.2 + k * 0.62, 0.1)

    # goodbye: footsteps away down the aisle, the door, whistle, the jolt
    footsteps(13.9, 17.2, 2.4, 0.18, 0.1)
    footsteps(13.2, 16.6, 3.0, 0.12, -0.1)
    footsteps(10.4, 11.1, 3.2, 0.2, 0.2)       # Rahim
    footsteps(16.4, 17.2, 3.2, 0.2, 0.2)
    put(norm(band(noise(int(0.6 * SR)), 300, 3000)) * env(int(0.6 * SR), 0.05, 0.3), 17.2, 0.1, 0.0)
    put(whistle(1.4), 15.4, 0.3, -0.3)
    clunk = band(noise(int(0.6 * SR)), 30, 500) * np.exp(-tt(int(0.6 * SR)) * 9)
    put(norm(clunk), 16.0, 0.7)
    put(norm(clunk), 26.4, 0.6)

    # radio, phone
    static = band(noise(int(1.6 * SR)), 800, 6000) * (0.5 + 0.5 * (rng.random(int(1.6 * SR)) > 0.6))
    put(static * env(int(1.6 * SR), 0.05, 0.2), 16.9, 0.1, 0.3)
    put(band(noise(int(0.12 * SR)), 1000, 5000), 16.85, 0.2, 0.3)
    for k in range(4):
        put(tone(950, 0.3, 0.06), 21.0 + k * 0.36)
        put(tone(1400, 0.3, 0.04), 21.12 + k * 0.36)

    # brakes
    n = int(2.0 * SR)
    sq = np.sin(2 * np.pi * np.cumsum(np.linspace(3100, 2400, n)) / SR) * env(n, 0.3, 0.5)
    put(sq + 0.3 * band(noise(n), 2000, 7000) * env(n, 0.3, 0.5), 24.8, 0.12)
    put(band(noise(int(1.5 * SR)), 2000, 9000) * env(int(1.5 * SR), 0.02, 1.0), 26.6, 0.12, -0.3)

    # outside: wind over the empty fields, far rumbles
    wind = norm(band(noise(N), 150, 1800)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.13 * t))
    put(wind * outside * 0.12, 0, 1.0, 0.2)
    for tb, g in ((30.8, 0.18), (35.5, 0.22), (43.6, 0.25)):
        put(explosion(3.0, 1.6), tb, g, rng.uniform(-0.8, 0.8))

    # the jump, the run, the knocking, the stuck door
    put(norm(band(noise(int(0.4 * SR)), 40, 3000)) * np.exp(-tt(int(0.4 * SR)) * 14), 27.98, 0.7)
    gravel_steps(28.1, 29.9, 4.2, 0.3)
    gravel_steps(28.7, 32.0, 3.8, 0.16, 0.4)     # Jalal behind us
    for tk in (30.05, 30.3, 30.55, 30.8, 31.85, 32.05):
        knock(tk, 0.55)
    for tk in (32.55, 32.7, 32.85):
        put(norm(band(noise(int(0.12 * SR)), 200, 4000)) * env(int(0.12 * SR), 0.005, 0.1), tk, 0.35)
    scrape(33.0, 0.85, 0.3)
    put(norm(clunk), 33.85, 0.5)
    put(norm(clunk) * 0.6, 34.3, 0.35)         # climbing in

    # the jet: a far rumble that grows, the fly-by, the explosion
    approach = norm(band(noise(N), 60, 1500)) * curve([(0, 0), (39.4, 0), (40.2, 0.05), (46.0, 0.12),
                                                         (46.8, 0.25), (47.6, 0.05), (49, 0), (71, 0)])
    put(approach, 0, 1.0, -0.3)
    put(jet(1.6), 46.4, 0.9, -0.2)
    put(explosion(4.0, 1.6), 47.7, 1.0, 0.6)
    glass = band(noise(int(1.2 * SR)), 2500, 12000) * np.exp(-tt(int(1.2 * SR)) * 5)
    put(glass, 47.8, 0.08, 0.6)

    # walking back slowly, climbing aboard, the train leaving
    gravel_steps(45.9, 49.0, 2.2, 0.2)
    gravel_steps(46.0, 49.0, 1.7, 0.14, -0.4)
    for tc in (49.5, 50.3, 50.9, 51.9):
        put(norm(clunk) * 0.6, tc, 0.4)
    put(whistle(1.3), 52.0, 0.3)

    # the ride back: phone rings, the call connects, radio, heartbeat to the end
    for k in range(2):
        put(tone(1318, 0.12, 0.2), 59.2 + k * 0.25)
        put(tone(1568, 0.12, 0.18), 59.32 + k * 0.25)
    put(tone(880, 0.1, 0.15), 59.75)
    put(static * env(int(1.6 * SR), 0.05, 0.2), 62.95, 0.1, 0.3)
    put(band(noise(int(0.12 * SR)), 1000, 5000), 62.9, 0.2, 0.3)
    heartbeat(64.0, 70.0, 105, 0.5)
    put(tone(200, 0.12, 0.4) * np.exp(-tt(int(0.12 * SR)) * 20), 66.05, 1.0)  # card thump

    # tension pad
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.0), (2, 0.05), (12, 0.06), (16, 0.04), (24, 0.07), (34.5, 0.03), (39.5, 0.04),
                           (46, 0.09), (52, 0.06), (56, 0.03), (60, 0.04), (66, 0.1), (70, 0.1), (70.6, 0),
                           (71, 0)]), 0, 1.0)
    # a gentle warm chord when grandma says she knew we'd come
    warm = sum(np.sin(2 * np.pi * f * t) for f in (261.6, 329.6, 392.0)) * curve(
        [(0, 0), (34.5, 0), (35.5, 0.025), (39.0, 0.02), (39.6, 0), (71, 0)])
    put(warm, 0, 1.0)

    fade = curve([(0, 1), (70.3, 1), (70.5, 0), (71, 0)])
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
