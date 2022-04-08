name="protocol_conversion"
pdflatex "$name.tex" && bibtex "$name.aux" && pdflatex "$name.tex" && pdflatex "$name.tex"

