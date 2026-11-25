"""Synthesised sound effects for «دیوار» (no voices) -> out/wall_sfx.wav (film + question card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S          # noqa: E402
from captions import END  # noqa: E402

TOTAL = END + 4.0


def steel(size=1.0, ring=1.0):
    """A fist / hammer on a thick steel plate: dull low thud + short metallic ring."""
    n = int(1.2 * S.SR)
    t = S.tt(n)
    thud = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 14)
    ring_ = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (5 + k * 2.5)) for k, f in enumerate((180, 287, 433, 690)))
    hit = S.band(S.noise(n), 200, 3000) * np.exp(-t * 60)
    return S.norm(thud + 0.35 * ring * ring_ + 0.5 * hit) * size


def creak(length=1.3):
    n = int(length * S.SR)
    t = S.tt(n)
    f = 300 + 120 * np.sin(2 * np.pi * 0.7 * t)
    ph = 2 * np.pi * np.cumsum(f) / S.SR
    x = np.sign(np.sin(ph)) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t))
    return S.norm(S.band(x, 300, 2500)) * S.env(n, 0.05, 0.3)


def crumble(length=1.6):
    n = int(length * S.SR)
    t = S.tt(n)
    x = S.band(S.noise(n), 80, 2500) * np.exp(-t * 2.2)
    for k in range(18):
        x += np.roll(S.knock(0.4)[:n] if len(S.knock(0.4)) >= n else np.pad(S.knock(0.4), (0, n - len(S.knock(0.4)))),
                     int(S.rng.uniform(0.05, length * 0.8) * S.SR)) * S.rng.uniform(0.2, 0.6)
    return S.norm(x)


def wall_hit(size=1.0):
    """Sledgehammer on plaster/brick."""
    n = int(0.7 * S.SR)
    t = S.tt(n)
    x = np.sin(2 * np.pi * 85 * t) * np.exp(-t * 18) + 0.8 * S.band(S.noise(n), 150, 4000) * np.exp(-t * 25)
    return S.norm(x) * size


def build():
    n = S.N
    t = S.tt(n)
    room = S.band(S.noise(n), 40, 220) * 0.04 + 0.015 * np.sin(2 * np.pi * 50 * t)
    S.L += room
    S.R += room
    S.put(S.knock(0.35), 0.6, 0.4)                       # key turns
    S.put(S.knock(0.25), 0.75, 0.3)
    S.put(creak(1.3), 2.0, 0.35, -0.2)                   # door swings in
    S.put(steel(1.0, 0.4), 2.95, 0.55)                   # ...steel: a deep dead hum
    S.put(S.tone(48, 2.5, 0.35) * S.env(int(2.5 * S.SR), 0.05, 1.5), 2.95, 0.6)
    S.heartbeat(3.4, 19.0, 92, 0.3)
    S.footsteps(5.0, 6.0, 2.0, 0.35, 0.4)
    S.put(steel(0.9), 8.45, 0.8, 0.3)                    # Kazemi punches the window steel
    k = 10.15
    while k < 12.3:                                      # mom pounds the door steel
        S.put(steel(0.55, 0.6), k, 0.6, -0.3)
        k += 0.27
    for k in (12.6, 12.95, 13.3):                        # knocking: hollow
        S.put(S.knock(0.9), k, 0.7, 0.2)
    S.put(S.scrape(0.6), 14.6, 0.25)                     # cabinet door
    S.put(S.knock(0.5), 16.2, 0.4)
    import json
    hits = json.load(open(os.path.join(HERE, "out", "hits.json")))
    for k in hits["ab"]:                                 # sledgehammer on the wall (times from the animation)
        S.put(wall_hit(0.9), k, 0.9, 0.2)
        S.put(S.scrape(0.3), k + 0.05, 0.25)
    S.put(crumble(1.8), hits["ab"][-1], 0.9)
    S.put(S.knock(1.4), 25.9, 0.7)                       # landing next door
    S.heartbeat(26.0, 41.0, 108, 0.33)
    for k in hits["bc"]:
        S.put(wall_hit(0.9), k, 0.9, -0.2)
    S.put(crumble(1.8), hits["bc"][-1], 0.9)
    tv = S.band(S.noise(int(11 * S.SR)), 2000, 6000) * 0.05
    S.put(tv, 51.0, 1.0, -0.4)
    for k in (59.6, 60.0, 60.5, 61.2):                   # lights flicker
        S.put(S.band(S.noise(int(0.18 * S.SR)), 90, 400) * 0.5, k, 0.5)
    S.heartbeat(59.0, 75.5, 120, 0.4)
    for k in (62.6, 63.0, 63.4):                         # someone knocks from the far wall
        S.put(S.knock(0.8), k, 0.75, 0.6)
    S.put(S.groan(1.6, 90), 72.6, 0.35)                  # Rezaei raises his head
    S.put(S.explosion(2.0, 0.8), END - 0.4, 0.5)
    S.put(S.tone(55, 4.0, 0.25) * S.env(int(4.0 * S.SR), 0.8, 1.5), END, 1.0)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "wall_sfx.wav")
    S.write(p, build())
    print(p)
