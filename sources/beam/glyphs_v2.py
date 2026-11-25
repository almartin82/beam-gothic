"""Phase 2: the rest of printable ASCII and the typesetting punctuation.

Nothing here is documented in the source material. Every glyph follows the three cutting rules
where they apply (sheared stem ends, spurred arms, no curves) and is labeled extrapolated, or
decided where the choice went to the panel."""
from shapely import affinity

from . import decisions, params as p
from .glyphs_v1 import (Glyph, arm, dot, open_round, quote_shape, ring, s_shape, spaced, stem)
from .prims import CR, P, R, corner, cut, diag, mirror, shear_bottom, shear_top, spur_right, translate, union

SH, SP, NC = "shear", "spur", "no-curves"
RULES = {}      # glyph name -> rules followed
DECIDED = {}    # glyph name -> panel decision id
BUILDERS = {}   # glyph name -> builder


def glyph(name, rules=(), decision=None):
    def wrap(fn):
        BUILDERS[name] = fn
        RULES[name] = list(rules)
        if decision:
            DECIDED[name] = decision
        return fn
    return wrap


def rot180_box(geom, width, y0=0, y1=None):
    """Turn a drawing upside down inside its own box."""
    y1 = p.CAP if y1 is None else y1
    return affinity.rotate(geom, 180, origin=(width / 2, (y0 + y1) / 2))


def chevron(w, h, t, *, tip=None):
    """A '<' pointing left: w wide, h tall, arms t thick (measured vertically), blunt tip.
    Drawn with its bottom at y=0."""
    tip = t * 0.7 if tip is None else tip
    mid = h / 2
    slope = (mid - tip / 2) / w                      # outer edge, rise per unit run
    inner_x = w - (mid - t) / slope
    return P([(0, mid - tip / 2), (w, 0), (w, t), (inner_x, mid), (w, h - t), (w, h), (0, mid + tip / 2)])


def miniring(w, h, v, t, c, ci):
    return cut(CR(0, 0, w, h, c=c), CR(v, t, w - v, h - t, c=ci))


# ---------------------------------------------------------------- ASCII

@glyph("numbersign")
def numbersign():
    w, lean = 440, 46
    g = union(diag(118, 0, 118 + lean, p.CAP, p.SYM), diag(276, 0, 276 + lean, p.CAP, p.SYM),
              R(0, 424, w, 424 + p.SYM), R(0, 184, w, 184 + p.SYM))
    return spaced(g, w)


@glyph("percent", [NC])
def percent():
    w = 560
    o = miniring(196, 300, 66, 60, 34, 10)
    g = union(translate(o, 0, p.CAP - 300), translate(o, w - 196, 0), diag(126, 0, w - 126, p.CAP, p.SYM))
    return spaced(g, w)


def ampersand_et():
    """Option A: the Et construction. An E skeleton with clipped left corners; the bottom arm
    turns up into a short sheared stem, and the middle bar runs through it and ends in a spur."""
    w = 470
    t_x = 262                                            # left edge of the rising stroke
    body = cut(CR(0, 0, 330, p.CAP, tr=0, br=0), R(p.V, p.T, 400, p.CAP - p.T))
    body = spur_right(body, 330, p.CAP - p.T, p.CAP)     # top arm, spur up
    body = cut(body, R(t_x + p.V, -10, 400, p.T + 10))   # bottom arm stops at the rising stroke
    riser = stem(t_x, y0=0, y1=520, bottom=False)
    bar = arm(0, w, p.BAR_Y0, p.BAR_Y1, right=True)
    return spaced(union(body, riser, bar), w)


def ampersand_eight():
    """Option B: the cut v1.000 idea, redrawn. An 8 whose lower bowl opens into a spurred leg."""
    w = 470
    inset = 40
    upper = cut(CR(inset, p.BAR_Y0, 380 - inset, p.CAP, c=p.C * .8, bl=0, br=0),
                CR(inset + p.V - 16, p.BAR_Y1, 380 - inset - p.V + 16, p.CAP - p.T, c=p.CI))
    lower = cut(CR(0, 0, 380, p.BAR_Y1, c=p.C, tl=18, tr=18), CR(p.V, p.T, 380 - p.V, p.BAR_Y0, c=p.CI))
    leg = shear_bottom(diag(w - 66, 0, 250, p.BAR_Y1, p.V - 4), w - 132, w)
    return spaced(union(upper, lower, leg), w, right=p.SBD)


