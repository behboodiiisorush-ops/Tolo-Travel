"""Characters for «پارک»: three kids, a puppy, a mother duck and ducklings — round, cute, original designs.

Motion: every actor moves on routes (eased start/stop, constant cruising speed), turns smoothly, and its feet are
driven by a stepping solver: a planted foot stays exactly where it is until the body has moved too far from it,
then it lifts and lands ahead of the body. No foot ever slides on the ground (checked by check_feet()).
Forward is local -Y.  Times in seconds, FPS = 24.
"""
import bpy, math, random
from mathutils import Vector, Matrix, Euler
import lib as L

FPS = 24
DT = 1.0 / (FPS * 4)            # solver sub-step
GROUND = 0.0


def trapz(u, a=0.18):
    """Arc-length fraction for a trapezoid speed profile (accelerate, cruise, brake)."""
    u = min(1.0, max(0.0, u))
    vmax = 1.0 / (1.0 - a)
    if u < a:
        return 0.5 * vmax * u * u / a
    if u > 1 - a:
        w = 1 - u
        return 1.0 - 0.5 * vmax * w * w / a
    return 0.5 * vmax * a + vmax * (u - a)


class Route:
    def __init__(self, t0, t1, pts, accel=0.18):
        self.t0, self.t1, self.accel = t0, t1, accel
        pts = [Vector((p[0], p[1], 0)) for p in pts]
        dense = L.catmull(pts, samples=max(8, 24 * (len(pts) - 1))) if len(pts) > 2 else \
            [pts[0].lerp(pts[1], k / 20) for k in range(21)]
        self.pts = dense
        self.cum = [0.0]
        for a, b in zip(dense, dense[1:]):
            self.cum.append(self.cum[-1] + (b - a).length)
        self.length = self.cum[-1]

    def at(self, t):
        u = trapz((t - self.t0) / max(1e-6, self.t1 - self.t0), self.accel)
        s = u * self.length
        for i in range(1, len(self.cum)):
            if self.cum[i] >= s:
                k = (s - self.cum[i - 1]) / max(1e-9, self.cum[i] - self.cum[i - 1])
                return self.pts[i - 1].lerp(self.pts[i], k)
        return self.pts[-1].copy()


