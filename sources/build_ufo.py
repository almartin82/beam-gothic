"""Write sources/BeamGothic-Regular.ufo from the glyph program in sources/beam/.

The UFO is a build product of the program and is committed so that Google Fonts tooling
(gftools builder, fontmake) has a standard source to compile. Run via `make ufo`."""
import shutil
import sys
from pathlib import Path

import ufoLib2
from shapely.geometry.polygon import orient
from ufoLib2.objects import Anchor, Component, Contour, Point

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from beam import decisions, font, kerning, meta, params  # noqa: E402

import os  # noqa: E402

UFO_PATH = Path(os.environ.get("BEAM_UFO_OUT", HERE / "BeamGothic-Regular.ufo"))
PROV_KEY = "org.fontmachine.provenance"


def _drop_collinear(pts):
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        (px, py), (nx, ny) = pts[i - 1], pts[(i + 1) % n]
        if (x - px) * (ny - y) - (y - py) * (nx - x) != 0:
            out.append((x, y))
    return out


def geom_to_contours(geom):
    """Shapely geometry -> list of point lists. Outer contours counter-clockwise, counters
    clockwise (the UFO / PostScript convention; ufo2ft reverses them for TrueType)."""
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    contours = []
    for poly in sorted(polys, key=lambda p: (p.bounds[0], p.bounds[1])):
        poly = orient(poly, sign=1.0)
        for ring in [poly.exterior, *poly.interiors]:
            pts = [(int(round(x)), int(round(y))) for x, y in ring.coords[:-1]]
            pts = _drop_collinear(pts)
            start = min(range(len(pts)), key=lambda i: (pts[i][1], pts[i][0]))
            contours.append(pts[start:] + pts[:start])
    return contours


def build():
    glyphs = font.assemble()
    ufo = ufoLib2.Font()
    info = ufo.info

    info.familyName = meta.FAMILY
    info.styleName = meta.STYLE
    info.styleMapFamilyName = meta.FAMILY
    info.styleMapStyleName = "regular"
    info.versionMajor = meta.VERSION_MAJOR
    info.versionMinor = meta.VERSION_MINOR
    info.unitsPerEm = params.UPM
    info.capHeight = params.CAP
    # Lowercase keys type capitals, so the x really is drawn at cap height.
    info.xHeight = params.CAP
    info.ascender = meta.ASCENDER
    info.descender = meta.DESCENDER
    info.italicAngle = 0
    info.copyright = meta.COPYRIGHT
    info.postscriptFontName = f"{meta.FAMILY.replace(' ', '')}-{meta.STYLE}"
    info.postscriptFullName = f"{meta.FAMILY} {meta.STYLE}"
    info.postscriptUnderlinePosition = meta.UNDERLINE_POSITION
    info.postscriptUnderlineThickness = meta.UNDERLINE_THICKNESS
    info.postscriptWeightName = "Regular"
    version = f"{meta.VERSION_MAJOR}.{meta.VERSION_MINOR:03d}"
    info.openTypeNameVersion = f"Version {version}"
    info.openTypeNameUniqueID = f"{version};{meta.VENDOR_ID};{info.postscriptFontName}"
    info.openTypeNameDesigner = meta.DESIGNER
    info.openTypeNameDesignerURL = meta.REPO_URL
    info.openTypeNameManufacturer = meta.MANUFACTURER
    info.openTypeNameManufacturerURL = meta.REPO_URL
    info.openTypeNameDescription = meta.DESCRIPTION
    info.openTypeNameLicense = meta.LICENSE
    info.openTypeNameLicenseURL = meta.LICENSE_URL
    info.openTypeHeadCreated = "2026/11/22 00:00:00"
    info.openTypeHheaAscender = meta.ASCENDER
    info.openTypeHheaDescender = meta.DESCENDER
    info.openTypeHheaLineGap = 0
    info.openTypeOS2TypoAscender = meta.ASCENDER
    info.openTypeOS2TypoDescender = meta.DESCENDER
    info.openTypeOS2TypoLineGap = 0
    info.openTypeOS2WinAscent = meta.WIN_ASCENT
    info.openTypeOS2WinDescent = meta.WIN_DESCENT
    info.openTypeOS2Type = []                 # fsType 0: installable embedding, as an open font needs
    info.openTypeOS2Selection = [7]           # Use-Typo-Metrics; the Regular bit comes from styleMapStyleName
    info.openTypeOS2VendorID = meta.VENDOR_ID
    info.openTypeOS2WeightClass = 400
    info.openTypeOS2WidthClass = 5
    info.openTypeOS2Panose = meta.PANOSE
    if getattr(meta, "GASP", None):
        info.openTypeGaspRangeRecords = meta.GASP

    categories = {}
    for name, g in glyphs.items():
        ug = ufo.newGlyph(name)
        ug.width = g.advance
        ug.unicodes = list(g.unicodes)
        if g.geom is not None:
            for pts in geom_to_contours(g.geom):
                ug.contours.append(Contour([Point(x, y, "line") for x, y in pts]))
        for base, dx, dy in g.components:
            ug.components.append(Component(base, (1, 0, 0, 1, dx, dy)))
        for aname, (x, y) in g.anchors.items():
            ug.anchors.append(Anchor(x, y, aname))
        if g.prov:
            ug.lib[PROV_KEY] = g.prov
        if name != ".notdef":
            categories[name] = g.category

    ufo.lib["public.glyphOrder"] = list(glyphs)
    ufo.lib["public.openTypeCategories"] = categories
    ufo.lib["public.postscriptNames"] = {}

    k = kerning.build(glyphs)
    ufo.groups.update(k["groups"])
    ufo.kerning.update(k["pairs"])

    fea = "\n".join(p.read_text() for p in sorted((HERE / "features").glob("*.fea")))
    # The lowercase preview variants (panel options B and C) lack the glyphs ccmp and locl name.
    if fea.strip() and decisions.choice("P2-lowercase") == "A":
        ufo.features.text = fea

    if UFO_PATH.exists():
        shutil.rmtree(UFO_PATH)
    ufo.save(UFO_PATH, overwrite=True)
    print(f"wrote {UFO_PATH.name}: {len(glyphs)} glyphs, "
          f"{len(k['pairs'])} kerning pairs, {len(k['groups'])} groups")


if __name__ == "__main__":
    build()
