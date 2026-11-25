PY := .venv/bin/python
UFO := sources/BeamGothic-Regular.ufo
TTF := fonts/ttf/BeamGothic-Regular.ttf
WOFF2 := fonts/webfonts/BeamGothic-Regular.woff2

.PHONY: venv ufo build check-v1100 bounds bake-universal bake-googlefonts proof gate clean

venv:
	uv venv --python 3.12 .venv
	uv pip install -r requirements.txt

ufo:
	$(PY) sources/build_ufo.py

build: ufo
	$(PY) scripts/compile.py

check-v1100:
	$(PY) scripts/check_v1100.py

bounds:
	$(PY) scripts/bounds_check.py $(TTF)

bake-universal: build
	.venv/bin/fontbakery check-universal $(TTF) --loglevel WARN --ghmarkdown build/fontbakery-universal.md

bake-googlefonts: build
	.venv/bin/fontbakery check-googlefonts $(TTF) --loglevel WARN --ghmarkdown build/fontbakery-googlefonts.md

proof: build
	$(PY) scripts/proof.py

gate: build
	$(PY) scripts/gate.py

clean:
	rm -rf build
