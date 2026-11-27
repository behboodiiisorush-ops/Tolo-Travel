"""Synthesised sound effects for «هشدار» (no voices) -> out/bird_sfx.wav (film + question card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402
from captions import END  # noqa: E402

TOTAL = END + 4.0
# flights of the bird (same as PLAN in scene.py): (t0, t1, hover)
FLIGHTS = [(5.8, 8.8, 0), (13.9, 17.4, 0), (22.6, 25.6, 0), (27.0, 27.7, 0), (33.0, 33.7, 0), (41.0, 41.7, 0),
           (49.0, 49.8, 0), (49.8, 52.6, 1), (52.6, 54.0, 0)]


def flap(size=1.0):
    """One wing beat: a soft feathery whump."""
    n = int(0.11 * S.SR)
    t = S.tt(n)
    return S.norm(S.band(S.noise(n), 150, 1800) * np.sin(np.pi * t / t[-1]) ** 2) * size


def tweet(t0, gain=0.5, pan=0.0, notes=3):
    for k in range(notes):
        S.chirp(t0 + k * 0.13, gain, pan)


def buzzer(length=1.4):
    n = int(length * S.SR)
    t = S.tt(n)
    x = np.sign(np.sin(2 * np.pi * 440 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 220 * t)) * 0.3
    return S.norm(S.band(x, 300, 3000)) * S.env(n, 0.01, 0.05)


def bang(size=1.0):
    """A fist on the heavy entrance door, heard from above."""
    n = int(0.5 * S.SR)
    t = S.tt(n)
    x = np.sin(2 * np.pi * 75 * t) * np.exp(-t * 16) + 0.6 * S.band(S.noise(n), 80, 1500) * np.exp(-t * 30)
    return S.norm(x) * size


def scream(length=1.2, f0=520):
    n = int(length * S.SR)
    t = S.tt(n)
    f = f0 * (1 + 0.25 * np.sin(np.pi * t / length)) * (1 + 0.03 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(f) / S.SR
    x = sum(np.sin(k * ph) / k for k in range(1, 6)) + 0.3 * S.noise(n)
    return S.norm(S.band(x, 300, 5000)) * S.env(n, 0.05, 0.4)


def build():
    n = S.N
    t = S.tt(n)
    city = S.band(S.noise(n), 50, 600) * 0.05                          # far traffic hum
    S.L += city
    S.R += city
    for k in np.arange(0.5, END, 2.3):                                  # other birds around
        tweet(k + S.rng.uniform(0, 1.2), 0.12, S.rng.uniform(-0.9, 0.9), int(S.rng.integers(2, 5)))
    tweet(0.3, 0.45, 0.0, 4)                                           # our sparrow
    tweet(9.2, 0.35, 0.0, 3)
    tweet(26.0, 0.35, 0.0, 2)
    for a, b, hover in FLIGHTS:                                         # wing beats + wind
        rate = 9.0 if hover else 5.0
        k = a
        while k < b:
            S.put(flap(0.9 if hover else 0.6), k, 0.5, S.rng.uniform(-0.2, 0.2))
            k += 1.0 / rate
        wn = int((b - a) * S.SR)
        S.put(S.band(S.noise(wn), 200, 2500) * S.env(wn, 0.3, 0.4) * 0.25, a, 0.6)
    for k in np.arange(9.7, 13.0, 0.45):                                # pecking the rail
        S.put(S.knock(0.15) * 0.4, k, 0.5)
    S.put(S.knock(0.3), 12.9, 0.3, -0.2)                               # Kian goes in
    S.put(S.groan(1.8, 85), 16.8, 0.5, 0.3)
    S.put(scream(1.3, 480), 18.0, 0.55, 0.4)                           # the passer-by
    S.put(S.groan(2.2, 75), 20.2, 0.5, 0.3)
    S.heartbeat(17.6, 26.0, 150, 0.3)                                   # the bird's heart
    for k in np.arange(39.2, 42.0, 0.42):                               # Rezaei bangs the entrance door
        S.put(bang(0.9), k, 0.6, 0.1)
    S.put(buzzer(1.4), 40.2, 0.45, -0.3)
    S.put(buzzer(0.8), 42.3, 0.4, -0.3)
    S.heartbeat(42.0, 61.0, 160, 0.33)
    S.put(S.groan(1.6, 90), 55.0, 0.35, 0.2)
    S.put(S.groan(3.0, 70), 56.8, 0.9, 0.0)                            # he screams up at them
    S.put(S.tone(55, 4.0, 0.25) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "bird_sfx.wav")
    S.write(p, build())
    print(p)
