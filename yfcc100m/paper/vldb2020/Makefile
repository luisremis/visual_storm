FILE = main
COMM = pdflatex

all: ${FILE}.tex
			make clean
			${COMM} ${FILE}.tex
			bibtex vdms-vldb2020
			${COMM} ${FILE}.tex
			${COMM} ${FILE}.tex
			# ${COMM} ${FILE}.tex
			# xdvi ${FILE}.dvi&
			# open ${FILE}.pdf
			make clean

clean:
	rm -f *.log *.aux *.bbl *.blg *.lot *.toc *.lof *.out *~

see: all
	gv ${FILE}.ps &
