"""Synthesised sound effects for «آستین» (no voices) -> out/sleeve_sfx.wav (film + question card)."""
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
    t = S.tt(n)
    room = S.band(S.noise(n), 40, 200) * 0.035
    S.L += room
    S.R += room
    S.put(hum(END, 100) * 0.05, 0.0, 1.0)                # fluorescent tubes
    nr = int(5.0 * S.SR)
    S.put(S.rotor(nr, np.linspace(9.0, 7.0, nr)) * np.linspace(1, 0, nr) ** 1.5, 0.0, 0.5)   # the helicopter leaving
    for k in (8.2, 9.1, 10.2, 11.4):                      # radio static
        S.put(static(0.7), k, 0.35, 0.3)
    S.heartbeat(19.5, 30.5, 88, 0.25)
    S.put(S.tone(880, 0.05, 0.2), 24.0, 0.2)              # (a drop)
    S.heartbeat(34.5, 46.0, 104, 0.32)
    S.put(S.tone(50, 3.0, 0.3) * S.env(int(3.0 * S.SR), 0.05, 1.5), 41.2, 0.7)   # the bite: low hit
    S.put(S.scrape(0.4), 41.0, 0.2)
    S.footsteps(44.0, 45.0, 4.0, 0.3, -0.2)              # the kids step back
    S.put(S.knock(0.25), 54.2, 0.6)                       # key on the floor
    S.put(S.knock(0.15), 54.35, 0.3)
    S.footsteps(57.0, 58.8, 1.8, 0.35, 0.3)
    S.put(metal_door(0.5), 59.0, 0.4, 0.3)               # door handle
    S.put(metal_door(1.0), 61.9, 0.9, 0.3)               # door shuts
    for k in (62.4, 63.9, 65.1, 66.0, 66.6):             # flicker clicks
        S.put(S.band(S.noise(int(0.12 * S.SR)), 90, 400) * 0.4, k, 0.4)
    S.heartbeat(62.0, 67.5, 70, 0.3)
    S.put(S.groan(1.6, 80), 63.2, 0.25, 0.3)              # breathing behind the door
    S.put(growl(2.0, 70), 64.8, 0.45, 0.3)
    S.put(static(0.6, 1.0), 67.4, 0.5, -0.2)             # radio clears
    S.put(static(4.4, 0.25), 67.8, 0.25, -0.2)
    t_ = 72.6
    import random
    r = random.Random(3)
    while t_ < END:                                       # fists on the hall doors
        t_ += r.uniform(0.18, 0.34)
        S.put(metal_door(0.6), t_, 0.55, -0.6)
    S.put(growl(3.0, 60), 72.8, 0.35, -0.6)
    S.heartbeat(72.5, END, 128, 0.4)
    S.put(S.tone(55, 4.0, 0.25) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "sleeve_sfx.wav")
    S.write(p, build())
    print(p)