def ampersand_plus():
    """Option C: the sign-painter's shorthand. A reversed 3 struck through with a vertical."""
    w = 410
    e = union(R(0, 0, p.V, p.CAP), arm(0, w, p.CAP - p.T, p.CAP, right=True),
              arm(0, w - 60, p.BAR_Y0, p.BAR_Y1, right=True), arm(0, w, 0, p.T, right=True, up=False))
    e = corner(corner(e, 0, 0, "bl"), 0, p.CAP, "tl")
    strike = R(190, p.BR_Y0 - 20, 190 + p.C, p.BR_Y1 + 20)
    return spaced(union(e, strike), w)


AMPERSAND_OPTIONS = {"A": ampersand_et, "B": ampersand_eight, "C": ampersand_plus}
glyph("ampersand", [SP, SH, NC], decision=decisions.decision_id("P2-ampersand"))(AMPERSAND_OPTIONS[decisions.choice("P2-ampersand")])


@glyph("asterisk")
def asterisk():
    w, t, cy = 300, 70, 545
    bar_ = R(w / 2 - t / 2, cy - 155, w / 2 + t / 2, cy + 155)
    g = union(*[affinity.rotate(bar_, a, origin=(w / 2, cy)) for a in (0, 60, 120)])
    return spaced(g, w, bearing=24)


@glyph("less")
def less():
    w, h = 350, 420
    return spaced(translate(chevron(w, h, 112), 0, p.MATH_Y - h / 2), w)


@glyph("greater")
def greater():
    w, h = 350, 420
    return spaced(mirror(translate(chevron(w, h, 112), 0, p.MATH_Y - h / 2), w), w)


@glyph("equal")
def equal():
    w, gap = 380, 84
    return spaced(union(R(0, p.MATH_Y + gap / 2, w, p.MATH_Y + gap / 2 + p.BAR),
                        R(0, p.MATH_Y - gap / 2 - p.BAR, w, p.MATH_Y - gap / 2)), w)


def mini_A(w, h, s, bar_y, bar_t):
    """A small flat-topped A for @ and the ordinals: two diagonal strokes s wide and a bar."""
    top = 0.38 * w
    g = union(diag(s / 2, 0, top, h, s), diag(w - s / 2, 0, w - top, h, s), R(w * .22, bar_y, w * .78, bar_y + bar_t))
    return g


def at_A():
    """Option A: a chamfered-rectangle ring, cut open at the lower right, around a small A.
    The A's right foot runs out into the ring, as the tail of an @ does."""
    w, y0, s = 700, -120, 78
    outer = cut(CR(0, y0, w, p.CAP, c=90), CR(s, y0 + s, w - s, p.CAP - s, c=44))
    outer = cut(outer, R(500, y0 - 10, w + 10, 120))                  # open the lower right
    outer = spur_right(outer, 500, y0, y0 + s, up=False)             # free end of the bottom run
    a = translate(mini_A(290, 400, 84, 96, 66), 196, 120)
    foot = R(196 + 290 - 84, 120, w - s / 2, 120 + 66)                # the A's foot joins the ring
    return spaced(union(outer, a, foot), w)


def at_a():
    """Option B: the same ring around a one-storey square bowl with a right stem (a boxed 'a')."""
    w, y0, s = 700, -120, 78
    outer = cut(CR(0, y0, w, p.CAP, c=90), CR(s, y0 + s, w - s, p.CAP - s, c=44))
    outer = cut(outer, R(500, y0 - 10, w + 10, 120))
    outer = spur_right(outer, 500, y0, y0 + s, up=False)
    bowl = translate(miniring(250, 400, 84, 72, 40, 12), 196, 120)
    st = R(196 + 250 - 84, 120, 196 + 250 + 20, 520)
    foot = R(196 + 250 - 84, 120, w - s / 2, 120 + 72)
    return spaced(union(outer, bowl, st, foot), w)


