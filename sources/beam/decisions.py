"""Panel decisions: the style calls the source material cannot answer.

Each decision has drawn options (see scripts/panel.py) and a recommended default. The build takes
the pick in PICKS; until the submitter picks, the recommended option stands in and the status says so.
A different option can be built without editing this file: BEAM_OPTIONS="ampersand=B,at=C" make build."""
import os

DECISIONS = {
    "P2-ampersand": {
        "options": {"A": "Et construction: E skeleton, rising stroke, spurred bar",
                    "B": "Figure-8 with a spurred leg (the cut v1.000 idea, redrawn)",
                    "C": "Reversed 3 struck through with a vertical"},
        "recommended": "A",
    },
    "P2-at": {
        "options": {"A": "Open clipped ring around a small A, the A's foot running into the ring",
                    "B": "Open clipped ring around a boxed one-storey a",
                    "C": "Closed clipped ring around a small A, no tail"},
        "recommended": "A",
    },
    "P2-lowercase": {
        "options": {"A": "Capitals on the lowercase keys",
                    "B": "Small capitals on the lowercase keys",
                    "C": "No lowercase: the keys fall back to another font"},
        "recommended": "A",
    },
}

# The submitter's picks. None means not picked yet: the recommended option is built.
# Picked by Andy on the panel page, 2026-11-25 04:19 UTC: option A for all three.
PICKS = {"P2-ampersand": "A", "P2-at": "A", "P2-lowercase": "A"}


def _overrides():
    out = {}
    for kv in os.environ.get("BEAM_OPTIONS", "").split(","):
        if "=" in kv:
            k, v = kv.split("=")
            out["P2-" + k.strip()] = v.strip()
    return out


def choice(decision):
    """The option to build for a decision: an override, else the pick, else the recommendation."""
    return _overrides().get(decision) or PICKS[decision] or DECISIONS[decision]["recommended"]


def decision_id(decision):
    return f"{decision}:{choice(decision)}"


def status(decision):
    return "picked" if PICKS[decision] else "recommended default, awaiting pick"
