"""Release gate for Beam Gothic. Run via `make gate` (after `make build`).

Part-scoped defects (one glyph out of bounds, one bad provenance label) are WARNs on that glyph:
the report always covers the whole font, and the flagged glyphs go back through the revision loop.
The release waits until the report is clean. Only an unreadable font stops the run outright.

Checks:
  1. bounds        no outline past its advance width (marks excepted)
  2. no curves     every point on-curve
  3. provenance    labels in the UFO lib agree with the letter inventory: no glyph claims more
                   evidence than the inventory holds; every decision ID exists; every rule exists
  4. coverage      GF Latin Core, confirmed by the glyphsets tool
  5. v1.100        every outline that differs from v1.100 has a recorded reason
  6. fontbakery    googlefonts profile, zero FAILs (pass --skip-fontbakery to reuse the last report)
"""
import re
import subprocess
import sys
from pathlib import Path

import glyphsets
import ufoLib2
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "sources"))
import bounds_check  # noqa: E402
import check_build_v1100  # noqa: E402
from beam import decisions, inventory  # noqa: E402

TTF = ROOT / "fonts/ttf/BeamGothic-Regular.ttf"
UFO = ROOT / "sources/BeamGothic-Regular.ufo"
PROV_KEY = "org.fontmachine.provenance"
FB_MD = ROOT / "build/fontbakery-googlefonts.md"


def provenance_flags(ufo):
    flags = []
    for g in ufo:
        if g.name in (".notdef", "space"):
            continue
        prov = g.lib.get(PROV_KEY)
        if not prov:
            flags.append((g.name, "no provenance label"))
            continue
        label = prov.get("label")
        if label == "documented":
            claimed = prov.get("sources", [])
            held = inventory.DOCUMENTED.get(prov.get("component_of", g.name), [])
            if not claimed or any(s not in held or s not in inventory.SOURCES for s in claimed):
                flags.append((g.name, "claims documented, but the inventory does not hold those sources"))
        elif label == "decided":
            key, _, opt = prov.get("decision", "").partition(":")
            if key not in decisions.DECISIONS or opt not in decisions.DECISIONS[key]["options"]:
                flags.append((g.name, f"decided, but decision {prov.get('decision')!r} is not on record"))
        elif label != "extrapolated":
            flags.append((g.name, f"unknown label {label!r}"))
        for r in prov.get("rules", []):
            if r not in inventory.RULES:
                flags.append((g.name, f"cites rule {r!r}, which the inventory does not define"))
        if g.name in inventory.DOCUMENTED and label != "documented":
            flags.append((g.name, "is in the inventory as documented but is not labeled so"))
    return flags


def curve_flags(font):
    glyf = font["glyf"]
    return [(n, "has off-curve points") for n in font.getGlyphOrder()
            if glyf[n].numberOfContours > 0 and not all(f & 1 for f in glyf[n].flags)]


def main():
    try:
        font = TTFont(TTF)
        ufo = ufoLib2.Font.open(UFO)
        assert font.getBestCmap()
    except Exception as e:                                   # nothing true to report on
        sys.exit(f"STOP: the font cannot be read ({e})")

    lines, problems = ["# Beam Gothic release gate", ""], 0

    def section(title, flags, ok):
        nonlocal problems
        problems += len(flags)
        lines.append(f"## {title}: {'clean' if not flags else str(len(flags)) + ' flagged'}")
        lines.append(ok if not flags else "")
        lines.extend(f"- WARN `{name}`: {why}" for name, why in flags)
        lines.append("")

    b = [(n, f"outline x {x0}..{x1} outside advance 0..{adv}") for n, x0, x1, adv in bounds_check.check(TTF)]
    section("Bounds", b, f"All {len(font.getGlyphOrder())} glyphs sit inside their advance widths (marks excepted).")
    section("No curves", curve_flags(font), "Every outline point is on-curve.")
    prov = provenance_flags(ufo)
    counts = {}
    for g in ufo:
        label = g.lib.get(PROV_KEY, {}).get("label")
        if label:
            counts[label] = counts.get(label, 0) + 1
    section("Provenance", prov, "Labels agree with the inventory: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())) + ".")

    need = set(glyphsets.unicodes_per_glyphset("GF_Latin_Core"))
    missing = sorted(need - set(font.getBestCmap()))
    section("GF Latin Core coverage", [("U+%04X" % c, "missing") for c in missing],
            f"All {len(need)} codepoints present ({len(font.getBestCmap())} mapped in the font).")

    ref = check_build_v1100.json.loads((ROOT / "sources/reference/v1100.json").read_text())["glyphs"]
    face = check_build_v1100.Face(TTF)
    unexplained, changed = [], []
    for name, r in ref.items():
        diff = check_build_v1100.geom(face.rings(name)).symmetric_difference(check_build_v1100.geom(r["contours"])).area
        if diff or font["hmtx"][name][0] != r["advance"]:
            (changed if name in check_build_v1100.CHANGED else unexplained).append(name)
    section("Outlines against v1.100", [(n, "differs from v1.100 with no recorded reason") for n in unexplained],
            f"{len(ref) - len(changed)} of {len(ref)} v1.100 glyphs unchanged; {len(changed)} changed with a recorded reason "
            f"({', '.join(changed)}).")

    if "--skip-fontbakery" not in sys.argv:
        FB_MD.parent.mkdir(exist_ok=True)
        subprocess.run([str(Path(sys.executable).parent / "fontbakery"), "check-googlefonts", str(TTF), "--loglevel", "WARN",
                        "--ghmarkdown", str(FB_MD), "-q"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    md = FB_MD.read_text()
    row = re.findall(r"\| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|", md)[-1]
    err, fatal, fail, warn = (int(x) for x in row[:4])
    fb = [(m, "fontbakery FAIL") for m in re.findall(r"<summary>(?:🔥|💥|☠)[^\n]*?href=\"[^\"]*#([^\"]+)\"", md)]
    if err + fatal + fail and not fb:
        fb = [("fontbakery", f"{err} ERROR, {fatal} FATAL, {fail} FAIL")]
    section("fontbakery googlefonts", fb, f"0 FAIL, {warn} WARN, {row[6]} PASS. WARNs are read in documentation/DOSSIER.md.")

    lines.append(f"**Gate: {'CLEAN' if not problems else str(problems) + ' item(s) flagged, release waits'}**")
    report = "\n".join(lines) + "\n"
    (ROOT / "build/gate-report.md").write_text(report)
    print(report)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
