# Beam Gothic: dossier

Version 2.000 · 2026-11-24 · written live in a Claude Code session

This is the working record of the font. It replaces the context dump written after v1.100, which is referred to below as "the dump".

## Where it stands

Beam Gothic v2.000 passes the release gate: fontbakery's `googlefonts` profile with 0 FAILs, GF Latin Core coverage confirmed by the `glyphsets` tool, every outline inside its advance width, no curves, and provenance labels that agree with the letter inventory. It went from 54 glyphs and 81 codepoints to 344 glyphs and 339 codepoints.

The three style decisions went to the panel and were picked on 2026-11-25. One piece of metadata is still a placeholder, listed under "Open" at the end. Nothing else is outstanding against the fix plan.

## The source, and what it documents

The lettering comes from the Bethlehem Steel wordmark as it appears on catalog covers from 1931 to 1966, eight of which are in the inventory (`sources/beam/inventory.py`). The wordmark only ever spelled BETHLEHEM STEEL, so seven letters are documented: B E H L M S T. The 1961 Structural Shapes cover is the main reference.

Three rules were read from those letters:

1. **Sheared stem ends.** Free stem ends are cut on a rising diagonal, slope 0.45, low point at the left. Read from T, H, M.
2. **Spurred arms.** On a free arm end the outer edge runs 56 units longer. Read from E, L.
3. **No curves.** Bowls and rounds are rectangles with clipped corners. Read from B, S.

Every glyph in the UFO carries a label under `org.fontmachine.provenance`: 7 documented, 222 extrapolated, 113 decided. The lowercase glyphs count as decided even where the capital they show is documented, because putting a capital on a lowercase key was a panel decision and the archive says nothing about it.

## How the source of truth was rebuilt

The v1.100 build scripts lived in the original chat session and were not on this machine. The TTF has straight lines only, so its outlines decompile without loss (`sources/reference/v1100.json`). The drawing program was rewritten from the parameters and helper functions the context dump describes, and checked glyph by glyph against those outlines.

