"""Cut the lines of «واگن آخر ۳» out of the user's ElevenLabs export(s) into per-line clips.

    python3 cut_voices.py recording1.mp3 [recording2.mp3 ...]

Whisper (faster-whisper, word timestamps) transcribes the files; every caption is matched to
the stretch of words that reads most like it (lines may be recorded in any order).  Writes voices/clips/*.wav,
voices/clips.txt (start, end, speaker, file) for mix_voices.py, and lists lines it could not find.
"""
import difflib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES  # noqa: E402

OUT = os.path.join(HERE, "voices", "clips")


def norm(s):
    s = s.replace("ي", "ی").replace("ك", "ک").replace("‌", "")
    return re.sub(r"[^\w\s]", " ", s).split()


def transcribe(path):
    import numpy as np
    from faster_whisper import WhisperModel
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=2)
    segs, _ = model.transcribe(np.frombuffer(pcm, dtype=np.float32), language="fa", word_timestamps=True)
    words = []
    for s in segs:
        for w in s.words:
            for piece in norm(w.word):
                words.append((piece, w.start, w.end, path))
    return words


def main():
    words = []
    for src in sys.argv[1:]:
        words += transcribe(src)
    os.makedirs(OUT, exist_ok=True)
    rows, missing, used = [], [], set()
    for key, who, text in LINES:
        a, b = 0.0, 0.0
        target = " ".join(norm(text))
        n = len(target.split())
        best = (0.0, None)
        for i in range(len(words)):
            for m in (n - 1, n, n + 1, n + 2):
                if m < 1 or i + m > len(words) or len({w[3] for w in words[i:i + m]}) > 1 \
                        or used.intersection(range(i, i + m)):
                    continue
                r = difflib.SequenceMatcher(None, target, " ".join(w[0] for w in words[i:i + m])).ratio()
                if r > best[0]:
                    best = (r, (i, m))
        if best[0] < 0.55:
            missing.append(f"{key} {who}: {text}")
            continue
        i, m = best[1]
        used.update(range(i, i + m))
        s, e, src = words[i][1] - 0.08, words[i + m - 1][2] + 0.15, words[i][3]
        name = f"{key}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{max(0, s)}", "-t", f"{e - s}", "-i", src,
                        "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse", "-ar", "48000", "-ac", "1",
                        os.path.join(OUT, name)], check=True)
        rows.append((key, 0, who, name))
    with open(os.path.join(HERE, "voices", "clips.txt"), "w") as f:
        for a, b, who, name in rows:
            f.write(f"{a}\t{b}\t{who}\t{name}\n")
    print(len(rows), "clips")
    for m in missing:
        print("missing:", m)


if __name__ == "__main__":
    main()