def at_plain():
    """Option C: no tail. A closed ring around a small A, read as a monogram."""
    w, s = 640, 78
    outer = cut(CR(0, 0, w, p.CAP, c=90), CR(s, s, w - s, p.CAP - s, c=44))
    a = translate(mini_A(270, 370, 84, 90, 62), 185, 165)
    return spaced(union(outer, a), w)


AT_OPTIONS = {"A": at_A, "B": at_a, "C": at_plain}
glyph("at", [NC, SP], decision=decisions.decision_id("P2-at"))(AT_OPTIONS[decisions.choice("P2-at")])


def bracket_shape():
    w, sw = 210, 110
    return union(R(0, p.BR_Y0, sw, p.BR_Y1), arm(0, w, p.BR_Y1 - p.SYM, p.BR_Y1, right=True),
                 arm(0, w, p.BR_Y0, p.BR_Y0 + p.SYM, right=True, up=False))


@glyph("bracketleft", [SP])
def bracketleft():
    return spaced(bracket_shape(), 210, bearing=40, right=20)


@glyph("bracketright", [SP])
def bracketright():
    return spaced(mirror(bracket_shape(), 210), 210, bearing=20, right=40)


@glyph("backslash")
def backslash():
    return spaced(mirror(diag(62, -60, 342, 760, p.D - 4), 404), 404, bearing=8)


@glyph("asciicircum")
def asciicircum():
    w, h, t = 380, 250, 118                 # an upward chevron: the '<' turned a quarter
    c = affinity.rotate(chevron(h, w, t, tip=84), -90, origin=(0, 0))
    x0, y0, _, _ = c.bounds
    return spaced(translate(c, -x0, p.CAP - h - y0), w)


@glyph("underscore")
def underscore():
    return Glyph(R(0, -170, 500, -90), 500)


def brace_shape():
    """Angular brace: the bracket with clipped corners and a nib at the middle."""
    w, x0, sw = 250, 64, 104
    x1 = x0 + sw
    mid = (p.BR_Y0 + p.BR_Y1) / 2
    return P([(w, p.BR_Y1), (x0 + p.C, p.BR_Y1), (x0, p.BR_Y1 - p.C), (x0, mid + 84), (0, mid + 36), (0, mid - 36),
              (x0, mid - 84), (x0, p.BR_Y0 + p.C), (x0 + p.C, p.BR_Y0), (w, p.BR_Y0), (w, p.BR_Y0 + p.SYM),
              (x1 + p.CI, p.BR_Y0 + p.SYM), (x1, p.BR_Y0 + p.SYM + p.CI), (x1, p.BR_Y1 - p.SYM - p.CI),
              (x1 + p.CI, p.BR_Y1 - p.SYM), (w, p.BR_Y1 - p.SYM)])


@glyph("braceleft", [NC])
def braceleft():
    return spaced(brace_shape(), 250, bearing=24, right=20)


@glyph("braceright", [NC])
def braceright():
    return spaced(mirror(brace_shape(), 250), 250, bearing=20, right=24)


@glyph("bar", [SH])
def bar():
    g = shear_bottom(shear_top(R(0, p.BR_Y0, 110, p.BR_Y1), 0, 110, p.BR_Y1), 0, 110, p.BR_Y0)
    return spaced(g, 110, bearing=44)


def zigzag(w, h, t):
    """A tilde with no curves: three straight runs, t thick (measured vertically), bottom at y=0."""
    lo, hi = t / 2, h - t / 2
    xs = (0, w * 0.32, w * 0.68, w)
    ys = (lo + (hi - lo) * .25, hi, lo, hi - (hi - lo) * .25)
    top = [(x, y + t / 2) for x, y in zip(xs, ys)]
    bot = [(x, y - t / 2) for x, y in zip(xs, ys)]
    return P(top + bot[::-1])


@glyph("asciitilde")
def asciitilde():
    w, h = 400, 200
    return spaced(translate(zigzag(w, h, 100), 0, p.MATH_Y - h / 2), w)


# ---------------------------------------------------------------- typesetting punctuation

@glyph("endash", [SP])
def endash():
    return spaced(spur_right(arm(0, 470, 280, 380, left=True, up=False), 470, 280, 380), 470)


def quote_left_shape():
    return rot180_box(quote_shape(), 96, 480, p.CAP)


@glyph("quotedblleft", [SH])
def quotedblleft():
    q = quote_left_shape()
    return spaced(union(q, translate(q, 140)), 236, bearing=34, right=30)


