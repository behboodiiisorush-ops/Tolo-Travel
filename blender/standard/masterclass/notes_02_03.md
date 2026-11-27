# Notes: Kenny Praise masterclass, Chapters 4 (body/hands/feet) and 5 (clothes/accessories/hair)

**Coverage read:** `02_body.txt`: 100% (all 94,860 characters, in four slices 0–25k, 25k–50k, 50k–75k, 75k–end; transcript runs [2:28:05] to [4:14:46]).
`03_clothes.txt`: 100% (all 92,387 characters, in four slices 0–25k, 25k–50k, 50k–75k, 75k–end; transcript runs [4:15:04] to [6:02:14]).

Caveats:
- The transcript is auto-generated, so some words are garbled. "Purifier" is PureRef. "clues brush", "client brush" and "glitches brush" all mean the Clay Strips brush. "crease polish" is the Crease Polish brush. "script brush" is the Scrape brush. "engra/in place" is most likely the Grab or Inflate brush. "M modifier" is the Mirror modifier. "glute/clute/CL" means cloth/clothes. "skit/sket" means skirt. "fits/pits" means feet.
- Numbers spoken as "0.0 six" or "0 73" are written below exactly as transcribed, with my reading in brackets.
- The workflow is manual sculpting. The character is a stylised female sculpted over earlier blockout primitives (round cubes and similar shapes from previous chapters).

---

## 1. Chapter 4: Body, hands, feet. Workflow in order

### Theory (slides), [2:28:05]–[2:39:36]
- [2:28:54] **Observation over anatomy charts.** "You don't need to memorize anatomy charts". The real skill is to "observe your reference and translate what you see… onto your 3D sculpt". The reference "is going to become your anatomy guide". It should "naturally guide the proportions, the volumes, and the structure". If your reference is weak, get a better one.
- [2:30:16] **Arms are "interlocked chains".** Shoulder interlocks with the bicep, the bicep with the lower arm, the lower arm with the wrist/hand. Get these forms first, then refine the muscles from the reference.
- [2:31:22] **Legs: "straight versus curves".** On the upper leg the front is curved and the back is straight. On the lower leg the back is curved and the front is straight. This contrast "is going to create a lot of rhythm… prevent your character from being stiff."
- [2:32:14] **"Angry face" over the lower leg.** It keeps leg proportions correct. On the inside of the lower leg the high point sits higher than on the outside. "The inner ankles sit higher than the outer ankles. They should never sit on the same horizontal line."
- [2:33:05] **Torso** varies by character, so rely heavily on the reference. "Think in rhythm and balance", so forms flow into one another even in a T-pose. **Check the silhouette often** (zoom out; he keeps a second viewport to the side for this). "A clean silhouette is a good sign that our forms are working together."
- [2:34:25] **Hands: start from simple shapes.** The palm is a rectangle with a **wedge** attached where the thumb comes out.
  - The **palm is not flat**. It has a natural curve "so the fingers feel relaxed rather than stiff".
  - The **knuckles sit on a curve**, not a straight line. Each further row of finger joints sits on a **steeper** curve.
  - **Finger proportions:** knuckle to fingertip is one unit. The first joint is at the halfway point. The second joint is halfway between the first joint and the tip.
  - **Joint angles:** "the first joint angles slightly backward", the second goes "upward and forwards a little", the third goes forward. Avoid perfectly straight fingers.
- [2:37:43] **Feet: a triangle.** From the front and the side the foot is a **right-angle triangle** attached to the leg, not an isosceles one.
  - From the bottom it is a **rectangle**; then push the sides in.
  - From the side it stays triangular, but the midsection pushes inward and up into an **arch**.
  - Use **stepped toes** for a gradual transition into the foot.
  - Ankle: same angry-face rule, the inner ankle is higher.

### Hands in Blender, [2:40:27]–[3:23:15]
1. [2:40:43] Shift+A, add a Cube and turn off snapping. In Edit Mode, scale it on Z, rotate it to the hand's angle and move it to the palm. Move the front faces back and scale on Y to block out the palm. Hide the earlier hand blockout.
2. [2:41:48] Add a **loop cut in the middle and raise it** for the palm curve, then two more loops raised for more curvature. Add more loops, then **extrude four faces twice** to form the thumb wedge and shape it. Use **GG (edge slide)** to relax the loops. Ctrl+R, then Alt+S to scale out slightly. Size the finger area at the end of the palm so the fingers "fit right into this place". He turns on the Screencast Keys add-on to show his keypresses.
3. [2:44:12] In Sculpt Mode, shape with the Grab brush and Shift (smooth). Make the wrist flow into the lower arm.
4. [2:45:01] Add a **Mirror** modifier, then a **Subdivision Surface** modifier. Tip: right-click a modifier and choose "Add to Quick Favorites", then open it with Q. Thin the palm where it is "too thick". In Edit Mode, Alt+Z (X-ray), select two edges and pull them down to mark the fat pad on the other side of the thumb.
5. [2:47:09] **Fingers from a single-vertex skin chain:**
   - Add a Cube. In Edit Mode, select all, M, "At Center" to merge everything into one vertex. Turn off the Origins overlay if needed.
   - **Do not move that vertex in Edit Mode**, so the origin stays at the knuckle for rotating the finger. E to extrude along X.
   - Add a **Skin** modifier, then **Subdivision Surface level 1**. In Edit Mode, **Ctrl+A** (skin resize) sets finger thickness.
   - Position and rotate in **Object Mode** only.
