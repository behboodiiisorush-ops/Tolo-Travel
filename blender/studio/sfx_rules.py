"""Synthesised sound effects for «قانون‌ها» (no voices) -> out/rules_sfx.wav (same timeline as the film + card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402  (helpers + the stereo mix buffers)
from captions import LINES, END  # noqa: E402

TOTAL = END + 4.0


def buzz(n_pulses=2):
    out = []
    for _ in range(n_pulses):
        n = int(0.28 * S.SR)
        t = S.tt(n)
        x = np.sin(2 * np.pi * 165 * t) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 33 * t)))
        out += [x * S.env(n, 0.01, 0.05), np.zeros(int(0.12 * S.SR))]
    return np.concatenate(out)


def metal(size=1.0):
    n = int(0.6 * S.SR)
    t = S.tt(n)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (6 + k * 3)) for k, f in enumerate((310, 523, 911, 1460)))
    return S.norm(x + 0.6 * S.band(S.noise(n), 300, 4000) * np.exp(-t * 30)) * size


def glitch(length):
    n = int(length * S.SR)
    x = S.band(S.noise(n), 800, 9000)
    gate = np.repeat(S.rng.random(int(length * 40) + 1) > 0.45, int(S.SR / 40) + 1)[:n]
    return S.norm(x * gate + 0.4 * np.sign(np.sin(2 * np.pi * 220 * S.tt(n))) * gate)


def build():
    n = S.N
    t = S.tt(n)
    room = S.band(S.noise(n), 40, 260) * 0.05 + 0.02 * np.sin(2 * np.pi * 50 * t)
    S.L += room
    S.R += room
    S.put(S.explosion(0.9, 0.35), 3.0, 0.9, 0.5)                    # front door kicked in
    S.put(S.knock(1.6), 3.02, 0.9, 0.5)
    S.footsteps(3.1, 4.3, 2.2, 0.55, 0.4)
    S.footsteps(3.3, 6.4, 2.2, 0.35, 0.6)
    S.heartbeat(6.3, 28.0, 96, 0.35)
    S.heartbeat(28.0, 40.0, 118, 0.45)
    S.heartbeat(50.0, 57.6, 110, 0.35)
    for a, b, who, _ in LINES:
        if who == "rule":
            S.put(buzz(), a - 0.45, 0.5)
    S.footsteps(17.0, 18.6, 2.0, 0.6, 0.3)
    S.footsteps(26.4, 29.2, 2.0, 0.5, 0.2)
    k = 30.9
    while k < 39.9:                                                  # crawling: cloth + palms on the boards
        S.put(S.scrape(0.25), k, 0.12, -0.2)
        S.put(S.knock(0.4), k + 0.1, 0.12, 0.2)
        k += 0.42
    S.put(S.knock(0.8), 41.9, 0.6)                                  # bedroom door shut
    S.put(metal(0.7), 54.0, 0.6)                                     # vent grille swings down
    S.put(S.scrape(2.0), 54.1, 0.3)
    k = 57.6
    while k < 61.0:                                                  # inside the duct
        S.put(metal(0.25), k, 0.35, S.rng.uniform(-0.4, 0.4))
        k += 0.45
    S.put(S.knock(1.4), 61.1, 0.9)                                   # landing
    S.put(S.siren(9.0), 66.6, 0.25, -0.4)
    S.put(S.siren(9.0), 67.4, 0.2, 0.5)
    S.put(glitch(2.2), 70.6, 0.25)
    S.put(S.explosion(2.0, 0.8), END - 0.4, 0.5)                    # low hit on the cut to black
    S.put(S.tone(55, 4.0, 0.25) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "rules_sfx.wav")
    S.write(p, build())
    print(p)
