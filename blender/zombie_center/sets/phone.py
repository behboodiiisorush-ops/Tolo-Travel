"""PROP_PHONE_ARIN — a plain dark phone (no logo) with a glowing screen image.

    import phone
    img = phone.screen_lock("/path/out.png")        # lock screen: «نیکا — ۱ ویدیوی جدید»
    ph = phone.build(img)                            # object; screen strength in ph["screen_mat"]
Screens are drawn with Pillow + raqm in Vazirmatn (Persian shaping) at 540x1170.
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "fonts", "Vazirmatn-FD-ExtraBold.ttf")
W, H = 540, 1170


def _font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)


def _bg():
    im = Image.new("RGB", (W, H), (10, 14, 26))
    d = ImageDraw.Draw(im)
    for y in range(H):                                   # soft dark-blue gradient wallpaper (no picture, no brand)
        c = int(18 + 22 * (y / H))
        d.line([(0, y), (W, y)], fill=(8, 12 + c // 3, 24 + c))
    return im


def _rtl(d, xy, text, size, fill, anchor="mm"):
    d.text(xy, text, font=_font(size), fill=fill, anchor=anchor, direction="rtl", language="fa")


def screen_lock(path, time_txt="۲۲:۴۰", name="نیکا", line="۱ ویدیوی جدید", ago="ارسال: ۲ ساعت پیش"):
    im = _bg(); d = ImageDraw.Draw(im)
    d.text((W // 2, 210), time_txt, font=_font(120), fill=(235, 238, 245), anchor="mm")
    # notification card
    card = Image.new("RGBA", (W - 60, 190), (255, 255, 255, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, W - 61, 189], 28, fill=(40, 46, 60, 225))
    im.paste(card, (30, 470), card)
    _rtl(d, (W - 70, 520), name, 44, (250, 250, 252), "ra")
    _rtl(d, (W - 70, 585), line, 34, (210, 214, 222), "ra")
    _rtl(d, (W - 70, 630), ago, 26, (150, 156, 170), "ra")
    d.ellipse([60, 520, 140, 600], fill=(70, 80, 100))         # contact circle, no photo
    im.save(path)
    return path


def screen_call(path, label="شماره‌ی ناشناس", sub="در حال تماس…"):
    im = _bg(); d = ImageDraw.Draw(im)
    _rtl(d, (W // 2, 330), label, 52, (245, 245, 250))
    _rtl(d, (W // 2, 400), sub, 30, (170, 176, 190))
    d.ellipse([W // 2 - 80, 90, W // 2 + 80, 250], fill=(60, 66, 82))
    for x, col in ((150, (200, 50, 50)), (W - 150, (50, 170, 80))):
        d.ellipse([x - 55, 940, x + 55, 1050], fill=col)
    im.save(path)
    return path


def screen_off(path):
    Image.new("RGB", (W, H), (2, 2, 3)).save(path)
    return path


def build(screen_path, name="PROP_PHONE_ARIN", strength=2.5):
    import bpy, props as P
    body = P.mat(name + "_body", (0.03, 0.03, 0.035), rough=0.35, metal=0.3)
    o = P.box((0, 0, 0.0045), (0.072, 0.152, 0.009), body, name, bevel=0.004)
    scr = bpy.data.materials.new(name + "_screen"); scr.use_nodes = True
    nt = scr.node_tree; p = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(screen_path, check_existing=False)
    nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = strength
    p.inputs["Roughness"].default_value = 0.05
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0092))
    s = bpy.context.object; s.name = name + "_screen"; s.scale = (0.066, 0.145, 1)
    bpy.ops.object.transform_apply(scale=True)
    s.data.materials.append(scr)
    s.parent = o
    o["screen_mat"] = scr.name
    o["screen_tex"] = tex.name
    light = bpy.data.lights.new(name + "_glow", "AREA"); light.energy = 0.8; light.size = 0.1; light.color = (0.6, 0.7, 1.0)
    lo = bpy.data.objects.new(name + "_glow", light); lo.location = (0, 0, 0.03); lo.parent = o
    bpy.context.scene.collection.objects.link(lo)
    return o
