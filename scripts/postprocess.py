"""Post-compile steps on the TTF: autohinting.

ttfautohint adds TrueType instructions plus the `prep`, `fpgm`, `cvt` and `gasp` tables. Beam has
no lowercase, so the hinter is told to treat every glyph as Latin capitals (fallback script latn)
and not to hint the composites separately. The unhinted build is kept beside it for comparison."""
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont
from ttfautohint import ttfautohint

ROOT = Path(__file__).resolve().parent.parent


def run(ttf_path):
    ttf_path = Path(ttf_path)
    unhinted = ROOT / "build" / (ttf_path.stem + "-unhinted.ttf")
    unhinted.parent.mkdir(exist_ok=True)
    shutil.copy(ttf_path, unhinted)
    ttfautohint(in_file=str(unhinted), out_file=str(ttf_path), default_script="latn", fallback_script="latn",
                hinting_range_min=8, hinting_range_max=50, no_info=True, windows_compatibility=False)
    font = TTFont(ttf_path)
    # Google Fonts convention for hinted fonts: one gasp range, all smoothing flags on.
    font["gasp"].gaspRange = {0xFFFF: 15}
    font["head"].flags |= 1 << 3        # force ppem to integer values, as hinted fonts should
    # meta table: the script the font is designed for and supports.
    from fontTools.ttLib import newTable
    meta = newTable("meta")
    meta.data = {"dlng": "Latn", "slng": "Latn"}
    font["meta"] = meta
    font.save(ttf_path)