6. [2:49:49] **Duplicate fingers with Alt+D (linked duplicate)**, so an edit-mode change on one finger changes all of them. Spread and rotate the fingers. Lengths: pinky shortest, then ring, middle longest, then index. Leave space between fingers. Place the fingers "following the curvature of the palm".
7. [2:52:02] Ctrl+R to add a mid vertex and angle the tip up. Ctrl+A to narrow the tip. Add another loop and bend it more.
8. [2:53:23] **Thumb:** duplicate a finger with **Shift+D** (independent data). Rotate it with R R (trackball). Shorten it, Ctrl+X to dissolve a vertex, Ctrl+A to fatten. Vary the radius along its length (scale in/out per vertex). Seat it in the thumb wedge and check from all angles. Reshape the palm around the thumb.
9. [2:56:20] Apply the palm's Subdivision Surface for more resolution. Grab it into the thumb. Use Inflate (probably) to round the fat pads, then smooth.
10. [2:57:44] **Pivot = Individual Origins** (period key pie menu) to scale all fingers from their own knuckles, then return to Median Point.
11. [2:58:18] Applying modifiers on linked data gives an error. Workaround: select all fingers, **Ctrl+A, "Visual Geometry to Mesh"**. The objects stay linked, so a sculpt on one still transfers to the others.
12. [2:59:10] Sculpt with **Y symmetry** ("it might either be the X symmetry for you or the Y symmetry", depending on orientation). Drag out the tip and shape the sides.
13. [3:00:18] **Mark joints with the Crease Polish brush, small radius,** at the half and quarter proportions. Draw annotation lines first, then erase them. "You don't want to overdo this."
14. [3:01:24] **Fingernail bed:** use Scrape to flatten the area and Grab to push it down. He adds no nails for this character. At [3:11:09] he shows how to add nails anyway: outline with Crease Polish, Ctrl to sharpen the edges, keep the nail flat.
15. [3:01:57] Upper joint creases with Crease Polish and Ctrl (inverted), following the backward / up-forward / forward angles.
16. [3:03:02] Thumb: Visual Geometry to Mesh, then sculpt. "Most time [symmetry] doesn't work for the thumb", so sculpt it symmetrical by hand.
17. [3:05:25] **Save Incremental** (File menu).
18. Palm: **remesh voxel size 0.025, then Ctrl+R**, then gently smooth.
19. **Alt+B clipping region** isolates part of the viewport without hiding objects.
20. Palm details from the reference: creases with Crease Polish (Shift+C), volume with Clay Strips plus smooth. Flatten the top of the palm with Scrape. Define the edges with Crease Polish and Ctrl.
21. [3:09:31] Fingers: **remesh 0.01**, gently smooth ("we don't want to get rid of our main shape"). Make the joint creases "really subtle". Thumb: also 0.01.
22. [3:14:04] **Join (Ctrl+J; transcript says "Ctrl G")** the fingers into the palm with the palm active.
   - Remesh at **0.01**. "If you go with a low resolution… the mesh is like sticking in between the fingers."
   - After joining, the fingers must be sculpted individually, so be happy with them before you join.
   - **Blend transitions:** draw straight Clay Strips strokes "coming in from the palm" onto the fingers, then smooth. Add volume at the sides and smooth.
   - Make the palm "flush with the fingers". Crease Polish the bottom finger creases and the palm creases.
   - Adjust the lower arm to fit the hand.
23. [3:21:25] Mark the knuckles with Crease Polish and Ctrl ("always looks nice for most characters"). Flatten the sides. "Rotate around your sculpt… make sure that the forms are looking good from all angles." A higher remesh would allow more refinement, which he skips to save time.

### Feet in Blender, [3:23:15]–[3:47:33]
1. Add a **round cube** (from earlier chapters). Scale it on Z, X and Y to the foot size.
2. From the bottom view (−Z), use the Grab brush to make a **rectangle**.
3. [3:25:28] Use the **Lasso Mask** to protect the sole, then Grab up into the triangle and into the leg. Gotcha: **turn off "Front Faces Only"** on the lasso mask, otherwise hidden faces are not masked. Ctrl+drag unmasks. **Alt+M** clears the mask.
4. Push it into a **right-angle triangle**. Smooth the sharp areas. **Inflate the heel/back of the leg into a "teardrop shape".** Adjust the lower leg to the new foot.
5. [3:29:44] Use the **Line Project** brush (with lasso) to cut a flat plane. Grab the toe area forward.
6. [3:30:16] **Toes use the same single-vertex method as the fingers:**
   - Merge to one vertex, extrude on Y, add Skin, then Subdivision Surface level 2. Ctrl+A sets thickness.
   - Move only in Object Mode.
   - **Stepped big toe:** add two loops, GG back, G Z down. Add a loop cut to sharpen the crease. **GG then C** extends the slide beyond its normal limit. Keep the toe "flat on the ground".
