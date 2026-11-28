"""Synthesised sound effects for «قانون‌ها — قسمت دوم» (no voices) -> out/rules2_sfx.wav (film + question card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402
from captions import END  # noqa: E402

TOTAL = END + 4.0


def buzz(length=0.9):
    """Phone vibrating twice."""
    n = int(length * S.SR)
    t = S.tt(n)
    x = np.sign(np.sin(2 * np.pi * 170 * t)) * 0.4 + S.band(S.noise(n), 100, 600) * 0.3
    gate = ((t % 0.45) < 0.28).astype(float)
    return S.norm(S.band(x, 90, 900)) * gate * S.env(n, 0.01, 0.05)


def ping():
    n = int(0.6 * S.SR)
    t = S.tt(n)
    return S.norm(np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 9) + 0.5 * np.sin(2 * np.pi * 1980 * t) * np.exp(-t * 12))


def megaphone(t0, t1):
    """Distorted voice-like blur through a loudspeaker (the words are the user's / ElevenLabs voice)."""
    n = int((t1 - t0) * S.SR)
    t = S.tt(n)
    x = S.band(S.noise(n), 600, 2500) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)) * 0.15
    S.put(x * S.env(n, 0.05, 0.2), t0, 0.5, -0.3)


def bang(size=1.0):
    n = int(0.6 * S.SR)
    t = S.tt(n)
    x = np.sin(2 * np.pi * 75 * t) * np.exp(-t * 16) + 0.7 * S.band(S.noise(n), 120, 2500) * np.exp(-t * 30)
    return S.norm(x) * size


def creak(length=1.3):
    n = int(length * S.SR)
    t = S.tt(n)
    f = 300 + 120 * np.sin(2 * np.pi * 0.7 * t)
    ph = 2 * np.pi * np.cumsum(f) / S.SR
    x = np.sign(np.sin(ph)) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t))
    return S.norm(S.band(x, 300, 2500)) * S.env(n, 0.05, 0.3)


def crickets(t0, t1, gain):
    n = int((t1 - t0) * S.SR)
    t = S.tt(n)
    chirp = np.sin(2 * np.pi * 4300 * t) * ((t * 18) % 1 < 0.35) * ((t % 1.1) < 0.6)
    S.put(chirp * gain * S.env(n, 1.0, 1.0), t0, 1.0, 0.5)
    S.put(np.roll(chirp, 7000) * gain * 0.7 * S.env(n, 1.0, 1.0), t0, 1.0, -0.6)


def build():
    n = S.N
    t = S.tt(n)
    room = S.band(S.noise(n), 40, 200) * 0.03
    S.L += room
    S.R += room
    siren = S.siren(43.0)                                # wailing outside while we are in the house
    S.put(siren * 0.12 * S.env(len(siren), 1.0, 2.0), 0.0, 1.0, -0.2)
    megaphone(0.8, 3.8)
    S.heartbeat(8.5, 18.0, 96, 0.22)
    S.put(buzz(), 18.9, 0.7)                            # rule 6 arrives
    S.put(ping(), 19.1, 0.25)
    S.put(S.scrape(0.4), 24.8, 0.25)                     # Nina gets up from the sofa
    S.heartbeat(24.0, 33.0, 110, 0.25)
    k = 33.0
    while k < 37.9:                                      # fists on the front door
        S.put(bang(0.85), k, 0.85, -0.25)
        k += 0.27 if int((k - 33.0) / 1.2) % 2 == 0 else 0.55
    S.put(S.knock(0.5), 39.3, 0.5, 0.3)                  # back door handle
    S.put(creak(1.4), 39.6, 0.5, 0.3)
    S.footsteps(41.0, 43.0, 3.0, 0.3, 0.2)
    crickets(43.0, 55.0, 0.04)
    S.footsteps(43.0, 50.0, 3.2, 0.22, 0.0)              # on the grass
    S.put(S.knock(0.4), 51.0, 0.4, 0.2)                  # shed door
    S.put(creak(1.6), 51.2, 0.55, 0.2)
    S.footsteps(52.6, 55.0, 3.0, 0.2, 0.0)
    crickets(55.0, END, 0.015)
    S.heartbeat(55.0, 62.0, 88, 0.2)
    S.put(buzz(), 61.9, 0.7)                            # rule 7 arrives
    S.put(ping(), 62.1, 0.25)
    S.heartbeat(62.0, END, 128, 0.42)
    for k2 in [60 + 0.6 * i for i in range(27)]:        # the hidden camera ticks with its blinking light
        if 68.0 < k2 < END:
            S.put(S.knock(0.12), k2, 0.12, -0.6)
    S.put(S.tone(52, 6.0, 0.3) * S.env(int(6.0 * S.SR), 3.0, 1.0), 69.5, 0.9)   # a low drone as we turn
    S.put(S.groan(1.2, 80), 73.6, 0.25)                  # a breath behind us
    S.put(S.explosion(1.6, 0.6), END - 0.35, 0.5)        # hit on the cut to black
    S.put(S.tone(55, 4.0, 0.25) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "rules2_sfx.wav")
    S.write(p, build())
    print(p)
