# Notes: Kenny Praise "Stylized 3D Characters" masterclass, files 00 + 01

**Coverage:** I read both files from start to end, every line.
- `00_intro_concept_blockout.txt`: 354 lines, 90,633 chars, [0:00] to [1:35:52]. All of it read.
- `01_face.txt`: 191 lines, 50,347 chars, [1:36:09] to [2:27:47]. All of it read.

**About the transcript:** it is auto-generated, so some tool names come out garbled. My readings:
- "clear shield / clay shoot / clear street brush" = Clay Strips
- "script brush / screw brush", used to "pl out" = Scrape brush, used to plane out
- "in place brush" = Inflate
- "max / maxed" = mask
- "P right / key right / quill right / Q right / key favorite" = Quick Favorites (Q)
- "X3" = X-ray
- "eximemetry / Xmmetry" = X symmetry
- "no shoes" = nostrils
- "escort / scurve / scope" = S-curve
- "cob / cos / corves" = curves
- "lake" = leg, "skits" = skirt
- "PRF / Pure F / PURF" = PureRef
- "weather expense mode" = vertex paint mode

He says "Ctrl G to join". Blender's join is Ctrl J, so this is probably a mishearing; it is kept as spoken below. He also says "Ctrl X" fills the vertex-paint colour. That is quoted as spoken and not checked here.

---

## 0. Intro (file 00, [0:00] to [9:24])

The course has 8 sessions and 13 chapters:
1. Concept and references
2. Sculpting: blockout, face/head, body, clothes/accessories
3. Retopology: fundamentals plus face; body, including hands, feet, mouth interior, teeth and tongue; clothes
4. UV unwrapping
5. Hair grooming. Sculpted hair is replaced with strand hair made with "Blender's geometry node hair system".
6. Shading and texturing: eye shader, hair shader, painted textures, normal maps, "additional maps"
7. Rigging with Rigify, then posing
8. Lighting and presentation: turntable/animation renders and final renders

What he says before starting:
- Prerequisites:
  - The Blender Guru donut tutorial.
  - Rate your own sculpting from 1 to 10. Below 5, do his sculpting masterclass first.
- A graphics tablet is "very nice to have" but not required. He uses an XP-Pen Artist Pro 14.
- Don't skip the "fundamentals" segment at the start of each chapter. The practical part builds on it.
- Realistic timeline: one chapter per week, so about 3 months.
- The rest of the intro is promotion (academy, reviews).

## 1. Chapter 1: Choosing a concept and references (file 00, [9:24] to [21:23])

Steps in order:
1. **[10:11] Why the concept matters.** "A good 3D character is going to start with a good concept". The concept "guide[s] every decision" later on. Skipping it means "weak results" and "confusion" in Blender.
2. **[11:31] What a good concept is.** "Anything that you find beautiful or appealing", something that makes you excited to build it. "Don't overthink it."
3. **[12:19] What to avoid while learning.** Avoid "overly complex character designs". Highly detailed concepts "slow down the learning". Pick simpler concepts.
4. **[13:22] Where to find concepts.** Instagram, ArtStation, Pinterest. He has a Pinterest board with over 60 beginner-friendly concepts. If you use an artist's work, "make sure to take their permission".
5. **[14:43] Gathering references.**
   - "References should support your chosen concept". You are not "just gathering more beautiful images".
   - Gather by category: hair, clothing, material, style.
   - Purpose: "Strong references are going to help you stay consistent".
   - His example concept is by Jennifer Park, used with permission.
   - His reference set has a separate group for each of the following:
     - **Face.** The overall style, such as big eyes. Since the character is Asian, he adds 3 photo references used as "proportion guides".
     - **Boots.** One main reference showing exactly what he will model, plus 3 for folds. The concept itself was unclear on the boots.
     - **Skirt.** The concept was unclear about how it works.
     - **Hair.** Shows strand direction and where sections separate.
     - **Body.** "Simplistic shapes".
   - A second example character has references for face (sculpt style), torso, dress ruffles, dress **material** ("so that once we start shading we can cross check"), heels, hair and jewelry.
6. **[19:15] PureRef.** A free reference-board app; you can type a custom amount of 0. In Blender he keeps it "pinned to always on top".
7. **[20:02] Checkpoint.** Lock the concept, then gather relevant references.

## 2. Chapter 2: Blockout (file 00, [21:23] to [1:35:52])

### Fundamentals (slides)

- **[22:14] What a blockout is.** "Using very simple shapes to build the foundation of your character". At this stage you "ignore all the details and only focus on the basic forms, the proportions, and the structure". No clothes and no fine detail.
- **[23:19] Know the proportions first.** Stylised characters "often break" human proportions, so the chosen concept is "your main guide". Measure and compare against it in Blender.
  - Example: on one character the head height is about the same as the body height, and also about the same as the leg length.
  - Identify these ratios before you start.
- **[24:56] Why block out.**
  - It gives a strong foundation; "everything else ... will be built on this foundation. So it needs to feel correct".
  - Demo: select the parts, Ctrl G (as spoken) to join, remesh, and "just with a few brush strokes" it already looks good.
  - Once the proportions are fixed, sculpting is "so much easier and so much more controlled".
