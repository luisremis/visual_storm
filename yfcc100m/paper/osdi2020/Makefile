MAIN=main
COMM=pdflatex
OUTPUT=vdms-osdi2020

all: ${MAIN}.tex
	make clean
	${COMM} -shell-escape ${MAIN}.tex
	bibtex ${MAIN}
	${COMM} -shell-escape ${MAIN}.tex
	${COMM} -shell-escape ${MAIN}.tex
	# ${COMM} ${MAIN}.tex
	# xdvi ${MAIN}.dvi&
	mv ${MAIN}.pdf ${OUTPUT}.pdf
	# open ${OUTPUT}.pdf
	make clean


clean:
	rm -f *.log *.aux *.bbl *.blg *.lot *.toc *.lof *.out *~

see: all
	gv ${MAIN}.ps &
