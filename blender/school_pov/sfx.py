"""
Sound effects + ambience for «زنگ آخر» (no voices).

All synthesised with numpy (no third-party sound files). Writes out/sfx.wav (80 s, 48 kHz stereo);
post.py puts it under the video when it exists.
"""

import math
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = 80.0
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


# ---------------------------------------------------------------- more sounds

def groan(length=1.6, f0=95):
    """Zombie groan: wobbling low buzz through a throaty band."""
    n = int(length * SR)
    t = tt(n)
    f = f0 * (1 + 0.08 * np.sin(2 * np.pi * 3.3 * t) + 0.05 * rng.standard_normal() * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    x = band(saw + 0.4 * noise(n), 120, 1400)
    return norm(x) * env(n, 0.25, 0.6)


def knock(size=1.0):
    n = int(0.35 * SR)
    t = tt(n)
    thump = band(noise(n), 40, 500) * np.exp(-t * 18 / size)
    wood = sum(np.sin(2 * np.pi * f * t) for f in (180, 330, 610)) * np.exp(-t * 25)
    return norm(thump + 0.5 * wood)


def bell(length=1.2):
    """Electric school bell: bright partials with a fast hammer tremolo."""
    n = int(length * SR)
    t = tt(n)
    x = sum(np.sin(2 * np.pi * f * t) / (k + 1) for k, f in enumerate((1250, 2710, 4180, 5350)))
    x *= 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 22 * t))
    return norm(x) * env(n, 0.01, 0.15)


def scrape(length):
    n = int(length * SR)
    x = band(noise(n), 250, 2200) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * tt(n) + rng.random())))
    return norm(x) * env(n, 0.05, 0.1)


def rotor(n, rate):
    """Helicopter: chopping low noise; rate = blade pulses per second (array)."""
    ph = 2 * np.pi * np.cumsum(rate) / SR
    chop = (0.5 + 0.5 * np.cos(ph)) ** 6
    body = band(noise(n), 30, 450)
    whine = band(noise(n), 1500, 4000) * 0.15
    return norm(body * (0.3 + chop) + whine)


def chirp(t0, gain, pan):
    n = int(0.12 * SR)
    f = np.linspace(rng.uniform(3000, 4200), rng.uniform(4500, 5600), n)
    put(np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.01, 0.06), t0, gain, pan)


# ---------------------------------------------------------------- the mix

