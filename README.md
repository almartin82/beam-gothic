# Beam Gothic

A caps-only display font, drawn from the lettering in the old Bethlehem Steel wordmark (on their catalogs from 1931 to at least 1966). The wordmark only gives you seven letters: B E H L M S T. I drew everything else from three rules those seven follow - sheared stem ends, spurred arms, no curves.

Version 2.001 covers Google Fonts Latin Core (344 glyphs, accents, kerning) and is licensed under the SIL Open Font License 1.1.

## Motivation

<img src="documentation/specimen/pennant-highmark-stadium.jpg" alt="A cream felt banner reading BETHLEHEM STEEL in black chiseled capitals over a red I-beam, hanging at Highmark Stadium" width="420">

I took this picture at a Bills game on November 22, 2026. The banner hangs in the Blue Moon Bar at Highmark Stadium (Oxford Pennant, out of Buffalo, made it) and I wanted to know what font it was.

It isn't one. The letters are hand-cut felt, copied from the mark Bethlehem Steel put on its own catalogs. So I went looking for the catalogs.

### Into the archive

The Internet Archive has ~two dozen Bethlehem catalog covers, mostly in the Building Technology Heritage Library. Lined up by date, you can watch the lettering change:

- 1931: the earliest one I found, on [Bethlehem Sections](https://archive.org/details/BethlehemSteelCompanyCCA72866). Thin, light letters, but the chisel cuts are already there.
- 1936-37: same lettering, gold-stamped on [Catalogue 107](https://archive.org/details/bethlehem-steel-company-pdf-a) and embossed on [Carbon Steel Bars and Special Sections](https://archive.org/details/BethlehemCarbonSteelBarsAndSpecialSectionsWithProfilesTables).
- 1950s and 60s: redrawn a lot heavier. The [1950 fence catalog](https://archive.org/details/BethelemSteelFenceBarbedWireFencePostsBaleTiesNailsAndStaples) is the closest match to the banner. The [1961 Structural Shapes](https://archive.org/details/BethlehemStructuralShapesInformationAndTablesForArchitectsEngineers_904) cover is the cleanest, so that's the one I drew from. There's also a nice reversed-out version on the [1959 joist catalog](https://archive.org/details/BethlehemOpen-webSteelJoistssSeries_825).
- 1966: [still using it](https://archive.org/details/whosayssteelfram00beth).

### What the letters do

Looking closely at the 1961 mark:

- The bottoms of the stems are cut on a diagonal, low on the left. Easiest to see on the T, H and M.
- Where an arm ends in open space, its outside edge runs a little longer than the inside. The top arm of the E kicks up, and the foot of the L kicks down.
- The B has no curves at all. Its bowls are rectangles with the corners clipped off.
- The S is basically a Z with clipped turns.
- The real mark sits on an arched baseline. I left that out, since it's a layout choice and not part of the letters.

Those turned into the three rules the rest of the font is built on.

### Seven letters

As far as I can tell, Bethlehem never used this lettering for anything except the mark, and the mark only ever says BETHLEHEM STEEL. The other lettering on their covers is ordinary type, which doesn't help: a plain block gothic on the 1929 [Lackawanna Steel Sheet Piling](https://archive.org/details/LackawanaSteelSheetPiling) cover, a condensed grotesque on the 1947 [Wire Nails](https://archive.org/details/BethlehemWireNailsAndOtherWireProducts) catalog.

So seven letters are real and the rest are my best guess at what the same hand would have cut. The font keeps track of which is which (the seven are in red on the specimen).

## Specimen

![Specimen](documentation/specimen/BeamGothic-Specimen.png)

## Sources

The catalog covers, all on the Internet Archive. The links in the specimen image above aren't clickable (it's a picture), so here they are again.

| Year | Catalog |
|---|---|
| 1966 | [Who Says Steel Framing Isn't Best for Apartments?](https://archive.org/details/whosayssteelfram00beth) |
| 1961 | [Bethlehem Structural Shapes](https://archive.org/details/BethlehemStructuralShapesInformationAndTablesForArchitectsEngineers_904) |
| 1960 | [Bethlehem Steel H-Piles](https://archive.org/details/steelhpiles00beth) |
| 1959 | [Bethlehem Open-Web Steel Joists, "S" Series](https://archive.org/details/BethlehemOpen-webSteelJoistssSeries_825) |
| 1950 | [Bethlehem Steel Fence catalog](https://archive.org/details/BethelemSteelFenceBarbedWireFencePostsBaleTiesNailsAndStaples) |
| 1937 | [Bethlehem Carbon Steel Bars and Special Sections](https://archive.org/details/BethlehemCarbonSteelBarsAndSpecialSectionsWithProfilesTables) |
| 1936 | [Bethlehem Alloy and Special Steels, Catalogue 107](https://archive.org/details/bethlehem-steel-company-pdf-a) |
| 1931 | [Bethlehem Sections](https://archive.org/details/BethlehemSteelCompanyCCA72866) |

## Files

| Path | What |
|---|---|
| `fonts/ttf/BeamGothic-Regular.ttf` | Hinted TrueType |
| `fonts/webfonts/BeamGothic-Regular.woff2` | Web font |
| `sources/beam/` | The glyph program: parameters, primitives, glyphs, kerning, metadata, inventory |
| `sources/BeamGothic-Regular.ufo` | UFO written by the program, compiled by fontmake |
| `sources/features/` | `ccmp` and `locl` |
| `documentation/DOSSIER.md` | Provenance, rules, decisions, what the gate found |
| `documentation/specimen/` | Specimen page, PNG and PDF |
| `documentation/panel/` | Drawn options for the open style decisions |
| `releases/` | Tagged builds |

## Building

```
make venv      # once: pinned toolchain in .venv (needs uv)
make build     # glyph program -> UFO -> fontmake -> ttfautohint -> TTF and WOFF2
make gate      # release gate; writes build/gate-report.md
```

Other targets: `make bounds`, `make bake-googlefonts`. `python scripts/specimen.py` rebuilds the specimen page, `python scripts/panel.py` the panel sheets, `python scripts/kern_report.py` the kerning comparison.

Every glyph is labeled in the UFO lib (`org.fontmachine.provenance`) as documented, extrapolated or decided. The gate fails a glyph that claims to be documented when `sources/beam/inventory.py` doesn't back it up.
