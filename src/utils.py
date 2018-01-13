from PIL import Image
from environment import env

def open_in_landscape(filename):
    img = Image.open(filename)

    if img.height > img.width * 1.2:
        return img.rotate(90, expand=True)

    return img


def log(msg):
    if env.verbose or env.debug:
        print(msg)

def debug(msg):
    if env.debug:
        print("DEBUG: %s" % msg)
