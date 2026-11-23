"""Cut the Persian lines out of one ElevenLabs export (times found with Whisper) into per-line clips."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from captions import CAPTIONS
SRC = sys.argv[1]  # the ElevenLabs export with all lines
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voices', 'clips')
SEG = {
 'Me': [(14.42,18.44),(18.44,20.58),(20.58,22.63),(22.63,24.67),(24.67,26.32),(26.32,28.89),(28.89,31.92),(31.92,33.43),(33.43,36.18)],
 'Mom': [(49.43,51.78),(51.78,53.34),(53.34,55.65),(55.65,56.91),(56.91,58.33),(58.33,60.20),(60.20,62.79)],
 'Lena': [(77.90,80.16),(80.16,83.06),(83.06,85.22),(85.22,86.62),(86.62,87.99),(87.99,90.49)],
 'Grandma': [(101.89,104.04),(104.04,107.43)],
 'Rahim': [(120.40,122.56),(122.56,124.67),(124.67,127.71),(127.71,130.22),(130.22,132.74),(132.74,135.07),(135.07,137.27)],
 'Jalal': [(148.03,150.37),(150.37,153.07),(153.07,155.50),(155.50,158.20)],
 'Sara': [(169.27,171.07),(171.07,173.00)],
 'Phone': [(180.64,184.16)],
 'Radio': [(191.89,194.19)],
}
os.makedirs(OUT, exist_ok=True)
used = {k: 0 for k in SEG}
rows = []
for a, b, who, text in CAPTIONS:
    k = {None: 'Me', 'Grandma voice': 'Grandma'}.get(who, who)
    s, e = SEG[k][used[k]]; used[k] += 1
    name = f"{a:05.1f}_{(who or 'Me').replace(' ', '_')}.wav"
    d = e - s
    subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',f'{s}','-t',f'{d}','-i',SRC,
        '-af',f'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse',
        '-ar','48000','-ac','1',os.path.join(OUT,name)], check=True)
    rows.append((a, b, who, name))
assert all(used[k] == len(v) for k, v in SEG.items()), used
with open(os.path.join(OUT, '..', 'clips.txt'), 'w') as f:
    for a, b, who, name in rows:
        f.write(f"{a}\t{b}\t{who}\t{name}\n")
# one file with only the Persian speech, in story order
lst = os.path.join(OUT, '..', 'concat.txt')
gap = os.path.join(OUT, '..', 'gap.wav')
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','0.5',gap],check=True)
with open(lst,'w') as f:
    for _,_,_,name in rows:
        f.write(f"file '{os.path.join(OUT,name)}'\nfile '{gap}'\n")
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',lst,'-c:a','libmp3lame','-b:a','192k',
                os.path.join(OUT,'..','persian_only.mp3')],check=True)
os.remove(lst); os.remove(gap)
print(len(rows), 'clips')
