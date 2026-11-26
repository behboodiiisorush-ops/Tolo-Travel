"""The ElevenLabs voices of «سال ۱۵۰۰» (voices/*.mp3, eleven_v3) placed on the film's timeline.
    out/year1500_voices.wav   the voices alone (film + question card, 76 s)
    out/year1500_mix.wav      voices + the synthesised sound effects (ducked under the voices)
Each take is trimmed of silence, sped up a little only when it would run into the next line,
and mom's line from the broken screen gets a small-speaker sound.          python3 voices.py"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
V = os.path.join(HERE, "voices")
TOTAL = 76.0
# file, start (s), latest end (s), extra filter
TAKES = [
    ("01_me", 0.8, 7.45, ""),
    ("02_me", 7.2, 12.15, ""),
    ("03_mom", 12.25, 15.25, ""),
    ("04_me", 15.4, 23.0, ""),
    ("05_kian", 23.2, 26.85, ""),
    ("06_kian", 27.0, 35.8, ""),
    ("07_mom", 36.0, 44.2, "highpass=f=350,lowpass=f=3800,acrusher=bits=10:mix=0.25,aecho=0.8:0.5:40:0.25,volume=2.4,"),
    ("08_kian", 44.4, 49.45, ""),
    ("09_me", 49.6, 55.8, ""),
    ("10_me", 56.0, 71.2, ""),
    ("11_card", 72.0, 75.95, ""),
]
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")


def length(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main():
    tmp = os.path.join(OUT, "vtmp")
    os.makedirs(tmp, exist_ok=True)
    parts = []
    for name, start, latest, fx in TAKES:
        src = os.path.join(V, name + ".mp3")
        a = os.path.join(tmp, name + "_t.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", TRIM, "-ar", "48000", "-ac", "1", a], check=True)
        d = length(a)
        tempo = max(1.0, d / (latest - start))
        b = os.path.join(tmp, name + ".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af",
                        f"{fx}atempo={tempo:.3f},afade=t=out:st={max(0, d / tempo - 0.06):.3f}:d=0.06,"
                        f"adelay={int(start * 1000)}", "-ar", "48000", "-ac", "1", b], check=True)
        print(f"{name}: {d:.2f}s at {start}s, tempo {tempo:.2f}")
        parts.append(b)
    voices = os.path.join(OUT, "year1500_voices.wav")
    ins = sum([["-i", p] for p in parts], [])
    n = len(parts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
                    f"amix=inputs={n}:normalize=0:duration=longest,apad=whole_dur={TOTAL},"
                    f"atrim=0:{TOTAL},loudnorm=I=-16:TP=-1.5,aformat=channel_layouts=stereo",
                    "-ar", "48000", voices], check=True)
    sfx = os.path.join(OUT, "year1500_sfx.wav")
    if os.path.exists(sfx):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sfx, "-i", voices, "-filter_complex",
                        "[0:a]volume=0.7[s];[1:a]asplit[v1][v2];"
                        "[s][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[d];"
                        f"[d][v2]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95",
                        "-ar", "48000", os.path.join(OUT, "year1500_mix.wav")], check=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    print("voices ->", voices)


if __name__ == "__main__":
    main()