7. Alt+D the other toes. **S Y Y** scales on the local Y axis (once is global, twice is local). Size the toes from smallest outward. Fatten them with Ctrl+A. **Leave space between toes**; it is reduced after retopology.
8. Grab the foot to match the toes and push in the arch. Use Alt+B to isolate. Ctrl+A, Visual Geometry to Mesh. Check X symmetry; it works here.
9. Add creases with Crease Polish and keep the toes flat on the ground. "Zoom out once in a while."
10. Remesh the foot, smooth, keep the arch, Inflate the teardrop heel. Use Clay Strips with Ctrl to remove volume, and add volume, for the curvature and arch. Check the bottom view. Toe: remesh, Crease Polish the tip and joints, make it "a little bit more box like", Scrape the top.
11. [3:42:58] Join the toes and foot, then **remesh at "0.0 six" [likely 0.006]**. Blend with Clay Strips and smooth. Crease Polish the separation between toes and under the toes. Push the pinky toe in slightly.
12. [3:46:42] Toe spacing looks too wide now "so that we can easily topologize this". Clear the viewport mask and mirror to the other side.

### Body in Blender, [3:47:33]–[4:13:56]
- "This is where we want to rely heavily on our reference." Remesh each part, smooth, then join progressively.
- [3:48:04] **Upper legs:**
  - Remesh 0.05. "The mesh resolution is going to depend on the scale of your scene." Smooth.
  - Make the front of the thigh curved with Grab (the straight/curve rule) and define the hips.
- **Lower leg:** remesh and smooth. Its thickness comes from the reference: Inflate the calf and pull it out. Straight front, curved back. Make the two meshes flow into each other.
- **Knee:** indicate it with Crease Polish and Ctrl.
- [3:51:17] **Torso parts:** remesh and smooth, define the back separation with Crease Polish. "Make sure that these are not intersecting." Bring the waist in tightly per the reference. Mark the rib cage with Crease Polish, clean with Scrape, add volume. "Notice how I didn't add any details just yet."
- [3:54:14] Save Incremental and delete unused blockouts.
- **Arms:**
  - Remesh 0.03. Lengthen the biceps.
  - **Elbow:** Grab out the back, Crease Polish with Ctrl, Scrape to flatten.
  - Shoulders and neck: remesh and smooth so they merge into the body and arms. Mark a line at the back of the neck.
- [3:57:27] **Join the legs** and remesh at 0.04. "Make sure you're happy with the way your shapes looks before going forward." Blend the upper/lower leg transition with Clay Strips and smooth. The knees only get "slightly indicated" because the concept barely shows them. Re-apply straight vs curve.
- [4:00:10] Arch the back with Grab into a "nice S shape at the back".
- [4:00:42] **Join three torso objects** and remesh at 0.03. Smooth the transitions. Drag the buttocks down to overlap the legs and pull them up into a "peach shape". Make the S-shaped back again.
  - Side crease with Crease Polish, then the **Pinch** brush to sharpen it. Pull the shoulders out for a V shape.
  - Clay Strips plus smooth on the transitions. Mark the belly centre with Crease Polish and the belly button with the Draw brush. Adjust the rib cage, then the stomach crease.
- [4:05:04] **Chest:** use Clay Strips strokes "coming out from the shoulders… make a number six", then build up and smooth. Lower the rib cage. Set size to taste. Inflate, crease under the chest and lead the crease "going into the shoulders". Widen the hips.
- [4:07:49] **Join the hands to the arms**, remesh, smooth the wrist transitions. Do a light bicep/forearm crease ("I won't make it too intense"). Inflate the arm to match the reference.
- [4:10:09] **Join the arms to the shoulders**, remesh, blend with Clay Strips "so the shoulders is flowing nicely into the arms".
  - Gotcha: if colour patches appear you pressed a face set shortcut by accident. Fix with Face Sets, "Face Sets from Visible".
  - Refine the rib cage ("once you're progressing… you'll see things you can improve"). Make the back bigger with a big Grab brush ("big brush size… big change").
- [4:13:26] **Final proportion pass:** the head is too small, so scale it up; the feet are too small, so scale them up.
- Summary: "your observation is key".

---

## 2. Chapter 5: Clothes, accessories, hair. Workflow in order

### Theory, [4:15:04]–[4:24:27]
- [4:15:52] **Water analogy:** clothing "follows and conforms to the surface that it is placed on". The look and flow of clothing is "completely dependent on the structure of your character's body".
- [4:17:03] **Two forces cause every fold:**
  - **Tension** means the cloth is pulled from one, two or many points.
  - **Compression** means the cloth is pushed into itself or into another surface, so it "bunch[es] up" (for example sleeves).
  - Every fold is "a combination of both". Understanding this means you "stop placing random folds and start placing them with intention".
