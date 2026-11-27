# Notes: Kenny Praise masterclass, rigging/posing chapter + lighting/presentation chapter (13)

**Coverage read:**
- `10_rigging_posing.txt`: 102,760 / 102,760 characters, **100%** ([17:25:18] to [19:05:36]; the file ends with the first lines of chapter 13).
- `11_lighting_present.txt`: 65,354 / 65,354 characters, **100%** ([19:05:53] to [20:06:09]; the last ~4 minutes, [20:02:11] onward, are an ad for his "Stylized Character Academy" with no technique in them).

I read both files in sequential 25,000-character slices with no gaps. The transcript never gives the rigging chapter a number. The lighting chapter calls itself "chapter 13 ... the last and the final chapter".

Character: "Jenny" (collection names `CH_Jenny…`). It is a stylized girl with separate eye/cornea objects, a jaw/teeth/tongue mesh, hair curves on "scalp" objects (hair, brows, lashes, ponytail), a hair band, a shirt, a skirt, a necklace (chain) and multi-part shoes/boots. Blender 5.0.

---

## 1. Workflow, in order, with timestamps

### Rigging and posing chapter

**Theory (slides)**
- [17:26:22] Rigging gives the character a skeleton, which Blender calls an "armature". He keeps it to "the bare minimum ... to avoid breaking your character" and to pose well.
- [17:27:43] Bones are linked by parent/child hierarchy. A child can sit at an offset from its parent; the dashed relationship line shows the link. Edit mode is for building bones (extrude), pose mode is for posing and animating.
- [17:29:37] Weights bind the mesh to the bones. Influence runs from 0% (blue) to 100% (red) and is "blended between multiple bones so that the movement can look natural". You see it in Weight Paint mode as a heat map. Example: "Instead of this head bone controlling the leg, cuz that can actually happen".
- [17:32:05] Add-ons: **Rigify** (built in, the one he uses; enable it in Preferences > Add-ons) and **Auto-Rig Pro** (paid, "can guess ... where the fingers of your character is"; left for you to explore).
- [17:34:30] Posing principles. Details are in section 2.

**Practice in Blender**
1. [17:42:02] Collections: under `CH_Jenny`, create `CH_Jenny_rig` and `CH_Jenny_model`. All geometry goes into the model collection.
2. [17:43:07] Shift+A > Armature > Rigify > **Human (Meta-Rig)**.
3. [17:43:24] Fit the metarig **in Edit Mode, not Object Mode**, so the object transform "can stay the same". Scale it down to character height with the pivot at the 3D cursor.
4. [17:44:13] Turn on Armature > Viewport Display > **In Front**. Isolate body + rig with `/` (local view).
5. [17:45:36] Turn on **X-axis mirror** in edit mode so you only work on one side.
6. [17:45:52] Spine/pelvis: line up from front and side; the spine curves to follow the body. Box-select the shared joint of connected bones so you don't disconnect them.
7. [17:46:57] Legs: thigh to knee, then the foot bone where the foot rotates, the toe, and the **heel bone at the bottom of the shoe sole** so the foot rolls from the right point. Scale the heel bone (S X) to the width of the shoe. [17:48:04] Leave **a slight bend at the knee** "so that Blender knows that we want to rotate the leg bone in this direction ... Don't make it completely straight".
8. [17:49:09] Neck/head: two neck bones (named "spine"), head bone up to the top of the skull. Leave the "face" bone inside the head roughly where it is.
9. [17:49:40] Breast bones go to the middle of each breast.
10. [17:50:12] Shoulder/arm: the shoulder bone follows the clavicle, the upper arm runs to the elbow, then forearm, then hand. Watch out: pressing F creates a new bone.
11. [17:51:33] Fingers and palm bones. Method for putting bones in the middle of the finger volume: in the body's edit mode, select an edge loop at the knuckle, Shift+S > Cursor to Selected, then in the armature's edit mode, Shift+S > Selection to Cursor. Repeat for each joint.
12. [17:55:00] Face bones: scale them to the face width. Turn on snapping with **Face Project** plus Align Rotation/Scale and snap the bones onto the surface: ear (3 + 2), temple, jaw, chin, mouth corner, cheek bottom and top, forehead (placed just above the brows), brow top and bottom, nose, lips, eyelid corners and middles. Move **disconnected, stacked bones by box-selecting all of them together**, otherwise rig generation errors. Move centre-line bones **only from the side view with snapping off**.
13. [18:02:03] Eye bone: snap the cursor to the cornea object's centre, then move the head and tail of the bone there and pull the tail straight forward along Y.
14. [18:02:51] "The ones that we tend to forget ... are the tongue bones and the teeth bones": 3 tongue bones and one `teeth.B`, placed in X-ray.
15. [18:04:13] Generate: the old face rig warning comes up, so click **upgrade face rig**. He moves the new **jaw_master** bone down near the ear ("that's where the jaw is going to open from"). Then Rigify > **Generate Rig**.
16. [18:05:34] "In edit mode [of the generated rig] ... you don't really want to touch anything." Work only in pose mode. Hide the bone collections you don't need.
17. [18:05:51] Bind: select body, then rig, Ctrl+P > **With Automatic Weights**.
18. [18:07:11] Finger curl test: scaling the finger control should curl the finger, but it curled the wrong way. Fixes are in the metarig, after which he regenerates (you "can always still come back and regenerate"):
    - **Bone roll** (Ctrl+R): X axis along the curl direction, Z pointing down, on every finger bone.
    - **Straighten** each finger chain: Transform Orientation **Normal**, pivot **Active Element**, snapping off, `S X 0` (and for the thumb also `S Z 0`). Then re-centre it with R Z / R X.
    - Then add back **a small deliberate bend toward the palm** (G Z a tiny amount on the middle joints) "so that Blender knows ... we want to rotate it in towards the palm".
    - Regenerate. "Now everything is working just right."
