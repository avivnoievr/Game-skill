"""Objective image metrics and grayscale copies for screenshots from any engine (Godot, Unity, renders).

Same metrics and flag thresholds as scripts/web/capture.mjs, so art-critic can treat all engines alike.
Usage (Blender):  blender -b --factory-startup --python-exit-code 1 -P image_metrics.py -- IMG [IMG ...] [--gray] [--json out.json]
Usage (pip bpy):  python image_metrics.py IMG [IMG ...] [--gray] [--json out.json]
Exit codes: 0 = ok, 1 = at least one blank image (nothing rendered), 2 = usage/load error.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
import numpy as np  # noqa: E402

from gs_common import die, script_args  # noqa: E402


def load_rgb(path):
    """RGB as uint8-range floats, rows bottom-up (Blender order; irrelevant for these metrics)."""
    try:
        img = bpy.data.images.load(os.path.abspath(path), check_existing=False)
    except RuntimeError as e:
        die(f"cannot load {path}: {e}")
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return np.clip(px.reshape(h, w, 4)[..., :3] * 255.0, 0, 255)


def metrics(rgb):
    h, w, _ = rgb.shape
    W = 320
    H = max(3, round(h * W / w))
    small = rgb[(np.arange(H) * h // H)[:, None], (np.arange(W) * w // W)[None, :]]
    r, g, b = small[..., 0], small[..., 1], small[..., 2]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    q = small.astype(np.uint8) >> 5
    keys = (q[..., 0].astype(np.int32) << 6) | (q[..., 1].astype(np.int32) << 3) | q[..., 2]
    counts = np.bincount(keys.ravel(), minlength=512)
    p = counts[counts > 0] / keys.size
    mx, mn = small.max(axis=2), small.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    gx = (lum[:-2, 2:] + 2 * lum[1:-1, 2:] + lum[2:, 2:]) - (lum[:-2, :-2] + 2 * lum[1:-1, :-2] + lum[2:, :-2])
    gy = (lum[2:, :-2] + 2 * lum[2:, 1:-1] + lum[2:, 2:]) - (lum[:-2, :-2] + 2 * lum[:-2, 1:-1] + lum[:-2, 2:])
    return {
        "lumaMean": round(float(lum.mean()), 1), "lumaStd": round(float(lum.std()), 1),
        "colorEntropyBits": round(float(-(p * np.log2(p)).sum()), 2),
        "dominantColorShare": round(float(counts.max() / keys.size), 3),
        "edgeDensity": round(float((np.hypot(gx, gy) > 96).mean()), 4),
        "saturationMean": round(float(sat.mean()), 3),
        "clippedShadows": round(float((lum < 5).mean()), 3), "clippedHighlights": round(float((lum > 250).mean()), 3),
    }


def flags(m):
    out = []
    if m["lumaStd"] < 30:
        out.append("low contrast (lumaStd < 30)")
    if m["colorEntropyBits"] < 3:
        out.append("very few distinct colors (entropy < 3 bits)")
    if m["dominantColorShare"] > 0.6:
        out.append("one color fills >60% of the frame")
    if m["edgeDensity"] < 0.02:
        out.append("little visible structure (edgeDensity < 0.02)")
    if m["clippedHighlights"] > 0.05:
        out.append("blown highlights (>5% pure white)")
    if m["clippedShadows"] > 0.15:
        out.append("crushed shadows (>15% pure black)")
    return out


def write_gray(rgb, path):
    h, w, _ = rgb.shape
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    rgba = np.dstack([lum, lum, lum, np.ones_like(lum)]).astype(np.float32)
    img = bpy.data.images.new("gs_gray", w, h, alpha=True)
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def main():
    p = argparse.ArgumentParser(prog="image_metrics.py", description=__doc__.split("\n")[0])
    p.add_argument("images", nargs="+")
    p.add_argument("--gray", action="store_true", help="also write <name>_gray.png next to each image")
    p.add_argument("--json")
    a = p.parse_args(script_args())
    results, blank = [], 0
    for path in a.images:
        if not os.path.isfile(path):
            die(f"file not found: {path}")
        rgb = load_rgb(path)
        m = metrics(rgb)
        is_blank = m["lumaStd"] < 3 and m["dominantColorShare"] > 0.97
        blank += is_blank
        entry = {"file": os.path.abspath(path), "metrics": m, "flags": flags(m), "blank": is_blank}
        if a.gray:
            entry["grayFile"] = os.path.splitext(os.path.abspath(path))[0] + "_gray.png"
            write_gray(rgb, entry["grayFile"])
        results.append(entry)
        print(f"{os.path.basename(path)}: lumaStd {m['lumaStd']} entropy {m['colorEntropyBits']} "
              f"dominant {m['dominantColorShare']} edges {m['edgeDensity']}"
              + (f"  FLAGS: {'; '.join(entry['flags'])}" if entry["flags"] else "") + ("  BLANK" if is_blank else ""))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
    sys.exit(1 if blank else 0)


if __name__ == "__main__":
    main()
