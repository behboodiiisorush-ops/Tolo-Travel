# Notes: Kenny Praise masterclass, files 07 (UV unwrapping) and 08 (hair grooming)

**How much was read:** both files were read in full, from the first character to the last.
- `07_uv.txt`: 76,946 characters, read 100% in chunks [0:25000], [25000:52000], [52000:end]. Covers [10:44:02] to [12:05:12] (the masterclass calls this "Chapter 9").
- `08_hair.txt`: 133,725 characters, read 100% in chunks [0:27000], [27000:54000], [54000:81000], [81000:108000], [108000:end]. Covers [12:05:29] to [14:24:47] (the masterclass calls this "Chapter 10"). The last lines are the opening of Chapter 11 (shading/texturing), which only gives its agenda.

**Not covered in these two chapters (stated so nobody invents it):** Principled Hair BSDF and any hair material values, EEVEE vs Cycles hair render settings, hair physics or how hair behaves when the character moves, and UDIMs (mentioned and skipped). The only render setting used is the curves **Strand vs Strip** shape in Render Properties (see 2.2). Texel density is handled by eye with a UV checker grid and "Average Island Scale"; no numeric texel density is given.

---

## 1. Workflow steps in order, with timestamps

### 1.1 Chapter 9 — UV unwrapping (07_uv.txt)
- [10:44–10:49] Theory. UV means the 2D texture space (U = horizontal, V = vertical). Unwrapping flattens the 3D surface into 2D so textures can be painted on it. The comparison is a sewing pattern: seams are where the cloth is cut and joined.
  - Put seams "in areas that are less visible", in places "hidden from the camera", and on "naturally separated areas". On clothes, put them where the real garment seams are.
- [10:49:41] Checklist, applied to every object: **1. cut seams → 2. fix stretching (if any) → 3. arrange the UVs.** Name your objects first.
- [10:50:30] Switch to the UV Editing workspace (it enters Edit Mode). Set the viewport focal length to 150 mm in the N panel.
- [10:51:37] Turn on **Live Unwrap** in two places: the 3D viewport header option and UV menu > Live Unwrap. Turn on **UV Sync Selection** so the UVs show without everything selected.
- **Seam placement on the body** [10:51–11:04]:
  - Legs, arms and neck are treated as cylinders. Cut a ring at each end plus one seam along the length.
    - The leg seam runs down the inside.
    - Arm seams go "on the underside of the arm cuz you're not going to see that one as much", and the wrist ring goes on the inside.
    - The neck ring sits where the shirt will cover it. The upper ring is moved to where it is not visible from the front.
  - Mark seams with Ctrl+E > Mark Seam (or the Edge menu). Mirror the edge selection with Ctrl+Shift+M and tick "Extend".
    - If mirroring fails on a symmetric mesh, use Mesh > Snap to Symmetry. On an asymmetric character, select both sides by hand.
  - Feet: one loop around the foot separates top from sole. Press L to select an island, and set "delimit by seam".
  - Hands: one loop separates top from palm (hide the other faces to keep the loop from running across the body). Optionally cut a ring at each finger base so every finger is its own UV island.
  - Torso: separates into a front island and a back island.
  - Head:
    - Separate the ears, then separate the front of each ear from its back.
    - Cut a seam down the back of the head, "covered by the hair".
    - Separate the eye cavity and the mouth bag into their own islands. The mouth-bag seam is moved inside so it is "not too visible from the front", and the mouth bag also gets a cut down its middle.