class Actor:
    """Root motion (routes, hops, facing) + feet (stepping solver), precomputed for every frame."""

    def __init__(self, name, start, yaw0=0.0, feet=(), thresh=(0.10, 0.20), stride_t=(0.30, 0.17), lift=(0.05, 0.09),
                 lead=0.45, run_v=1.6, turn_rate=7.0):
        self.name = name
        self.start = Vector((start[0], start[1], 0))
        self.yaw0 = yaw0
        self.routes = []
        self.hops = []               # (t0, t1, height)
        self.face = []               # (t, target Vector or yaw float or None)
        self.feet = list(feet)       # [(local x, local y, group)]
        self.thresh, self.stride_t, self.lift, self.lead, self.run_v = thresh, stride_t, lift, lead, run_v
        self.turn_rate = turn_rate
        self.lift_scale = []         # (t, factor) keys, e.g. marching
        self.free_feet = {}          # foot index -> function(t) -> (weight, world pos) override

    def move(self, t0, t1, *pts, accel=0.18):
        self.routes.append(Route(t0, t1, pts, accel))
        return self

    def hop(self, t0, t1, h):
        self.hops.append((t0, t1, h))
        return self

    def look(self, t, target):
        self.face.append((t, target))
        return self

    # ---- root
    def build_trail(self, t0, t1):
        """Path history (for followers): arc length -> position, sampled at DT."""
        self.trail_t0 = t0
        self.trail_p, self.trail_s = [], []
        prev, s = None, 0.0
        t = t0
        while t <= t1 + DT:
            p = self.root_xy(t)
            if prev is not None:
                s += (p - prev).length
            self.trail_p.append(p)
            self.trail_s.append(s)
            prev = p
            t += DT
        return self

    def trail_at_time(self, t):
        i = int(round((t - self.trail_t0) / DT))
        i = max(0, min(len(self.trail_s) - 1, i))
        return self.trail_s[i]

    def trail_at_s(self, s):
        import bisect
        i = bisect.bisect_left(self.trail_s, s)
        i = max(1, min(len(self.trail_s) - 1, i))
        a, b = self.trail_s[i - 1], self.trail_s[i]
        k = 0.0 if b - a < 1e-9 else (s - a) / (b - a)
        return self.trail_p[i - 1].lerp(self.trail_p[i], max(0.0, min(1.0, k)))

    def follow(self, leader, gap, until=1e9):
        self.leader, self.gap, self.follow_until = leader, gap, until
        return self

    def root_xy(self, t):
        if getattr(self, "leader", None) is not None and t < self.follow_until:
            return self.leader.trail_at_s(self.leader.trail_at_time(t) - self.gap)
        p = self.start.copy()
        for r in sorted(self.routes, key=lambda r: r.t0):
            if t >= r.t1:
                p = r.pts[-1].copy()
            elif t >= r.t0:
                return r.at(t)
        return p

    def hop_z(self, t):
        z = 0.0
        for t0, t1, h in self.hops:
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0)
                z = max(z, 4 * h * u * (1 - u))
        return z

    def face_target(self, t):
        cur = None
        for tt, tg in sorted(self.face, key=lambda x: x[0]):
            if t >= tt:
                cur = tg
        return cur

    def look_point(self, t):
        tg = self.face_target(t)
        if callable(tg):
            tg = tg(t)
        if tg is None or isinstance(tg, (int, float)):
            return None
        return Vector(tg)

    def precompute(self, T):
        n = int(T * FPS) + 2
        sub = 4
        self.pos, self.z, self.yaw, self.vel = [], [], [], []
        self.footp = [[] for _ in self.feet]
        self.footlift = [[] for _ in self.feet]
        yaw = self.yaw0
        prev = self.root_xy(0.0)
        planted = []
        for (fx, fy, g) in self.feet:
            planted.append(self.root_xy(0) + L.Matrix.Rotation(yaw, 3, "Z") @ Vector((fx, fy, 0)))
        swing = [None] * len(self.feet)          # (A, B, ts, T, h)
        last_step = [-9.0] * len(self.feet)
        v_s = Vector((0, 0, 0))
        for i in range(n * sub):
            t = i * DT
            p = self.root_xy(t)
            v = (p - prev) / DT if i else Vector((0, 0, 0))
            v_s = v_s.lerp(v, min(1.0, DT * 12))
            prev = p
            sp = v_s.length
            # facing: travel direction, else a look target, else keep
            tg = self.face_target(t)
            want = yaw
            if sp > 0.25:
                want = L.yaw_of(v_s)
            elif isinstance(tg, (int, float)):
                want = tg
            elif tg is not None:
                if callable(tg):
                    tg = tg(t)
                d = Vector(tg) - p
                d.z = 0
                if d.length > 0.05:
                    want = L.yaw_of(d)
            dy = L.wrap(want - yaw)
            yaw += max(-self.turn_rate * DT, min(self.turn_rate * DT, dy * min(1.0, DT * 10)))
            hz = self.hop_z(t)
            R = Matrix.Rotation(yaw, 3, "Z")
            k = min(1.0, sp / self.run_v)
            thr = self.thresh[0] + (self.thresh[1] - self.thresh[0]) * k
            stT = self.stride_t[0] + (self.stride_t[1] - self.stride_t[0]) * k
            lf = self.lift[0] + (self.lift[1] - self.lift[0]) * k
            lf *= L.track(self.lift_scale, t) if self.lift_scale else 1.0
            for j, (fx, fy, g) in enumerate(self.feet):
                ideal = p + R @ Vector((fx, fy, 0))
                if hz > 0.01:                                  # in the air: feet tucked under the body
                    planted[j] = ideal + Vector((0, 0, hz))
                    swing[j] = None
                    continue
                if planted[j].z > 0.001 and swing[j] is None:    # landing from a hop
                    planted[j] = ideal
                if swing[j] is not None:
                    A, B, ts, T, h = swing[j]
                    # keep aiming at where the foot should land
                    if (t - ts) / T < 0.6:                    # re-aim early in the swing only
                        B = ideal + v_s * (T - (t - ts)) * self.lead
                        swing[j] = (A, B, ts, T, h)
                    if t - ts >= T:
                        planted[j] = Vector((B.x, B.y, 0))
                        swing[j] = None
                        last_step[j] = t
                    continue
                drift = (ideal - planted[j]).length
                busy = any(swing[q] is not None and self.feet[q][2] != g for q in range(len(self.feet)))
                partner_air = [swing[q] for q in range(len(self.feet)) if q != j and self.feet[q][2] != g]
                if busy and sp > self.run_v * 0.85:              # running: allow a flight phase
                    busy = not all(s is not None and (t - s[2]) / s[3] > 0.55 for s in partner_air if s)
                if drift > thr and not busy and t - last_step[j] > stT * 0.5:
                    swing[j] = (planted[j].copy(), ideal + v_s * stT * self.lead, t, stT, lf)
                elif sp < 0.05 and drift > 0.035 and not busy and t - last_step[j] > 0.25:   # settle step
                    swing[j] = (planted[j].copy(), ideal, t, 0.22, 0.035)
            if i % sub == 0:
                self.pos.append(p.copy())
                self.z.append(hz)
                self.yaw.append(yaw)
                self.vel.append(v_s.copy())
                for j in range(len(self.feet)):
                    if swing[j] is not None:
                        A, B, ts, T, h = swing[j]
                        u = (t - ts) / T
                        e = L.ease(u)
                        q = A.lerp(B, e)
                        q.z = h * math.sin(math.pi * min(1, u)) ** 0.9
                        self.footp[j].append(q)
                        self.footlift[j].append(q.z)
                    else:
                        self.footp[j].append(planted[j].copy())
                        self.footlift[j].append(planted[j].z)
        return self

    def check_feet(self, tol=0.004):
        """Report frames where a foot on the ground moves horizontally (= sliding)."""
        bad = []
        for j in range(len(self.feet)):
            for f in range(1, len(self.footp[j])):
                a, b = self.footp[j][f - 1], self.footp[j][f]
                if a.z < 0.002 and b.z < 0.002 and (Vector((a.x, a.y, 0)) - Vector((b.x, b.y, 0))).length > tol:
                    bad.append((self.name, j, f))
        return bad


