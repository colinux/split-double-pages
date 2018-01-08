import glob
import os
import sys
import traceback
#import PythonMagick

import constants as cst
from src.utils import open_in_landscape
from src.binding_locator import BindingLocator
from src.vertical_split import VerticalSplit

files = glob.glob(os.path.join(cst.INPUT_DIR, "*.jpg"))
files.sort()

if len(files) == 0:
    print("Directory '%s' must contains at least 1 *.jpg file to handle." % cst.INPUT_DIR)

for filename in files:
    print("Handling %s..." % filename)

    try:
        img = open_in_landscape(filename)

        locator = BindingLocator(img)
        splitter = VerticalSplit(img, filename)

        split_x = locator.call()
        new_paths = splitter.split_at(split_x)

        print("  Splitted at x=%d :" % split_x)
        for position, path in new_paths.items():
            print("    - %s=%s" % (position, path.replace(cst.ROOT_PATH + "/", "")))

    except:
        traceback.print_exc()
    # exit()
