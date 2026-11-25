"""Assemble the whole glyph set: geometry, advances, codepoints, components, anchors, provenance.

`assemble()` returns an ordered dict of GlyphDef. build_ufo.py turns it into the UFO."""
import unicodedata
from collections import OrderedDict
from dataclasses import dataclass, field

from shapely import affinity

from fontTools import agl

from . import decisions, glyphs_latin, glyphs_v1, glyphs_v2, inventory
from . import params
from .prims import CR, P, R, snap, translate, union


@dataclass
class GlyphDef:
    name: str
    advance: int
    geom: object = None                              # shapely geometry, or None for composites / space
    unicodes: list = field(default_factory=list)
    components: list = field(default_factory=list)   # (base glyph name, dx, dy)
    anchors: dict = field(default_factory=dict)      # anchor name -> (x, y)
    category: str = "base"                           # GDEF class: base | mark | ligature
    prov: dict = field(default_factory=dict)         # provenance label, see provenance()


V1_UNICODES = {
    "space": [0x20, 0xA0],
    "exclam": [0x21], "quotedbl": [0x22], "dollar": [0x24], "quotesingle": [0x27],
    "parenleft": [0x28], "parenright": [0x29], "plus": [0x2B], "comma": [0x2C], "hyphen": [0x2D],
    "period": [0x2E], "slash": [0x2F],
    "zero": [0x30], "one": [0x31], "two": [0x32], "three": [0x33], "four": [0x34],
    "five": [0x35], "six": [0x36], "seven": [0x37], "eight": [0x38], "nine": [0x39],
    "colon": [0x3A], "semicolon": [0x3B], "question": [0x3F],
    "emdash": [0x2014], "quoteright": [0x2019],
}
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    V1_UNICODES[_c] = [ord(_c)]

# Which cutting rules each extrapolated v1 glyph follows.
_SHEAR, _SPUR, _NC = "shear", "spur", "no-curves"
V1_RULES = {
    "I": [_SHEAR], "F": [_SHEAR, _SPUR], "P": [_SHEAR, _NC], "R": [_SHEAR, _NC], "D": [_NC],
    "O": [_NC], "Q": [_NC], "C": [_SPUR, _NC], "G": [_SPUR, _NC], "J": [_SHEAR, _NC],
    "K": [_SHEAR], "N": [_SHEAR], "A": [_SHEAR], "V": [_SHEAR], "W": [_SHEAR], "X": [_SHEAR],
    "Y": [_SHEAR], "Z": [_SPUR], "U": [_SHEAR, _NC],
    "zero": [_NC], "one": [_SHEAR], "two": [_SPUR, _NC], "three": [_SPUR, _NC], "four": [_SHEAR],
    "five": [_SPUR, _NC], "six": [_SPUR, _NC], "seven": [_SPUR], "eight": [_NC], "nine": [_SPUR, _NC],
    "period": [_SHEAR], "comma": [_SHEAR], "colon": [_SHEAR], "semicolon": [_SHEAR],
    "hyphen": [_SPUR], "emdash": [_SPUR], "exclam": [_SHEAR], "question": [_SHEAR, _SPUR, _NC],
    "quotesingle": [_SHEAR], "quoteright": [_SHEAR], "quoteleft": [_SHEAR], "quotedbl": [_SHEAR],
    "slash": [], "parenleft": [_NC], "parenright": [_NC], "dollar": [_SPUR, _NC], "plus": [],
}


def provenance(name, rules=None, decision=None):
    """Label a glyph: documented (with source IDs), decided (with a decision ID), or extrapolated (with rules)."""
    if name in inventory.DOCUMENTED:
        return {"label": "documented", "sources": inventory.DOCUMENTED[name]}
    if decision:
        return {"label": "decided", "decision": decision, "rules": rules or []}
    return {"label": "extrapolated", "rules": rules or []}


def _rot180_in_place(geom):
    """Rotate 180 degrees about the centre of the glyph's own bounding box."""
    x0, y0, x1, y1 = geom.bounds
    return affinity.rotate(geom, 180, origin=((x0 + x1) / 2, (y0 + y1) / 2))


