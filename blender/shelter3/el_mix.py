"""Sound of «پناهگاه ۳» from ElevenLabs only (voices + effects in el/, generated with the ElevenLabs MCP tools,
flow HpUe7Y4z5ieVYxp4gmq6; see el_lines.py and voice_script.md).
    python3 el_mix.py   ->  out/sfx.wav (effects only)  and  out/voice.wav (voices + effects)
Event times come from out/events.json (written by pov.py) and the line times from times.py."""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, END, CARD_SECONDS, KEY_OF  # noqa: E402
EL, OUT = os.path.join(HERE, "el"), os.path.join(HERE, "out")
SR = 48000
TOTAL = END + CARD_SECONDS
N = int(TOTAL * SR)
rng = np.random.default_rng(3)
T_IN = json.load(open(os.path.join(OUT, "events.json")))["T_IN"]
MASK = "lowpass=f=5200,equalizer=f=1100:t=q:w=1.2:g=3,equalizer=f=250:t=q:w=1:g=-3"


def load(path, af=None, norm=True):
    flt = "aformat=channel_layouts=mono"
    if af:
        flt += "," + af
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-af", flt, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
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
    if j <= i:
        return
    buf[i:j, 0] += x[:j - i] * (1 - max(0, pan))
    buf[i:j, 1] += x[:j - i] * (1 + min(0, pan))


def bed(buf, x, t0, t1, gain, fade=1.5, pan=0.0):
    """loop an ambience from t0 to t1 with crossfaded repeats"""
    if t1 <= t0:
        return
    n = int((t1 - t0) * SR)
    cf = int(1.0 * SR)
    out = np.zeros(n + len(x), np.float32)
    i = 0
    while i < n:
        seg = x.copy()
        seg[:cf] *= np.linspace(0, 1, cf)
        seg[-cf:] *= np.linspace(1, 0, cf)
        out[i:i + len(seg)] += seg
        i += len(x) - cf
    put(buf, out[:n], t0, gain, pan, fade=fade)


def effects():
    E = json.load(open(os.path.join(OUT, "events.json")))
    T = KEY_OF
    buf = np.zeros((N, 2), np.float32)
    door, out_, t_in, go = E["T_DOOR"], E["T_OUT"], E["T_IN"], E["T_GO"]
    forest, dogs, bang, stop, lights = E["T_FOREST"], E["T_DOGS"], E["T_BANG"], E["T_STOP"], E["T_LIGHTS"]
    arr0, arr1 = E["T_ARRIVE"]
    muff = "lowpass=f=900"                                   # outside sounds heard through the steel door
    # the shelter
    bed(buf, fx("amb_shelter"), 0, door + 0.8, 0.30)
    cough = fx("cough")
    for t, p in ((4.0, -0.5), (18.0, 0.4), (27.5, -0.2)):
        put(buf, cough, t, 0.22, p, length=3.0)
    # the loudspeaker outside, the bus arriving (muffled), the door
    put(buf, fx("megaphone", muff), E["T_LOUD"], 0.5)
    put(buf, fx("bus_arrive", muff), arr0 - 4.5, 0.45, 0.2)
    # the steel door: separate unlock (wheel + bolts, when I grab the handle) and the slow heavy swing open
    put(buf, fx("door_unlock"), KEY_OF["me2"][0] + 0.4, 0.75)
    put(buf, fx("door_open"), door - 0.1, 0.85)
    put(buf, fx("busdoor_open", muff), arr1 + 0.3, 0.4, 0.2)       # the bus doors fold open outside
    # outside: the dead city wind; footsteps to the bus; the bus idling then leaving
    bed(buf, fx("amb_city"), door + 0.2, t_in + 0.5, 0.35)
    put(buf, fx("footsteps"), out_ + 0.4, 0.5, 0.1)
    bed(buf, fx("amb_bus", "lowpass=f=1500"), out_, t_in, 0.15, pan=0.3)       # idling outside
    put(buf, fx("busdoor_close"), go - 0.8, 0.7)                    # doors shut behind us, then we pull away
    put(buf, fx("bus_depart", "atrim=start=1.2,asetpts=PTS-STARTPTS"), go - 0.2, 0.6)
    # inside the moving bus: engine rumble all the way, the city outside quieter
    bed(buf, fx("amb_bus"), t_in, stop + 0.5, 0.32)
    bed(buf, fx("amb_city", "lowpass=f=2500"), go, forest, 0.12)
    put(buf, fx("siren"), T["n4"][0] + 1.0, 0.18, -0.6)
    # the forest
    bed(buf, fx("amb_forest"), forest - 1.0, END + CARD_SECONDS, 0.25)
    put(buf, fx("growl"), T["lena5"][0] - 0.6, 0.55, -0.5)
    put(buf, fx("growl", "asetrate=40000,aresample=48000"), T["old3"][1] - 0.5, 0.45, 0.6)
    dg = fx("dogs")
    put(buf, dg, dogs, 0.6, 0.0, length=min(len(dg) / SR, bang - dogs + 1.5))
    put(buf, fx("chew"), T["me5"][0] - 0.3, 0.6, -0.3)
    put(buf, fx("burst"), bang, 0.95, -0.2, length=1.2, fade=0.3)   # short, so «لاستیک ترکید!» stays clear
    put(buf, fx("bus_stop"), stop - 3.0, 0.7)
    cl = fx("claws")
    put(buf, cl, stop + 0.5, 0.5)
    put(buf, cl, stop + 0.5 + len(cl) / SR - 0.5, 0.35, 0.4,
        length=max(0.5, T["n7"][0] - (stop + len(cl) / SR)))
    # the radio static around the radio lines and when the boy uses it
    rad = fx("radio")
    for k in ("me1", "radio1", "me4", "radio2", "me6"):
        a, b = T[k]
        put(buf, rad, a - 0.4, 0.22 if k.startswith("radio") else 0.15, length=min(len(rad) / SR, b - a + 0.8))
    put(buf, fx("far_car"), lights - 0.6, 0.4)
    # tension under the forest and the end
    hb = fx("heartbeat")
    bed(buf, hb, T["lena5"][0], dogs, 0.28)
    bed(buf, hb, stop + 1.0, END, 0.3)
    dr = fx("drone")
    bed(buf, dr, T["radio1"][0] - 1, END + CARD_SECONDS, 0.2, fade=3.0)
    fade = np.ones(N, np.float32)
    nf = int(0.8 * SR)
    fade[-nf:] = np.linspace(1, 0, nf)
    return buf * fade[:, None]


