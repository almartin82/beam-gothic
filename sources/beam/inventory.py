"""The letter inventory: what the source material documents, and where.

Every provenance claim the font makes comes from this table. A glyph may be labeled
`documented` only if it is listed in DOCUMENTED with at least one source ID."""

# Internet Archive item identifiers. Dates are from the item records.
SOURCES = {
    "ia:whosayssteelfram00beth": (1966, "Who Says Steel Framing Isn't Best for Apartments?"),
    "ia:BethlehemStructuralShapesInformationAndTablesForArchitectsEngineers_904": (1961, "Bethlehem Structural Shapes"),
    "ia:steelhpiles00beth": (1960, "Bethlehem Steel H-Piles"),
    "ia:BethlehemOpen-webSteelJoistssSeries_825": (1959, 'Bethlehem Open-Web Steel Joists, "S" Series'),
    "ia:BethelemSteelFenceBarbedWireFencePostsBaleTiesNailsAndStaples": (1950, "Bethlehem Steel Fence catalog"),
    "ia:BethlehemCarbonSteelBarsAndSpecialSectionsWithProfilesTables": (1937, "Bethlehem Carbon Steel Bars and Special Sections"),
    "ia:bethlehem-steel-company-pdf-a": (1936, "Bethlehem Alloy and Special Steels, Catalogue 107"),
    "ia:BethlehemSteelCompanyCCA72866": (1931, "Bethlehem Sections"),
}

# The wordmark only ever spells BETHLEHEM STEEL, so every source shows the same seven letters.
# The 1961 cover is the main letterform reference and is listed first.
_MARK = [
    "ia:BethlehemStructuralShapesInformationAndTablesForArchitectsEngineers_904",
    "ia:BethelemSteelFenceBarbedWireFencePostsBaleTiesNailsAndStaples",
    "ia:steelhpiles00beth",
    "ia:BethlehemOpen-webSteelJoistssSeries_825",
    "ia:whosayssteelfram00beth",
    "ia:BethlehemCarbonSteelBarsAndSpecialSectionsWithProfilesTables",
    "ia:bethlehem-steel-company-pdf-a",
    "ia:BethlehemSteelCompanyCCA72866",
]
DOCUMENTED = {letter: list(_MARK) for letter in "BEHLMST"}

# The three cutting rules, and the letters each was read from.
RULES = {
    "shear": "Free stem ends are cut on a rising diagonal, slope 0.45, low point at the left (read from T, H, M).",
    "spur": "On a free arm end the outer edge runs 56 units longer (read from E, L).",
    "no-curves": "Bowls and rounds are rectangles with chamfered corners (read from B, S).",
}
