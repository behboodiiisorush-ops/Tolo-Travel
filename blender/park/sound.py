"""Music + sound effects for «پارک» (no dialogue), all synthesised with numpy.

    python3 sound.py        -> audio/music.wav, audio/sfx.wav, audio/mix.wav (60 s, 44.1 kHz stereo)

Music: bright ukulele / glockenspiel / bass / light drums at 120 bpm, following the story sections.
Sound effects: footsteps from the animation (events.json), barks, quacks, peeps, throws, kicks, bounces,
splash, squeaky toy, claps, butterfly twinkle, the sneeze and the pop.
"""
import json, math, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR, DUR = 44100, 60.5
N = int(SR * DUR)
rng = np.random.default_rng(11)
EV = json.load(open(os.path.join(HERE, "events.json")))
SNEEZE = EV["SNEEZE"]
DROP = EV["DROP"]


def t_(d):
    return np.arange(int(SR * d)) / SR


def env(d, a=0.005, r=None):
    n = int(SR * d)
    e = np.ones(n)
    na = max(1, int(SR * a))
    e[:na] = np.linspace(0, 1, na)
    if r is None:
        r = d - a
    nr = max(1, int(SR * r))
    e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e


def fft_band(x, lo=0.0, hi=20000.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = ((f >= lo) & (f <= hi)).astype(float)
    # soft edges
    m = np.convolve(m, np.ones(9) / 9, mode="same")
    return np.fft.irfft(X * m, len(x))


def put(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    j = min(len(buf), i + len(x))
    s = max(0, i)
    seg = x[s - i: j - i] * gain
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[s:j, 0] += seg * l * 1.41
    buf[s:j, 1] += seg * r * 1.41


def hz(note):
    """'C4' style note -> Hz."""
    names = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    n = names[note[0]]
    i = 1
    if note[1] == "#":
        n += 1; i = 2
    elif note[1] == "b":
        n -= 1; i = 2
    octv = int(note[i:])
    return 440.0 * 2 ** ((n + (octv - 4) * 12) / 12)


# ------------------------------------------------------------------------------------------------ instruments
def pluck(f, d=1.2, bright=0.5):
    n = int(SR * d)
    p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p)
    buf = np.convolve(buf, np.ones(3) / 3, mode="same") * (0.5 + bright)
    out = np.zeros(n)
    k = 0.996 - 0.002 * (1 - bright)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = k * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out * env(d, 0.002, d * 0.5)


_PL = {}


def pluck_c(f, d=1.0):
    key = (round(f, 1), d)
    if key not in _PL:
        _PL[key] = pluck(f, d)
    return _PL[key]


def glock(f, d=1.4):
    t = t_(d)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 8)
         + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 14))
    return x * env(d, 0.002, 0.05)


def bass(f, d=0.45):
    t = t_(d)
    ph = 2 * np.pi * f * t
    x = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
    return x * np.exp(-t * 3.5) * env(d, 0.004, 0.06)


def kick(d=0.25):
    t = t_(d)
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)


def noise(d):
    return rng.uniform(-1, 1, int(SR * d))


def clap(d=0.12):
    x = fft_band(noise(d), 900, 5000)
    t = t_(d)
    e = np.exp(-t * 40) + 0.6 * np.exp(-np.maximum(0, t - 0.012) * 40) * (t > 0.012)
    return x * e * 2.2


def shaker(d=0.06):
    return fft_band(noise(d), 5000, 14000) * np.exp(-t_(d) * 60) * 1.8


def snare_tick(d=0.09):
    return (fft_band(noise(d), 1500, 9000) * np.exp(-t_(d) * 45) * 1.6
            + 0.4 * np.sin(2 * np.pi * 190 * t_(d)) * np.exp(-t_(d) * 30))


