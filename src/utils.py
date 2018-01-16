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

def rescale(serie):
    serie -= serie.min()
    return serie / serie.max()

def middle(df, replacement):
    df2 = df.copy()

    third = int(len(df.columns) / 3)

    df2.loc[:, :third] = replacement
    df2.loc[:, 2*third:] = replacement

    return df2
