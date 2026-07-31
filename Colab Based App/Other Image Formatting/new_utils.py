import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import math
import random
import string
import helper_utils
import prep_utils

#show_grid = None

# ===============
# From utils.py
# ===============

def generate_random_title():
    random_code = ''.join(random.choices(string.digits, k=4))
    return f'Spectrum-{random_code}'

# =======================
# Calculation Functions
# =======================

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

def round_to_multiple(num, mult):
    rounded = math.ceil(num / mult) * mult 
    return rounded

def colored_rgb(base_rgb, final_intensity_scale):
    colored_rgb = (base_rgb[0] * final_intensity_scale,
                   base_rgb[1] * final_intensity_scale,
                   base_rgb[2] * final_intensity_scale)
    return colored_rgb

def set_y_lim(graph_type, show_peak_labels):
    if graph_type == 'scatter' or show_peak_labels is True:
        if prep_utils.Y_MAX > 230:
            y_max = round_to_multiple(prep_utils.Y_MAX, 100)
        else:
            y_max = round_to_multiple(prep_utils.Y_MAX, 50)
    else:
        y_max = round_to_multiple(prep_utils.Y_MAX, 50)
    print('(set_y_lim)', y_max)
    return y_max


# ==================================
# Other Image Formatiing Functions
# ==================================

def peak_labels(data_df, show_label_colour, ):
    peaks, _ = find_peaks(data_df[helper_utils.INT_col], prominence=dynamic_prominence(helper_utils.DEFAULT_PROM_PERC, prep_utils.int_range)) # Using dynamic prominence
    # Label the identified sharp peaks
    for peak_index in peaks:
        row = data_df.iloc[peak_index]
        wl_labels = float(data_df.iloc[peak_index][helper_utils.wl_col])
        base_rgb = helper_utils.rgb(wl_labels)
        final_intensity_scale = 1.0
        color_rgb = colored_rgb(base_rgb, final_intensity_scale)
        
        if show_label_colour is True: #and mode == 'dark':
            plt.annotate(f"{row[helper_utils.wl_col]:.2f} nm", # Formatted nm to two decimal places
                        (row[helper_utils.wl_col], row[helper_utils.INT_col]),
                        textcoords="offset points", # Offset the text
                        xytext=(0,10), # Distance from point to label
                        ha='center', # Horizontal alignment
                        color=color_rgb,        # this makes the text rgb
                        )
        else:
            plt.annotate(f"{row[helper_utils.wl_col]:.2f} nm", # Formatted nm to two decimal places
                        (row[helper_utils.wl_col], row[helper_utils.INT_col]),
                        textcoords="offset points", # Offset the text
                        xytext=(0,10), # Distance from point to label
                        ha='center', # Horizontal alignment
                        color = helper_utils.COLOUR,
                        )

# =============================
# Traditional Spec Codes
# =============================

def trad_spec_labels(fig, title, random_title, ax, x_min, x_max, has_any_nist, scale_mode, figure_bg_color = helper_utils.BG, text_color = helper_utils.COLOUR):

    if has_any_nist or scale_mode == 'raw': 
        pad = 15
    else:
        pad = 10

    if title:
        plt.title(str(title).strip(), color = text_color, y=0.98, pad=pad)
    if random_title:
        plt.title(str(generate_random_title()), color=text_color, y=0.98, pad=pad)

    fig.patch.set_facecolor(figure_bg_color)
    ax.set_facecolor('black')  
    ax.yaxis.set_visible(False)
    ax.set_xlabel(helper_utils.X_TITLE, color=text_color)
    ax.xaxis.set_major_locator(helper_utils.major_locator)
    ax.xaxis.set_minor_locator(helper_utils.minor_locator)
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0,1)