- **Fix stretching** [11:04:28–11:23]:
  - Turn on the UV Editor overlay **Display Stretch**, set the display to black, and untick faces. Blue is fine; yellow or red means stretching.
  - Make a test material "UV checker" with an Image Texture set to a new image, Generated type **Color Grid**, size **4096×4096** ("1024*4" typed into the field). Show it in Solid mode with Viewport Shading > Color = Texture.
  - Re-unwrap the problem islands with **U > Minimum Stretch**.
    - Angle Based is Blender's default.
    - Conformal is "more for simpler objects", not characters.
  - After each re-unwrap: select all, then UV > **Average Islands Scale**.
  - **Pins**: P pins a vertex, Alt+P unpins.
    - With Live Unwrap on, moving pinned vertices re-solves the rest of the island. This is "why we turned on live UV unwrapping".
    - Pinned parts also stay put when you unwrap again.
  - Face island:
    - Move it to the UV centre by setting the N panel UV Vertex X/Y to 0.5, and put the 2D cursor at 0.5.
    - Rotate it 180°, then S X 0 with the 2D cursor as pivot.
    - Pin the borders, eyes and ears, then straighten the lips and nose with G Y on pinned vertices or with the **Grab** UV brush (F changes its size).
  - **Eyes**: select the eyelid edges and scale them down in Y (S Y) so the texture "looks compressed" while open and is "not going to be stretched once the eyes are closed".
  - UVs are not mirrored, to keep the class simple.
- **Arrange / pack** [11:11:45, 11:23–11:38]:
  - Pack Islands once to bring everything into 0–1, then arrange by hand.
  - Give the face a larger scale. Scaling an island up means "more resolution than other parts". The ears are scaled up to match the face.
  - Scale down what is seen less: legs, feet ("inside the shoes"), soles, inside parts.
  - Keep right-side parts on the right of the layout and left on left. Rotate islands so the checker letters "stand up straight" (Ctrl snaps rotation).
  - No overlaps "except you know what you're doing".
  - Use Pivot = Individual Origins to scale several islands at once. Move islands in Face select mode so connected vertices do not come along.
- [11:38:18] In Blender 5.0+ the UVs show even in Object Mode.
- **Shirt** [11:38:34]:
  - Mark seams where the shirt already had seams, plus side seams and an underarm/sleeve seam.
  - The leftover inner "solidify-like" geometry was left alone.
  - Live Unwrap reuses the last method used (Minimum Stretch), so there was little stretching.
- **Skirt** [11:42:28]:
  - Hide the inner faces, mark the panel seams, mirror them, then Select All > U > Minimum Stretch.
  - Add a seam where the texture skews, and one more seam on the inside.
  - Pack Islands gave a result he didn't like, so he arranged it by hand. The inside of the skirt was scaled down a little.
- **Shoes** [11:49:07]:
  - Several shoe parts are edited together so they share one UV map.
  - Boot: seam at the back and on the inside.
  - Straps are unwrapped "like an elongated cube": a ring at each end plus a long edge. Shift+R repeats the last action.
  - A seam was moved under a strap so it is covered.
  - The sole needed several seams.
  - Straighten skewed strips: pin one end and scale to 0 on one axis (S Y 0 or S X 0). To reset after a change: Alt+P to clear pins, then re-mark any seam to re-unwrap.
  - Empty UV space is "completely fine" because "we are using this character for animation".
- [12:02:16] The eyes and teeth from the Blender asset meshes already have UVs. The teeth sat in UDIM tiles and were scaled into the 0–1 tile. High-poly sculpt objects are not unwrapped.

### 1.2 Chapter 10 — Hair grooming (08_hair.txt)
- [12:06–12:12] **Read the reference first.** Collect references from all angles. Then answer two questions:
  1. "Can we separate the hairstyle into parts or into volumes?" For example: the sides, the back, a ponytail, a bun's base and its top as separate curve objects.
  2. "What is the flow and the direction of the hair?" Note any noise and curliness.
  - A very curly or noisy style can stay as one volume.
- [12:12:51] **Concept.** An average human has about 100,000 strands. You groom a few **guide (parent) curves**, and modifiers add **children** that follow them, "similar to the subdivision surface modifier". You need enough guides: too many are hard to comb, too few give little control.
- [12:15:03] **Prerequisites.** A separate **scalp object** that the hair emits from, rather than the character mesh, and **the scalp must have UVs**.
  - Add > Curve > **Empty Hair** with the scalp selected. The new curves are parented to the scalp, and Blender adds a **Surface Deform** modifier automatically ("we don't want to play around with this one").
  - Edit the curves in Edit Mode or, mostly, in **Sculpt Mode**.
