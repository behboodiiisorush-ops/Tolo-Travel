"""Sound for «در رو باز نکن», all from ElevenLabs: voices/*.mp3 (eleven_v4: «من» = Arash +1.5 st, مامان = Hengameh,
the thing behind the door uses mom's voice) and sfx/*.mp3 (eleven_text_to_sound_v3, one effect per action).
Each line is heard the way it reaches me: through the phone speaker, muffled through the door, or right behind me.
Writes out/door_mix.wav and out/door_voice.wav (film + question card)."""
import os, sys, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lines import LINES, END, PITCH, BLACK  # noqa: E402

SR = 48000
CARD = 4.0
HOW = {
    "phone": ["highpass=f=350", "lowpass=f=3400", "acrusher=bits=10:mix=0.25", "volume=1.0"],
    "door": ["lowpass=f=1700", "aecho=0.8:0.7:18|37:0.25|0.15", "volume=0.9"],
    "close": ["highpass=f=120", "aecho=0.8:0.5:9:0.12"],
    "me": [],
}


def decode(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", ",".join(af)]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def add(track, x, t, g=1.0, fade_out=0.0, max_len=None, fade_in=0.0, src_from=0.0):
    x = x[int(src_from * SR):].copy()
    if max_len:
        x = x[:int(max_len * SR)]
    if fade_in:
        n = min(len(x), int(fade_in * SR))
        x[:n] *= np.linspace(0, 1, n)
    if fade_out:
        n = min(len(x), int(fade_out * SR))
        x[-n:] *= np.linspace(1, 0, n)
    i = int(t * SR)
    j = min(len(track), i + len(x))
    if j > i:
        track[i:j] += g * x[:j - i]


def lead(x, thr=0.03):
    return np.argmax(np.abs(x) > thr * np.abs(x).max()) / SR


def S(nm):
    x = decode(os.path.join(HERE, "sfx", nm + ".mp3"))
    return x / max(1e-4, np.abs(x).max())


def tracks():
    n = int((END + CARD) * SR)
    voice = np.zeros(n, np.float32)
    for a, b, who, text, fn, how in LINES:
        af = []
        if PITCH.get(who):
            af.append(f"rubberband=pitch={2 ** (PITCH[who] / 12):.4f}:formant=preserved")
        af += HOW[how]
        x = decode(os.path.join(HERE, "voices", fn + ".mp3"), af or None)
        x /= max(1e-4, np.abs(x).max())
        g = {"phone": 0.6, "door": 0.62, "close": 0.75, "me": 0.7}[how]
        add(voice, x * g, max(0.0, a - lead(x)))
    fx = np.zeros_like(voice)
    room = S("room")
    add(fx, room, 0.0, 0.07, fade_out=0.1, max_len=BLACK[0])
    add(fx, room, BLACK[1], 0.05, src_from=12.0, fade_in=0.4, fade_out=1.0, max_len=END - BLACK[1])
    drone = S("drone")
    add(fx, drone, 2.6, 0.32, fade_in=3.0, max_len=17.0, src_from=0.6)
    add(fx, drone, 19.6, 0.38, max_len=BLACK[0] - 19.6, src_from=2.0, fade_out=0.08)
    add(fx, drone, BLACK[1], 0.25, src_from=6.0, fade_in=0.8, fade_out=1.2, max_len=END - BLACK[1])
    add(fx, S("knock"), 4.4 - 1.10, 0.95)                               # three knocks on the front door
    add(fx, S("steps"), 10.65 - 0.70, 0.45, max_len=4.4, fade_out=0.4)    # my socks on the hall floor
    add(fx, S("lean"), 14.05 - 2.25, 0.55)                               # my cheek against the door
    add(fx, S("vibrate"), 17.7, 0.5, max_len=1.3, fade_out=0.15)         # mom calling
    heart = S("heart")
    add(fx, heart, 26.6, 0.45, fade_in=1.2, max_len=6.4, fade_out=0.6)
    add(fx, S("flicker"), 33.0 - 1.6, 0.5, src_from=0.0, max_len=3.6, fade_out=0.3)   # the corridor light dies
    add(fx, heart, 35.0, 0.6, src_from=1.5, max_len=3.8, fade_in=0.3, fade_out=0.3)
    add(fx, S("stinger"), 38.85, 1.0, max_len=1.4, fade_out=0.25)        # she is inside
    add(fx, S("send"), 45.0 - 0.1, 0.55)                                 # the message is sent
    env = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1.0 - 0.5 * np.clip(env / (env.max() * 0.25 + 1e-6), 0, 1)
    return voice, fx * duck


def write(path, x):
    x = x / max(1e-6, np.abs(x).max()) * 0.89
    st = np.stack([x, x], 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", path],
                   input=st.tobytes(), check=True)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    v, fx = tracks()
    write(os.path.join(HERE, "out", "door_mix.wav"), v + fx)
    write(os.path.join(HERE, "out", "door_voice.wav"), v)
    print("mix", len(v) / SR, "s")
