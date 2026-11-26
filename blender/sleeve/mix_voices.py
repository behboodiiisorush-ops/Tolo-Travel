"""Put the user's ElevenLabs voices on «آستین».
voices/all_lines_take1.mp3 holds every line back to back (one voice); CUTS says where each line is in it and
where it goes in the film. Mum (behind the hall doors) and the kids are pitched up, mum is also muffled.
    python3 mix_voices.py   -> out/sleeve_voices.mp4 (captions + voices + sound effects)
"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "voices", "all_lines_take1.mp3")
OUT = os.path.join(HERE, "out")
# (name, from, to in the take, start in the film, extra filter)
CUTS = [
    ("me_1", 0.00, 2.30, 0.8, "rubberband=pitch=1.08:formant=preserved"),
    ("card", 2.75, 6.15, 76.9, "rubberband=pitch=1.08:formant=preserved"),
    ("kazemi_2", 6.20, 8.55, 8.6, "highpass=f=250,lowpass=f=3400"),             # into the radio
    ("kazemi_7", 8.80, 10.30, 35.6, ""),
    ("kian_3", 10.40, 12.12, 12.9, "rubberband=pitch=1.3:formant=shifted"),
    ("soldier_4", 12.12, 14.35, 16.0, ""),
    ("soldier_8", 14.70, 16.60, 46.3, ""),
    ("soldier_9", 16.85, 22.05, 48.7, ""),
    ("mahsa_5", 22.15, 24.30, 24.3, "rubberband=pitch=1.45:formant=shifted"),
    ("arian_6", 24.80, 26.88, 31.0, "rubberband=pitch=1.08:formant=preserved"),
    ("mom_10", 26.88, 31.32, 67.8, "rubberband=pitch=1.42:formant=shifted,lowpass=f=2200,aecho=0.6:0.4:18:0.25"),
]


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    vdir = os.path.join(HERE, "voices")
    parts = []
    for name, a, b, t, flt in CUTS:
        out = os.path.join(vdir, f"{name}.wav")
        af = f"atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.06:.2f}:d=0.06"
        if flt:
            af += "," + flt
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", SRC, "-af", af, "-ar", "48000", "-ac", "2", out])
        parts.append((out, t))
    ins, chains = [], []
    for i, (p, t) in enumerate(parts):
        ins += ["-i", p]
        ms = int(t * 1000)
        chains.append(f"[{i + 2}:a]adelay={ms}|{ms}[v{i}]")
    n = len(parts)
    mix = ";".join(chains) + ";" + "".join(f"[v{i}]" for i in range(n)) + \
        f"amix=inputs={n}:normalize=0[voc];[1:a]volume=0.55[fx];[voc]volume=1.0[vo];[vo][fx]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95[a]"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "sleeve_captions.mp4"),
         "-i", os.path.join(OUT, "sleeve_sfx.wav")] + ins +
        ["-filter_complex", mix, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", os.path.join(OUT, "sleeve_voices.mp4")])
    print(os.path.join(OUT, "sleeve_voices.mp4"))


if __name__ == "__main__":
    main()
