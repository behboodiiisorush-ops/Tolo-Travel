"""Synthesised sound effects for «زره‌پوش» (no voices) -> out/armored_sfx.wav (film + question card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402
from captions import END  # noqa: E402

TOTAL = END + 5.6
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


def engine(length, rpm=1.0, gain=1.0):
    """diesel: low pulses (firing rate) over a rumble; rpm scales the pitch."""
    n = int(length * S.SR)
    t = S.tt(n)
    r = np.atleast_1d(rpm)
    if r.size > 1:
        r = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, r.size), r)
    f = 28 * r
    ph = 2 * np.pi * np.cumsum(f) / S.SR
    x = (np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.35 * np.sin(3 * ph)) * (0.7 + 0.3 * np.abs(np.sin(ph * 2)))
    x = x + 0.5 * S.band(S.noise(n), 60, 400)
    return S.norm(x) * S.env(n, 0.3, 0.4) * gain


def jingle(length=0.8):
    n = int(length * S.SR)
    t = S.tt(n)
    hits = np.zeros(n)
    rng = np.random.default_rng(3)
    for k in range(9):
        i = int(rng.uniform(0, 0.85) * n)
        m = min(n - i, int(0.06 * S.SR))
        hits[i:i + m] += np.sin(2 * np.pi * rng.uniform(3500, 6500) * S.tt(m)) * np.exp(-S.tt(m) * 60)
    return S.norm(hits + 0.3 * S.band(S.noise(n), 2500, 8000) * S.env(n, 0.05, 0.3))


def clang(size=1.0):
    n = int(0.7 * S.SR)
    t = S.tt(n)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((140, 9), (390, 12), (760, 16), (1230, 20)))
    return S.norm(x + 0.6 * S.band(S.noise(n), 200, 4000) * np.exp(-t * 50)) * size


def build():
    n = S.N
    room = S.band(S.noise(n), 40, 200) * 0.03
    S.put(room[:int(34.4 * S.SR)], 0.0, 1.0)                   # the hall at night
    S.put(hum(34.4, 100) * 0.03, 0.0, 1.0)
    for t_ in (3.35, 3.7, 4.05):                               # he taps on the little window
        S.put(S.knock(0.3), t_, 0.35, 0.2)
    S.heartbeat(0.0, 12.0, 80, 0.18)
    S.footsteps(12.0, 13.5, 1.8, 0.14, 0.2)                    # Kazemi to the door
    S.put(S.band(S.noise(int(0.8 * S.SR)), 2000, 7000) * S.env(int(0.8 * S.SR), 0.05, 0.3) * 0.25, 12.6, 1.0, 0.2)
    S.put(jingle(0.7), 12.7, 0.35, 0.2)                        # the keys slide out under the door
    S.put(jingle(0.5), 15.6, 0.3, 0.2)                         # he picks them up
    S.footsteps(17.4, 18.4, 2.0, 0.12, 0.2)
    for k, (t0_, t1_) in enumerate(((29.2, 33.2), (29.8, 35.0), (30.4, 35.4), (31.0, 35.8), (29.8, 35.6))):
        S.footsteps(t0_ + 0.1 * k, t1_, 1.7, 0.1, [-0.2, 0.3, -0.4, 0.4, 0.0][k])   # all of them across the hall
    S.put(metal_door(0.7), 33.75, 0.55, 0.0)                   # the push bar
    S.put(S.scrape(0.8) * 0.4, 33.9, 0.5, 0.0)                 # the exit door swings open
    out_ = S.band(S.noise(n), 150, 1200) * 0.035               # outside: wind
    i0, i1 = int(34.2 * S.SR), int(62.4 * S.SR)
    w = out_[i0:i1] * S.env(i1 - i0, 0.8, 0.5)
    S.put(w, 34.2, 1.0)
    S.footsteps(34.6, 39.6, 1.9, 0.1, 0.3)                     # Kazemi round the car
    for t_ in np.arange(37.4, 40.2, 0.42):                     # feet on the steel ramp
        S.put(clang(0.25), float(t_), 0.25, 0.1)
    S.footsteps(38.2, 43.0, 3.0, 0.18, -0.4)                   # «من» runs to the gate
    gr = S.band(S.noise(int(4.6 * S.SR)), 80, 900) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * S.tt(int(4.6 * S.SR))))
    S.put(S.norm(gr) * S.env(len(gr), 0.2, 0.3) * 0.4, 43.3, 1.0, 0.2)   # the gate rolls
    S.put(clang(0.8), 47.8, 0.5, 0.3)                          # and hits the stop
    S.put(S.band(S.noise(int(0.7 * S.SR)), 300, 2500) * S.env(int(0.7 * S.SR), 0.05, 0.1) * 0.4, 45.4, 1.0, -0.1)   # starter
    S.put(engine(11.4, 1.0, 0.45), 46.1, 1.0, -0.1)            # idling
    S.heartbeat(48.0, 57.4, 120, 0.35)
    S.footsteps(48.8, 57.3, 3.4, 0.16, 0.5)                    # the two of them, running
    S.footsteps(49.3, 55.9, 3.2, 0.2, 0.0)                     # «من» running back
    for t_ in (55.95, 56.25):
        S.put(clang(0.6), t_, 0.45, 0.0)
    whine = np.sin(2 * np.pi * np.cumsum(np.linspace(300, 520, int(0.8 * S.SR))) / S.SR) * 0.3
    S.put(whine * S.env(len(whine), 0.05, 0.1), 56.6, 0.4, 0.0)   # the ramp goes up
    S.put(clang(1.0), 57.4, 0.75, 0.0)
    for t_ in (57.6, 57.95, 58.2, 58.55):                      # fists on the shut ramp
        S.put(metal_door(0.5), t_, 0.35, 0.2)
    S.put(engine(4.0, np.array([1.0, 1.6, 2.2, 1.9]), 0.7), 57.5, 1.0, 0.0)   # it pulls away
    S.put(engine(2.6, 1.7, 0.18), 59.8, 1.0, 0.6)              # far away now (the soldier's window)
    road = engine(END - 62.4, 1.5, 0.35) * 0.8 + S.band(S.noise(int((END - 62.4) * S.SR)), 80, 600) * 0.12
    S.put(S.band(road, 30, 900), 62.4, 1.0)                    # inside on the road
    S.put(static(0.6, 0.35), 63.4, 1.0, -0.2)                  # the radio wakes up
    S.put(static(4.3, 0.12), 64.0, 1.0, -0.2)
    S.put(S.tone(55, 4.0, 0.25) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "armored_sfx.wav")
    S.write(p, build())
    print(p)
