"""Put the user's ElevenLabs voices on «آستین».
voices/all_lines_take1.mp3 holds every line back to back (one voice); CUTS says where each line is in it and
where it goes in the film. Mum is muffled (behind the hall doors); Kian is pitched up a little.
    python3 mix_voices.py   -> out/sleeve_voices.mp4 (captions + voices + sound effects)
"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "voices", "all_lines_take2.mp3")
OUT = os.path.join(HERE, "out")
# (name, from, to in the take, start in the film, extra filter)
CUTS = [
    ("me_1", 0.00, 2.25, 0.8, ""),
    ("card", 2.55, 5.98, 76.9, ""),
    ("kazemi_2", 6.15, 8.60, 8.6, "highpass=f=250,lowpass=f=3400"),             # into the radio
    ("kazemi_7", 8.95, 10.20, 35.6, ""),
    ("kian_3", 10.35, 12.18, 12.9, "rubberband=pitch=1.25:formant=shifted"),
    ("soldier_4", 12.18, 14.40, 16.0, ""),
    ("soldier_8", 14.75, 16.55, 46.3, ""),
    ("soldier_9", 16.70, 21.75, 48.7, ""),
    ("mahsa_5", 21.95, 24.00, 24.3, ""),
    ("arian_6", 24.10, 26.60, 31.0, ""),
    ("mom_10", 26.60, 31.16, 67.8, "lowpass=f=2600,aecho=0.6:0.4:18:0.25"),      # behind the hall doors
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
