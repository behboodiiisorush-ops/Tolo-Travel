# Notes: Kenny Praise masterclass, retopology chapters (files 04, 05, 06)

**Coverage (what I read):**
- `04_retopo_face.txt`: 73,527 chars, read 100% (slices 0–25k, 25k–50k, 50k–end). Covers [6:02:34]–[7:21:13] (chapter 6, face/head).
- `05_retopo_body.txt`: 114,678 chars, read 100% (slices 0–25k, 25k–50k, 50k–75k, 75k–100k, 100k–end). Covers [7:21:29]–[9:21:30] (chapter 7, body/hands/feet/cavities/eyes/teeth/reprojection).
- `06_retopo_clothes.txt`: 78,856 chars, read 100% (slices 0–27k, 27k–54k, 54k–end). Covers [9:21:51]–[10:43:43] (chapter 8, clothes).

He calls each chapter "the most important video in the entire master class" ([6:03:25], [7:22:00], [9:22:25]).
He says this is **topology for animation and offline rendering**, not for games ([6:04:51], [6:05:57]).

---

## 1. Workflow per chapter (in order, with timestamps)

### Chapter 6: theory + face/head retopo (file 04)

**Theory**
1. [6:03:44] Definition: topology is "the arrangement of vertices, edges, and faces across the surface of a 3D object". Retopology means redoing it, because a sculpt is "very dense and messy geometry… not ideal for animation".
2. [6:06:12]–[6:07:50] Game vs animation criteria:
   - Game/real-time: keep the polycount low. Important areas (e.g. the face) get more geometry, unimportant props get less.
   - Animation/offline: the model "is often going to be subdivided during rendering" (Subdivision Surface modifier), so "a higher poly count in this case is acceptable". Build it from "mostly quad geometry" so it subdivides smoothly and "deform[s] better during animation".
3. [6:07:50] Why retopo: cut the sculpt's polycount (the sculpt has "over 2 million triangles" [6:08:07]), support deformation, and make UV unwrapping, texturing and viewport speed easier.
4. [6:08:56]–[6:13:31] Terms:
   - Tris, quads and n-gons. An n-gon is any face with 5 or more edges.
   - The renderer converts everything to triangles in the end. He shows how a non-planar quad folds along a hidden triangle.
   - Quads are preferred because loop cuts pass through them. An n-gon or triangle "stops the flow of the loop cut" [6:12:26].
   - Quads give "clean edge loops", "predictable subdivision", better edge flow, and "deform more naturally".
5. [6:13:31] Edge flow: "the direction and the path that edges follow across the surface". It "should usually follow the natural forms of the character".
6. [6:14:33] Edge loops: "continuous chains of connected edges". Loops create the edge flow.
7. [6:15:36] Poles: a vertex where more or fewer than 4 edges meet.
   - "For animation topology, we want to really keep it to three and to five pole. Once you start going with six pole, seven pole, eight pole is going to cause a lot of pinching and stretching".
   - Use poles to redirect loops and to reduce the flow. Demo of going from 4 faces to 2 [6:16:41]: collapse edges, merge by distance, delete the leftover triangle. The result is one 3-pole and one 5-pole.
8. [6:18:20]–[6:21:05] Face loops needed for animation (shown on a rigged model in pose mode):
   - Around the eyes, so the eyelids can close.
   - Around the nose.
   - Around the mouth ("very important").
   - The nasolabial loop, from the nose to the mouth corner, which supports "the laugh line" in an extreme smile.
   - The face contour, from the forehead down the side of the face to the chin.
   - Around the ear.

**Preparation**
9. [6:21:37] Organize collections: `clothes`, `hair`, `high poly`. Later add `low poly` for the retopo objects [6:43:20].
10. [6:23:00] **Set real-world scale before retopo.** A default cube is 2 m tall and the character was about 10× that. Scale everything around the 3D cursor until the height is about 1.6–1.7 m, feet on the floor. Then Ctrl+A Apply All Transforms.
    - Linked duplicates cannot have transforms applied.
    - After applying scale, fix Solidify thicknesses (he ends at 0.003 on the skirt and 0.03 on another object) and Skin modifier radii.
    - Fix the origin of any object whose Mirror modifier used the origin.
11. [6:27:51] Join the head, ears, neck, body, legs and arms. First apply their modifiers (Ctrl+A > Visual Geometry to Mesh). Make the head the active object, then Ctrl+J (he says "Ctrl G"). Clear Face Sets.
12. [6:28:41] Voxel remesh them together. A voxel size of 0.076 lost the detail. He settles on **about 0.008** (in the new metre scale).
13. [6:30:03]–[6:37:28] Clean up the seams with Clay Strips (add volume), Smooth (Shift) and Crease Polish. Before retopo, sharpen the forms you will place vertices on: eyelids, the side of the nose, ear, armpit, under the breast, rib cage, back. "We really want to define these details a lot more cuz we're going to start placing vertics on this topology."
14. [6:37:44] The hands and feet are much denser, so he does not remesh them in. He adds them with **two Boolean modifiers set to Union**, applies them, then smooths the transitions. Save first, because this is slow and can crash. He also sculpts ankle bones; the inner one sits higher than the outer one [6:41:55].

