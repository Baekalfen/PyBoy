FONTVER=terminus-font-4.49.1

all: download codepage fontblob

download:
	curl -L https://sourceforge.net/projects/terminus-font/files/terminus-font-4.49/$(FONTVER).tar.gz | tar xz

codepage: download
	cat $(FONTVER)/uni/cntrl.uni $(FONTVER)/uni/ascii-h.uni $(FONTVER)/uni/ibm-437.uni > all-437.uni

fontblob: codepage
	python3 makefont.py $(FONTVER)/ter-u16b.bdf all-437.uni

clean:
	rm -rf $(FONTVER) all-437.uni
