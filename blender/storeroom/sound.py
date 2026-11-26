"""Synthesised sound effects for «انباری» (no voices) -> out/storeroom_sfx.wav (film + question card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402
from captions import END  # noqa: E402

TOTAL = END + 4.0
S.DUR = TOTAL + 1.0                      # the shared mixer is 80 s long: make room
S.N = int(S.SR * S.DUR)
S.L = np.zeros(S.N)
S.R = np.zeros(S.N)


def static(length, gain=1.0):
    """Radio static: band-passed noise with a choppy envelope."""
    n = int(length * S.SR)
    t = S.tt(n)
    x = S.band(S.noise(n), 700, 5000) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 7.3 * t + 3 * np.sin(2 * np.pi * 1.1 * t))))
    return S.norm(x) * S.env(n, 0.02, 0.1) * gain


def hum(length, f=100):
    n = int(length * S.SR)
    t = S.tt(n)
    return S.norm(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.05 * S.noise(n)) * S.env(n, 0.3, 0.3)


def metal_door(slam=1.0):
    n = int(1.0 * S.SR)
    t = S.tt(n)
    x = np.sin(2 * np.pi * 62 * t) * np.exp(-t * 10) + 0.4 * sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
                                                              for f in (210, 330, 517))
    return S.norm(x + 0.5 * S.band(S.noise(n), 300, 3000) * np.exp(-t * 40)) * slam


def growl(length=1.6, f0=70):
    n = int(length * S.SR)
    t = S.tt(n)
    f = f0 + 15 * np.sin(2 * np.pi * 3 * t) + 8 * S.noise(n) * 0.2
    ph = 2 * np.pi * np.cumsum(f) / S.SR
    x = np.sign(np.sin(ph)) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 11 * t)))
    return S.norm(S.band(x, 60, 1200) + 0.4 * S.band(S.noise(n), 200, 900)) * S.env(n, 0.2, 0.4)


def build():
    n = S.N
    room = S.band(S.noise(n), 40, 200) * 0.03            # the empty hall at night
    S.L += room
    S.R += room
    S.put(hum(END, 100) * 0.03, 0.0, 1.0)                # the two tubes still on
    for t_ in (1.2, 1.65, 3.4, 3.85, 5.3, 5.72, 6.14, 6.56, 7.0, 7.42):   # tap, tap on the storeroom door
        S.put(S.knock(0.35), t_, 0.5, 0.3)
    S.footsteps(10.5, 16.0, 1.6, 0.18, 0.2)               # me across the hall
    S.heartbeat(10.5, 30.2, 84, 0.25)
    S.put(S.tone(60, 1.2, 0.3) * S.env(int(1.2 * S.SR), 0.02, 0.8), 16.8, 0.6)   # the face in the window
    S.footsteps(17.2, 17.9, 3.0, 0.25, 0.2)               # I step back
    S.footsteps(20.5, 25.5, 1.7, 0.14, 0.35)              # Mahsa comes over
    S.heartbeat(30.2, 41.0, 96, 0.3)
    S.put(S.groan(1.2, 70), 36.8, 0.15, 0.3)              # his breath goes rough
    for t_ in (44.5, 45.3, 46.6, 47.4, 70.0, 70.9, 72.2, 73.1):   # someone leaning on the hall doors
        S.put(metal_door(0.18), t_, 0.25, -0.6)
    S.footsteps(49.5, 55.0, 1.8, 0.16, -0.3)              # Kian to the doors
    k = 55.1
    import random
    r = random.Random(5)
    while k < 58.3:                                       # the chain rattles
        S.put(S.band(S.noise(int(0.12 * S.SR)), 1500, 6000) * 0.5, k, 0.35, -0.6)
        k += r.uniform(0.25, 0.45)
    S.put(metal_door(0.9), 53.6, 0.6, 0.3)               # his fists on the storeroom door
    S.put(metal_door(1.0), 54.0, 0.7, 0.3)
    S.put(metal_door(0.8), 54.6, 0.6, 0.3)
    S.put(metal_door(1.0), 55.1, 0.7, 0.3)
    S.put(growl(2.4, 75), 55.6, 0.35, 0.3)
    S.footsteps(55.5, 57.9, 2.0, 0.2, -0.4)               # Arian
    S.heartbeat(56.0, 67.5, 112, 0.35)
    S.footsteps(62.5, 64.2, 1.7, 0.2, 0.0)                # Kazemi
    for k in (67.6, 68.1, 68.5, 69.2):                    # the tube near the storeroom flickers
        S.put(S.band(S.noise(int(0.12 * S.SR)), 90, 400) * 0.4, k, 0.4, 0.3)
    S.heartbeat(70.0, END, 128, 0.4)
    S.put(S.tone(55, 4.0, 0.25) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "storeroom_sfx.wav")
    S.write(p, build())
    print(p)
