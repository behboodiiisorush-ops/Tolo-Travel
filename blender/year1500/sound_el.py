"""Sound effects of «سال ۱۵۰۰» from ElevenLabs (sfx_el/*.mp3, eleven_text_to_sound_v2) placed on the timeline
-> out/year1500_sfx.wav (76 s: film + question card). Replaces the old synthesised sound.py.
voices.py then mixes the voices on top (out/year1500_mix.wav).                 python3 sound_el.py"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sfx_el")
TOTAL = 76.0
# clip, start (s), volume, extra filter (applied on the clip's own time, before it is placed)
CUES = [
    ("wind", 0.0, 1.0, "aloop=loop=2:size=1440000,atrim=0:76,volume='if(between(t,6.8,19.5),0.04,0.35)':eval=frame,"),
    ("glass", 1.5, 0.35, ""),
    ("crowd", 7.0, 0.6, "afade=t=in:d=0.4,afade=t=out:st=7.6:d=0.6,"),
    ("blast", 14.6, 1.0, ""),
    ("ringing", 18.0, 0.45, "afade=t=out:st=3.5:d=1.5,"),
    ("getup", 22.3, 0.55, ""),
    ("glass", 24.8, 0.3, ""),
    ("birds", 28.2, 0.5, ""),
    ("static", 31.0, 1.0, "volume='if(between(t,4,12),0.12,0.5)':eval=frame,afade=t=out:st=13:d=1,"),
    ("steps", 31.0, 0.4, "atrim=0:3.6,afade=t=out:st=3.0:d=0.6,"),
    ("heart", 43.5, 0.5, "afade=t=out:st=5:d=1,"),
    ("steps", 54.2, 0.45, "afade=t=in:d=0.5,afade=t=out:st=16.5:d=1.5,"),
    ("pad", 57.5, 0.4, "afade=t=in:d=3,afade=t=out:st=15:d=3,"),
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
    out = os.path.join(HERE, "out", "year1500_sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", graph, "-ar", "48000", out], check=True)
    print(out)


if __name__ == "__main__":
    main()
