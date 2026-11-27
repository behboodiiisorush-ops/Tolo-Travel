# «نیلا» — stylised character study (Blender only)

Reference: Kenny Praise, *How to Create Stylized 3D Characters (Full Masterclass)* — a 20-hour
sculpt → retopo → UV → hair → shading → rig → pose → light workflow. Here the same kind of character
(big round face, huge brown eyes, freckles and rosy cheeks, full lips, messy top-knot, brown tee,
three layered cord necklaces with a small heart) is built **from code** in Blender:

| masterclass step | here |
|---|---|
| block-out + face/body sculpt | MPFB (MakeHuman) base + strong shape targets (`STYLE` in `scene.py`; eyes ×2.4, round head, small nose and chin, full lips, chubby cheeks) |
| hair | `culturalibre_hair_13` hair asset, fringe parted off the eyes by moving its vertices |
| clothes & accessories | MakeHuman tee / trousers / sneakers; necklaces are NURBS curves laid on the body by ray-casting, heart pendant from spheres + cone |
| shading & texturing | warm SSS skin, painted vertex mask → rosy cheeks + Voronoi freckles, glossy eyes with a ramp iris |
| rigging & posing | MPFB `game_engine` rig, **Mixamo motion capture** retargeted (`shelter3/mocap2.py`), cross-faded at full 24 fps |
| lighting & presenting | dark curved studio backdrop, warm key, cool fill, two rim lights, slow camera push-in, shallow focus on the eyes, Cycles + denoise |

Natural motion = real motion capture (breathing idle → thinking → nod "yes" → "listen…" gesture) plus life on
top: blinks (also when the eyes jump to a new place), the head follows a look target that moves in quick darts
with holds, brows lift while thinking, a smile that grows after the nod, and light lip movement during the gesture.

```bash
../cast/bpy.sh scene.py --still 1,130 --cycles --pct 50     # look checks -> out/
../cast/bpy.sh scene.py --still 1 --face --pct 50           # face close-up
PCT=67 SAMPLES=16 ./chain.sh 1 264                          # full clip -> frames/ (≈45 s/frame on 4 CPUs)
ffmpeg -framerate 24 -i frames/f_%04d.png -c:v libx264 -crf 17 -pix_fmt yuv420p nila.mp4
```
