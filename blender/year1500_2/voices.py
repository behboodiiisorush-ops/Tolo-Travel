"""ElevenLabs voices of «سال ۱۵۰۰ — قسمت دوم» (voices/*.mp3, eleven_v3) on the timeline (captions.py).
    out/y2_voices.wav  voices alone (86 s film + 4 s card)
    out/y2_mix.wav     voices + ElevenLabs effects (out/y2_sfx.wav, ducked under the voices)
The speaker's line gets a small-shop-loudspeaker sound.                          python3 voices.py"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, CARD, END  # noqa: E402
OUT = os.path.join(HERE, "out")
V = os.path.join(HERE, "voices")
TOTAL = END + 4.0
FX = {"voice": "highpass=f=300,lowpass=f=4200,acrusher=bits=9:mix=0.2,aecho=0.8:0.6:60|120:0.35|0.2,volume=1.8,"}
TAKES = [(take, a, b + 0.3, FX.get(who, "")) for a, b, who, _, take in LINES] + [(CARD[1], CARD[0], TOTAL - 0.1, "")]
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")


def length(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    tmp = os.path.join(OUT, "vtmp")
    os.makedirs(tmp, exist_ok=True)
    parts = []
    for name, start, latest, fx in TAKES:
        a = os.path.join(tmp, name + "_t.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(V, name + ".mp3"), "-af", TRIM,
                        "-ar", "48000", "-ac", "1", a], check=True)
        d = length(a)
        tempo = max(1.0, d / (latest - start))
        b = os.path.join(tmp, name + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af",
                        f"{fx}atempo={tempo:.3f},afade=t=out:st={max(0, d / tempo - 0.06):.3f}:d=0.06,"
                        f"adelay={int(start * 1000)}", "-ar", "48000", "-ac", "1", b], check=True)
        print(f"{name}: {d:.2f}s at {start}s tempo {tempo:.2f}")
        parts.append(b)
    voices = os.path.join(OUT, "y2_voices.wav")
    ins = sum([["-i", p] for p in parts], [])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
                    f"amix=inputs={len(parts)}:normalize=0:duration=longest,apad=whole_dur={TOTAL},"
                    f"atrim=0:{TOTAL},loudnorm=I=-16:TP=-1.5,aformat=channel_layouts=stereo", "-ar", "48000", voices],
                   check=True)
    sfx = os.path.join(OUT, "y2_sfx.wav")
    if os.path.exists(sfx):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sfx, "-i", voices, "-filter_complex",
                        "[0:a]volume=0.7[s];[1:a]asplit[v1][v2];"
                        "[s][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[d];"
                        f"[d][v2]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95",
                        "-ar", "48000", os.path.join(OUT, "y2_mix.wav")], check=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)


if __name__ == "__main__":
    main()
