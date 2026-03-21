.PHONY: all clean

build_dir := build
paper_name := main
paper_src := main.tex sections/*.tex figures/*
export TEXINPUTS := .:./macros:./sections:

$(build_dir)/$(paper_name).pdf: $(paper_src)
	-mkdir -p $(build_dir)
	pdflatex -output-directory=$(build_dir) main.tex
	bibtex $(build_dir)/main.aux
	pdflatex -output-directory=$(build_dir) main.tex
	pdflatex -output-directory=$(build_dir) main.tex

clean:
	-rm -rf $(build_dir)

all: $(build_dir)/$(paper_name).pdf 