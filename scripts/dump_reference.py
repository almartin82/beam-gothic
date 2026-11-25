"""Decompile the v1.100 TTF into sources/reference/v1100.json: per-glyph contours, advance, codepoints, and kerning pairs.
The TTF has straight lines only, so this is lossless."""
import json, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.agl import UV2AGL

ROOT = Path(__file__).resolve().parent.parent
f = TTFont(ROOT / "sources/reference/BeamGothic-Regular-v1.100.ttf")
glyf, hmtx = f["glyf"], f["hmtx"]
rev = {}
for cp, n in f.getBestCmap().items():
    rev.setdefault(n, []).append(cp)

def prod(n):
    if n.startswith("uni"):
        cp = int(n[3:], 16)
        return UV2AGL.get(cp, n)
    return n

out = {"glyphs": {}, "kerning": []}
for n in f.getGlyphOrder():
    g = glyf[n]
    contours = []
    if g.numberOfContours > 0:
        assert all(fl & 1 for fl in g.flags), n  # every point on-curve
        s = 0
        for e in g.endPtsOfContours:
            contours.append([list(p) for p in g.coordinates[s:e + 1]])
            s = e + 1
    out["glyphs"][prod(n)] = {"old_name": n, "advance": hmtx[n][0], "unicodes": sorted(rev.get(n, [])), "contours": contours}

gpos = f["GPOS"].table
for lk in gpos.LookupList.Lookup:
    for st in lk.SubTable:
        if st.Format == 1:
            for i, first in enumerate(st.Coverage.glyphs):
                for pvr in st.PairSet[i].PairValueRecord:
                    out["kerning"].append([prod(first), prod(pvr.SecondGlyph), pvr.Value1.XAdvance])
        else:
            sys.exit("unexpected class kerning in reference")
(ROOT / "sources/reference/v1100.json").write_text(json.dumps(out, indent=1))
print(len(out["glyphs"]), "glyphs,", len(out["kerning"]), "kerning pairs")