- [12:16–12:23] **Sculpt brushes** (details in 2.2).
- [12:23:12] **Hair node assets.** Asset Browser > Essentials > Hair. Each asset can be dropped on as a modifier or used as a node inside your own Geometry Nodes tree, which gives "much more control".
- [12:26:53] **His 4-step workflow** ("works for almost all hair types"):
  1. Create the guide hair.
  2. Interpolate the guides (children).
  3. Add clumps (primary and secondary).
  4. Add noise and frizz "to break up the perfection".
- [12:28:11] Setup:
  - Layout workspace, focal length 150, MatCap lighting, Outline off.
  - **Disable in Viewports** (the monitor icon) on the high-poly collection rather than hiding it: when it is disabled "Blender is not going to think about it anymore".
- Order of examples: eyebrows → eyelashes (using modifiers) → short hair (using Geometry Nodes) → long hair (main + left side + ponytail, using Geometry Nodes).

**Eyebrows** [12:29:32–12:58:05]
1. Make the scalp.
   - In Edit Mode on the body, select the faces under the brow, duplicate them, and separate them with P. Name the object "brow scalp".
   - Remove its Subdivision modifier. Add a **Shrinkwrap** (target = body) and a **Mirror** modifier. Delete the extra faces.
   - Apply with Ctrl+A > **Visual Geometry to Mesh**. Put it in a new "hair scalp" collection.
2. UV the scalp.
   - U > Angle Based; the orientation doesn't matter. **First Alt+P to remove pins inherited from the body UVs.**
3. Add the Empty Hair curve ("eyebrows").
4. Mark where the brow goes with the Annotate tool, placement = Surface.
5. Sculpt Mode, X symmetry on.
   - Add brush, length "01" then "0.7" (spoken values, see 2.2).
   - Comb in **Projected** mode. Add strands one at a time following the reference from the front and the top.
   - Selection brush in Curve mode. Alt+A deselects, A selects all. Z (or the overlay toggle) is used to check.
   - Slide brush evens the spacing. Shrink the tips with Grow/Shrink (Ctrl), with Scaling > Minimum Length = 0.
   - Keep strands from intersecting the head. Edit Mode + L is also used.
   - Late refinements in **Sphere** mode, so earlier combing isn't disturbed.
6. Drop **Interpolate Hair Curves** as a modifier.
   - Surface = brow scalp. Density 50,000 → 100,000 → about 800,000.
   - Children scatter over the whole scalp, so restrict them with a **Mask Texture** (see 2.4).
7. Render Properties > Curves > Shape: **Strip**, not Strand, so the thickness can taper. Add **Set Hair Curve Profile** at 0.1 mm ("the average human hair is about 0.1 mm"), shape about 6 ("Somewhere around 6").
   - For viewing: Object Properties > Viewport Display > Color black, and Viewport Shading color = Object.
   - Re-comb with the children visible.
   - Raise the interpolation amount, then "take this down to three". The control is not named.
8. **Clump Hair Curves** (primary): untick **Use Existing Guide Map** so Guide Distance takes effect. Guide distance 0.04 ("04"), factor toned down. A second Clump (secondary) uses guide distance 0.02 ("02"), giving "clumps inside of the primary clumps".
9. **Frizz Hair Curves**: untick **Cumulative Offset** ("everything goes crazy" otherwise), reduce Distance and reduce Factor.

**Eyelashes** [12:58:21–13:16:31]
1. Scalp: a duplicated face ring around the eye, separated and named "lashes scalp".
   - Shrinkwrap to the body. Snap and slide the vertices (GG) to fit the lid.
   - Delete the front/inner part where the reference has no lashes.
   - Mirror, then Visual Geometry to Mesh. UV unwrap it, after deleting duplicate geometry and rebuilding the faces.
2. Empty Hair "eyelashes". Add brush with length 0.01. Set the curves shape to Strand while grooming because the Strip radius was too big.
   - Place evenly spaced guides around the lid. Comb out and up. Shorten the corners with Grow/Shrink.
