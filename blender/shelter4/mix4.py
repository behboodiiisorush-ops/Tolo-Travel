"""Sound of «پناهگاه ۴»: the user's own voice lines + ElevenLabs effects (el/fx_*.mp3).
    python3 mix4.py  ->  out/sfx.wav (effects only), out/voice.wav (voices + effects)
Event times are the same formulas as scene4.py (from captions/times)."""
import os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, END, CARD_SECONDS, KEY_OF  # noqa: E402
EL, OUT = os.path.join(HERE, "el"), os.path.join(HERE, "out")
SR = 48000
N = int((END + CARD_SECONDS) * SR)


def at(k, i=0):
    return KEY_OF[k][i]


T_HORN = at("lena1", 1) + 0.5
T_FLOOD = T_HORN + 0.5
T_CAR0 = at("n3") - 2.4
T_OUT_CAR = at("n3") + 0.6
T_AT_DOOR = at("str1a") - 0.2
T_DOOR = at("str1a") - 1.0
T_BACK0 = at("n4") - 1.4
T_LENA_GO = at("me4") - 0.5
T_WALK0 = at("n6") - 0.6
T_DARK = at("n7") + 0.3


def load(path, af=None, norm=True):
    flt = "aformat=channel_layouts=mono" + ("," + af if af else "")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", flt, "-ac", "1", "-ar", str(SR), "-f", "f32le",
                          "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    return x / max(1e-6, np.abs(x).max()) if norm else x


def fx(name, af=None):
    return load(os.path.join(EL, f"fx_{name}.mp3"), af)


def put(buf, x, t, gain=1.0, pan=0.0, length=None, fade=0.05):
    if length is not None:
        x = x[:int(length * SR)]
    x = x * gain
    nf = min(len(x) // 2, int(fade * SR))
    if nf:
        x[:nf] *= np.linspace(0, 1, nf)
        x[-nf:] *= np.linspace(1, 0, nf)
    i = int(t * SR)
    if i < 0:
        x, i = x[-i:], 0
    j = min(buf.shape[0], i + len(x))
    if j > i:
        buf[i:j, 0] += x[:j - i] * (1 - max(0, pan))
        buf[i:j, 1] += x[:j - i] * (1 + min(0, pan))


def bed(buf, x, t0, t1, gain, pan=0.0):
    n, cf = int((t1 - t0) * SR), int(1.0 * SR)
    if n <= 0:
        return
    out = np.zeros(n + len(x), np.float32)
    i = 0
    while i < n:
        seg = x.copy()
        seg[:cf] *= np.linspace(0, 1, cf)
        seg[-cf:] *= np.linspace(1, 0, cf)
        out[i:i + len(seg)] += seg
        i += len(x) - cf
    put(buf, out[:n], t0, gain, pan, fade=1.5)


def effects():
    b = np.zeros((N, 2), np.float32)
    total = END + CARD_SECONDS
    bed(b, fx("amb_forest"), 0, total, 0.25)
    hb = fx("heartbeat")
    bed(b, hb, 0, T_FLOOD, 0.3)
    put(b, fx("growl"), 0.4, 0.5, -0.1, length=4)                       # the beast close in front of the bus
    put(b, fx("claws"), 1.0, 0.25, 0.5, length=4)                       # dogs still scratching round the bus
    put(b, fx("horn"), T_HORN, 0.95, -0.1)
    put(b, fx("flood_on"), T_FLOOD - 0.1, 0.8)
    put(b, fx("beast_scream"), T_FLOOD + 0.05, 0.9, -0.2, length=6, fade=0.6)
    put(b, fx("dogs_flee"), T_FLOOD + 0.3, 0.55, 0.3, length=6, fade=0.8)
    put(b, fx("car_roll"), T_CAR0, 0.45, -0.2, length=at("str1a") - T_CAR0, fade=1.0)
    put(b, fx("car_doors"), T_OUT_CAR - 0.3, 0.6, -0.2, length=4)
    put(b, fx("suit_steps"), T_OUT_CAR + 0.3, 0.45, 0.1, length=T_AT_DOOR - T_OUT_CAR)
    put(b, fx("busdoor_open"), T_DOOR - 0.1, 0.8, 0.3, length=3)
    put(b, fx("suit_steps"), T_BACK0, 0.35, 0.1, length=3.5)
    rad = fx("radio")
    for k in ("str2b", "str1d"):
        put(b, rad, at(k) - 0.4, 0.15, length=at(k, 1) - at(k) + 0.8)
    put(b, fx("cage"), at("str1d") - 0.5, 0.5, -0.2, length=at("me4", 1) - at("str1d") + 0.5, fade=0.8)
    put(b, fx("child_steps"), T_WALK0, 0.4, 0.4, length=END - T_WALK0)
    put(b, fx("suit_steps"), T_WALK0, 0.3, 0.4, length=END - T_WALK0)
    put(b, fx("flood_off"), T_DARK - 0.05, 0.85, length=END + CARD_SECONDS - T_DARK)
    bed(b, hb, at("mom2"), END, 0.32)
    bed(b, fx("drone"), at("n4") - 1, END + CARD_SECONDS, 0.18)
    fade = np.ones(N, np.float32)
    nf = int(0.8 * SR)
    fade[-nf:] = np.linspace(1, 0, nf)
    return b * fade[:, None]


def voices():
    b = np.zeros((N, 2), np.float32)
    duck = np.ones(N, np.float32)
    for key, who, _ in LINES:
        a = at(key)
        x = load(os.path.join(HERE, "voices", "clips", key + ".wav"), norm=False)
        put(b, x, a, 1.0, {"Lena": 0.12, "Mom": -0.12, "Old man": 0.15, "Stranger 1": 0.2,
                           "Stranger 2": 0.25}.get(who, 0.0), fade=0.02)
        i, j = int((a - 0.15) * SR), int((a + len(x) / SR + 0.15) * SR)
        duck[max(0, i):j] = 10 ** (-13 / 20)                 # effects -13 dB under every line
    duck = np.convolve(duck, np.ones(4800) / 4800, mode="same").astype(np.float32)
    return b, duck


def write(path, data):
    data = data / max(1e-6, np.abs(data).max()) * 0.89
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af",
                    "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), path], input=pcm.tobytes(), check=True)
    print(path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fxb = effects()
    write(os.path.join(OUT, "sfx.wav"), fxb)
    vo, duck = voices()
    fxd = fxb * duck[:, None]

    def db(x):
        return 20 * np.log10(max(1e-9, float(np.sqrt(np.mean(x ** 2)))))
    g, worst = 0.6, 99.0
    for key, _, _ in LINES:
        i, j = int(at(key) * SR), int(at(key, 1) * SR)
        worst = min(worst, db(vo[i:j]) - db(fxd[i:j] * g))
    if worst < 12.0:
        g *= 10 ** ((worst - 12.0) / 20)
    print(f"effects gain {g:.3f}; worst speech-over-effects {worst:.1f} dB -> {worst - 20 * np.log10(g / 0.6):.1f} dB")
    write(os.path.join(OUT, "voice.wav"), vo + fxd * g)