# =====================================================================================================  kids
class Kid:
    def __init__(self, name, start, yaw0, k=1.0, skin="#ffd2b0", shirt="#ff5a5f", pants="#3d6fd8",
                 shoes="#ffffff", hair="#3a2a1e", style="short", dress=False, sock="#ffffff"):
        self.name, self.k = name, k
        self.act = Actor(name, start, yaw0, feet=[(0.075 * k, 0.0, 0), (-0.075 * k, 0.0, 1)],
                         thresh=(0.09 * k, 0.22 * k), stride_t=(0.30, 0.19), lift=(0.05 * k, 0.09 * k), run_v=2.0)
        self.arms = [(0.0, "rest")]
        self.looks = [(0.0, None)]
        self.expr = [(0.0, (0.55, 0.0))]          # (mouth open 0..1.2, eyes happy-closed 0..1)
        self.sit = [(0.0, 0.0)]
        self.fall = [(0.0, 0.0)]
        self.kick = [(0.0, 0.0)]                  # 0..1 kick progress on the right foot
        self.kick_w = [(0.0, 0.0)]
        self.laugh = [(0.0, 0.0)]
        self.blinks = [random.Random(name).uniform(1, 3)]
        while self.blinks[-1] < 70:
            self.blinks.append(self.blinks[-1] + random.Random(name + str(len(self.blinks))).uniform(2.2, 4.2))
        self.build(skin, shirt, pants, shoes, hair, style, dress, sock)
        self.hand_world = {1: Vector(), -1: Vector()}

    def build(self, skin, shirt, pants, shoes, hair, style, dress, sock):
        k, n = self.k, self.name
        SK, SH, PA = L.toon(n + "_skin", skin), L.toon(n + "_shirt", shirt), L.toon(n + "_pants", pants)
        HA, SO = L.toon(n + "_hair", hair), L.toon(n + "_shoe", shoes)
        self.root = L.empty(n)
        self.root.scale = (k, k, k)
        self.hips = L.empty(n + "_hips", self.root, (0, 0, 0.30))
        h = self.hips
        if dress:
            L.blob(n + "_dress", (0, 0, 0.02), (0.20, 0.18, 0.15), SH, parent=h, half=False)
            L.blob(n + "_top", (0, 0, 0.17), (0.145, 0.12, 0.17), SH, parent=h)
        else:
            L.blob(n + "_torso", (0, 0, 0.17), (0.155, 0.125, 0.18), SH, parent=h)
            L.blob(n + "_shorts", (0, 0, 0.02), (0.15, 0.125, 0.085), PA, parent=h)
        self.head = L.empty(n + "_head", h, (0, 0, 0.53))
        hd = self.head
        L.blob(n + "_skull", (0, 0, 0), (0.25, 0.235, 0.24), SK, parent=hd)
        for s in (-1, 1):
            L.blob(n + "_ear%d" % s, (s * 0.24, 0.01, 0.0), (0.04, 0.03, 0.055), SK, parent=hd, lw=0.008)
            L.blob(n + "_cheek%d" % s, (s * 0.135, -0.205, -0.055), (0.042, 0.012, 0.026),
                   L.flat("cheek", "#ff9aa2"), parent=hd, line=False)
            L.blob(n + "_sleeve%d" % s, (s * 0.15, 0, 0.29), (0.065, 0.065, 0.06), SH, parent=h, lw=0.008)
        self.eyes, self.glints = [], []
        for s in (-1, 1):
            e = L.blob(n + "_eye%d" % s, (s * 0.085, -0.222, 0.02), (0.042, 0.016, 0.062),
                       L.flat("eyeblack", "#2a1d1a"), parent=hd, line=False)
            L.blob(n + "_glint%d" % s, (0.012, -0.012, 0.022), (0.012, 0.006, 0.016), L.flat("glint", "#ffffff"),
                   parent=e, line=False)
            L.blob(n + "_brow%d" % s, (s * 0.088, -0.226, 0.105), (0.04, 0.01, 0.011), HA, parent=hd, line=False,
                   rot=(0, s * 0.15, 0))
            self.eyes.append(e)
        L.blob(n + "_nose", (0, -0.243, -0.03), (0.026, 0.02, 0.02), SK, parent=hd, lw=0.006)
        self.mouth = L.blob(n + "_mouth", (0, -0.226, -0.098), (0.055, 0.02, 0.045), L.flat("mouth", "#8a2b2b"),
                            parent=hd, half=True, lw=0.008)
        L.blob(n + "_tongue", (0, -0.006, -0.03), (0.032, 0.012, 0.016), L.flat("tongue", "#ff7b7b"),
               parent=self.mouth, line=False)
        # hair
        if style == "pigtails":
            L.blob(n + "_cap", (0, 0.04, 0.06), (0.262, 0.232, 0.205), HA, parent=hd)
            L.blob(n + "_fringe", (0, -0.17, 0.15), (0.2, 0.07, 0.07), HA, parent=hd, rot=(0.3, 0, 0))
            for s in (-1, 1):
                L.blob(n + "_tail%d" % s, (s * 0.29, 0.07, 0.0), (0.085, 0.08, 0.13), HA, parent=hd,
                       rot=(0, s * -0.35, 0))
                L.blob(n + "_tie%d" % s, (s * 0.245, 0.055, 0.08), (0.03, 0.03, 0.03), L.toon("tie", "#ff4f9a"),
                       parent=hd, lw=0.006)
        elif style == "short":
            L.blob(n + "_cap", (0, 0.05, 0.07), (0.258, 0.225, 0.195), HA, parent=hd)
            for j, (x, z, r) in enumerate(((-0.10, 0.17, 0.07), (0.0, 0.2, 0.075), (0.1, 0.17, 0.07))):
                L.blob(n + "_spike%d" % j, (x, -0.15, z), (r, 0.05, r * 0.9), HA, parent=hd, rot=(0.4, 0, 0))
        else:  # curly
            L.blob(n + "_cap", (0, 0.05, 0.06), (0.255, 0.225, 0.2), HA, parent=hd)
            rnd = random.Random(n)
            for j in range(11):
                a = -math.pi * 0.9 + j * math.pi * 1.8 / 10
                L.blob(n + "_curl%d" % j, (0.2 * math.sin(a), -0.08 + 0.13 * (1 - math.cos(a)) * 0.6,
                                           0.16 + 0.05 * math.cos(a)),
                       (0.075, 0.07, 0.07), HA, parent=hd, lw=0.008, seg=16)
        # limbs (world-space tubes), hands, shoes
        self.arm = {s: L.tube(n + "_arm%d" % s, SK, 0.034 * k, lw=0.008) for s in (-1, 1)}
        self.leg = {s: L.tube(n + "_leg%d" % s, SK, 0.04 * k, lw=0.009) for s in (-1, 1)}
        self.hand = {s: L.blob(n + "_hand%d" % s, (0, 0, 0), (0.048 * k, 0.045 * k, 0.05 * k), SK, lw=0.008)
                     for s in (-1, 1)}
        self.sock = {s: L.blob(n + "_sock%d" % s, (0, 0, 0), (0.045 * k, 0.045 * k, 0.03 * k), L.toon(n + "_sock", sock),
                               lw=0.007) for s in (-1, 1)}
        self.shoe = {s: L.blob(n + "_shoe%d" % s, (0, 0, 0), (0.055 * k, 0.085 * k, 0.04 * k), SO, lw=0.009)
                     for s in (-1, 1)}
        self.shadow = L.blob(n + "_shadow", (0, 0, 0), (0.26 * k, 0.22 * k, 0.003), L.flat("shadow", "#5aa63a"),
                             line=False, seg=24)

    # -------------------------------------------------------------------------------------------- pose
    ARM_MODES = {
        "rest": lambda s, t: Vector((s * 0.21, 0.0, 0.07 + 0.01 * math.sin(t * 2 + s))),
        "up": lambda s, t: Vector((s * 0.25, -0.03, 0.66 + 0.04 * math.sin(t * 14 + s))),
        "wave": lambda s, t: Vector((0.28 + 0.07 * math.sin(t * 11), -0.06, 0.64)) if s > 0 else
        Vector((-0.21, 0.0, 0.07)),
        "hold": lambda s, t: Vector((s * 0.11, -0.22, 0.2)),
        "wind": lambda s, t: Vector((s * 0.09, 0.12, 0.66)),
        "throw": lambda s, t: Vector((s * 0.1, -0.34, 0.44)),
        "catch": lambda s, t: Vector((s * 0.13, -0.32, 0.30)),
        "sit": lambda s, t: Vector((s * 0.25, 0.14, -0.17)),
        "laugh": lambda s, t: Vector((s * 0.11, -0.17, 0.12 + 0.015 * math.sin(t * 20))),
        "flail": lambda s, t: Vector((s * 0.32, 0.02, 0.45 + 0.1 * math.sin(t * 16 + s * 2))),
        "point": lambda s, t: Vector((0.16, -0.40, 0.42)) if s > 0 else Vector((-0.21, 0.0, 0.07)),
        "worry": lambda s, t: Vector((s * 0.08, -0.2, 0.42)),
        "clap": lambda s, t: Vector((s * (0.03 + 0.06 * abs(math.sin(t * 9))), -0.25, 0.32)),
    }

    def arm_target(self, s, t, gait):
        keys = self.arms
        i = max(j for j in range(len(keys)) if keys[j][0] <= t) if t >= keys[0][0] else 0
        cur = self._mode(keys[i][1], s, t, gait)
        if i > 0:
            w = L.ease((t - keys[i][0]) / 0.28)
            if w < 1:
                cur = self._mode(keys[i - 1][1], s, t, gait).lerp(cur, w)
        return cur

    def _mode(self, m, s, t, gait):
        if m in ("swing", "march"):
            big = 1.6 if m == "march" else 1.0
            return Vector((s * 0.21, gait[s] * big, 0.1 + (0.08 if m == "march" else 0.02)))
        return self.ARM_MODES[m](s, t)

    def pose(self, f):
        t = f / FPS
        a, k = self.act, self.k
        p, yaw, hz, v = a.pos[f], a.yaw[f], a.z[f], a.vel[f]
        sp = v.length
        sit = L.track(self.sit, t)
        fall = L.track(self.fall, t)
        low = max(sit, fall)
        lifts = [a.footlift[j][f] for j in range(2)]
        bob = 0.45 * max(lifts) * (1 - low)
        self.root.location = (p.x, p.y, hz)
        self.root.rotation_euler = (0, 0, yaw)
        laugh = L.track(self.laugh, t)
        lean = min(0.25, sp * 0.09) * (1 - low) - 0.12 * sit - 0.25 * fall
        shake = laugh * 0.05 * math.sin(t * 30)
        self.hips.location = (0, 0, 0.30 - 0.17 * low + bob / k + 0.01 * math.sin(t * 2.2))
        self.hips.rotation_euler = (lean + shake, 0.0, 0)
        # head look
        hy, hp = 0.0, 0.0
        bpy.context.view_layer.update()
        look = a.look_point(t)
        if look is not None:
            if look.z == 0:
                look = look + Vector((0, 0, 0.45))
            M = self.hips.matrix_world.inverted()
            d = (M @ look) - Vector((0, 0, 0.53))
            hy = max(-1.0, min(1.0, math.atan2(d.x, -d.y)))
            hp = max(-0.5, min(0.6, math.atan2(-d.z, math.hypot(d.x, d.y))))
        self.head.rotation_euler = Euler((hp + 0.15 * laugh * math.sin(t * 25), 0.0, hy), "ZXY")
        # face
        mo, happy = L.track(self.expr, t)
        bl = any(0 <= t - b < 0.12 for b in self.blinks)
        for e in self.eyes:
            e.scale = (1, 1, 0.12 if (bl or happy > 0.5) else 1.0)
        self.mouth.scale = (1.0 + 0.2 * mo, 1, 0.35 + mo)
        bpy.context.view_layer.update()
        # legs
        R = Matrix.Rotation(yaw, 3, "Z")
        kick = L.track(self.kick, t)
        kw = L.track(self.kick_w, t)
        for j, s in enumerate((1, -1)):
            foot = a.footp[j][f].copy()
            if low > 0:
                fwdp = p + R @ Vector((s * 0.09 * k, -0.34 * k, 0)) + Vector((0, 0, 0.035 * k + 0.12 * fall * k))
                foot = foot.lerp(fwdp, low)
            if s == -1 and kw > 0:
                # kick: back-swing then a big forward swing with the right foot
                ang = -0.9 + 2.4 * kick
                kp = p + R @ Vector((s * 0.08 * k, -0.30 * k * math.sin(ang), 0)) + \
                    Vector((0, 0, max(0, 0.30 * k * (1 - math.cos(ang)) * 0.7)))
                foot = foot.lerp(kp, kw)
            foot.z += 0.03 * k + hz
            hipp = self.hips.matrix_world @ Vector((s * 0.075, 0, 0.0))
            pts = L.limb(hipp, foot, 0.30 * k, R @ Vector((0, -1, 0.2)))
            L.set_tube(self.leg[s], pts)
            self.sock[s].location = foot + Vector((0, 0, 0.01 * k))
            self.shoe[s].location = foot + R @ Vector((0, -0.025 * k, -0.005 * k))
            self.shoe[s].rotation_euler = (0.0 - 0.6 * low, 0, yaw)
        # arms: swing comes from the feet (opposite to the same-side leg)
        loc_feet = {}
        Mi = self.root.matrix_world.inverted()
        for j, s in enumerate((1, -1)):
            loc_feet[s] = (Mi @ a.footp[j][f]).y
        gait = {s: max(-0.18, min(0.18, -0.9 * loc_feet[s])) for s in (1, -1)}
        for s in (1, -1):
            tl = self.arm_target(s, t, gait)
            hw = self.hips.matrix_world @ tl
            sh = self.hips.matrix_world @ Vector((s * 0.15, 0, 0.29))
            pts = L.limb(sh, hw, 0.27 * k, R @ Vector((s * 0.6, 0.4, -0.4)))
            L.set_tube(self.arm[s], pts)
            self.hand[s].location = hw
            self.hand_world[s] = hw
        self.shadow.location = (p.x, p.y, 0.004)
        sc = max(0.4, 1 - hz * 1.2)
        self.shadow.scale = (sc, sc, 1)

    def _look_point(self, t):
        cur = None
        for tt, x in self.looks:
            if t >= tt:
                cur = x
        return cur() if callable(cur) else cur


