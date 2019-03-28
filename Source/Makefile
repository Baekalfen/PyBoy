
.PHONY: build clean run

all: build run

NUMPY := $(shell python -c 'import numpy; print numpy.get_include()')
SDL := $(shell sdl2-config --static-libs)

# CFLAGS := $(CFLAGS)
CFLAGS := ""
CFLAGS += "-I$(NUMPY)"
CFLAGS += "-I/usr/local/include/SDL2/"
CFLAGS += "-I/usr/local/Cellar/sdl2/2.0.9_1/include/SDL2"
CFLAGS += "-L/usr/local/lib"
CFLAGS += "-L/usr/local/lib"
# Don't know why, the following line doesn't work. But providing the output on separate lines, work...
# CFLAGS += "$(SDL)" # Too many variables, but gives the -L above
CFLAGS += "-lSDL2"
CFLAGS += "-lm"
CFLAGS += "-liconv"
CFLAGS += "-Wl,-framework,CoreAudio"
CFLAGS += "-Wl,-framework,AudioToolbox"
CFLAGS += "-Wl,-framework,ForceFeedback"
CFLAGS += "-lobjc"
CFLAGS += "-Wl,-framework,CoreVideo"
CFLAGS += "-Wl,-framework,Cocoa"
CFLAGS += "-Wl,-framework,Carbon"
CFLAGS += "-Wl,-framework,IOKit"
CFLAGS += "-Wl,-weak_framework,QuartzCore"
CFLAGS += "-Wl,-weak_framework,Metal"

CFLAGS += "-DCYTHON_WITHOUT_ASSERTIONS"
CFLAGS += "-O3"
CFLAGS += "-F/Library/Frameworks -framework SDL2"
export CFLAGS

export SDL2_INCLUDE_DIR="/Library/Frameworks/SDL2.framework/Headers"

PATH += "/usr/local/bin"
export PATH

build:
	@echo "Building..."
	@echo $(CFLAGS)
	/usr/local/bin/python setup.py build_ext --inplace

clean:
	@echo "Cleaning..."
	find . -name "*.pyo" -delete
	find . -name "*.pyc" -delete
	find . -name "*.so" -delete
	find . -name "*.c" -delete
	find . -name "*.h" -delete
	find . -name "*.html" -delete

run:
	python main.py SDL2 ROMs/POKEMON\ BLUE.gb
	# python main.py SDL2 ROMs/pokemon_gold.gbc
	# python main.py dummy ROMs/pokemon_gold.gbc
