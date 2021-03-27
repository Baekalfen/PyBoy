This project uses a portion of the bold 16 pixel height Terminus font.

The Terminus font is released under the Open Font License, which can
be found in this directory.

The full source code for the Terminus font is available at
<terminus-font.sourceforge.net>.

The embedded font should be bundled with PyBoy when you
download/install it, but this directory also contains the code needed
to recreate the compressed font object as follows:

  1. Download and extract the font source (`make download`)
  2. Make the code page file (`make all-437.uni`)
  3. Make the font object (`make font.txt`)

Of course, this process can be automated by just running `make`
without arguments.