**Face retopo**
15. [6:43:38] Plan the edge flow with the Annotation tool, placement set to Surface. Draw loops for the eye, nose, mouth, nose-to-mouth-corner-to-chin, forehead-to-chin contour and ear. Set annotation opacity to 0.3 and turn on "In Front".
16. [6:45:14] Start from a plane reduced to one vertex.
    - Snapping: Face Project, with "rotate and scale" enabled.
    - Turn on Statistics in the overlays.
17. [6:46:01] **Each feature loop starts with 8 edges**: extrude 4, then Subdivide → 8. Build these rings in order:
    - Eye: placed on the eyelids, then E+S rings outward.
    - Nasolabial/mouth-corner strip.
    - Mouth ring: 4 edges → subdivide → 8.
    - Face-contour ring: 4 faces on top + 4 on the bottom = 8.
    - Ear ring.
18. [6:47:22] Recalculate normals with Shift+N. Turn on the Retopology overlay ("topology", which shows blue faces).
19. [6:48:10] Add a Mirror modifier with **Clipping** and **On Cage** on, to find the centre line.
20. [6:54:05] Fill the gaps between rings.
    - F (the F2 add-on, from Get Extensions [6:57:03]) to create faces one after another.
    - M > At Center to merge, Shift+R to repeat.
    - Ctrl+R loop cuts where counts do not match.
21. [6:58:38] Add a **Shrinkwrap** modifier (target = body sculpt), shown On Cage.
    - Recurring trick: in object mode, Duplicate and Apply the Shrinkwrap from the modifier menu ("duplicate and apply"). This bakes the projection but keeps a live Shrinkwrap. Needed when the mesh sinks or relaxing misbehaves.
22. [7:00:01] Smooth the topology in Sculpt mode with the **Relax Slide** brush. Hold Shift to relax the topology. Show wireframe via Object Properties > Viewport Display.
23. [7:01:22] Fill the inside of the mouth: E, Z, S to flatten, then place verts along the lip line.
24. [7:02:11] Nose: extrude from the eyelid and lower loops over the bridge. Build a ring around the nose tip with an **even vertex count (8)**, E+S inward twice, then **Ctrl+F Grid Fill** (span 2). Grid Fill errors on odd counts.
    - [7:03:33] If the camera clips when zoomed in, reset the View clip start.
25. [7:05:01] Head: extrude across the forehead matching the edge count. Extrude the back of the head and neck, fill with F, add loop cuts, relax.
26. [7:09:08] Ear: the general approach is a ring around the rim, matching the edge count front and back.
    - Back of the ear: E+S twice, then Grid Fill.
    - Front of the ear: inner rings plus grid fills, dissolving an edge to make an odd count even.
    - "For the air [ear], you don't need to be really specific because the air is not going to deform as much" [7:14:08].
27. [7:17:28] Neck: make the ring count even (14 verts). Extrude down with S Z 0 to flatten, add 5 loop cuts, relax.
28. [7:19:04] The Mirror modifier makes relaxed loops drift upward. Fix: temporarily apply the mirror, enable X symmetry, relax, then re-add the mirror with the **Auto Mirror** add-on ([7:19:36], Edit > Auto Mirror). Place it **above** the Shrinkwrap.
29. [7:20:26] Summary: "we started low poly and then we started adding more resolution as we needed them".

### Chapter 7: body, hands, feet, cavities, eyes/teeth, reprojection (file 05)

**Theory**
1. [7:22:19] The body retopo is not done until these exist:
   - the **eye cavity** (where the eyeball sits);
   - the **mouth cavity** (for teeth, tongue and gums, so an open mouth is "not an empty space");
   - the eyeballs, teeth and tongue (taken from existing assets);
   - the sculpted detail, **reprojected** onto the retopo. "I did not say we are going to bake… We are going to repro sculpted details. Those are two very different things" [7:23:58].
2. [7:24:16]–[7:26:43] Body loops needed for deformation (shown on a rig):
   - **Shoulder loops**: loops round the shoulder to the back, plus loops round the armpit. They make "the shoulder… deforming really nicely".
   - **Elbow**: "this kind of patch at the back of the elbow". When bent, it is "helping us retain the shape".
   - **Wrist loops**.
   - **Knee**: the same patch as the elbow, "preserving the shape of the knee".
   - **Hip loops**: "helping to preserve the volumes".

