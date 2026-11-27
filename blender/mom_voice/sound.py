"""Sound mix for «صدای مامان»: ElevenLabs dialogue (out/dialogue.wav from voice.py) + ElevenLabs SFX in sfx/.
Each effect sits on the frame of its action; effects are ducked 13 dB under speech.
Writes out/mix_clean.wav (voices + room tone) and out/mix_sfx.wav (voices + every effect).   python3 sound.py"""
import os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import END
SR = 48000
OUT = os.path.join(HERE, "out")
N = int(END * SR)


def load(name, af=None):
    flt = ["-af", af] if af else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "sfx", name + ".mp3"), *flt,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def read(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def write(p, x):
    x = np.clip(x, -1, 1)
    with wave.open(p, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def db(v):
    return 10 ** (v / 20)


def fade(x, fin=0.02, fout=0.05):
    x = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a: x[:a] *= np.linspace(0, 1, a)
    if b: x[-b:] *= np.linspace(1, 0, b)
    return x


def loop(x, secs, xf=0.25):
    """Loop a short clip to `secs` with crossfades so the seam is not heard."""
    k = int(xf * SR)
    out = x.copy()
    while len(out) < secs * SR:
        a = out[-k:] * np.linspace(1, 0, k) + x[:k] * np.linspace(0, 1, k)
        out = np.concatenate([out[:-k], a, x[k:]])
    return out[:int(secs * SR)]


def put(track, x, t, gain=1.0):
    i = int(t * SR)
    n = min(len(x), len(track) - i)
    track[i:i + n] += x[:n] * gain


dlg = read(os.path.join(OUT, "dialogue.wav"))[:N]
dlg = np.pad(dlg, (0, N - len(dlg)))

# room tone: clock + fridge through the whole film, power dies with the lights at 31.2 s
room = np.zeros(N, np.float32)
tone = loop(load("room_tone"), 31.2)
put(room, fade(tone, 0.5, 0.08), 0.0, db(-14))

fx = np.zeros(N, np.float32)
put(fx, fade(load("phone_vibrate")), 1.2, db(-4))                       # phone buzzes on the table
put(fx, fade(load("pot_spoon", "lowpass=f=5000")), 7.9, db(-9))         # kitchen, before «شام حاضره»
steps = load("footsteps")
put(fx, fade(steps), 12.0, db(-7))                                      # Arian walks out of the kitchen
put(fx, fade(steps, 0.05, 0.4)[:int(1.6 * SR)], 13.9, db(-6))           # ... and arrives at 15.2
hang = load("hangup", "highpass=f=320,lowpass=f=3400")[:int(2.2 * SR)]
put(fx, fade(hang), 26.4, db(-6))                                       # the call cuts off
drone = loop(load("drone"), END - 25.8, 0.5)
drone *= np.linspace(0.15, 1, len(drone)) ** 1.5                        # swells as Mom stands in the doorway
put(fx, fade(drone, 0.8, 1.2), 25.8, db(-8))
put(fx, fade(load("flicker"), 0.01, 0.15), 29.2, db(-5))                # flicker; the pop lands on the blackout

# duck effects 13 dB under speech (smoothed speech envelope)
win = int(0.05 * SR)
env = np.sqrt(np.convolve(dlg ** 2, np.ones(win) / win, mode="same"))
speech = (env > 0.01).astype(np.float32)
sm = int(0.15 * SR)
speech = np.clip(np.convolve(speech, np.ones(sm) / sm, mode="same") * 2, 0, 1)
duck = 1 - speech * (1 - db(-13))

clean = dlg + room * duck
full = dlg + (room + fx) * duck
for name, x in (("mix_clean", clean), ("mix_sfx", full)):
    pk = np.max(np.abs(x))
    if pk > 0.95:
        x = x * 0.95 / pk
    write(os.path.join(OUT, name + ".wav"), x)
    print(name, f"peak {pk:.2f}")
