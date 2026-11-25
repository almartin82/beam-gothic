"""Class kerning generated from the outlines (Phase 4).

For every glyph the generator measures a left and a right side profile: the distance from the
advance box to the ink, in 25-unit bands from below the baseline to the cap line. Glyphs with
the same profile share a kerning class, which is how the accented letters and the lowercase
components inherit their base letter's kerning without being listed.

For a pair, the gap in each band where both glyphs have ink is right profile + left profile.
The tightest gap, compared with the 60 units two straight stems get, is the excess. The pair is
closed by a fixed share of that excess, plus a smaller share of the pair's average openness.
The shares and the cap were fitted to the 46 pairs
hand-picked for v1.100, which scripts/kern_report.py prints side by side with the generated values.
"""
from shapely.geometry import box

from . import params as p

BAND = 25
Y_MIN, Y_MAX = -150, 700
SMEAR = 1                 # bands: ink this close above or below still counts as facing ink
TARGET = 2 * p.SB         # the gap between two straight stems
SHARE = 0.44              # share of the tightest-point excess closed; fitted to v1.100's pairs
MEAN_SHARE = 0.15         # share of the remaining average openness closed; fitted likewise
OPEN_CAP = 260            # a band counts as no more open than this
CAP = -70                 # no pair closes by more than this (the largest value v1.100 used)
FLOOR = 15                # ignore corrections smaller than this
MIN_GAP = 24              # pairs that come closer than this are opened

FIGURES = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}
# Glyphs that take part in kerning: letters, figures and running-text punctuation.
PUNCT = {"period", "comma", "colon", "semicolon", "hyphen", "endash", "emdash", "exclam", "question",
         "quotesingle", "quotedbl", "quoteleft", "quoteright", "quotedblleft", "quotedblright",
         "quotesinglbase", "quotedblbase", "slash", "parenleft", "parenright", "ampersand",
         "guillemotleft", "guillemotright", "guilsinglleft", "guilsinglright", "ellipsis", "asterisk"}
NOT_LETTERS = {"mu", "uni030C.alt"}


def resolve(glyphs, name):
    """Geometry of a glyph with its components placed."""
    from shapely import affinity
    from shapely.ops import unary_union
    g = glyphs[name]
    parts = [] if g.geom is None else [g.geom]
    for base, dx, dy in g.components:
        parts.append(affinity.translate(resolve(glyphs, base), dx, dy))
    return unary_union(parts) if parts else None


def profiles(geom, advance):
    left, right = [], []
    for y in range(Y_MIN, Y_MAX, BAND):
        s = geom.intersection(box(-2000, y, 3000, y + BAND))
        if s.is_empty or s.area == 0:
            left.append(None), right.append(None)
        else:
            x0, _, x1, _ = s.bounds
            left.append(round(x0)), right.append(round(advance - x1))
    return tuple(left), tuple(right)


def _smear(profile):
    out = []
    for i in range(len(profile)):
        near = [v for v in profile[max(0, i - SMEAR): i + SMEAR + 1] if v is not None]
        out.append(min(near) if near else None)
    return out


def pair_value(right_profile, left_profile):
    gaps = [r + l for r, l in zip(_smear(right_profile), _smear(left_profile)) if r is not None and l is not None]
    if not gaps:
        return 0
    tight = min(gaps)
    if tight < MIN_GAP:
        return int(5 * round((MIN_GAP - tight) / 5))
    # Second term: how open the pair is on average once the tightest point is dealt with. It is
    # what closes round-against-diagonal pairs (OT, AO, KO) whose tightest point is already at target.
    mean = sum(min(g, OPEN_CAP) for g in gaps) / len(gaps)
    tight_ex = max(0, tight - TARGET)
    mean_ex = max(0, mean - TARGET)
    value = max(CAP, -(SHARE * tight_ex + MEAN_SHARE * max(0, mean_ex - tight_ex)))
    value = int(5 * round(value / 5))
    return value if value <= -FLOOR else 0


def kernable(glyphs):
    names = []
    for name, g in glyphs.items():
        if g.category == "mark" or name in NOT_LETTERS or name == ".notdef" or g.advance == 0:
            continue
        cps = g.unicodes
        is_letter = any(chr(c).isalpha() for c in cps) or name == "i.loclTRK"
        if is_letter or name in FIGURES or name in PUNCT:
            names.append(name)
    return names


def build(glyphs):
    names = kernable(glyphs)
    prof = {}
    for n in names:
        geom = resolve(glyphs, n)
        if geom is None or geom.is_empty:
            continue
        prof[n] = profiles(geom, glyphs[n].advance)

    def classes(side):
        by_profile = {}
        for n, pr in prof.items():
            by_profile.setdefault(pr[side], []).append(n)
        return by_profile

    left_side, right_side = classes(0), classes(1)      # keyed by left profile / right profile

    def label(members):
        return sorted(members, key=lambda n: (len(n), n))[0]

    groups, pairs = {}, {}
    first_names, second_names = {}, {}
    for pr, members in right_side.items():              # first glyph of a pair: its right side matters
        key = f"public.kern1.{label(members)}" if len(members) > 1 else members[0]
        if len(members) > 1:
            groups[key] = sorted(members)
        first_names[pr] = (key, members)
    for pr, members in left_side.items():
        key = f"public.kern2.{label(members)}" if len(members) > 1 else members[0]
        if len(members) > 1:
            groups[key] = sorted(members)
        second_names[pr] = (key, members)

    for rp, (first, m1) in first_names.items():
        for lp, (second, m2) in second_names.items():
            if all(a in FIGURES for a in m1) and all(b in FIGURES for b in m2):
                continue                                  # figures keep their own rhythm
            v = pair_value(rp, lp)
            if v:
                pairs[(first, second)] = v
    return {"groups": groups, "pairs": pairs, "profiles": prof}


# The 46 pairs the v1.100 file holds. Kept as the calibration set for the generator, not shipped.
# (The context dump says kern.fea listed 53; kern.fea is lost and the seven others cannot be named.)
V1_PAIRS = [
    ("F", "A", -45), ("F", "period", -50), ("F", "comma", -50),
    ("L", "T", -70), ("L", "V", -55), ("L", "Y", -55), ("L", "quoteright", -60),
    ("T", "O", -20), ("T", "A", -50), ("T", "period", -70), ("T", "comma", -70),
    ("P", "A", -45), ("P", "period", -70), ("P", "comma", -70),
    ("R", "T", -20), ("R", "O", -10), ("R", "C", -10), ("R", "G", -10), ("R", "V", -25), ("R", "Y", -25),
    ("O", "T", -20), ("O", "A", -15), ("O", "V", -20), ("O", "X", -20), ("O", "Y", -25),
    ("C", "A", -10), ("K", "O", -25),
    ("A", "T", -45), ("A", "O", -15), ("A", "Q", -15), ("A", "C", -15), ("A", "G", -15),
    ("A", "V", -55), ("A", "Y", -55),
    ("V", "O", -20), ("V", "A", -55), ("V", "period", -55), ("V", "comma", -55),
    ("X", "O", -20), ("Y", "O", -25), ("Y", "A", -55), ("Y", "period", -55), ("Y", "comma", -55),
    ("one", "one", -20), ("seven", "period", -60), ("seven", "comma", -60),
]
