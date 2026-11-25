"""Phase 3: accents, the special Latin letters and the symbols.

The accents are drawn once, centred on x=0, and every accented letter is composed from a base
and marks through anchors (see compose.py). Nothing here is documented in the source material."""
from shapely import affinity

from . import params as p
from .glyphs_v1 import (GLYPHS as V1, Glyph, arm, dot, open_round, quote_shape, ring, spaced, stem)
from .glyphs_v2 import GLYPHS as V2, chevron, mini_A, miniring, zigzag
from .prims import CR, P, R, corner, cut, diag, mirror, shear_bottom, shear_top, spur_left, spur_right, translate, union

SH, SP, NC = "shear", "spur", "no-curves"
Y0, Y1 = p.MARK_Y, p.MARK_Y + p.MARK_H

# ---------------------------------------------------------------- accents (centred on x = 0)

MARKS = {}        # name -> (geometry, kind, rules)   kind: top | bottom | ogonek


def mark(name, kind="top", rules=()):
    def wrap(fn):
        MARKS[name] = (fn(), kind, list(rules))
        return fn
    return wrap


def slant(w, lean, y0=Y0, y1=Y1):
    """A sheared parallelogram w wide leaning `lean` to the right, centred on x=0."""
    return P([(-(w + lean) / 2, y0), ((w - lean) / 2, y0), ((w + lean) / 2, y1), (-(w - lean) / 2, y1)])


def small_dot(w):
    """The period's parallelogram at accent size, bottom-left at the origin."""
    return P([(0, 0), (w, p.S * w), (w, w + p.S * w), (0, w)])


def chevron_up(w, h, t):
    c = affinity.rotate(chevron(h, w, t, tip=t * .62), -90, origin=(0, 0))
    x0, y0, x1, _ = c.bounds
    return translate(c, -(x0 + x1) / 2, -y0)


@mark("acutecomb", rules=[SH])
def acute():
    return slant(100, 70)


@mark("gravecomb", rules=[SH])
def grave():
    return affinity.scale(slant(100, 70), xfact=-1, origin=(0, 0))


@mark("uni030B", rules=[SH])
def hungarumlaut():
    a = slant(80, 64)
    return union(translate(a, -66), translate(a, 66))


def dieresis_shape(w, gap):
    d = small_dot(w)
    return union(translate(d, -gap / 2 - w, Y0 + 4), translate(d, gap / 2, Y0 + 4))


@mark("uni0308", rules=[SH])
def dieresis():
    return dieresis_shape(84, 44)


@mark("uni0308.narrow", rules=[SH])
def dieresis_narrow():
    return dieresis_shape(72, 32)


@mark("uni0307", rules=[SH])
def dotaccent():
    return translate(small_dot(92), -46, Y0)


@mark("uni030A", rules=[NC])
def ring_mark():
    return cut(CR(-78, Y0, 78, Y0 + 150, c=34), CR(-34, Y0 + 44, 34, Y0 + 106, c=10))


@mark("uni0302")
def circumflex():
    return translate(chevron_up(250, p.MARK_H, p.MK + 8), 0, Y0)


@mark("uni0302.narrow")
def circumflex_narrow():
    return translate(chevron_up(176, p.MARK_H, p.MK + 2), 0, Y0)


@mark("uni030C")
def caron():
    return affinity.scale(translate(chevron_up(250, p.MARK_H, p.MK + 8), 0, Y0), yfact=-1, origin=(0, (Y0 + Y1) / 2))


@mark("tildecomb")
def tilde():
    return translate(zigzag(250, p.MARK_H, 70), -125, Y0)


def macron_shape(w):
    lean = p.K * (p.MK - 4) / p.BAR       # the hyphen's lean, scaled to the accent's thickness
    return slant(w - lean, lean, Y0 + 20, Y0 + 20 + p.MK - 4)


@mark("uni0304", rules=[SP])
def macron():
    return macron_shape(250)


@mark("uni0304.narrow", rules=[SP])
def macron_narrow():
    return macron_shape(176)


@mark("uni0306")
def breve():
    w, t = 115, 68
    return P([(-w, Y1), (-w, Y0 + 40), (-w + 40, Y0), (w - 40, Y0), (w, Y0 + 40), (w, Y1),
              (w - t, Y1), (w - t, Y0 + t), (-w + t, Y0 + t), (-w + t, Y1)])


