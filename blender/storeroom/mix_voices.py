"""Put the ElevenLabs voices (voices/NN_who.mp3, one file per line) on «انباری».
The soldier is turning: his voice is pitched down, roughened, with a low growl layer under it and
muffled by the storeroom door. Mum (the voice behind the hall doors) is muffled too and plays twice,
the very same file. The boys are pitched up a little to sound like teenagers.
    python3 mix_voices.py   -> out/storeroom_voices.wav  (+ out/storeroom_voices.mp4 when the captions film exists)
"""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "voices")
OUT = os.path.join(HERE, "out")

DOOR = "lowpass=f=3600,aecho=0.7:0.5:14:0.2"
TEEN = "rubberband=pitch=1.1:formant=shifted"
MOM = "lowpass=f=2500,aecho=0.6:0.4:18:0.25,volume=0.85"
# (file, start in the film, filter, zombie growl layer?)
CUTS = [
    ("01_me", 0.8, TEEN, False),
    ("02_soldier", 18.2, DOOR, True),
    ("03_mahsa", 27.6, "", False),
    ("04_soldier", 30.0, DOOR, True),
    ("05_mom", 44.6, MOM, False),
    ("06_kian", 50.6, "rubberband=pitch=1.25:formant=shifted", False),
    ("07_soldier", 54.0, DOOR, True),
    ("08_arian", 59.6, TEEN, False),
    ("09_kazemi", 64.2, "", False),
    ("05_mom", 70.0, MOM, False),
    ("11_card", 76.7, TEEN, False),
]
TOTAL = 82.1


def run(cmd):
    subprocess.run(cmd, check=True)


def zombie(src, dst, flt):
    """voice a bit lower and rough + the same words an octave down, trembling, as a growl underneath."""
    fc = ("[0:a]asplit=2[a][b];"
          "[a]rubberband=pitch=0.9:formant=preserved,volume=2.2,asoftclip=type=tanh,volume=0.75[main];"
          "[b]rubberband=pitch=0.5:formant=shifted,tremolo=f=32:d=0.8,lowpass=f=900,volume=0.55[growl];"
          f"[main][growl]amix=inputs=2:normalize=0,{flt}[o]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[o]",
         "-ar", "48000", "-ac", "2", dst])


def main():
    os.makedirs(os.path.join(V, "fitted"), exist_ok=True)
    parts = []
    for i, (name, t, flt, z) in enumerate(CUTS):
        src = os.path.join(V, name + ".mp3")
        dst = os.path.join(V, "fitted", f"{i:02d}_{name}.wav")
        if z:
            zombie(src, dst, flt)
        else:
            af = "afade=t=in:d=0.02" + ("," + flt if flt else "")
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, "-ar", "48000", "-ac", "2", dst])
        parts.append((dst, t))
    ins, chains = [], []
    for i, (p, t) in enumerate(parts):
        ins += ["-i", p]
        ms = int(t * 1000)
        chains.append(f"[{i + 1}:a]adelay={ms}|{ms}[v{i}]")
    n = len(parts)
    mix = ";".join(chains) + ";" + "".join(f"[v{i}]" for i in range(n)) + \
        f"amix=inputs={n}:normalize=0[voc];[0:a]volume=0.55,apad[fx];" \
        f"[voc][fx]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL},alimiter=limit=0.95[a]"
    wav = os.path.join(OUT, "storeroom_voices.wav")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(OUT, "storeroom_sfx.wav")] + ins +
        ["-filter_complex", mix, "-map", "[a]", "-ar", "48000", wav])
    print(wav)
    film = os.path.join(OUT, "storeroom_captions.mp4")
    if os.path.exists(film):
        mp4 = os.path.join(OUT, "storeroom_voices.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", film, "-i", wav, "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", mp4])
        print(mp4)


if __name__ == "__main__":
    main()
