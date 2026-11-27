"""Sound for «دیوار ۲», all from ElevenLabs: the voices (voices/NN_who.mp3, one fixed voice per character, see
../voices/VOICES.md) and the effects (sfx/*.mp3). Lines are placed at captions.VOICE, effects at the moments of
the scene (out/hits.json has the blows on the sofa); effects duck under the dialogue.
Writes out/wall2_voice.wav and out/wall2_mix.wav (video time: OPEN seconds of opening card first)."""
import os, sys, json, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import VOICE, END  # noqa: E402
from post import OPEN, CARD  # noqa: E402

SR = 48000
DUR = OPEN + END + CARD
PITCH = {"kian": 2.5, "arian": 1.5, "mahsa": 1.0, "me": 1.5}      # the teenagers a little younger (semitones)
GAIN = {"rezaei": 1.1, "me": 0.9}


def decode(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", ",".join(af)]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def add(track, x, t, g=1.0, fade_out=0.0, max_len=None):
    if max_len:
        x = x[:int(max_len * SR)].copy()
    if fade_out:
        n = min(len(x), int(fade_out * SR))
        x[-n:] *= np.linspace(1, 0, n)
    i = int((OPEN + t) * SR)
    j = min(len(track), i + len(x))
    track[i:j] += g * x[:j - i]


voice = np.zeros(int(DUR * SR), np.float32)
for name, t in VOICE:
    who = name.split("_", 1)[1]
    af = []
    if PITCH.get(who):
        af.append(f"rubberband=pitch={2 ** (PITCH[who] / 12):.4f}:formant=preserved")
    x = decode(os.path.join(HERE, "voices", name + ".mp3"), af)
    x /= max(1e-4, np.abs(x).max())
    add(voice, x * 0.8, t, GAIN.get(who, 1.0))

S = lambda n: decode(os.path.join(HERE, "sfx", n + ".mp3"))  # noqa: E731
fx = np.zeros_like(voice)
room = S("room")
for k in range(int(END / 19) + 2):                       # room tone under the whole film
    add(fx, room, k * 19.0, 0.35, fade_out=1.0, max_len=20.0)
hits = json.load(open(os.path.join(HERE, "out", "hits.json")))
add(fx, S("scream"), 8.8, 0.9)
add(fx, S("run"), 11.5, 0.75, fade_out=1.0)
add(fx, S("sofa"), hits["push"][0], 0.9)
thud = S("thud")
for b in hits["blows"]:
    add(fx, thud, b - 0.03, 0.85, max_len=1.2, fade_out=0.3)
add(fx, S("growl"), 24.4, 0.6, fade_out=1.5)
add(fx, S("flicker"), 28.0, 0.5)
add(fx, S("away"), 34.2, 0.6, fade_out=1.0)
add(fx, S("phone"), 38.9, 0.7, max_len=1.6, fade_out=0.4)
drone = S("drone")
add(fx, drone, END - len(drone) / SR + 0.3, 0.75)       # the stinger lands at the cut to black

# duck the effects under the dialogue
env = np.abs(voice)
k = int(0.15 * SR)
env = np.convolve(env, np.ones(k) / k, mode="same")
duck = 1.0 - 0.55 * np.clip(env / 0.05, 0, 1)
mix = voice + fx * duck
mix /= max(1.0, np.abs(mix).max() / 0.95)
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)


def write(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", path],
                   input=x.astype(np.float32).tobytes(), check=True)
    print(path, round(len(x) / SR, 2))


write(os.path.join(HERE, "out", "wall2_voice.wav"), voice)
write(os.path.join(HERE, "out", "wall2_mix.wav"), mix)
