# Beam Gothic

A caps-only display face drawn after the lettering of the Bethlehem Steel wordmark, c. 1931 to 1966. Seven letters (B E H L M S T) are documented in the source. Everything else follows three cutting rules read from them: sheared stem ends, spurred arms, no curves.

Version 2.001 covers Google Fonts Latin Core: 344 glyphs, accents composed through anchors, class kerning, `mark`, `mkmk`, `ccmp` and `locl`. Licensed under the SIL Open Font License 1.1.

Beam Gothic is an original drawing, not the trademark. It does not contain the hexagonal I-beam emblem.

![Specimen](documentation/specimen/BeamGothic-Specimen.png)

## Sources

The wordmark as it ran on Bethlehem Steel catalog covers, opened as page images on the Internet Archive. The 1961 cover is the main letterform reference. (The specimen above is a picture, so its source list isn't clickable. These are the same links.)

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

Other targets: `make check-v1100` (does the program still reproduce the v1.100 outlines), `make bounds`, `make bake-googlefonts`. `python scripts/specimen.py` rebuilds the specimen page, `python scripts/panel.py` the panel sheets, `python scripts/kern_report.py` the kerning comparison.

Every glyph carries a provenance label in the UFO lib (`org.fontmachine.provenance`): documented, extrapolated or decided. The gate fails any glyph that claims more evidence than `sources/beam/inventory.py` holds.
