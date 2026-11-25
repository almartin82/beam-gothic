"""Draw the panel sheets: for each open decision, every option built into the font itself and set
in words from the source. Writes documentation/panel/<decision>.png. The pictures are evidence;
the recommendation and its reasoning are written in the dossier, not here."""
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "sources"))
from beam import decisions  # noqa: E402
from proof import Face, render_text  # noqa: E402

WORDS = {
    "P2-ampersand": ["BETHLEHEM STEEL & IRON", "H-PILES & SHAPES &"],
    "P2-at": ["STEEL@BETHLEHEM @ 1961", "SHAPES @ SPARROWS POINT"],
    "P2-lowercase": ["Bethlehem Steel", "Structural Shapes, 1961"],
}
OUT = ROOT / "documentation/panel"
WORK = ROOT / "build/panel"


def build_variant(key, opt):
    WORK.mkdir(parents=True, exist_ok=True)
    ufo, ttf = WORK / f"{key}-{opt}.ufo", WORK / f"{key}-{opt}.ttf"
    env = dict(os.environ, BEAM_OPTIONS=f"{key[3:]}={opt}", BEAM_UFO_OUT=str(ufo))
    subprocess.run([sys.executable, str(ROOT / "sources/build_ufo.py")], check=True, env=env, stdout=subprocess.DEVNULL)
    subprocess.run([str(Path(sys.executable).parent / "fontmake"), "-u", str(ufo), "-o", "ttf", "--output-path", str(ttf),
                    "--no-production-names", "--keep-overlaps", "--verbose", "ERROR"], check=True)
    return ttf


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    label = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
    for key, d in decisions.DECISIONS.items():
        rows = []
        for opt, text in d["options"].items():
            tmp = WORK / f"{key}-{opt}.png"
            render_text(Face(build_variant(key, opt)), WORDS[key], tmp, size=92, width=1500)
            rows.append((opt, text, Image.open(tmp)))
        h = sum(r[2].height + 56 for r in rows) + 20
        sheet = Image.new("L", (1500, h), 255)
        draw = ImageDraw.Draw(sheet)
        y = 10
        for opt, text, img in rows:
            draw.text((30, y + 10), f"{key}  option {opt}: {text}", fill=70, font=label)
            sheet.paste(img, (0, y + 46))
            y += img.height + 56
            draw.line([(30, y - 4), (1470, y - 4)], fill=215)
        sheet.save(OUT / f"{key}.png")
        print(OUT / f"{key}.png")


if __name__ == "__main__":
    main()
