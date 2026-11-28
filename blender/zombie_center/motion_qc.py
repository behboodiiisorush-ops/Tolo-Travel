"""Motion QC — measures what the project law asks for, frame by frame (not just first/last frame).

    import motion_qc as Q
    rep = Q.feet(ch, f0, f1)            # foot contact: slide (cm/frame while planted), sinking (cm), floating
    Q.write(rep, "test/qc_walk.json")

Feet are measured on the real shoe/foot geometry (evaluated mesh, world space), not on bones:
- planted  = lowest point of the foot within CONTACT cm of the floor
- slide    = horizontal movement of that foot between two planted frames (cm/frame)
- sink     = how far the lowest point goes below the floor (cm)
- float    = frames where neither foot is near the floor while the clip says the character is standing/walking
"""
import bpy, json, math
from mathutils import Vector

CONTACT = 0.025      # m
SLIDE_OK = 0.6       # cm/frame while planted (≈ invisible at 24 fps)
SINK_OK = 0.8        # cm


def _foot_objects(ch):
    """The shoe meshes (or bare feet: the body) split by side using the foot bones."""
    shoes = [o for o in ch.parts.get("Clothes", []) if any(k in o.name.lower() for k in ("shoe", "boot", "sneaker", "flat", "sandal"))]
    return shoes or [ch.body]


def _side_points(ch, objs, dg):
    rig = ch.rig
    fl = rig.matrix_world @ rig.pose.bones["foot_l"].head
    fr = rig.matrix_world @ rig.pose.bones["foot_r"].head
    L, R = [], []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        for v in me.vertices:
            p = mw @ v.co
            if p.z > 0.25:                     # only the feet
                continue
            (L if (p - fl).length < (p - fr).length else R).append(p)
        ev.to_mesh_clear()
    return L, R


def _sole(ch, objs, dg):
    """{side: {(obj, vertex index): world position}} for foot geometry below 25 cm."""
    rig = ch.rig
    fl = rig.matrix_world @ rig.pose.bones["foot_l"].head
    fr = rig.matrix_world @ rig.pose.bones["foot_r"].head
    out = {"l": {}, "r": {}}
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        for v in me.vertices:
            p = mw @ v.co
            if p.z > 0.25:
                continue
            out["l" if (p - fl).length < (p - fr).length else "r"][(o.name, v.index)] = p
        ev.to_mesh_clear()
    return out


