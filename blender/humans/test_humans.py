import bpy, addon_utils, os, sys, math
from mathutils import Vector
addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.targetservice import TargetService
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
bpy.ops.wm.read_factory_settings(use_empty=True)

def human(name, x, gender, age, skin, hair, brow, clothes, eye="brown", height=0.5):
    m = TargetService.get_default_macro_info_dict()
    m.update(gender=gender, age=age, height=height, weight=0.45, muscle=0.45)
    m["race"] = {"asian": 0.15, "caucasian": 0.65, "african": 0.2}
    b = HumanService.create_human(macro_detail_dict=m)
    b.name = name
    HumanService.set_character_skin(f"{A}/skins/{skin}/{skin}.mhmat", b, skin_type="ENHANCED_SSS")
    add = lambda p, t: HumanService.add_mhclo_asset(p, b, asset_type=t, subdiv_levels=1, material_type="MAKESKIN")
    add(f"{A}/eyes/high-poly/high-poly.mhclo", "Eyes")
    add(f"{A}/eyebrows/{brow}/{brow}.mhclo", "Eyebrows")
    add(f"{A}/eyelashes/eyelashes01/eyelashes01.mhclo", "Eyelashes")
    add(f"{A}/teeth/teeth_base/teeth_base.mhclo", "Teeth")
    add(f"{A}/hair/{hair}/{hair}.mhclo", "Hair")
    for c in clothes:
        f = [x for x in os.listdir(f"{A}/clothes/{c}") if x.endswith(".mhclo")][0]
        add(f"{A}/clothes/{c}/{f}", "Clothes")
    for o in bpy.data.objects:
        if o.parent is None and o.type == "MESH" and o.name == name:
            o.location.x = x
    for o in bpy.data.objects:
        if o.type == "MESH" and ("hair" in o.name.lower() or "brow" in o.name.lower()):
            for ms in o.material_slots:
                if ms.material and ms.material.node_tree:
                    for n in ms.material.node_tree.nodes:
                        if n.type == "TEX_IMAGE":
                            mix = ms.material.node_tree.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
                            mix.inputs[0].default_value = 1.0; mix.inputs[7].default_value = (0.18, 0.11, 0.07, 1)
                            outs = [l for l in ms.material.node_tree.links if l.from_node == n and l.from_socket.name == "Color"]
                            for l in outs:
                                ms.material.node_tree.links.new(mix.outputs[2], l.to_socket)
                            ms.material.node_tree.links.new(n.outputs["Color"], mix.inputs[6])
    return b

human("Arian", -0.45, 1.0, 0.42, "young_caucasian_male", "short02", "eyebrow001",
      ["elvs_crude_t-shirt_male", "cortu_cargo_pants", "shoes01"], height=0.6)
human("Mahsa", 0.45, 0.0, 0.42, "young_caucasian_female", "ponytail01", "eyebrow010",
      ["toigo_basic_tucked_t-shirt", "toigo_wool_pants", "toigo_flats"], height=0.45)

sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = 64; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1080
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.65, 0.7, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
for loc, e in (((2, -3, 3), 400), ((-3, -2, 2), 150), ((0, 3, 3), 200)):
    bpy.ops.object.light_add(type="AREA", location=loc); l = bpy.context.object
    l.data.energy = e; l.data.size = 2
    l.rotation_euler = (Vector((0, 0, 1.4)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
bpy.ops.mesh.primitive_plane_add(size=20)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam

def shot(path, loc, target, lens):
    cam.location = loc; cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)

out = sys.argv[-1]
for o in bpy.data.objects:
    if o.type == "MESH" and o.name in ("Arian", "Mahsa"): print(o.name, [round(v, 2) for v in o.dimensions])
shot(f"{out}/full.png", (0, -4.2, 1.0), (0, 0, 0.85), 40)
def top(n):
    o = bpy.data.objects[n]; return max((o.matrix_world @ v.co).z for v in o.data.vertices)
for n, x in (("Arian", -0.45), ("Mahsa", 0.45)):
    z = top(n) - 0.12 if n == "Arian" else bpy.data.objects[n].dimensions.z * 0.935
    shot(f"{out}/face_{n.lower()}.png", (x + 0.15, -0.75, z + 0.02), (x, 0, z), 75)
bpy.ops.wm.save_as_mainfile(filepath=f"{out}/test_humans.blend")