**Torso**
3. [7:27:15] Add a Circle with **10 vertices**, placed under the armpit (scaled S Y to wrap it). Shift+D a copy, rotated, for the arm loop. Extrude front and back, Shift+N, add Shrinkwrap, "duplicate and apply".
4. [7:29:42] Leave 3 faces on top for the shoulder. Avoid triangles by adding loop cuts so the fill stays quads ("We don't want triangles for this topology").
5. [7:30:46] Add a Mirror modifier (clipping and on cage), moved above the Shrinkwrap. Two 10-vert loops → Ctrl+E **Bridge Edge Loops**, which needs equal vertex counts.
6. [7:31:51] Ctrl+R subdivide the loops. Check: the arm loop should end at **20 vertices** ("that's how I know you did that correctly").
7. [7:33:09] **Match counts before joining parts.**
   - The neck opening of the body (9 verts / 8 edges) has to match the head's neck ring (14 verts / 13 edges).
   - Add loop cuts and remove one edge. Put more edges in front than behind.
   - Snap each vertex to the corresponding head edge so they join easily.
8. [7:36:08] Chest/breast: extrude down the middle, follow the breast. Female: E+S rings to the centre, then Grid Fill (add loop cuts if counts error). Male: add a loop for an even count and grid fill directly [7:37:28].
9. [7:40:28] **Turn off snapping before extruding** (Face Project snaps the extrusion wrongly), then turn it back on and place each vertex.
10. [7:42:22] **Add local detail without sending loops all the way round** (rib cage), the "bevel trick":
    - Select edges, Ctrl+B bevel with 2 segments.
    - Turn on Auto Merge Vertices, GG-slide the end verts onto their neighbours to kill the n-gons.
    - Ctrl+X dissolve the leftover triangles.
    - Result: "more vertices without taking more [loops] to the back". Reused at the elbow, knee, finger joints, ankles and clothing folds.
11. [7:44:47] Hip/pelvis: extrude 3 edges down and around the hip without merging at the middle. Shape the hip loops with the Grab brush [7:46:26]. Extrude the leg opening flat (S Z 0).
12. [7:46:43] "The legs and the hands are just essentially tubes".

**Legs and arms**
13. [7:48:40] Leg:
    - Extrude the ring down. Add a loop at the knee rotated to follow the knee.
    - Loop cuts: 4, 4, 4 and 7.
    - [7:50:18] Make the number of faces down the leg **even**: "That's going to make the leg a little bit easier."
    - Relax to keep the topology "not too pinched together".
14. [7:52:59] Arm: the same approach. Loop at the elbow, cuts of 9 and 8.
    - If relax "pops", duplicate-apply the Shrinkwrap.
    - Follow the sculpted elbow curve with a bevel (2 segments), GG-slide to remove the n-gon, Ctrl+X to remove the triangle.
15. [7:56:46] **Elbow joint loops**: bevel the edge pair, auto-merge, dissolve the triangle, relax so it follows the sculpted elbow.
16. [7:58:10] **Knee**: rotate the loop to the knee curvature, bevel and dissolve. Do the same above the knee.
17. [8:00:37] Join the body and head (Ctrl+J; same modifiers on both, so it is fine). Bridge the neck loops (Ctrl+E), relax.

**Hands**
18. [8:01:43] Start with a cube per finger.
    - Delete the face at the finger root. Put loops at the **joints** ("where the joint of this finger is going to be").
    - Duplicate it per finger, scaled and rotated.
    - The **thumb has 2 joints**, so delete one loop [8:06:03].
19. [8:06:52] Finger layout: **2 rows of faces on top and 3 faces on each side**. Snap the side faces to the sides of each finger. Bridge neighbouring fingers with F. Add a middle loop cut to follow the sculpt.
20. [8:09:48] Extrude the ring round the finger base into the palm (snapping off). Add LoopTools > Relax and 3 loop cuts. Line the loops up with the knuckles and the sculpted palm crease.
21. [8:11:47] **Match counts.**
    - Finger base ring 34 verts vs arm 20: collapse edges with Auto Merge and dissolve the triangles → 22.
    - Hand ring 26 → 22 by connecting a loop back on itself.
    - → 20 by connecting the 3 side faces of the fingers with those on the thumb [8:19:25].
    - It ends equal to the arm's 20.
22. [8:20:13] Fingers: 3 loop cuts per segment, plus loops at the fingernail start.
    - [8:20:46] **Finger joint topology**: "you want to make sure that the fingers bend really nicely". Bevel the two top faces at each joint (Ctrl+B), GG-slide verts down with auto-merge, dissolve the extra edges. "This is the topology that we want for each of these finger joints."
    - Do this on all joints and the thumb. Add loops at the fingers "so when it starts to deform, it actually deforms really nicely" [8:23:57].
