#!/usr/bin/env python3
"""Driving-quiz episode: voice clean-up + timeline + full sound mix.

usage: build.py <episode_dir> [--tempo 1.12] [--duration 60]

Needs in <ep>/audio/raw/: intro, q1..q5, a1..a5, outro (.mp3, ElevenLabs narrator),
whoosh, tick, ding, pop, hit, music  (_a/_b takes; the take named in episode.json "takes" wins, default _a).
Writes <ep>/timeline.json and <ep>/audio/mix.wav, <ep>/audio/voice.wav (voice only).
"""
import json, subprocess, sys, os, argparse
import numpy as np

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument("ep"); ap.add_argument("--tempo", type=float, default=1.12)
ap.add_argument("--duration", type=float, default=60.0)
A = ap.parse_args()
EP = A.ep
ep = json.load(open(f"{EP}/episode.json"))
RAW = f"{EP}/audio/raw"
takes = ep.get("takes", {})

def load(path, filt=""):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if filt: cmd += ["-af", filt]
    cmd += ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()

def raw(name):
    for cand in (f"{name}_{takes.get(name,'a')}.mp3", f"{name}.mp3"):
        p = f"{RAW}/{cand}"
        if os.path.exists(p): return p
    raise FileNotFoundError(name)

TRIM = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
def voice(name):
    return load(raw(name), f"{TRIM},atempo={A.tempo},highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5")

nq = len(ep["questions"])
V = {"intro": voice("intro"), "outro": voice("outro")}
for i in range(1, nq + 1):
    V[f"q{i}"] = voice(f"q{i}"); V[f"a{i}"] = voice(f"a{i}")
dur = {k: len(v) / SR for k, v in V.items()}

# ---- timeline -----------------------------------------------------------
GAP_IN = 0.20      # whoosh -> question voice
GAP_CD = 0.15      # question voice end -> countdown
GAP_A = 0.12       # reveal -> answer voice
TAIL = 0.30        # answer voice end -> next scene
INTRO_PAD, OUTRO_TAIL = 0.25, 0.7
fixed = INTRO_PAD + dur["intro"] + 0.25 + sum(GAP_IN + dur[f"q{i}"] + GAP_CD + GAP_A + dur[f"a{i}"] + TAIL for i in range(1, nq + 1)) \
        + 0.3 + dur["outro"] + OUTRO_TAIL
C = (A.duration - fixed) / nq
print(f"voice total {sum(dur.values()):.2f}s, fixed {fixed:.2f}s -> countdown {C:.2f}s per question")
if C < 1.8: sys.exit("countdown would be shorter than 1.8 s: raise --tempo or shorten lines")
C = min(C, 3.6)

t = 0.0
tl = {"fps": 30, "duration": A.duration, "q": []}
iv0 = INTRO_PAD; t = iv0 + dur["intro"] + 0.25
tl["intro"] = {"start": 0.0, "end": t, "voice": [iv0, iv0 + dur["intro"]]}
for i in range(1, nq + 1):
    s = t; qv0 = s + GAP_IN; qv1 = qv0 + dur[f"q{i}"]
    n_opt = len(ep["questions"][i - 1]["options"])
    span = max(0.9, (qv1 - qv0) * 0.75)
    opts = [round(qv0 + 0.35 + k * span / n_opt, 3) for k in range(n_opt)]
    cd0 = qv1 + GAP_CD; cd1 = cd0 + C
    av0 = cd1 + GAP_A; av1 = av0 + dur[f"a{i}"]
    t = av1 + TAIL
    tl["q"].append({"start": s, "end": t, "qv": [qv0, qv1], "opts": opts, "cd": [cd0, cd1], "reveal": cd1, "av": [av0, av1]})
ov0 = t + 0.3
tl["outro"] = {"start": t, "end": A.duration, "voice": [ov0, ov0 + dur["outro"]]}
json.dump(tl, open(f"{EP}/timeline.json", "w"), indent=1)

# ---- mix ----------------------------------------------------------------
N = int(A.duration * SR)
vo = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
def put(buf, x, at, gain=1.0):
    i = int(at * SR); j = min(N, i + len(x))
    if j > i: buf[i:j] += gain * x[: j - i]
put(vo, V["intro"], tl["intro"]["voice"][0]); put(vo, V["outro"], ov0)
for i, q in enumerate(tl["q"], 1):
    put(vo, V[f"q{i}"], q["qv"][0]); put(vo, V[f"a{i}"], q["av"][0])

norm = "loudnorm=I=-18:TP=-2"
whoosh = load(raw("whoosh"), f"{TRIM},{norm}")
ding = load(raw("ding"), f"{TRIM},{norm}")
pop = load(raw("pop"), f"{TRIM},{norm}")
hit = load(raw("hit"), f"{TRIM},{norm}")
tickfile = load(raw("tick"), TRIM)
# cut one tick out of the ElevenLabs tick take: the loudest onset, 0.25 s long
env = np.convolve(np.abs(tickfile), np.ones(240) / 240, "same")
k = int(np.argmax(env)); k0 = max(0, k - int(0.02 * SR))
tick = tickfile[k0:k0 + int(0.25 * SR)].copy()
tick *= np.linspace(1, 0, len(tick)) ** 0.5
tick /= (np.abs(tick).max() + 1e-9)

whoosh_peak = int(np.argmax(np.convolve(np.abs(whoosh), np.ones(2400) / 2400, "same"))) / SR
put(fx, hit, 0.0, 0.9)
for i, q in enumerate(tl["q"]):
    put(fx, whoosh, max(0, q["start"] + 0.2 - whoosh_peak), 0.8)       # whoosh peaks as the scene slides in
    for o in q["opts"]: put(fx, pop, o, 0.35)
    step = (q["cd"][1] - q["cd"][0]) / 3
    for k in range(3): put(fx, tick, q["cd"][0] + k * step, 0.55 + 0.15 * k)
    put(fx, ding, q["reveal"], 0.9)
put(fx, whoosh, max(0, tl["outro"]["start"] + 0.2 - whoosh_peak), 0.8)
for k in range(6): put(fx, pop, tl["outro"]["start"] + 0.9 + k * 0.18, 0.3)

music = load(raw("music"), "loudnorm=I=-20:TP=-3")
if len(music) < N: music = np.tile(music, N // len(music) + 1)
music = music[:N].copy()
# duck the music under the voice (and a bit under the countdown so ticks cut through)
venv = np.convolve(np.abs(vo), np.ones(SR // 20) / (SR // 20), "same")
duck = np.where(venv > 0.01, 0.28, 0.6).astype(np.float32)
for q in tl["q"]:
    a, b = int(q["cd"][0] * SR), int(q["cd"][1] * SR); duck[a:b] = 0.4
sm = SR // 8; duck = np.convolve(duck, np.ones(sm) / sm, "same")
fade = np.ones(N, np.float32); fl = int(1.2 * SR); fade[-fl:] = np.linspace(1, 0, fl)
fade[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
mix = vo * 1.0 + fx * 0.8 + music * duck * fade
mix /= max(1.0, np.abs(mix).max() / 0.97)

def write(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-af", "loudnorm=I=-14:TP=-1.0", "-ar", str(SR), path], input=x.astype(np.float32).tobytes(), check=True)
write(f"{EP}/audio/mix.wav", mix)
write(f"{EP}/audio/voice.wav", vo)
print("wrote timeline.json, audio/mix.wav, audio/voice.wav")