3. Mirror without X symmetry:
   - Edit Mode, select all, Shift+D.
   - Shift+S > Cursor to World Origin, pivot = 3D Cursor.
   - Ctrl+M X mirrors. Then turn X symmetry on.
4. Lower lashes: fewer guides. Delete the extras and Slide to space them. Shift+drag smooths, as in sculpt.
5. Interpolate Hair Curves: surface = lashes scalp, high density. Re-shape with Grow/Shrink and Comb.
   - Paste the viewport color (Ctrl+C/Ctrl+V on the field).
   - Shape back to Strip. Set Hair Curve Profile at 0.1 mm, then "2 mm" (spoken value, made thicker).
   - The position of Set Hair Curve Profile in the stack "doesn't really matter". He moves it above Interpolate.
6. Clump: untick Existing Guide Map, low guide distance, very low **Tip Spread** to break it up.
7. **Hair Curves Noise**: untick Cumulative Offset, raise Scale and Scale Along Curve to 15, reduce Factor.
8. Too many lower lashes, so split them off:
   - Edit Mode, select them, Ctrl+L, P to a separate object.
   - Split the scalp with V along an edge (rip) into an upper and a lower part.
   - On the lower object's Clump, use the existing guide map.
   - Interpolate amount reduced ("one is maybe too sparse"), final **25**.
   - Pinch or comb pairs of lashes together.

**Short hair** [13:16:31–13:41:54]
1. Scalp:
   - Annotate the hairline. Duplicate the body faces under it (half of them), separate, Mirror, remove Subdivision, extrude to the hairline with snapping.
   - Shrinkwrap (above the Mirror) to the body.
   - In Sculpt Mode with the wireframe on: Grab brush plus **Relax Slide** brush to follow the annotation.
   - Extrude, fill faces, merge vertices. Alt+W, **Fill Holes / Face Sets from Visible** (spoken as "see faces from visible") removes the stray face sets.
   - Visual Geometry to Mesh. UV: Alt+P to clear pins, Ctrl+E > Clear Seam, U unwrap.
   - "We don't need to be too accurate", because a texture mask can still limit where hair grows.
2. One volume. Empty Hair "short hair". Shape = Strand while grooming.
   - **Density brush**, length 0.04 (tried 0.01, 0.07, 0.05).
   - Minimum distance 0.02, then **0.013**. Add and remove until spacing is even.
3. Comb the directions from the reference (the top goes forward and up, the sides and back go down).
   - Make "a clear separation" between top and sides.
   - **Keep hair off the ear.**
   - Switch between Projected and Sphere ("not just one size fits all").
   - Shorten the sides with Grow/Shrink.
4. Geometry Nodes, a new tree named "short hair":
   - Set Hair Curve Profile at 0.1 mm, shape = Strip.
   - Interpolate Hair Curves: Surface = hair scalp, Surface UV Map = **Named Attribute** with the UV map's name copied from Object Data > UV Maps. High density.
   - Re-comb.
5. Primary Clump: untick Existing Guide Map, guide distance 0.01 → **0.015**, factor reduced.
6. Secondary clumps through a **guide index map** (node chain in 3.3).
   - When it lags, set Interpolate **Viewport Amount 0.5** and raise it back to 1 later.
7. Noise on only part of the strands: Separate Geometry (Spline) with a random selection of about 25%.
   - Hair Curves Noise: untick "relative/cumulative offset", raise Scale and Scale Along Curve, Scale about 10. Distance, Shape and Offset Per Curve were also adjusted.
   - Join Geometry with the inverted output.

**Long hair** (main + left side + ponytail) [13:41:54–14:23:22]
1. Plan: left and right volumes, a parting line, a short ponytail, all meeting at a hair band.
   - Annotate the parting and the outline. Use the existing hair scalp.
   - Empty Hair "main". Add brush with points **30**. Shape = Strip.
2. Guides around the **perimeter of the hairline**, combed to the back to meet at the band.
   - Shift smooths. Pressure sensitivity off.
   - "Leave some space between the head and the hair strand", so the interpolated hair keeps volume.
   - Reduce the comb size near the middle so the X-symmetry sides don't fight.
   - Add brush settings: **Interpolate Length** and **Interpolate Shape** under Curve Shape. New guides then copy their neighbours instead of standing straight up, which makes grooming "a lot faster".
