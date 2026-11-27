"""Render-speed benchmark: one realistic cast character in a lit corridor with fog, EEVEE vs Cycles, 1920x1080."""
import bpy, math, time, os, json
import cast
HERE = os.path.dirname(os.path.abspath(__file__))
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
ch = cast.spawn("me")                       # hero quality realistic character
ch.rig.location = (0, 0, 0)
def box(loc, sc_, col):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.scale = sc_
    m = bpy.data.materials.new("m"); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*col, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
    o.data.materials.append(m); return o
box((0, 0, -0.05), (2, 8, 0.05), (0.2, 0.2, 0.22)); box((-2, 0, 1.5), (0.05, 8, 1.6), (0.5, 0.52, 0.55))
box((2, 0, 1.5), (0.05, 8, 1.6), (0.5, 0.52, 0.55)); box((0, 0, 3.1), (2, 8, 0.05), (0.4, 0.4, 0.4))
for y in (-4, 0, 4):
    l = bpy.data.lights.new("p", "AREA"); l.energy = 250; l.size = 1.2; l.color = (0.8, 0.9, 1.0)
    o = bpy.data.objects.new("p", l); o.location = (0, y, 3.0); sc.collection.objects.link(o)
r = bpy.data.lights.new("red", "POINT"); r.energy = 150; r.color = (1, 0.1, 0.05)
o = bpy.data.objects.new("red", r); o.location = (1.5, 3, 2.2); sc.collection.objects.link(o)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
vol = w.node_tree.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = 0.02
w.node_tree.links.new(vol.outputs[0], w.node_tree.nodes["World Output"].inputs["Volume"])
cd = bpy.data.cameras.new("c"); cd.lens = 40; cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam)
cam.location = (0.4, -3.2, 1.55); cam.rotation_euler = (math.radians(88), 0, math.radians(7)); sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
res = {}
def go(tag):
    sc.render.filepath = os.path.join(HERE, "test", f"bench_{tag}.png")
    t = time.time(); bpy.ops.render.render(write_still=True); res[tag] = round(time.time() - t, 1)
import sys
sc.render.engine = "BLENDER_EEVEE"
for (w,h,s) in [(1280,720,8),(960,540,8),(1280,720,16)]:
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.eevee.taa_render_samples = s
    go(f"eevee_{h}p_{s}")
print("BENCH", json.dumps(res)); sys.exit(0)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32
try: sc.eevee.use_volumetric_shadows = True
except Exception: pass
go("eevee_32"); go("eevee_32_warm")
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 32; sc.cycles.use_denoising = True
go("cycles_32")
print("BENCH", json.dumps(res))
