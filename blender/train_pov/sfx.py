"""
Sound effects + ambience for «واگن آخر» (no voices — those are recorded by hand).

Everything is synthesised with numpy, so there are no third-party sound files.
Writes out/sfx.wav (70 s, 48 kHz stereo).  mux.sh puts it under the video.
"""

import math
import os
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUR = 70.0
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

def build():
    t = tt(N)
    # train speed (m/s): accelerating out of the station, cruising, braking at the border
    speed = np.interp(t, [0, 20, 22, 55.5, 57.5, 70], [2.6, 5.0, 8.0, 8.0, 0.0, 0.0])
    inside = curve([(0, 0), (10.3, 0), (10.6, 1), (70, 1)])
    in_car = curve([(0, 0), (19.8, 0), (20.4, 1), (70, 1)])

    # rumble + clacks (louder outside on the platform)
    rumble = band(noise(N), 25, 220)
    rumble = norm(rumble) * (0.12 + 0.02 * speed) * (speed > 0.05)
    clacks = clack_track(speed) * (0.25 + 0.15 * (1 - in_car))
    for x in (rumble, clacks):
        put(x * curve([(0, 1), (57.5, 1), (58.5, 0), (70, 0)]), 0, 1.0)

    # wind while running on the platform, then rushing air at the door
    wind = norm(band(noise(N), 200, 2500)) * curve([(0, 0.1), (9.5, 0.18), (10.4, 0.05), (13.8, 0.06),
                                                     (14.5, 0.16), (17.9, 0.16), (18.5, 0.02), (20, 0)])
    put(wind, 0, 1.0, -0.2)

    # station crowd + panic, muffled interior murmur in the car
    crowd = norm(band(noise(N), 250, 1800))
    crowd *= (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.7 * t)))
    put(crowd * curve([(0, 0.0), (0.4, 0.12), (13.5, 0.1), (20, 0.04), (20.5, 0.04), (44, 0.035),
                       (44.3, 0.08), (50, 0.06), (51, 0.02), (70, 0.02)]), 0, 1.0, 0.3)

    # station tannoy chime
    for k, f in enumerate((660, 550, 440)):
        put(tone(f, 0.35, 0.18), 1.2 + k * 0.32)

    # heartbeat & breathing in the hook
    heartbeat(0.0, 3.2, 110, 0.6)
    breath = band(noise(int(0.5 * SR)), 300, 3000) * env(int(0.5 * SR), 0.15, 0.3)
    for k in range(5):
        put(breath, 0.2 + k * 0.62, 0.12)

    footsteps(0.0, 9.6, 3.2, 0.35, -0.1)       # our running steps
    footsteps(0.15, 9.6, 2.9, 0.15, 0.4)       # mum
    footsteps(20.0, 23.2, 2.2, 0.25)           # walking down the aisle
    footsteps(44.1, 44.6, 4.0, 0.25, 0.3)      # Rahim running in
    footsteps(46.0, 46.6, 4.0, 0.2, -0.3)
    footsteps(50.6, 51.4, 3.2, 0.22)

    # whistles
    put(whistle(1.8), 3.3, 0.35, -0.4)
    put(whistle(1.2), 15.8, 0.25, -0.6)
    put(whistle(1.0), 50.6, 0.12, 0.0)
    put(whistle(1.6), 65.4, 0.3, 0.0)

    # explosions
    put(explosion(3.0, 1.0), 4.25, 0.55, 0.6)
    put(explosion(3.2, 1.2), 7.85, 0.65, 0.5)
    put(explosion(2.5, 0.8), 16.35, 0.4, 0.7)
    put(explosion(3.0, 1.0), 28.4, 0.45, -0.7)
    put(explosion(4.0, 1.6), 46.7, 1.0, -0.4)
    glass = band(noise(int(1.2 * SR)), 2500, 12000) * np.exp(-tt(int(1.2 * SR)) * 5)
    for k in range(6):
        put(glass * rng.uniform(0.3, 0.7), 46.8 + k * 0.07, 0.25, rng.uniform(-0.8, 0.2))

    # the jump: metal thud on landing
    thud = band(noise(int(0.5 * SR)), 40, 900) * np.exp(-tt(int(0.5 * SR)) * 12)
    clang = sum(np.sin(2 * np.pi * f * tt(int(0.8 * SR))) for f in (310, 527, 893)) * np.exp(
        -tt(int(0.8 * SR)) * 7)
    put(norm(thud), 10.4, 0.8)
    put(norm(clang), 10.42, 0.2)
    put(norm(thud) * 0.6, 12.6, 0.4)
    put(norm(thud) * 0.6, 13.6, 0.4)

    # phone: ringing tone, then "unavailable" beeps; a message ding at the border
    for k in range(3):
        put(tone(425, 1.0, 0.09), 32.0 + k * 1.1)
    for k in range(4):
        put(tone(950, 0.33, 0.07), 33.7 + k * 0.36)
        put(tone(1400, 0.33, 0.05), 33.82 + k * 0.36)
    for k in range(5):
        put(tone(425, 0.25, 0.08), 36.6 + k * 0.5)
    put(tone(1318, 0.15, 0.25), 60.0)
    put(tone(1760, 0.25, 0.22), 60.13)
    # biscuit crunch, apple thunk
    put(band(noise(int(0.25 * SR)), 1500, 8000) * env(int(0.25 * SR), 0.005, 0.15), 39.7, 0.15)
    put(norm(band(noise(int(0.15 * SR)), 80, 600)) * env(int(0.15 * SR), 0.002, 0.1), 42.6, 0.4)

    # air raid
    put(siren(6.2), 44.0, 0.22)
    put(jet(1.6), 43.9, 0.9, -0.8)
    alarm_beep = np.concatenate([tone(880, 0.16, 0.12), np.zeros(int(0.17 * SR))])
    for k in range(17):
        put(alarm_beep * 0.5, 44.2 + k * 0.333)

    # radio static under the radio line
    static = band(noise(int(1.8 * SR)), 800, 6000) * (0.5 + 0.5 * (rng.random(int(1.8 * SR)) > 0.6))
    put(static * env(int(1.8 * SR), 0.05, 0.2), 51.5, 0.12, 0.3)
    put(band(noise(int(0.12 * SR)), 1000, 5000), 51.45, 0.2, 0.3)

    # heartbeat building towards the border, brakes, loudspeaker hum, dog barks
    heartbeat(53.0, 57.0, 125, 0.45)
    n = int(2.2 * SR)
    sq = np.sin(2 * np.pi * np.cumsum(np.linspace(3100, 2500, n)) / SR) * env(n, 0.3, 0.6)
    put(sq + 0.3 * band(noise(n), 2000, 7000) * env(n, 0.3, 0.6), 55.5, 0.12)
    put(norm(band(noise(int(0.4 * SR)), 50, 400)) * env(int(0.4 * SR), 0.01, 0.3), 57.4, 0.5)
    hiss = band(noise(int(1.5 * SR)), 2000, 9000) * env(int(1.5 * SR), 0.02, 1.0)
    put(hiss, 57.6, 0.15, -0.3)
    for tb in (57.8, 58.1, 61.4):
        nb = int(0.18 * SR)
        f = np.linspace(520, 300, nb)
        bark = np.sin(2 * np.pi * np.cumsum(f) / SR) * band(noise(nb), 300, 2500) * env(nb, 0.01, 0.1)
        put(norm(bark), tb, 0.18, -0.8)

    # final card: heartbeat, then sudden silence
    heartbeat(65.0, 69.0, 95, 0.55)
    put(tone(200, 0.12, 0.4) * np.exp(-tt(int(0.12 * SR)) * 20), 65.05, 1.0)  # UI thump

    # tension pad: low minor drone that swells with the story
    pad = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate((55, 65.4, 82.4, 110)))
    pad *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    put(norm(pad) * curve([(0, 0.0), (2, 0.05), (20, 0.04), (26, 0.06), (32, 0.05), (44, 0.08), (50, 0.04),
                           (55, 0.09), (65, 0.1), (69, 0.1), (69.6, 0), (70, 0)]), 0, 1.0)

    # hard cut to silence at the very end
    fade = curve([(0, 1), (69.3, 1), (69.5, 0), (70, 0)])
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