- **[26:36] How to block out.**
  1. **Follow the character's shape language.** Characters are "round, angular, boxy". The blockout should reflect the concept's shapes, and you keep them "throughout the whole sculpting process". His examples:
     - A "triangulated box" character.
     - A boxy character, boxy in the face and the legs.
     - An "elongated box" character.
  2. **Break the character into parts**: head, torso, arms, legs, each a separate object. This keeps it "clearer and ... organized".
  3. **Use very simple primitives at low resolution** "so that we can avoid details". Everything is a modified **Round Cube**.
  4. **Straight versus curves.** "Mixing straight and curved forms makes the character look more appealing and more dynamic" and avoids "stiff or boring shapes".
     - Legs: curved on one side, straight on the other. Later he specifies curve at the front and straight at the back of the upper leg.
     - Also: an "S shape running through the whole character" in side view.
  5. **Check the silhouette often.**
     - "Your character should be readable from a distance. A strong silhouette is a sign of a good blockout."
     - How: Viewport Shading, Lighting = Flat, Color = **Custom**, set to **black** (the default is white).
     - In Blender 5.0, "make sure specular lighting is turned off".
     - He keeps a second viewport split permanently on the silhouette view.

### Blender setup ([31:17] onward, Blender 5.0)

- **Delete the default scene**: select all, X.
- **Round Cube**:
  - Edit, Preferences, Get Extensions, search **"Extra Mesh Objects"**, install. This adds Add > Mesh > Round Cube.
  - Right-click it, Add to Quick Favorites (Q menu).
  - He also adds these to Quick Favorites as the course goes on:
    - Line Project brush
    - Lasso Mask
    - Mirror modifier, in both the object-mode and edit-mode Q menus
- **Workspace**: Sculpting workspace, sculpt mode on the round cube.
- **Focal length**: N panel, View, **Focal Length = 150**, "that way your sculpt is not going to look distorted".
- **Viewport layout**:
  - Split the viewport. The second, small viewport is for the "overall progression" preview and the silhouette check. In it, T hides the toolbar and gizmos and overlays are toggled off.
  - A third area holds PureRef with the references, always on top.
- **Shortcut display**: screencast keys are on, to show shortcuts.
- **Z pie menu**: Preferences, Keymap, enable **"Extra Shading Pie Menu Items"**. In the Z pie, swipe up toggles overlays and swipe down toggles X-ray.
- **Alt Z**: toggles X-ray.

### Blockout steps (in order)

1. **[37:23] Brush and symmetry.** The **Grab brush (G)** is "our best friend" for the blockout. Turn on **X symmetry**.
2. **[37:40] Head** (the first round cube).
   - Grab it down into "a nice egg shape".
   - Side view (numpad 3): pull forward for the jaw.
   - Front view (the −Y gizmo): use the **Line Project brush** to slice the sides of the head flat ("we don't want that to be round"). You can repeat the slice.
   - **Crease Polish (Shift C)** marks the jaw/cranium separation. Brushes can be found through the brush search box.
   - Pull the cranium up with Grab.
   - **Shift** gives Smooth.
   - Pull the back of the head back: "we don't want the back of the head to be completely round".
   - Pull the jaw forward from the side.
   - **Scrape (Shift T)** cleans the side of the head flat.
3. **[40:55] Neck** (a new round cube from Q).
   - **Rule: "move these objects only in edit mode"**. This keeps the object origin so that "the symmetry inside of sculpt mode is going to work correctly". "Don't transform the object in object mode."
   - In edit mode: scale down, then with X-ray on select the bottom half and extrude down.
   - "The neck actually rotates or tilts backward". Don't leave it vertical.
   - To get sculptable geometry, add loop cuts: **Ctrl R**, type 6, Enter, then Esc to keep them in place.
   - In sculpt mode with X symmetry:
     - Pull the front out to merge with the chest.
     - Pull the back out to merge with the back.
     - From the bottom view, pull the sides out toward the shoulders.
   - Make it "flow nicely into the head".
   - Slice it with Line Project.
4. **[45:18] Head again.** Crease the jaw/cranium separation up to where "the ear is going to sit", then smooth.
5. **[45:50] Ears** (a round cube).
   - Placement, done in edit mode:
     - Scale it down and put it at the side of the face.
     - In side view, place it "on that separation within the jaw and the cranium".
   - Shape it with Line Project. **F** flips which side gets cut; the greyed side is the side that is cut.
   - Mirror it with **Symmetrize**: Symmetry dropdown, direction **+X to −X**. He explains how to check the axes with the gizmo.
   - Then Grab with X symmetry.
   - "The ear doesn't usually face front". Rotate it in edit mode.
   - After adding parts, go back and adjust the head. "Make sure you're happy with this before actually moving forward".
