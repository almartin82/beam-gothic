"""Shared drawing metrics, in font units."""
UPM = 1000  # Units per em.
CAP = 700  # Cap height (H in the original program).
V = 136  # Vertical stem width.
T = 114  # Horizontal arm thickness.
S = 0.45  # Rise/run of sheared stem ends.
K = 56  # Extra length of an arm's outer edge.
C = 60  # Outer bowl corner chamfer.
CI = 22  # Inner counter corner chamfer.
BAR_Y0 = 300  # Bottom of the middle bar.
BAR_Y1 = 400  # Top of the middle bar.
SB = 30  # Straight-sided left/right bearing.
SBD = 14  # Diagonal-sided bearing.
SHEAR_PAD = 70  # Sideways reach of a stem-end cutting plane.
D = 128  # Horizontal width of the narrower diagonal strokes.
BAR = BAR_Y1 - BAR_Y0  # Middle stroke thickness.
PLUS_LIGHTENING = 36  # Reduce V for the plus sign's smaller vertical stroke.
BRACKET_LIGHTENING = 32  # Reduce V for the angular parentheses.
QUOTE_HEAD_LIGHTENING = 40  # Reduce V for the uncut tapered quote head.
QUOTE_FOOT_LIGHTENING = 84  # Reduce V for the tapered quote foot.

# --- v2 additions (Phase 2 and 3) ---
SYM = 92  # Stroke of symbols and brackets: lighter than a stem so # % @ { } do not clot.
BR_Y0 = -70  # Bottom of brackets, braces and the bar (the v1 parentheses already use this).
BR_Y1 = 770  # Top of brackets, braces and the bar.
MATH_Y = 340  # Vertical centre of the math operators (the v1 plus is centred here).
MK = 84  # Stroke of the accents.
MARK_Y = 745  # Bottom of the accents above: 45 units clear of the cap line.
MARK_H = 125  # Height of the accents above. Kept low and wide: Beam is heavy enough to carry them.
SUP = 0.58  # Scale of superiors, ordinals and fraction figures.
