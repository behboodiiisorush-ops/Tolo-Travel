"""Synthesised sound effects for «سایه‌ی دانیال» (no voices) -> out/sayeh_sfx.wav (film + question card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402
from lines import END  # noqa: E402

TOTAL = END + 4.0


def buzz(length):
    """Electric hum + crackle of a failing light."""
    n = int(length * S.SR)
    t = S.tt(n)
    hum = np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t)
    crack = S.band(S.noise(n), 1500, 7000) * (S.rng.random(n) < 0.004) * 8
    return S.norm(hum * 0.4 + crack)


def drone(length, f=48):
    n = int(length * S.SR)
    t = S.tt(n)
    x = sum(np.sin(2 * np.pi * f * k * t + k) / k for k in (1, 1.5, 2.02, 3.01))
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t)
    return S.norm(x + 0.3 * S.band(S.noise(n), 40, 160)) * S.env(n, 1.5, 1.5)


def whoosh(length=1.2):
    n = int(length * S.SR)
    t = S.tt(n)
    x = S.band(S.noise(n), 300, 3000) * np.sin(np.pi * t / length) ** 2
    return S.norm(x)


def build():
    n = S.N
    t = S.tt(n)
    room = S.band(S.noise(n), 40, 220) * 0.03 + 0.01 * np.sin(2 * np.pi * 50 * t)
    S.L += room
    S.R += room
    S.footsteps(0.6, 3.2, 2.0, 0.35, 0.5)              # Daniel comes in from the right
    for k in (5.0, 5.4, 5.9, 6.3, 6.8, 7.1):           # the lights fail
        S.put(buzz(0.25), k, 0.45, 0.1)
    S.put(S.knock(0.6), 7.2, 0.5)                      # ...and click off
    S.put(drone(24, 46), 7.4, 0.45)
    S.heartbeat(9.0, 26.5, 96, 0.3)
    S.put(whoosh(1.6), 9.0, 0.35, 0.0)                 # the Shadow appears
    S.put(S.groan(1.8, 70), 13.3, 0.25)
    S.put(S.tone(880, 1.2, 0.05) * S.env(int(1.2 * S.SR), 0.4, 0.6), 17.4, 0.2)   # Daniel looks down: a thin ring
    S.footsteps(23.0, 24.0, 2.0, 0.25, -0.1)           # the Shadow walks up
    S.put(whoosh(0.8), 26.6, 0.5)
    S.put(S.explosion(1.2, 0.4), 27.0, 0.45)           # flash
    for k, fq in enumerate((1568, 2093, 2637)):          # a soft chime
        S.put(S.tone(fq, 2.0, 0.08) * np.exp(-S.tt(int(2.0 * S.SR)) * 2.5), 27.1 + 0.08 * k, 0.4)
    S.put(S.tone(392, 3.5, 0.12) * S.env(int(3.5 * S.SR), 0.3, 1.5), 28.0, 0.5)   # warm chord at the end
    S.put(S.tone(494, 3.5, 0.1) * S.env(int(3.5 * S.SR), 0.3, 1.5), 28.0, 0.5)
    S.put(S.tone(587, 3.5, 0.08) * S.env(int(3.5 * S.SR), 0.3, 1.5), 28.0, 0.5)
    S.put(S.tone(55, 4.0, 0.2) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "sayeh_sfx.wav")
    S.write(p, build())
    print(p)