6. **[49:40] Torso** in 3 parts: rib cage/upper torso, the middle, and the pelvis/hips.
   - "Always make sure that you have an eye on your references".
   - Upper torso:
     - In edit mode: S Y to scale, then rotate it to follow the **S-curve** through the whole body.
     - In sculpt mode: pull it into the neck, pull out the shoulders, pull it down for the rib cage.
     - Make the back not rounded, so it looks "more natural".
   - Middle part:
     - The parts must flow into each other: "avoid stacking ... make sure that these are flowing nicely".
     - Line Project the bottom; F flips the cut side.
   - Pelvis:
     - **Alt Q** switches the sculpted object.
     - If the S-curve is lost, select all the torso parts, go into edit mode, and rotate them together.
     - Pull down and out for the hips.
     - Line Project where the legs come out.
     - Crease Polish the back separation and pull out the back.
     - In side view, the parts were "kind of floating on each other". Pull them together and keep a nice arc at the back.
   - Compare with the reference: his body was too thin. Select all, then in edit mode S X and S Y to widen it.
7. **[58:58] Upper leg** (a round cube).
   - In edit mode: scale, then S Z to make it long.
   - Mirror it with a **Mirror modifier**. If the object was moved in object mode, the mirror is wrong; fix it with **Ctrl A, All Transforms**.
   - Flow it into the torso and pull out the hips.
   - Line Project, then form the knee with Grab.
   - In side view, it was going "out of our S-curve". Rotate it backward in edit mode.
   - **Upper leg: "curve at the front ... straight at the back"**.
   - The back/buttock part must overlap the legs.
   - Widen the hips with S X.
8. **[1:02:48] Lower leg** (a round cube with a Mirror modifier from Q).
   - Make the bottom narrower and Line Project the bottom.
   - **The "angry face" rule for lower legs.** Draw an angry face on the lower legs. The eyes and mouth lines show the calf contours: the inner side bulges higher and the outer side lower. The bottom of the face is the ankle: "the [inner] ankle is going to be higher ... this other part of the ankle is going to be lower". The proper explanation is promised for a later chapter.
   - In side view it was too thick; thin it and apply straight versus curve.
   - Check that the S-curve runs through the whole character.
   - Refine the hips and the knee formed by the upper leg, with each part flowing into the next from front and side.
9. **[1:08:21] Foot** (a round cube with Mirror).
   - Bottom view (−Z gizmo): "think of it as a rectangular shape".
   - Line Project, then Grab it up to merge with the lower leg.
   - **Lasso Mask** in side view protects the sole while pulling up, so the bottom is not affected. **Alt M** clears the mask.
   - **Foot shape rule:**
     - Front view: a "right angle triangle".
     - Side view: a triangle, which makes the "character feel much more balanced".
   - Round the heel, smooth, and from the bottom pull in a bit on each side.
   - Check "from all angles possible".
   - Adjust the lower leg so it flows into the foot.
   - The legs were too long compared with the reference. Select them and scale in edit mode.
10. **[1:15:06] Arms.**
    - Slice the arm area of the upper torso with Line Project.
    - **Viewport artefacts.** Because the scene is not at real-world scale, set N panel, View, **Clip Start = 0.1**, in both viewports. It will be put into "real world scale" once sculpting is done.
    - Upper arm (a round cube):
      - Like the neck: X-ray, select the bottom half, extrude (E), rotate.
      - **Neutral pose for rigging**: an **A-pose**, with "hands not too close to the character", otherwise "it might affect our rigging".
      - Line it up with the shoulder and add a Mirror modifier.
    - Lower arm:
      - Shift D to duplicate it. He moved it in object mode, so the mirror broke; Ctrl A, All Transforms fixes it.
      - In edit mode: scale half of it with S, then S Y.
      - **Give the lower arm a slight bend** (A to select all, R Z): "that way once we start rigging Blender knows how to bend the arm".
      - Add loop cuts and scale them to get the reference's curve of the forearm.
      - Add 3 loop cuts in each of 3 places so it can be sculpted.
    - On the upper arm: Ctrl R with 8 cuts, then Grab out the bicep.
    - "The bicep end[s] in a V shape" into the lower arm.
    - "Don't add details at this stage".
    - The arms were too big. Scale them down in edit mode, make the forearm longer, add a loop cut.
11. **[1:24:27] Shoulders** (a round cube with Mirror from the edit-mode Q menu).
    - Pull it out and into the upper arm.
    - "Since this is a female character, we don't want the shoulders to be too massive".
    - Flow it into the back and the torso. It must **overlap** the upper arm and be "pulled into the chest".
    - Use Scrape to flatten the rounded front.
    - Add Crease Polish lines on the back.
12. **[1:28:01] Hands** (a placeholder, since a later chapter covers hands).
    - A round cube; Line Project the top and bottom.
    - A simple rectangle for the palm, shaped with Grab.
    - **Inflate (I)** puffs out both sides of the palm.
    - Grab out an indication of the thumb.
    - Flow it into the forearm and add Mirror.
    - Check from all angles.
13. **[1:30:58] Proportion pass against the reference.**
    - **Common mistake:** when you multi-select and enter edit mode, make sure the active object (the yellow outline) is one of the intended parts. Otherwise an unwanted object joins edit mode.
    - Scale the legs, widen them on X, refine the torso and shoulders.
    - **Scale the head up "to start to match the proportions"**.
    - Move the shoulders inward and shorten the forearm.