23. [8:25:20] Fingertips: 2 loop cuts, then Inset (I) the tip faces.
    - If the character has nails, use the same steps lined up to the nail and add a loop there.
    - Watch out for auto-merge joining verts by accident when insetting [8:26:42].
24. [8:28:39] Join the hand to the body and bridge the loops. **Add 2 loop cuts at the wrist** ("Remember we said we want loops around the wrist").

**Feet**
25. [8:29:42] Toes: one cube per toe, same method as the fingers (3 faces on the sides), with 2 loop cuts per toe. Extrude the base ring back and relax it.
26. [8:34:55] Collapse the 42-vertex outflow by merging edge pairs and dissolving the triangles.
27. [8:36:51] Extrude the sole and heel. Connect the loops back on themselves at the heel. Fill the bottom with an even count (add a loop when it is odd) and merge at centre.
28. [8:41:13] Reduce 26 → 24 → 22 verts to match the leg's 22: extrude a strip up and close it with faces.
29. [8:42:17] Toes "don't deform as much… not going to pay much attention to them". He still adds 2 loops per toe.
30. [8:43:24] Join to the leg, bridge, add 2 loops. Ankle shape uses the bevel trick [8:43:56].

**Face cleanup**
31. [8:45:35]–[8:47:33]
    - Push the mouth edges closer to the corner and add a loop "to retain the shapes of the mouth".
    - Add extra loops at the eyes "so when the eye starts to close… the topology is going to be able to support the closing of the eye".
    - Apply the mirror, enable X symmetry and relax the centre seam.

**Eye cavity** [8:48:40]
32. Re-add the mirror (Auto Mirror). On the eyelid border loop, E+S inward and GG/C-push back to give the eyelid an "even thickness around the whole eyelid".
33. Then E+S a ring and push it deep into the head. Round it into a sphere-ish socket (LoopTools Relax). Add loops and Alt+S to thicken.

**Mouth cavity** [8:52:14]
34. Extrude the lip-inner loop back along Y and overlap the lips, so you "don't see through the mouth" from the front.
35. Build a bag shape (annotation side and top profile): S Y 0, scale, LoopTools Relax, loop cuts. Shape it with Grab/Inflate.
    - Inflate behaves inverted "because these faces are inverted… which is actually how we want it", so hold Ctrl [8:57:14].
36. Test: open the mouth with proportional editing to check there is something visible inside [8:58:35].

**Eyes, teeth and tongue from assets** [8:59:24]
37. Get the **Blender Studio "Human Base Meshes"** bundle from blender.org/download/demo files: "free assets… both on personal projects and… commercial projects".
    - Add it as an asset library (Preferences > File Paths, import method **Append**). Copy the bundle to the library.
    - From the Stylized category use the **jaw** (teeth, gums, tongue) and the **eyes**.
38. Alt+G to clear location. Scale the eyeball to match the sculpt's eye and shade smooth.
    - **Check: rotate the eyeball (R R) and make sure it does not clip through the eye cavity** [9:03:49].
    - Mirror to the other side.
39. Fit the teeth and widen the mouth cavity (S X with proportional editing). Delete unseen faces of the asset (L-select, delete hidden faces under the tongue and gums) "to optimize the mesh".

**Reprojection** [9:06:17]
40. Apply the Mirror. Add a Shrinkwrap targeting the sculpt.
    - The cavities must not be projected: assign the eye and mouth cavity verts to the vertex group **"no shrink wrap"**. Set it as the Shrinkwrap vertex group with **Invert**.
41. Add a **Multiresolution** modifier **above** the Shrinkwrap and Subdivide twice → "most of our details are back". Apply the Shrinkwrap.
42. Sculpt on the multires to re-sharpen: eyelids, lip crease, mouth corners (Inflate to close the gap so the teeth are not visible), nostrils, ear forms, knee, ankles, knuckles, finger joints. "We're not adding extra details… just to refine". Shortcut Shift+Q toggles wireframe.
43. [9:19:16] **Do not apply the multires** ("you're going to have too much resolution… less optimal for animation and deformation"). Use Multires > Shape > **Apply Base**, which pulls the base cage toward the sculpted shape. Then remove the multires. With subdivision, the details still come through.

### Chapter 8: clothes (file 06)

**Theory**
1. [9:22:42] Use the same techniques as the body. Key rule: "**keep the same or similar topology with the underlying geometry**".
2. Demo [9:23:14]: a shirt with unrelated topology, rigged, in pose mode "is breaking", and hip rotation makes it clip through the body. A shirt duplicated from the body topology shows "no form of clipping".
   - With folds or collars you cannot match exactly, "so we want to just try to keep similar topology".