3. GN tree "main hair":
   - Set Hair Curve Profile at 0.1 mm. Interpolate (hair scalp, Named Attribute UV).
   - Children come out over the whole scalp although guides are only at the edges, so paint a **mask texture** "main hair density" (2K, saved to textures/) and assign it to the Interpolate mask.
4. Clump Hair Curves with its **Guide Index fed from Interpolate Hair Curves' guide index output** ("just the main heads that we added in"). Shape "about8" (spoken value).
5. **Blend Hair Curves** with blend radius 0.01 fills the gaps.
6. **Parting**:
   - Interpolate has **Part by Mesh Islands**. Split the scalp mesh with V (rip) along the parting and around the region, so the left, right and rest are separate islands. Blender then respects the parting.
   - Blend Hair Curves erased the parting again. Fix it with a vertex group "pattern": select the parting faces, invert with Ctrl+I, assign. A **Named Attribute "pattern"** goes into Blend Hair Curves' **Factor**.
   - Raise the density only at the end, to keep the viewport fast.
7. Noise subset: Separate Geometry (Spline, random about 0.1).
   - Hair Curves Noise: Scale and Scale Along Curve up, Distance about 0.02, Cumulative Offset kept ON here ("actually looks good"), Shape 0.2 ("02"), Factor reduced.
   - Join Geometry with the inverted output.
8. Short frizzy strays: a duplicate of the random Separate with a different seed, then **Trim Hair Curves**.
   - Untick Replace Length. Length Factor 0.1 means 10%.
   - Randomise the length factor with a Random Value (min 0, max "2"), with ID from a Curve Info node.
   - Then Hair Curves Noise: Scale up, Distance 0.02, Trim 0.1 → 0.3 with Preserve Length on, Shape 0, then 0.1. Selection amount 0.05 → 0.1.
   - Join back. This gives "randomness to the whole hair... rather than making everything look perfect".
9. **Left side** as its own Empty Hair curve with its own GN tree "left side hair". Name the curve and the tree the same.
   - Add Set Hair Curve Profile at once, so you don't keep toggling Render Properties.
   - Groom, then Interpolate with a mask texture "left side hair" painted only on that side (X symmetry off).
   - Clump with the Interpolate guide index.
   - Secondary clumps: **Delete Geometry** (not Separate) + Random Value → **Create Guide Index Map** → a second Clump. Then the noise subset and Join.
   - The right side uses the same node setup with its own painted texture.
10. **Ponytail** [14:15:23]:
    - Scalp = a Plane named "ponytail scalp", rotated and scaled at the band, subdivided twice, then **LoopTools > Circle**.
    - Empty Hair "pony tail", its own GN tree, Set Hair Curve Profile, guides combed outward in the planned directions.
    - The plane already has a default UV map, so Blender didn't prompt for one, but he unwrapped a new one anyway.
    - **Error fix**: select the curve, then the scalp, Ctrl+P > **Object (Attach Curves to Surface)**.
    - Interpolate (Named Attribute UV) → Clump (guide index) → noise subset (Separate random → Hair Curves Noise, Shape 0.1, Distance up, Factor tuned) → Join. Reduce the noise distance and scale at the end.
- [14:23:39] Summary: the same four steps work for any style; "once you know the principles, you can always break the principles".

---

## 2. Concrete techniques (reference list)

### 2.1 UV
- **Seams**: hidden or low-visibility places (inner leg, underside of arm, inner wrist), places covered by other geometry (neck under the collar, back of the head under the hair, seam under a shoe strap), and natural or garment seams on clothes. Cylinder rule: a ring at each end plus one lengthwise cut.
  - Separate islands for each finger, ear front and back, eye cavity, mouth bag, top and bottom of the hand and foot, front and back of the torso.
