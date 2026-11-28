"""EP01 post: cold-open hook + SC001–SC005, Persian captions, branding, full ElevenLabs sound mix.

    python3 blender/zombie_center/episodes/ep01/post.py [preview]

Reads the rendered frames (out/sc00N/f_####.png, 1280x720; `preview` uses prev_####.png held for 2 frames),
the real event frames of SC003/SC004 (out/sc00N/events.json), the voices (audio/voice) and effects (audio/sfx).
Writes out/EP01/:
  EP01_final.mp4      captions + sound (the episode to publish)
  EP01_nocaptions.mp4 sound, no captions
  EP01_silent.mp4     captions, no sound (rule: always keep a version without sound)
  EP01_mix.wav, EP01_captions.srt
Branding on every frame: logo top-left, «مرکز زامبی‌ها · قسمت ۱» top-right (blender/brand/brand.py, no Blender credit).
Mix rules (CLAUDE.md): every line loudnorm -16, effects ducked ~13 dB under speech, phone colour light.
"""
import os, sys, json, glob, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "brand"))
from brand import overlay                                                         # noqa: E402

PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
FPS, W, H, SR = 24, 1280, 720, 48000
TITLE = "مرکز زامبی‌ها · قسمت ۱"
FONT = os.path.join(HERE, "..", "..", "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
OUT = os.path.join(HERE, "out", "EP01"); os.makedirs(OUT, exist_ok=True)
VO = os.path.join(HERE, "audio", "voice"); FX = os.path.join(HERE, "audio", "sfx")
ev3 = json.load(open(os.path.join(HERE, "out", "sc003", "events.json")))
ev4 = json.load(open(os.path.join(HERE, "out", "sc004", "events.json")))

# ---------------------------------------------------------------- the cut: (scene dir, first frame, last frame)
SCENES = [("sc001", 1, 1080), ("sc002", 1081, 2684), ("sc003", ev3["F0"], ev3["F1"]), ("sc004", ev4["G0"], ev4["G1"]),
          ("sc005", 1, 1919)]
HOOK = [("black", 0, int(0.8 * FPS)), ("sc001", 889, 922), ("video", 650, 702), ("sc001", 712, 745),
        ("sc001", 1030, 1053), ("title", 0, int(1.2 * FPS))]


def frame_path(scene, f):
    d = os.path.join(HERE, "out", scene)
    if not PREVIEW:
        return os.path.join(d, f"f_{f:04d}.png")
    g = f if f % 2 == 1 else f - 1                                               # previews: every 2nd frame
    return os.path.join(d, f"prev_{g:04d}.png")


def video_frame(f):
    v = Image.open(os.path.join(HERE, "out", "sc002_video", f"f_{f:04d}.png")).convert("RGB").resize((405, 720))
    im = Image.new("RGB", (W, H), (0, 0, 0)); im.paste(v, ((W - 405) // 2, 0))
    return im


def font(s):
    return ImageFont.truetype(FONT, s, layout_engine=ImageFont.Layout.RAQM)


timeline = []                                                                    # (kind, scene, frame) per output frame
starts = {}
for kind, a, b in HOOK:
    for f in range(a, b + 1):
        timeline.append((kind, f))
for sc, a, b in SCENES:
    starts[sc] = len(timeline) - a                                               # global frame = starts[sc] + scene frame
    for f in range(a, b + 1):
        timeline.append((sc, f))
N = len(timeline)
print("EP01 frames", N, "=", round(N / FPS, 1), "s")
G = lambda sc, f: (starts[sc] + f) / FPS                                         # scene frame -> seconds in the episode
HOOK_T = {"phone": 0.8, "video": 0.8 + 34 / FPS, "sniff": 0.8 + 34 / FPS + 53 / FPS, "eyes": 0.8 + (34 + 53 + 34) / FPS}
TITLE_T = (sum(b - a + 1 for _, a, b in HOOK[:-1])) / FPS

# ---------------------------------------------------------------- dialogue (file, who, episode seconds, caption)
V2S = 1249 - 1                                                                   # SC002 frame of Nika video frame 1 (minus 1)
LINES = [
    ("sc002_nika_04", "nika_video", HOOK_T["video"] + 0.05, "به هیچ‌کس اعتماد نکن، حتی به —"),
    ("sc001_arin_01", "arin", G("sc001", 1040), "نیکا؟"),
    ("sc002_nika_01", "nika_video", G("sc002", V2S + 14), "آرین... اگه اینو می‌بینی، یعنی بالاخره یکی کمکم کرد. من زنده‌م. همه‌ی این سال‌ها زنده بودم."),
    ("sc002_nika_02", "nika_video", G("sc002", V2S + 356), "اونا می‌گن دارم خوب می‌شم... دروغ می‌گن."),
    ("sc002_nika_03", "nika_video", G("sc002", V2S + 440), "مرکز... زیر تپه، آخر جاده‌ی معدن. بیا دنبالم. خواهش می‌کنم."),
    ("sc002_nika_04", "nika_video", G("sc002", V2S + 650), "به هیچ‌کس اعتماد نکن، حتی به —"),
    ("sc002_arin_02", "arin", G("sc002", 2451), "«همه‌ی این سال‌ها»... تو مُرده بودی."),
    ("sc003_arin_03", "arin", G("sc003", ev3["NO_LINE"]), "نه... نه!"),
    ("sc004_arin_04", "arin", G("sc004", ev4["G0"] + 24 * FPS), "چرا... ولم کرد؟"),
    ("sc004_arin_05", "arin", G("sc004", ev4["G0"] + int(37.6 * FPS)), "آخ —!"),
    ("sc005_operator", "phone", G("sc005", 1 + 32 * FPS), "«دستگاه مشترک مورد نظر در دسترس نمی‌باشد»"),
    ("sc005_mark_01", "mark", G("sc005", 1 + 40 * FPS), "آرین. پیامِ خواهرت رسید؟"),
    ("sc005_arin_06", "arin", G("sc005", 1 + int(43.4 * FPS)), "تو کی هستی؟ از کجا می‌دونی من کی‌ام؟"),
    ("sc005_mark_02", "mark", G("sc005", 1 + int(46.4 * FPS)), "قبل از طلوع برس به مرکز. جاده‌ی قدیمی معدن، بعد از سد. دمِ در فقط اسم کوچیکت رو بگو. هیچی بیشتر."),
    ("sc005_arin_07", "arin", G("sc005", 1 + int(55.4 * FPS)), "جوابمو بده! نیکا کجاست؟"),
    ("sc005_mark_03", "mark", G("sc005", 1 + int(58.6 * FPS)), "کسی که بهت بدهکاره."),
]
COLOUR = {"arin": (255, 255, 255), "nika_video": (190, 225, 255), "mark": (255, 205, 120), "phone": (200, 200, 200)}

# ---------------------------------------------------------------- effects (file, episode seconds, gain dB, loop seconds or 0)
e3, e4 = ev3, ev4
S1, S2, S3, S4, S5 = (lambda f: G("sc001", f)), (lambda f: G("sc002", f)), (lambda f: G("sc003", f)), (lambda f: G("sc004", f)), (lambda f: G("sc005", f))
END = N / FPS
FXC = [
    # hook
    ("sc001_phone_buzz", 0.0, -8, 0), ("sc001_arin_nose_breath", 0.1, -14, 0), ("hook_sub_hit", HOOK_T["phone"], -6, 0),
    ("sc001_z1_sniff", HOOK_T["sniff"], -8, 0), ("hook_sub_hit", TITLE_T, -3, 0), ("sc001_nika_motif_sting", TITLE_T + 0.1, -8, 0),
    # SC001–SC002: the avenue
    ("sc001_amb_avenue", S1(1), -20, S3(e3["F0"]) - S1(1)), ("sc001_bus_drips", S1(1), -24, S3(e3["F0"]) - S1(1)),
    ("sc001_phone_buzz", S1(1), -10, 0), ("sc001_car_alarm_far", S1(160), -22, 0),
    ("sc001_z1_drag_steps", S1(420), -16, 0), ("sc001_z1_sniff", S1(712), -10, 0), ("sc001_z1_drag_steps", S1(830), -20, 0),
    ("sc001_arin_nose_breath", S1(418), -18, S1(880) - S1(418)), ("sc001_nika_motif_sting", S1(905), -12, 0),
    ("sc002_room_vent", S2(1249), -27, S2(1964) - S2(1249)), ("sc002_lock_clack", S2(V2S + 605), -12, 0),
    ("sc001_nika_motif_sting", S2(2440), -18, 0), ("sc004_dog_far", S2(2230), -28, 0),
    # SC003: the chase
    ("sc001_amb_avenue", S3(e3["F0"]), -22, S5(1) - S3(e3["F0"])),
    ("sc003_driver_sprint", S3(e3["D_START"]), -12, S3(e3["PIN"]) - S3(e3["D_START"])),
    ("sc003_arin_run_steps", S3(e3["BOLT"]), -11, S3(e3["FALL"]) - S3(e3["BOLT"])),
    ("sc003_car_bump_alarm", S3(e3["BUMP"]), -8, 0), ("sc003_bonnet_vault", S3(e3["V0"]), -8, 0),
    ("sc003_driver_over_car", S3(e3["D_ARRIVE"]), -8, 0), ("sc003_trolley", S3(e3["R0"] + 14), -12, 0),
    ("sc003_cable_fall", S3(e3["FALL"]), -6, 0), ("sc003_phone_skid", S3(e3["FALL"] + 6), -10, 0),
    ("sc004_sniff_groan", S3(e3["PIN"] + 20), -8, 0),
    # SC004
    ("sc004_sniff_groan", S4(e4["G0"] + 2 * FPS), -8, 0), ("sc004_dog_far", S4(e4["G0"] + 13 * FPS), -16, 0),
    ("sc003_driver_sprint", S4(e4["G0"] + 16 * FPS), -16, 4.0), ("sc004_shudder_breath", S4(e4["G0"] + 19 * FPS), -14, 11.0),
    ("sc004_grab_kick", S4(e4["G0"] + int(32.6 * FPS)), -8, 0), ("sc004_glass_cut", S4(e4["G0"] + int(37.4 * FPS)), -8, 0),
    ("sc003_arin_run_steps", S4(e4["G0"] + int(39.2 * FPS)), -12, 5.0), ("sc004_crawler_drag", S4(e4["G0"] + int(35.6 * FPS)), -14, 9.0),
    # SC005: the pharmacy
    ("sc005_door_shove", S5(1 + 12), -8, 0), ("sc005_shelf_drag", S5(1 + 3 * FPS), -8, 0),
    ("sc005_tv_beep", S5(1 + 8 * FPS), -24, 72.0), ("sc005_disinfect_gauze", S5(1 + 15 * FPS), -10, 0),
    ("sc005_lullaby_hum", S5(1 + 24 * FPS), -12, 0), ("sc005_ring", S5(1 + 34 * FPS), -10, 0),
    ("sc005_call_drop", S5(1 + 62 * FPS), -10, 0), ("sc005_door_hits", S5(1 + int(77.4 * FPS)), -4, 0),
    ("sc001_nika_motif_sting", S5(1 + int(58.6 * FPS)), -16, 0),
]


def load(path, af=None):
    flt = ["-af", af] if af else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path] + flt + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def place(bus, x, t, gain_db, loop=0.0):
    a = int(t * SR)
    if loop > 0:
        n = int(loop * SR)
        reps = int(np.ceil(n / len(x))) + 1
        x = np.tile(x, reps)[:n]
        fade = min(len(x) // 4, SR)
        x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
    b = min(len(bus), a + len(x))
    if b > a > -1:
        bus[a:b] += x[:b - a] * (10 ** (gain_db / 20))


def mix():
    L = int(END * SR) + SR
    speech, fx = np.zeros(L, np.float32), np.zeros(L, np.float32)
    colour = {"mark": "highpass=f=320,lowpass=f=3300,asetrate=48000*0.95,aresample=48000,atempo=1.0526",   # light voice changer
              "nika_video": "highpass=f=180,lowpass=f=6500", "phone": "highpass=f=400,lowpass=f=3000", "arin": None}
    for name, who, t, _ in LINES:
        place(speech, load(os.path.join(VO, name + ".wav"), colour[who]), t, 0)
    for name, t, g, loop in FXC:
        place(fx, load(os.path.join(FX, name + ".mp3")), t, g, loop)
    env = np.convolve(np.abs(speech), np.ones(SR // 10) / (SR // 10), mode="same")
    duck = 1.0 - 0.78 * np.clip(env / 0.02, 0, 1)                                 # ≈ −13 dB under every line
    duck = np.convolve(duck, np.ones(SR // 8) / (SR // 8), mode="same")
    out = speech + fx * duck
    out /= max(1.0, float(np.abs(out).max()) / 0.95)
    p = os.path.join(OUT, "EP01_mix_raw.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", p],
                   input=out.astype(np.float32).tobytes(), check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR),
                    os.path.join(OUT, "EP01_mix.wav")], check=True)


_dur = {}


def dur(name):
    if name not in _dur:
        _dur[name] = len(load(os.path.join(VO, name + ".wav"))) / SR
    return _dur[name]


def caption_at(t):
    for name, who, t0, text in LINES:
        if t0 <= t <= t0 + dur(name) + 0.4:
            return who, text
    return None


def draw_caption(im, who, text):
    d = ImageDraw.Draw(im); f = font(34)
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f, direction="rtl", language="fa") > W * 0.8 and cur:
            lines.append(cur); cur = w
        else:
            cur = test
    lines.append(cur)
    y = H - 46 - 48 * (len(lines) - 1)
    for ln in lines:
        for dx, dy in ((2, 2), (-2, 2), (2, -2), (-2, -2), (0, 3)):
            d.text((W // 2 + dx, y + dy), ln, font=f, fill=(0, 0, 0), anchor="mm", direction="rtl", language="fa")
        d.text((W // 2, y), ln, font=f, fill=COLOUR[who], anchor="mm", direction="rtl", language="fa")
        y += 48


def picture(i):
    kind, f = timeline[i]
    if kind == "black":
        return Image.new("RGB", (W, H), (0, 0, 0))
    if kind == "title":
        im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((W // 2, H // 2 - 10), "مرکز زامبی‌ها", font=font(84), fill=(235, 235, 235), anchor="mm", direction="rtl", language="fa")
        d.text((W // 2, H // 2 + 70), "قسمت ۱", font=font(36), fill=(170, 30, 30), anchor="mm", direction="rtl", language="fa")
        return im
    if kind == "video":
        return video_frame(f)
    return Image.open(frame_path(kind, f)).convert("RGB").resize((W, H))


def encode(name, captions, sound):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if sound:
        cmd += ["-i", os.path.join(OUT, "EP01_mix.wav"), "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", os.path.join(OUT, name)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        im = picture(i)
        if captions:
            c = caption_at(i / FPS)
            if c:
                draw_caption(im, *c)
        overlay(im, TITLE)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()


def srt():
    def ts(t):
        return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(t * 1000 % 1000):03d}"
    with open(os.path.join(OUT, "EP01_captions.srt"), "w") as fh:
        for k, (name, who, t0, text) in enumerate(sorted(LINES, key=lambda l: l[2]), 1):
            d = dur(name)
            fh.write(f"{k}\n{ts(t0)} --> {ts(t0 + d + 0.4)}\n{text}\n\n")


if __name__ == "__main__":
    mix(); srt()
    encode("EP01_final.mp4", captions=True, sound=True)
    if not PREVIEW:
        encode("EP01_nocaptions.mp4", captions=False, sound=True)
        encode("EP01_silent.mp4", captions=True, sound=False)
    print("done", OUT)