14. **[1:33:56] Take a break and come back.** "Take a break right now and come back in the next 30 minutes and you definitely see some things that you want to change". Lock in the blockout before moving on.
15. **[1:34:28] Save the file** as `blockout.blend`. He admits "I should have mentioned that earlier".

## 3. Chapter 3: Face and head (file 01, [1:36:09] to [2:27:47])

### Fundamentals: face proportions (slides, [1:37:11])

1. **Eye line**
   - The eye line is "halfway between the top of the head and the bottom of the jaw".
   - It is always the first landmark ("the first place I like to start"). It is "a foundation for placing all facial features".
2. **Brow line and bottom of the nose**
   - Choose an arbitrary hairline. Split hairline-to-jaw-bottom into **3 equal thirds**.
   - The first division is the brow line; the second is the bottom of the nose.
3. **The ear and the back of the head**
   - The ear sits in the band between the brow line and the bottom of the nose.
   - Projected to the back of the head: at the brow line, the back of the head "starts to change direction and merge nicely with the neck".
   - "This might be different based on your own character but for most generic cases" it holds.
4. **Side-profile depth** ("most beginners ... make it flat")
   - Outer corner of the eye to the front edge of the eye = 1 unit.
   - Front edge of the eye to the nose bridge = 1 unit.
   - Bridge to the tip of the nose = 1 unit.
   - Keeping these "the face is not going to look flat".
5. **Mouth**
   - Halve bottom-of-nose to bottom-of-jaw. That midpoint is the **bottom of the lower lip**.
6. **Eye spacing**
   - One eye width between the eyes, and one eye width from each eye's outer corner to the side of the head. That gives 5 eye widths across.
   - For stylised characters "it might be a little bit different".
7. **Mouth width**
   - "The corners of the mouth should not go past the midpoint of the eyes", that is, vertical lines dropped from the iris centres.

### Fundamentals: forms

- **[1:42:53] The head is two primary forms.**
  - The cranium, plus the jaw as "a wedge attached to the cranium". This holds "for any head size or any head shape".
- **The planes he sculpts after that:**
  - Forehead
  - Temples (both sides)
  - Eye line and brow line
  - Side of the face
  - Chin
  - "I don't consider the nose as a plane" because noses vary too much; the nose is added on afterwards.
  - The planes "guide the facial placement" and give clarity.
- **[1:44:32] Eyes**
  - "The iris sits inside of sockets". The eyelids don't sit on a flat surface.
  - If you sculpt the eye line and brow line properly, the eye won't end up on a flat surface.
- **Eyelids**
  - They "wrap around the eyeball. The eyelids are not flat."
  - **Three edges to get right:**
    1. The contact edge with the eyeball.
    2. The eyelid fold.
    3. The edge that transitions into the face.
  - In side section, the lid edges radiate from the eyeball's centre, for the upper and lower lids alike.
- **[1:46:44] Nose**
  - "Simplify the nose into a rounded triangular block". Details come after the base form. "Don't over complicate the nose."
  - References are "really important" for believable nose shapes.
- **[1:47:15] Mouth**
  - "Think of the forms of the mouth as three-dimensional. The lips wrap around the teeth."
  - "Bulk up the area where the mouth is going to be" first, then the planes, then details, then refinement. He cites a reference by "Glu".
- **[1:48:05] Ear**
  - Placement: between the brow line and the bottom of the nose.
  - Shape: "a wedge attached to the head" in both front and top views, a triangular wedge.
  - Details: "a question mark and a Y shape". The question mark is the rim (helix); the Y is the inner forms (antihelix).
  - Ears vary a lot, so always use reference.

### Sculpting steps (in Blender, [1:49:25] onward)

Layout: the same 3 areas as before (references, top comparison viewport, main viewport).

1. **[1:49:57] Add resolution to the head blockout.**
   - Voxel remesh size **0.04 to 0.05**, then **Ctrl R** to remesh.
   - Smooth everything with Shift.
   - **/ (slash)** for Local View, to isolate the head.
2. **[1:51:01] Separation.** Crease Polish deepens the jaw/cranium separation.
3. **[1:51:32] Eye line**
   - Measure top of head to bottom of jaw and take the halfway point.
   - Mark it with Crease Polish, holding Ctrl to dig in.
   - Don't take it all the way to the back.
   - Grab the centre inward to "make some space for the nose", leaving the eyes recessed to each side.
4. **[1:52:37] Brow line**
   - Smoothing above the eye line starts to form the brow ridge. Also smooth around the face.
   - Verify the brow height with the thirds measurement (hairline to jaw), then mark it with Crease Polish (Ctrl).
5. **[1:53:57] Temples.** Scrape flattens the side of the head ("plane out"). Smooth it flat without destroying the eye line; if you damage it, re-crease it.
6. **[1:54:32] Side of the face.** Scrape again.
7. **Chin.** Crease Polish marks it "very simply".
8. **[1:55:04] Compare with the reference.**
   - Hers had wider cheeks; pull them out with Grab.
   - Pull the brow in from the side.
   - "Always taking a look at the reference".
   - He simplifies the planes: "you don't really need to go very detailed".