- **Unwrap method**: Minimum Stretch for characters. Angle Based is the default. Conformal is for simple objects only. Live Unwrap reuses the last method.
- **Stretch check**: Display Stretch overlay (blue good, red bad) plus a 4096² Color Grid checker material.
- **Texel density**: UV > Average Islands Scale after every re-unwrap, then deliberate scaling. Face and ears bigger; legs, feet inside shoes, soles and inner cloth smaller. No numeric value.
- **Pins + Live Unwrap**: hand-straighten islands; the Grab UV brush; scale-to-zero on one axis to straighten strips.
- **Animation-aware UVs**: pre-compress the eyelid UVs in Y so they don't stretch when the eyes close.
- **Packing**: Pack Islands as a first pass, then arrange by hand (left/right logic, upright orientation, no overlaps). Empty space is fine for an animation character. Several objects (shoe parts) can share one UV map. One 0–1 tile, no UDIMs.
- **Mirror**: Ctrl+Shift+M (Extend) for symmetric seam selection; Snap to Symmetry if it fails.

### 2.2 Hair curves system and sculpt brushes
- **Object and settings**:
  - Add > Curve > **Empty Hair** creates a Curves object parented to the scalp, with an automatic **Surface Deform** modifier.
  - The scalp needs UVs. Children use the UV map through the Interpolate node's Surface UV Map input.
  - Error fix: Ctrl+P > Object (Attach Curves to Surface).
- **Add brush** (Tool settings > Curve Shape):
  - **Length**: 0.15 in the demo, 0.04 for short hair, 0.01 for lashes. For brows the spoken values were "01" then "0.7".
  - **Points** per curve: 8 by default, 20 and 30 used. More points give more control when combing.
  - **Count**: he leaves it at 1.
  - **Interpolate Length / Interpolate Shape**: new guides copy their neighbours.
- **Density brush**: Distance Min sets the spacing; 0.1/0.01 in the demo, 0.02 → 0.013 for short hair. The same Curve Shape options apply.
- **Other brushes**:
  - **Delete**.
  - **Selection**: Points or Curve mode. He sets a W shortcut; Alt+A deselects.
  - **Comb**.
  - **Grow/Shrink**: Ctrl shrinks. Set Scaling > Minimum Length = 0 to shrink fully.
  - **Pinch**: for clumps.
  - **Puff**: stands hair up.
  - **Pull Teeth**: the transcript's name for the tool that pulls the tips in a direction.
  - **Slide**: moves roots.
  - **Smooth**: Shift held smooths as well.
- **Falloff shape**: **Projected** (through the whole volume) for blocking out; **Sphere** (only front strands, like a real comb) for refining.
- Add the brushes to Quick Favorites (Q + underlined letter); X symmetry; Z or the overlay toggle to inspect.
- Mirroring guides without symmetry: Shift+D, cursor to world origin, pivot = 3D Cursor, Ctrl+M X.

### 2.3 Hair node assets used (Essentials > Hair)
- **Interpolate Hair Curves**:
  - Surface (the scalp object).
  - Surface UV Map (Named Attribute string = the UV map name).
  - Density: 50k–800k used; set high.
  - Mask Texture (the painted density image).
  - **Part by Mesh Islands**.
  - **Viewport Amount**: 0.5 while combing.
  - "Interpolation amount" (in the eyebrow section the value went down to 3).
  - Outputs a **Guide Index** for Clump.
- **Set Hair Curve Profile**: radius 0.1 mm for real hair; lashes "2 mm" (spoken value). A **Shape** value of about 6 for brows tapers root to tip. Needs Render > Curves Shape = **Strip**.
- **Clump Hair Curves**:
  - Untick **Use Existing Guide Map** to use Guide Distance: brows 0.04/0.02, short hair 0.015.
  - Or feed a Guide Index (from Interpolate, or from Create Guide Index Map).
  - Factor, Shape ("about8"), Tip Spread (very low on lashes).
