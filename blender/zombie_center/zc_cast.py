"""THE ZOMBIE CENTER — the permanent cast of this series (separate from the Tolo Travel cast).

    import zc_cast
    arin = zc_cast.spawn("zc_arin")          # same Character API as blender/cast/cast.py

One definition per person = one master look. Never change these values per scene; damage/blood/dirt are
added on top (zombify, paint masks), never by editing the base.
Rules: no hijab, no logos/emblems/insignia on any clothing.
"""
import cast

WARM = cast.WARM
OLIVE = (0.56, 0.41, 0.3)      # tested: visible warm olive under AgX

ZC = {
    "zc_arin": dict(
        fa="آرین", role="Subject 001. 19, lean, black centre-parted hair, dark eyes, small scar at the LEFT eyebrow.",
        gender=1.0, age=0.43, height=0.55, weight=0.42, muscle=0.5, skin="young_caucasian_male", skin_tint=OLIVE,
        hair="short04", hair_col=(0.02, 0.018, 0.018), strand_hair="centre_part",   # short04 = dark scalp layer under the strands
        brow="eyebrow006", brow_col=(0.03, 0.025, 0.022), dark_eyes=True,
        scar="left_brow",
        clothes={"male_casualsuit05": (0.16, 0.17, 0.18), "toigo_ankle_boots_male": (0.12, 0.1, 0.09)}),
    "zc_nika": dict(
        fa="نیکا", role="Subject 002. 16, slight, long loose black hair, pale hospital gown, barefoot, red-thread bracelet.",
        gender=0.0, age=0.37, height=0.35, weight=0.35, muscle=0.3, skin="young_caucasian_female", skin_tint=OLIVE,
        hair="long01", hair_col=(0.035, 0.03, 0.03), brow="eyebrow010", brow_col=(0.04, 0.03, 0.025), dark_eyes=True,
        clothes={"toigo_shift_dress": (0.78, 0.84, 0.86)}),
    "zc_elena": dict(
        fa="دکتر النا", role="Scientist, 48. Dark-blonde jaw-length bob, white lab coat over grey top, dark trousers.",
        gender=0.0, age=0.68, height=0.5, weight=0.45, muscle=0.35, skin="middleage_caucasian_female", skin_tint=WARM,
        hair="bob02", hair_set=(0.5, 0.39, 0.25), brow="eyebrow011", brow_col=(0.3, 0.22, 0.14), dark_eyes=True,
        clothes={"joepal_crude_t-shirt_female": None, "mindfront_female_trousers_1": None,
                 "toigo_ankle_boots_female": (0.1, 0.09, 0.09), "mindfront_cardigan_long_open_front": None},
        flat={"joepal_crude_t-shirt_female": (0.36, 0.37, 0.39), "mindfront_female_trousers_1": (0.12, 0.12, 0.14),
              "mindfront_cardigan_long_open_front": (0.93, 0.93, 0.92)}),
    "zc_sara": dict(
        fa="سارا", role="Survivor, 23. Dark-brown hair in a low ponytail, olive field jacket, black jeans, worn boots.",
        gender=0.0, age=0.48, height=0.48, weight=0.42, muscle=0.45, skin="young_caucasian_female2", skin_tint=(0.68, 0.52, 0.4),
        hair="ponytail01", hair_col=(0.1, 0.06, 0.04), brow="eyebrow009", brow_col=(0.08, 0.05, 0.035), dark_eyes=True,
        clothes={"elvs_hooded_sweat_jacket1": (0.3, 0.33, 0.2), "punkduck_female_tight_jeans": (0.07, 0.07, 0.08),
                 "toigo_ankle_boots_female": (0.22, 0.16, 0.11)}),
    "zc_mark": dict(
        fa="مارک", role="Security guard, 52. Short grey hair, plain dark uniform shirt and cargo trousers, boots. No badges.",
        gender=1.0, age=0.71, height=0.6, weight=0.58, muscle=0.62, skin="middleage_caucasian_male", skin_tint=WARM,
        hair="short04", hair_set=(0.5, 0.49, 0.47), brow="eyebrow006", dark_eyes=True,
        clothes={"elvs_male_shirt_untucked_bd1": (0.1, 0.11, 0.13), "mindfront_male_trousers_2": (0.1, 0.1, 0.11),
                 "culturalibre_male_boots": (0.08, 0.07, 0.07)}),
    "zc_sam": dict(
        fa="سام", role="Survivor, 32, heavy-set delivery driver. Red knit fleece, khaki cargo trousers, grey cap.",
        gender=1.0, age=0.56, height=0.45, weight=0.8, muscle=0.4, skin="young_caucasian_male2", skin_tint=(0.66, 0.5, 0.38),
        hair="short01", hair_col=(0.08, 0.05, 0.04), brow="eyebrow004", dark_eyes=True,
        clothes={"mindfront_knitted_sweater_02": (0.55, 0.12, 0.1), "mindfront_male_trousers_1": (0.45, 0.4, 0.3),
                 "punkduck_comfortable_sneakers": (0.2, 0.2, 0.2), "jujube_newsboy_cap": None},
        flat={"jujube_newsboy_cap": (0.28, 0.28, 0.3)}),
}
cast.CAST.update(ZC)


def spawn(key, **kw):
    ch = cast.spawn(key, **kw)
    finish(ch, ZC[key])
    return ch


def finish(ch, d):
    """The parts of the master look that cast.py doesn't know about (same every time)."""
    import bpy, mpfb_tools as M, zc_look, zc_hair
    if d.get("brow_col"):
        for o in ch.parts.get("Eyebrows", []):
            M.set_color(o, d["brow_col"], keep=0.5)
    for asset, rgb in d.get("flat", {}).items():     # solid colour: no printed patterns / logos survive
        for o in ch.parts.get("by_asset", {}).get(asset, []):
            if not any(ms.material for ms in o.material_slots):     # asset shipped without a material
                m = bpy.data.materials.new(o.name + "_flat"); m.use_nodes = True
                b = m.node_tree.nodes["Principled BSDF"]
                b.inputs["Base Color"].default_value = (*M.lin(rgb), 1); b.inputs["Roughness"].default_value = 0.8
                o.data.materials.clear(); o.data.materials.append(m)
                continue
            M.set_color(o, rgb, keep=0.04)
            for ms in o.material_slots:
                m = ms.material
                if m and m.node_tree:
                    for n in m.node_tree.nodes:
                        if n.type == "BSDF_PRINCIPLED" and not n.inputs["Base Color"].is_linked:
                            n.inputs["Base Color"].default_value = (*M.lin(rgb), 1)
    if d.get("dark_eyes"):
        zc_look.dark_eyes(ch)
    if d.get("scar") == "left_brow":
        zc_look.brow_scar(ch, side=+1)
    if d.get("strand_hair") == "centre_part":
        ch.hair_strands = zc_hair.centre_part_hair(ch)
    for o in ch.parts.get("Clothes", []):          # no plastic shoes / clothes
        for ms in o.material_slots:
            m = ms.material
            if m and m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == "BSDF_PRINCIPLED" and not n.inputs["Roughness"].is_linked:
                        n.inputs["Roughness"].default_value = max(0.55, n.inputs["Roughness"].default_value)
