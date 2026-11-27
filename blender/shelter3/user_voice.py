"""The user's own recording (one take, all 38 lines in voice_script order) -> voices/clips/<key>.wav,
each line fitted into its slot in the existing film (times.py stays as it is: no re-render)."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import KEY_OF  # noqa: E402
SRC = os.path.join(HERE, "user_voice", "mard_v4.mp3")
# line -> (start, end) in the take, from the whisper transcript (user_voice/transcript.txt)
SEG = [("n1", 0.00, 4.52), ("n2", 4.88, 8.48), ("me1", 8.80, 14.00), ("me2", 14.32, 15.68), ("n3", 15.96, 19.96),
       ("n4", 20.24, 23.80), ("me3", 24.12, 25.72), ("me4", 26.08, 28.08), ("n5", 28.52, 31.40), ("me5", 31.72, 33.16),
       ("n6", 33.56, 37.28), ("me6", 37.60, 38.80), ("n7", 39.16, 43.72), ("lena1", 44.04, 47.40),
       ("lena2", 47.76, 50.76), ("lena3", 51.12, 52.32), ("lena4", 52.76, 54.84), ("lena5", 55.24, 57.24),
       ("mom1", 57.76, 59.76), ("mom2", 60.24, 62.92), ("mom3", 63.48, 65.28), ("mom4", 65.72, 67.52),
       ("mom5", 67.88, 70.72), ("guard1", 70.96, 73.84), ("guard2", 74.20, 76.20), ("guard3", 76.48, 79.52),
       ("resc1", 79.76, 83.56), ("resc2", 83.76, 86.52), ("resc3", 86.72, 90.24), ("resc4", 90.48, 93.24),
       ("resc5", 93.48, 96.36), ("resc6", 96.52, 98.36), ("resc7", 98.52, 101.28), ("old1", 102.76, 107.76),
       ("old2", 108.16, 114.04), ("old3", 114.40, 118.20), ("radio1", 118.48, 123.32), ("radio2", 123.48, 126.19)]
SPEAKER = "highpass=f=220,lowpass=f=6000,aecho=0.8:0.35:80:0.18"
RADIO = "highpass=f=280,lowpass=f=4800,acrusher=bits=14:mix=0.06"
EXTRA = {"resc1": SPEAKER, "resc2": SPEAKER, "radio1": RADIO, "radio2": RADIO}
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
SQUEEZE = {"old1": (104.05, 104.95)}   # cut [104.05, 104.95] out of the take
MAXFIT = 1.3   # never speed a line up more than this


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


out_dir = os.path.join(HERE, "voices", "clips")
os.makedirs(out_dir, exist_ok=True)
# cut at the middle of each pause so no word is clipped
for i, (k, a, b) in enumerate(SEG):
    a0 = 0.0 if i == 0 else (SEG[i - 1][2] + a) / 2
    b0 = b + 0.15 if i == len(SEG) - 1 else (b + SEG[i + 1][1]) / 2
    tmp = os.path.join("/tmp", f"uv_{k}.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a0:.3f}", "-to", f"{b0:.3f}", "-i", SRC, "-af", TRIM,
                    "-ar", "48000", "-ac", "1", tmp], check=True)
    if k in SQUEEZE:                           # drop the long pause inside the line: two parts, 0.3 s apart
        (pa, pb), sq = SQUEEZE[k], tmp.replace(".wav", "_sq.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a0:.3f}", "-to", f"{pa:.3f}", "-i", SRC,
                        "-ss", f"{pb:.3f}", "-to", f"{b0:.3f}", "-i", SRC, "-filter_complex",
                        "[0:a]apad=pad_dur=0.3[x];[x][1:a]concat=n=2:v=0:a=1," + TRIM, "-ar", "48000", "-ac", "1", sq],
                       check=True)
        tmp = sq
    d, (s, e) = dur(tmp), KEY_OF[k]
    slot = (e - s) + 0.35                      # the line's slot in the film (+ the usual gap)
    af = []
    if d > slot:
        af.append(f"rubberband=tempo={min(MAXFIT, d / slot):.4f}:formant=preserved")
    if k in EXTRA:
        af.append(EXTRA[k])
    af += ["loudnorm=I=-16:TP=-1.5:LRA=11", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.05,areverse"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", ",".join(af), "-ar", "48000", "-ac", "1",
                    os.path.join(out_dir, k + ".wav")], check=True)
    nd = dur(os.path.join(out_dir, k + ".wav"))
    print(f"{k:7s} take {d:4.2f}s  slot {slot:4.2f}s  -> {nd:4.2f}s{'  (sped up)' if d > slot else ''}")
