"""The recorded lines run longer than the caption slots they were animated for: keep the mouths talking until the
voice ends (frames not rendered yet only). Rezaei 46.6-48.1, Kian 71.6-73.1."""
import bpy, os, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "wall_toon.blend")
bpy.ops.wm.open_mainfile(filepath=F)
FPS = 24
rnd = random.Random(3)
for who, a, b in (("Rezaei", 46.5, 48.1), ("Kian", 71.5, 73.1)):
    sk = bpy.data.objects[f"{who} mouth"].data.shape_keys
    kb = sk.key_blocks["open"]
    for f in range(int(a * FPS) + 1, int(b * FPS) + 2):
        t = (f - 1) / FPS
        fade = min(1.0, (b - t) / 0.15)
        kb.value = max(0.0, (0.18 + 0.32 * abs(math.sin(t * 10.5 + rnd.random() * 0.6))) * fade)
        sk.keyframe_insert(f'key_blocks["open"].value', frame=f)
    print("LIPS", who)
bpy.ops.wm.save_as_mainfile(filepath=F)
