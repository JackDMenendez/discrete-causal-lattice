#!/bin/bash
# Build script for the A=1 discrete causal lattice paper.
# Run this from inside the paper/ directory:
#   cd paper && bash build.sh

cd "$(dirname "$0")"

echo "[1/3] First pass..."
pdflatex -interaction=nonstopmode main.tex

echo "[2/3] Bibliography..."
bibtex main

echo "[3/3] Final passes..."
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

echo "Done. Output: main.pdf"
