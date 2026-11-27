"""Sound for «سایه‌ی دانیال», all from ElevenLabs (the user's rule): voices/NN_who.mp3 (eleven_v4) and sfx/*.mp3
(eleven_text_to_sound_v3; room/flicker/drone/growl reused from blender/wall2/sfx). Voices start at their caption
times in lines.LINES, effects at the story beats; effects duck under the dialogue.
Writes out/sayeh_voice.wav and out/sayeh_mix.wav in VIDEO time: cold open (COLD of the film) + black card + film +
question card. sound.py (the old synthesised effects) is kept only for reference."""
import os, sys, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lines import LINES, END, COLD, COLD_CARD  # noqa: E402

SR = 48000
CARD = 4.0
VOICE_FILES = ["01_mother", "02_lina", "03_arian", "04_father", "05_daniel", "06_daniel"]   # in LINES order
PITCH = {"daniel": 2.0, "lina": 3.0, "arian": 1.5}       # children / teenagers a little younger (semitones)


def decode(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", ",".join(af)]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def add(track, x, t, g=1.0, fade_out=0.0, max_len=None, fade_in=0.0):
    x = x.copy()
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
    """Seconds of silence before the speech starts."""
    k = np.argmax(np.abs(x) > thr * np.abs(x).max())
    return k / SR


def film_tracks():
    n = int((END + 1.0) * SR)
    voice = np.zeros(n, np.float32)
    for (a, b, who, text), name in zip(LINES, VOICE_FILES):
        af = []
        if PITCH.get(who):
            af.append(f"rubberband=pitch={2 ** (PITCH[who] / 12):.4f}:formant=preserved")
        x = decode(os.path.join(HERE, "voices", name + ".mp3"), af)
        x /= max(1e-4, np.abs(x).max())
        add(voice, x * 0.85, max(0.0, a - lead(x) + 0.05))
    def S(nm):                                                       # every effect peak-normalised, then gained
        x = decode(os.path.join(HERE, "sfx", nm + ".mp3"))
        return x / max(1e-4, np.abs(x).max())
    fx = np.zeros_like(voice)
    room = S("room")
    add(fx, room, 0.0, 0.08, fade_out=0.5, max_len=7.3)               # evening room tone until the power dies
    add(fx, S("steps"), 0.5, 0.55, fade_out=0.6, max_len=3.0)          # Daniel walks in
    fl = S("flicker")
    add(fx, fl, 5.0, 0.6, max_len=2.2, fade_out=0.2)                   # the lights fail
    add(fx, S("powerout"), 6.9, 0.7, max_len=2.5, fade_out=0.8)        # ...and die
    drone = S("drone")
    for k, t in enumerate((7.6, 16.6)):                                # dark drone under the blackout
        add(fx, drone, t, 0.45, fade_in=1.0 if k == 0 else 0.5, fade_out=1.0, max_len=10.0)
    add(fx, S("whoosh"), 8.6, 0.8, fade_out=0.5)                       # the Shadow in the doorway
    heart = S("heart")
    add(fx, heart, 9.5, 0.55, fade_in=1.0, fade_out=1.0, max_len=15.0)
    add(fx, S("growl"), 13.0, 0.35, fade_in=0.3, fade_out=1.0, max_len=3.5)
    add(fx, S("ring"), 17.3, 0.45, fade_in=0.2, fade_out=1.0, max_len=4.0)   # Daniel looks down: no shadow
    add(fx, S("creep"), 22.6, 0.6, fade_in=0.2, fade_out=0.8, max_len=4.2)   # the Shadow walks up
    add(fx, S("flash"), 26.9, 0.95, fade_out=0.8)                      # the white flash
    add(fx, room, 28.0, 0.07, fade_in=1.0, fade_out=1.5, max_len=4.0)  # the room comes back
    env = np.convolve(np.abs(voice), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1.0 - 0.55 * np.clip(env / (env.max() * 0.25 + 1e-6), 0, 1)
    return voice, fx * duck


def to_video(film, boom):
    a, b = int(COLD[0] * SR), int(COLD[1] * SR)
    cold = film[a:b].copy()
    cold[-int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR))
    gap = np.zeros(int(COLD_CARD[0] * SR), np.float32)
    add(gap, boom, 0.0, 0.9)
    body = film[:int(END * SR)].copy()
    body[:int(0.2 * SR)] *= np.linspace(0, 1, int(0.2 * SR))
    card = np.zeros(int(CARD * SR), np.float32)
    add(card, film[int(END * SR):], 0.0, 1.0, fade_out=0.8)
    return np.concatenate([cold, gap, body, card])


def write(path, x):
    x = x / max(1e-6, np.abs(x).max()) * 0.89
    st = np.stack([x, x], 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", path],
                   input=st.tobytes(), check=True)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    voice, fx = film_tracks()
    boom = decode(os.path.join(HERE, "sfx", "boom.mp3"))
    mix = to_video(voice + fx, boom)
    write(os.path.join(HERE, "out", "sayeh_mix.wav"), mix)
    write(os.path.join(HERE, "out", "sayeh_voice.wav"), to_video(voice, boom * 0))
    print("mix", len(mix) / SR, "s")
