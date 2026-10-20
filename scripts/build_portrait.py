#!/usr/bin/env python3
"""
Composite the owner's REAL photograph into a neon HUD frame.

    python scripts/build_portrait.py                      # uses scripts/source/portrait-original.png
    python scripts/build_portrait.py --input me.png --out assets/portrait-frame.png

Only the supplied photo is used. Nothing is generated or replaced: the script crops it to a
square, adds a faint scanline/vignette grade, then draws the HUD frame around it with Pillow.
Requires: pip install pillow
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 640, 740
PHOTO = 520
PX, PY = (W - PHOTO) // 2, 96
CYAN, BLUE, GREEN, PURPLE = (0, 229, 255), (41, 121, 255), (57, 255, 150), (157, 92, 255)
BG_TOP, BG_BOT = (4, 8, 16), (8, 16, 34)
MONO_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
             "C:/Windows/Fonts/consolab.ttf", "/System/Library/Fonts/Menlo.ttc"]
MONO = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consola.ttf", "/System/Library/Fonts/Menlo.ttc"]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def background():
    bg = Image.new("RGB", (W, H), BG_TOP)
    px = bg.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(grid)
    for x in range(0, W, 32):
        g.line([(x, 0), (x, H)], fill=CYAN + (14,), width=1)
    for y in range(0, H, 32):
        g.line([(0, y), (W, y)], fill=CYAN + (14,), width=1)
    return Image.alpha_composite(bg.convert("RGBA"), grid)


def prepare_photo(path):
    im = Image.open(path).convert("RGB")
    s = min(im.size)
    left, top = (im.width - s) // 2, (im.height - s) // 2
    im = im.crop((left, top, left + s, top + s)).resize((PHOTO, PHOTO), Image.LANCZOS)
    # faint scanlines (a display-like texture; the face itself is untouched)
    sl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sl)
    for y in range(0, PHOTO, 4):
        d.line([(0, y), (PHOTO, y)], fill=(0, 20, 40, 30), width=1)
    im = Image.alpha_composite(im.convert("RGBA"), sl)
    # gentle vignette so the photo sits inside the dark environment
    vig = Image.new("L", im.size, 0)
    ImageDraw.Draw(vig).ellipse([-PHOTO * 0.12, -PHOTO * 0.12, PHOTO * 1.12, PHOTO * 1.12], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(70))
    dark = Image.new("RGBA", im.size, (3, 8, 18, 255))
    im = Image.composite(im, dark, ImageChops.add(vig, Image.new("L", im.size, 110)))
    # chamfered corner mask
    cut = 34
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon([(cut, 0), (PHOTO - cut, 0), (PHOTO, cut), (PHOTO, PHOTO - cut),
                                  (PHOTO - cut, PHOTO), (cut, PHOTO), (0, PHOTO - cut), (0, cut)], fill=255)
    return im, mask, cut


def glow_layer(draw_fn, blur=8, strength=1.0):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    glow = layer.filter(ImageFilter.GaussianBlur(blur))
    if strength != 1.0:
        glow.putalpha(glow.getchannel("A").point(lambda v: min(255, int(v * strength))))
    return glow, layer


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--input", default=os.path.join(here, "source", "portrait-original.png"))
    ap.add_argument("--out", default=os.path.join(here, "..", "assets", "portrait-frame.png"))
    ap.add_argument("--jpeg", default=os.path.join(here, "source", "portrait-frame-embed.jpg"),
                    help="smaller JPEG copy that build_assets.py embeds inside hero.svg")
    a = ap.parse_args()

    canvas = background()
    photo, mask, cut = prepare_photo(a.input)
    cx, cy = PX, PY
    pts = [(cx + cut, cy), (cx + PHOTO - cut, cy), (cx + PHOTO, cy + cut), (cx + PHOTO, cy + PHOTO - cut),
           (cx + PHOTO - cut, cy + PHOTO), (cx + cut, cy + PHOTO), (cx, cy + PHOTO - cut), (cx, cy + cut)]

    glow, _ = glow_layer(lambda d: d.polygon(pts, outline=CYAN + (255,), width=5), blur=10, strength=1.6)
    canvas = Image.alpha_composite(canvas, glow)
    canvas.paste(photo, (cx, cy), mask)
    d = ImageDraw.Draw(canvas)
    d.polygon(pts, outline=CYAN + (255,), width=3)

    off, ln, th = 22, 64, 5
    def brackets(dd):
        x0, y0, x1, y1 = cx - off, cy - off, cx + PHOTO + off, cy + PHOTO + off
        for (x, y, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            dd.line([(x, y), (x + sx * ln, y)], fill=CYAN + (255,), width=th)
            dd.line([(x, y), (x, y + sy * ln)], fill=CYAN + (255,), width=th)
    g2, l2 = glow_layer(brackets, blur=6, strength=1.4)
    canvas = Image.alpha_composite(canvas, g2)
    canvas = Image.alpha_composite(canvas, l2)
    d = ImageDraw.Draw(canvas)

    for i in range(0, PHOTO + 1, 26):  # edge tick marks
        L = 12 if (i // 26) % 2 == 0 else 6
        d.line([(cx - off - 6, cy + i), (cx - off - 6 - L, cy + i)], fill=CYAN + (170,), width=2)
        d.line([(cx + PHOTO + off + 6, cy + i), (cx + PHOTO + off + 6 + L, cy + i)], fill=CYAN + (170,), width=2)

    fb, fm = font(MONO_BOLD, 22), font(MONO, 17)
    left, right = cx - off, W - cx + off
    d.text((left, 28), "SABER://ID", font=fb, fill=CYAN + (255,))
    d.ellipse([right - 112, 36, right - 100, 48], fill=GREEN + (255,))
    d.text((right - 90, 29), "ONLINE", font=fb, fill=GREEN + (255,))
    d.line([(left, 66), (right, 66)], fill=CYAN + (120,), width=1)

    fy = cy + PHOTO + off + 28
    d.line([(left, fy), (right, fy)], fill=CYAN + (120,), width=1)
    d.text((left, fy + 10), "SABER BARHOUMI", font=fb, fill=(230, 245, 255, 255))
    d.text((left, fy + 40), "github.com/saber-barhoumi", font=fm, fill=CYAN + (230,))
    seed, x = 188176268, right - 150  # barcode ticks seeded from the public GitHub user id
    for i in range(40):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        wdt = 2 + (seed >> 16) % 3
        if x + wdt > right:
            break
        d.rectangle([x, fy + 14, x + wdt - 1, fy + 52], fill=(PURPLE if i % 7 == 0 else CYAN) + (200,))
        x += wdt + 2

    out = canvas.convert("RGB")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    out.save(a.out, optimize=True)
    out.save(a.jpeg, quality=84, optimize=True)
    print("wrote", a.out, out.size, round(os.path.getsize(a.out) / 1024), "KB;",
          a.jpeg, round(os.path.getsize(a.jpeg) / 1024), "KB")


if __name__ == "__main__":
    main()