9. **[1:55:53] Nose as a separate round cube.**
   - In object mode, add it from Q. In edit mode from the side view: scale, place, rotate.
   - In sculpt mode with X symmetry:
     - Grab the root into the face.
     - Make it triangular from the bottom view.
     - Pull it down to suit the character.
     - Mark the nostrils with the Draw brush (spoken as "throw brush") holding Ctrl, then push with Grab.
   - **Merge it**: select nose, then head, then Ctrl G (as spoken; Ctrl J in Blender) to join.
   - Remesh at **0.03**.
   - **Clay Strips** blends the transition: "adding in volumes going towards the eyebrow" and at the sides. Then smooth.
   - Re-crease the brow line.
10. **[1:58:54] Eyeballs**
    - Shift A, Mesh, **UV Sphere**. Rotate **90° on X** so the pole faces forward. Scale it down and place it in the socket, moving it forward.
    - Shade Smooth.
    - **Mirror modifier with Mirror Object = the head**.
    - His reference has wide spacing, so he spaces the eyes out.
    - In sculpt mode, Grab pushes back the area where the eyelids go; then smooth.
    - Character-specific: the outer corner is higher than the inner corner, done with Grab.
11. **[2:01:19] Eyelids**
    - Remesh at **0.02** and smooth.
    - **Draw brush (V)** over the upper lid, then shape it with Grab to match the reference's eye shape. Same for the lower lid.
    - Character-specific: "the upper eyelid is basically non-existent" because the character is Asian, so he smooths the fold away. "This is why you need to have references".
    - **The three edges:**
      - Crease Polish (Shift C, Ctrl) defines the lid margin and the fold.
      - **Scrape planes the underside of the lid**.
      - Grab pulls it back "to make sure that the eyelids are wrapping around the eyeball".
      - Same for the lower lid.
      - Crease Polish defines the edge transitioning into the face.
    - Smooth the transitions.
12. **[2:05:25] Nose refinement**
    - "The nose has to be way smaller for my character".
    - Side profile: "this nice curve going into the forehead". He calls it good "especially for female characters".
    - Narrower from the front; smooth.
    - Pull the nostril wings out; Crease Polish the nostrils; round off the bottom.
13. **[2:06:45] Brow shape.** From the reference, marked with Crease Polish.
14. **Chin.** Crease Polish plus Grab to shape it.
15. **[2:07:35] Mouth**
    - "The mouth doesn't sit on a flat surface. Right now, this is really flat."
    - First add volume with Clay Strips so "the mouth wraps around the teeth", then smooth.
    - Mouth corners: Crease Polish, placed using the iris-midpoint rule. If wrong, move them with Grab.
    - "Pull back the corners of the mouth" to show the wrap around the teeth.
    - Lip line: Crease Polish draws "a straight line from the corners of the mouth to the center of the face". He pulls the whole mouth down because it was too high.
    - **Upper lip:**
      - Crease Polish (Ctrl) marks the lip edge, then Grab pulls it out because it is "too flat".
      - "The upper lip ... sits in front of the lower lip". Add volume and curvature.
    - **Lower lip:**
      - Inflate the area, smooth the corners, define the edges with Crease Polish (Ctrl).
      - Grab it into place, dragging slightly down to fit the reference.
16. **[2:11:36] Make everything work together**
    - Adjust the jaw shape against the reference.
    - Add cheek volume (spoken as "crease brush", probably Clay Strips) and smooth.
    - Smooth the lip transitions.
17. **[2:12:41] Refinement**
    - Remesh at **0.012**.
    - Crease Polish the mouth line and corners; smooth "surface irregularities".
    - Raise the jaw line to the reference.
    - Refine the nostrils with Crease Polish; dig in with Draw (Ctrl).
    - **Remove the construction eye line**: fill it with Clay Strips, then smooth.
18. **[2:14:21] Iris colour (vertex paint)**
    - Select the eyeball in edit mode. Select the front-pole vertex, then **Ctrl Numpad +** to grow the selection.
    - Go to Vertex Paint, enable the **face-selection paint mask**, and paint.
    - To see it in object mode: Viewport Shading, **Color = Attribute**, in both viewports.
    - Rotate the eyes to fit (gaze direction).
    - Reason: "with the iris in place, we're going to have a better feel for the character".
19. **[2:15:28] Eyelid refinement.** Crease Polish on the margin and upper edge, then smooth.
20. **[2:16:16] Final shape adjustments.** Smooth the brows; make the jaw "more pointed" from the front; adjust the cheek volume.
21. **[2:16:47] Placeholder eyebrows**
    - Shift A, **Plane**. In edit mode, rotate it 90° on X, move it forward, scale it, and put it on the left side.
    - **Snapping:** Face Project, with **rotation and scale alignment on**, so faces stick to the sculpt surface.
    - Scale it thin on Z ("really thin" for this character) and extrude it along the brow line.
    - Modifiers: **Mirror (Mirror Object = the head) plus Solidify** with the thickness raised until the shape reads. Shade Smooth.
    - Colour it with vertex paint.
      - **Not pure black:** "If you use a completely black color, you won't really be able to see the forms". The value is set to "about 25".
      - Fill: spoken as Ctrl X.
    - Shape it with Grab in sculpt mode.
    - "This is going to be a placeholder ... replaced with actual hair geometry in future chapters".
