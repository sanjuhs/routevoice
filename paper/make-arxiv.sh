#!/bin/sh
# Package the paper source for arXiv: build/routevoice-arxiv.tar.gz
# arXiv does not run BibTeX, so the generated main.bbl is included.
set -eu
cd "$(dirname "$0")"
mkdir -p build
tectonic -X compile --keep-intermediates --outdir build main.tex
rm -rf build/arxiv-src && mkdir -p build/arxiv-src/sections build/arxiv-src/figures
cp main.tex refs.bib build/main.bbl build/arxiv-src/
cp sections/*.tex build/arxiv-src/sections/
cp figures/*.tex figures/*.pdf figures/*.jpg build/arxiv-src/figures/
tar -C build/arxiv-src -czf build/routevoice-arxiv.tar.gz .
ls -la build/routevoice-arxiv.tar.gz
