# README

This tool splits double pages scanned of a book by detecting the white separation of the pages (the margin) and the binding.

See below for installation instructions.


## Usage

Currently, only jpg images are handled.

Copy your images into the `input` directory.

Requirements:
- only JPG files
- the image must have room for 2 book pages (2 writtens or 1 written page on one side + 1 blank page on the other)
- the page margins (separation between pages) MUST be located around the center of the image (~ the central third of the width)
- the binding may be visible, (can help the detection when straight and well visible)
- portrait images will be rotated to landscape

```
source ENV/bin/activate # virtualenv

# by default, all images found in input dir will be splitted.
python main.py

# options and arguments
python main.py [ --verbose ] [ --debug ] path/to/image1 path/to/image2
```

Splitted pages will be found in `output` dir, with respect of the page numbers (when a number is found in the input filename).

The script detect the page separation (the margins) as a bright band near the middle of the page, with an optional dark line inside (the binding of the book).

Tips to improve results :

- input images should be fairly straight (not too skewed)
- the separation should be near the middle (not too off-centred)
- a white and enough large band, should be visible (with an optional thin dark column for the binding)
- avoid manual annotations or any trace inside margins
- increase contrast between text and background
- try in black and white

## Configuration

You can change default input/output dirs or output filenames pattern in the `constants.py` file.

## Installation

You'll need a python 3.x environment, and virtualenv.

Then :

```
virtualenv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

### PythonMagick
You'll also need to compile [PythonMagick](https://github.com/ImageMagick/PythonMagick).

For example, with MacOS :

```sh
# install dependencies
brew install imagemagick pkg-config libtool make
brew install boost-python --with-python3 --without-python

# download pythonmagick source code
git clone git@github.com:ImageMagick/PythonMagick.git
cd PythonMagick

# compile (this takes a while)
./configure
make
make install
```

See also https://gist.github.com/tomekwojcik/2778301


Symlink package into `ENV`.

For instance:

```sh
# (source dir may differ for your installation, if you're not using python 3.5 for instance)
ln -s /usr/local/lib/python3.5/site-packages/PythonMagick \
      ENV/lib/python3.5/site-packages
```

## License

Please see [LICENSE](https://github.com/colinux/split-double-pages/blob/master/LICENSE) for licensing details.
