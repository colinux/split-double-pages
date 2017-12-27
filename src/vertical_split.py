import os
import re
import constants as cst

class VerticalSplit():
    def __init__(self, original, filename):
        self.original = original
        self.filename = filename
        self.regex_original_name = \
            re.compile(r"\D+(?P<left>[0-9]+)(?:[-_](?P<right>[0-9]+))?\.jpg$")


    def split_at(self, x):
        o_width, o_height = self.original.size

        dimLeft = (0, 0, x - 1, o_height)
        imgLeft = self.original.crop(dimLeft)

        dimRight = (x, 0, o_width, o_height)
        imgRight = self.original.crop(dimRight)

        file_paths = self.pages_paths()

        imgLeft.save(file_paths['left'])
        imgRight.save(file_paths['right'])

        return file_paths

    def pages_paths(self):
        pages_names = self.pages_names()

        return {
            "left": self.output_path(pages_names["left"]),
            "right": self.output_path(pages_names["right"]),
        }

    def pages_names(self):
        match = self.regex_original_name.search(self.filename)

        # page names as numbers
        # left = int(match.group('left'))
        # right = int(match.group('right') or left + 1)

        # page names as suffixed from original
        left = match.group('left') + "-a"
        right = match.group('right') or (match.group('left') + "-b")

        return {
            "left": left,
            "right": right,
        }

    def output_path(self, page_n):
        return os.path.join(cst.ROOT_PATH, cst.OUTPUT_DIR, cst.OUTPUT_PATTERN % page_n)