def build():
    t = tt(N)
    # hook over black: heartbeat and breath
    heartbeat(0.2, 2.6, 100, 0.55)

    # ---- house 2.4-11: TV news, steps down the stairs, the front door
    put(tone(523, 0.18, 0.12), 2.5)
    put(tone(784, 0.35, 0.12), 2.7)
    news = norm(band(noise(N), 300, 2500)) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 3.1 * t)))
    put(news * curve([(0, 0), (2.4, 0), (2.6, 0.05), (4.4, 0.04), (7.9, 0.035), (10.5, 0.03), (11, 0)]), 0, 1.0, -0.2)
    footsteps(3.1, 6.0, 2.6, 0.45)                 # wooden stairs
    footsteps(6.2, 9.4, 2.2, 0.3)
    put(norm(band(noise(int(0.1 * SR)), 200, 1500)) * env(int(0.1 * SR), 0.005, 0.08), 8.1, 0.12, -0.3)  # mug on table
    n = int(0.6 * SR)
    put(np.sin(2 * np.pi * np.cumsum(np.linspace(300, 520, n)) / SR) * band(noise(n), 200, 2000) * env(n, 0.05, 0.2),
        10.3, 0.12)                                # door creak
    put(knock(1.2), 11.0, 0.35)                    # door shuts behind me

    # ---- street 11-15: birds, steps, the army truck passing, distant siren
    for k in range(14):
        chirp(10.6 + k * 0.33 + rng.uniform(0, 0.2), 0.05, rng.uniform(-0.8, 0.8))
    footsteps(11.0, 15.0, 2.4, 0.3)
    n = int(3.0 * SR)
    eng = band(noise(n), 30, 600) + 0.6 * np.sin(2 * np.pi * np.cumsum(np.linspace(70, 55, n)) / SR)
    eng = norm(eng) * np.exp(-((tt(n) - 1.3) / 0.7) ** 2)
    put(eng, 11.1, 0.75, 0.6)
    put(siren(3.5) * 0.4, 11.5, 0.06, -0.7)

    # ---- class 15-63
    room = norm(band(noise(N), 80, 400))
    put(room * curve([(0, 0), (14.8, 0), (15, 0.03), (51, 0.03), (51.2, 0.01), (63, 0.01), (63.2, 0)]), 0, 1.0)
    put(bell(1.0), 14.7, 0.22)                     # the school bell (زنگ)
    kids = norm(band(noise(N), 300, 2000)) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 1.7 * t)))
    put(kids * curve([(0, 0), (15, 0), (15.1, 0.08), (15.6, 0.08), (16.0, 0.0), (37.5, 0), (37.8, 0.1),
                      (39, 0.06), (45, 0.06), (45.6, 0.12), (51, 0.08), (51.5, 0.02), (63, 0.02), (63.2, 0)]),
        0, 1.0, 0.1)
    for a, b in ((15.0, 15.4), (16.9, 18.6)):     # chalk
        k = a
        while k < b:
            nn = int(0.12 * SR)
            put(band(noise(nn), 2500, 9000) * env(nn, 0.01, 0.05), k, 0.06, 0.2)
            k += 0.17
    for k in range(48):                            # the clock
        put(knock(0.4) * 0.3, 15.0 + k, 0.03, -0.5)
    # phone buzz under the desk, the voice note, then the call failing
    for k in range(3):
        n = int(0.35 * SR)
        put(band(np.sign(np.sin(2 * np.pi * 160 * tt(n))), 60, 900) * env(n, 0.01, 0.05), 20.9 + k * 0.5, 0.25)
    put(tone(1000, 0.05, 0.1), 22.4)               # tap: play
    for k in range(3):
        put(tone(480, 0.3, 0.1), 25.6 + k * 0.4)   # call failed
    # loudspeaker: chime, hum, then cut off by a crash
    for k, f in enumerate((659, 523, 587, 392)):
        put(tone(f, 0.4, 0.15), 32.6 + k * 0.25)
    hum = (np.sin(2 * np.pi * 50 * t) + 0.5 * np.sin(2 * np.pi * 100 * t)) * curve(
        [(0, 0), (33.4, 0), (33.5, 0.03), (37.2, 0.03), (37.25, 0)])
    put(hum, 0, 1.0)
    put(band(noise(int(0.3 * SR)), 1000, 6000) * env(int(0.3 * SR), 0.005, 0.2), 37.15, 0.25)
    put(explosion(2.5, 1.0), 37.2, 0.55, 0.2)
    put(siren(10.0), 38.2, 0.05, -0.6)
    # yard: zombie groans, the gate rattling
    for tg in (39.5, 40.8, 42.0, 43.4, 44.2):
        put(groan(1.5, rng.uniform(80, 120)), tg, 0.18 if tg != 43.4 else 0.4, -0.6)
    gate = sum(np.sin(2 * np.pi * f * tt(int(0.25 * SR))) for f in (410, 820, 1330)) * np.exp(-tt(int(0.25 * SR)) * 14)
    k = 39.0
    while k < 51.0:
        put(norm(gate), k, 0.05, -0.7)
        k += rng.uniform(0.25, 0.6)
    put(norm(band(noise(int(1.2 * SR)), 30, 200)) * env(int(1.2 * SR), 0.01, 1.0), 43.4, 0.5)  # sting
    # the door: banging, the glass, desks scraping
    for k in range(16):
        put(knock(1.0), 44.9 + k * 0.38 + rng.uniform(0, 0.08), 0.45, 0.5)
    glass = band(noise(int(1.2 * SR)), 2500, 12000) * np.exp(-tt(int(1.2 * SR)) * 5)
    for k in range(5):
        put(glass * rng.uniform(0.4, 0.8), 45.6 + k * 0.06, 0.3, 0.5)
    for tg in (45.2, 46.6, 48.0, 49.4, 50.6):
        put(groan(1.2, rng.uniform(90, 130)), tg, 0.3, 0.5)
    put(scrape(3.0), 47.5, 0.25, 0.3)
    put(norm(band(noise(int(0.3 * SR)), 40, 300)) * env(int(0.3 * SR), 0.005, 0.2), 50.5, 0.5, 0.4)  # desk hits door
    # lights out
    n = int(0.9 * SR)
    put(np.sin(2 * np.pi * np.cumsum(np.linspace(240, 40, n)) / SR) * env(n, 0.01, 0.4), 51.0, 0.2)
    put(knock(1.5), 51.0, 0.4)
    heartbeat(51.3, 57.0, 112, 0.5)
    for tg in (52.0, 53.7, 55.8):
        put(groan(1.4, 85), tg, 0.08, 0.6)
    put(tone(480, 0.25, 0.08), 55.1)
    put(tone(480, 0.25, 0.08), 55.5)               # no signal
    # helicopter: far, then over the school, then on the roof
    rate = curve([(0, 14), (80, 14)])
    heli = rotor(N, rate)
    put(heli * curve([(0, 0), (56.5, 0), (58.5, 0.15), (60, 0.35), (63, 0.3), (66, 0.35), (69, 0.5), (75, 0.55),
                      (75.05, 0), (80, 0)]), 0, 1.0)
    # ---- stairs 63-69: running, the railing, zombies below
    footsteps(63.0, 69.0, 4.2, 0.45)
    footsteps(63.1, 69.0, 3.6, 0.2, 0.3)
    for k in range(4):
        put(norm(gate) * 0.7, 63.6 + k * 1.3, 0.12, -0.6)
    for tg in (63.4, 64.6, 66.0, 67.5):
        put(groan(1.4, rng.uniform(90, 120)), tg, 0.3, -0.6)
    # ---- roof 69-75: wind, the reveal
    wind = norm(band(noise(N), 150, 1500)) * curve([(0, 0), (69, 0), (69.5, 0.12), (75, 0.12), (75.05, 0)])
    put(wind, 0, 1.0, 0.2)
    footsteps(69.0, 70.6, 3.5, 0.3)
    put(explosion(3.0, 1.4), 72.95, 0.7)          # mask off: the sting
    put(groan(1.8, 75), 73.2, 0.5)
    heartbeat(73.0, 75.0, 140, 0.6)
    # ---- the question card 75-80: the last bell, then silence
    put(tone(200, 0.12, 0.4) * np.exp(-tt(int(0.12 * SR)) * 20), 75.05, 1.0)
    put(bell(1.6), 75.3, 0.18)
    heartbeat(76.5, 79.5, 80, 0.4)

    # tension pad
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.04), (2.4, 0.03), (3, 0.0), (21, 0.0), (23, 0.03), (33, 0.04), (39, 0.07),
                           (51, 0.08), (57, 0.09), (63, 0.08), (73, 0.1), (75, 0.06), (79.5, 0.06), (80, 0)]), 0, 1.0)

    fade = curve([(0, 1), (79.5, 1), (80, 0)])
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