# =====================================================================================================  puppy
class Dog:
    def __init__(self, name, start, yaw0):
        self.name = name
        self.act = Actor(name, start, yaw0, feet=[(0.075, -0.15, 0), (-0.075, 0.15, 0), (-0.075, -0.15, 1),
                                                   (0.075, 0.15, 1)],
                         thresh=(0.06, 0.16), stride_t=(0.22, 0.14), lift=(0.035, 0.07), run_v=2.4, turn_rate=9)
        self.looks = [(0.0, None)]
        self.tail = [(0.0, 1.0)]          # wag strength
        self.tongue = [(0.0, 1.0)]
        self.sit = [(0.0, 0.0)]
        self.bow = [(0.0, 0.0)]           # front down (sniff / pick up)
        self.sneeze = []                  # times
        self.cross = [(0.0, 0.0)]         # cross-eyed amount
        self.build()

    def build(self):
        n = self.name
        BR, TAN, DK = L.toon("dog", "#c98a4b"), L.toon("dog_tan", "#f3d7ad"), L.toon("dog_ear", "#7a4a26")
        self.root = L.empty(n)
        self.body = L.empty(n + "_body", self.root, (0, 0, 0.2))
        L.blob(n + "_torso", (0, 0, 0), (0.13, 0.22, 0.12), BR, parent=self.body)
        L.blob(n + "_belly", (0, -0.02, -0.03), (0.1, 0.17, 0.08), TAN, parent=self.body, line=False)
        L.blob(n + "_spot", (0.05, 0.05, 0.1), (0.07, 0.08, 0.03), TAN, parent=self.body, line=False)
        L.blob(n + "_collar", (0, -0.17, 0.06), (0.09, 0.05, 0.08), L.toon("collar", "#2aa7ff"), parent=self.body,
               lw=0.007)
        self.head = L.empty(n + "_head", self.body, (0, -0.22, 0.13))
        hd = self.head
        L.blob(n + "_skull", (0, 0, 0), (0.13, 0.12, 0.12), BR, parent=hd)
        L.blob(n + "_snout", (0, -0.11, -0.035), (0.075, 0.08, 0.055), TAN, parent=hd)
        L.blob(n + "_nose", (0, -0.19, -0.01), (0.032, 0.022, 0.024), L.flat("dognose", "#2a1d1a"), parent=hd,
               lw=0.006)
        self.eyes = []
        for s in (-1, 1):
            e = L.blob(n + "_eye%d" % s, (s * 0.052, -0.105, 0.045), (0.022, 0.01, 0.03),
                       L.flat("eyeblack", "#2a1d1a"), parent=hd, line=False)
            L.blob(n + "_glint%d" % s, (0.006, -0.006, 0.01), (0.007, 0.004, 0.009), L.flat("glint", "#ffffff"),
                   parent=e, line=False)
            self.eyes.append(e)
        self.ears = {s: L.blob(n + "_ear%d" % s, (0, 0, -0.07), (0.045, 0.03, 0.09), DK,
                               parent=L.empty(n + "_earpiv%d" % s, hd, (s * 0.1, 0.01, 0.07)), lw=0.008)
                     for s in (-1, 1)}
        self.mouth_t = L.blob(n + "_tongue", (0.02, -0.13, -0.09), (0.03, 0.035, 0.012), L.toon("dtongue", "#ff7b8b"),
                              parent=hd, lw=0.006)
        self.legs = [L.tube(n + "_leg%d" % j, BR, 0.032, lw=0.008) for j in range(4)]
        self.paws = [L.blob(n + "_paw%d" % j, (0, 0, 0), (0.04, 0.05, 0.028), TAN, lw=0.007) for j in range(4)]
        self.tailo = L.tube(n + "_tail", BR, 0.025, lw=0.007, taper=0.5)
        self.shadow = L.blob(n + "_shadow", (0, 0, 0), (0.2, 0.3, 0.003), L.flat("shadow", "#5aa63a"), line=False,
                             seg=24)
        self.mouth_world = Vector()

    HIPS = [Vector((0.075, -0.15, -0.06)), Vector((-0.075, 0.15, -0.06)), Vector((-0.075, -0.15, -0.06)),
            Vector((0.075, 0.15, -0.06))]

    def pose(self, f):
        t = f / FPS
        a = self.act
        p, yaw, hz, v = a.pos[f], a.yaw[f], a.z[f], a.vel[f]
        sp = v.length
        sit, bow = L.track(self.sit, t), L.track(self.bow, t)
        lifts = [a.footlift[j][f] for j in range(4)]
        bob = 0.5 * max(lifts)
        self.root.location = (p.x, p.y, hz)
        self.root.rotation_euler = (0, 0, yaw)
        sn = 0.0
        for ts in self.sneeze:
            if ts - 0.5 <= t < ts:
                sn = -0.25 * L.ease((t - ts + 0.5) / 0.5)          # breathe in, head up
            elif ts <= t < ts + 0.35:
                sn = 0.45 * math.sin(math.pi * (t - ts) / 0.35)     # achoo: head snaps down
        self.body.location = (0, 0, 0.2 + bob - 0.05 * sit + 0.01 * math.sin(t * 9) * min(1, sp))
        self.body.rotation_euler = (-0.45 * sit + 0.3 * bow + 0.05 * math.sin(t * 18) * min(1, sp / 2), 0, 0)
        hy, hp = 0.0, 0.0
        bpy.context.view_layer.update()
        look = a.look_point(t)
        if look is not None:
            d = (self.body.matrix_world.inverted() @ Vector(look)) - Vector((0, -0.22, 0.13))
            hy = max(-0.9, min(0.9, math.atan2(d.x, -d.y)))
            hp = max(-0.6, min(0.7, math.atan2(-d.z, math.hypot(d.x, d.y))))
        self.head.rotation_euler = Euler((hp + 0.4 * sit + sn + 0.4 * bow, 0, hy + 0.06 * math.sin(t * 3)), "ZXY")
        cross = L.track(self.cross, t)
        for e, s in zip(self.eyes, (-1, 1)):
            e.location = (s * (0.052 - 0.018 * cross), -0.105, 0.045 - 0.01 * cross)
            e.scale = (1, 1, 0.15 if sn > 0.2 else 1.0)
        for s, ear in self.ears.items():
            flop = 0.5 * min(1, sp / 2) + 0.15 * math.sin(t * 12 + s)
            ear.parent.rotation_euler = (-flop * 0.8, s * (0.35 + 0.4 * flop), 0)
        self.mouth_t.hide_render = L.track(self.tongue, t) < 0.5
        self.mouth_t.scale = (1, 1 + 0.2 * math.sin(t * 16), 1)
        bpy.context.view_layer.update()
        R = Matrix.Rotation(yaw, 3, "Z")
        for j in range(4):
            foot = a.footp[j][f].copy()
            if sit > 0 and j in (1, 3):                    # back legs fold under when sitting
                foot = foot.lerp(p + R @ Vector((self.HIPS[j].x * 1.4, 0.05, 0)), sit)
            foot.z += 0.025 + hz
            hp_w = self.body.matrix_world @ self.HIPS[j]
            L.set_tube(self.legs[j], L.limb(hp_w, foot, 0.17, R @ Vector((0, 1 if j in (1, 3) else -1, 0))))
            self.paws[j].location = foot + R @ Vector((0, -0.015, -0.005))
            self.paws[j].rotation_euler = (0, 0, yaw)
        wag = L.track(self.tail, t)
        base = self.body.matrix_world @ Vector((0, 0.2, 0.05))
        sw = wag * 0.12 * math.sin(t * 22)
        tip = self.body.matrix_world @ Vector((sw, 0.33, 0.22))
        mid = self.body.matrix_world @ Vector((sw * 0.4, 0.29, 0.12))
        L.set_tube(self.tailo, [base, mid, tip])
        self.mouth_world = self.head.matrix_world @ Vector((0, -0.2, -0.06))
        self.nose_world = self.head.matrix_world @ Vector((0, -0.2, 0.02))
        self.shadow.location = (p.x, p.y, 0.004)
        sc = max(0.4, 1 - hz * 1.5)
        self.shadow.scale = (sc, sc, 1)
        self.shadow.rotation_euler = (0, 0, yaw)


