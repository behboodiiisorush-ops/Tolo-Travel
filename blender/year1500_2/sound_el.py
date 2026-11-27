"""Sound effects of «سال ۱۵۰۰ — قسمت دوم», all real ElevenLabs clips (sfx_el/*.mp3), placed on the frame they
belong to (door / bread times come from timing.txt, written by scene.py) -> out/y2_sfx.wav (86 s + 4 s card).
voices.py then mixes the voices on top (out/y2_mix.wav).                          python3 sound_el.py"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sfx_el")
TOTAL = 90.0
TM = {}
for line in open(os.path.join(HERE, "timing.txt")):
    k, v = line.split()
    TM[k] = float(v)
DOOR, BREAD = TM["door_touch"], TM["bread_grab"]
# clip, start (s), volume, extra filter on the clip's own time
CUES = [
    ("wind", 0.0, 1.0, "aloop=loop=3:size=1440000,atrim=0:90,volume='if(between(t,35.5,60),0.08,0.32)':eval=frame,"),
    ("steps", 7.0, 0.42, "atrim=0:12,afade=t=out:st=11.2:d=0.8,"),
    ("creak", 19.4, 0.7, ""),
    ("whisper", 23.6, 0.55, "afade=t=in:d=0.6,"),
    ("canroll", 22.4, 0.65, ""),
    ("steps", 30.0, 0.4, "atrim=0:7.6,afade=t=out:st=7.0:d=0.6,"),
    ("shophum", 35.0, 0.5, "afade=t=in:d=1.5,afade=t=out:st=13.5:d=1.5,"),
    ("shophum", 49.5, 0.5, "atrim=0:10,afade=t=out:st=9:d=1,"),
    ("bread", BREAD - 0.1, 0.8, ""),
    ("cangrab", 43.2, 0.9, ""),
    ("speakeron", 49.9, 0.9, ""),
    ("heart", 52.0, 0.55, "afade=t=out:st=5:d=1,"),
    ("run", 59.3, 0.75, ""),
    ("steps", 65.0, 0.18, "atrim=0:6.6,afade=t=out:st=6:d=0.6,"),        # the man, far away
    ("doorhandle", DOOR - 0.05, 0.8, ""),
    ("dooropen", DOOR + 0.2, 0.8, ""),
    ("doorslam", 79.1, 1.0, ""),
    ("drone", 76.0, 0.55, "afade=t=in:d=3,afade=t=out:st=12:d=2,"),
]


def main():
    ins, parts = [], []
    for i, (name, start, vol, fx) in enumerate(CUES):
        ins += ["-i", os.path.join(SRC, name + ".mp3")]
        parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,{fx}volume={vol},"
                     f"adelay={int(start * 1000)}:all=1[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(CUES)))
    graph = ";".join(parts) + f";{mix}amix=inputs={len(CUES)}:normalize=0:duration=longest," \
                              f"apad=whole_dur={TOTAL},atrim=0:{TOTAL},alimiter=limit=0.89"
    out = os.path.join(HERE, "out", "y2_sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", graph, "-ar", "48000", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
