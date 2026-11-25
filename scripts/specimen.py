"""Build documentation/specimen/index.html: one self-contained page with the font embedded.

Code lays out the evidence (the character grid from the font's own cmap and provenance labels,
the waterfall, the source list from the inventory). Every sentence comes from prose.json, which
is written live and carries its authoring record; this script holds no prose of its own and
refuses to build if that record is missing."""
import base64
import html
import json
import sys
from pathlib import Path

import ufoLib2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sources"))
from beam import inventory, meta  # noqa: E402

OUT = ROOT / "documentation/specimen"
prose = json.loads((OUT / "prose.json").read_text())
if not all(prose.get("_authored", {}).get(k) for k in ("by", "date", "session")):
    sys.exit("STOP: prose.json has no authoring record; specimen prose must be written live")
P = {k: html.escape(v) for k, v in prose.items() if k != "_authored"}

ufo = ufoLib2.Font.open(ROOT / "sources/BeamGothic-Regular.ufo")
woff2 = base64.b64encode((ROOT / "fonts/webfonts/BeamGothic-Regular.woff2").read_bytes()).decode()
version = f"{meta.VERSION_MAJOR}.{meta.VERSION_MINOR:03d}"

cells = []
for name in ufo.lib["public.glyphOrder"]:
    g = ufo[name]
    if not g.unicodes or g.unicodes[0] in (0x20, 0xA0, 0x25CC):
        continue
    cp = g.unicodes[0]
    label = g.lib.get("org.fontmachine.provenance", {}).get("label", "")
    ch = ("◌" if 0x300 <= cp < 0x370 else "") + chr(cp)
    cells.append(f'<div class="cell {label}"><span class="g">{html.escape(ch)}</span><span class="u">{cp:04X}</span></div>')

sources = "".join(
    f'<li><span class="yr">{year}</span><a href="https://archive.org/details/{sid[3:]}">{html.escape(title)}</a></li>'
    for sid, (year, title) in sorted(inventory.SOURCES.items(), key=lambda kv: -kv[1][0]))

WATERFALL = [(120, "BETHLEHEM STEEL"), (72, "SPARROWS POINT · LACKAWANNA"), (48, "WIDE FLANGE BEAMS & H-PILES, 1931–1966"),
             (30, "SPHINX OF BLACK QUARTZ, JUDGE MY VOW. 0123456789"), (20, "“OPEN-WEB STEEL JOISTS” @ $4.75 PER FOOT (±2%) · LOT #47 · A/B · [C] {D}")]
LANGS = [("Français", "L’ACIER ÉTIRÉ À FROID, DÉJÀ PRÊT"), ("Polski", "ZAŻÓŁĆ GĘŚLĄ JAŹŃ: STAL ŁÓDŹ"),
         ("Česky", "PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ ÚPĚL ĎÁBELSKÉ ÓDY"), ("Türkçe", "ÇELİK FABRİKASI, IŞIK VE İŞÇİ"),
         ("Română", "OȚEL ȘI FIER, ÎN ORAȘUL ȚĂRII"), ("Deutsch", "GROẞE STAHLTRÄGER FÜR BRÜCKEN"),
         ("Íslenska", "ÞÚ ERT STÁLIÐ OG ÆÐIN"), ("Magyar", "ÁRVÍZTŰRŐ TÜKÖRFÚRÓGÉP")]
LANG_TAG = {"Türkçe": "tr", "Română": "ro"}