# =====================================================================================================  ducks
class Duck:
    def __init__(self, name, start, yaw0, k=1.0, baby=False, pond=None):
        self.name, self.k, self.baby = name, k, baby
        self.in_pond = pond
        self.act = Actor(name, start, yaw0, feet=[(0.05 * k, 0, 0), (-0.05 * k, 0, 1)],
                         thresh=(0.035 * k, 0.07 * k), stride_t=(0.16, 0.12), lift=(0.025 * k, 0.035 * k), run_v=1.0,
                         turn_rate=5)
        self.looks = [(0.0, None)]
        self.peck = [(0.0, 0.0)]
        self.quacks = []
        self.build()

    def build(self):
        n, k = self.name, self.k
        BODY = L.toon(n + "_c", "#ffe14d" if self.baby else "#ffffff", shade=0.86)
        BEAK = L.toon("beak", "#ff9a1f")
        self.root = L.empty(n)
        self.root.scale = (k, k, k)
        self.body = L.empty(n + "_body", self.root, (0, 0, 0.12))
        L.blob(n + "_torso", (0, 0.02, 0), (0.12, 0.17, 0.1), BODY, parent=self.body)
        L.blob(n + "_tail", (0, 0.16, 0.05), (0.05, 0.06, 0.04), BODY, parent=self.body, rot=(-0.6, 0, 0), lw=0.008)
        for s in (-1, 1):
            L.blob(n + "_wing%d" % s, (s * 0.1, 0.04, 0.02), (0.03, 0.11, 0.06), BODY, parent=self.body, lw=0.008)
        self.neck = L.empty(n + "_neck", self.body, (0, -0.11, 0.06))
        L.blob(n + "_neckb", (0, 0, 0.05), (0.055, 0.055, 0.08), BODY, parent=self.neck, lw=0.008)
        self.head = L.empty(n + "_head", self.neck, (0, -0.01, 0.13))
        L.blob(n + "_skull", (0, 0, 0), (0.075, 0.075, 0.07), BODY, parent=self.head)
        L.blob(n + "_beak", (0, -0.085, -0.012), (0.04, 0.05, 0.016), BEAK, parent=self.head, lw=0.007)
        for s in (-1, 1):
            e = L.blob(n + "_eye%d" % s, (s * 0.04, -0.055, 0.02), (0.014, 0.008, 0.02),
                       L.flat("eyeblack", "#2a1d1a"), parent=self.head, line=False)
            L.blob(n + "_glint%d" % s, (0.004, -0.004, 0.007), (0.005, 0.003, 0.006), L.flat("glint", "#ffffff"),
                   parent=e, line=False)
        self.feet = [L.blob(n + "_foot%d" % j, (0, 0, 0), (0.035 * k, 0.045 * k, 0.008 * k), BEAK, lw=0.006)
                     for j in range(2)]
        self.shadow = L.blob(n + "_shadow", (0, 0, 0), (0.16 * k, 0.22 * k, 0.003), L.flat("shadow", "#5aa63a"),
                             line=False, seg=20)
        self.ripples = [L.ring(n + "_rip%d" % j, L.flat("ripple", "#c9eeff")) for j in range(3)]

    def pose(self, f):
        t = f / FPS
        a, k = self.act, self.k
        p, yaw, v = a.pos[f], a.yaw[f], a.vel[f]
        sp = v.length
        water = self.in_pond(p)
        self.root.location = (p.x, p.y, 0)
        self.root.rotation_euler = (0, 0, yaw)
        lifts = [a.footlift[j][f] for j in range(2)]
        waddle = 0.0 if water else (a.footp[0][f].z - a.footp[1][f].z) * 6
        pk = L.track(self.peck, t)
        z = (0.035 + 0.01 * math.sin(t * 3 + k * 5)) if water else 0.12 + 0.4 * max(lifts) / k
        self.body.location = (0, 0, z / 1.0)
        self.body.rotation_euler = (0.05 * pk, waddle, 0)
        bpy.context.view_layer.update()
        look = None
        for tt, x in self.looks:
            if t >= tt:
                look = x
        hy = 0.0
        if callable(look):
            look = look()
        if look is not None:
            d = self.body.matrix_world.inverted() @ Vector(look)
            hy = max(-0.8, min(0.8, math.atan2(d.x, -d.y)))
        q = 0.0
        for tq in self.quacks:
            if 0 <= t - tq < 0.25:
                q = math.sin(math.pi * (t - tq) / 0.25)
        self.neck.rotation_euler = (0.9 * pk - 0.2 * q, 0, hy * 0.5)
        self.head.rotation_euler = (0.4 * pk + 0.3 * q, 0, hy * 0.5 + 0.08 * math.sin(t * 2.5 + k))
        R = Matrix.Rotation(yaw, 3, "Z")
        for j, ft in enumerate(self.feet):
            ft.hide_render = water
            ft.location = a.footp[j][f] + Vector((0, 0, 0.008))
            ft.rotation_euler = (0, 0, yaw)
        self.shadow.hide_render = water
        self.shadow.location = (p.x, p.y, 0.004)
        for j, r in enumerate(self.ripples):
            age = ((t * 0.9 + j / 3.0) % 1.0)
            r.hide_render = not water or sp < 0.05
            if water and sp >= 0.05:
                back = a.pos[max(0, f - int(age * FPS / 0.9))]
                rr = (0.10 + 0.20 * age) * k
                r.location = (back.x, back.y, 0.021)
                r.scale = (rr, rr * 1.0, 1)
                r.hide_render = age > 0.85
        self.beak_world = self.head.matrix_world @ Vector((0, -0.12, -0.01))