def assemble():
    glyphs = OrderedDict()

    for name, g in glyphs_v1.GLYPHS.items():
        geom = None if g.geom is None or g.geom.is_empty else snap(g.geom)
        glyphs[name] = GlyphDef(
            name=name, advance=g.advance, geom=geom,
            unicodes=list(V1_UNICODES.get(name, [])),
            prov={} if name in (".notdef", "space") else provenance(name, V1_RULES.get(name)),
        )

    # .notdef was an empty slot in v1.100. Fonts need a visible fallback box.
    box = R(0, 0, 400, params.CAP).difference(R(50, 50, 350, params.CAP - 50))
    glyphs[".notdef"] = GlyphDef(name=".notdef", advance=460, geom=snap(translate(box, params.SB)))

    # The Q tail ran 6 units past the bowl, and Q's advance (504) was R's, not O's.
    # Pull the tail tip inside the bowl's right edge and give Q the advance of O.
    tail = P([(224, 190), (328, 190), (460, -90), (356, -90)])     # v1.100 tail, moved 6 units left
    o = glyphs["O"]
    glyphs["Q"].geom = snap(union(o.geom, translate(tail, params.SB)))
    glyphs["Q"].advance = o.advance

    # v1.200: the left single quote is its own glyph, the right quote turned 180 degrees,
    # so that a quoted word opens and closes correctly. v1.100 mapped both to one glyph.
    qr = glyphs["quoteright"]
    glyphs["quoteleft"] = GlyphDef(
        name="quoteleft", advance=qr.advance, geom=snap(_rot180_in_place(qr.geom)),
        unicodes=[0x2018], prov=provenance("quoteleft", V1_RULES["quoteleft"]),
    )
    # Phase 2: the rest of ASCII and the typesetting punctuation. Three v1 glyphs are redrawn.
    for name, g in glyphs_v2.GLYPHS.items():
        prov = provenance(name, glyphs_v2.RULES[name], glyphs_v2.DECIDED.get(name))
        if name in glyphs:
            glyphs[name].geom, glyphs[name].advance, glyphs[name].prov = snap(g.geom), g.advance, prov
        else:
            glyphs[name] = GlyphDef(name=name, advance=g.advance, geom=snap(g.geom),
                                    unicodes=[ord(c) for c in agl.toUnicode(name)], prov=prov)

    add_latin(glyphs)

    # Lowercase (panel decision P2-lowercase). Option A, capitals on the lowercase keys: each
    # lowercase codepoint is its own glyph, a component of the capital, so nothing is double-mapped.
    low, low_id = decisions.choice("P2-lowercase"), decisions.decision_id("P2-lowercase")
    if low == "A":
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            glyphs[c.lower()] = component_of(glyphs, c.lower(), c, [ord(c.lower())], decision=low_id)
        for lc, cap in LOWER_SPECIAL.items():
            glyphs[lc] = component_of(glyphs, lc, cap, [ord(c) for c in agl.toUnicode(lc)], decision=low_id)
    elif low == "B":
        # Panel preview only: capitals scaled to 80%. A release would redraw them at full stem weight.
        from shapely import affinity
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            g = glyphs[c]
            glyphs[c.lower()] = GlyphDef(name=c.lower(), advance=round(g.advance * .8), unicodes=[ord(c.lower())],
                                         geom=snap(affinity.scale(g.geom, .8, .8, origin=(0, 0))),
                                         prov={"label": "decided", "decision": low_id, "rules": []})
    if low != "A":
        return glyphs          # options B and C are drawn for the panel only: no lowercase composites
    add_composites(glyphs)
    return glyphs


def component_of(glyphs, name, base, unicodes, decision=None):
    """A glyph that is a plain component of another, with the same advance, anchors and class."""
    b = glyphs[base]
    while b.geom is None and len(b.components) == 1 and b.components[0][1:] == (0, 0):
        base = b.components[0][0]          # point at the drawn glyph, never at another component
        b = glyphs[base]
    prov = dict(b.prov)
    if decision:
        # The shape may be documented; putting it on this key is the panel's decision.
        prov = {"label": "decided", "decision": decision, "rules": prov.get("rules", [])}
    prov["component_of"] = base
    return GlyphDef(name=name, advance=b.advance, unicodes=unicodes, components=[(base, 0, 0)],
                    anchors=dict(b.anchors), category=b.category, prov=prov)


# ---------------------------------------------------------------- Phase 3