- **Seven fold types:** zigzag, spiral, pipe, drapery ("three pre"), half-lock, drop, inert ("in"). "You don't need to memorize them". Find where tension and compression happen instead.
  - Pipe folds: held from above, so straight folds.
  - Zigzag and spiral folds: heavy compression.
  - Drop folds: two tension points give straight folds, with gravity compression in between.
  - Half-lock folds: tension from the elbow, compression at the bend.
  - Chest pulling the shirt gives tension folds.
- He shares a PureRef file. Exercise: mark the tension and compression points on reference photos.
- [4:23:04] **Animation rule, shown on Blender Studio characters (Sprite Fright etc., "red rig"):**
  - Folds are "very subtle" because "this character is going to deform… we don't want the folds to be excessive".
  - Folds sit only "in some certain points so that when this character deforms, it still looks good".
  - **"When sculpting clothes for your own character, don't overdo the folds."**

### Shirt (cropped, short slanted sleeves, tucked in), [4:25:34]–[4:51:37]
1. Start with a Cube and use "very simple box modeling to block out the forms", then sculpt.
2. Shape the edges to the body. E Z extrudes the hem. Add a loop and scale it so the cloth follows the body.
3. [4:26:40] **Auto Mirror add-on** (Edit, Preferences, Get Extensions, "auto mirror"). It is in the N panel, Edit tab, and the defaults are fine. It adds a Mirror modifier and deletes half the geometry.
4. [4:27:31] Add loops for the sleeve faces.
   - Neck: **I (inset) with B (boundary)** so the inset clamps to the mirror seam, then delete those faces for the neck hole. Delete the bottom faces too.
   - Extrude the short slanted sleeves once. S Y, G Y, GG to fit the arm.
   - Move edges close to the body, front and back. Add loops and **Alt+S (shrink/fatten along normals)** "so that it's not intersecting with the body". Check the side profile with S Y.
5. [4:31:02] **Sculpt Mode, mainly Grab** to push and pull, with Shift to smooth.
   - Viewport shading Color set to **Object**, then a random colour per cloth object under Object Properties, Viewport Display, to tell the meshes apart.
   - If the cloth intersects the body, **Inflate it out**. "Some parts might still intersect. That's completely fine… we don't have enough geometry right now."
   - The shirt is tucked into the trousers, so keep it tight at the sides.
   - Long sleeve alternative: extrude to the wrist and add loops.
6. [4:33:45] Edit Mode, select all, right-click **Subdivide, Smoothness = 1**.
   - Grab and Inflate so the collar is round all around the neck.
   - Fix any opening by joining the vertices back together. Remove extra loops. Inset and delete the last row of faces.
   - Pull the cloth down onto the chest so it lies on the chest.
   - Use the **Relax Slide** brush with Shift to even out the topology, so geometry isn't "too bunched up together".
   - Check against the hand/arm. "Take your time at the blockout stage."
7. [4:37:57] **Apply the Mirror modifier.** Smooth the centre with X symmetry on, then **Symmetrize**. Fix centre vertices with **M, At Center**.
8. [4:39:17] **Add Multiresolution and Subdivide twice.**
   - Explanation: with a **Subdivision Surface** modifier you still sculpt only the base vertices. With **Multires** "you can sculpt on the subdivided pieces".
9. [4:40:54] **Folds:**
   - A tight shirt gives compression folds. "We don't want to overdo the folds… when this character deforms, the fold still looks nice."
   - **Turn X symmetry off** for folds, so they are asymmetrical.
   - Draw brush strokes lay in the folds, with a branch coming off a fold. Ctrl+Draw digs the valleys between folds, and connected folds go across the back.
   - **"Make sure you're actually using reference"** or the folds "look really bad".
   - Lightly smooth.
10. [4:43:16] **Stylised trick: sharpen the folds with Crease Polish and Ctrl** ("on stylized characters, something that makes folds look really good is when we actually sharpen the folds"). Crease the low points too.
    - **Avoid parallel, equal folds**: "try to get in curves and diagonals".
11. [4:45:31] **Armpit folds:** compression and tension from the shoulder. Draw them with X symmetry on, then turn it off and adjust each side. Keep them subtle and sharpen with Crease Polish. Pull the cloth closer to the body. On the sleeves, add a few Draw folds and crease them.
12. [4:47:52] **Shade Smooth.** Add one more Multires subdivide, turn X symmetry off, refine the folds with Crease Polish. Grab so the cloth sits on the body. Crease the armpit edges front and back.
13. [4:50:48] **Add a Solidify** modifier "so that the clothes has thickness". No number is given ("increase the thickness something like this"). **Solidify is not shown in Sculpt Mode while Multires is enabled**; that is normal.

