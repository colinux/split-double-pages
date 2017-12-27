from PIL import Image

def open_in_landscape(filename):
    img = Image.open(filename)

    if img.height > img.width * 1.2:
        return img.rotate(90, expand=True)

    return img
