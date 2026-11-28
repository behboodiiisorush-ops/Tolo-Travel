"""Final-render settings shared by every Zombie Center scene (CPU only here: Cycles + denoiser beats EEVEE on
llvmpipe ~6x: 36 s vs 3.6 min per 720p frame, measured 28 Nov).

    import finalize; finalize.apply(sc)        # in each scene's MODE == "final" branch, before rendering
Env: FINAL_SAMPLES (24), FINAL_EXPOSURE (scene default − 1.6 stops: night without fog volumes), ZC_FOG must be 0.
"""
import os


def apply(sc, exposure_shift=-1.6):
    sc.render.engine = "CYCLES"
    c = sc.cycles
    c.device = "CPU"
    c.samples = int(os.environ.get("FINAL_SAMPLES", 24))
    c.use_adaptive_sampling = True
    c.use_denoising = True; c.denoiser = "OPENIMAGEDENOISE"
    c.max_bounces = 4; c.diffuse_bounces = 2; c.glossy_bounces = 2; c.transmission_bounces = 2
    c.volume_bounces = 0; c.transparent_max_bounces = 8
    c.caustics_reflective = False; c.caustics_refractive = False
    sc.render.threads_mode = "AUTO"
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.image_settings.file_format = "PNG"
    vs = sc.view_settings
    if "FINAL_EXPOSURE" in os.environ:
        vs.exposure = float(os.environ["FINAL_EXPOSURE"])
    else:
        ad = sc.animation_data
        animated = bool(ad and ad.action and any("exposure" in fc.data_path for fc in getattr(ad.action, "fcurves", [])))
        if animated:                                   # keyed exposure (e.g. a flash): shift every key
            for fc in ad.action.fcurves:
                if "exposure" in fc.data_path:
                    for k in fc.keyframe_points:
                        k.co.y += exposure_shift; k.handle_left.y += exposure_shift; k.handle_right.y += exposure_shift
        else:
            vs.exposure = vs.exposure + exposure_shift
