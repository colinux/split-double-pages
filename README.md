# README

WIP python script which will try to split a double page scanned of a book by detecting the white-separation of the pages.

This is currently a big WIP and does not work at all.

## Installation

```
virtualenv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

You'll also need to compile [PythonMagick](https://github.com/ImageMagick/PythonMagick).

```sh
# install dependencies
brew install imagemagick pkg-config libtool make
brew install boost-python --with-python3 --without-python

# download pythonmagick source code
git clone git@github.com:ImageMagick/PythonMagick.git
cd PythonMagick

# compile
./configure
make
make install
```

See also https://gist.github.com/tomekwojcik/2778301


Symlink into ENV

```
ln -s /usr/local/lib/python3.5/site-packages/PythonMagick ./ENV/lib/python3.5/site-packages
```