- **Create Guide Index Map**: input Geometry (the clumped hair) plus Guides (a random subset kept by Delete Geometry, Spline domain, random probability 0.95 deleted). Its Guide Index feeds a second Clump, which gives the secondary clumps.
- **Frizz Hair Curves**: untick Cumulative Offset, reduce Distance and Factor (brows).
- **Hair Curves Noise**:
  - Cumulative Offset off in most uses, on in "main hair".
  - Scale and Scale Along Curve raised (15 on lashes, 10 on short hair).
  - Distance about 0.02, Shape 0–0.2, Factor reduced, Offset Per Curve.
  - Trim with Preserve Length.
- **Blend Hair Curves**: Blend Radius 0.01, Factor = vertex-group Named Attribute (masks the parting).
- **Trim Hair Curves**: untick Replace Length, Length Factor 0.1 driven by Random Value (0 to "2") with ID from Curve Info.
- Core nodes: Named Attribute, Random Value (Boolean probability), Separate Geometry (**Spline** domain; outputs Selection and Inverted), Delete Geometry (Spline), Join Geometry, Curve Info, Group Output. Press M to mute a node and compare.

### 2.4 Density mask textures
- Texture Paint workspace, Mode = **Single Image**, a new image at 2K (brow density, main hair density, left side hair), black fill.
- Paint white where hair should grow; X swaps the colours. Paint Soft brush, pressure off.
- **Save the image (Alt+S) every time** into a `textures/` folder: "Blender will not automatically save the image for you... you can lose the image".
- Select it in Interpolate Hair Curves > Mask Texture.

### 2.5 How hair attaches to the head
- Through a scalp mesh made from the body's own faces (duplicated, Shrinkwrapped to the body, applied), or through a plane for a ponytail.
- The curves are parented to the scalp with a Surface Deform modifier added automatically.
- The transcript does not say how the scalp follows the rig or animation.

### 2.6 Common mistakes called out
- Pins inherited from the body UVs break the scalp unwrap; Alt+P first.
- Children scatter over the whole scalp, so use a mask texture.
- Guide Distance does nothing while Use Existing Guide Map is ticked.
- With Cumulative Offset on, Frizz goes "crazy".
- Blend Hair Curves fills in the parting, so use a vertex-group factor.
- No parting without separate mesh islands plus Part by Mesh Islands.
- Hair through the head: check from the top and side.
- Hair on the ear.
- Comb conflicts at the symmetry line.
- Lag: Viewport Amount 0.5 and add density last.
- Unsaved painted images.
- Strip radius too big while grooming lashes: groom in Strand.
- Too many lower-lash children: separate object, interpolate 25.

---

## 3. Applicable to a scripted bpy pipeline

**Can be scripted (Blender 4.x/5.x API):**
- **Scalp creation**: duplicate selected body faces by vertex group or index, `bpy.ops.mesh.separate(type='SELECTED')`, then Shrinkwrap (target = body) + Mirror, then `bpy.ops.object.convert(target='MESH')` (the equivalent of Visual Geometry to Mesh).
  - Clear pins (`uv.pin=False` via bmesh, or `bpy.ops.uv.pin(clear=True)`) and `bpy.ops.uv.unwrap(method='ANGLE_BASED')`.
  - For a ponytail: `primitive_plane_add`, subdivide twice, then make it circular in code; LoopTools is an add-on, so position the vertices on a circle directly.
- **Hair object**: `bpy.ops.object.curves_empty_hair_add()` with the scalp active. It sets the parent, `curves.surface` and `surface_uv_map`, and adds the Surface Deform modifier.
  - Or build it in code: `bpy.data.hair_curves.new()`, then `curves.add_curves(sizes)` and write `position`, then set `curves.surface = scalp` and `curves.surface_uv_map = "UVMap"`, then `bpy.ops.curves.surface_set()` (Attach Curves to Surface; this also fixes his error).
  - Guides from code: sample points on the scalp (e.g. hairline perimeter vertices), grow each strand along a direction field (normal blended with a "flow" vector per region: back/down, forward/up) with **20–30 points**, and keep strands offset from the head for volume.
