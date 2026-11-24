"""
Automatic Persian captions for any video.

The speech is turned into text by Whisper (runs on this computer, no API key),
saved as an .srt file you can fix by hand, then burned onto the video with the
Vazirmatn font (Pillow + raqm, so Persian letters join correctly right-to-left).

    python3 subtitle.py film.mp4                  # transcribe + burn -> out/film_fa.srt, out/film_captioned.mp4
    python3 subtitle.py film.mp4 --only-srt       # just make out/film_fa.srt, to correct it first
    python3 subtitle.py film.mp4 --srt fixed.srt  # burn your corrected .srt (no transcription)

Options: --model large-v3-turbo (default, best Persian) | small (much faster, more mistakes), --words 5 (max words
per caption), --pos 0.72 (caption height, 0 = top, 1 = bottom), --size 1.0 (text size), --audio
voice.wav (transcribe this audio instead of the video's own sound track).
Needs ffmpeg, Pillow with raqm, and `pip install faster-whisper`.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont, features

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "blender", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
OUT = os.path.join(HERE, "out")
# The Hugging Face "xet" download host is blocked on some networks; the plain one works.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")


# ---------------------------------------------------------------- video info

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:format=duration", "-of", "json", path],
                       capture_output=True, text=True, check=True)
    info = json.loads(r.stdout)
    s = info["streams"][0]
    return s["width"], s["height"], float(info["format"]["duration"])


# ---------------------------------------------------------------- speech -> text

def normalize(text):
    """Whisper often writes Arabic ي / ك; use the Persian letters."""
    text = text.replace("ي", "ی").replace("ك", "ک").replace("ى", "ی")
    text = re.sub(r"(?<!\S)(ن?می) (?=\S)", "\\1\u200c", text)  # «می رفتم» -> «می‌رفتم»
    return re.sub(r"\s+", " ", text).strip()


def load_audio(media):
    """16 kHz mono samples, decoded by ffmpeg (avoids PyAV version problems)."""
    import numpy as np

    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", media, "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def transcribe(media, model_name, max_words):
    from faster_whisper import WhisperModel

    print(f"loading Whisper model «{model_name}» (first time downloads it)...")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(load_audio(media), language="fa", word_timestamps=True, vad_filter=True,
                                   beam_size=5)
    cues = []
    for seg in segments:
        words = [w for w in (seg.words or []) if w.word.strip()]
        if not words:
            if seg.text.strip():
                cues.append([seg.start, seg.end, normalize(seg.text)])
            continue
        chunk = []
        for w in words:
            chunk.append(w)
            long_enough = len(chunk) >= max_words or chunk[-1].end - chunk[0].start > 3.2
            if long_enough or w is words[-1]:
                cues.append([chunk[0].start, chunk[-1].end, normalize("".join(x.word for x in chunk))])
                chunk = []
        print(f"  {seg.end:6.1f}s  {normalize(seg.text)}")
    # keep each caption on screen a little longer, but never over the next one
    for i, c in enumerate(cues):
        nxt = cues[i + 1][0] if i + 1 < len(cues) else c[1] + 1.0
        c[1] = max(c[1], min(c[1] + 0.35, nxt - 0.02))
    return [c for c in cues if c[2]]


# ---------------------------------------------------------------- .srt files

def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(cues, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, text) in enumerate(cues, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n")


def read_srt(path):
    def sec(s):
        h, m, rest = s.strip().replace(".", ",").split(":")
        s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

    cues = []
    with open(path, encoding="utf-8-sig") as f:
        blocks = re.split(r"\n\s*\n", f.read().strip())
    for block in blocks:
        lines = [x for x in block.splitlines() if x.strip()]
        for i, line in enumerate(lines):
            if "-->" in line:
                a, b = line.split("-->")
                cues.append([sec(a), sec(b), "\n".join(lines[i + 1:])])
                break
    return cues


# ---------------------------------------------------------------- drawing

class Painter:
    def __init__(self, w, h, pos, size):
        self.w, self.h, self.pos = w, h, pos
        self.font = ImageFont.truetype(FONT, int(min(w, h) * 0.075 * size),
                                       layout_engine=ImageFont.Layout.RAQM)
        self.stroke = max(3, int(self.font.size * 0.11))

    def text_width(self, d, text):
        l, _, r, _ = d.textbbox((0, 0), text, font=self.font, direction="rtl", language="fa")
        return r - l

    def wrap(self, d, text):
        lines = []
        for para in text.split("\n"):
            line = ""
            for word in para.split():
                trial = f"{line} {word}".strip()
                if line and self.text_width(d, trial) > self.w * 0.86:
                    lines.append(line)
                    line = word
                else:
                    line = trial
            if line:
                lines.append(line)
        return "\n".join(lines)

    def card(self, text):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.multiline_text((self.w // 2, int(self.h * self.pos)), self.wrap(d, text), font=self.font,
                         fill=(255, 255, 255, 255), anchor="mm", align="center", direction="rtl",
                         language="fa", stroke_width=self.stroke, stroke_fill=(15, 15, 15, 255),
                         spacing=int(self.font.size * 0.25))
        return img


# ---------------------------------------------------------------- burn

def burn(video, cues, out_path, pos, size):
    w, h, duration = probe(video)
    painter = Painter(w, h, pos, size)
    tmp = tempfile.mkdtemp(prefix="captions_")
    try:
        blank = os.path.join(tmp, "blank.png")
        Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(blank)
        # a timeline of still images: blank between captions, one picture per caption
        entries, t = [], 0.0
        for i, (a, b, text) in enumerate(sorted(cues)):
            a, b = max(a, t), min(b, duration)
            if b <= a:
                continue
            if a > t:
                entries.append((blank, a - t))
            png = os.path.join(tmp, f"c_{i:04d}.png")
            painter.card(text).save(png)
            entries.append((png, b - a))
            t = b
        entries.append((blank, max(0.04, duration - t)))
        listing = os.path.join(tmp, "list.txt")
        with open(listing, "w") as f:
            f.write("ffconcat version 1.0\n")
            for path, dur in entries:
                f.write(f"file '{path}'\nduration {dur:.3f}\n")
            f.write(f"file '{blank}'\n")
        subprocess.run([
            "ffmpeg", "-loglevel", "error", "-y", "-i", video,
            "-f", "concat", "-safe", "0", "-i", listing,
            "-filter_complex", "[1:v]format=rgba[s];[0:v][s]overlay=0:0:eof_action=pass:format=auto[v]",
            "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-c:a", "copy", "-movflags", "+faststart", out_path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description="Automatic Persian captions (Whisper + Vazirmatn).")
    p.add_argument("video")
    p.add_argument("--srt", help="use this (corrected) .srt instead of transcribing")
    p.add_argument("--only-srt", action="store_true", help="only write the .srt, do not burn")
    p.add_argument("--audio", help="transcribe this audio file instead of the video's sound")
    p.add_argument("--model", default="large-v3-turbo", help="large-v3-turbo (default), small (faster), large-v3")
    p.add_argument("--words", type=int, default=5, help="max words per caption (default 5)")
    p.add_argument("--pos", type=float, default=0.72, help="caption height 0..1 (default 0.72)")
    p.add_argument("--size", type=float, default=1.0, help="text size multiplier (default 1.0)")
    p.add_argument("--out", help="output video path")
    args = p.parse_args()

    if not features.check("raqm"):
        sys.exit("Pillow needs raqm for Persian text (pip install --force-reinstall pillow).")
    if not os.path.exists(args.video):
        sys.exit(f"not found: {args.video}")
    os.makedirs(OUT, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.video))[0]

    if args.srt:
        cues = read_srt(args.srt)
    else:
        cues = transcribe(args.audio or args.video, args.model, args.words)
        srt_path = os.path.join(OUT, f"{stem}_fa.srt")
        write_srt(cues, srt_path)
        print(f"captions: {srt_path}  ({len(cues)} lines)")
    if not cues:
        sys.exit("no speech found.")
    if args.only_srt:
        return
    out_path = args.out or os.path.join(OUT, f"{stem}_captioned.mp4")
    burn(args.video, cues, out_path, args.pos, args.size)
    print(f"video:    {out_path}")


if __name__ == "__main__":
    main()
