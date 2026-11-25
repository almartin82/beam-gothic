"""Font-wide metadata. One place for every name-table and OS/2 value the build writes."""

FAMILY = "Beam Gothic"
STYLE = "Regular"
VERSION_MAJOR = 2
VERSION_MINOR = 1            # head.fontRevision 2.001

REPO_URL = "https://github.com/almartin82/beam-gothic"
COPYRIGHT = f"Copyright 2026 The Beam Gothic Project Authors ({REPO_URL})"
DESIGNER = "Andy Martin"
MANUFACTURER = "font-machine"
# Chosen by Andy, 2026-11-25. Not yet registered with Microsoft.
VENDOR_ID = "ANDY"
DESCRIPTION = (
    "Beam Gothic is an original caps-only display face drawn after the lettering of the "
    "Bethlehem Steel wordmark, c. 1931-1966: sheared stems, spurred arms, no curves."
)
LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org"
)
LICENSE_URL = "https://openfontlicense.org"

# Vertical metrics, Google Fonts rule: typo == hhea, line gap 0, Use-Typo-Metrics on,
# win covers the bounding box. v1.200 kept 820/-200. The accents of v2 reach 895 and the comma
# below reaches -200, so the metrics grow to 950/-250 (1.2 em, the Google Fonts minimum).
ASCENDER = 950
DESCENDER = -250
WIN_ASCENT = 950
WIN_DESCENT = 250

UNDERLINE_POSITION = -110
UNDERLINE_THICKNESS = 70

# PANOSE: Latin text, normal sans, bold, condensed, no contrast, no stroke variation,
# straight arms / wedge, normal contact, standard midline, constant large x-height.
PANOSE = [2, 11, 8, 6, 2, 2, 3, 2, 2, 4]