3. [9:24:53] Every garment differs, so watch the thought process.

**His written 6-step process** [9:26:17]
1. Make the base topology from the body.
2. Align the topology with the seams.
3. Align the topology with the folds.
4. Reinforce the seams.
5. Add cloth thickness.
6. Reproject sculpted details (if any).

**Shirt**
4. [9:25:26] Collection `clothes_topology` inside `low poly`. Duplicate the body retopo and name it `shirt_topo`. Delete the faces outside the garment.
5. [9:28:54] Remove the Subdivision Surface modifier. Add a Shrinkwrap to the cloth sculpt.
   - **Disable the sculpt's Solidify** so the projection lands on the front surface.
   - Duplicate-apply the Shrinkwrap.
6. [9:29:58] Delete half and add a Mirror (clipping). Remove body-only support topology (the rib-cage bevel extras) by sliding verts onto themselves with auto-merge. Delete unneeded faces and rebuild the bottom hem by extruding. Relax.
7. [9:33:31] **Align to seams** (collar, sleeve): put edge loops exactly on the sculpted seams. Rebuild the sleeve topology where the body flow does not fit (extrude down, 4 loop cuts). Remove an unnecessary pole ("I don't really like this pole… It's not really necessary") and rebuild it.
8. [9:38:19] **Align to folds**: annotate the high and low points of each fold and move loops onto those lines. Add geometry for folds with the bevel trick (2 segments, GG-slide with auto-merge, dissolve triangles). Then shape the extra verts into the fold.
   - "We are going to be [baking] the normals of this clothes. So we just want the topology to follow the shape of the clo just a little bit more. Then we are going to use the normals to get in back all our details" [9:43:16].
9. [9:46:16] Too many edges compressing toward the sleeve end: collapse edge pairs into one (auto-merge), dissolve the triangles, and make a "diamond shape". This reduces the edge count down the sleeve "while still maintaining the folds".
10. [9:48:10] **Reinforce seams**: "adding more geometry to the seams so that when we subdivide this the seams are still intact". Bevel the seam loop so there are supporting edges in front of and behind it.
    - **Intersecting seams**: select the crossing vert, S 0 with auto-merge, then Ctrl+X dissolve the extra edges.
    - Keep space between reinforced seams and other loops, and avoid stretched faces. "Even [quad] topology all around."
11. [9:51:16] **Thickness**:
    - Apply the Mirror. Add Solidify; preview it with a temporary Subdivision (Ctrl+1) "to gauge the type of thickness". **0.007** for the shirt. Then remove the subsurf.
    - Problem: the Shrinkwrap also pulls the solidified inner shell and rim onto the sculpt.
    - Fix: Solidify output vertex groups **"shell"** and **"rim"**. Apply. Put the shell and rim verts in a new group and set it as the Shrinkwrap vertex group, **inverted**.
    - [9:53:55] Add a loop near the rim and Alt+S to round the edge.
    - [9:54:29] **Delete the inner faces that will never be seen** (Ctrl+Shift+M mirror selection, extend). "Optimize this mesh".
12. [9:55:49] **Reproject**: Multires above the Shrinkwrap, subdivided twice; apply the Shrinkwrap.
    - For clothes he does **not** Apply Base. He keeps the multires "because we are going to be baking down the normals".
    - You can sculpt smaller folds on the multires to bake.

**Skirt** [9:57:23]
13. Same 6 steps, base from the body (delete the non-skirt faces), mirror, disable the sculpt Solidify, Shrinkwrap.
    - Leave a hole open rather than fill it with a triangle: "easy enough to fill this in with a quad" later [10:03:21].
    - Align to the seams and add loop cuts. Folds were mostly handled already.
    - Reinforce the seams with a bevel; intersecting seams again use S 0 + dissolve.
    - [10:10:13] Reduce 4 edges to 2 to close holes with quads.
    - Add supporting edge loops at the edges.
14. [10:12:07] Solidify:
    - Add a loop at the bottom to fix "weird" shading.
    - Use the shell/rim group trick.
    - Delete unseen inner faces, but go "higher a little bit because this is the skirt… potential of it being seen".
    - Slide the inner shell verts back so they do not intersect.
    - Sculpt-mode Symmetrize +X→−X. Add loops at the hem and waist with Alt+S to round.
15. [10:16:33] Multires with 1 subdivision ("delete higher"), then apply the Shrinkwrap.

