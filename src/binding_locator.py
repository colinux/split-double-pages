import numpy as np
import pandas as pd
from PIL import Image

from src.utils import debug, rescale, middle

class BindingLocator():
    # not to low, as we need the thin black binding at the middle
    DOWNSCALED_WIDTH = 400

    def __init__(self, image):
        self.image = image
        self.signal = None
        self.brightness_groups = None
        self.brightness_levels = []

    def call(self):
        img = self.downscale()
        df = self.normalized_pixels_df(img)

        self.signal = self.amplify(df)

        downscaled_binding = self.locate_binding()

        o_width, _ = self.image.size
        original_binding = round(o_width * (downscaled_binding / self.DOWNSCALED_WIDTH))

        return original_binding


    def downscale(self):
        o_width, o_height = self.image.size
        height = round((self.DOWNSCALED_WIDTH/o_width) * o_height)

        ds_img = self.image.convert('L').resize((self.DOWNSCALED_WIDTH, height), resample=Image.BILINEAR)
        return ds_img


    def normalized_pixels_df(self, img):
        pixels = list(img.getdata())
        width, height = img.size
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

        df = pd.DataFrame(pixels)

        # more contrast, reduce to a scale between O (black) and 1 (white)
        return df.applymap(
            lambda x: int(np.sqrt(x) if x < 127 else x**2)
        ) / 255**2

    def amplify(self, df):
        means = middle(df, np.nan).mean()

        apply_func = self.apply_func_factory(means)

        # amplify at center of image
        center_amplifier = means.reset_index().apply(apply_func, axis=1)

        # amplify columns with low std dev.
        low_std_amplifier = rescale(means / (1 - means.std()))


        amplified = rescale(rescale(means) * center_amplifier * low_std_amplifier)

        # normalize signal in 0-10 values rounded. 10 = maximum of white around center of image.
        return (amplified * 10).round()

    def apply_func_factory(self, serie):
        center = len(serie)/2

        def apply_func(x):
            idx = x.name
            return 1 - (abs(center - idx) ** 1.618) / center**1.618

        return apply_func


    def locate_binding(self):
        self.handle_brightness()

        # There are 4 kinds of binding:
        # 1) a strong white band
        # 2) darkest column(s) inside a bright band
        # 3) a strong dark peak
        # 4) fallback to the middle of the whitest band (brightness zone)
        return self.binding_as_strong_white_band() \
            or self.binding_as_dark_inside_white_band() \
            or self.binding_as_dark_peak() \
            or self.binding_as_brightness_max()


    def binding_as_dark_inside_white_band(self):
        white_band = self.detect_white_band()

        # local darkest inside white band
        darkest_local = white_band.min()
        debug("Darkest inside white band: %s" % darkest_local)

        if darkest_local <= self.brightness_levels.max() - 5:
            # dark band inside white columns: this is our binding
            # returns the median of these cols
            darkest_cols = white_band[white_band == darkest_local].reset_index()['index']

            binding_point = darkest_cols.median()

            debug("binding_point=%f (local dark inside white band)" % binding_point)

            return binding_point

    def binding_as_dark_peak(self):
        darkest = self.brightness_levels[0]
        dark_cols = self.cols_of_brightness(darkest)

        if darkest == 0 and len(dark_cols) <= 0.01 * self.DOWNSCALED_WIDTH:
            binding_point = dark_cols.median()

            debug("binding_point=%f (dark peak)" % binding_point)

            return binding_point

    def binding_as_strong_white_band(self):
        whitest = self.brightness_levels.max()
        white_cols = self.cols_of_brightness(whitest)
        length = len(white_cols)

        first_idx, last_idx = white_cols.min(), white_cols.max()
        expected_length = len(np.arange(first_idx, last_idx)) + 1

        debug("whitest=%i, white_cols_length=%i, expected_length=%i" % (whitest, length, expected_length))

        if whitest == 10 and expected_length == length and length >= 0.02 * self.DOWNSCALED_WIDTH:
            binding_point = white_cols.median()
            debug("binding_point=%f (strong white band)")

            return binding_point

    def binding_as_brightness_max(self):
        # mean of the whitest columns
        whitest = self.brightness_levels.max()
        binding_point = self.cols_of_brightness(whitest).median()
        debug("binding_point=%f (brightness max (default))" % binding_point)

        return binding_point

    def handle_brightness(self):
        # group signal by its value (brightness)
        self.brightness_groups = pd.DataFrame([self.signal]).T.groupby(self.signal, as_index=False)

        # brightness distinct sorted values (10 at max = whitest)
        self.brightness_levels = self.brightness_groups[0].last().round().values.flatten()
        self.brightness_levels.sort()

    def detect_white_band(self):
        # whitests columns (maximum of luminosity)
        whitest = self.brightness_levels[-1]
        white_cols = self.cols_of_brightness(whitest)

        # we want enough columns to increase sensibility
        # so we add the second whitest columns (unless it's too large or too dark)
        if len(white_cols) < 0.01 * self.DOWNSCALED_WIDTH and self.brightness_levels[-2] >= whitest - 1:
            next_group = self.cols_of_brightness(self.brightness_levels[-2])

            if len(next_group) < 0.02 * self.DOWNSCALED_WIDTH:
                white_cols = white_cols.append(next_group).sort_values()

        # First : try to detect a black binding inside the whitest columns range.
        # Use an extra margin because sometimes
        # the binding isn't preceeded or followed by a white col
        # so the binding could be just before or after the whitest cols
        first_idx, last_idx = white_cols.min(), white_cols.max()

        band = self.signal.loc[first_idx:last_idx]

        if band.min() > band.max() - 2:
            debug("Use band margin because original band min=%i, max=%i" % (band.min(), band.max()))
            margin = max(1, round(0.01 * self.DOWNSCALED_WIDTH))
            band = self.signal.loc[first_idx-margin:last_idx+margin]

        debug("White band has index range %d-%d" % (band.index[0], band.index[-1]))

        return band

    def cols_of_brightness(self, level):
        return pd.Series(self.brightness_groups.get_group(level).index)
