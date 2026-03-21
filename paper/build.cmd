@echo off
REM Build script for the A=1 discrete causal lattice paper.
REM Run this from inside the paper/ directory.
REM
REM Usage:
REM   cd paper
REM   build.cmd

cd /d "%~dp0"

echo [1/3] First pass...
pdflatex -interaction=nonstopmode main.tex

echo [2/3] Bibliography...
bibtex main

echo [3/3] Final pass...
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

echo Done. Output: main.pdf
