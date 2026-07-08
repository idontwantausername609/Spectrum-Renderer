import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np
from scipy.signal import find_peaks
import matplotlib.ticker as ticker


y_title = 'Intensity'
x_title = 'Wavelength (nm)'
fig_size = (15,6)
prominence = 0.12
min_bright = 0.1
min_alpha = 0.1
min_alpha_scatter = 0.2
base_marker_size = 5
max_marker_size_factor = 95
gamma_factor = 0.8
bar_width = 1
smoothing_window = 5    # Increase this value to control the degree of smoothing
base_sigma_nm = 0.5 # Base width of the Gaussian (for low intensity peaks)
max_sigma_multiplier = 4.0 # How much wider the highest intensity peaks can be
x_min = 400
x_max = 750
reverse_x = True
show_grid = True
plot_type = None



major_locator = ticker.MultipleLocator(50)
minor_locator = ticker.MultipleLocator(10)


lambda_tokens = ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm", "Observed", "Observed Wavelength", "obs", "wave"]

int_tokens =["Grey Val", "grey val", "gray val", "grayscale", "gray value", "intensity", "signal", "counts", "value", "int", "rel. int.", "grey", "Rel. Int.", "Relative Intensity", "Rel Int", "Intensity", "A", "Aki", "gA", "gf", "weighted f", "f", "Intensity/Counts", 'rel', 'count', 'flux', 'grey value',]


def resolve_column(df, candidates, label):
    headers = [(str(col).strip(), str(col).strip().lower()) for col in df.columns]

    # Build a flat keyword list from all candidates.
    # Each candidate may be a phrase; we split on non-alphanumeric characters.
    keywords = []
    for candidate in candidates:
        text = str(candidate).strip().lower()
        if not text:
            continue
        parts = [part for part in re.split(r'[^a-z0-9]+', text) if part]
        keywords.extend(parts if parts else [text])

    # Prefer exact matches first, then keyword containment.
    for original, normalized in headers:
        for candidate in candidates:
            candidate_norm = str(candidate).strip().lower()
            if candidate_norm and normalized == candidate_norm:
                return original

    for original, normalized in headers:
        for keyword in keywords:
            if keyword and keyword in normalized:
                return original

    raise KeyError(f"Could not find a {label} column. Available columns: {list(df.columns)}")


def res_col_names(
    data_df,
    nm_col = None,
    int_col = None,
):
    global wl_col
    global INT_col
    if nm_col is None:
        wl_col = resolve_column(data_df, lambda_tokens, "wavelength",)
    if int_col is None:
        INT_col = resolve_column(data_df, int_tokens, "intensity",)

    print(wl_col, INT_col)
    return data_df, wl_col, INT_col


def rgb(wavelength, gamma=gamma_factor):

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
    return (R, G, B)

def get_mode():
    global mode
    inp = input("Choose Mode: Dark or Light").lower()
    if inp == 'dark' or inp == 'd':
        mode = 'dark'
    elif inp == 'light' or inp == 'l':
        mode = 'light'
    return mode

def dynamic_prominence(prominence, int_range):
    dyn_prom = prominence * int_range
    return dyn_prom

# for final_alpha AND final_intensity_scale
def final_scale(min, factor):
    final = min + (1 - min) * factor
    return final

def left_x(a, b):
    xleft = a - b / 2
    return xleft

def right_x(a, b):
    xright = a + b / 2
    return xright

def colored_rgb(base_rgb, final_intensity_scale):
    colored_rgb = (base_rgb[0] * final_intensity_scale,
                   base_rgb[1] * final_intensity_scale,
                   base_rgb[2] * final_intensity_scale)
    return colored_rgb

def text_colour():
    global colour
    global bg
    if mode == 'dark':
        colour = 'white'
        bg = 'black'
    if mode == 'light':
        colour = 'black'
        bg = 'white'
    return colour, bg

def axis_labels(
    fig_size = (15, 6),
    show_grid = True,
    reverse_x = None,
    x_min = 400,
    x_max = 750,
    x_title = "Wavelength (nm)",
    y_title = "Intensity",
    text = None,
):
    
    plt.figure(figsize=fig_size)
    ax = plt.gca()
    get_mode()
    text_colour()
    print ("text colour:", colour, "bg colour:", bg, "mode:", mode)

    if mode == 'dark':
        fig_bg = bg
        text = colour
        plt.gcf().set_facecolor(fig_bg)
        if show_grid is True:
            plt.grid(show_grid, color='darkgrey', linestyle=':', linewidth=0.5)
    else:
        fig_bg = bg
        text = colour
        if show_grid is True:
            plt.grid(show_grid)
    
    reverse_x = (input("Reverse x-axis? Yes or No")).lower()
    if reverse_x == 'yes' or reverse_x == 'y':
        reverse_x is True
        plt.xlim(x_max, x_min)
    else:
        reverse_x is False
        plt.xlim(x_min, x_max)

    ax.set_facecolor(fig_bg)
    plt.xlabel(x_title, color=text)
    plt.ylabel(y_title, color=text)
    plt.xticks(color=text)
    plt.yticks(color=text)

# =============================
# Traditional Spec Codes
# =============================

def get_generic_type():
    global generic_type
    gen_type = (input('Choose Rendering: Raw or Normalised')).lower()
    if gen_type == 'raw' or gen_type == 'r':
        generic_type = 'raw'
    elif gen_type == 'normalised' or gen_type == 'norm' or gen_type == 'n':
        generic_type = 'normalised'
    
    print (generic_type)
    return generic_type

def trad_spec_labels(fig, ax, x_min, x_max,):
    get_mode()
    text_colour()

    global figure_bg_color
    global text_color
    
    if mode == 'dark':
        figure_bg_color = 'black'
        text_color = colour
    elif mode == 'light':
        figure_bg_color = 'white'
        text_color = colour
    print("mode:", mode, ", fig bg colour:", figure_bg_color)

    fig.patch.set_facecolor(figure_bg_color)
    ax.set_facecolor('black')  
    ax.yaxis.set_visible(False)
    ax.set_xlabel(x_title, color=text_color)
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_minor_locator(minor_locator)
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0,1)