def feet(ch, f0, f1, floor=0.0):
    """Real sliding = the SAME sole points moving sideways while they stay on the ground
    (heel-to-toe roll is not sliding)."""
    sc = bpy.context.scene
    objs = _foot_objects(ch)
    rows, prev = [], None
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        cur = _sole(ch, objs, dg)
        row = {"frame": f}
        for s in ("l", "r"):
            pts = cur[s]
            if not pts:
                continue
            h = min(p.z for p in pts.values()) - floor
            touch = {k for k, p in pts.items() if p.z - floor < 0.012}
            slide = None
            if prev is not None:
                both = [k for k in touch if k in prev[s] and prev[s][k].z - floor < 0.012]
                if len(both) >= 3:
                    ds = [math.hypot(pts[k].x - prev[s][k].x, pts[k].y - prev[s][k].y) for k in both]
                    slide = sum(ds) / len(ds) * 100
            row[s] = {"h_cm": round(h * 100, 2), "planted": bool(touch), "slide_cm": None if slide is None else round(slide, 2)}
        rows.append(row)
        prev = cur
    slides = [r[s]["slide_cm"] for r in rows for s in ("l", "r") if s in r and r[s]["slide_cm"] is not None]
    sinks = [-r[s]["h_cm"] for r in rows for s in ("l", "r") if s in r and r[s]["h_cm"] < 0]
    floats = [r["frame"] for r in rows if not any(r.get(s, {}).get("planted") for s in ("l", "r"))]
    summ = {
        "frames": [f0, f1],
        "slide_max_cm": round(max(slides), 2) if slides else 0.0,
        "slide_mean_cm": round(sum(slides) / len(slides), 2) if slides else 0.0,
        "slide_bad_frames": sorted({r["frame"] for r in rows for s in ("l", "r")
                                    if s in r and (r[s]["slide_cm"] or 0) > SLIDE_OK}),
        "sink_max_cm": round(max(sinks), 2) if sinks else 0.0,
        "sink_bad_frames": sorted({r["frame"] for r in rows for s in ("l", "r") if s in r and -r[s]["h_cm"] > SINK_OK}),
        "airborne_frames": floats,
    }
    summ["pass"] = (summ["slide_max_cm"] <= SLIDE_OK * 2 and not summ["sink_bad_frames"]
                    and len(summ["slide_bad_frames"]) <= max(1, (f1 - f0) // 40))
    return {"summary": summ, "rows": rows}


def write(rep, path):
    with open(path, "w") as f:
        json.dump(rep, f, indent=1)
    return rep["summary"]


def ground(ch, f0, f1, floor=0.0, smooth=2, keep_flight=False):
    """Put the soles on the floor every frame: the rig is lifted/lowered so the lowest foot point is at
    `floor` (no sinking, no floating), lightly smoothed so the body doesn't jitter. Keys rig location z."""
    sc = bpy.context.scene
    objs = _foot_objects(ch)
    rig = ch.rig
    lows, base, stance = [], [], []
    prevc = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        L, R = _side_points(ch, objs, dg)
        pts = L + R
        lows.append(min(p.z for p in pts) - floor if pts else 0.0)
        base.append(rig.location.z)
        # stance = a foot whose lowest patch is (nearly) not moving horizontally -> it is on the ground
        st = None
        for s, P in (("l", L), ("r", R)):
            if not P:
                continue
            zs = sorted(p.z for p in P); cut = zs[max(0, len(zs) // 7)]
            c = sum((p for p in P if p.z <= cut), Vector()) / max(1, len([p for p in P if p.z <= cut]))
            if s in prevc and math.hypot(c.x - prevc[s].x, c.y - prevc[s].y) < 0.02:
                low = min(p.z for p in P) - floor
                st = low if st is None else min(st, low)
            prevc[s] = c
        stance.append(st)
    n = len(lows)
    if keep_flight:      # correct only stance frames, interpolate the offset through flight (keeps the jump)
        idx = [i for i in range(n) if stance[i] is not None]
        if idx:
            corr = [0.0] * n
            for i in range(n):
                a = max([j for j in idx if j <= i], default=None)
                b = min([j for j in idx if j >= i], default=None)
                if a is None: corr[i] = stance[b]
                elif b is None or a == b: corr[i] = stance[a]
                else: corr[i] = stance[a] + (stance[b] - stance[a]) * (i - a) / (b - a)
            # but never let a foot sink below the floor during flight
            lows = [max(min(lows[i], corr[i]), corr[i] if lows[i] >= corr[i] else lows[i]) for i in range(n)]
            lows = [min(corr[i], lows[i]) if lows[i] < corr[i] else corr[i] for i in range(n)]
    sm = []
    for i in range(n):
        a, b = max(0, i - smooth), min(n, i + smooth + 1)
        # never let the smoothed value leave a foot under the floor: use the min of raw and smoothed
        sm.append(min(lows[i], sum(lows[a:b]) / (b - a)))
    for i, f in enumerate(range(f0, f1 + 1)):
        sc.frame_set(f)
        loc = rig.location.copy()
        for k in range(3):
            if k < 2:
                rig.keyframe_insert("location", index=k, frame=f)
        rig.location.z = base[i] - sm[i]
        rig.keyframe_insert("location", index=2, frame=f)
    return [round(-x * 100, 2) for x in sm]


def ground_body(ch, f0, f1, floor=0.0, step=3):
    """For lying / falling / crawling: put the lowest point of the WHOLE body (skin + clothes) on the floor
    (feet-only grounding can't see a body hanging in the air above its feet). Keys rig location z."""
    import bpy
    sc = bpy.context.scene
    rig = ch.rig
    objs = [ch.body] + list(ch.parts.get("Clothes", []))
    keys = []
    for f in list(range(f0, f1 + 1, step)) + [f1]:
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        low = 1e9
        for o in objs:
            ev = o.evaluated_get(dg); me = ev.to_mesh()
            mw = o.matrix_world
            for v in me.vertices[::7]:
                z = (mw @ v.co).z
                if z < low:
                    low = z
            ev.to_mesh_clear()
        keys.append((f, rig.location.z - (low - floor)))
    for f, z in keys:
        rig.location.z = z
        rig.keyframe_insert("location", index=2, frame=f)