@mark("uni0327", kind="bottom", rules=[SP])
def cedilla():
    return union(R(-18, -84, 52, 10), arm(-92, 52, -154, -84, left=True, up=False))


@mark("uni0326", kind="bottom", rules=[SH])
def commaaccent():
    return P([(-42, -88), (42, -50), (20, -200), (-24, -200)])


@mark("uni0328", kind="ogonek", rules=[SP])
def ogonek():
    return union(P([(-40, 60), (30, 60), (-14, -92), (-84, -92)]), arm(-84, 62, -160, -92, right=True, up=False))


@mark("uni030C.alt", kind="none", rules=[SH])
def caron_alt():
    """The caron of L: a quote wedge set beside the stem, as Slovak typesetting does."""
    return translate(quote_shape(), -48, 0)


# ---------------------------------------------------------------- letters and symbols

RULES, BUILDERS = {}, {}


def glyph(name, rules=()):
    def wrap(fn):
        BUILDERS[name] = fn
        RULES[name] = list(rules)
        return fn
    return wrap


def body(name):
    """A v1/v2 glyph's drawing, moved back to x=0 (its left bearing removed)."""
    g = (V2.get(name) or V1[name]).geom
    return translate(g, -g.bounds[0])


def scaled(geom, f=None, y=0):
    f = p.SUP if f is None else f
    g = affinity.scale(geom, xfact=f, yfact=f, origin=(0, 0))
    return translate(g, 0, y)


def e_arms(x0, w):
    return union(arm(x0, w, p.CAP - p.T, p.CAP, right=True), arm(x0, w - 50, p.BAR_Y0, p.BAR_Y1, right=True),
                 arm(x0, w, 0, p.T, right=True, up=False))


@glyph("AE", [SH, SP])
def AE():
    w, ex = 690, 326
    left = shear_bottom(diag(p.V / 2, 0, ex + p.V / 2 - 30, p.CAP, p.V), 0, p.V)
    g = union(left, R(ex, 0, ex + p.V, p.CAP), e_arms(ex, w), R(150, 190, ex + 10, 286))
    return spaced(g, w, bearing=p.SBD, right=p.SB)


@glyph("OE", [SP, NC])
def OE():
    w, ow = 660, 400
    o = cut(CR(0, 0, ow, p.CAP, tr=0, br=0), CR(p.V, p.T, ow - p.V, p.CAP - p.T, c=p.CI))
    return spaced(union(o, e_arms(ow - p.V, w)), w)


@glyph("Oslash", [NC])
def Oslash():
    return spaced(union(ring(460), diag(86, -50, 374, p.CAP + 50, p.SYM)), 460)


def d_shape():
    w = 450
    return cut(CR(0, 0, w, p.CAP, c=p.C * 1.4, bl=0, tl=0), CR(p.V, p.T, w - p.V, p.CAP - p.T, c=p.CI + 13, bl=0, tl=0))


@glyph("Eth", [NC])
def Eth():
    return spaced(translate(union(d_shape(), R(-40, 310, 236, 390)), 40), 490, bearing=14, right=p.SB)


@glyph("Thorn", [SH, NC])
def Thorn():
    w = 410
    bowl = cut(CR(0, 150, w, 560, bl=0, tl=0), CR(p.V, 150 + p.BAR, w - p.V, 560 - p.T, c=p.CI, bl=0, tl=0))
    return spaced(union(stem(), bowl), w)


@glyph("Lslash", [SH, SP])
def Lslash():
    g = union(body("L"), P([(-44, 232), (252, 365), (252, 465), (-44, 332)]))
    return spaced(translate(g, 44), 404, bearing=14, right=p.SB)


@glyph("Hbar", [SH])
def Hbar():
    g = union(body("H"), R(-24, 520, 474, 596))
    return spaced(translate(g, 24), 498, bearing=10, right=10)


@glyph("Eng", [SH, SP, NC])
def Eng():
    """N whose right stem runs below the baseline and hooks left, like the foot of J."""
    w, drop = 480, -160
    hook = union(R(w - p.V, drop, w, 70), arm(w - p.V - 130, w, drop, drop + p.T, left=True, up=False))
    return spaced(union(body("N"), corner(hook, w, drop, "br")), w)


