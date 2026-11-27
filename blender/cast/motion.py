"""The standard motion system for every cast character (see blender/STANDARD.md).

    import motion as MO
    clips = MO.load(["breathing_idle", "thinking"])            # BEFORE the heavy scene is built
    tl = MO.Timeline(ch, fps=24)
    tl.add(clips["breathing_idle"], start=1, length=96, offset=pos, facing=180, src_from=1.0)
    tl.add(clips["thinking"], start=80, length=100, blend=20, match=1.0)   # cross-fade, best matching entry point
    tl.build()                       # writes keys: full 24 fps, overlapping cross-fades, gentle smoothing
    MO.foot_lock(ch, 1, N)           # IK foot planting: no sliding, no floor penetration
    findings = MO.check(ch, 1, N)    # frame-by-frame QA (motion_check.py) - must be empty before rendering

Why each piece exists:
  * cross-fades always overlap the previous clip completely (the old clip is held on its last pose if it ends
    early), so a blend can never jump;
  * `match` searches the first `match` seconds of the incoming clip for the pose closest to the outgoing one
    (a motion-graph transition), so blends are short distances, not big swings;
  * a light Gaussian filter (sigma ~0.8 frame) on rotations removes capture jitter without softening the acting;
  * foot_lock pins planted feet with 2-bone IK (calf/thigh) to targets that hold still while the foot is down
    and ease in/out over 4 frames, so weight shifts move the hips, not the feet.
"""
import bpy, math, os
from mathutils import Matrix, Quaternion, Vector
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(HERE, "..", "shelter3"))
import mocap2 as MC  # noqa: E402
import motion_check  # noqa: E402

MOCAP = os.path.join(HERE, "..", "mocap")
CORE = ["pelvis", "spine_01", "spine_02", "spine_03", "neck_01", "head", "clavicle_l", "clavicle_r",
        "upperarm_l", "upperarm_r", "lowerarm_l", "lowerarm_r", "hand_l", "hand_r",
        "thigh_l", "thigh_r", "calf_l", "calf_r", "foot_l", "foot_r"]


def load(names):
    return {n: MC.load(os.path.join(MOCAP, n + ".fbx")) for n in names}


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)        # smootherstep: zero velocity AND acceleration at the ends


def _qpath(b):
    return f'pose.bones["{b}"].rotation_quaternion'