def pad(freqs, d, a=0.4):
    t = t_(d)
    x = np.zeros(len(t))
    for f in freqs:
        for det in (-0.25, 0.25):
            ph = 2 * np.pi * (f + det) * t
            x += sum(np.sin(k * ph) / k for k in range(1, 7)) * 0.2
    x = fft_band(x, 80, 1800)
    return x * env(d, a, min(0.6, d * 0.4)) / max(1, len(freqs))


def tone_glide(f0, f1, d, wave="sine", vib=0.0):
    t = t_(d)
    f = f0 * (f1 / f0) ** (t / d)
    f = f * (1 + vib * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if wave == "saw":
        return sum(np.sin(k * ph) / k for k in range(1, 9))
    return np.sin(ph)


# ------------------------------------------------------------------------------------------------ music
BEAT = 0.5
PROG = {"main": [("C4", "E4", "G4"), ("G3", "B3", "D4"), ("A3", "C4", "E4"), ("F3", "A3", "C4")],
        "march": [("C4", "E4", "G4"), ("F3", "A3", "C4"), ("G3", "B3", "D4"), ("C4", "E4", "G4")]}
ROOT = {"C4": "C2", "G3": "G1", "A3": "A1", "F3": "F1"}
MELODY = ["E5", "G5", "A5", "G5", "E5", "D5", "C5", "D5",
          "D5", "G5", "B5", "A5", "G5", "D5", "B4", "D5",
          "C5", "E5", "A5", "G5", "E5", "C5", "A4", "C5",
          "A4", "C5", "F5", "E5", "C5", "A4", "G4", "C5"]
SECTIONS = [  # (start, end, style)
    (0.0, 5.0, "intro"), (5.0, 20.2, "groove"), (20.2, 24.0, "uhoh"), (24.0, 30.4, "tiptoe"),
    (30.4, 35.5, "party"), (35.5, 50.0, "march"), (50.0, SNEEZE - 0.05, "hush"), (SNEEZE + 0.9, 59.6, "finale")]


def music():
    m = np.zeros((N, 2))
    for s0, s1, style in SECTIONS:
        prog = PROG["march" if style == "march" else "main"]
        b = math.ceil(s0 / BEAT)
        while b * BEAT < s1 - 0.01:
            t = b * BEAT
            bar, beat = divmod(b, 4)
            chord = prog[(bar // 1) % 4]
            mel = MELODY[(b * 2) % len(MELODY)]
            mel2 = MELODY[(b * 2 + 1) % len(MELODY)]
            if style in ("groove", "party", "finale"):
                for i, n_ in enumerate(chord):                       # ukulele strum on every beat
                    put(m, pluck_c(hz(n_) * 2, 0.9), t + i * 0.012, 0.16, pan=-0.3)
                if beat in (0, 2):
                    put(m, bass(hz(ROOT[chord[0]])), t, 0.5)
                    put(m, kick(), t, 0.35)
                else:
                    put(m, clap(), t, 0.10, pan=0.2)
                put(m, shaker(), t + 0.25, 0.08, pan=0.4)
                put(m, shaker(), t, 0.05, pan=0.4)
                put(m, glock(hz(mel)), t, 0.16, pan=0.2)
                put(m, glock(hz(mel2)), t + 0.25, 0.12, pan=0.2)
            elif style == "intro":
                put(m, glock(hz(mel)), t, 0.18, pan=0.15)
                if beat == 0:
                    put(m, pad([hz(n_) for n_ in chord], 2.0), t, 0.25)
            elif style == "tiptoe":
                put(m, pluck_c(hz(ROOT[chord[0]]) * 2, 0.4), t, 0.35)            # pizzicato steps
                put(m, pluck_c(hz(chord[2]), 0.4), t + 0.25, 0.18)
                if beat % 2 == 0:
                    put(m, glock(hz(mel) * 2, 1.0), t, 0.07, pan=0.3)
            elif style == "march":
                put(m, bass(hz(ROOT[chord[0]]) if beat % 2 == 0 else hz(ROOT[chord[0]]) * 1.5), t, 0.45)
                put(m, snare_tick(), t + 0.25, 0.18, pan=-0.2)
                if beat in (0, 2):
                    put(m, kick(), t, 0.3)
                for i, n_ in enumerate(chord):
                    put(m, pluck_c(hz(n_) * 2, 0.5), t + 0.25 + i * 0.01, 0.10, pan=0.3)
                put(m, glock(hz(mel)), t, 0.14, pan=0.1)
                # a whistled march tune on top
                w = tone_glide(hz(mel), hz(mel), 0.45, vib=0.006) * env(0.45, 0.03, 0.15)
                put(m, w, t, 0.05, pan=-0.1)
            elif style == "hush":
                if beat == 0:
                    put(m, pad([hz(n_) for n_ in chord], 2.0, a=0.8), t, 0.18)
                if beat % 2 == 1:
                    put(m, glock(hz(mel) * 2, 1.2), t, 0.06, pan=0.3)
            b += 1
    # stingers
    put(m, pad([hz("C4"), hz("E4"), hz("G4"), hz("C5")], 1.4, a=0.02), 30.4, 0.35)          # hooray
    for i, n_ in enumerate(("C5", "E5", "G5", "C6")):
        put(m, glock(hz(n_), 1.2), 30.45 + i * 0.09, 0.22)
    for i, (a, b2) in enumerate((("G3", "F#3"), ("F#3", "F3"), ("F3", "E3"))):              # uh-oh trombone
        d = 0.42 if i < 2 else 0.9
        x = tone_glide(hz(a), hz(b2), d, "saw", vib=0.01 if i == 2 else 0.0)
        x = fft_band(x, 60, 1400) * env(d, 0.03, 0.2)
        put(m, x, 21.0 + i * 0.45, 0.22)
    # tension roll before the sneeze, final chord
    t0 = SNEEZE - 0.55
    for i in range(10):
        put(m, glock(hz("C6") * 2 ** (i / 12), 0.3), t0 + i * 0.05, 0.05)
    put(m, pad([hz("C4"), hz("E4"), hz("G4"), hz("C5")], 1.0, a=0.01), 59.55, 0.35)
    for i, n_ in enumerate(("C5", "G5", "C6")):
        put(m, glock(hz(n_), 1.0), 59.55 + i * 0.07, 0.25)
    return m


# ------------------------------------------------------------------------------------------------ sfx
def bark(pitch=1.0, d=0.13):
    t = t_(d)
    f = (720 - 280 * t / d) * pitch
    x = tone_glide(f[0], f[-1], d, "saw")
    x = fft_band(x, 300, 3500) + 0.25 * fft_band(noise(d), 800, 4000)
    return x * np.sin(np.pi * t / d) ** 0.6


def arf(t, pitch=1.0, gain=0.55, pan=0.0):
    put(S, bark(pitch), t, gain, pan)
    put(S, bark(pitch * 1.08, 0.11), t + 0.17, gain * 0.85, pan)


def quack(pitch=1.0, d=0.17):
    t = t_(d)
    x = tone_glide(320 * pitch, 250 * pitch, d, "saw")
    x = fft_band(x, 700, 2600) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
    return x * np.sin(np.pi * t / d) ** 0.4 * 1.6


def peep(d=0.09):
    return tone_glide(3200, 3900, d) * np.sin(np.pi * t_(d) / d)


def whoosh(d=0.4, lo=300, hi=3000):
    x = noise(d)
    t = t_(d)
    out = np.zeros_like(x)
    for k in range(4):                                         # moving band
        a, b = int(k * len(x) / 4), int((k + 1) * len(x) / 4)
        out[a:b] = fft_band(x, lo * (1 + k), hi * (0.6 + 0.3 * k))[a:b]
    return out * np.sin(np.pi * t / d) ** 2


def thump(d=0.18, f=110):
    t = t_(d)
    return np.sin(2 * np.pi * np.cumsum(f * (0.6 + 0.8 * np.exp(-t * 25))) / SR) * np.exp(-t * 22) + \
        0.3 * fft_band(noise(d), 200, 2000) * np.exp(-t * 60)


def boing(d=0.5, f=300):
    t = t_(d)
    ff = f * (1 + 0.35 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 4)) * (1 + 0.6 * np.exp(-t * 8))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-t * 5)


def splash(d=1.3):
    t = t_(d)
    x = fft_band(noise(d), 200, 6000) * np.exp(-t * 4.5) * (1 - np.exp(-t * 80))
    for k in range(14):
        tt = rng.uniform(0.08, 0.9)
        f = rng.uniform(900, 2400)
        dd = 0.05
        blip = tone_glide(f, f * 1.6, dd) * np.sin(np.pi * t_(dd) / dd) * 0.3
        i = int(tt * SR)
        x[i:i + len(blip)] += blip[:len(x) - i]
    return x


def squeak(d=0.22):
    t = t_(d)
    f = 1300 + 600 * np.sin(np.pi * t / d)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)) * \
        np.sin(np.pi * t / d) ** 0.5


