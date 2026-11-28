"""Transcribe the final voiced mix with faster-whisper (small, fa) and compare each line with its caption.
    HF_HUB_DISABLE_XET=1 python3 qc_whisper.py  ->  out/qc_whisper.txt"""
import difflib, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from captions import LINES, KEY_OF  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402
SR = 16000
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(HERE, "out", "voice.wav"), "-ac", "1", "-ar", str(SR),
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.float32)
model = WhisperModel("small", device="cpu", compute_type="int8")


def norm(s):
    s = re.sub(r"[^؀-ۿ ]", " ", s.replace("‌", "").replace("ي", "ی").replace("ك", "ک"))
    return " ".join(s.split())


rows, bad = [], []
ONLY = sys.argv[1:]
for key, who, text in LINES:
    if ONLY and key not in ONLY:
        continue
    a, b = KEY_OF[key]
    seg = audio[int((a - 0.2) * SR):int((b + 0.3) * SR)]
    out = " ".join(s.text for s in model.transcribe(seg, language="fa", beam_size=5, vad_filter=False)[0])
    r = difflib.SequenceMatcher(None, norm(text), norm(out)).ratio()
    rows.append(f"{key:7s} {r:.2f}  | {norm(text)}  ->  {norm(out)}")
    if r < 0.6:
        bad.append(key)
rep = "\n".join(rows) + f"\n\nlow (<0.60): {bad}\n"
open(os.path.join(HERE, "out", "qc_whisper.txt"), "w").write(rep)
print(rep)
