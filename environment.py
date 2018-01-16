import sys
import getopt
import glob
import os

import constants as cst


class Environment():
    def __init__(self, argv):
        self.verbose = False
        self.debug = False
        self.files = []

        self.parse(argv)


    def parse(self, argv):
        try:
            opts, args = getopt.getopt(argv[1:], "v", ["debug", "verbose"])
        except getopt.GetoptError:
            print('main.py [-v | --verbose] [--debug] [ imgpath1, imgpath2, ...]')
            sys.exit(2)

        if len(args) > 0:
            self.files = args
        else:
            self.files = glob.glob(os.path.join(cst.INPUT_DIR, "*.jpg"))
            self.files.sort()

        self.configure(opts)

    def configure(self, opts):
        for opt, arg in opts:
            if opt == '-v' or opt == '--verbose':
                self.verbose = True
            elif opt == '--debug':
                self.debug = True


try:
    env
except NameError:
    env = Environment(sys.argv)