@glyph("quotedblright", [SH])
def quotedblright():
    q = quote_shape()
    return spaced(union(q, translate(q, 140)), 236, bearing=34, right=30)


LOW_QUOTE_DY = -(480 + 110)   # drop the quote so it straddles the baseline like the comma


@glyph("quotesinglbase", [SH])
def quotesinglbase():
    return spaced(translate(quote_shape(), 0, LOW_QUOTE_DY), 96, bearing=34, right=30)


@glyph("quotedblbase", [SH])
def quotedblbase():
    q = translate(quote_shape(), 0, LOW_QUOTE_DY)
    return spaced(union(q, translate(q, 140)), 236, bearing=34, right=30)


def guil(w=200, h=340, t=100):
    return translate(chevron(w, h, t, tip=70), 0, p.MATH_Y - h / 2)


@glyph("guilsinglleft")
def guilsinglleft():
    return spaced(guil(), 200)


@glyph("guilsinglright")
def guilsinglright():
    return spaced(mirror(guil(), 200), 200)


@glyph("guillemotleft")
def guillemotleft():
    return spaced(union(guil(), translate(guil(), 170)), 370)


@glyph("guillemotright")
def guillemotright():
    return spaced(mirror(union(guil(), translate(guil(), 170)), 370), 370)


@glyph("ellipsis", [SH])
def ellipsis():
    step = p.V + 2 * p.SB
    return spaced(union(dot(), translate(dot(), step), translate(dot(), 2 * step)), 2 * step + p.V)


@glyph("bullet", [NC])
def bullet():
    return spaced(CR(0, p.MATH_Y - 120, 240, p.MATH_Y + 120, c=p.C), 240, bearing=40)


@glyph("periodcentered", [SH])
def periodcentered():
    d = dot()
    return spaced(translate(d, 0, p.CAP / 2 - (d.bounds[3] - d.bounds[1]) / 2), p.V)


@glyph("exclamdown", [SH])
def exclamdown():
    return spaced(rot180_box(union(dot(), stem(y0=220)), p.V), p.V)


# ---------------------------------------------------------------- redrawn v1 glyphs

def comma_shape():
    """The comma redrawn as the quote's heavier sibling: the period's sheared top, tapering to a
    blunt foot below the baseline. v1.100 hung a flag-like tail off the period, which left a notch."""
    top = p.S * p.V
    return P([(0, p.V), (p.V, p.V + top), (p.V - 44, -140), (34, -140)])


@glyph("comma", [SH])
def comma():
    return spaced(comma_shape(), p.V)


@glyph("semicolon", [SH])
def semicolon():
    return spaced(union(comma_shape(), translate(dot(), y=330)), p.V)


def question_shape():
    """The question mark redrawn narrower, with the bowl vocabulary of the S: clipped outer
    corners (C) and clipped counter corners (CI). v1.100's hook was 400 wide with square counters."""
    w, sx = 370, 122                                   # sx: left edge of the stem under the hook
    hook_y0 = 320
    outer = union(arm(0, w, p.CAP - p.T, p.CAP, left=True), R(w - p.V, hook_y0, w, p.CAP),
                  R(sx, hook_y0, w, hook_y0 + p.BAR))
    outer = corner(corner(outer, w, p.CAP, "tr"), w, hook_y0, "br", p.C * .6)
    # clipped counter corners, top right and bottom right of the counter
    cx, cy0, cy1 = w - p.V, hook_y0 + p.BAR, p.CAP - p.T
    outer = union(outer, P([(cx - p.CI, cy1), (cx, cy1), (cx, cy1 - p.CI)]), P([(cx - p.CI, cy0), (cx, cy0), (cx, cy0 + p.CI)]))
    st = stem(sx, y0=215, y1=hook_y0 + p.BAR, top=False)
    return union(outer, st, translate(dot(), sx)), w


@glyph("question", [SH, SP, NC])
def question():
    g, w = question_shape()
    return spaced(g, w)


@glyph("questiondown", [SH, SP, NC])
def questiondown():
    g, w = question_shape()
    return spaced(rot180_box(g, w), w)


GLYPHS = {name: fn() for name, fn in BUILDERS.items()}
