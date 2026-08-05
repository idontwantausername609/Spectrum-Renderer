import pandas as pd
import numpy as np
import string
import math
import random
from scipy.signal import find_peaks


def rgb(wavelength, gamma=0.8):
    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = (1.0) ** gamma
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = (1.0) ** gamma
        B = ((-(wavelength - 510) / (510 - 490))) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = (1.0) ** gamma
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = (1.0) ** gamma
        G = ((-(wavelength - 645) / (645 - 580))) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    return (R*255, G*255, B*255)

def colored_rgb(base_rgb, final_intensity_scale):
    colored_rgb = ((base_rgb[0] * final_intensity_scale),
                   (base_rgb[1] * final_intensity_scale),
                   (base_rgb[2] * final_intensity_scale))

    return colored_rgb

def rgb_str(colored_rgb):
    rgb = f"rgb({int(colored_rgb[0])}, {int(colored_rgb[1])}, {int(colored_rgb[2])})"
    return rgb

def colours(base_rgb, final_intensity_scale):
    colored_rgb = ((base_rgb[0] * final_intensity_scale),
                   (base_rgb[1] * final_intensity_scale),
                   (base_rgb[2] * final_intensity_scale))
    rgb = f"rgb({int(colored_rgb[0])}, {int(colored_rgb[1])}, {int(colored_rgb[2])})"
    return rgb


def dynamic_prominence(prominence, int_range):
    dyn_prom = prominence * int_range
    return dyn_prom

# for final_alpha AND final_intensity_scale
def final_scale(min, factor):
    final = min + (1 - min) * factor
    return final

def generate_random_title():
    random_code = ''.join(random.choices(string.digits, k=4))
    return f'Spectrum-{random_code}'



def left_x(a, b):
    xleft = a - b / 2
    return xleft

def right_x(a, b):
    xright = a + b / 2
    return xright

def round_to_multiple(num, mult):
    rounded = math.ceil(num / mult) * mult 
    return rounded




lambda_tokens = ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm", "Observed", "Observed Wavelength", "obs", "wave"]

int_tokens =["Grey Val", "grey val", "gray val", "grayscale", "gray value", "intensity", "signal", "counts", "value", "int", "rel. int.", "grey", "Rel. Int.", "Relative Intensity", "Rel Int", "Intensity", "A", "Aki", "gA", "gf", "weighted f", "f", "Intensity/Counts", 'rel', 'count', 'flux', 'grey value',]

# Shared Values
Y_TITLE = 'Intensity'
X_TITLE = 'Wavelength (nm)'
COLOUR = 'white'
BG = 'black'
X_MIN = 400
X_MAX = 750
FIG_WIDTH = 15
DPI = 600

# Traditional Plot Values
FIG_HEIGHT_BASE = 3.0
FIG_SIZE = (FIG_WIDTH, FIG_HEIGHT_BASE)
MIN_NEEDLE_WIDTH = 0.1
MAX_NEEDLE_WIDTH = 0.3
MAX_Y_SCALE = 0.77
NEEDLE_POWER_SHAPE = 4
LABEL_NORM_INT = 0.20
GLOW_WIDTH_MULT = 1.3

# Dynamic Height Values (overflow section)
fig_height_overflow_scale = 9.0

# Normalised-Specific Values
NORM_PROM_PERC = 0.15
NORM_MIN_BRIGHT = 0.01
NORM_GLOW_ALPHA = 0
NORM_PEAK_EMPHASIS = 1.1
NORM_PEAK_LABEL_POSN = 0.75

# "Default" Values (i.e. for not normalised)
DEFAULT_PROM_PERC = 0.08    # also used by "other" plots
DEFAULT_MIN_BRIGHT = 0.1    # also used by "other" plots
DEFAULT_GLOW_ALPHA = 0.35
DEFAULT_PEAK_EMPHASIS = 1.4
DEFAULT_PEAK_LABEL_POSN = 0.77

# Other Plot Values
fig_size = (15,6)
prominence = 0.08       # changed from 0.12
min_bright = 0.1
min_alpha = 0.1
min_alpha_scatter = 0.2
base_marker_size = 2
max_marker_size_factor = 10
gamma_factor = 0.8
bar_width = 1
smoothing_window = 5    # Increase this value to control the degree of smoothing
base_sigma_nm = 0.5 # Base width of the Gaussian (for low intensity peaks)
max_sigma_multiplier = 4.0 # How much wider the highest intensity peaks can be
reverse_x = True
plot_type = None
show_grid = True