STACK = 150                 # how far a second accent above is lifted over the first
# Where accents attach, in glyph coordinates. Defaults are the centre of the drawing.
TOP_X = {"L": 108, "J": 332}
OGONEK_X = {"A": 440, "E": 330, "I": 110, "U": 318}
OVERLAPPING = {"uni0327", "uni0328"}
# dcaron and tcaron show the capitals, whose caron is the ordinary one. fontbakery's alt_caron check
# reads any caron component under these two codepoints as the lowercase apostrophe-caron mistake,
# so they are stored as plain outlines. The drawing is the same as Dcaron and Tcaron.
BAKED = {"dcaron", "tcaron"}
NARROW_BASES = {"I"}        # too narrow for the wide accents: they take the .narrow forms
NARROW = {"uni0302": "uni0302.narrow", "uni0308": "uni0308.narrow", "uni0304": "uni0304.narrow"}
MARK_OF = {0x300: "gravecomb", 0x301: "acutecomb", 0x302: "uni0302", 0x303: "tildecomb", 0x304: "uni0304",
           0x306: "uni0306", 0x307: "uni0307", 0x308: "uni0308", 0x30A: "uni030A", 0x30B: "uni030B",
           0x30C: "uni030C", 0x326: "uni0326", 0x327: "uni0327", 0x328: "uni0328"}
MATH = ["less", "greater", "equal", "minus", "multiply", "divide", "plusminus", "notequal", "lessequal",
        "greaterequal", "approxequal", "asciitilde"]
SPACING = {"grave": "gravecomb", "acute": "acutecomb", "dieresis": "uni0308", "macron": "uni0304",
           "cedilla": "uni0327", "circumflex": "uni0302", "caron": "uni030C", "breve": "uni0306",
           "dotaccent": "uni0307", "ring": "uni030A", "ogonek": "uni0328", "tilde": "tildecomb",
           "hungarumlaut": "uni030B"}
LOWER_SPECIAL = {"ae": "AE", "oe": "OE", "oslash": "Oslash", "eth": "Eth", "thorn": "Thorn", "lslash": "Lslash",
                 "hbar": "Hbar", "eng": "Eng", "germandbls": "uni1E9E", "dotlessi": "I", "uni0237": "J",
                 "dcroat": "Dcroat"}
# Letters whose Unicode decomposition says cedilla but which are drawn with a comma below.
COMMA_BELOW = set("GKLNRgklnr")
# Composites beyond GF Latin Core: T with cedilla, so the Romanian locl has both letters to swap.
EXTRA_COMPOSITES = [0x0162, 0x0163]


def add_latin(glyphs):
    """Anchors on the capitals, the accents as mark glyphs, then the drawn letters and symbols."""
    for name in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        g = glyphs[name]
        x0, _, x1, _ = g.geom.bounds
        cx = round((x0 + x1) / 2)
        g.anchors = {"top": (TOP_X.get(name, cx), params.CAP), "bottom": (cx, 0)}
        if name in OGONEK_X:
            g.anchors["ogonek"] = (OGONEK_X[name], 0)

    for name, (geom, kind, rules) in glyphs_latin.MARKS.items():
        geom = snap(geom)
        _, y0, _, y1 = geom.bounds
        anchors = {"top": {"_top": (0, params.CAP), "top": (0, params.CAP + STACK)},
                   "bottom": {"_bottom": (0, 0), "bottom": (0, round(y0))},
                   "ogonek": {"_ogonek": (0, 0)}, "none": {}}[kind]
        uni = [int(name[3:], 16)] if name.startswith("uni") and "." not in name else \
              [ord(c) for c in agl.toUnicode(name)] if "." not in name else []
        glyphs[name] = GlyphDef(name=name, advance=0, geom=geom, unicodes=uni, anchors=anchors,
                                category="mark" if kind != "none" else "base",
                                prov=provenance(name, rules))
    glyphs["uni030C.alt"].advance = 96 + 2 * params.SB
    glyphs["uni030C.alt"].geom = translate(glyphs["uni030C.alt"].geom, 44 + params.SB)

    for name, g in glyphs_latin.GLYPHS.items():
        geom = snap(g.geom)
        x0, _, x1, _ = geom.bounds
        cx = round((x0 + x1) / 2)
        glyphs[name] = GlyphDef(name=name, advance=g.advance, geom=geom,
                                unicodes=[int(name[3:], 16)] if name.startswith("uni") else [ord(c) for c in agl.toUnicode(name)],
                                prov=provenance(name, glyphs_latin.RULES[name]))
        if name in ("AE", "OE", "Oslash", "Eth", "Thorn", "Lslash", "Hbar", "Eng", "uni1E9E"):
            glyphs[name].anchors = {"top": (cx, params.CAP), "bottom": (cx, 0)}
    glyphs["Dcroat"] = component_of(glyphs, "Dcroat", "Eth", [0x0110])

    # Math signs share the advance of the plus, each centred in it.
    width = glyphs["plus"].advance
    for name in MATH:
        g = glyphs[name]
        x0, _, x1, _ = g.geom.bounds
        g.geom = snap(translate(g.geom, round((width - (x1 - x0)) / 2 - x0)))
        g.advance = width

    # Dotted circle: what a shaping engine puts under an accent that has no letter. Twelve clipped
    # squares on a ring, with the same anchors as a capital.
    import math
    dots = [translate(CR(-24, -24, 24, 24, c=12), 300 + 230 * math.cos(math.radians(a)), 350 + 230 * math.sin(math.radians(a)))
            for a in range(0, 360, 30)]
    glyphs["uni25CC"] = GlyphDef(name="uni25CC", advance=600, geom=snap(union(*dots)), unicodes=[0x25CC],
                                 anchors={"top": (300, params.CAP), "bottom": (300, 0), "ogonek": (300, 0)},
                                 prov=provenance("uni25CC", ["no-curves"]))

    # Spacing accents: the combining mark as a component, centred in its own advance.
    for name, m in SPACING.items():
        x0, _, x1, _ = glyphs[m].geom.bounds
        adv = round(x1 - x0) + 2 * params.SB
        glyphs[name] = GlyphDef(name=name, advance=adv, unicodes=[ord(c) for c in agl.toUnicode(name)],
                                components=[(m, round(params.SB - x0), 0)],
                                prov={**glyphs[m].prov, "component_of": m})