page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Beam Gothic specimen</title>
<style>
@font-face {{ font-family: "Beam Gothic"; src: url(data:font/woff2;base64,{woff2}) format("woff2"); }}
:root {{ --ground:#F2EDE1; --ink:#17181C; --red:#C42032; --rule:#cfc7b4; --soft:#5b5a55; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--ground); color:var(--ink); font:17px/1.5 "IBM Plex Sans Condensed","Avenir Next Condensed","Helvetica Neue",Arial,sans-serif; }}
main {{ max-width:1200px; margin:0 auto; padding:56px 48px 40px; }}
.beam {{ font-family:"Beam Gothic",sans-serif; font-weight:400; line-height:1.05; }}
.mono {{ font-family:"IBM Plex Mono",Menlo,Consolas,monospace; font-size:12px; letter-spacing:.04em; text-transform:uppercase; color:var(--soft); }}
h1 {{ font-size:clamp(72px,17vw,210px); margin:0 0 20px; letter-spacing:.01em; }}
h1 span {{ color:var(--red); }}
h2 {{ margin:72px 0 18px; padding-top:14px; border-top:3px solid var(--ink); }}
p {{ max-width:68ch; margin:0 0 14px; }}
.lede {{ font-size:22px; max-width:56ch; }}
.key {{ display:flex; gap:28px; margin-top:22px; flex-wrap:wrap; }}
.key i {{ display:inline-block; width:14px; height:14px; margin-right:8px; vertical-align:-2px; background:var(--ink); }}
.key .d i {{ background:var(--red); }}
.banner {{ background:var(--ink); color:var(--ground); padding:44px 40px 36px; margin-top:56px; }}
.banner .beam {{ font-size:clamp(48px,11vw,132px); }}
.banner .beam + .beam {{ font-size:clamp(24px,5.2vw,62px); color:var(--red); margin-top:6px; }}
.banner p {{ margin:18px 0 0; color:#b9b4a6; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(74px,1fr)); border-top:1px solid var(--rule); border-left:1px solid var(--rule); margin-top:22px; }}
.cell {{ border-right:1px solid var(--rule); border-bottom:1px solid var(--rule); padding:14px 4px 6px; text-align:center; }}
.cell .g {{ display:block; font:400 40px/1.35 "Beam Gothic",sans-serif; height:62px; }}
.cell .u {{ font:10px "IBM Plex Mono",Menlo,monospace; color:var(--soft); }}
.cell.documented .g {{ color:var(--red); }}
.wf div {{ border-bottom:1px solid var(--rule); padding:14px 0; overflow-wrap:anywhere; }}
.wf .mono {{ display:block; margin-bottom:4px; }}
.rules {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:28px; margin-top:22px; }}
.rules .fig {{ font:400 190px/1.25 "Beam Gothic",sans-serif; color:var(--red); border-bottom:1px solid var(--rule); margin-bottom:14px; height:250px; }}
.rules h3 {{ margin:0 0 6px; font-size:19px; }}
.rules p {{ font-size:16px; }}
.langs div {{ display:grid; grid-template-columns:110px 1fr; gap:16px; align-items:baseline; border-bottom:1px solid var(--rule); padding:12px 0; }}
.langs .beam {{ font-size:clamp(22px,3.6vw,40px); overflow-wrap:anywhere; }}
ul.src {{ list-style:none; padding:0; margin:18px 0 0; }}
ul.src li {{ border-bottom:1px solid var(--rule); padding:9px 0; display:grid; grid-template-columns:70px 1fr; }}
ul.src .yr {{ font-family:"IBM Plex Mono",Menlo,monospace; font-size:14px; }}
a {{ color:inherit; }}
footer {{ margin-top:64px; padding-top:16px; border-top:3px solid var(--ink); font-size:15px; color:var(--soft); }}
</style></head><body><main>
<div class="mono">Specimen · Version {version} · Regular</div>
<h1 class="beam">BEAM <span>GOTHIC</span></h1>
<p class="lede">{P['lede']}</p>
<div class="key mono"><span class="d"><i></i>{P['key_documented']}</span><span><i></i>{P['key_other']}</span></div>

<div class="banner"><div class="beam">LACKAWANNA</div><div class="beam">PLANT · NEW YORK</div><p>{P['banner_note']}</p></div>

<h2 class="mono">Character set</h2>
<p>{P['charset_intro']}</p>
<div class="grid">{''.join(cells)}</div>

<h2 class="mono">Waterfall</h2>
<div class="wf">{''.join(f'<div><span class="mono">{px} px</span><span class="beam" style="font-size:{px}px">{html.escape(t)}</span></div>' for px, t in WATERFALL)}</div>

<h2 class="mono">The cutting rules</h2>
<p>{P['rules_intro']}</p>
<div class="rules">
<div><div class="fig">H</div><h3>1. {P['rule1_title']}</h3><p>{P['rule1']}</p></div>
<div><div class="fig">E</div><h3>2. {P['rule2_title']}</h3><p>{P['rule2']}</p></div>
<div><div class="fig" style="color:var(--ink)">O</div><h3>3. {P['rule3_title']}</h3><p>{P['rule3']}</p></div>
<div><div class="fig" style="color:var(--ink)">ÉÅ</div><h3>4. {P['rule4_title']}</h3><p>{P['rule4']}</p></div>
</div>

<h2 class="mono">In use</h2>
<p>{P['languages_intro']}</p>
<div class="langs">{''.join(f'<div><span class="mono">{html.escape(l)}</span><span class="beam" lang="{LANG_TAG.get(l, "")}">{html.escape(t)}</span></div>' for l, t in LANGS)}</div>

<h2 class="mono">Sources</h2>
<p>{P['sources_intro']}</p>
<ul class="src">{sources}</ul>

<footer>{P['footer']}</footer>
</main></body></html>
"""
(OUT / "index.html").write_text(page)
print(f"wrote {OUT / 'index.html'} ({len(cells)} cells)")
