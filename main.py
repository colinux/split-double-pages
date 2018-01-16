import sys
import traceback

import constants as cst
from environment import env
from src.utils import log, open_in_landscape
from src.binding_locator import BindingLocator
from src.vertical_split import VerticalSplit


if len(env.files) == 0:
    print("Directory '%s' must contains at least 1 *.jpg file to handle." % cst.INPUT_DIR)

for filename in env.files:
    log("Handling %s..." % filename)

    try:
        img = open_in_landscape(filename)

        locator = BindingLocator(img)
        splitter = VerticalSplit(img, filename)

        split_x = locator.call()
        new_paths = splitter.split_at(split_x)

        log("  Splitted at x=%d :" % split_x)
        for position, path in new_paths.items():
            log("    - %s=%s" % (position, path.replace(cst.ROOT_PATH + "/", "")))

    except Exception:
        traceback.print_exc()
    # exit()
