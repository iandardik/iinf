name="mn_theorem"
pdflatex "$name.tex" && bibtex "$name.aux" && pdflatex "$name.tex" && pdflatex "$name.tex"