class Timeline:
    def __init__(self, ch, fps=24, cuts=()):
        """cuts: first frames of new camera shots. A clip that starts on a cut may change place/facing
        (blend=0); smoothing never crosses a cut, foot_lock/check are run per shot (pass the same cuts)."""
        self.ch, self.fps, self.segs, self.cuts = ch, fps, [], sorted(cuts)
        self.transitions = []          # (first, last) frame of every cross-fade -> foot_lock(free=...)

    def add(self, clip, start, length, blend=0, match=0.0, **kw):
        self.segs.append(dict(clip=clip, start=start, length=length, blend=blend, match=match, kw=kw))

    def _render(self, seg, src_from=None, length=None):
        kw = dict(seg["kw"])
        if src_from is not None:
            kw["src_from"] = src_from
        rig = self.ch.rig
        keep = MC.BUF.pop(rig.name, None)
        MC.apply(self.ch, seg["clip"], start=seg["start"], length=length or seg["length"], step=1, **kw)
        out = MC.BUF.pop(rig.name)
        if keep is not None:
            MC.BUF[rig.name] = keep
        return out

    @staticmethod
    def _pose_dist(a, b, f):
        d = 0.0
        for bn in CORE:
            p = _qpath(bn)
            if (p, 0) in a and (p, 0) in b and f in a[(p, 0)] and f in b[(p, 0)]:
                qa = Quaternion([a[(p, i)][f] for i in range(4)])
                qb = Quaternion([b[(p, i)][f] for i in range(4)])
                d += abs(qa.rotation_difference(qb).angle if qa.dot(qb) >= 0 else
                         qa.rotation_difference(-qb).angle)
        return d

    def build(self, sigma=0.8):
        acc = {}
        for k, seg in enumerate(self.segs):
            start, blend = seg["start"], seg["blend"]
            base = seg["kw"].get("src_from", 0.0)
            if k and seg["match"] > 0 and blend:
                mid = start + blend // 2
                best, bd = base, None
                steps = int(seg["match"] * self.fps)
                for j in range(0, steps + 1, 2):
                    sf = base + j / self.fps
                    probe = self._render(seg, src_from=sf, length=blend)
                    d = self._pose_dist(acc, probe, mid)
                    if bd is None or d < bd:
                        best, bd = sf, d
                seg["kw"]["src_from"] = best
            new = self._render(seg)
            if not acc:
                acc = {k2: dict(v) for k2, v in new.items()}
                continue
            end = start + blend
            self.transitions.append((start, end))
            # hold the old animation on its last value through the whole blend window
            for key, pts in acc.items():
                if not pts:
                    continue
                last = max(pts)
                for f in range(last + 1, end + 1):
                    pts[f] = pts[last]
            quat = {}
            for (path, idx), pts in new.items():
                if path.endswith("rotation_quaternion"):
                    quat.setdefault(path, {})[idx] = pts
                    continue
                dst = acc.setdefault((path, idx), {})
                for f, v in pts.items():
                    w = smooth((f - start) / blend) if blend and f in dst and f < end else 1.0
                    dst[f] = dst.get(f, v) * (1 - w) + v * w
            for path, comps in quat.items():
                olds = [acc.setdefault((path, i), {}) for i in range(4)]
                for f in comps[0]:
                    qn = Quaternion([comps[i][f] for i in range(4)])
                    if blend and f in olds[0] and f < end:
                        qo = Quaternion([olds[i][f] for i in range(4)])
                        w = smooth((f - start) / blend)
                        qn = qo.slerp(qn if qo.dot(qn) >= 0 else -qn, w)
                    for i in range(4):
                        olds[i][f] = qn[i]
            # frames of the old clip after the end of the blend are dropped (new clip owns them)
        if sigma:
            _gauss(acc, sigma, self.cuts)
        MC.BUF[self.ch.rig.name] = acc
        MC.flush(self.ch)


EXTRA = {"hand_l": 2.2, "hand_r": 2.2, "lowerarm_l": 1.6, "lowerarm_r": 1.6,   # wrists: a little softer
         "ball_l": 1.6, "ball_r": 1.6}                                        # toe roll: no one-frame flicks


def _gauss(buf, sigma0, cuts=()):
    paths = {}
    for (path, idx) in buf:
        paths.setdefault(path, []).append(idx)
    for path, idxs in paths.items():
        bone = path.split('"')[1] if '"' in path else ""
        sigma = sigma0 * EXTRA.get(bone, 1.0)
        r = int(math.ceil(3 * sigma))
        ker = [math.exp(-0.5 * (i / sigma) ** 2) for i in range(-r, r + 1)]
        allf = sorted(buf[(path, idxs[0])])
        if len(allf) < 3:
            continue
        edges = [c for c in cuts if allf[0] < c <= allf[-1]]
        groups, cur = [], []
        for f in allf:
            if edges and f >= edges[0]:
                while edges and f >= edges[0]:
                    edges.pop(0)
                if cur:
                    groups.append(cur)
                cur = []
            cur.append(f)
        groups.append(cur)
        for frames in groups:
            _gauss_run(buf, path, idxs, frames, sigma, r, ker)