def step(kind):
    d = 0.05
    if kind == "kid":
        x = fft_band(noise(d), 120, 1800) * np.exp(-t_(d) * 70)
        return x * rng.uniform(0.6, 1.0)
    if kind == "dog":
        return fft_band(noise(0.03), 300, 2500) * np.exp(-t_(0.03) * 120) * 0.6
    return fft_band(noise(0.04), 400, 2000) * np.exp(-t_(0.04) * 90) * 0.5     # duck: soft pat


def chirp_bird():
    d = rng.uniform(0.06, 0.12)
    f0 = rng.uniform(2800, 4200)
    return tone_glide(f0, f0 * rng.uniform(1.15, 1.5), d) * np.sin(np.pi * t_(d) / d)


S = np.zeros((N, 2))


def sfx():
    # park ambience: soft air + birds
    amb = fft_band(noise(DUR), 100, 1200) * 0.012
    S[:len(amb), 0] += amb
    S[:len(amb), 1] += amb[::-1]
    tb = 0.6
    while tb < DUR - 1:
        n = rng.integers(1, 4)
        for i in range(n):
            put(S, chirp_bird(), tb + i * 0.13, 0.05, pan=rng.uniform(-0.8, 0.8))
        tb += rng.uniform(1.5, 3.5)
    # footsteps from the animation
    for t, kind, name in EV["steps"]:
        g = {"kid": 0.10, "dog": 0.07, "duck": 0.05, "baby": 0.03}[kind]
        put(S, step(kind if kind != "baby" else "duck"), t, g, pan=rng.uniform(-0.3, 0.3))
    # barks
    for t, p in ((6.2, 1.0), (9.0, 1.05), (18.1, 1.1), (18.6, 1.15), (20.05, 0.95), (57.7, 1.05)):
        arf(t, p, 0.45)
    put(S, bark(0.8, 0.25) * 0.5, 20.9, 0.4)                       # little whine
    put(S, squeak(), 30.95, 0.35)                                  # squeaky ball in the mouth
    put(S, squeak(0.15), 31.5, 0.25)
    # quacks / peeps
    for t, who in EV["quacks"]:
        if who == "mom":
            put(S, quack(1.0), t, 0.5, pan=-0.1)
            put(S, quack(1.05, 0.14), t + 0.2, 0.4, pan=-0.1)
        else:
            put(S, peep(), t, 0.18, pan=0.2)
            put(S, peep(0.07), t + 0.12, 0.14, pan=0.2)
    # ball game
    put(S, whoosh(0.5), 12.95, 0.35)
    put(S, thump(0.12, 160), 14.2, 0.35)                           # catch
    put(S, thump(0.15, 130), 15.6, 0.35)                           # drop
    put(S, thump(0.2, 90), 16.05, 0.55)                            # kick
    put(S, fft_band(noise(0.9), 80, 600) * np.sin(np.pi * t_(0.9) / 0.9) * 0.4, 16.05, 0.4)   # roll on grass
    put(S, thump(0.25, 80), 17.75, 0.7)                            # big kick
    sw = tone_glide(450, 1600, 1.1, vib=0.01) * env(1.1, 0.05, 0.2)  # slide whistle up
    put(S, sw, 17.8, 0.16)
    sw2 = tone_glide(1200, 380, 0.35, vib=0.01) * env(0.35, 0.02, 0.1)
    put(S, sw2, 17.85, 0.14)                                       # small kid falls...
    put(S, boing(0.55, 220), 18.15, 0.35)                          # ...on his bottom
    put(S, thump(0.2, 120) + 0.4 * boing(0.2, 400)[:int(0.2 * SR)], 19.0, 0.45)
    put(S, thump(0.18, 140) + 0.3 * boing(0.18, 450)[:int(0.18 * SR)], 19.6, 0.4)
    put(S, fft_band(noise(0.35), 600, 5000) * np.linspace(1, 0, int(0.35 * SR)), 19.75, 0.2)  # dog skids
    put(S, splash(), 20.2, 0.65)
    # duck paddling
    tp = 24.0
    while tp < 30.4:
        put(S, fft_band(noise(0.08), 300, 1500) * np.sin(np.pi * t_(0.08) / 0.08), tp, 0.06)
        tp += 0.32
    # cheering claps
    for t0, t1, who in ((14.3, 15.4, 1), (33.2, 35.0, 3)):
        for w in range(who):
            t = t0 + 0.03 * w
            while t < t1:
                put(S, clap(), t, 0.22, pan=-0.4 + 0.4 * w)
                t += math.pi / 9
    # parade: a toy drum would be music; here a few happy quacks are already in
    # butterfly, sneeze, pop
    for i, n_ in enumerate(("E6", "G6", "C7")):
        put(S, glock(hz(n_), 0.6), 51.9 + i * 0.06, 0.12)
    put(S, thump(0.12, 150), DROP + 0.35, 0.3)                    # ball put down
    ah = fft_band(tone_glide(380, 520, 0.4, "saw"), 300, 2200) * env(0.4, 0.05, 0.1)
    put(S, ah, SNEEZE - 0.55, 0.22)
    put(S, ah, SNEEZE - 0.13, 0.12)
    choo = fft_band(noise(0.32), 1500, 9000) * np.exp(-t_(0.32) * 9) + \
        0.3 * fft_band(tone_glide(600, 300, 0.32, "saw"), 300, 3000) * np.exp(-t_(0.32) * 10)
    put(S, choo, SNEEZE, 0.75)
    put(S, boing(0.5, 380), SNEEZE + 0.05, 0.35)
    put(S, whoosh(0.6, 500, 4000), SNEEZE + 0.08, 0.25)
    put(S, thump(0.12, 170), SNEEZE + 0.75, 0.35)                 # girl catches
    for i, n_ in enumerate(("C6", "E6", "G6", "C7", "E7")):        # giggly trills while they laugh
        put(S, glock(hz(n_), 0.5), SNEEZE + 1.0 + i * 0.12, 0.06)
        put(S, glock(hz(n_), 0.5), SNEEZE + 1.9 + i * 0.1, 0.05)
    for i, n_ in enumerate(("G5", "C6", "E6", "G6")):              # wave chime
        put(S, glock(hz(n_), 1.0), 57.6 + i * 0.08, 0.1)
    return S


def save(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
    m = music()
    s = sfx()
    m *= 0.55 / max(1e-6, np.abs(m).max())
    s *= 0.8 / max(1e-6, np.abs(s).max())
    fade = np.ones(N)
    fade[int(59.6 * SR):] = np.linspace(1, 0, N - int(59.6 * SR))
    mix = (m * 0.75 + s) * fade[:, None]
    mix *= 0.9 / np.abs(mix).max()
    save(os.path.join(HERE, "audio", "music.wav"), m)
    save(os.path.join(HERE, "audio", "sfx.wav"), s)
    save(os.path.join(HERE, "audio", "mix.wav"), mix)
    print("audio done")
