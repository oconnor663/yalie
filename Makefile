all: report.pdf yalie.tar.gz

report.pdf: report.tex README builtins.y
	pdflatex report.tex && pdflatex report.tex

yalie.tar.gz: yalie.py README builtins.y
	mkdir yalie/
	cp yalie.py README builtins.y yalie/
	tar cfz yalie.tar.gz yalie/
	rm -rf yalie/
