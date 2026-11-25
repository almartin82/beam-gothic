"""Does the compiled TTF (program -> UFO -> fontmake) still hold the v1.100 outlines?
Compares every reference glyph with the compiled glyph as polygons. Glyphs that v1.200+ changed on
purpose are listed in CHANGED and reported as such, not as failures."""
import json
import sys
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from proof import Face  # noqa: E402

CHANGED = {
    ".notdef": "empty slot in v1.100, now a fallback box",
    "Q": "tail moved 6 units left, advance set to O's",
    "comma": "redrawn in v2.000 as a tapered wedge",
    "semicolon": "follows the redrawn comma",
    "question": "redrawn in v2.000, narrower, with clipped corners",
}


def geom(rings):
    g = Polygon()
    for r in rings:
        g = g.symmetric_difference(Polygon(r))
    return g


def main(changed=CHANGED):
    ref = json.loads((ROOT / "sources/reference/v1100.json").read_text())["glyphs"]
    face = Face(sys.argv[1] if len(sys.argv) > 1 else ROOT / "fonts/ttf/BeamGothic-Regular.ttf")
    bad = 0
    same = 0
    for name, r in ref.items():
        mine = geom(face.rings(name))
        theirs = geom(r["contours"])
        diff = mine.symmetric_difference(theirs).area
        adv = face.tt["hmtx"][name][0]
        if diff == 0 and adv == r["advance"]:
            same += 1
        elif name in changed:
            print(f"CHANGED {name}: {changed[name]} (area diff {diff:.0f}, advance {r['advance']} -> {adv})")
        else:
            bad += 1
            print(f"WARN {name}: differs from v1.100 with no recorded reason (area diff {diff:.0f}, advance {r['advance']} -> {adv})")
    print(f"{same}/{len(ref)} glyphs identical to v1.100, {len(ref) - same - bad} changed on purpose, {bad} unexplained")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
