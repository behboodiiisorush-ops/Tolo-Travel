"""Synthesised sound effects for «سال ۱۵۰۰» (no voices) -> out/year1500_sfx.wav (film + question card)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
sys.path.insert(0, HERE)
import sfx as S                                     # noqa: E402
from captions import END, FLASHBACK, FALL, WAKE     # noqa: E402
import screen_frames as SF                          # noqa: E402

TOTAL = END + 4.0
FB0, FB1 = FLASHBACK


def span(t0, t1):
    return int(t0 * S.SR), int(t1 * S.SR)


def wind(length, gain):
    n = int(length * S.SR)
    t = S.tt(n)
    x = S.band(S.noise(n), 150, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.037 * t + 1))
    return S.norm(x) * gain


def tinkle(size=1.0):
    """Small glass pieces: a few short high pings."""
    n = int(0.6 * S.SR)
    t = S.tt(n)
    x = np.zeros(n)
    for k in range(5):
        f = S.rng.uniform(2500, 6000)
        d = int(S.rng.uniform(0, 0.25) * S.SR)
        x[d:] += np.sin(2 * np.pi * f * t[:n - d]) * np.exp(-t[:n - d] * 30) * S.rng.uniform(0.3, 1)
    return S.norm(x) * size


def shatter(length=2.0):
    n = int(length * S.SR)
    t = S.tt(n)
    x = S.band(S.noise(n), 1500, 9000) * np.exp(-t * 3)
    for k in range(25):
        p = tinkle(1.0)
        d = int(S.rng.uniform(0, length * 0.8) * S.SR)
        x[d:d + len(p)] += p[:n - d] * S.rng.uniform(0.2, 0.7)
    return S.norm(x)


def static(length, level):
    """Screen crackle: hiss + random pops, shaped by the screen brightness."""
    n = int(length * S.SR)
    x = S.band(S.noise(n), 1500, 8000) * 0.5
    pops = (S.rng.random(n) < 0.0008).astype(float) * S.rng.uniform(-1, 1, n)
    x += S.band(pops, 200, 6000) * 6
    return S.norm(x) * level


def crowd(length, gain):
    n = int(length * S.SR)
    t = S.tt(n)
    x = np.zeros(n)
    for k in range(8):                              # murmur: band noise with syllable-like wobble
        f = S.rng.uniform(2.5, 5.0)
        x += S.band(S.noise(n), 250, 1600) * (0.5 + 0.5 * np.sin(2 * np.pi * f * t + k)) ** 2
    return S.norm(x) * gain


def build():
    n = S.N
    t = S.tt(n)
    amb = wind(TOTAL, 0.12)                          # the empty city: wind all through the present
    a, b = span(FB0, FB1)
    amb[a:b] *= 0.15
    S.L[:len(amb)] += amb
    S.R[:len(amb)] += np.roll(amb, 900)
    drone = S.tone(55, TOTAL, 0.05) * S.env(int(TOTAL * S.SR), 2.0, 2.0)
    S.L[:len(drone)] += drone
    S.R[:len(drone)] += drone
    for k in (1.5, 4.2, 7.8):                        # bits of glass falling somewhere
        S.put(tinkle(0.25), k, 0.3, S.rng.uniform(-0.7, 0.7))
    # flashback: crowd, footsteps, a soft hum of the new city
    S.put(crowd(FALL - FB0, 0.22), FB0, 0.8)
    S.put(S.tone(220, FALL - FB0, 0.04) * S.env(int((FALL - FB0) * S.SR), 0.5, 0.3), FB0, 0.5)
    S.footsteps(FB0, FALL, 1.9, 0.3, 0.0)
    # the fall
    S.put(S.tone(40, 1.2, 0.5) * S.env(int(1.2 * S.SR), 0.6, 0.2), FALL - 0.4, 0.6)     # a deep rising hum
    S.put(S.explosion(3.0, 1.0), FALL + 0.4, 0.9)
    S.put(shatter(2.5), FALL + 0.7, 0.7, -0.3)
    S.put(shatter(2.0), FALL + 1.3, 0.6, 0.4)
    S.put(static(3.5, 0.3), FALL, 0.4, 0.5)
    S.heartbeat(FALL, FB1, 130, 0.4)
    S.put(S.tone(3000, 2.5, 0.08) * S.env(int(2.5 * S.SR), 0.05, 1.5), FB1 - 0.3, 0.5)   # ringing in the ears
    # waking up
    S.put(S.tone(2800, 3.0, 0.05) * S.env(int(3.0 * S.SR), 0.1, 2.5), WAKE, 0.4)
    S.put(S.scrape(0.5), WAKE + 2.6, 0.25, 0.3)              # Kian gets up from the glass
    S.put(tinkle(0.5), WAKE + 3.0, 0.4, 0.3)
    S.put(S.scrape(0.5), WAKE + 4.6, 0.25, -0.2)             # I sit up
    S.put(tinkle(0.4), WAKE + 4.9, 0.35, -0.2)
    # Kian shouts; the echo comes back from the towers (handled by the voice; here: a flock of birds flies off)
    for k in range(10):
        S.put(S.band(S.noise(int(0.08 * S.SR)), 1500, 4000) * 0.4, 28.0 + k * 0.09, 0.3, S.rng.uniform(-0.8, 0.8))
    # the screen
    f_step = 1.0 / 24
    k = SF.ON0
    while k < SF.OFF:
        lvl = SF.brightness(k)
        if not (SF.PIC0 <= k < SF.PIC1):
            S.put(static(f_step * 1.2, 0.35 * (0.3 + lvl)), k, 0.6, 0.15)
        else:
            S.put(static(f_step * 1.2, 0.06), k, 0.6, 0.15)
        k += f_step
    S.put(S.tone(60, SF.PIC1 - SF.PIC0, 0.12) * S.env(int((SF.PIC1 - SF.PIC0) * S.SR), 0.3, 0.3), SF.PIC0, 0.4)
    S.footsteps(31.0, 34.4, 1.7, 0.25, 0.0)            # we walk towards the screen
    S.heartbeat(43.5, 49.0, 66, 0.22)                 # Kian's tear
    # walking off
    S.footsteps(54.2, END, 1.75, 0.3, -0.1)
    S.footsteps(54.5, END, 1.85, 0.22, 0.15)
    S.put(S.tone(110, TOTAL - 58, 0.08) * S.env(int((TOTAL - 58) * S.SR), 4.0, 3.0), 58.0, 0.6)
    end = int(TOTAL * S.SR)
    out = np.stack([S.L[:end], S.R[:end]], axis=1)
    out /= max(1e-9, np.max(np.abs(out))) / 0.89
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "year1500_sfx.wav")
    S.write(p, build())
    print(p)