**Shoes** [10:17:21]
16. Base from the body (delete everything but the foot; delete the sole-bottom and unneeded faces). Remove the subsurf. Shrinkwrap to the shoe sculpt with its Solidify off.
17. Rebuild the toe tip by finding the middle edges by counting (14 edges) and bridging with F.
18. Align to the seams and the shoe design. Rip (V) to remove a triangle and rebuild with quads [10:26:20].
19. Align to the folds (annotations, bevel-add geometry, dissolve triangles, supporting loop) [10:27:44]. Reinforce the seams with a bevel.
20. Thickness: Solidify previewed with a subsurf, shell/rim groups. Delete the unseen bottom and inner faces. Multires ×2, apply the Shrinkwrap.
21. [10:38:33] Parts already modelled as clean low poly (sole, ring/eyelet) are **reused** rather than retopologized:
    - duplicate into `low poly`;
    - apply or remove the modifiers (Skin, Subsurf, Mirror);
    - dissolve unnecessary edges;
    - Ctrl+M mirror the copy for the other side.
22. [10:42:38] **End state rule**: "for the close topology objects… it should either have the mult modifier or you should have a subdivision of his modifiers. All other modifier should be applied at this stage." Mirroring the shoe waits until after UV unwrapping.

---

## 2. Concrete techniques, rules, values, tools, checks and warnings

### Topology rules for deformation
- **All quads.** N-gons and triangles break loop flow and subdivision. He repeatedly removes the triangles and n-gons a bevel creates (GG-slide with Auto Merge, then Ctrl+X Dissolve). A hole is left open rather than filled with a triangle.
- **Poles: only 3- and 5-poles.** 6+ cause "pinching and stretching". Use poles to redirect loops and reduce face counts (4→2 demo). Remove poles that are "not really necessary".
- **Face loops**: eyes (for the lid closing; add extra loops so the "closing of the eye" is supported), nose, mouth ("very important"; push loops to the corner and add a loop to keep its shape), nasolabial (laugh line), face contour (forehead → side → chin), ear (low deformation, can be looser).
- **Body loops**:
  - Shoulder: loops around the shoulder continuing to the back, plus loops around the armpit.
  - Elbow: a patch at the back of the elbow made with the bevel trick.
  - Wrist: 2 extra loops.
  - Knee: the same patch, plus extra loops above.
  - Hips: loops around the hips to "preserve the volumes".
- **Fingers**:
  - 2 face rows on top and 3 faces per side. Loops sit exactly at each joint (thumb 2 joints).
  - Joint topology uses a bevel on the top faces, slid down and dissolved, "so the fingers bend really nicely".
  - 3 loop cuts per segment, plus extra loops "so when it starts to deform, it actually deforms really nicely". A loop at the nail start.
- Toes deform little, so they get less care (2 loops each).
- **Local detail without full loops**: bevel 2 segments, GG-slide the ends with auto-merge, dissolve the triangles. Used for rib cage, elbow, knee, ankles, finger joints and cloth folds.
- **Even counts**: Grid Fill needs an even vertex count on the ring. Leg faces are made even. Bridge Edge Loops needs equal counts on both loops.
- **Match vertex counts at junctions before joining**: neck 14v/13e, arm 20v, hand → 20, leg 22, foot → 22. Reduce with collapse-and-dissolve or by looping edges back on themselves.
- **Start feature loops with 8 edges.** The torso starts from a 10-vert circle → 20.
- Even, relaxed spacing ("not too pinched together", no "stretched" faces). Add loops where faces stretch.
- Keep the edge flow on the sculpted forms (knuckles, palm crease, elbow curve, rib cage, ankles) "so that we retain the forms of the sculpt".

### Clothing topology rules
- **Same or similar topology to the body under it**. A clothing mesh that does not match "breaks" and clips in pose; one made from duplicated body topology does not.
- Build it by **duplicating the body retopo** and deleting faces, then projecting onto the cloth sculpt.
- Put loops exactly on the seams and **reinforce the seams** with bevel support loops on both sides, so they survive subdivision. Crossing seams: scale the crossing to 0 and dissolve.
- Align loops with the high and low points of the folds. Use the bevel trick for extra fold geometry. Fine fold detail goes to baked normals.
- Reduce edge counts toward sleeve ends with collapses ("diamond shape") while keeping the folds.
- Thickness with Solidify (shirt **0.007**). Preview with a temporary subsurf. Round the rims with a loop plus Alt+S.
- Delete inner and unseen faces (go further on a skirt, where the inside can be seen). Slide the inner shell verts so they do not intersect.
- The final garment carries **only a Multires or a Subdivision Surface**; apply everything else.

