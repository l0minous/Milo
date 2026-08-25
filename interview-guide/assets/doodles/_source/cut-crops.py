"""Cut each drawing out of the user's sketch as a tight, transparent PNG.

Nothing here redraws anything -- every output is a pixel-for-pixel region of
the original file, trimmed to its own ink and padded slightly.
"""
import json
import os

import numpy as np
from PIL import Image

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sketch-original.webp")
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.makedirs(OUT, exist_ok=True)

im = Image.open(SRC).convert("RGBA")
arr = np.array(im)
alpha = arr[..., 3]
print("alpha: min=%d max=%d  transparent px=%d (%.1f%%)" % (
    alpha.min(), alpha.max(), int((alpha == 0).sum()), 100 * (alpha == 0).mean()))

# Ink = anything not fully transparent and not near-white.
rgb = arr[..., :3].astype(float)
a = (alpha.astype(float) / 255.0)[..., None]
grey = (rgb * a + 255.0 * (1 - a)).mean(axis=2)
ink = grey < 128

# Component boxes found by detect2.py (radius=6), mapped to names.
# (x0, y0, x1, y1) in source pixels.
BOXES = {
    "person-laptop": (320, 314, 468, 451),
    "party-popper":  (582, 353, 711, 496),
    "lightbulb":     (448, 577, 523, 665),
    "house":         (245, 646, 334, 736),
    "cloud-1":       (793, 338, 904, 375),
    "cloud-2":       (959, 315, 1068, 352),
    "cloud-3":       (1152, 338, 1304, 371),
    "cloud-4":       (872, 414, 961, 452),
    "cloud-5":       (1027, 404, 1094, 436),
    "sparkle-1":     (1189, 409, 1214, 448),
    "sparkle-2":     (1087, 445, 1107, 481),
    "sparkle-3":     (1145, 461, 1167, 507),
    "sparkle-4":     (1028, 491, 1052, 557),
    "sparkle-5":     (1197, 506, 1220, 565),
    "sparkle-6":     (1094, 515, 1113, 555),
    # Full handwritten title block, both lines together.
    "title":         (686, 605, 1155, 741),
}

PAD = 6
manifest = {}

for name, (x0, y0, x1, y1) in BOXES.items():
    # Re-trim to the ink actually inside the box so padding is even.
    region = ink[y0:y1 + 1, x0:x1 + 1]
    yy, xx = np.where(region)
    if len(yy) == 0:
        print("!! no ink in", name)
        continue
    tx0 = x0 + int(xx.min()) - PAD
    tx1 = x0 + int(xx.max()) + PAD
    ty0 = y0 + int(yy.min()) - PAD
    ty1 = y0 + int(yy.max()) + PAD
    tx0, ty0 = max(0, tx0), max(0, ty0)
    tx1, ty1 = min(im.width - 1, tx1), min(im.height - 1, ty1)

    crop = im.crop((tx0, ty0, tx1 + 1, ty1 + 1))

    # Guard: make sure we didn't drag in ink from a neighbouring drawing.
    sub = np.array(crop)
    sub_grey = (sub[..., :3].astype(float) * (sub[..., 3:4].astype(float) / 255.0)
                + 255.0 * (1 - sub[..., 3:4].astype(float) / 255.0)).mean(axis=2)
    sub_ink = int((sub_grey < 128).sum())
    expected = int(ink[y0:y1 + 1, x0:x1 + 1].sum())

    path = os.path.join(OUT, f"{name}.png")
    crop.save(path, optimize=True)
    manifest[name] = {
        "file": f"{name}.png",
        "src_box": [tx0, ty0, tx1, ty1],
        "w": crop.width,
        "h": crop.height,
        "ink": sub_ink,
    }
    flag = "" if sub_ink == expected else f"  <-- +{sub_ink - expected} px from neighbours"
    print(f"{name:15s} {crop.width:4d}x{crop.height:<4d} ink={sub_ink:5d} "
          f"src=({tx0},{ty0})-({tx1},{ty1}) {os.path.getsize(path)//1024}KB{flag}")

with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
print(f"\nwrote {len(manifest)} crops to {OUT}")
