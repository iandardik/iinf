name="permless_mn"
pdflatex "$name.tex" && bibtex "$name.aux" && pdflatex "$name.tex" && pdflatex "$name.tex"
