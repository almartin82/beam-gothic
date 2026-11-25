"""Proof renderer. Draws straight from the compiled TTF, shaped with HarfBuzz, so kerning,
marks and locl show exactly as a browser would set them.

  proof.py text OUT.png [--size N] [--lang TRK] [--features kern=0] "LINE" "LINE" ...
  proof.py grid OUT.png [--cell N] [--cols N] glyphname glyphname ...   (or --all)
"""
import argparse
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TTF = ROOT / "fonts/ttf/BeamGothic-Regular.ttf"
SS = 3  # supersampling


class Face:
    def __init__(self, path=DEFAULT_TTF):
        self.path = str(path)
        self.tt = TTFont(self.path)
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(self.path)))
        self._rings = {}

    def rings(self, name):
        if name not in self._rings:
            pen = DecomposingRecordingPen(self.gs)
            self.gs[name].draw(pen)
            rings, cur = [], []
            for op, args in pen.value:
                if op == "moveTo":
                    cur = [args[0]]
                elif op == "lineTo":
                    cur.append(args[0])
                elif op in ("closePath", "endPath"):
                    if len(cur) > 2:
                        rings.append(cur)
                    cur = []
                else:
                    raise ValueError(f"{name}: curve segment {op} in a no-curves font")
            self._rings[name] = rings
        return self._rings[name]

    def shape(self, text, lang=None, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        if lang:
            buf.language = lang
        hb.shape(self.hbfont, buf, features or {})
        return [(self.order[i.codepoint], p.x_advance, p.x_offset, p.y_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def draw_glyph(mask, face, name, ox, oy, scale):
    """Even-odd fill of one glyph into an 'L' mask. (ox, oy) is the origin in pixels, y up."""
    for ring in face.rings(name):
        tmp = Image.new("1", mask.size, 0)
        ImageDraw.Draw(tmp).polygon([(ox + x * scale, oy - y * scale) for x, y in ring], fill=1)
        mask.paste(ImageChops.logical_xor(mask.convert("1"), tmp).convert("L"))


def render_text(face, lines, out, size=120, lang=None, features=None, width=None):
    scale = size / 1000 * SS
    line_h = int(size * 1.42 * SS)
    shaped = [face.shape(t, lang, features) for t in lines]
    w = width * SS if width else int(max(sum(a for _, a, _, _ in s) for s in shaped) * scale) + 60 * SS
    mask = Image.new("L", (w, line_h * len(lines) + 30 * SS), 0)
    for li, run in enumerate(shaped):
        x, base = 30 * SS, int(line_h * li + size * 1.08 * SS)
        for name, adv, dx, dy in run:
            draw_glyph(mask, face, name, x + dx * scale, base - dy * scale, scale)
            x += adv * scale
    img = ImageChops.invert(mask).resize((mask.width // SS, mask.height // SS), Image.LANCZOS)
    img.save(out)
    return out


def render_grid(face, names, out, cell=230, cols=10):
    scale = cell * 0.62 / 1000 * SS
    cw, ch = cell * SS, int(cell * 1.05 * SS)
    rows = (len(names) + cols - 1) // cols
    mask = Image.new("L", (cw * cols, ch * rows), 0)
    guides = Image.new("L", mask.size, 255)
    gd = ImageDraw.Draw(guides)
    try:
        lab = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11 * SS)
    except OSError:
        lab = ImageFont.load_default()
    hmtx = face.tt["hmtx"]
    for i, name in enumerate(names):
        cx, cy = (i % cols) * cw, (i // cols) * ch
        adv = hmtx[name][0]
        ox = cx + (cw - adv * scale) / 2
        base = cy + ch * 0.74
        for y, tone in ((0, 150), (700, 190), (-200, 225), (900, 225)):
            gd.line([(cx + 4, base - y * scale), (cx + cw - 4, base - y * scale)], fill=tone, width=SS)
        for x in (0, adv):
            gd.line([(ox + x * scale, base - 930 * scale), (ox + x * scale, base + 220 * scale)], fill=200, width=SS)
        gd.rectangle([cx, cy, cx + cw - 1, cy + ch - 1], outline=235)
        gd.text((cx + 6 * SS, cy + 4 * SS), name, fill=90, font=lab)
        draw_glyph(mask, face, name, ox, base, scale)
    img = ImageChops.multiply(guides, ImageChops.invert(mask))
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
    img.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("text")
    t.add_argument("out"); t.add_argument("lines", nargs="+")
    t.add_argument("--size", type=int, default=120); t.add_argument("--lang"); t.add_argument("--font", default=DEFAULT_TTF)
    t.add_argument("--features", default="")
    g = sub.add_parser("grid")
    g.add_argument("out"); g.add_argument("names", nargs="*")
    g.add_argument("--all", action="store_true"); g.add_argument("--cell", type=int, default=230)
    g.add_argument("--cols", type=int, default=10); g.add_argument("--font", default=DEFAULT_TTF)
    a = ap.parse_args()
    face = Face(a.font)
    if a.cmd == "text":
        feats = {k: bool(int(v)) for k, v in (kv.split("=") for kv in a.features.split(",") if kv)}
        render_text(face, a.lines, a.out, a.size, a.lang, feats)
    else:
        names = [n for n in face.order if n != ".notdef"] if a.all else a.names
        render_grid(face, names, a.out, a.cell, a.cols)
    print(a.out)


if __name__ == "__main__":
    main()