def voices():
    buf = np.zeros((N, 2), np.float32)
    duck = np.ones(N, np.float32)
    for key, who, _ in LINES:
        a, b = KEY_OF[key]
        af = "aecho=0.8:0.3:30:0.06" if who in ("Mom", "Guard", "Me", "Old man") else None   # light room (Lena dry: clearer)
        if key[0] != "n" and who != "Radio" and key not in ("resc1", "resc2") and \
                (who in ("Rescuer", "Old man") or a >= T_IN):      # talking through a radiation mask
            af = (af + "," if af else "") + MASK
        x = load(os.path.join(HERE, "voices", "clips", key + ".wav"), af, norm=False)   # clips are loudnorm'd
        g = 1.0
        put(buf, x, a, g, {"Lena": 0.12, "Mom": -0.12, "Guard": 0.2, "Old man": 0.15}.get(who, 0.0), fade=0.02)
        i, j = int((a - 0.15) * SR), int((a + len(x) / SR + 0.15) * SR)
        duck[max(0, i):j] = 10 ** (-13 / 20)          # effects -13 dB under every line
    duck = np.convolve(duck, np.ones(4800) / 4800, mode="same").astype(np.float32)
    return buf, duck


def write(path, data):
    data = data / max(1e-6, np.abs(data).max()) * 0.89
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), path], input=pcm.tobytes(), check=True)
    print(path)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fxb = effects()
    write(os.path.join(OUT, "sfx.wav"), fxb)
    vo, duck = voices()
    fxd = fxb * duck[:, None]
    # speech must sit >= 10 dB above the effects in every line: measure each line, lower the effects if needed
    def db(x):
        return 20 * np.log10(max(1e-9, float(np.sqrt(np.mean(x ** 2)))))
    worst, g = 99.0, 0.6
    for key, who, _ in LINES:
        a, b = KEY_OF[key]
        i, j = int(a * SR), int(b * SR)
        worst = min(worst, db(vo[i:j]) - db(fxd[i:j] * g))
    if worst < 12.0:                       # aim for 12 dB so the quietest line still clears 10 dB
        g *= 10 ** ((worst - 12.0) / 20)
    print(f"effects gain {g:.3f}; worst speech-over-effects before {worst:.1f} dB, after {worst - 20*np.log10(g/0.6):.1f} dB")
    write(os.path.join(OUT, "voice.wav"), vo + fxd * g)