Result: all 54 v1.100 glyphs are reproduced exactly, with identical advances, zero area difference and identical vertices (`make check-v1100`). The program is parametric where the dump says it should be: moving the stem width by 4 units changes every glyph that has a vertical stem. Five small parts are free polygons with no rule behind them (the Q tail, K's filler, the flag of the 1, the old comma tail, the quote wedge), which matches what the dump says about the lost program.

One thing could not be recovered. The dump says `kern.fea` listed 53 pairs and the file holds 46. Without `kern.fea` the seven missing pairs cannot be named. They no longer matter, because the hand-picked list is replaced by class kerning, but the loss is recorded here because the plan asked for them to be found.

## What changed, by release

**v1.200, repair only.** Name table completed (IDs 0, 3, 4, 6, 8, 9, 10, 13, 14). fsType 0 instead of 4. Regular and Use-Typo-Metrics bits. Vertical metrics by the Google Fonts rule at the old line spacing. Underline values, GDEF classes, production glyph names, a visible `.notdef`. The left single quote became its own glyph. The Q tail moved 6 units left, and Q's advance, which had been R's 504 by mistake, became O's 520. fontbakery `universal`: 0 FAILs. Tagged `v1.200`, files in `releases/v1.200/`.

**v2.000, the full set.**

- The 18 missing ASCII characters, the en dash, double and low quotes, guillemets, ellipsis, bullet, middle dot and the inverted marks.
- The comma is redrawn as a tapered wedge, the heavier sibling of the quote marks. The v1.100 comma hung a flag off the period and left a notch. The question mark is narrower and takes the clipped corners of the S.
- Fourteen accents drawn once, plus narrow forms of three of them for the letter I. Every accented letter is composed from a base and its accents through anchors. Letters with a cedilla or ogonek are merged into one outline, because the hook runs into the letter and overlapping components fill differently across rasterizers.
- Æ Œ Ø Ð Đ Þ Ł Ħ Ŋ and capital ẞ, with ß mapped to it.
- Currency, © ® ™ °, the math signs on one shared advance, ordinals, superiors, fractions, µ § ¶ † ‡, and a dotted circle so a stray accent has something to sit on.
- Features: `kern`, `mark`, `mkmk`, `ccmp`, `locl`.
- Vertical metrics grew to 950/−250 (1.2 em, the Google Fonts minimum) to hold the accents.

## The fourth rule: accents

The source never needed an accent, so this rule is ours. Accents are cut in the same language as the letters: sheared slabs for acute and grave, two small periods for the dieresis, chevrons for circumflex and caron, a zigzag for the tilde, a clipped square for the ring. They sit 45 units above the cap line and are kept low and wide. A face this heavy can carry a low accent, and tall ones would have pushed the line spacing well past what a display face wants.

## Panel decisions

Each decision has three options drawn in the font itself and set in words from the source. The sheets are in `documentation/panel/`. The picks are recorded in `sources/beam/decisions.py`; any other option still builds with `BEAM_OPTIONS="ampersand=B" make build`.

| Decision | Options | Recommended | Status |
|---|---|---|---|
| Ampersand | A: Et construction. B: figure-8 with a leg. C: reversed 3 with a vertical strike | A | Picked A, 2026-11-25 |
| At sign | A: open ring around a small A. B: open ring around a boxed a. C: closed ring, no tail | A | Picked A, 2026-11-25 |
| Lowercase | A: capitals on the lowercase keys. B: small capitals. C: no lowercase | A | Picked A, 2026-11-25 |

The submitter picked the recommended option each time. The reasoning behind each recommendation:

Ampersand: set in a line, B reads as the figure 8 and C reads as a cent or euro sign. A is the only one that cannot be mistaken for another character already in the font. It is also the weakest of the recommended glyphs. In isolation it leans toward a 6 with a crossbar, and it would be the first thing to redraw if a better construction turns up.

At sign: A follows the fix plan's brief and matches the O. Option B is the closest to a conventional @ and is a fair pick for anyone who cares more about recognition than about staying caps-only.

Lowercase: the source is a caps-only wordmark and nothing in it supports a second alphabet. Options B and C are drawn as panel previews only. B scales the capitals to 80 percent, which thins the stems, so choosing it means redrawing 26 letters at full weight before a release.

## Kerning

The 46 hand-picked pairs are gone. Kerning is generated from the outlines (`sources/beam/kerning.py`): each glyph gets a left and right side profile in 25-unit bands, glyphs with the same profile share a class, and a pair is closed by 44 percent of the excess at its tightest point plus 15 percent of its remaining average openness, capped at 70 units.

Those shares were fitted to the old hand-picked pairs, which makes them the test: the generator lands within 8.7 units of them on average, and only two of the 46 differ by more than 15 (F before period and comma, where it gives −70 against the old −50). The result is 92 classes and about 2,000 class pairs. The accented letters inherit their base letter's kerning automatically because the accents sit above the measured bands. The pairs the dump called untested now have values: LO −25, Y before colon −40, T before hyphen −70. `python scripts/kern_report.py` prints the comparison.

## Hinting

The TTF is autohinted with ttfautohint and carries a `gasp` table. At 12 to 16 px the hinted stems are more even in weight and height than the unhinted ones. In 1-bit rendering the hinted letters also sit closer and start to touch at 12 px. That mode is rare now, and with antialiasing the two are close, so hinting stays. The unhinted build is written to `build/` on every compile for comparison.

## The gate

`make gate` runs six checks and writes `build/gate-report.md`. A defect in one glyph is a warning on that glyph, the report always covers the whole font, and the release waits until it is clean. As built:

- Bounds: all 344 glyphs inside their advance widths (combining marks excepted by design).
- No curves: every point on-curve.
- Provenance: labels agree with the inventory.
- Coverage: all 319 GF Latin Core codepoints present.
- Against v1.100: 49 of 54 outlines unchanged, 5 changed with a recorded reason.
- fontbakery `googlefonts`: 0 FAIL, 8 WARN, 112 PASS.

The eight WARNs, each read:

1. **Contour count.** Lowercase codepoints show capitals, so `i` has one contour where a font with lowercase has two. Follows from the lowercase decision.
2. **alt_caron.** `dcaron` and `tcaron` are stored as outlines, so the check cannot inspect them. They show the capitals Ď and Ť, whose ordinary caron is correct. As components they failed the check, which assumes a lowercase d or t.
3. **Vendor ID** `FMCH` is not registered. Placeholder.
4. **Unreachable subsetting.** Some spacing and combining accents are in GF Latin Core but not in Google's `latin` or `latin-ext` serving subsets. That is a mismatch between two Google lists.
5. **Shape languages.** A few auxiliary letters beyond Core (Ĕ Ĭ Ŏ Ō Ŭ Ŀ) are absent.
6. **Outline alignment** and 7. **short segments.** Sheared ends put points near, but not on, the baseline and cap line, and M, N and W have 16 to 19 unit steps where a diagonal meets a stem. All of these are v1.100 geometry.
8. **Article.** Google Fonts catalog metadata, which does not exist yet.

108 checks are skipped, most of them because there is no `METADATA.pb`. That file belongs to the Google Fonts submission packet, which the fix plan does not cover.

## Where this departs from the fix plan

- **GF Latin Core is smaller than the plan assumed.** It does not include fractions, superiors, daggers, µ or the comparison signs. They are drawn anyway, because the plan lists them.
- **No soft hyphen.** The plan asked for one. fontbakery recommends leaving it out, since shaping engines handle it and never display it, so it is not in the font.
- **The x-height stays at 700.** The plan listed "x-height set to cap height" as a defect. With capitals on the lowercase keys the x really is 700 tall, and fontbakery accepts it.
- **Turkish does need a dotted-i switch.** The plan expected none. Lowercase i is the dotted letter in Turkish, Azeri, Crimean Tatar, Kazakh and Tatar, so with capitals on the lowercase keys it has to show İ. `locl` does that for those five languages.
- **The optical pass on K, X, Y and V changed nothing.** Measured across the stroke, their diagonals run 120 to 133 units against 136 for a stem, which is ordinary optical thinning, and the mix of sheared and flat ends follows a consistent logic (a 0.45 cut across a stroke rising to the right would leave a spike). Nothing looked wrong enough to redraw without source evidence, and the plan itself says another research pass should come first.
- **No new research pass.** Ads, plant signage and Bethlehem Review covers are still unchecked.

## Open

1. A registered vendor ID to replace `FMCH`.
