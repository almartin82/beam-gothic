"""Print the generated class kerning beside the 46 hand-picked v1.100 pairs it was fitted to,
plus the pairs the context dump called untested."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sources"))
from beam import font, kerning  # noqa: E402

glyphs = font.assemble()
k = kerning.build(glyphs)
prof = k["profiles"]
print(f"{len(k['groups'])} classes, {len(k['pairs'])} class pairs")
diffs = []
for a, b, v in kerning.V1_PAIRS:
    mine = kerning.pair_value(prof[a][1], prof[b][0])
    diffs.append(abs(mine - v))
    print(f"{a:>6} {b:<11} v1.100 {v:>4}   generated {mine:>4}   {'' if abs(mine - v) <= 15 else '<-- differs by more than 15'}")
print(f"mean absolute difference {sum(diffs) / len(diffs):.1f} units over {len(diffs)} pairs")
print("untested in v1.100:")
for a, b in [("L", "O"), ("Y", "colon"), ("Y", "semicolon"), ("Y", "hyphen"), ("T", "hyphen"), ("A", "quoteright"),
             ("quoteleft", "A"), ("W", "A"), ("A", "W"), ("K", "Y"), ("Aacute", "V"), ("T", "Aring"), ("L", "quotedblright")]:
    print(f"{a:>12} {b:<14} {kerning.pair_value(prof[a][1], prof[b][0]):>4}")