- **Hair node assets**: in Essentials > Hair the assets are node groups in Blender's bundled `datafiles/assets/geometry_nodes/procedural_hair_node_assets.blend`. Load them with `bpy.data.libraries.load(path, link=False)` (data_to.node_groups = [...]) and either:
  - stack them as Geometry Nodes modifiers (`mod = obj.modifiers.new("Interpolate", 'NODES'); mod.node_group = ng`, inputs set through `mod["Socket_X"]` or the interface identifiers), or
  - build one tree per hair part (`bpy.data.node_groups.new(type='GeometryNodeTree')`) with group nodes, as in the course.
  - The asset names in the transcript: Interpolate Hair Curves, Set Hair Curve Profile, Clump Hair Curves, Create Guide Index Map, Frizz Hair Curves, Hair Curves Noise, Blend Hair Curves, Trim Hair Curves. Verify the exact socket names by listing `ng.interface.items_tree` in the installed version.
- **His tree, as a template for each hair part**:
  1. `Group Input` → Set Hair Curve Profile (radius 0.0001 m = 0.1 mm; shape about 6 for taper).
  2. → Interpolate Hair Curves.
     - Surface = Object Info(scalp), Surface UV Map = Named Attribute("UVMap"), Density high (start 50k), Mask Texture = painted image.
     - Part by Mesh Islands = True for partings; Viewport Amount 0.5 while previewing.
  3. → Clump Hair Curves (Guide Index ← Interpolate's guide index; or Use Existing Guide Map off with Guide Distance 0.015–0.04; low Tip Spread).
  4. → [secondary] Delete Geometry (Spline, Selection = Random Value Boolean p≈0.95) → Create Guide Index Map (Guides) → second Clump (Guide Index).
  5. → Blend Hair Curves (radius 0.01, Factor = Named Attribute of a "parting" vertex group).
  6. → Separate Geometry (Spline, Random Boolean ~0.1–0.25) → Hair Curves Noise on Selection (Cumulative Offset off, Scale ~10–15, Distance ~0.02, low factor) → Join Geometry with Inverted.
  7. → an optional second random subset → Trim Hair Curves (Replace Length off, Length Factor = Random Float(ID = Curve Info / index)) → Noise → Join.
  8. → Group Output.
- **Render shape**: `scene.render.hair_type = 'STRIP'` (Strip vs Strand). This is the only render setting the course mentions; the rest of EEVEE/Cycles hair settings are not covered.
- **Density masks**: either paint them procedurally (`bpy.data.images.new("main_hair_density", 2048, 2048)`, write white where a vertex group or UV region applies, then `image.filepath_raw = ...; image.save()`; remember the "save or lose it" warning), or skip the image and drive density or selection with a vertex group Named Attribute.
- **Partings**: split the scalp mesh into islands in code (bmesh `split_edges` along a seam edge list) and enable Part by Mesh Islands. Add a vertex group for the Blend factor.
- **Brows and lashes**: separate scalps (a brow patch, an eyelid ring with the front removed), very short guides (length about 0.01), Interpolate with a mask, two Clumps (0.04 / 0.02), Frizz or Noise with Cumulative Offset off. Keep the lower lashes as a separate object with low density (25).
- **UVs in code**:
  - Mark seams from edge lists or vertex groups (`edge.seam = True` via bmesh), then `bpy.ops.uv.unwrap(method='MINIMUM_STRETCH')` (available in Blender 4.3+; otherwise `'ANGLE_BASED'`).
  - Then `bpy.ops.uv.average_islands_scale()` and `bpy.ops.uv.pack_islands(margin=...)`.
  - Scale the face and head islands up by moving their UVs (bmesh loop uv) before packing.
  - To check, generate a checker: `bpy.data.images.new(..., 4096, 4096)` with `generated_type='COLOR_GRID'`.
  - Hand-straightening with pins and the Grab brush is manual work; no scripted equivalent is given.
  - MPFB/MakeHuman bodies already ship with UVs, so this chapter mostly applies to custom clothing and props.
- **Not addressed in these chapters, so it must come from elsewhere**: Principled Hair BSDF settings, hair dynamics or physics, and how the groom deforms with an armature. Surface Deform plus a scalp that is skinned or parented to the head is implied, but never shown with animation.
