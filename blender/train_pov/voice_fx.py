"""
Make one recorded/AI female voice sound like four different people.

    python3 voice_fx.py lena  in.mp3  out.wav
    python3 voice_fx.py sara  in.mp3  out.wav
    python3 voice_fx.py grandma in.mp3 out.wav
    python3 voice_fx.py grandma_phone in.mp3 out.wav   # grandma's voice message
    python3 voice_fx.py mom   in.mp3  out.wav
    python3 voice_fx.py phone in.mp3 out.wav           # operator
    python3 voice_fx.py radio in.mp3 out.wav           # walkie-talkie

Needs ffmpeg with the rubberband filter.
"""

import subprocess
import sys

PRESETS = {
    # child: +5 semitones with the formants moved up too (smaller "throat"), thinner low end
    "lena": "rubberband=pitch=1.34:formant=shifted:pitchq=quality,"
            "highpass=f=220,equalizer=f=3500:t=q:w=1.2:g=3",
    # nurse: a little higher, brighter, slightly faster and crisper
    "sara": "rubberband=pitch=1.07:tempo=1.06:formant=preserved:pitchq=quality,"
            "highpass=f=130,equalizer=f=3000:t=q:w=1:g=4,equalizer=f=250:t=q:w=1:g=-3",
    # grandma: lower, slower, shaky (vibrato + tremolo), duller top, a touch of breath
    "grandma": "rubberband=pitch=0.88:tempo=0.92:formant=preserved:pitchq=quality,"
               "vibrato=f=5.5:d=0.22,tremolo=f=5.5:d=0.15,lowpass=f=6000,"
               "equalizer=f=1200:t=q:w=1:g=2,equalizer=f=150:t=q:w=1:g=-4",
    # mother: slightly lower and warmer than the original so she differs from Sara
    "mom": "rubberband=pitch=0.95:formant=preserved:pitchq=quality,equalizer=f=220:t=q:w=1:g=2",
    # filters for voices coming through devices
    "grandma_phone": "rubberband=pitch=0.88:tempo=0.92:formant=preserved:pitchq=quality,"
                     "vibrato=f=5.5:d=0.22,highpass=f=350,lowpass=f=3300,"
                     "acrusher=bits=10:mix=0.25,volume=1.3",
    "phone": "highpass=f=350,lowpass=f=3400,acrusher=bits=12:mix=0.15",
    "radio": "highpass=f=500,lowpass=f=2800,acrusher=bits=8:mix=0.35,volume=1.6",
}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in PRESETS:
        print(__doc__)
        print("presets:", ", ".join(PRESETS))
        sys.exit(1)
    preset, src, dst = sys.argv[1:]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", PRESETS[preset] + ",loudnorm=I=-16",
                    "-ar", "48000", dst], check=True)
    print(dst)


if __name__ == "__main__":
    main()
