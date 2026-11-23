"""Sound + final video for the 10 s zombie test.

Reuses the synthesis helpers from ../school_pov/sfx.py with a 10 s buffer,
then upscales the 576x1024 frames to 1080x1920 with light grain and vignette,
cuts to black at 9.7 s and muxes the sound -> out/zombie_test.mp4
"""
import os, sys, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "school_pov"))
import sfx as S

DUR = 10.0
S.N = N = int(S.SR * DUR)
S.L = np.zeros(N)
S.R = np.zeros(N)
SR = S.SR
t = S.tt(N)
put, band, noise, env, norm = S.put, S.band, S.noise, S.env, S.norm
BLACK = 9.7


def auto(points):
    ts, vs = zip(*points)
    return np.interp(t, ts, vs)


def crackle(t0, t1, gain, seed):
    r = np.random.default_rng(seed)
    x = t0
    while x < t1:
        n = int(r.uniform(0.02, 0.09) * SR)
        put(band(noise(n), 1500, 9000) * env(n, 0.002, 0.01), x, gain * r.uniform(0.4, 1.0), 0.1)
        x += r.uniform(0.04, 0.2)


# fluorescent hum + room tone
hum = sum(np.sin(2 * np.pi * f * t) / k for k, f in ((1, 120), (2, 240), (3, 360)))
hum += 0.3 * band(noise(N), 3000, 7000)
room = band(noise(N), 40, 300)
amb = (0.05 * norm(hum) + 0.06 * norm(room)) * auto([(0, 0), (0.3, 1), (BLACK - 0.01, 1), (BLACK, 0), (DUR, 0)])
put(amb, 0, 1.0)

# Arian's footsteps, then stopping
S.footsteps(0.15, 3.45, 1.8, 0.35, -0.05)
crackle(2.2, 3.4, 0.12, 1)
put(S.groan(1.4, 85) * 0.5, 2.6, 0.12, 0.2)          # far away, barely there
put(band(S.groan(1.6, 92), 100, 900), 4.3, 0.45, 0.35)  # the one he hears
S.heartbeat(4.7, 8.5, 92, 0.5)
S.heartbeat(8.5, BLACK, 140, 0.6)

# tension drone rising through shots B and C
dr = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 58.3 * t) + 0.4 * np.sin(2 * np.pi * 110.7 * t))
dr *= auto([(0, 0), (3.5, 0), (6.0, 0.06), (8.4, 0.16), (BLACK, 0.2), (BLACK + 0.01, 0), (DUR, 0)])
put(dr, 0, 1.0)

# zombie: dragging shuffle and groans
r = np.random.default_rng(3)
x = 6.0
while x < 8.5:
    put(band(noise(int(0.09 * SR)), 60, 1800) * np.exp(-S.tt(int(0.09 * SR)) * 30), x, 0.3, 0.15)
    put(S.scrape(0.45) * 0.5, x + 0.45, 0.14, 0.15)
    x += 1.0 / 1.1
crackle(6.4, 8.5, 0.14, 2)
put(S.groan(1.3, 100), 6.3, 0.5, 0.1)
put(S.groan(1.1, 88), 7.6, 0.6, 0.0)

# lunge: roar + sting, then hard cut to silence
put(S.groan(1.15, 135) * np.linspace(0.6, 1.0, int(1.15 * SR)), 8.55, 0.95, 0.0)
crackle(8.6, 9.7, 0.16, 4)
n = int(1.1 * SR)
sting = norm(band(noise(n), 30, 200)) * np.exp(-S.tt(n) * 3) * 0.9
sting += norm(sum(np.sin(2 * np.pi * f * S.tt(n)) for f in (1870, 1990, 2210))) * env(n, 0.005, 0.6) * 0.25
put(sting, 8.95, 0.9)
mix = np.stack([S.L, S.R], 1)
mix[int(BLACK * SR):] *= np.exp(-np.arange(N - int(BLACK * SR)) / (0.05 * SR))[:, None]
mix = mix / max(1e-9, np.max(np.abs(mix))) * 0.9

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
wav = os.path.join(HERE, "out", "sfx.wav")
S.write(wav, mix)

if "--audio" in sys.argv:
    sys.exit(0)
vid = os.path.join(HERE, "out", "zombie_test.mp4")
vf = ("scale=1080:1920:flags=lanczos,noise=alls=5:allf=t,vignette=PI/5,"
      f"drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='gte(t,{BLACK})'")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "24", "-i", os.path.join(HERE, "frames", "f_%04d.png"),
                "-i", wav, "-vf", vf, "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-shortest", vid], check=True)
print(vid)
