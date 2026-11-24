"""First-person POV rig: a full 'me' body (so arms, hands and the walk are real), the camera sits in its head.

    import pov
    me = pov.POV(house_collection)
    me.animate(f, t, pos, facing, walk=1, phase=..., look=(yaw, pitch))
    me.reach("r", f0, f1, target_location_or_object, f_release)   # hand goes to a handle / switch (IK)
    me.flush()
Hands enter and leave the frame through IK blending (no floating hands); the camera follows the head bone,
so walking, turning and looking give natural, subtle camera motion.
"""
import bpy, math
from mathutils import Vector
import characters as C
import props as P


class POV(C.StudioCharacter):
    def __init__(self, look_key="arian", name="Me"):
        super().__init__(look_key, name=name)
        for o in self.face_objects:            # my own head is never seen
            o.hide_render = True
        rig = self.rig
        self.ik = {}
        for side in ("l", "r"):
            tgt = P.empty(f"{name} hand target {side}")
            c = rig.pose.bones[f"lowerarm_{side}"].constraints.new("IK")
            c.target = tgt
            c.chain_count = 2
            c.influence = 0.0
            self.ik[side] = (tgt, c)
        # camera at the eyes, following the head bone
        cam = bpy.data.objects.new("POV camera", bpy.data.cameras.new("POV camera"))
        bpy.context.scene.collection.objects.link(cam)
        cam.data.lens = 17
        cam.data.sensor_width = 36
        cam.data.clip_start = 0.06
        self.cam = cam
        self._cam_bound = False

    def bind_camera(self, frame):
        """Call after the first animate(): puts the camera at the eyes and makes it follow the head."""
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        rig = self.rig
        hw = rig.matrix_world @ rig.pose.bones["head"].head
        fwd = (rig.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
        eye = hw + Vector((0, 0, 0.1)) + fwd * 0.09
        self.cam.location = eye
        self.cam.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
        c = self.cam.constraints.new("CHILD_OF")
        c.target = rig
        c.subtarget = "head"
        bpy.context.view_layer.update()
        c.inverse_matrix = (rig.matrix_world @ rig.pose.bones["head"].matrix).inverted()
        self._cam_bound = True

    def reach(self, side, f_in, f_hold, target, f_out, lift=0.0):
        """IK hand to target (Vector or object) between f_in..f_out; target keyed per frame if it moves."""
        tgt, c = self.ik[side]
        for f, v in ((f_in - 8, 0.0), (f_in, 1.0), (f_out, 1.0), (f_out + 8, 0.0)):
            c.influence = v
            c.keyframe_insert("influence", frame=f)
        for f in range(f_in - 8, f_out + 9):
            if hasattr(target, "matrix_world"):
                bpy.context.scene.frame_set(f)
                bpy.context.view_layer.update()
                p = target.matrix_world.translation.copy()
            else:
                p = Vector(target)
            tgt.location = p + Vector((0, 0, lift))
            tgt.keyframe_insert("location", frame=f)