@glyph("uni1E9E", [SP, NC])
def Germandbls():
    """Capital sharp s: stem, flat arch, and a lower bowl stepped out to the right."""
    w, ux = 500, 426                           # ux: right edge of the upper part
    top = corner(corner(R(0, p.CAP - p.T, ux, p.CAP), 0, p.CAP, "tl"), ux, p.CAP, "tr")
    upper = R(ux - p.V, p.BAR_Y0, ux, p.CAP - 30)
    low = cut(CR(ux - p.V, 0, w, p.BAR_Y1, tl=0, bl=0, tr=p.C * .6), CR(0, p.T, w - p.V, p.BAR_Y0, c=p.CI, tl=0, bl=0))
    foot = arm(236, w - p.C, 0, p.T, left=True, up=False)
    return spaced(union(R(0, 0, p.V, p.CAP - 30), top, upper, low, foot), w)


@glyph("mu", [SH, NC])
def mu():
    return spaced(union(body("U"), stem(0, y0=-170, y1=120, top=False)), 450)


# ---- currency

@glyph("cent", [SP, NC])
def cent():
    return spaced(union(open_round(410), R(175, -70, 175 + p.C, 770)), 410)


@glyph("sterling", [SH, SP, NC])
def sterling():
    """Stem, a hooked top (arm, clipped corners, short sheared drop), crossbar and spurred foot."""
    w, sx, hx = 440, 90, 410                               # hx: right edge of the hook
    top = corner(corner(R(sx, p.CAP - p.T, hx, p.CAP), sx, p.CAP, "tl"), hx, p.CAP, "tr")
    drop = shear_bottom(R(hx - 116, 500, hx, p.CAP - 30), hx - 116, hx, 500)
    g = union(R(sx, 60, sx + p.V, p.CAP - 40), top, drop, R(10, p.BAR_Y0, 330, p.BAR_Y1),
              arm(0, w, 0, p.T, right=True, up=False))
    return spaced(g, w)


@glyph("yen", [SH])
def yen():
    w = 500
    return spaced(union(body("Y"), R(70, 200, w - 70 - 24, 270), R(70, 84, w - 70 - 24, 154)), 476, bearing=38, right=p.SBD)


@glyph("Euro", [SP, NC])
def Euro():
    g = union(translate(open_round(410), 50), R(0, 392, 330, 462), R(0, 248, 330, 318))
    return spaced(g, 460, bearing=20, right=p.SB)


# ---- marks of ownership, ordinals, superiors, fractions

def roundel(inner):
    w, s = 700, 62
    r = cut(CR(0, 0, w, p.CAP, c=110), CR(s, s, w - s, p.CAP - s, c=74))
    x0, y0, x1, y1 = inner.bounds
    return union(r, translate(inner, (w - (x1 - x0)) / 2 - x0, (p.CAP - (y1 - y0)) / 2 - y0))


@glyph("copyright", [NC])
def copyright():
    return spaced(roundel(scaled(body("C"), 0.56)), 700)


@glyph("registered", [NC])
def registered():
    return spaced(roundel(scaled(body("R"), 0.56)), 700)


@glyph("trademark", [SH, SP])
def trademark():
    t, m = scaled(body("T"), 0.46), scaled(body("M"), 0.46)
    g = union(t, translate(m, t.bounds[2] + 26))
    return spaced(translate(g, 0, p.CAP - 0.46 * p.CAP), g.bounds[2], bearing=24)


@glyph("degree", [NC])
def degree():
    return spaced(translate(miniring(230, 250, 66, 62, 44, 14), 0, p.CAP - 250), 230, bearing=24)


def superior(name):
    g = scaled(body(name))
    return spaced(translate(g, 0, p.CAP - p.SUP * p.CAP), g.bounds[2], bearing=20)


for _n, _b in (("onesuperior", "one"), ("twosuperior", "two"), ("threesuperior", "three"),
               ("ordmasculine", "O"), ("ordfeminine", "A")):
    glyph(_n, [NC])(lambda _b=_b: superior(_b))


def frac_bar(w=260):
    return diag(p.SYM / 2 - 6, 0, w - p.SYM / 2 + 6, p.CAP, p.SYM - 12)


@glyph("fraction")
def fraction():
    return spaced(frac_bar(), 260, bearing=14)


