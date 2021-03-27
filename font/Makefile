FONTVER=terminus-font-4.49.1

.PHONY: all clean download install

all: $(FONTVER) all-437.uni font.txt

$(FONTVER):
	curl -L https://sourceforge.net/projects/terminus-font/files/terminus-font-4.49/$(FONTVER).tar.gz | tar xz

download: $(FONTVER)

all-437.uni: $(FONTVER)
	cat $(FONTVER)/uni/cntrl.uni $(FONTVER)/uni/ascii-h.uni $(FONTVER)/uni/ibm-437.uni > all-437.uni

font.txt: all-437.uni $(FONTVER) makefont.py
	python3 makefont.py $(FONTVER)/ter-u16b.bdf all-437.uni

install: font.txt
	cp -v font.txt ../pyboy/plugins/font.txt

clean:
	rm -rf $(FONTVER) all-437.uni font.txt
