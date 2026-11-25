"""Compile the UFO to TTF with fontmake, then write WOFF2. Run via `make build`."""
import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
UFO = ROOT / "sources/BeamGothic-Regular.ufo"
TTF = ROOT / "fonts/ttf/BeamGothic-Regular.ttf"
WOFF2 = ROOT / "fonts/webfonts/BeamGothic-Regular.woff2"


def main():
    TTF.parent.mkdir(parents=True, exist_ok=True)
    WOFF2.parent.mkdir(parents=True, exist_ok=True)
    fontmake = Path(sys.executable).parent / "fontmake"
    subprocess.run(
        [str(fontmake), "-u", str(UFO), "-o", "ttf", "--output-path", str(TTF),
         "--no-production-names", "--keep-overlaps", "--verbose", "WARNING"],
        check=True,
    )
    sys.path.insert(0, str(ROOT / "scripts"))
    import postprocess
    postprocess.run(TTF)
    font = TTFont(TTF)
    font.flavor = "woff2"
    font.save(WOFF2)
    print(f"built {TTF.relative_to(ROOT)} ({TTF.stat().st_size} bytes), "
          f"{WOFF2.relative_to(ROOT)} ({WOFF2.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