22. **[2:19:30] Placeholder eyelashes**
    - Use the same object. Duplicate one vertex with Shift D and extrude it along the eyelid edge (hide the eyeballs while doing this). Extrude back with the same number of segments, then fill faces with **F** repeatedly.
    - Solidify came out flipped. **Shift N** recalculates normals.
    - Vertex paint, then shape with Grab.
23. **[2:20:38] Ears**
    - **/** brings back the other objects.
    - Smooth the blockout ear and place it from the reference.
    - Remesh at **0.02**.
    - **Stylised-ear technique:**
      - Choose the **Lasso Mask** (from the Box Mask tool group, added to Quick Favorites).
      - Enable **"Front Faces Only"** so the back isn't masked. Ctrl removes from the mask.
      - Mask the ear's outline, then **Ctrl I** to invert.
      - Use **Grab with a very big radius** to push the inner bowl in, then down.
      - **Alt M** clears the mask.
    - Raise the remesh resolution, smooth, then Crease Polish the inner edge, the rim edge, and so on. Reshape with Draw.
    - Details: question-mark rim, then a **Y shape** built with Clay (two branches), then smoothed and defined with Crease Polish (Ctrl).
    - Remesh at **0.008** and define all the ear shapes again.
24. **[2:26:10] Wrap-up**
    - "Carefully look at your reference, compare it with what you have on your sculpt".
    - Take breaks: when you come back "you'll be able to also spot some mistakes".

---

## 4. All concrete techniques, values and rules (summary list)

### Settings and numbers

| Item | Value |
|---|---|
| Blender version | 5.0 |
| Viewport focal length | 150 mm (avoids distortion while sculpting) |
| Viewport clip start | 0.1 (fixes artefacts at non-real-world scale; real-world scale applied after sculpting) |
| Silhouette view | Flat lighting, Custom colour black, specular off (5.0) |
| Voxel remesh progression | Blockout: low-res round cubes with loop cuts (6, 8 or 3×3)<br>Head: 0.04–0.05<br>After nose join: 0.03<br>Eyelids / ear start: 0.02<br>Refinement: 0.012<br>Ear details: 0.008 |
| Eyeball | UV Sphere rotated 90° on X; Mirror modifier with Mirror Object = head |
| Iris | Vertex paint; viewport Color = Attribute |
| Eyebrow / lash placeholder colour | Value about 25 (dark grey, not black) |
| Placeholder geometry | Plane + Mirror + Solidify; snapping Face Project with rotation and scale alignment |

### Add-ons and preferences

- **Extra Mesh Objects** extension, which provides the Round Cube.
- Keymap option **"Extra Shading Pie Menu Items"**: the Z pie gets an overlays toggle (swipe up) and an X-ray toggle (swipe down).
- Screencast keys (display only).
- **PureRef**, pinned always on top.

### Shortcuts (as spoken)

| Shortcut | Action |
|---|---|
| G | Grab |
| Shift C | Crease Polish |
| Shift T | Scrape |
| V | Draw |
| I | Inflate |
| Shift | Smooth |
| Ctrl | Invert brush (dig in) |
| F | Flip Line Project cut side |
| Alt M | Clear mask |
| Ctrl I | Invert mask |
| Ctrl R | Loop cut (edit mode), voxel remesh (sculpt mode) |
| R | Set remesh size |
| Alt Q | Switch sculpted object |
| Alt Z | X-ray |
| / | Local view |
| Ctrl A | Apply all transforms |
| Shift D | Duplicate |
| E | Extrude |
| F | Fill face (edit mode) |
| Shift N | Recalculate normals |
| Ctrl Numpad + | Grow selection |
| Numpad 3 | Side view |
| −Y / −Z gizmo | Front / bottom view |
| Q | Quick Favorites |
| N / T | Sidebar / toolbar |
| Ctrl G (as spoken) | Join |

### Brushes and what each is used for

- **Grab:** primary blockout tool. Also positions every feature, and with a very big radius pushes in the masked ear bowl.
- **Line Project:** flat cuts on the head sides, neck, torso bottoms, legs, feet, arm sockets and hand.
- **Crease Polish:** separations and landmark lines: jaw/cranium, eye line, brow line, chin, eyelid edges, lip edges, nostrils, ear folds.
- **Scrape:** planes (temples, side of face, underside of the eyelid, flattening the round front of the shoulder).
- **Clay Strips:** volume (nose-to-brow blend, mouth bulk, filling the construction line, ear Y shape).
- **Inflate:** palm sides, lower lip.
- **Draw:** eyelids, nostril digs.
- **Lasso Mask:** protects the sole; ear technique with Front Faces Only.
- **Smooth (Shift):** constantly.

### Construction rules

- Use separate primitive objects per body part. Each part should flow into and overlap its neighbour, never stack.
- Transform blockout parts **only in edit mode**, to keep the origin for sculpt symmetry and Mirror. If you must, apply Ctrl A All Transforms before adding Mirror.
- Symmetry: X symmetry while sculpting. Use Symmetrize +X→−X for parts made on one side, and the Mirror modifier for paired parts. For eyes and brows, Mirror Object = the head.
- Check the active object (the yellow one) before entering multi-object edit mode.
- Save early.

### Proportions and anatomy

- Head
  - The head is a cranium plus a jaw wedge.
  - The back of the head is not fully round.
  - The sides of the head are flat-cut.
- The neck tilts backward and merges with the chest (front), the back, and the shoulders (sides).
- Ear
  - On the jaw/cranium separation line.
  - Between the brow line and the bottom of the nose.
  - Not facing front.
  - A wedge from the front and top views.
  - Details: a question-mark rim and a Y inside.
- Torso: rib cage, middle and pelvis, following a side-view S-curve.
- Female character: shoulders "not too massive".
- Legs
  - Upper leg: curve at the front, straight at the back.
  - The buttock overlaps the leg.
  - Knee formed by the upper leg.
  - Lower leg follows the "angry face": the inner calf is higher, and the inner ankle is higher than the outer.
- Foot: rectangular from below, a right-angle triangle from the front, a triangle from the side, giving "balance".
- Arms
  - A-pose, not too close to the body.
  - Slight elbow bend, for rigging.
  - The bicep ends in a V into the forearm.
  - The forearm has a curve profile.
- Hand: blockout is a rectangle palm, with inflated sides and a thumb nub.
- Face proportions: see the Chapter 3 fundamentals above (eye line at ½, thirds, 1-1-1 side-profile depth, mouth at ½ of nose-to-jaw, 5 eye widths, mouth corners inside the iris centres).
- Eyes sit in sockets. The lids wrap around the eyeball and have three edges.
- The nose is a rounded triangular block. A nose-to-forehead curve suits female characters.
- The mouth is volumetric and wraps around the teeth. The upper lip sits in front of the lower lip, and the corners are pulled back.

### Stylisation principles

- **Shape language** (round, angular, boxy, triangulated box, elongated box), kept consistent across the whole character and through all stages.
- **Straight versus curve** pairing.
- **S-curve** through the side view.
- **Silhouette readability.**
- **Exaggeration comes from the concept.** Stylised characters break human proportion; measure the concept's own ratios (for example head height = body height = leg length) and copy those.
- In the face, the proportions are a "generic" baseline that stylised characters may deviate from. His character has big eyes, wide eye spacing, wider cheeks, a small nose and a pointed jaw.

### Reference advice

- Keep one master concept plus targeted references per part, chosen to answer what the concept doesn't show (boots, skirt, hair flow, materials).
- Use photo references as proportion guides for the ethnicity.
- Keep the references visible at all times and compare constantly.
- Get permission for other artists' concepts.
- Avoid overly complex concepts while learning.

### Checks he does repeatedly

- The silhouette viewport.
- Looking at the model from all angles: "so that you don't have something that looks like this".
- Front versus side flow between parts.
- Keeping the S-curve.
- Comparing with the reference.
- Measuring the proportion lines on the face.
- Taking a break of about 30 minutes and coming back with fresh eyes.

### Mistakes he warns about

- Skipping the concept, references or fundamentals.
- Choosing an overly complex concept.
- Adding detail during the blockout.
- Transforming parts in object mode, which breaks the origin, symmetry and Mirror.
- Parts stacking or floating instead of flowing together.
- Losing the S-curve.
- Eyes or features on a flat face. Side-profile depth is "where most beginners make mistakes".
- A flat mouth.
- A round back of the head.
- An ear facing front.
- A straight neck.
- Arms too close to the body, which hurts rigging.
- A dead-straight arm (no bend for the rig).
- Pure black eyebrows, which hide the form.
- Inverted Solidify normals.
- The Line Project cutting the wrong side.
- The wrong active object in multi-edit.
- Not saving early.
- Clipping artefacts from non-real-world scale.

---

## 5. Applicable to a scripted bpy pipeline (MPFB/MakeHuman, Mixamo, EEVEE/Cycles, toon look)

### Can become rules or code

1. **Concept and reference step as a pipeline gate.**
   - For every new cast member, require a concept sheet and a per-part reference list (face, hair flow, clothing, boots or shoes, materials) before scripting.
   - Store the references next to the cast sheet. This matches the "references answer what the concept doesn't show" rule.
2. **Proportion checker** (a Python function on an MPFB head, or on any head mesh with landmark vertex groups). Measure from bounding-box and landmark Z/X values and flag deviations:
   - eye line ≈ 0.5 × (top of head to bottom of jaw)
   - brow line and nose base at ⅓ and ⅔ of hairline to jaw
   - ear top and bottom between brow line and nose base
   - bottom of lower lip ≈ midpoint of nose base to jaw
   - inter-eye distance ≈ 1 eye width; total face width ≈ 5 eye widths
   - mouth corner |x| ≤ iris-centre |x|
   - side-profile depth: outer eye corner → eye front → nose bridge → nose tip in roughly equal Y steps, so the face is not flat
   - For CARTOON style, the targets can be deliberately offset (for example bigger eyes, wider spacing) and the offsets stored per character in `cast.py`, which matches "stylised characters break proportions". The checker reports; it does not force.
3. **Body-proportion targets from a concept.**
   - Encode the concept's ratios per character (for example head height : torso : leg) and drive the MPFB modifiers or bone scales toward them.
   - Check the side-view S-curve (spine/pelvis angles) and confirm the neck tilts back slightly.
4. **Silhouette render check** (fully scriptable).
   - A workbench or EEVEE pass with flat lighting, an object colour of pure black on white (`shading.light='FLAT'`, `shading.color_type='SINGLE'`, `single_color=(0,0,0)`, white background), specular off.
   - Render front, side and 3/4 turnaround thumbnails per character and per key pose. Use them to judge readability, and compare shape language between cast members.
5. **Review-camera standard.**
   - Use about 150 mm focal length for character review or turnaround renders. That is his anti-distortion setting, and it also suits portrait and close-up shots.
   - Set clip start sensibly for the scene scale (he uses 0.1 at non-metric scale). Work at real-world scale for final assets, as he says he will.
6. **Rig-ready rest pose.**
   - The base mesh should be in an A-pose with arms clear of the torso and a slight elbow bend.
   - This applies when we build or modify bodies before Rigify or Mixamo retargeting.
7. **Transform hygiene in scripts.**
   - Apply transforms (`bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)`) or do the modelling in mesh space before adding Mirror or symmetry operations.
   - Keep origins at the body centre for mirrored parts.
   - For eyes and brows, use a Mirror modifier with `mirror_object = head`.
8. **Procedural eyes** (this replicates his steps).
   - A UV sphere rotated 90° on X so the pole faces forward, shaded smooth, mirrored about the head.
   - Iris as vertex colour, or better a material ring driven from the front pole. Select the pole vertex and grow the selection N rings.
   - Set eye rotation/gaze per shot. This fits our toon look and eye tracking.
9. **Placeholder brows and lashes as mesh strips.**
   - A plane extruded along a curve of surface points, shrinkwrapped or snapped to the face (scripted equivalent of Face Project snapping: a Shrinkwrap modifier with Project or Nearest Surface).
   - Then Solidify, then Mirror. Recalculate normals afterwards (`bmesh.ops.recalc_face_normals`) to avoid flipped Solidify.
   - **Colour rule: brows and lashes are not pure black.** Use about 0.25 value so the form reads. This is directly useful for cel shading, where pure black merges with the ink outlines.
10. **Shape-language and stylisation rules for the cast**, as design documentation and per-character parameters:
    - one dominant shape family per character (round, boxy, angular or triangular), kept consistent across head, body, props and clothes
    - straight-versus-curve pairing on limbs (curved front and straight back of the thigh; calf "angry face" with inner bulge high and outer low; inner ankle higher)
    - feet as a right-angle triangle from the front
    - upper lip in front of the lower lip; mouth corners pulled back
    - nose as a rounded triangle block
    - these can guide MPFB slider choices and any shape-key tweaks
11. **Mouth and eyelid wrap**, relevant to lip-sync (`talking=True`).
    - Lips wrap around the teeth and lids wrap around the eyeball.
    - Check that MPFB/our mouth shapes keep volume (corners recessed), and that eyelid closing or blink shape keys follow the eyeball's curvature rather than a flat plane.
12. **Iterative review loop.**
    - Front, side and all-angle turnaround renders compared side by side with the reference image (he always keeps a comparison viewport).
    - Fresh-eyes review after a break. For us: re-check renders in a separate pass before the final render.
13. **Workflow ordering as a template:** concept → references → blockout/proportions → face → body → clothes → retopology → UV → hair → shading → rig → lighting/present. Our MPFB pipeline skips retopology and blockout, but the order of decisions (proportions locked before detail) still applies.

### Hand-done in the course (sculpting) and hard to script

- All the brush work:
  - Grab, Crease Polish, Scrape, Clay Strips, Inflate, Draw and Smooth strokes
  - the planes of the head, eyelid edges, lips, nostrils
  - ear folds (lasso mask plus big Grab)
  - flow between parts
- These need an artist with a tablet. bpy can call voxel remesh (`mesh.remesh_voxel_size`, `object.voxel_remesh`) and apply masks programmatically, but the shaping strokes themselves are not practical to script.
- Judging appeal, matching a concept "by eye", and the break-and-revisit judgement are human tasks. Scripts can only provide measurements and silhouette or turnaround renders to support them.
- Only parts can be done procedurally: primitive blockouts (round cubes via Extra Mesh Objects or bmesh, mirrored, loop-cut) could be generated from a parameter table to make a rough proxy or silhouette. For production faces, our pipeline should keep using MPFB/MakeHuman targets, shape keys and the cast system rather than sculpting.