### Tools, modifiers and add-ons
- **Snapping**: Face Project with rotate/scale alignment. **Turn snapping off before extruding**, then on again to place verts. Auto Merge Vertices on for slides and merges; off when it would merge by accident (insets, mirroring copies).
- **Shrinkwrap** (target = sculpt), shown On Cage. "Duplicate and apply" to bake projection mid-work and fix relax popping. Vertex group with Invert to exclude cavities ("no shrink wrap") and solidify shell/rim.
- **Mirror**: Clipping and On Cage; placed **above** the Shrinkwrap. Auto Mirror add-on. Apply it before the final relax on the centre seam, using X-symmetry in sculpt mode.
- **Relax Slide brush** with Shift in Sculpt mode, the main topology smoother. Show wireframe via Object Properties > Viewport Display > Wireframe.
- LoopTools > Relax. Grid Fill (Ctrl+F, span 2). Bridge Edge Loops (Ctrl+E). Loop cut (Ctrl+R). Bevel (Ctrl+B, 2 segments). Inset (I). Rip (V). Merge At Center (M). Repeat (Shift+R). Mirror select (Ctrl+Shift+M). Recalc normals (Shift+N).
- Overlays: Statistics (count edges and verts); Retopology overlay (blue faces; recalc normals if a face is not blue).
- **Annotation tool** (placement Surface) to plan loops and fold lines.
- **Add-ons**: **F2** (fast face fill with F), **Auto Mirror**, **LoopTools**, Screencast Keys (for recording only).
- **Multiresolution** for reprojection (2 subdivisions on the body and shirt/shoes, 1 on the skirt). Body: **Apply Base**, then remove it. Clothes: keep it for normal baking.
- **Solidify** with output vertex groups "shell" and "rim".
- **Boolean Union** to attach the dense hands and feet to the remeshed body sculpt.
- **Voxel remesh** at about 0.008 (after setting 1.6–1.7 m scale).
- Blender Studio **Human Base Meshes** asset bundle (eyes, jaw with teeth, gums and tongue), library import method Append.

### Checks he does
- Count verts and edges (Statistics) at every junction before bridging. Count the arm loop = 20 "that's how I know you did that correctly".
- Even count before Grid Fill.
- Normals: blue faces in the retopo overlay, Shift+N otherwise.
- The mesh should not sink into the sculpt (duplicate-apply the Shrinkwrap).
- **Pose tests** in the theory sections: the eyelid closes, the mouth deforms, shoulder/elbow/wrist/knee/hip bend, clothes on a rig clip vs not.
- Eyeball rotation does not clip through the cavity.
- An open mouth shows the cavity, not a void, and you cannot see through the closed mouth from the front.
- Inspect the topology "from all angles". Isolate a mesh in object mode to see whether the folds read in the silhouette.
- Preview solidify thickness under subsurf.
- Shading at hems: add a loop where the shading looks weird.

### Common mistakes he warns about
- Retopologizing without real-world scale. Linked duplicates will not apply transforms. Solidify and Skin values change after applying scale.
- Remeshing the dense hands and feet together with the body gives "a lot of geometry"; use Boolean instead. Save before booleans, which can crash.
- Extruding with snapping on (bad placement).
- The Mirror modifier makes relaxed loops creep up at the centre.
- The Shrinkwrap pulls the cavities and solidify shell onto the sculpt (fix with an inverted vertex group). The cloth sculpt's Solidify must be off when shrinkwrapping.
- Leaving triangles or n-gons after bevels. Unnecessary poles. Poles of 6+.
- **Applying the multires on the body** gives "too much resolution… less optimal for animation and deformation".
- Auto-merge accidentally merging inset verts or mirrored copies.
- Too-dense outflow from fingers and toes into the arm and leg (34 vs 20); reduce it.

**No numeric total polycount target is given** in these three chapters. The only polycount statements are: games keep it low; for animation "a higher poly count… is acceptable" because it is subdivided at render; and the sculpt had "over 2 million triangles".

---

## 3. Applicable to a scripted bpy pipeline (MPFB bodies + code-made clothes/accessories)

Our MPFB/MakeHuman base mesh already has the animation loops he builds by hand (eye/mouth/nasolabial rings, shoulder/armpit, elbow, wrist, knee, hip, finger joints). So we do not retopo bodies. Rules to adopt, each tied to what he says:

**A. Body (MPFB)**
1. Do not apply a high subdivision or multires into the mesh that gets rigged. Deform the base mesh and add a **Subdivision Surface modifier after the Armature** in the stack (viewport 0–1, render 1–2). This follows his point that the animation mesh is "subdivided during rendering", and his warning that baking in resolution is "less optimal for animation and deformation".
2. Keep the final object stack minimal: Armature → (corrective/shape keys) → Subsurf. This matches his rule "either… the mult modifier or… subdivision… All other modifier should be applied".
3. Work in real-world scale (MPFB is ~1.6–1.8 m) with transforms applied before parenting or rigging. Scripted check: `obj.scale == (1,1,1)` and `rotation == 0` on every deforming mesh.
4. Eyes, teeth and tongue: use the MPFB eye/teeth/tongue proxies (or Blender Studio Human Base Meshes, which are free for commercial use). Script checks:
   - rotate each eye bone or object ±30° and test the eyeball vs eyelid/cavity mesh for intersections (BVHTree overlap). His check is "rotate it… not clipping".
   - with the jaw open, the mouth interior must exist; the cavity has to be closed so no hole shows.