def _gauss_run(buf, path, idxs, frames, sigma, r, ker):
    if True:
        if len(frames) < 3:
            return
        if path.endswith("rotation_quaternion"):
            q = [Quaternion([buf[(path, i)][f] for i in range(4)]) for f in frames]
            for j in range(1, len(q)):
                if q[j].dot(q[j - 1]) < 0:
                    q[j].negate()
            vals = [[v[i] for v in q] for i in range(4)]
        else:
            vals = [[buf[(path, i)][f] for f in frames] for i in sorted(idxs)]
        out = []
        for ch in vals:
            n = len(ch)
            sm = []
            for j in range(n):
                s = w = 0.0
                for o, kv in zip(range(-r, r + 1), ker):
                    jj = min(n - 1, max(0, j + o))
                    s += ch[jj] * kv
                    w += kv
                sm.append(s / w)
            out.append(sm)
        if path.endswith("rotation_quaternion"):
            for j, f in enumerate(frames):
                qq = Quaternion([out[i][j] for i in range(4)]).normalized()
                for i in range(4):
                    buf[(path, i)][f] = qq[i]
        else:
            for c, i in enumerate(sorted(idxs)):
                for j, f in enumerate(frames):
                    buf[(path, i)][f] = out[c][j]


# ------------------------------------------------------------------ foot planting (IK)
def foot_lock(ch, a, b, floor=None, ease=6, min_plant=6, free=(), lift=0.035, cuts=()):
    """free: frame windows (usually the clip cross-fades, Timeline.transitions) where the stance may change:
    the left foot re-plants in the first half, the right in the second, each with a small lifted step."""
    """Pin feet that are down: 2-bone IK on each leg to a target that holds still while the foot is planted."""
    rig = ch.rig
    sc = bpy.context.scene
    fps = sc.render.fps
    mats = {s: [] for s in "lr"}
    balls = {s: [] for s in "lr"}
    knees = {s: [] for s in "lr"}
    hips = {s: [] for s in "lr"}
    ballp = {s: [] for s in "lr"}
    for f in range(a, b + 1):
        sc.frame_set(f)
        for s in "lr":
            knees[s].append((rig.matrix_world @ rig.pose.bones[f"calf_{s}"].matrix).translation.copy())
            hips[s].append((rig.matrix_world @ rig.pose.bones[f"thigh_{s}"].matrix).translation.copy())
            mats[s].append(rig.matrix_world @ rig.pose.bones[f"foot_{s}"].matrix)
            bp_ = (rig.matrix_world @ rig.pose.bones[f"ball_{s}"].matrix).translation.copy()
            balls[s].append(bp_.z)
            ballp[s].append(bp_)
    n = b - a + 1
    A0, N0 = a, n
    FULL = dict(mats=mats, balls=balls, ballp=ballp, knees=knees, hips=hips)
    # camera cuts: every shot is solved on its own (a plant never holds across a cut)
    edges = [A0] + sorted(c for c in cuts if A0 < c <= A0 + N0 - 1) + [A0 + N0]
    blocks = [(edges[k], edges[k + 1] - 1) for k in range(len(edges) - 1)]
    for s in "lr":
        TG_ALL = []
        for (ba, bb) in blocks:
            o0, a, n = ba - A0, ba, bb - ba + 1
            mats, balls, ballp, knees, hips = ({k: v[o0:o0 + n] for k, v in FULL[nm].items()}
                                               for nm in ("mats", "balls", "ballp", "knees", "hips"))
            M = mats[s]
            Z = sorted(m.translation.z for m in M)
            stand = Z[max(0, n // 20)]
            BZ = sorted(balls[s])
            bstand = BZ[max(0, n // 20)]
            down, heel = [], []
            for i in range(n):
                j = min(n - 1, i + 1)
                k = max(0, i - 1)
                v = (M[j].translation - M[k].translation)
                v.z = 0
                hv = v.length * fps / max(1, j - k)
                # down = heel and ball near the floor (no speed test: a planted foot must never slide, the hips move instead)
                fr = a + i
                stepping = any((f0 <= fr <= (f0 + f1) // 2) if s == "l" else ((f0 + f1) // 2 <= fr <= f1) for f0, f1 in free)
                down.append(M[i].translation.z < stand + 0.012 and balls[s][i] < bstand + 0.012 and not stepping)
                heel.append(M[i].translation.z < stand + 0.012 and not stepping)
            spans, i = [], 0
            while i < n:
                if down[i]:
                    j = i
                    while j + 1 < n and down[j + 1]:
                        j += 1
                    if j - i + 1 >= min_plant:
                        spans.append((i, j))
                    i = j + 1
                else:
                    i += 1
            # Offset warping: inside a plant the foot is pinned where it landed; between plants the mocap path keeps
            # its shape, but its offset from the mocap is blended smoothly from one plant's correction to the next.
            locs, pre, post = [], {}, {}
            for (i0, i1) in spans:
                h0 = i0
                while h0 - 1 >= 0 and heel[h0 - 1]:
                    h0 -= 1                                  # heel strike happened here
                h1 = i1
                while h1 + 1 < n and heel[h1 + 1]:
                    h1 += 1                                  # heel leaves the floor here
                loc = M[i0].translation.copy()
                loc.x, loc.y = M[h0].translation.x, M[h0].translation.y
                loc.z = max(loc.z, stand)
                locs.append((i0, i1, loc, M[i0].to_quaternion()))
                for i in range(h0, i0):
                    pre[i] = loc
                for i in range(i1 + 1, h1 + 1):
                    post[i] = loc
            def corr(i, k):      # correction that pins frame i to plant k
                i0, i1, loc, q = locs[k]
                qm = M[i].to_quaternion()
                dq = q @ qm.inverted()
                return loc - M[i].translation, dq
            TG = []
            PROC = set()                                  # frames of procedural short steps
            for i in range(n):
                pm, qm = M[i].translation.copy(), M[i].to_quaternion()
                if not locs:
                    pm.z = max(pm.z, stand)
                    TG.append((pm, qm))
                    continue
                k = next((k for k, (i0, i1, _, _) in enumerate(locs) if i0 <= i <= i1), None)
                if k is not None:
                    TG.append((locs[k][2].copy(), locs[k][3].copy()))
                    continue
                prev = max((k for k, l in enumerate(locs) if l[1] < i), default=None)
                nxt = min((k for k, l in enumerate(locs) if l[0] > i), default=None)
                if prev is not None:
                    dp0, dq0 = corr(locs[prev][1], prev)
                if nxt is not None:
                    dp1, dq1 = corr(locs[nxt][0], nxt)
                if prev is None:
                    dp, dq = dp1, dq1
                elif nxt is None:
                    dp, dq = dp0, dq0
                else:
                    g = locs[nxt][0] - locs[prev][1]
                    ul = (i - locs[prev][1]) / g
                    L0, L1 = locs[prev][2], locs[nxt][2]
                    Q0, Q1 = locs[prev][3], locs[nxt][3]
                    move = Vector((L1.x - L0.x, L1.y - L0.y)).length
                    if g <= 40:
                        # a short re-plant (weight shift / small step), built cleanly: the foot lifts first, travels from
                        # plant to plant in the middle 70 %, sets down; zero speed at both ends (16u²(1-u)² lift)
                        u = smooth((ul - 0.25) / 0.5)          # sideways only once the foot is off the floor
                        PROC.add(i)
                        p = L0.lerp(L1, u)
                        p.z = L0.z + (L1.z - L0.z) * u + (min(lift, 0.8 * move + 0.015) * 16 * ul * ul * (1 - ul) ** 2
                                                          if move > 0.008 else 0.0)
                        TG.append((p, Q0.slerp(Q1 if Q0.dot(Q1) >= 0 else -Q1, smooth(ul))))
                        continue
                    u = smooth(ul)
                    dp = dp0.lerp(dp1, u)
                    dq = dq0.slerp(dq1 if dq0.dot(dq1) >= 0 else -dq1, u)
                    raw = pm + dp
                    raw.z = max(raw.z, stand)
                    rq = dq @ qm
                    E = min(ease, g / 2)
                    Exy = min(3 * ease, g / 2)                # sideways settles earlier than height: no touchdown skid
                    wa = smooth((i - locs[prev][1]) / E)      # ease out of the last plant
                    wb = smooth((locs[nxt][0] - i) / E)       # ease into the next one
                    wax = smooth((i - locs[prev][1]) / Exy)
                    wbx = smooth((locs[nxt][0] - i) / Exy)
                    p = L0.lerp(raw, wa)
                    p = L1.lerp(p, wb)
                    px = L0.lerp(raw, wax)
                    px = L1.lerp(px, wbx)
                    p.x, p.y = px.x, px.y
                    q = Q0.slerp(rq if Q0.dot(rq) >= 0 else -rq, wa)
                    q = Q1.slerp(q if Q1.dot(q) >= 0 else -q, wb)
                    TG.append((p, q))
                    continue
                p = pm + dp
                p.z = max(p.z, stand)
                TG.append((p, dq @ qm))

            # heel strike / heel off — a proper heel-toe roll:
            #   toes coming down after heel strike: ground point held, foot keeps the plant's heading (no toe swivel);
            #   heel lifting before toe off: the foot pivots about the planted toes (the ball stays put).
            OFF = M[0].inverted() @ ballp[s][0]                  # ball position in the foot's own space
            def heading(q):
                v = q @ Vector((0, 1, 0))
                return math.atan2(v.y, v.x)
            def with_heading(q, h):
                return Quaternion((0, 0, 1), h - heading(q)) @ q
            roll = {}
            for k, (i0, i1, L, Q) in enumerate(locs):
                hq = heading(Q)
                ball_lock = (Matrix.Translation(L) @ Q.to_matrix().to_4x4()) @ OFF
                for i in range(n):
                    if i in pre and pre[i] is L:
                        roll[i] = ("land", 1.0, L, hq, ball_lock)
                    if i in post and post[i] is L:
                        roll[i] = ("lift", 1.0, L, hq, ball_lock)
            for i, v in list(roll.items()):
                for d in range(1, 5):
                    for j in (i - d, i + d):
                        if 0 <= j < n and j not in roll and not any(l[0] <= j <= l[1] for l in locs):
                            wj = smooth(1 - d / 5)
                            if wj > roll.get(j, (0, 0.0))[1]:
                                roll[j] = (v[0], wj, v[2], v[3], v[4])
            for i, (kind, w, L, hq, bl) in roll.items():
                if any(l[0] <= i <= l[1] for l in locs) or i in PROC:   # a built step already lands/lifts cleanly
                    continue
                p, q = TG[i]
                qh = with_heading(q, hq)
                q2 = q.slerp(qh if q.dot(qh) >= 0 else -qh, w)
                if kind == "land":
                    p2 = p.copy()
                    p2.x += (L.x - p.x) * w
                    p2.y += (L.y - p.y) * w
                else:
                    piv = bl - q2 @ OFF                              # ankle that keeps the toes where they were
                    p2 = p.lerp(piv, w)
                TG[i] = (p2, q2)
            # contact stick (final pass): while the heel or the toes touch the floor on consecutive frames, that point
            # may not move sideways; the correction this needs is carried and eased away once the foot is in the air.
            off = Vector((0.0, 0.0, 0.0))
            yoff = 0.0
            prev = None
            rel = None
            for i in range(n):
                p, q = TG[i]
                p = p + off
                q = Quaternion((0, 0, 1), yoff) @ q
                heel_on = p.z < stand + 0.008
                ball = (Matrix.Translation(p) @ q.to_matrix().to_4x4()) @ OFF
                toe_on = ball.z < bstand + 0.008
                if prev is not None:
                    pp, pb, ph, pt, pq = prev
                    if heel_on and toe_on and ph and pt:          # flat on the floor: no swivel
                        dy = heading(pq) - heading(q)
                        dy = (dy + math.pi) % (2 * math.pi) - math.pi
                        yoff += dy
                        q = Quaternion((0, 0, 1), dy) @ q
                    else:
                        yoff *= 0.75
                    ball = (Matrix.Translation(p) @ q.to_matrix().to_4x4()) @ OFF
                    rising = p.z > pp.z + 0.0005
                    if toe_on and pt and (rising or not (heel_on and ph)):   # heel lifting: pivot on the toes
                        d = Vector((pb.x - ball.x, pb.y - ball.y, 0))
                    elif heel_on and ph:                                    # heel down: the heel holds
                        d = Vector((pp.x - p.x, pp.y - p.y, 0))
                    else:
                        d = None                                            # airborne
                    if d is not None:
                        rel = None
                        off = off + d
                        p = p + d
                        ball = ball + d
                    else:
                        if rel is None:                     # just left the floor: ease from rest onto the natural path
                            rel = (0, pp.copy(), pq.copy())
                        t, H, HQ = rel
                        w = smooth((t + 1) / 7)
                        raw = TG[i][0]
                        p = H.lerp(raw, w)
                        p.z = max(p.z, raw.z)          # the foot keeps its lift: only the sideways catch-up eases
                        q = HQ.slerp(q if HQ.dot(q) >= 0 else -q, w)
                        off = p - raw
                        rel = (t + 1, H, HQ) if t + 1 < 6 else (99, H, HQ)
                        if t >= 6:
                            p, off = raw.copy(), Vector((0.0, 0.0, 0.0))
                        ball = (Matrix.Translation(p) @ q.to_matrix().to_4x4()) @ OFF
                TG[i] = (p, q)
                prev = (p, ball, heel_on, toe_on, q)
            # soft IK: as the leg nears full extension the reach is eased (exponential), so the knee never snaps straight
            B = rig.data.bones
            sx = rig.matrix_world.to_scale().x
            Lmax = ((B[f"thigh_{s}"].tail_local - B[f"thigh_{s}"].head_local).length
                    + (B[f"calf_{s}"].tail_local - B[f"calf_{s}"].head_local).length) * sx
            soft = 0.02
            # while the foot follows the capture (not planted) a reach the captured leg itself makes is never eased
            # (easing it only moves a near-straight knee about, e.g. at heel strike); planted feet keep the plain
            # soft limit. The two blend over a few frames.
            freew = [0.0 if any(l_[0] <= i <= l_[1] for l_ in locs) else 1.0 for i in range(n)]
            freew = [sum(freew[max(0, i - 4):i + 5]) / len(freew[max(0, i - 4):i + 5]) for i in range(n)]
            for i in range(n):
                p, q = TG[i]
                h = hips[s][i]
                d = (p - h).length
                draw = (mats[s][i].translation - h).length
                lim = (Lmax - soft) + freew[i] * max(0.0, min(draw, Lmax - 1e-4) - (Lmax - soft))
                if d > lim:
                    zone = max(1e-4, Lmax - lim)
                    dn = lim + zone * (1 - math.exp(-(d - lim) / zone))
                    TG[i] = (h + (p - h).normalized() * dn, q)
            TG_ALL += TG
        a, n, TG = A0, N0, TG_ALL
        mats, balls, ballp, knees, hips = (FULL[nm] for nm in ("mats", "balls", "ballp", "knees", "hips"))
        e = bpy.data.objects.new(f"{rig.name}_foot_{s}", None)
        sc.collection.objects.link(e)
        e.empty_display_size = 0.05
        e.rotation_mode = "QUATERNION"
        fc = {}
        act = bpy.data.actions.new(e.name + "Action")
        e.animation_data_create()
        e.animation_data.action = act
        vals = {}
        for i in range(n):
            pm, qm = TG[i]
            for c in range(3):
                vals.setdefault(("location", c), []).append((a + i, pm[c]))
            for c in range(4):
                vals.setdefault(("rotation_quaternion", c), []).append((a + i, qm[c]))
        for (path, c), pts in vals.items():
            _fc(e, act, path, c, pts)
        # knee pole: in front of the knee, over the toes (stable even when the leg is straight)
        pe = bpy.data.objects.new(f"{rig.name}_knee_{s}", None)
        sc.collection.objects.link(pe)
        pe.empty_display_size = 0.04
        pvals = {}
        # the foot's horizontal heading; while the toes point down (swing leg) its projection gets short and
        # unstable, so the last steady heading is held there - otherwise the pole (and the knee) can flip
        M_ALL = mats[s]
        heads, last = [], None
        for i in range(n):
            fwd = TG[i][1] @ Vector((0, 1, 0))          # foot bone Y points to the toes
            fwd.z = 0
            if fwd.length > 0.35 or last is None:
                last = fwd.normalized() if fwd.length > 1e-6 else Vector((0, -1, 0))
            heads.append(last.copy())
        for i in range(n):                              # light smoothing of the heading (no snaps)
            acc_ = Vector((0, 0, 0))
            for j in range(max(0, i - 3), min(n, i + 4)):
                acc_ += heads[j]
            fwd = acc_.normalized() if acc_.length > 1e-6 else heads[i]
            # where the captured knee actually bends (perpendicular to the hip->foot line): the IK then reproduces
            # the mocap knee; only a nearly straight leg falls back on the foot heading
            h_, p_ = hips[s][i], M_ALL[i].translation        # the captured foot: the plane the knee bends in
            ax = (p_ - h_)
            if ax.length > 1e-6:
                ax.normalize()
                v_ = knees[s][i] - h_
                bend = v_ - ax * v_.dot(ax)
                w_ = smooth((bend.length - 0.015) / 0.03)
                if w_ > 0:
                    fwd = (bend.normalized() * w_ + fwd * (1 - w_))
                    fwd = fwd.normalized() if fwd.length > 1e-6 else heads[i]
            pp = knees[s][i] + fwd * 0.5
            for c in range(3):
                pvals.setdefault(c, []).append((a + i, pp[c]))
        pe.animation_data_create()
        pa = bpy.data.actions.new(pe.name + "Action")
        pe.animation_data.action = pa
        for c, pts in pvals.items():
            _fc(pe, pa, "location", c, pts)
        ik = rig.pose.bones[f"calf_{s}"].constraints.new("IK")
        ik.target, ik.chain_count, ik.use_tail = e, 2, True
        ik.use_rotation = False
        ik.pole_target = pe
        ik.pole_angle = _pole_angle(rig, s)
        cr = rig.pose.bones[f"foot_{s}"].constraints.new("COPY_ROTATION")
        cr.target = e
    return True


def _signed_angle(u, v, normal):
    ang = u.angle(v)
    return -ang if u.cross(v).angle(normal) < 1 else ang


def _pole_angle(rig, s):
    """Pole angle that keeps the rest pose: pole in front of the rest knee, over the rest toes."""
    B = rig.data.bones
    th, ca, ft = B[f"thigh_{s}"], B[f"calf_{s}"], B[f"foot_{s}"]
    fwd = ft.matrix_local.to_3x3() @ Vector((0, 1, 0))
    fwd.z = 0
    pole = ca.head_local + fwd.normalized() * 0.5
    normal = (ca.tail_local - th.head_local).cross(pole - th.head_local)
    proj = normal.cross(th.tail_local - th.head_local)
    return _signed_angle(th.matrix_local.to_3x3().col[0], proj, th.tail_local - th.head_local)


def _fc(obj, act, path, idx, pts):
    """Insert keys into an action (works with Blender 4.4+ layered actions and older ones)."""
    obj.keyframe_insert(path, index=idx, frame=pts[0][0])
    fcs = None
    if hasattr(act, "fcurves"):
        try:
            fcs = act.fcurves
        except Exception:
            fcs = None
    fc = None
    if fcs is not None:
        fc = fcs.find(path, index=idx)
    if fc is None:
        for layer in getattr(act, "layers", []):
            for strip in layer.strips:
                for bag in strip.channelbags:
                    fc = bag.fcurves.find(path, index=idx) or fc
    fc.keyframe_points.add(len(pts) - 1)
    co = []
    for f, v in pts:
        co += [f, v]
    fc.keyframe_points.foreach_set("co", co)
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"
    fc.update()


def check(ch, a, b, path=None, cuts=()):
    edges = [a] + sorted(c for c in cuts if a < c <= b) + [b + 1]
    f = []
    for k in range(len(edges) - 1):
        if edges[k + 1] - edges[k] > 3:
            f += motion_check.check(ch.rig, edges[k], edges[k + 1] - 1)
    f.sort()
    motion_check.report(f, path)
    return f