def fraction_of(num, den):
    n = translate(scaled(body(num), 0.5), 0, p.CAP - 0.5 * p.CAP)
    bar = translate(frac_bar(), n.bounds[2] - 60)
    d = translate(scaled(body(den), 0.5), bar.bounds[2] - 60)
    g = union(n, bar, d)
    return spaced(g, g.bounds[2], bearing=24)


glyph("onequarter")(lambda: fraction_of("one", "four"))
glyph("onehalf")(lambda: fraction_of("one", "two"))
glyph("threequarters")(lambda: fraction_of("three", "four"))


# ---- math

def minus_bar(w=380):
    return R(0, p.MATH_Y - p.BAR / 2, w, p.MATH_Y + p.BAR / 2)


@glyph("minus")
def minus():
    return spaced(minus_bar(), 380)


@glyph("multiply")
def multiply():
    w, r = 340, 170
    g = union(diag(48, p.MATH_Y - r, w - 48, p.MATH_Y + r, p.SYM + 4), diag(w - 48, p.MATH_Y - r, 48, p.MATH_Y + r, p.SYM + 4))
    return spaced(g, w)


@glyph("divide", [SH])
def divide():
    d = small_dot(96)
    dy = p.S * 96 / 2
    g = union(minus_bar(), translate(d, 142, p.MATH_Y + 96 - dy), translate(d, 142, p.MATH_Y - 192 - dy))
    return spaced(g, 380)


@glyph("plusminus")
def plusminus():
    return spaced(union(translate(body("plus"), 0, 70), R(0, 100, 380, 100 + p.BAR)), 380)


@glyph("notequal")
def notequal():
    return spaced(union(body("equal"), diag(130, 110, 250, 570, 84)), 380)


@glyph("lessequal")
def lessequal():
    return spaced(union(translate(body("less"), 0, 80), R(0, 90, 350, 90 + p.SYM)), 350)


@glyph("greaterequal")
def greaterequal():
    return spaced(union(translate(body("greater"), 0, 80), R(0, 90, 350, 90 + p.SYM)), 350)


@glyph("approxequal")
def approxequal():
    z = zigzag(400, 170, 84)
    return spaced(union(translate(z, 0, p.MATH_Y + 14), translate(z, 0, p.MATH_Y - 184)), 400)


# ---- reference marks

@glyph("section", [NC])
def section():
    """Two small angular S forms sharing a square middle counter."""
    w, t, v = 330, 84, 104
    top = union(arm(0, w, p.CAP - t, p.CAP, right=True), R(0, 470, v, p.CAP), R(0, 470, w, 470 + t))
    top = corner(top, 0, p.CAP, "tl", 44)
    mid = cut(CR(0, 180, w, 554, c=44), CR(v, 180 + t, w - v, 554 - t, c=12))
    bot = union(arm(0, w, p.BR_Y0, p.BR_Y0 + t, left=True, up=False), R(w - v, p.BR_Y0, w, 264), R(0, 180, w, 264))
    bot = corner(bot, w, p.BR_Y0, "br", 44)
    return spaced(union(top, mid, bot), w)


@glyph("paragraph", [NC])
def paragraph():
    w, s = 400, 84
    bowl = CR(0, 330, 220, p.CAP, tl=p.C, bl=p.C, tr=0, br=0)
    g = union(bowl, R(180, p.BR_Y0, 180 + s, p.CAP), R(w - s, p.BR_Y0, w, p.CAP), R(180, p.CAP - s, w, p.CAP))
    return spaced(g, w)


def dagger_stem(w=300, s=92):
    g = R((w - s) / 2, p.BR_Y0, (w + s) / 2, p.CAP)
    return shear_bottom(shear_top(g, (w - s) / 2, (w + s) / 2), (w - s) / 2, (w + s) / 2, p.BR_Y0)


@glyph("dagger", [SH])
def dagger():
    return spaced(union(dagger_stem(), R(0, 440, 300, 440 + p.SYM)), 300)


@glyph("daggerdbl", [SH])
def daggerdbl():
    return spaced(union(dagger_stem(), R(0, 440, 300, 440 + p.SYM), R(0, 100, 300, 100 + p.SYM)), 300)


GLYPHS = {name: fn() for name, fn in BUILDERS.items()}
