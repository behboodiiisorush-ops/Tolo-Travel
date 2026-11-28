"""Sound for «صدای رادیو»: the ElevenLabs voices (voices/) + the ElevenLabs sound effects (sfx/), one effect per action.
Every line is loudness-matched (loudnorm -16), the boys pitched gently with formants kept, the radio / tape voice
lightly coloured, and the effects ducked ~13 dB under every line.
    python3 sound.py   -> out/radio_mix.wav (film + question card)
"""
import os, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
from captions import LINES, FILES, END, CARD_VOICE  # noqa: E402
SR = 48000
CARD = 5.6
TOTAL = END + CARD
OUT = os.path.join(HERE, "out")
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")      # same trim as lipsync.py
PITCH = {"me": "rubberband=pitch=1.1225:formant=preserved",                     # +2 semitones
         "kian": "rubberband=pitch=1.189:formant=preserved"}                    # +3 semitones
COLOUR = {"radio": "highpass=f=280,lowpass=f=4800,volume=0.95",
          "tape": "highpass=f=220,lowpass=f=5200,aecho=0.8:0.5:25:0.18"}


def load(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()


def place(track, clip, t, gain_db=0.0, length=None, fade_in=0.02, fade_out=0.05):
    a = int(t * SR)
    if length:
        clip = clip[:int(length * SR)]
    clip = clip * (10 ** (gain_db / 20))
    n = len(clip)
    fi, fo = int(fade_in * SR), int(fade_out * SR)
    if fi:
        clip[:fi] *= np.linspace(0, 1, min(fi, n))[:, None]
    if fo:
        clip[-fo:] *= np.linspace(1, 0, min(fo, n))[:, None]
    b = min(len(track), a + n)
    track[a:b] += clip[:b - a]


def main():
    n = int(TOTAL * SR) + SR
    voc = np.zeros((n, 2), np.float32)
    fx = np.zeros((n, 2), np.float32)
    # ---- voices
    lines = [(a, who, f) for (a, b, who, _), f in zip(LINES, FILES)] + [(END + 1.0, "me", CARD_VOICE)]
    for t, who, f in lines:
        flt = [TRIM]
        if who in PITCH:
            flt.append(PITCH[who])
        flt.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        if who in COLOUR:
            flt.append(COLOUR[who])
        place(voc, load(os.path.join(HERE, "voices", f + ".mp3"), ",".join(flt)), t)
    # ---- effects (start, file, gain dB, length s, fade in, fade out)
    S = lambda name: load(os.path.join(HERE, "sfx", name + ".mp3"))
    road = S("road_night")
    room = S("room_clock")
    for t, clip, g, ln, fi, fo in [
        (0.0, S("engine_dies"), -3, 6.0, 0.02, 1.0),
        (0.0, road, -24, 25.0, 1.0, 0.5),                 # wind outside the car, very low
        (5.6, S("radio_static"), -12, 4.6, 0.3, 0.6),
        (18.8, S("hatch_open"), -5, 2.6, 0.02, 0.4),
        (20.3, S("tiptoe_steel"), -9, 4.7, 0.3, 0.4),
        (25.0, road, -8, 13.0, 0.4, 1.5),
        (25.2, S("steps_asphalt"), -9, 7.8, 0.3, 0.6),
        (33.9, S("front_door"), -4, 4.0, 0.02, 0.5),
        (38.0, room, -16, END - 38.0, 0.6, 0.4),
        (38.5, S("tape_play"), -8, 4.0, 0.02, 0.6),
        (54.0, S("heartbeat"), -10, END - 54.0 + 2.0, 2.0, 1.5),
        (59.5, S("back_door"), -2, 5.0, 0.02, 0.8),
    ]:
        place(fx, clip, t, g, ln, fi, fo)
    # ---- duck the effects ~13 dB under every line (smoothed envelope of the voice track)
    env = np.abs(voc).max(axis=1)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    on = (env > 0.01).astype(np.float32)
    on = np.convolve(on, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same")
    gain = 1.0 - (1.0 - 10 ** (-13 / 20)) * np.clip(on, 0, 1)
    mix = voc + fx * gain[:, None]
    mix = mix[:int(TOTAL * SR)]
    peak = np.abs(mix).max()
    if peak > 0.95:
        mix *= 0.95 / peak
    os.makedirs(OUT, exist_ok=True)
    wav = os.path.join(OUT, "radio_mix.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s16le", wav], input=mix.astype(np.float32).tobytes(), check=True)
    # check: speech >= 10 dB above the effects while someone talks
    m = on > 0.9
    if m.any():
        sv = 20 * np.log10(np.sqrt(np.mean(voc[:len(on)][m] ** 2)) + 1e-9)
        sf = 20 * np.log10(np.sqrt(np.mean((fx[:len(on)] * gain[:, None])[m] ** 2)) + 1e-9)
        print(f"speech {sv:.1f} dB, effects under speech {sf:.1f} dB, margin {sv - sf:.1f} dB")
    print(wav)


if __name__ == "__main__":
    main()
