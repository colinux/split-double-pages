import numpy as np
import pandas as pd
from PIL import Image

class BindingLocator():
    # not to low, as we need the thin black binding at the middle
    DOWNSCALED_WIDTH = 400

    def __init__(self, image):
        self.image = image

    def call(self):
        img = self.downscale()
        df = self.normalized_pixels_df(img)

        means = df.mean()

        amplified = self.amplify(means)

        downscaled_binding = self.locate_binding(amplified)

        o_width, _ = self.image.size
        original_binding = round(o_width * (downscaled_binding / self.DOWNSCALED_WIDTH))

        return original_binding


    def downscale(self):
        o_width, o_height = self.image.size
        height = round((self.DOWNSCALED_WIDTH/o_width) * o_height)

        ds_img = self.image.resize((self.DOWNSCALED_WIDTH, height), resample=Image.BICUBIC)
        return ds_img


    def normalized_pixels_df(self, img):
        pixels = list(img.getdata())
        width, height = img.size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

        df = pd.DataFrame(pixels)

        # more contrast, reduce to a scale between O (black) and 1 (white)
        return df.applymap(
            lambda x: int(np.sqrt(x) if x <= 127 else x**2)
        ) / 255**2


    def amplify(self, means):
        apply_func = self.apply_func_factory(means)

        # amplify signal at center of image
        amplifier = means.reset_index().apply(apply_func, axis=1)

        # 0-10 values rounded. 10 = maximum of white around center of image.
        return (means * amplifier * 10).round()


    def apply_func_factory(self, serie):
        center = len(serie)/2

        def apply_func(x):
            idx = x.name
            return 1 - (abs(center - idx) ** 2) / center**2

        return apply_func


    def locate_binding(self, amplified):
        # group series by its value
        grouped = amplified.reset_index().groupby(amplified, as_index=False)

        # luminosity distinct sorted values (10 at max = whitest)
        lum_val = grouped[0].last().round().values.flatten()
        lum_val.sort()
        whitest = lum_val[-1]

        # whitests columns (maximum of luminosity)
        white_cols = grouped.get_group(whitest)['index']

        # we want enough columns to increase sensibility
        # so we add the second whitest columns (unless it's too large)
        if len(white_cols) < 0.02 * self.DOWNSCALED_WIDTH:
            next_group = grouped.get_group(lum_val[-2])['index']
            if len(next_group) < 0.1 * self.DOWNSCALED_WIDTH:
                white_cols = white_cols.append(next_group)

        # first : try to detect a black binding
        # inside the whitest columns range (with an added margin)
        first_idx, last_idx = white_cols.min(), white_cols.max()
        margin = max(1, round(0.01 * self.DOWNSCALED_WIDTH))
        white_band = amplified[first_idx-margin:last_idx+margin]

        # local darkest inside white band
        band_min = white_band.min()

        if band_min <= whitest - 2:
            # dark band inside white columns: this is our binding
            # returns the median of these cols
            darkest_cols = white_band[white_band == band_min].reset_index()['index']
            return darkest_cols.median()
        else:
            # median of the whitest columns
            return white_cols.median()