5. **Deformation QA render**: before a film, script a pose-test turntable or contact sheet per character with blink (eyelids fully closed, no lid poke-through), wide smile/open jaw, arm raised to 150°, elbow and knee at 120°, wrist twist, fist (finger joints), hip twist. This is his pose-mode demo, done as an automated check.

**B. Clothes and accessories built by code**
6. **Derive garments from the body topology** instead of free primitives. Select body faces by vertex group or region (MPFB has body vertex groups / helper geometry; or select by distance from bones), duplicate them, delete the rest, then inflate along the normals or Shrinkwrap with an offset to the garment shape. This is his #1 cloth rule ("same or similar topology with the underlying geometry" → "no form of clipping"). MPFB/MakeHuman clothes (`.mhclo`) already follow this; prefer them, or fit through MPFB's clothes fitting.
7. **Weights**: copy weights from the body to the garment with a Data Transfer modifier (vertex groups, nearest face interpolated), then apply it. Add an Armature modifier. Because the topology matches, the weights match.
8. **Topology checks in script** for every generated garment or accessory, using `bmesh`:
   - n-gons = 0 (faces with >4 verts);
   - triangles ≈ 0 on deforming parts (allowed on rigid accessories);
   - poles with valence ≥6 = 0 (his "keep it to three and five pole"); report the count of valence-3/5 poles;
   - no non-manifold edges except intended open borders; normals consistent (his Shift+N / blue-faces check);
   - loops across a bending joint: at least 3 edge rings within the joint region (elbow, knee, shoulder for sleeves/trousers) so the garment can bend like the body;
   - edge-length uniformity, to flag stretched or pinched quads ("not too pinched", "too stretched").
9. **Thickness**: Solidify on garments.
   - His real-scale values: shirt 0.007 m, skirt 0.003 m (thin fabric). Thicker items about 0.01–0.03 m.
   - Put Solidify **before** Subsurf in the stack so the subdivided rim stays clean. Use `use_rim` and set `shell_vertex_group`/`rim_vertex_group` if later steps (shrinkwrap/offset) must skip them.
   - Delete or skip inner faces that are never seen to save polys (except skirts/open garments, where the inside shows).
   - Round hem edges with an extra support loop near the rim (his Alt+S loop).
10. **Seams and hard edges under subdivision**: reinforce them with support loops (a bevel with 2 segments, or `bmesh.ops.bevel` on seam edges), or use edge crease (`crease_edge` attribute). This follows his "reinforce the seams… so that when we subdivide this the seams are still intact". Collars, cuffs, hems and shoe welts need it.
11. **Clipping prevention**:
    - keep the garment offset from the skin (Shrinkwrap with offset, or Displace along normals);
    - the body under tight clothes may get a mask (Mask modifier / delete hidden body faces), the same idea as his "delete faces we'll never see";
    - test it with the deformation QA poses in item 5 (raycast or BVH overlap of the body through the garment per pose).
12. Folds: do not model fine folds into the deforming cage. He moves the cage loops to the high and low points of big folds and bakes the small ones to normal maps. For our toon/cel pipeline, keep garment cages smooth and let the shading or outlines carry it. Only add geometry (the bevel trick) where a fold changes the silhouette.
13. Edge-count matching: when code joins two generated parts (sleeve to cuff, leg to boot), make the boundary loops have equal vertex counts before `bridge_edge_loops`. Even counts are required for grid-fill caps (`bmesh.ops.grid_fill`).
14. Rigid accessories (bags, watches, buttons, shoes' soles/eyelets): he reuses clean existing low-poly parts rather than retopologizing them. For us: parent them to a bone (or use one-bone rigid weights). Bending topology is not needed, but keep quads and apply modifiers except the final Subsurf.
15. **Subdivision levels**: viewport 0–1, render 1–2. Hard-surface or seam fidelity comes from support loops or crease, not from higher levels. This is consistent with his body (2 multires levels for detail recovery only) and his rule of one Subsurf at the end.

**C. Not applicable or skipped**
- Manual retopo with F2, Relax Slide, annotations, voxel remesh and Boolean union of sculpt parts. These are sculpt-pipeline steps; MPFB replaces them.
- Multires Apply Base reprojection: only relevant if we sculpt custom detail onto an MPFB body. Then use a Multires modifier → Apply Base (or Shape Keys) and never apply the multires levels into the rigged mesh.
