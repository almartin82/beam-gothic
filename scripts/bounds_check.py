"""Bounds check: no glyph outline may run past its advance width or left of the origin.
This is the SPARROWS POINT bug. One bad glyph is a WARN on that glyph; the exit code is 1 if any are flagged
so a revision loop can pick them up, but the report always covers every glyph."""
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont


def check(path, allow=()):
    font = TTFont(path)
    gs = font.getGlyphSet()
    gdef = font["GDEF"].table.GlyphClassDef.classDefs if "GDEF" in font and font["GDEF"].table.GlyphClassDef else {}
    flagged = []
    for name in font.getGlyphOrder():
        if gdef.get(name) == 3 or name in allow:   # combining marks sit outside their zero advance by design
            continue
        pen = BoundsPen(gs)
        gs[name].draw(pen)
        if pen.bounds is None:
            continue
        x0, _, x1, _ = pen.bounds
        adv = font["hmtx"][name][0]
        if x0 < 0 or x1 > adv:
            flagged.append((name, x0, x1, adv))
    return flagged


if __name__ == "__main__":
    bad = check(sys.argv[1])
    for name, x0, x1, adv in bad:
        print(f"WARN {name}: outline x {x0}..{x1} outside advance 0..{adv}")
    print(f"bounds check: {len(bad)} glyph(s) flagged")
    sys.exit(1 if bad else 0)
