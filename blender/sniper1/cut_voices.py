"""Cut the lines of «تک‌تیرانداز ۱» out of the user's ElevenLabs export(s) into per-line clips.

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


def silences(path, noise="-40dB", dur=0.12):
    """[(start, end)] of the pauses in a recording."""
    err = subprocess.run(["ffmpeg", "-i", path, "-af", f"silencedetect=noise={noise}:d={dur}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    out, start = [], None
    for line in err.splitlines():
        if "silence_start:" in line:
            start = float(line.split("silence_start:")[1].split()[0])
        elif "silence_end:" in line and start is not None:
            out.append((start, float(line.split("silence_end:")[1].split()[0])))
            start = None
    return out


def main():
    words = []
    for src in sys.argv[1:]:
        words += transcribe(src)
    os.makedirs(OUT, exist_ok=True)
    found, missing, used = {}, [], set()
    for key, who, text in LINES:
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
        found[key] = (words[i][1], words[i + m - 1][2], words[i][3], who)
    # Whisper's word times are rough, so cut in the silences between lines: for every line, start
    # in the middle of the pause before its first word and end in the middle of the pause after
    # its last word (pauses found with ffmpeg silencedetect).
    by_src = {}
    for key, (a, b, src, who) in found.items():
        by_src.setdefault(src, []).append((a, b, key))
    cuts = {}
    for src, items in by_src.items():
        sil = silences(src)
        items.sort()
        bounds = []
        for (a0, b0, k0), (a1, b1, k1) in zip(items, items[1:]):
            lo, hi = b0 - 0.8, a1 + 0.8          # where the gap between the two lines must be
            cand = [(e - s_, (s_ + e) / 2) for s_, e in sil if s_ > a0 + 0.2 and e < b1 - 0.2 and e > lo and s_ < hi]
            mid = max(cand)[1] if cand else (b0 + a1) / 2   # the longest pause in that window
            bounds.append(mid)
        for j, (a, b, key) in enumerate(items):
            start = bounds[j - 1] if j > 0 else max(0.0, a - 0.3)
            end = bounds[j] if j < len(bounds) else b + 0.4
            cuts[key] = (start, end, src)
    rows = []
    for key, who, text in LINES:
        if key not in cuts:
            continue
        start, end, src = cuts[key]
        name = f"{key}.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{start}", "-t", f"{end - start}", "-i", src,
                        "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                               "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                               "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse",
                        "-ar", "48000", "-ac", "1", os.path.join(OUT, name)], check=True)
        rows.append((key, 0, who, name))
        print(f"{key:7s} {start:6.2f}-{end:6.2f}", flush=True)
    with open(os.path.join(HERE, "voices", "clips.txt"), "w") as f:
        for a, b, who, name in rows:
            f.write(f"{a}\t{b}\t{who}\t{name}\n")
    print(len(rows), "clips")
    for m in missing:
        print("missing:", m)


if __name__ == "__main__":
    main()