def _glyph_for_char(ch):
    name = agl.UV2AGL.get(ord(ch), "uni%04X" % ord(ch))
    return name


def add_composites(glyphs):
    """Every accented letter in GF Latin Core, composed from a base and marks through anchors.
    Lowercase composites reuse the capital base: the lowercase keys type capitals."""
    import glyphsets
    cps = sorted(set(glyphsets.unicodes_per_glyphset("GF_Latin_Core")) | set(EXTRA_COMPOSITES))
    for cp in cps:
        ch = chr(cp)
        d = unicodedata.normalize("NFD", ch)
        if len(d) < 2 or not all(ord(m) in MARK_OF for m in d[1:]) or not d[0].isascii():
            continue
        base = d[0].upper()
        name = _glyph_for_char(ch)
        if name in glyphs:
            continue
        marks = []
        for m in d[1:]:
            mname = MARK_OF[ord(m)]
            if mname == "uni0327" and d[0] in COMMA_BELOW:
                mname = "uni0326"
            if base in NARROW_BASES:
                mname = NARROW.get(mname, mname)
            marks.append(mname)
        b = glyphs[base]
        comps = [(base, 0, 0)]
        anchors = dict(b.anchors)
        lift = 0
        if marks == ["uni030C"] and base == "L":
            # L takes the wedge caron beside the stem, top-aligned with the cap line.
            comps.append(("uni030C.alt", params.V + 40, 0))
        else:
            for mname in marks:
                kind = glyphs_latin.MARKS[mname][1]
                ax, ay = b.anchors[kind]
                dy = lift if kind == "top" else 0
                comps.append((mname, ax, ay - (params.CAP if kind == "top" else 0) + dy))
                if kind == "top":
                    lift += STACK
                    anchors["top"] = (ax, params.CAP + lift)
                elif kind == "bottom":
                    anchors["bottom"] = (ax, glyphs[mname].anchors["bottom"][1])
        prov = {"label": "decided" if ch.islower() else "extrapolated", "composed_of": [c[0] for c in comps],
                "rules": sorted({r for c in comps for r in glyphs[c[0]].prov.get("rules", [])})}
        if ch.islower():
            prov["decision"] = decisions.decision_id("P2-lowercase")
        geom = None
        if any(m in OVERLAPPING for m in marks) or name in BAKED:
            # A cedilla or ogonek runs into the letter. Overlapping components fill differently in
            # different rasterizers, so these glyphs are merged into one outline.
            geom = snap(union(*[translate(glyphs[c].geom, dx, dy) for c, dx, dy in comps]))
            comps = []
        glyphs[name] = GlyphDef(name=name, advance=b.advance, unicodes=[cp], components=comps, geom=geom,
                                anchors=anchors, prov=prov)

    # Turkish, Azeri, Crimean Tatar, Kazakh and Tatar: lowercase i is the dotted letter, so with
    # capitals on the lowercase keys it must show the dot. locl swaps it in for those languages.
    glyphs["i.loclTRK"] = GlyphDef(name="i.loclTRK", advance=glyphs["I"].advance,
                                   components=list(glyphs["Idotaccent"].components), geom=glyphs["Idotaccent"].geom,
                                   anchors=dict(glyphs["Idotaccent"].anchors), prov=dict(glyphs["Idotaccent"].prov))