19. [18:14:14] Clear the pose with **Alt+R / Alt+G / Alt+S**. For bones use **Local** transform orientation and **Individual Origins** pivot.
20. [18:15:52] Test the jaw (R opens the mouth) and the mouth controls (smile).
21. [18:16:56] Performance: Render Properties > **Simplify**, Max Subdivision **0**. He adds it to Quick Favourites (Q) so he can toggle it while posing.
22. [18:17:47] Pose-mode **X-Mirror** so posing one eyelid mirrors to the other.
23. [18:18:17] Weight-paint fixes:
    - The brows were dragging the top of the head. With **Auto Normalize** on and X symmetry on, paint `spine.006` (head) at 1.0 over the skull (avoiding the ears). Auto Normalize then removes other bones' influence there.
    - Eyelids (`lid.T.L`, `lid.T.L.001/.002` …): use a tablet with pressure. Paint adds weight, **Shift** smooths/blurs, **Ctrl** subtracts. Use a **face-selection mask** (select the upper-lid faces in edit mode, Ctrl+Numpad+ to grow, enable Paint Mask) so the lower lids stay untouched. Take brow influence off the eyelids.
    - His view: weight painting "is kind of a guessing game".
24. [18:25:10] **Corrective shape key driven by a bone** (for the eye-close shape weights couldn't give):
    - Pose the lid control closed and note its local Y location: **-0.024**.
    - Shape keys: Basis (never touch it), then a new key `eye_close`. In Blender 5 the value defaults to 1; in 4.5 and earlier set it to 1 by hand.
    - Sculpt the key (mask the lower lid with Shift+A grow mask, Grab brush), "bulging out just a tiny bit" when closed.
    - Make sure the **Armature modifier is at the top of the stack, above Subdivision** ("deform before we subdivide").
    - Driver on the key value: type **Averaged Value**, Object = rig, Bone = `lid.T.L.002`, **Y Location, Local Space**. In the Driver Editor, set the F-curve end keyframe to (-0.024, 1) with the start at (rest 0, 0), and make both keyframes **Linear** interpolation.
    - [18:33:42] Left/right split: make vertex groups `left_side` and `right_side`. Assign each side at weight 1.0, the centre line at 0.5 to both. Set the key's Vertex Group to `left_side`, then **duplicate** the key as `eye_close_R` with `right_side`, **copy/paste the driver** and change its bone to `lid.T.R.002`, then Update Dependencies.
25. [18:37:30] Eyes: select cornea + eyeball, then rig, Ctrl+P > **With Empty Groups** (so the temple bone etc. can't move the eyeball). In edit mode select all and assign weight 1.0 to `DEF-eye.L` / `eye.R`.
26. [18:40:35] Teeth/tongue (jaw mesh): parent with Empty Groups. Top teeth go to `teeth.T` at 1.0, bottom teeth to `teeth.B`. For the tongue, show only the DEF bone collection, select the 3 tongue DEF bones, then Weight Paint > Weights > **Assign Automatic From Bones** (automatic weights limited to the selected bones).
27. [18:44:03] Hair: parent the **scalp** objects (not the curves) with Empty Groups. Main hair scalp: everything to `spine.006` (head) at 1.0. Brows and lashes scalps: **Weight Paint > Transfer Weights** from the body, using **Nearest Face Interpolated** and layer matching **By Name**. Ponytail scalp and hair band: all at 1.0 to the head bone ("doesn't need to deform").
28. [18:47:48] Shirt: parent with Empty Groups, then Transfer Weights from the body (same settings). "Deforming nicely". Hair curve viewport display amount goes down to 0.02.
29. [18:48:56] **Shoes and skirt: proxy "rig helper" + Surface Deform**:
    - Multi-part objects (a sole separate from the rest) "might not deform well" with automatic weights.
    - Model a simple low-poly closed proxy that "envelopes the whole object" without clipping into it. Smooth it in sculpt mode. Name it `GEO_Jenny_shoe_rigHelper`, put it in a `CH_Jenny_rig_helpers` collection, add a Mirror modifier for both feet.
    - Parent the proxy to the rig **With Automatic Weights**. Display it As **Wire**.
    - Real shoe: parent to the rig With Empty Groups, leave the groups empty, Armature modifier above Subdivision, add a **Surface Deform** modifier (also above Subdivision) targeting the helper. **Turn on Simplify (max subdiv 0) before pressing Bind**, "if you have the subdivision turned on at this point, you're going to get a little error". Hide the helper in viewport and render.
    - Skirt: same method. "Much better than what we would have gotten if we used automatic weights."
    - [18:58:48] Clipping when the leg lifts: **unbind** Surface Deform, sculpt the skirt outward, then rebind. Sculpting while it is bound looks like nothing happens ("we are not just seeing it").
    - The necklace chain gets the same treatment (done off camera).
30. [18:59:19] **Mask hidden body**: select the body faces under the clothes (Ctrl+Shift+M mirrors the selection, keep the shoulders) into a vertex group `mask`. Add a Mask modifier with **invert** on, placed above Subdivision. This stops the body poking through the clothes and helps performance. Turn it off while posing the bare body.
31. [19:02:04] Posing workflow: "start off with the bare body ... don't get worried about the clothes". Save iterations as **Pose Assets**: Asset Browser > Current File, then in pose mode Assets > Create New Pose Asset. To get a thumbnail, add a camera (Numpad 0, Lock Camera to View) and create the pose asset again. Double-click a pose to apply it. He recommends at least two poses for the final renders.
32. [19:04:26] Summary: "rigging gives your character a skeleton ... weight is how you control how the character is going to deform ... good posing relies on reference, exaggeration and balance."

### Chapter 13, lighting and presentation

**Theory (slides)**
- [19:07:14] Lighting drives storytelling and mood. Good lighting means **(1) the right mood, (2) depth/three-dimensionality, (3) control over where the viewer looks** (usually the eyes or face).
- [19:09:59] Lighting and composition (framing, camera angle, focal length) "always work hand in hand". Light that works from one angle may not work from another. "Cheat code": use reference stills from movies and animation.
- [19:11:19] Light types:
  - **HDRI**: 360° environment light with natural reflections. Its sun position is fixed. **He uses it only as ambient light**, "not ... our main lighting".
  - **Point**: a bulb that emits in all directions. Power can be negative.
  - **Sun**: only its direction matters, not its position. Good for outdoors; he "usually" doesn't use it for character renders.
  - **Spot**: a stage-light cone. Spot Size default 45°. Blend 0 gives a harsh edge, 1 a smooth one.
  - **Radius/size on any light**: 0 gives harsh shadows, larger gives softer ones.
  - **Area**: a soft box, "perfect for lighting characters". His main light type.
- [19:17:12] **Three-point lighting** as the reliable starting point. Practise it first, then experiment beyond it.
  - Key: brightest light, defines forms, main shadows and highlights.
  - Fill: on the opposite side; brightens the key's shadows without removing them.
  - Rim: behind the character; outlines the edges and separates the character from the background.
  - Together they give "clear forms, controlled contrast, and a strong separation".
- [19:20:44] Post-processing: film grain, lens distortion, chromatic aberration, subtle glow, vignette, "stuff that comes with natural cameras". They make the image "more natural and much more grounded". "Don't skip".

**Practice in Blender**
1. [19:21:50] Pose check. On the skirt and boot rig helpers he added **per-pose shape keys** to fix unnatural shape and clipping after posing. Rig hidden.
2. [19:23:09] Camera: Numpad 0, padlock "Lock Camera to View". Resolution **1200×1500** (Instagram), 1920×1080 for YouTube/ArtStation, "or something more cinematic". Portrait focal length "**about 80 to about 90 mm**". "You don't have to stick to the standard since you're in 3D. Just go for what looks good" (he pushes it a bit beyond that range).
3. [19:25:38] Split the viewport: one view is the camera in rendered mode with overlays and gizmos off. In the shading popover turn on **Scene Lights** and **Scene World** (they were off during texturing).
4. [19:26:58] **Backdrop (studio cyclorama)**: a plane extruded up and bevelled shows its edges from some angles, so he uses a **filled circle**, extrudes the back half of the rim edges up, bevels the corner (Ctrl+B), shades smooth. Put it in a `render` collection, lights in a `render/lights` sub-collection, camera in `render`.
5. [19:29:40] **Key**: an Area light, `light_key`. Power raised without overexposing. Aimed to cast shadow on the far side of the face. Later [19:39:59] adjusted so the face isn't split into two flat halves: "I want some of the light to fall on this other side of the face".
6. [19:30:28] Hair viewport display amount 0.05 (later 0.01) while lighting, set to full for the check render.
7. [19:31:47] **Fill**: an Area light on the opposite side, `light_fill`, at much lower power. At equal power "the whole render look[s] flat". **Scaled up large** so it barely casts shadows. Larger area means softer shadows, smaller means sharper ([19:32:53]).
8. [19:33:43] **Rim**: an Area light behind the character, "power up way higher". **Scaled narrow on X** so it favours one side. Rotated with **Global** orientation (switch back from Local after rigging), stretched on Z so it reaches the legs.
9. [19:35:25] **Light linking** (Blender 5.0, Object > Shading > Light Linking) on the rim light: new collection, drag the backdrop in, set it to **Exclude**, which removes the harsh rim spill on the backdrop.
10. [19:36:31] Backdrop material: dark base colour, made non-reflective ("turn off the roughness" in his words; the intent is no reflection) and **specular turned down**.
11. [19:37:04] See only the frame: in Cycles, **Ctrl+B render region** around the camera frame; in EEVEE, Camera > Viewport Display > **Passepartout 1.0**.
12. [19:37:52] The legs were too dark, so he duplicated the key lower down and **Ctrl+L > Link Object Data** so both keys share power. Also a second, lower fill.
13. [19:39:11] **Rim colour**: "something like a orange red", chosen from the scene/character palette.
14. [19:40:49] Extra **Point light** `light_backdrop` placed **directly behind the character, opposite the camera**, lighting the backdrop to separate the character further; tinted. Another duplicated fill aimed at the backdrop to remove its shadows.
15. [19:42:41] Check render with full hair. Lower the backdrop base colour.
16. [19:43:13] **HDRI for ambience only**: a "forest"/nature HDRI via the Poly Haven add-on (or World > Environment Texture), "reduce the strength so it doesn't overpower the lights". Rotate it with the add-on's slider.
17. [19:44:50] "I'm not going to stick with the three-point lighting ... I'll go with some more cinematic lighting styles for my final renders."
18. [19:45:06] Cameras: `camera_wideShot`, `camera_closeUp`, optionally detail shots (shoes, skirt). "If you have no idea ... I'll suggest a wide shot and a close-up."
19. [19:46:30] **Turntable**:
    - Duplicate the wide camera as `camera_turnaround`.
    - Add an Empty (sphere), `camera_turnaround_CTRL`, at the origin. Parent the camera to it.
    - Problem: from behind, the backdrop blocks the view and the lighting no longer reads. So **parent all lights and the backdrop to the same empty**, giving "consistent lighting whenever we turn around".
20. [19:49:24] **Camera binding** on the timeline (Ctrl+B in the timeline with the camera active): frame 1 = close-up, frame 2 = wide shot, frame 3 onward = turnaround camera.
21. [19:50:46] Timing: 24 fps, 8 s = 192 frames, so frames 3 to 195 (end frame 195). Keyframe the empty's rotation at frame 3 (K > Rotation) and at the last frame `R Z 360` plus a key. He does not mention interpolation.
22. [19:52:44] Output: 1200×1500, **resolution scale 150%** ("with 150 we don't really need to use a lot of render samples"; 200% for 4K), Frame Step 1 "so that we have a nice smooth turn around", **PNG** image sequence into a `renders` folder.
23. [19:54:37] Render: **Cycles**, GPU if available, **Max Samples 200** (default 4096 "is a bit too much"; "anywhere between 200 and 500"). "I don't like to play with any of these render settings". No other settings are changed.
24. [19:55:25] **Test renders** on random frames before the full animation. Rendering and lighting are "an iterative process" (he shows many iterations of an older project). Render the full sequence overnight.
25. [19:57:37] Assemble the image sequence in DaVinci Resolve (Media tab: drag images, recognised as a sequence; Cut tab timeline), or in Blender/CapCut. Video grading in the Resolve Color tab is "way beyond the scope".
26. [19:59:12] **Still post-processing**: Photoshop, convert to smart object, **Camera Raw filter**: temperature, tint, exposure, contrast, highlights, **Color Mixer** (saturation of magentas and blues), **Effects: grain** ("so that it feels like it's actually coming from a camera lens and it's not so perfect") and **vignetting**. "Postprocessing is going to be what looks good for you."
27. [20:01:37] Final renders were made with "a different lighting setup" (not shown). [20:02:11] onward: end of the course and an advert.

---

## 2. Concrete techniques (by topic)

### Rig system
- **Rigify Human Meta-Rig, generated rig.** Auto-Rig Pro is mentioned only. No custom rig. Face uses the **new Rigify face rig** (upgrade button), with jaw_master moved near the ear.
- Generated-rig rule: never edit the generated rig in edit mode. Fix problems in the **metarig and regenerate**.

### Bone placement rules
- Fit in edit mode, not object mode, with X-mirror on.
- Use In Front + local view.
- Box-select shared joints of connected bones and stacked disconnected bones so nothing disconnects.
- Pre-bend the knee (and finger joints) in the intended bend direction.
- Heel bone at the bottom of the sole, scaled to the shoe width.
- Finger bones centred in the finger volume using cursor-to-loop snapping.
- Finger bone roll: X along the curl axis, Z down.
- Face bones are surface-snapped (Face Project); midline bones are moved from the side only, with snapping off.
- Eye bone from the eyeball centre straight forward along Y.
- Don't forget the tongue (3 bones) and the teeth bone.

### Weight painting
- Body: Ctrl+P With Automatic Weights. "For the most part the automatic weights are going to do a really nice job". Problem areas he found: eyes/eyelids, and brows pulling the head top.
- Tools: Auto Normalize, X symmetry, pressure, Ctrl subtracts, Shift smooths, face-selection Paint Mask.
- Rigid parts (eyes, teeth, hair scalp, ponytail, hair band): **Empty Groups + manual 100% assignment to one bone**, so unrelated bones can't influence them.
- Partial auto: **Assign Automatic From Bones** with only the relevant DEF bones selected (tongue).
- **Transfer Weights** body to clothes/brows/lashes: Nearest Face Interpolated, By Name.

### Clothes and accessories
- Tight shirt: transfer weights from the body.
- Multi-part or loose items (shoes, skirt, necklace chain): **proxy cage + Surface Deform**. The cage gets automatic weights; bind at subdivision 0; the cage is hidden.
- Modifier order: **Armature (and Surface Deform, Mask) above Subdivision Surface**.
- Fix clothing clipping by **unbind, sculpt outward, rebind**, or by **per-pose corrective shape keys** on the cage ([19:22:05]).
- **Mask modifier** hides body under clothes.

### Shape keys / correctives
- Bone-driven corrective shape keys: driver Averaged Value, bone local-space transform channel, linear 0 to 1 mapping via the F-curve keyframe (-0.024 maps to 1). Left/right via vertex groups with the centre at 0.5.
- "Shape keys are going to allow us to push and refine the pose beyond the limits of the rig" ([17:40:58]).

### Eye controls
- Rigify face eye controls rotate the eyeballs. Eyelids follow, "just like the way you would for a normal human character". Eye meshes are weighted 100% to `eye.L`/`eye.R`.

### IK/FK
- **Not discussed explicitly.** Rigify's generated controls are used as-is. No IK/FK switching, pole targets or foot roll explanation beyond heel placement.

### Deformation checks
- Rotate controls in pose mode after binding.
- Finger curl test (scale the finger controls).
- Jaw open, smile, eyelid close (G Y).
- Brow move to check head-top dragging.
- Leg raise to check skirt clipping.
- Elbow, shoulder and knee bends are **not specifically demonstrated** beyond a generic "rotate this ... see how the rig is working".

### Posing principles ([17:34:30] to [17:41:46])
- "Posing is actually much more important than the rig". A bad pose makes the whole render "look off".
- **Always use reference.** "You may know what a movement feels like, but you actually don't know what it looks like". His example: "how much your shoulder is going to tilt if you raise one of your hands up?" Sources: Pinterest, the concept art.
- **Line of action**: find the line through the movement (head down through the legs) before posing.
- **Balance**: find where the weight and balance sit. Hips shift when the weight is on one leg.
- **Exaggerate** beyond the reference for stylized characters.
- **Avoid symmetry**: hands and fists never identical, legs asymmetric.
- **Contrapposto**: "weight ... shifted onto one leg causing a natural chain of opposing tilts in the hips, the torso and the shoulders". Hips tilt one way, shoulders the other; one side of the torso stretches, the other compresses. "Don't have parallel poses for the shoulders and for the hips."
- Push further with shape keys.
- Pose the bare body first. Save pose assets with thumbnails.
- Not covered: **hands/fingers posing and gaze** get no specific guidance beyond asymmetric hands and "control where the viewer is looking" (a lighting point).
- Silhouette is not mentioned.

### Lighting and presentation (values are as stated; he gives **no numeric light powers or colour values**)
- Area lights for key, fill (large, low power) and rim (higher power, narrow on X, orange-red). Extra key/fill copies low for the legs with linked data. Point light behind the character for the backdrop glow. HDRI at low strength for ambience.
- Light linking excludes the backdrop from the rim light.
- Dark, non-reflective backdrop: a curved cyclorama from a filled circle.
- Camera: 80–90 mm portrait, 1200×1500 at 150%. Wide shot plus close-up.
- **Depth of field: not mentioned.**
- Composition: only "use reference" and the wide/close-up/detail shot suggestion.
- Render: Cycles, 200–500 max samples, PNG sequence, 24 fps. **Denoise, colour management (view transform/look), light paths, the Blender compositor and EEVEE settings are not mentioned.** "I don't like to play with any of these render settings". EEVEE appears only for the passepartout tip.
- Turntable: an empty rotates the camera **plus all lights and the backdrop**, 360° over 192 frames. Stills are bound to frames 1–2 by camera markers.
- Post-processing is outside Blender: Resolve for video, Photoshop Camera Raw for stills (temperature/tint/exposure/contrast/highlights/HSL saturation/grain/vignette). Lens distortion, chromatic aberration and glow are named on the slide but not demonstrated.

---

## 3. Applicable to a scripted bpy pipeline (MPFB game_engine rig + Mixamo, EEVEE/Cycles)

Our rig is MPFB/MakeHuman `game_engine` driven by Mixamo retargeting, not Rigify. The ideas carry over; the Rigify-specific steps do not.

**Rig and bind**
1. **Never edit the generated/deform rig's rest pose in a film script.** Fix rest-pose problems at the source (the MPFB rig generation and the cast file), then regenerate, as he regenerates from the metarig.
2. **Pre-bend rule**: knee and elbow rest bones must have a small bend in the natural direction. If retargeted chains pop or flip, check the rest-pose bend and bone roll first. Check: angle between thigh and shin vectors in rest > ~2°, with the knee forward.
3. **Modifier order is a hard rule.** Checked in code for every skinned mesh:
   ```python
   ORDER = ('ARMATURE','SURFACE_DEFORM','MASK','SUBSURF')  # deform first, subdivide last
   def fix_stack(ob):
       mods = list(ob.modifiers)
       for t in reversed(ORDER):
           for m in [m for m in mods if m.type == t]:
               with bpy.context.temp_override(object=ob):
                   bpy.ops.object.modifier_move_to_index(modifier=m.name, index=0)
   ```
   (Run so that the final order is Armature, Surface Deform, Mask, Subsurf.)
4. **Rigid parts get 100% to one bone, with no auto weights**: eyes to the eye bones, teeth/upper jaw to head, lower teeth to jaw, hair caps/hats/hair bands/glasses to head. In bpy: create a vertex group named after the bone, `vg.add(all_indices, 1.0, 'REPLACE')`, Armature modifier, no other groups. This stops "the temple bone moving the eyeball".
5. **Clothes that hug the body**: transfer weights from the body using Data Transfer (vertex groups, `vert_mapping='POLYINTERP_NEAREST'`, layers by name), then apply it. Equivalent to `bpy.ops.object.data_transfer(data_type='VGROUP_WEIGHTS', vert_mapping='POLYINTERP_NEAREST', layers_select_src='ALL', layers_select_dst='NAME')`. Normalize afterwards (`bpy.ops.object.vertex_group_normalize_all(lock_active=False)`) and limit to 4 influences for EEVEE/game rigs.
6. **Loose or multi-part items (skirts, coats, bags, shoes with separate soles, necklaces)**: use a hidden low-poly proxy cage weighted to the rig, and the real mesh follows it via **Surface Deform**. Script order: set Simplify with max subdivision 0, then create Surface Deform (target = cage), then `bpy.ops.object.surfacedeform_bind(modifier=name)`, then restore Simplify. The cage: `hide_render=True`, `display_type='WIRE'`, in a `*_rig_helpers` collection. To edit the garment shape later: unbind, edit, rebind.
7. **Mask modifier** (invert) on the body for the region under opaque clothes. This removes skin poke-through in Mixamo poses. Keep the shoulders, neck, hands and lower legs as the clothing requires.
8. **Bone-driven corrective shape keys** for the deformations our rig gets wrong (elbow/knee collapse, shoulder raise, eyelid close, skirt over a raised thigh). Use a linear 0 to 1 mapping on a local-space bone channel:
   ```python
   fc = key_block.driver_add('value'); d = fc.driver
   d.type = 'AVERAGE'
   v = d.variables.new(); v.type = 'TRANSFORMS'
   t = v.targets[0]; t.id = rig; t.bone_target = 'lowerarm_l'
   t.transform_type = 'ROT_X'; t.transform_space = 'LOCAL_SPACE'
   for m in list(fc.modifiers): fc.modifiers.remove(m)
   k0 = fc.keyframe_points.insert(0.0, 0.0); k1 = fc.keyframe_points.insert(math.radians(120), 1.0)
   for k in (k0, k1): k.interpolation = 'LINEAR'
   fc.extrapolation = 'CONSTANT'   # avoid overshoot past full bend
   ```
   Side-split via `key_block.vertex_group = 'left_side'`, with the centre-line vertices at 0.5 in both groups. Note: the course's rotation range ends at the "fully closed" value; we must also clamp (`CONSTANT` extrapolation) so the key never exceeds 1.
9. **Deformation test pose set (automated QA before any film render)**, from his test list plus the brief: jaw open, eyelids closed, fingers curled to a fist, elbow 120°, knee 120°, shoulder abduction 90°, leg lift (skirt clipping). Render a contact sheet of these on every cast change.
10. Viewport speed while scripting/previewing: `scene.render.use_simplify = True; scene.render.simplify_subdivision = 0`, and lower `hair curves display amount` (his values 0.01–0.05). Restore both for the final render.

**Posing / motion (applies to blended Mixamo clips and hand-keyed adjustments)**
11. Every held pose and every keyed adjustment layer must show **contrapposto**: weight on one leg, pelvis tilted down on the free-leg side, shoulders tilted the opposite way. Never parallel hip and shoulder lines, never mirror-identical arms or hands. Script check: `abs(hip_line_angle - shoulder_line_angle)` should be noticeably non-zero and of opposite sign in idle holds.
12. **Balance**: the centre of mass (pelvis/hips projected to the floor) sits over the support foot, or between the feet for a two-foot stance. If an offset or blend moves the hips, re-check that the feet are planted.
13. **Reference first, then exaggerate** a little for the cartoon cast (`cast.CARTOON`). Realistic cast: stay closer to the reference.
14. Save keeper poses as Pose Assets (`bpy.ops.poselib.create_pose_asset`) so shots can reuse them.

**Lighting (adopt as the default character-shot rig, scaled to the scene)**
15. Three-point setup with Area lights. Concrete starting values are **ours, since the course gives no numbers**: key area 1.0 m at ~45° off camera, ~30–45° up, fill area **2–3 m (large)** on the opposite side at roughly 1/4 to 1/3 of key power, rim area narrow (e.g. 0.3 × 2 m), behind and to the side, at 1.5–3× key power, warm orange-red in his example (choose from the shot palette). The fill must not flatten the image; the key must not split the face into two flat halves. Let a little key light wrap onto the far cheek.
16. Separation: a **point light behind the character aimed at the background**, plus light linking so the rim does not hit the background:
    ```python
    rim.light_linking.receiver_collection = coll  # objects in coll, with backdrop set to EXCLUDE
    ```
    (Blender 4.0+, Cycles; EEVEE Next in 4.2+ also supports light linking.)
17. **HDRI only as low-strength ambient** (World background strength well below the key's effect), never as the main light. Choose a neutral one; it must not show a recognisable real location (our project rule).
18. Link the data of duplicated key/fill lights (`light2.data = light1.data`) so one power change adjusts all of them.
19. **Camera**: 80–90 mm for portrait/close-ups (note: our vertical 1080×1920 films need wider lenses for wide shots; use 80–90 mm only for close-ups). Always cut wide shot, close-up, then detail.
20. For any orbit/turntable shot: parent the **camera plus the lights** to one empty and rotate that empty, so the lighting stays fixed relative to the camera. Use **linear** interpolation on the rotation for a constant spin. The course does not say this; Blender's default Bezier gives ease in/out. 24 fps × seconds = frames.
21. Render: Cycles 200–500 max samples at 150% resolution scale (his settings). For EEVEE we keep our own settings. Frame step 1. **PNG sequences** (crash-safe; already our `chain.sh` approach). Test-render random frames before the full sequence.
22. Post: subtle **film grain plus vignette** (plus small temperature/contrast tweaks) makes renders "feel natural ... not so perfect". We can do this in `post.py` (ffmpeg `noise`/`vignette` filters) or in the Blender compositor. Keep it subtle.

---

## 4. What these two chapters do NOT cover (precise)

- **No walk cycles, no character animation, no keyframing of the body.** The only animation is the turntable empty's two rotation keyframes. Posing is static, for still renders only. No timing, spacing, arcs, overlap, follow-through or graph-editor smoothing for motion.
- **No motion capture, no Mixamo, no retargeting, no NLA/action blending.**
- **No IK/FK explanation or switching**, pole vectors or foot-roll mechanics (only heel bone placement). No constraints are taught apart from what Rigify generates.
- **No Auto-Rig Pro or MPFB/MakeHuman workflow.** ARP is mentioned only.
- **No dedicated hand/finger posing guidance** beyond asymmetry. **No gaze/eye-direction posing rules.** **No silhouette discussion.** No facial expression library or lip-sync/visemes (only the jaw open and smile tests).
- **No corrective work for elbows, knees or shoulders** shown. The only correctives are the eyelid shape key and per-pose shape keys on the skirt/boot cages.
- **No cloth simulation, no hair physics/dynamics.** Clothes follow via weights or Surface Deform; hair is rigidly attached to the head. No soft body or bone-based jiggle.
- **No environments or sets** beyond a cyclorama backdrop. No props interaction.
- **No numeric light powers, colour temperatures or HDRI strength values.** **No depth of field.** **No denoiser settings, colour management (Filmic/AgX view transform, Look, exposure) or light-path settings.** **No Blender compositor.** **No EEVEE render settings** (only the passepartout tip). No render passes or AOVs.
- No video post-processing technique (Resolve Color is "beyond the scope"). The lens distortion, chromatic aberration and glow from the slide are not demonstrated.
- The final "cinematic lighting styles" he used for his own finals are **not shown**.