### Trousers (tight, fitted to the knee, flared/full length), [4:51:37]–[5:16:39]
1. Add a Cube **overlapping the shirt**. Scale it on X and Y to the body. Use Auto Mirror. Add a middle loop for the crotch gap and loops for shape. Delete the top faces. Select the bottom faces (**/ local view** to check you didn't miss any) and extrude to the knee ("tight at the knee… funnels out at the bottom"). Delete the faces there.
2. [4:54:18] **LoopTools add-on.** Right-click, LoopTools, **Circle** rounds the squared leg opening. Scale it to the knee and add loop cuts.
3. Sculpt: smooth and follow the body. Set a dark object colour for visibility. Add loops. Use Grab, and **Inflate where the cloth intersects** ("at any point that intersects you can either use the grab brush or the inflate brush"). Keep the top **above the shirt** (the shirt is tucked in). Relax Slide.
4. [4:58:17] Extrude the bottom faces with E, S Z to the ankle. Gotcha: if the centre vertices merge, **temporarily turn off Clipping** on the Mirror modifier, pull them out, then turn it back on. Add **8 loop cuts**, Grab and Inflate so the cloth doesn't intersect the leg. Shade Smooth "early on".
5. [5:00:57] Subdivide. Move the centre vertices back to the middle (select, G X). Relax Slide. Raise the trousers and push the shirt up so they don't intersect: "we want the shirts and the trousers to work well together."
6. [5:03:13] Add Solidify (not applied). **Apply Mirror**, then **Multires, Subdivide twice**. Use X symmetry to smooth and Clay Strips to fill indents. **Push the body object in** so it fits the clothes.
7. [5:04:51] **Folds:**
   - Tension folds at the crotch/hip with the Draw brush. Subdivide once more and smooth.
   - Sharpen with Crease Polish and Ctrl ("on stylized, sharp crease looks really nice"). "Make sure not to overdo it."
8. [5:06:30] **Seams:** Draw Sharp brush lines around to the back, then the **Pinch** brush to tighten the crease ("looks sharper").
9. [5:07:59] **Patch/fly:** Clay Strips volume at the centre front with symmetry. Scrape to flatten, Crease Polish the sides and sharpen the edges.
10. [5:09:52] The lower leg is tight, so "no much folds there". Use a few straight vertical Crease Polish folds. "We are still keeping in mind that this clothes is going to deform."
11. [5:11:44] **Behind the knee:** Draw Z-shaped (zigzag) compression folds "where the knee is going to bend", then smooth and sharpen. A few light tension folds at the back. His question to himself: "when this starts to deform, will they look good?"
12. [5:14:17] **Waistband/belt line:** Draw Sharp crease around to the back, then Pinch.

### Pleated skirt, [5:16:56]–[5:24:08]
1. Start from a **Circle** ("way easier to start from a circle"), **vertices set to 33** (as transcribed). Use / local view and Edit Mode, top view (numpad 7).
2. Select all, **Select, Checker Deselect with Selected = 2**, then **Ctrl+I** to invert. Scale those in and rotate them, which zigzags the outline.
3. Select the longer edges, right-click **Subdivide**, then S / Alt+S the new vertices out. This gives the pleat profile.
4. E Z extrudes down and scales up (flare). Extrude the top edge with E Z, then **LoopTools Relax** (twice). E Z again and **LoopTools Circle** for a round waistband.
5. Bad shading: select all and **Shift+N** (recalculate normals).
6. Add **Subdivision Surface level 2** plus one more loop.
7. Place it on the body. Scale S and Y front/back and shorten it.
8. Sculpt with X symmetry even though the skirt is not perfectly symmetrical. **The skirt overlaps the shirt.** Push the shirt in closer to the body. Make sure the skirt doesn't intersect the body. Grab the hem into a curve.
9. Copy the colour (hover Ctrl+C, Ctrl+V). Add **Solidify** with thickness raised, Shade Smooth. Add a loop so the shading isn't weird. Lower the back hem.
10. Optionally add Multires to sculpt details; not needed here.

### Boots (high heel), [5:24:08]–[5:46:58]
1. [5:24:23] **Adapt the foot to the shoe first:**
   - High heel, so in Edit Mode with X-ray select the front vertices and rotate them down. Ctrl+right-drag lasso-selects.
   - Fix the result in sculpt: remesh, Clay Strips, smooth, Scrape the underside. Smoothing is hard because there is a lot of geometry.
   - It would have been easier to sculpt the foot in heel pose from the start: "for your next character… scul the feet with the heel pose."
   - Remesh at **"0 73" [likely 0.0073]**.
   - **Toes fused by the remesh:** Ctrl+Z, then **Inflate with Ctrl (deflate) to make gaps between the toes**, then remesh again.
2. [5:31:30] **Boot box model** ("a general guideline for modeling a shoe"):
   - A Cube fitted to the leg. Extrude down the shin, then extrude the foot forward following the foot.
   - The sole is flattened with **S Z 0**.
   - Add a centre loop cut, then Auto Mirror. Add loops, GG to slide, and round off with the reference. "Don't worry about it clipping through the feet for now."
   - Delete the top faces (the boot opening), then LoopTools Relax.
   - Grab-sculpt. Scale the bottom faces in on X and Y. Isolate. Set a dark colour.
3. [5:36:13] **Apply Mirror, then add a new Mirror modifier with the Mirror Object = the head (world-centre object)**, which puts the boot on the other leg. From here, sculpt without X symmetry.
4. **Heel:** S Z 0 flattens the sole faces. Extrude the heel down, S Y to narrow it. Use S Z 0 to keep the faces coplanar. Round with S X / G Y. Narrow the heel from the back.
5. Sculpt without symmetry: pull the toe forward and push the sides. Hide the foot. Inflate the bulky areas. Check the back and side views. Scale the toe box on X.
6. [5:41:04] Shade Smooth, add **Solidify** (thickness raised), S Z 0 again. Add **Multires** (the Mirror stays unapplied because it is mirroring to the other side), subdivide, then subdivide once more.
7. **Sole separation line:** Draw Sharp brush all around. Tip: turn on **Stroke, Stabilize Stroke** to avoid jagged lines. Pinch the line.
8. **Line Project** slices the sole sharp; Crease Polish the edge.
9. Alternative: use this mesh as a base and box-model the shoe. He prefers sculpting.
10. [5:44:51] **Boot folds:** Draw folds (ankle wrinkles, "diamonds" at the top), smooth, Crease Polish with Ctrl to define them.

### Hair (placeholder, to be replaced by real hair at the grooming stage), [5:46:58]–[6:00:55]
1. [5:47:15] On the head in Sculpt Mode, from the side view, **Lasso Mask** the hair area (scalp cap). Then **Mask, Mask Extract** with defaults, **Offset = 0**, and raise the **Thickness**. This gives a separate mesh with a Solidify.
2. [5:48:40] **Break the hairstyle into simple big volumes:** a top volume, two side volumes and a back volume. Another style might be left part, right part and back. "Break the hair into really simple parts."
3. Sculpt the extracted plane: bring the sides in, smooth the edges. **Apply Solidify**, **remesh 0.015**, Scrape the planes over the head, Grab down, set the colour, smooth.
4. [5:51:23] **Flow direction:** the hair flows and "bunch[es] up at a certain point". Use **Clay Strips** strokes toward that convergence point. Add volume where the hair hangs.
5. [5:53:48] **Hanging locks with a skin chain:**
   - **Shift+A, Mesh, Single Vert** (Extra Objects add-on) or a merged cube.
   - Extrude on X, add Skin plus Subdivision Surface level 2. **Ctrl+A** scales the radius per vertex (thinner toward the tip).
   - Right-click **Smooth Vertices**.
   - Add a Mirror modifier for the other side. Paste the colour. Adjust with **Proportional Editing**.
6. [5:57:06] **Back piece:**
   - Shift+D, then Shift+S "Selection to Cursor" (cursor at world origin), **P, Separate by Selection**, remove the mirror, extrude.
   - Gotcha: "no valid root vertex" means select a vertex and **Mark Root** (Skin).
   - Ctrl+A then X scales the skin radius on X only.
   - Raise the subsurf, then Ctrl+A, Visual Geometry to Mesh, remesh, smooth.
   - Clay Strips strand direction (X symmetry OK). Grab.
7. [6:00:06] Proportion fixes against the concept: thicker thighs (Inflate) and a larger head.
8. Summary: "clothes follows the form of the body. Folds come from two forces… tension and compression… focus on the forces and not memorization." Next chapter is retopology.

---

## 3. Technique catalogue

**Modifiers and settings (numbers as given):**
- Mirror. Clipping can be toggled off temporarily to un-merge centre vertices. Mirror Object can be another object, such as the head at world centre, to mirror a boot to the other leg.
- Subdivision Surface levels 1–2. Applied for more resolution.
- Skin with Subdivision Surface for fingers, toes and hair locks:
  - Ctrl+A sets the skin radius, Ctrl+A then X scales one axis.
  - Mark Root fixes "no valid root vertex".
  - The chain starts from one vertex kept at the origin.
- Multiresolution with 2 subdivisions, plus more as needed. Used on all clothes before folds.
- Solidify gives clothes and the extracted hair thickness. It stays unapplied on clothes (and is hidden in sculpt with Multires). It is applied for the hair before remeshing.
- Ctrl+A, "Visual Geometry to Mesh" applies all modifiers, including on linked-data duplicates.

**Remesh voxel sizes:**

| Part | Voxel size |
|---|---|
| Palm | 0.025 |
| Fingers and thumb | 0.01 |
| Joined hand | 0.01 |
| Joined foot | "0.0 six" [likely 0.006] |
| Thighs | 0.05 |
| Joined legs | 0.04 |
| Joined torso | 0.03 |
| Arms | 0.03 |
| High-heel foot | "0 73" [likely 0.0073] |
| Hair | 0.015 |

He adds that the size "is going to depend on the scale of your scene". Too low a resolution makes the mesh web between the fingers.

**Edit-mode tools:**
- Subdivide with Smoothness 1.
- Checker Deselect with Selected = 2, then Ctrl+I.
- Inset (I) with B for boundary.
- LoopTools: Circle and Relax.
- Shift+N recalculates normals.
- M, At Center merges vertices.
- GG edge slide; GG then C extends the slide.
- Alt+S scales along normals.
- S Z 0 flattens a sole.
- S Y Y scales on the local axis.
- Ctrl+X dissolves.
- Smooth Vertices.
- Proportional Editing.
- P, Separate by Selection.
- Shift+S, Selection to Cursor.
- Symmetrize.

**Sculpt brushes and their roles:**

| Brush | Used for |
|---|---|
| Grab | Primary shaping of the blockout and clothes |
| Smooth (Shift) | Gentle passes after every remesh; "we don't want to get rid of our main shape" |
| Clay Strips | Adding volume; blending joined parts with strokes across the seam; Ctrl to remove volume; hair direction |
| Crease Polish | Joints, creases, knuckles, rib cage, sharpening folds (often with Ctrl) |
| Draw | Laying in folds; Ctrl to dig; belly button |
| Draw Sharp | Seams, waistband, sole line |
| Pinch | Tightening creases and seams |
| Scrape | Flattening planes (nail bed, palm top, sides of the trousers, hair planes) |
| Inflate | Pushing cloth out of the body; teardrop heel; calf; Ctrl to deflate and separate toes |
| Relax Slide (Shift) | Evening out the topology of clothes |
| Line Project | Flat cuts (foot, sole) |
| Lasso Mask | Masking; turn off "Front Faces Only" to mask through the mesh |

**Masks, viewport and snapping:**
- Alt+M clears the mask. Mask, Mask Extract with Offset 0 and a thickness.
- Face Sets from Visible clears stray face sets.
- Stabilize Stroke avoids jagged lines.
- Pivot can be set to Individual Origins or Median Point.
- Alt+B is the viewport clipping region. / is local view. Alt+Z is X-ray.
- Turn off the Origins overlay to see a single vertex.
- Viewport shading Color = Object, with a colour per cloth object.
- Quick Favorites (Q).
- File, Save Incremental.

**Add-ons:** Screencast Keys, Auto Mirror, LoopTools, Extra Objects (Single Vert).

**Duplication:** Alt+D (linked data) so all fingers or toes share one edit. Shift+D for an independent variant such as the thumb.

**Anatomy and proportion rules:**
- Arms are interlocked chains.
- Legs follow straight vs curve: the thigh has a curved front and straight back; the shin has a straight front and curved back.
- Angry-face rule: the inner ankle is higher than the outer ankle, and the inner calf high point is higher.
- Palm is a rectangle plus a thumb wedge and is curved.
- Knuckles sit on a curve, and each joint row is steeper.
- Finger joints are at 1/2 and 3/4 from knuckle to tip. Joint angles go back, up-forward, forward.
- Finger lengths: middle longest, then index/ring, then pinky.
- Foot is a right-angle triangle from the side, a rectangle from the bottom, with an arch, stepped toes and a teardrop heel.
- Back has an S-curve. Buttocks are peach-shaped and overlap the legs. Shoulders flare into a V.
- Chest is built with a "number six" stroke from the shoulder, with the crease under it leading into the shoulder.
- Knees are only indicated if the concept barely shows them.
- Final pass checks head and feet size against the concept; both were scaled up.

**Stylisation principles:**
- Observation and reference first.
- Rhythm and balance.
- Clean silhouette.
- Subtle joint creases ("you don't want to overdo this").
- Sharp creases on folds read as stylised.
- Few, non-parallel folds, using curves and diagonals.
- Break the hair into a few large volumes with a flow toward convergence points.

**Checks he does:**
- Silhouette in a side viewport.
- Rotate around the model and check all angles.
- Check front, side and bottom views (feet, boots).
- Make sure no cloth intersects the body.
- The cloth stack must work together (shirt tucked into trousers, skirt over shirt).
- Zoom out periodically.
- Compare with the concept and the reference.
- "Be happy with the shapes before joining/remeshing".
- Save incremental before destructive steps.
- For every fold, ask: will it look good when the character deforms?

**Mistakes he warns about:**
- Memorising anatomy instead of observing.
- Ankles level with each other.
- Flat palm, straight knuckle line, straight fingers.
- Isosceles foot.
- Remesh resolution too low (mesh webs between the fingers).
- Joining before you are happy with the parts.
- Moving the skin root vertex in Edit Mode (it breaks the pivot).
- Lasso Mask with Front Faces Only on.
- Over-strong joint creases.
- Folds without reference.
- Too many folds on an animated character.
- Parallel, equal folds.
- Symmetric folds (turn symmetry off).
- Merged centre vertices on the mirror.
- Toes fused by remesh.
- Jagged seam strokes.
- Toe spacing kept wide for retopology; it is not final.

**Not covered in these chapters:** cloth simulation, UVs/textures, retopology (next chapter) and rigging. Clothing thickness is never given as a number. There are no collision modifiers: clipping is fixed by hand with Inflate/Grab or by pushing the body in.

---

## 4. Applicable to a scripted bpy pipeline

### Can become rules or code
1. **Clothing as offset shells with Solidify.** Build a garment as a separate mesh close to the body, then add `SOLIDIFY` for thickness. In code, keep a per-garment thickness constant scaled to character height. He gives no number, so we must choose and test one.
   - Optionally derive the garment from the body with Mask Extract. `bpy.ops.sculpt` is awkward to script; for a scripted equivalent, duplicate the body faces by vertex group, then Displace or Shrinkwrap with a positive offset, then Solidify.
2. **Clipping avoidance replaces his manual Inflate/Grab.**
   - Add `SHRINKWRAP` (mode `OUTSIDE_SURFACE` / `ABOVE_SURFACE`, offset ≈ cloth gap) targeting the body.
   - Or run a script that measures garment-to-body distance with `BVHTree` and pushes vertices out along the normal.
   - Layer order as data: the shirt is inside the trousers, the skirt is over the shirt, and each outer layer gets a larger offset.
   - His other trick was pushing the body in under tight clothes. Equivalent: mask or delete hidden body faces, or shrink them under garments with a vertex-group Displace.
3. **Garments from primitives, as he builds them:**
   - Box-model the shirt, trousers and boots from a cube with a Mirror modifier (`use_clip=True`).
   - Leg openings: LoopTools Circle (`bpy.ops.mesh.looptools_circle` if the add-on is enabled) or our own circularise function.
   - **Pleated skirt is fully proceduralisable:**
     - Make a circle of N vertices and alternate radius in/out (his checker-deselect step).
     - Subdivide the long edges and push them out (pleat depth).
     - Extrude down with a larger radius (flare), add a round waistband loop.
     - Add Subdivision Surface level 2 and Solidify.
4. **Skin-modifier chains for fingers, toes and hair locks.**
   - Make a polyline of vertices with a per-vertex `skin_vertices[0].data[i].radius` (tapered) and set `use_root` on the first vertex (his "Mark Root" gotcha).
   - Add `SKIN` and `SUBSURF` level 1–2, then `bpy.ops.object.convert(target='MESH')`, which is equivalent to "Visual Geometry to Mesh".
   - This is the best scripted accessory method he shows. It suits hair strands, braids, straps and cords, and also ponytail placeholders.
   - Curves with bevel are an alternative he doesn't use.
5. **Proportion checks become automated asserts on MPFB bodies:**
   - Finger joint ratios: 1/2 and 3/4 from knuckle to tip.
   - Inner ankle higher than outer ankle.
   - Knuckle line curved; finger order middle > index ≈ ring > pinky.
   - Head and feet not undersized (his final fix). We can check bone and landmark positions for these.
6. **Fold policy for animated characters:**
   - Few, subtle folds only where tension or compression happens: armpits, elbow inside, behind the knee (zigzag), crotch/hip tension, waistband.
   - Avoid parallel repeats.
   - For scripted cloth, keep baked fold detail minimal; let motion or a light cloth sim or corrective shape keys handle the rest. For toon/EEVEE, a few sharp creases read better than many soft ones.
   - Fold placement can be data per garment type (zones keyed to bones).
7. **Seams and soles:** seams follow edge loops. A scripted seam could be a selected loop, bevel or inset, plus a slight inward Displace. Or use a normal/bump texture line, which is cheaper. The boot sole line comes from S Z 0 (flatten the sole faces to the floor plane) and a separate extruded heel block. Both can be scripted.
8. **Hair placeholder as data:**
   - Big volumes (top/sides/back) from an extracted scalp cap with Solidify, plus skin-chain locks.
   - A scripted version is a scalp vertex-group duplicate, then Solidify, then Displace, plus skin chains mirrored with a Mirror modifier whose Mirror Object is the head.
9. **Workflow conventions:**
   - Viewport colour per cloth object.
   - Save incremental.
   - Linked duplicates (`obj.data` shared) for repeated parts until they need to diverge.
   - Remesh voxel size relative to scene scale; his numbers suggest about 0.01 for fingers and about 0.03–0.05 for limbs at his scale. `obj.data.remesh_voxel_size` plus `bpy.ops.object.voxel_remesh()`.
10. **Mirror Object trick:** put one boot on the other leg by mirroring across a centre object. This is useful for scripted accessories, mirroring across the body's armature root.

### Inherently manual or artistic (not worth scripting)
- All brush sculpting: Crease Polish joints, Clay Strips blending, sharpening folds by eye, the "number six" chest, the S-shaped back.
- Observing and translating from references, and judging rhythm, balance and silhouette.
- Hand-placed asymmetric folds and their branching and connection.
- Hair flow direction strokes.
- Final proportion tuning against a concept.
- For our MPFB-based pipeline, the body sculpt chapter mainly serves as rules to validate or tweak MPFB proportions. The clothing chapter gives the garment construction method (shell, Solidify, few sharp folds, no clipping, correct layering), which we can turn into code.
