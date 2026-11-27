# Notes — Masterclass ch. "Shading & Texturing" (Kenny Praise), file 09_shading.txt

**Coverage: read 100% of the file** — all 138,890 characters, in six slices (0–25k, 25k–50k, 50k–75k, 75k–100k, 100k–125k, 125k–end). Timestamps run [14:25:03] → [17:25:02]; the last line is the start of chapter 12 (rigging).
**Note:** [15:25:39]–[16:22:50] (about 57 min) is a **time-lapse of texture painting with music only**. The transcript has no narration there (just "[music] Oh. Heat."), so nothing was taught in that stretch.

**What the chapter does NOT cover (so don't attribute it to him):** colour management / view transform (Filmic/AgX) is never mentioned. Freckles and pores are never mentioned as such: skin "bumpiness" comes from a noise-driven Bump. He doesn't hand-build an eye refraction setup beyond a transmissive cornea sphere, and doesn't do catch-lights. Lips get no material of their own, only a vertex-colour mask that excludes them from colour variation and roughness. No metal or leather node trees are built by hand: leather comes from a Poly Haven PBR texture, and metal is just Principled metallic plus low roughness. He gives no specular numbers except iris specular = 0. Redness on cheeks is only mentioned as a colour palette swatch for hand painting ("a reddish color for the cheeks"). Nose and ears are not mentioned.

---

## 1. Workflow in order (with timestamps)

| Time | Step |
|---|---|
| 14:25:51 | Definitions. **Texturing** = "the process of applying images onto a 3D model" (base colour, roughness map, scratches, logos). **Shading** = "how a material is going to react to light" (shiny, rough, transparent). "Shading can work with textures, but it can also work without textures." |
| 14:28:01 | **3-step workflow**: (1) **Material blockout**: simple colours plus basic roughness and specular, so "we can tell exactly what each part of the character is supposed to be". (2) **Create textures**: paint them, bake them, use PBR maps, or vertex paint. (3) **Enhance with procedural shading**: nodes to "add sort of variation, break things up". |
| 14:29:37 | PBR = physically based rendering. Map set: base colour, roughness, metallic, normal, emission, AO. Why use it: consistent under any lighting, industry standard (exports to Unreal/Maya/3ds Max), widely available online. |
| 14:30:56 | **What makes a good material**: it "should tell a little bit of a story" (worn or new, clean or rough). "Avoid materials that feel too flat and too generic. If everything has the same roughness, the same color, no variation, your character is going to look very boring." Don't leave "a flat principled BSDF node". |
| 14:32:02 | Add-ons: Node Wrangler (built in, needed for Ctrl+Shift+LMB preview and Ctrl+T), the Poly Haven add-on (used in this chapter), BlenderKit (similar), Ucupaint (layer painting, not used here). |
| 14:34:42 | **File cleanup before shading**. Delete the high-poly hierarchy (save a backup first). Naming follows the Blender Studio convention: collections `CH_Jenny`, `CH_Jenny_clothes`, `CH_Jenny_hair`; mesh objects prefixed `GEO_Jenny_`; curve objects `CRV_` (he says "CUV"); lashes renamed upper/lower lashes. Batch rename with Ctrl+F2 (find/replace, then set name with a prefix). The character name goes in the prefix so meshes don't collide when appending into other files. Geometry Nodes node groups are renamed to the object name. **Object data name = object name** (he uses a small script for meshes and renames curves by hand). Unused vertex groups are deleted; the one the hair GN uses stays and is locked. |
| 14:43:46 | **Viewport performance for hair**. Expose the Interpolate Hair Curves "viewport amount" on the GN group input. On the main hair, "Copy as New Driver", then "Paste Driver" onto the other hair objects, so one slider (e.g. 0.1) controls all of them. |
| 14:46:27 | Remove the UV checker material. Add a new material and use "Copy Material to Selected". Hide the hair scalp meshes in viewport and render (the hair stays visible). |
| 14:47:46 | **Material blockout**. One material per part, named with the character prefix: `Jenny_skin`, `Jenny_brows_lashes` (shared by brows and both lash curves), `Jenny_shirt`, `Jenny_skirt`, `Jenny_boots`, `Jenny_boots_metal` (assigned to faces in edit mode), `Jenny_necklace`, `Jenny_hair`, `hairband` (shirt colour), `Jenny_gums`, `Jenny_teeth`, `Jenny_tongue` (three slots on one mouth object, assigned per face selection). Colours are eyedropped from a concept colour sheet opened in the Image Editor. |
| 14:55:17 | Switch to **Cycles, GPU**. Rendered view with Scene Lights and Scene World turned off, so the built-in HDRI is used. Teeth/gums/tongue subsurface. Skin colour tweaked (more saturation). |
| 14:56:35 | **Eye blockout**: three material slots on the eyeball, `Jenny_eye_sclera`, `Jenny_eye_iris`, `Jenny_eye_pupil`, assigned by face loops (Ctrl+numpad-plus grows the selection out from the pupil). |
| 14:58:41 | **Hair root-to-tip gradient** (Curve Info → Intercept). Then Principled Hair BSDF for Cycles and Principled BSDF for EEVEE, using two Material Output nodes. |
| 15:03:45 | Eyebrows: same dual-output Hair BSDF setup. |
| 15:04:33 | **Procedural iris** (three gradient layers), pupil, sclera. |
| 15:12:48 | **Cornea** as a separate sphere: transmission glass, shadows off, EEVEE raytracing settings. Mirror to make L/R. |
| 15:18:14 | **Texture painting**: workspace walkthrough (4K image, palettes, face-mask painting, the blur trick). |
| 15:25:39–16:22:50 | Time-lapse painting with no narration. Result: colour maps for the skin, shirt, skirt and "trousers". |
| 16:22:50 | **Baking**: pointiness map (Cycles Geometry node → Emission bake), then normal maps from Multires. |
| 16:33:04 | **Shirt**: painted colour × pointiness, then overlay with a Poly Haven fabric PBR. Two normals combined with Vector Math Add → Normalize. |
| 16:39:09 | **Skirt**: pointiness and normal bake (including strap objects with Clear Image unchecked). |
| 16:46:58 | **Boots**: pointiness and normal bake. Common baking errors. Then Poly Haven "brown leather" PBR. |
| 16:55:33 | Skirt gets the fabric PBR (same one as the shirt). |
| 16:58:00 | **Procedural tongue and gums** (Voronoi bump, roughness from Voronoi × Noise). Teeth stay plain white plus clearcoat. |
| 17:04:11 | **Skin shader**: pointiness bake, tattoo layer, Layer Weight rim vibrance, two procedural colour-variation layers, a vertex-colour mask for the lips/mouth, roughness and bump from noise, subsurface Random Walk (Skin). |
| 17:23:57 | Summary. |

---

## 2. Concrete techniques and values

### 2.1 Basic blockout values
- **Boots metal** [14:51:04]: "turn off the metallic and also just turn down the roughness". He literally says "turn off" (probably a slip for "turn on", but it isn't clear).
- **Necklace** [14:51:20]: "make this metallic and also reduce the roughness". No numbers given.
- **Gums**: "a little bit more reflective", i.e. reduce roughness. Subsurface weight increased "not too much".
- **Teeth** [14:54:29]: "definitely drop down the roughness so that we have really shiny teeth". **Coat weight = 1.0**: "add another clear coat of just shine on top of the teeth". Small subsurface weight.
- **Tongue** [14:56:03]: **subsurface ≈ 0.5** ("Something around .5 should be just fine for the tongue"). A red base colour, to be painted later.
- **Sclera** [14:58:11]: pure white, roughness reduced ("reduce the roughness about one" is garbled). Later he takes "the roughness down" again [15:12:48].

### 2.2 Hair and brows/lashes [14:58:41–15:04:16]
- **Root-to-tip darkening**: `Curve Info.Intercept` → `ColorRamp` (for contrast) → `Mix Color` with **blend = Multiply, Factor = 1.0**. A = the ramp, B = an RGB/Color node holding the hair colour. The concept has a darker root that gets lighter toward the tip.
- **Principled Hair BSDF** (Cycles) takes the mixed colour in its Color input. "The principled hair BSDF just looks really good." He changes "really nothing much" on it.
- **EEVEE vs Cycles**: "this principled hair BSDF doesn't really work well inside of Eevee". He uses **two Material Output nodes**: one with target = Cycles fed by the Hair BSDF, and a duplicate with target = EEVEE fed by a regular Principled BSDF, "so that we can still preview the hair in Eevee". The final render is in Cycles.
- **Brows/lashes**: the same dual-output setup. The colour is copied (Ctrl+C/Ctrl+V on the colour field) from the Principled BSDF into the Hair BSDF.

### 2.3 Eye shading [15:04:33–15:18:14]
**Iris (all procedural, UV-based):**
1. Re-unwrap the iris faces (Minimum Stretching) so the iris sits in the UV centre. Scale the unused part of the eye UVs down out of the way.
2. **Layer A, rings**: `Texture Coordinate(UV)` → `Mapping` (Location X = −0.5, Y = −0.5, "to make sure that our texture coordinate is actually at the middle of the UVs") → `Gradient Texture` (**Spherical**) → `ColorRamp` (interpolation **Ease**, his preferred). Stops: an outer black stop (a "nice falloff around the pupil"), the iris colour, and a lighter variant of the iris colour.
3. **Layer B, radial fibres**: duplicate the coordinate/mapping/gradient and switch the gradient to **Radial** → `Noise Texture` (use the **Fac** output, scale increased) → `Mix Color` **Soft Light** (A = layer A colour, B = noise). "That looks a lot more vibrant for the eye."
4. **Layer C, top darkening**: duplicate and switch the gradient to **Linear** → new `ColorRamp` (Ease). Rotate the iris UVs so "the top half is the darker portion". → `Mix Color` **Multiply, Factor 1.0**. Lighten the ramp's dark stop if the top shouldn't go fully black.
5. The result goes into Principled Base Color with **Roughness = 1.0** and **Specular = 0** ("so that we don't really have light interacting with this"). The cornea supplies the shine.

**Pupil**: no light interaction. Either an empty material (Material Output only) or an **Emission shader set to black**.

**Cornea** [15:12:48]:
- A separate **UV sphere** created at the eyeball centre (3D cursor → selected), scaled to envelop the eyeball, shaded smooth, named `GEO_Jenny_eye_cornea`. The eyeball is parented to the cornea.
- Material `Jenny_eye_cornea`: Principled BSDF with **Roughness = 0** and **Transmission = 1.0** ("that reflective layer above the eye").
- **Object Properties → Visibility: shadows off**. Otherwise the cornea casts a shadow on the eyeball, "especially in cycles that's going to be really prominent".
- **EEVEE**: turn on render **Raytracing** (he says "R3C"), and in Material → Settings turn on **Raytrace Transmission**. Set **Thickness = 0**: "if I just increase... thickness is increasing which is making it refract in weird ways".
- Left/right: remove the mirror modifier, suffix the names `_L`, apply all transforms, duplicate, Ctrl+M then X with the pivot at the 3D cursor at world origin, apply transforms, Shift+N to recalculate normals, then batch rename `_L` → `_R` and fix the data names.
- No catch-light setup is built. Highlights come from the transmissive cornea plus the HDRI.

### 2.4 Texture painting [15:18:14–15:25:39]
- Image Texture → New: name e.g. `Jenny_skin_color_map`, **4K** (he multiplies the default 1024 by 4 for both sides), and the **fill colour = the base skin colour** (copied from the Principled base colour). "Save your file into a textures folder" as soon as you create a new image.
- Viewport Solid → Color: **Texture**, to see it in solid mode. In Texture Paint mode, set the texture slot mode to **Material** and pick the right image.
- Paint in the 3D viewport or in the Image Editor in Paint mode. He uses both: paint in 3D, clean up in 2D. X symmetry on or off as needed.
- **Color palette** "skin": base, a highlight shade, a darker shade, "a reddish color for the cheeks". Enable the **Fake User** so the palette survives a restart. Make palettes for clothes too.
- **Fill (bucket) tool** to fill the whole object.
- **Face selection masking**: select faces in edit mode, then turn on paint mask "face selection" so only those faces take paint.
- Warnings: "if you use a big brush size, the texture painting is going to get slow... texture painting in Blender is not the best". The Blur brush "doesn't work really nicely". His blur method: paint over edges with a **low strength** brush, or hold Shift to switch to blur temporarily.
- Paint tattoos on a **separate layer image** (see 2.7). Don't put them in the colour map.

### 2.5 Baking: pointiness and normal maps [16:22:50–16:52:21]
**Pointiness (a cavity/curvature-like map):**
- Shader Editor `Geometry` node (not GN) → **Pointiness** → `ColorRamp` with the black stop at about **0.45** and the white stop at about **0.5–0.55** (skin: black crunched in, white about 0.5; later "4", likely 0.4). "Make sure you're in cycles... This geometry node only works in cycles."
- Bake target: a new Image Texture (4K, black), e.g. `Jenny_shirt_pointiness_map`, **Color Space = Non-Color** ("this does not have any color information").
- Render Properties → Bake → **Bake Type = Emission**: "anything that's plugged into the surface" gets baked, so preview the pointiness chain to the output first. Select the object and the target image node, then Bake (about 10 s). Save the image (Alt+S) into the textures folder.
- For additional objects sharing a map (straps): **uncheck Clear Image** so the existing bake isn't erased.
- "For some reason the first [bake] just failed for no reason... just go ahead and bake again. That's completely normal inside Blender."
- **Usage**: `Mix Color` **Multiply**, A = painted colour map, B = baked pointiness, **Factor ≈ 0.3** (shirt). For the skin he increases it "somewhere around here". "Those lighter parts [get] lighter... darker parts darker."

**Normal map from Multires:**
- "If your character is going to be used completely inside of Blender, you don't need to bake normal map." This is for export or for getting rid of Multires.
- Steps: disable Multires in the viewport, then Multires → Shape → **Apply Base** (he says "conform base"). Bake Type = **Normal**, target image Non-Color (e.g. `Jenny_shirt_normal_map`), Bake. Save, delete Multires, add Subdivision Surface instead. Then `Normal Map` node (Color → Color, Normal → Principled Normal).
- **Common errors he shows**: (1) a **Mirror modifier left on** ruins the bake, so disable it, "you also want to disable it in the render. That's actually more important than disabling it in the view port". (2) Straps baked into the same map leave black areas where the normals are unknown, so re-bake with **Clear Image checked**. Afterwards join objects that share identical modifiers (Ctrl+J).
- Fix clipping after the swap in sculpt mode with the Grab brush and X symmetry.

### 2.6 Clothes with PBR textures (Poly Haven)
- Asset Browser → Poly Haven → Textures, search "fabric" or "leather". Test on a smooth UV sphere first. Pick a resolution in the material panel (1K/2K/4K/8K; **2K** "is going to be just fine").
- Don't drop the asset on the garment (it replaces the material). Instead **copy the PBR nodes (everything except the Material Output) and paste them into the garment's material**.
- **Shirt fabric**: a Poly Haven fabric ("Telea/Telena"-like name, garbled). **Skirt**: the same fabric. **Boots**: "brown leather". Delete the displacement node ("we are not really going to be using displacement").
- **Colour**: `Mix Color` **Overlay**, A = (painted map × pointiness), B = PBR base colour. **Factor ≈ 0.3** for the shirt, **≈ 0.2** for the boots, **≈ 0.2–0.3** for the skirt. Raise the PBR Mapping **scale** so the weave is finer.
- **Two normals**: `Vector Math (Add)` (baked Normal Map output + PBR Normal Map output) → `Vector Math (Normalize)` → Principled Normal. Without Normalize "this part becomes really light". Normalize "just evens everything out".
- He plans a separate material for part of the shoe "so that it's not completely the same material for every part".

### 2.7 Tongue and gums (procedural) [16:58:00–17:03:55]
- `TexCoord(UV)` → `Mapping` → **Voronoi** (scale raised a lot) → `ColorRamp` (crunched) → **Bump** (Height). Bump → Principled Normal. **Invert** the bump so the papillae come out, not in. Strength reduced.
- Colour: an RGB node with the base colour, then `Mix Color` with Fac = Voronoi ramp, A = colour, B = colour through **Hue/Saturation/Value** (Value lowered, Saturation adjusted, Hue "very slightly"). Then Base Color.
- Roughness: **Noise** (same coordinates, high scale, Detail raised, **Roughness ≈ 0.6**) × Voronoi via `Mix Color` **Multiply, Factor ≈ 0.5**. Optional ColorRamp → Principled Roughness.
- Gums: the same node group pasted in, gum colour, Voronoi scale raised.
- Teeth: left white. Optional painted yellowing near the top "later".

### 2.8 Skin shader [17:04:11–17:23:57]
Built in this order (the colour chain is grouped as "color map"):
1. **Painted skin colour map × baked pointiness** (`Mix Color` Multiply, factor adjusted by eye).
2. **Tattoo layer**: new image `Jenny_skin_tattoo` with the fill colour's **alpha = 0** (transparent). Paint on it, then `Mix Color` with **Fac = image Alpha**, A = skin map, B = tattoo Color. "Just in case you have tattoos on your character and you don't want to mess up your base color map." Muted for now.
3. **Rim vibrance with Layer Weight**: `Layer Weight` → **Facing**, Blend lowered → `ColorRamp` (interpolation **B-Spline**, flipped: white at the left, black at the right, with an extra black stop) → `Mix Color` **Soft Light**, A = colour map, B = ramp. "Making this outer part of the character a lot more vibrant."
4. **Colour variation 1**: `TexCoord(UV)` → `Mapping` → **Noise** (scale "really high") → `ColorRamp` (black stop pulled in) → `Mix Color` with Fac = ramp, A = colour map, B = colour map → **Hue/Saturation/Value** (Saturation up, Value down). Black areas keep the base colour; white areas get the variant. Put it in a frame named "color variation 1".
5. **Colour variation 2**: same idea with **Voronoi** (scale about **190**), ramp **flipped** so white = variant, chained after variation 1 (A = variation 1 output, B = the same HSV). Too intense? Move the ramp's white stop toward black. Frame "color variation 2".
6. **Mouth/lips mask from a vertex colour**: Vertex Paint → Object Data → Color Attributes, new attribute "color variation mask". Fill white (Ctrl+X fills), then in edit mode select the lips and inner mouth, turn on paint mask, and paint them **black**. In shaders, `Color Attribute` node → `Mix Color` Fac. Arrange it so black = unaffected (he swaps A/B to fix an inversion). Applied to both variation layers.
7. **Roughness**: from the variation-1 Noise Fac → `ColorRamp` (default) → Principled Roughness. Lips: the vertex mask mixes in a black value there, so "the lips is completely glossy". Move it toward white for less gloss.
8. **Bump**: duplicate the ramp with **Ctrl+Shift+D** (keeps the input link from the noise) → `Bump` Height → Principled Normal. Strength reduced ("I don't want it to be too intense"). No bump on the lips. "Now this is starting to look like skin."
9. **Subsurface** [17:23:09]: **Method = Random Walk (Skin)** ("the subsurface method that I find works best for the skin"). **Weight ≈ 0.5**. In Cycles "some of the parts are turning whitish", fixed by lowering **Scale to 0.01**. Then "for the subsurface, I'm just going to keep this about five". That's ambiguous: probably weight about 0.5, but it could mean scale 0.05. Radius is never touched (Blender default 1.0, 0.2, 0.1).
- Specular and IOR for the skin are not discussed.

### 2.9 EEVEE vs Cycles (everything he says)
- The final render is Cycles on GPU, previewed in Rendered view with the built-in HDRI (Scene Lights and Scene World off).
- Principled Hair BSDF is poor in EEVEE, so use dual Material Outputs (target Cycles / target EEVEE).
- The Geometry node's Pointiness works **only in Cycles**, so bake it to an image for EEVEE or for export.
- The cornea in EEVEE needs scene Raytracing, material Raytrace Transmission and Thickness = 0. In Cycles, turn off the cornea's shadow visibility.
- Random Walk (Skin) SSS turns whitish in Cycles at the default scale, so lower the scale (0.01).

### 2.10 Warnings and common mistakes (summary)
- Flat, uniform materials look "very boring". Add story and variation.
- Material preview lags with dense hair, so use a driver-linked viewport amount (0.1).
- Big brushes slow texture painting. The Blur brush is weak.
- Set baked data maps to **Non-Color**.
- Select the object **and** the target image node before baking, or Blender errors.
- Bakes sometimes fail randomly, so re-bake.
- Disable the Mirror modifier (especially for render) before a normal bake.
- Use Clear Image off to add to a bake, and on to avoid black holes.
- Normalize after adding two normal vectors.
- Don't drag a Poly Haven material onto the garment. Copy its nodes in instead.
- Cornea shadows and thickness.
- Name materials with the character prefix so appended characters don't clash.

---

## 3. Applicable to a scripted bpy pipeline

All of these are buildable procedurally. Node type identifiers are given for Blender 4.x. Values are his, or marked "by eye" where he gave none.

**A. Naming and housekeeping**
- Materials `"{char}_skin"`, `"{char}_eye_iris"`, etc. Objects `GEO_{char}_*`, curves `CRV_{char}_*`. Set `obj.data.name = obj.name` for every object (his helper script). Remove unused vertex groups.
- Hair performance: drive every hair GN modifier's viewport-amount input from one master property (`driver_add` on the modifier input, var = the master's input).

**B. Hair / brows / lashes**
```
CurveInfo(ShaderNodeHairInfo).Intercept -> ValToRGB -> MixRGB(ShaderNodeMix, data_type='RGBA', blend_type='MULTIPLY', Factor=1.0, B=hair_rgb)
  -> ShaderNodeBsdfHairPrincipled.Color -> OutputMaterial(target='CYCLES')
  -> ShaderNodeBsdfPrincipled.Base Color -> OutputMaterial(target='EEVEE')
```
(`ShaderNodeOutputMaterial.target` = 'CYCLES' / 'EEVEE' / 'ALL'.) This fits our EEVEE pipeline: the EEVEE output feeds a Principled BSDF, or the toon shader in our comic style.

**C. Iris** (needs iris UVs centred on (0.5, 0.5); alternatively use Object/Generated coordinates scripted around the iris centre)
```
TexCoord.UV -> Mapping(Location=(-0.5,-0.5,0)) -> TexGradient(gradient_type='SPHERICAL') -> ValToRGB(interpolation='EASE'; stops: dark->iris->lighter iris->black at outer)
TexCoord.UV -> Mapping(-0.5,-0.5) -> TexGradient('RADIAL') -> TexNoise(scale high).Fac
  Mix(RGBA, 'SOFT_LIGHT', A=rings, B=noise)
TexCoord.UV -> Mapping -> TexGradient('LINEAR') -> ValToRGB(EASE)  [UVs rotated so top = dark]
  Mix(RGBA, 'MULTIPLY', Factor=1.0, A=prev, B=topmask)
-> Principled(Base Color, Roughness=1.0, Specular IOR Level=0.0)
```
- Pupil: `ShaderNodeEmission(Color=black)` or an empty output. Sclera: white, low roughness.
- **Cornea**: UV sphere around the eyeball, parented. Principled with Roughness 0 and Transmission Weight 1.0. `obj.visible_shadow = False`. EEVEE Next: `scene.eevee.use_raytracing = True`, `mat.use_raytrace_refraction = True` (4.2+ name), `mat.thickness_mode`/thickness = 0 (in 4.2+, set the Material Output Thickness input to 0). Mirror via a scripted duplicate plus scale −1 X, apply, recalculate normals, rename `_L`→`_R`.

**D. Mouth**
- Teeth: Principled, low roughness, **Coat Weight 1.0**, small Subsurface Weight.
- Gums: lower roughness, small SSS.
- Tongue: SSS weight **0.5**, plus the procedural chain:
```
TexCoord.UV -> Mapping -> TexVoronoi(scale high) -> ValToRGB -> Bump(invert=True, Strength low) -> Principled.Normal
ValToRGB -> Mix(RGBA,'MIX', Factor=ramp, A=base_rgb, B=HueSat(base_rgb, Value<1, Hue~0.5±small)) -> Base Color
TexNoise(scale high, Detail up, Roughness 0.6) x Voronoi ramp : Mix(RGBA,'MULTIPLY',0.5) -> [ValToRGB] -> Principled.Roughness
```

**E. Skin** (procedural layers can run with no painted map: use an RGB node as the "color map")
```
base = Image(skin_color_map) or RGB(skin)
[Optional] base = Mix(MULTIPLY, Fac~0.3, A=base, B=Image(pointiness, Non-Color))
[Optional tattoo] base = Mix(MIX, Fac=Image(tattoo).Alpha, A=base, B=Image(tattoo).Color)
rim  = LayerWeight.Facing (Blend lowered) -> ValToRGB(B_SPLINE, flipped: white->black)
base = Mix(SOFT_LIGHT, Fac by eye, A=base, B=rim)
n1   = TexNoise(UV, scale very high) -> ValToRGB(black stop pulled in)
v1   = Mix(MIX, Fac=n1, A=base, B=HueSat(base, Saturation>1, Value<1))
v2r  = TexVoronoi(UV, scale ~190) -> ValToRGB (flipped; white stop toward black to soften)
v2   = Mix(MIX, Fac=v2r, A=v1, B=HueSat(...))
mask = ShaderNodeVertexColor(layer_name="color variation mask")   # black on lips/mouth
v1,v2 gated by Mix(MIX, Fac=mask, A=unvaried, B=varied)
Roughness = Mix(Fac=mask, A=0.0/low (lips glossy), B=ValToRGB(n1 Fac))
Normal    = Bump(Height=ValToRGB(n1 Fac) copy, Strength low; mask out lips)
Principled: subsurface_method='RANDOM_WALK_SKIN', Subsurface Weight ~0.5, Subsurface Scale 0.01
```
- The vertex colour mask can be written from a script: create `mesh.color_attributes.new("color variation mask", 'BYTE_COLOR', 'CORNER')`, fill white, and paint black on lip faces chosen by a vertex group or by face selection. On MPFB bodies, a lip/mouth vertex group or a material slot could select those faces.
- Note: `RANDOM_WALK_SKIN` is a Cycles method. In EEVEE, SSS uses the radius/scale, and the method enum is ignored.

**F. Baking** (bpy: `bpy.ops.object.bake(type='EMIT')` / `type='NORMAL'`)
- Pointiness: `ShaderNodeNewGeometry.Pointiness` → ValToRGB (0.45/0.5) → Emission/output. Create a Non-Color image (`img.colorspace_settings.name = 'Non-Color'`), make its node active (`nodes.active = img_node`), select the object, `scene.render.engine='CYCLES'`, `scene.render.bake.use_clear = True/False`, bake, `img.save()`. This brings the cavity look into EEVEE, where Pointiness doesn't exist.
- Normal from Multires: `scene.render.use_bake_multires = True` with `bake_type='NORMALS'` (the old Multires bake), or the Selected-to-Active route. Disable the Mirror modifier for render first.

**G. Clothes from PBR sets**
```
painted*pointiness (Mix MULTIPLY ~0.3)
 -> Mix(RGBA,'OVERLAY', Factor 0.2-0.3, A=that, B=Image(pbr_diff, sRGB))
 -> Principled.Base Color
Image(pbr_rough, Non-Color) -> Roughness ; Image(pbr_nor, Non-Color) -> NormalMap
VectorMath('ADD', NormalMap_baked.Normal, NormalMap_pbr.Normal) -> VectorMath('NORMALIZE') -> Principled.Normal
Mapping.Scale raised for finer weave; no displacement
```
- For our no-logo rule, use only plain fabric/leather PBRs (no printed patterns tying a shot to a place).
- Metal accessories: Principled Metallic 1.0, low roughness (he gives no exact numbers).

**H. Scene / render notes to carry over**
- Look-dev in rendered view with an HDRI (Scene World off). Final in Cycles GPU for his realistic-stylised look. For our EEVEE comic pipeline, use the dual-output trick so Cycles-only nodes (Hair BSDF, Pointiness) don't break EEVEE.
- He never talks about colour management, so no guidance comes from this chapter.
