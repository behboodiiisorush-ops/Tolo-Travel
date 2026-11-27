"""Radiation masks for «پناهگاه ۳» (the user: everyone on the rescue bus wears a mask, the air is still radioactive).
A respirator (half-face cup + two filter cartridges + strap) or a plain dust mask, parented to the head bone so it
follows every head turn.  Head-bone space: X = right, Y = up (along the bone), Z = forward (out of the face).
Only mouth and nose are covered; no logos or emblems."""
import bpy, math
from mathutils import Vector
import props as P

FIT = {"lena": (0.0, 0.0, 0.0)}   # per-character nudges (up, forward, scale) if a face needs it


def _sphere(r, m, name, scale):
    o = P.sphere((0, 0, 0), r, m, name, scale=scale)
    return o


def _attach(o, rig, loc, rot=(0, 0, 0)):
    o.parent = rig
    o.parent_type = "BONE"
    o.parent_bone = "head"
    L = rig.data.bones["head"].length
    o.location = Vector(loc) - Vector((0, L, 0))       # bone parenting is relative to the bone tail
    o.rotation_euler = rot


def mask(rig, kind, mats, who=""):
    """kind 'resp' (respirator) or 'dust'.  Returns the created objects."""
    s = rig.data.bones["head"].length / 0.16                 # child heads are smaller
    du, df, ds = FIT.get(who, (0.0, 0.0, 0.0))
    s *= 1 + ds
    up, fw = (-0.028 + du) * s, (0.07 + df) * s
    objs = []
    if kind == "resp":
        cup = _sphere(0.062 * s, mats["mask"], f"Mask {rig.name}", (1.0, 0.95, 0.9))
        _attach(cup, rig, (0, up, fw))
        objs.append(cup)
        for side in (-1, 1):
            c = P.cyl((0, 0, 0), (0, 0, 0.032 * s), 0.026 * s, mats["filter"], f"Mask filter {rig.name} {side}")
            _attach(c, rig, (side * 0.05 * s, up - 0.012 * s, fw + 0.02 * s),
                    (0, side * math.radians(55), 0))
            objs.append(c)
        v = P.cyl((0, 0, 0), (0, 0, 0.012 * s), 0.016 * s, mats["filter"], f"Mask valve {rig.name}")
        _attach(v, rig, (0, up - 0.02 * s, fw + 0.05 * s), (math.radians(20), 0, 0))
        objs.append(v)
    else:
        cup = _sphere(0.06 * s, mats["dust"], f"Dust mask {rig.name}", (1.05, 0.9, 0.85))
        _attach(cup, rig, (0, up, fw - 0.004 * s))
        objs.append(cup)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.085 * s, minor_radius=0.006 * s)
    t = bpy.context.object
    t.name = f"Mask strap {rig.name}"
    t.data.materials.append(mats["filter"])
    _attach(t, rig, (0, up + 0.025 * s, 0.0), (math.radians(90), 0, 0))
    t.scale = (1.0, 1.15, 1.0)
    objs.append(t)
    return objs


def follow(objs, body, frame_on):
    """mask visible only while the character's body is rendered and from frame_on on (driver on hide_render)"""
    for o in objs:
        o.hide_render = False
        d = o.driver_add("hide_render").driver
        d.type = "SCRIPTED"
        v = d.variables.new()
        v.name, v.type = "h", "SINGLE_PROP"
        v.targets[0].id = body
        v.targets[0].data_path = "hide_render"
        d.expression = f"h or frame < {int(frame_on)}"


def materials():
    return dict(mask=P.mat("Respirator", (0.18, 0.2, 0.22), 0.6),
                filter=P.mat("Respirator filter", (0.38, 0.42, 0.3), 0.6),
                dust=P.mat("Dust mask", (0.86, 0.9, 0.92), 0.9))
