FILE = p1971-remis
COMM = pdflatex

all: ${FILE}.tex
	make clean
	${COMM} -shell-escape ${FILE}.tex
	bibtex ${FILE}
	${COMM} -shell-escape ${FILE}.tex
	${COMM} -shell-escape ${FILE}.tex
	# ${COMM} ${FILE}.tex
	# xdvi ${FILE}.dvi&
	# open ${FILE}.pdf
	make clean

clean:
	rm -f *.log *.aux *.bbl *.blg *.lot *.toc *.lof *.out *~

see: all
	gv ${FILE}.ps &
