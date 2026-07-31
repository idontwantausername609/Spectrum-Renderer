This file holds the 2D combined code including the Smoothed Plot code. 

=============================
2d_combined_playground.py
=============================
import pandas as pd
import matplotlib.pyplot as plt
import utils
import new_utils
import prep_utils
import plot_funcs
import helper_utils

H_SHEET = "Colab Based App/Other Image Formatting/h test.xlsx"
HE_SHEET = "he test.xlsx"
NIST_SHEET = "oxygen nist 2.xlsx"
H_DF = pd.read_excel(H_SHEET)
HE_DF = pd.read_excel(HE_SHEET)
NIST_DF = pd.read_excel(NIST_SHEET)
global df  
df = NIST_DF

def trad_spec(data_df, fig_size=utils.FIG_SIZE, dpi=utils.DPI,):
    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = data_df)
    if should_exit_early:
        fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
        ax.set_axis_off()
        print("Ending Rendering Early.")
        return fig
    fig, ax = plot_funcs.plot(df_plot_data = df_plot_data, nm_col = helper_utils.wl_col, has_any_nist=has_any_nist)
    return fig

def plot_other_spec(data_df):
    helper_utils.get_graph_type()
    if helper_utils.graph_type == 'traditional':
        trad_spec(data_df=data_df)
    else:
        new_utils.scale_by_int()
        data_df, should_exit_early = prep_utils.prep_other(data_df = data_df)
        if should_exit_early:
            fig, ax = plt.subplots(figsize=new_utils.fig_size, dpi=utils.DPI)
            ax.set_axis_off()
            print("Ending Rendering Early.")
            return fig
        new_utils.axis_labels()

        if helper_utils.graph_type == 'bar':
            plot_funcs.bar_iteration(data_df = data_df)
            plt.title("Bar Chart", color = new_utils.colour)    # want bar title to be "Bar Chart", rest are set to "Plot". have to figure out how to make that conditional.
        elif helper_utils.graph_type == 'scatter':
            plot_funcs.scatter_iteration(data_df = data_df)
        elif helper_utils.graph_type == 'gaussian':
            plot_funcs.gaussian_iteration(df_plot_data= data_df)
        elif helper_utils.graph_type == 'line':
            plot_funcs.line_plot_iteration(data_df=data_df)
        elif helper_utils.graph_type == 'smoothed line':
            plot_funcs.filled_plot(data_df = data_df)
        elif helper_utils.graph_type == 'filled line':
            plot_funcs.filled_plot(data_df = data_df)

def detect_prep(data_df, force_nist = None):
    df_data, has_any_nist = prep_utils.run_nist_check(data_df=data_df, force_nist=force_nist)
    if has_any_nist is True:
        prep_type = 'nist'
        nist_plot_type = input("NIST Descriptors Detected. Choose NIST Graph Type: Gaussian or Traditional").lower()
        if nist_plot_type == 'gaussian' or nist_plot_type == 'g':
            helper_utils.graph_type = 'gaussian'
            new_utils.axis_labels()
            plot_funcs.gaussian_iteration(df_plot_data = df_data)
        if nist_plot_type == 'traditional' or nist_plot_type == 'trad' or nist_plot_type == 't':
            helper_utils.graph_type = 'traditional'
            trad_spec(data_df = df_data)
    else:
        prep_type = 'generic'
        plot_other_spec(data_df=df_data)
    return prep_type, helper_utils.graph_type

detect_prep(H_DF)
plt.show()


=============
new_utils.py
=============

import matplotlib.pyplot as plt
import math
import helper_utils
import prep_utils

#show_grid = None

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

def set_y_lim():
    if helper_utils.graph_type == 'scatter':
        if prep_utils.y_max > 230:
            y_max = round_to_multiple(prep_utils.y_max, 100)
        else:
            y_max = round_to_multiple(prep_utils.y_max, 50)
    else:
        y_max = round_to_multiple(prep_utils.y_max, 50)
    print('(set_y_lim)', y_max)
    return y_max

# ===========================
# Prompting Functions
# ===========================

def scale_by_int():
    global SCALE_BY_INT
    scale = input("Scale brightness by intensity? Yes or No").lower()
    if scale == 'yes' or scale == 'y':
        SCALE_BY_INT = 'yes'
    elif scale == 'no' or scale == 'n':
        SCALE_BY_INT = 'no'
    print('\nScale brightness:', SCALE_BY_INT.capitalize())

def get_mode():
    global mode
    inp = input("Choose Mode: Dark or Light").lower()
    if inp == 'dark' or inp == 'd':
        mode = 'dark'
    elif inp == 'light' or inp == 'l':
        mode = 'light'
    return mode

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



# ==================================
# Other Image Formatiing Functions
# ==================================

def axis_labels(
    fig_size = helper_utils.fig_size,
    reverse_x = helper_utils.reverse_x,
    x_min = helper_utils.x_min,
    x_max = helper_utils.x_max,
    x_title = helper_utils.x_title,
    y_title = helper_utils.y_title,
    text = None,
    y_min = 0,
    y_max = 0,
):
    
    plt.figure(figsize=fig_size)
    ax = plt.gca()
    get_mode()
    text_colour()
    show = input("Show Grid? Yes or No").lower()

    if mode == 'dark':
        fig_bg = bg
        text = colour
        plt.gcf().set_facecolor(fig_bg)
        for spine in ax.spines.values():        # new block. may have to take out or decrease linewidth. 
            spine.set_linewidth(0.3)
            spine.set_color('darkgrey')
        if show == 'yes' or show == 'y':
            plt.grid(True, color='darkgrey', linewidth=0.25)   # took out 'linestyle = ':' '    may have to add back in. 
        elif show == 'no' or show == 'n':
            plt.grid(False)
    else:
        fig_bg = bg
        text = colour
        for spine in ax.spines.values():       # new block
            spine.set_linewidth(0.5)
        if show == 'yes' or show == 'y':
            plt.grid(True)
        elif show == 'no' or show == 'n':
            plt.grid(False)


    reverse_x = (input("Reverse x-axis? Yes or No")).lower()
    if reverse_x == 'yes' or reverse_x == 'y':
        reverse_x is True
        plt.xlim(x_max, x_min)
    else:
        reverse_x is False
        plt.xlim(x_min, x_max)

    print(reverse_x)

    y_max = set_y_lim()

    ax.set_facecolor(fig_bg)
    plt.xlabel(x_title, color=text)
    plt.ylabel(y_title, color=text)
    plt.xticks(color=text)
    plt.yticks(color=text)
    ax.yaxis.set_major_locator(helper_utils.major_locator)
    plt.title(f'{helper_utils.graph_type.title()} Plot', color = colour)
    plt.ylim(y_min, y_max)
    

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
    print ('Rendering Type: ', generic_type)
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

    fig.patch.set_facecolor(figure_bg_color)
    ax.set_facecolor('black')  
    ax.yaxis.set_visible(False)
    ax.set_xlabel(helper_utils.x_title, color=text_color)
    ax.xaxis.set_major_locator(helper_utils.major_locator)
    ax.xaxis.set_minor_locator(helper_utils.minor_locator)
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0,1)


==================
helper_utils.py
==================

'''
this module has the predefined variables, get_graph_type(), set_grid(), the intensity column resolving, and the rgb conversion functions. 
'''

import re
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
plot_type = None
show_grid = True


major_locator = ticker.MultipleLocator(50)
minor_locator = ticker.MultipleLocator(10)


lambda_tokens = ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm", "Observed", "Observed Wavelength", "obs", "wave"]

int_tokens =["Grey Val", "grey val", "gray val", "grayscale", "gray value", "intensity", "signal", "counts", "value", "int", "rel. int.", "grey", "Rel. Int.", "Relative Intensity", "Rel Int", "Intensity", "A", "Aki", "gA", "gf", "weighted f", "f", "Intensity/Counts", 'rel', 'count', 'flux', 'grey value',]


def get_graph_type():
    global graph_type, plot_type
    plot_type = None
    GRAPH_TYPE = input("Choose Graph Type: Line, Bar, Scatter, Gaussian, Traditional").lower()
    if GRAPH_TYPE == 'bar' or GRAPH_TYPE == 'b':
        graph_type = 'bar'
    elif GRAPH_TYPE == 'scatter' or GRAPH_TYPE == 's':
        graph_type = 'scatter'
    elif GRAPH_TYPE == 'gaussian' or GRAPH_TYPE == 'g':
        graph_type = 'gaussian'
    elif GRAPH_TYPE == 'line' or GRAPH_TYPE == 'l':
        FILL_TYPE = input("Filled Graph? Choose: Yes or No").lower()
        if FILL_TYPE == 'yes' or FILL_TYPE == 'y':
            PLOT_TYPE = input("Smoothed Fill? Choose: Yes or No").lower()
            if PLOT_TYPE == 'yes' or PLOT_TYPE == 'y':
                graph_type = 'smoothed line'
                plot_type = 'Smoothed'
            elif PLOT_TYPE == 'n' or PLOT_TYPE == 'no':
                graph_type = 'filled line'
                plot_type = 'filled'
        else:
            graph_type = 'line'           
    elif GRAPH_TYPE == 'traditional' or GRAPH_TYPE == 'trad' or GRAPH_TYPE == 't':
        graph_type = 'traditional'

    return GRAPH_TYPE



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


def res_col_names(data_df, nm_col = None, int_col = None,):
    global wl_col
    global INT_col
    if nm_col is None:
        wl_col = resolve_column(data_df, lambda_tokens, "wavelength",)
    if int_col is None:
        INT_col = resolve_column(data_df, int_tokens, "intensity",)
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



==================
plot_funcs.py
==================

import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import utils
import nist_codes
import matplotlib.patheffects as pe
import new_utils
import prep_utils
import helper_utils

detection_col = '_raw_int'
int_col = '_adj_int'


# ================
# Traditonal Plot
# ================

# updated to work with trad_spec(). eventually want it to work with set_generic_type()

def plot(
    df_plot_data,
    nm_col,
    has_any_nist,
    prominence_percentage=0,     
    fig_size=utils.FIG_SIZE,
    min_brightness=0,
    peak_wavelengths=None,
    show_peak_labels=True,
    x_min=utils.X_MIN,
    x_max=utils.X_MAX,
    min_needle_max_width_nm=utils.MIN_NEEDLE_WIDTH,
    max_needle_max_width_nm=utils.MAX_NEEDLE_WIDTH,
    needle_shape_power=utils.NEEDLE_POWER_SHAPE,
    glow_width_multiplier=utils.GLOW_WIDTH_MULT,
    glow_alpha=0,
    dpi=utils.DPI,
    peak_label_y_position=0,
    label_min_norm_int=utils.LABEL_NORM_INT,
    subplots_adjust_top = 0.90,
    max_needle_y = utils.MAX_Y_SCALE,
    fig_height_overflow_scale = utils.fig_height_overflow_scale,
    fig_height_base = utils.FIG_HEIGHT_BASE,
):

    fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
    new_utils.trad_spec_labels(fig=fig, ax=ax, x_min=x_min, x_max=x_max)

    if has_any_nist:
        new_utils.generic_type = None
        min_brightness = utils.DEFAULT_MIN_BRIGHT
        glow_alpha = utils.DEFAULT_GLOW_ALPHA
        prominence_percentage = utils.DEFAULT_PROM_PERC
        peak_label_y_position = utils.DEFAULT_PEAK_LABEL_POSN
    else:
        new_utils.get_generic_type()
        if new_utils.generic_type == 'raw':
            glow_alpha = utils.DEFAULT_GLOW_ALPHA
            peak_label_y_position = utils.DEFAULT_PEAK_LABEL_POSN
        elif new_utils.generic_type == 'normalised':
            glow_alpha = utils.NORM_GLOW_ALPHA
            peak_label_y_position = utils.NORM_PEAK_LABEL_POSN

    # --- Peak Detection ---
    if peak_wavelengths is not None:
        nm_vals = df_plot_data[helper_utils.wl_col].values
        peaks = []
        for pw in peak_wavelengths:
            try:
                pv = float(pw)
            except Exception:
                continue
            idx = int(np.argmin(np.abs(nm_vals - pv)))
            peaks.append(idx)
        peaks = sorted(set(peaks))
    elif has_any_nist:
        peaks = nist_codes.identify_spectral_peaks(df_plot_data.reset_index(drop=True), prominence_percentage, peak_wavelengths=None)
    else:
        raw_min = df_plot_data[detection_col].min()
        raw_max = df_plot_data[detection_col].max()
        raw_range = raw_max - raw_min
        if new_utils.generic_type=='raw':
            prominence_percentage = utils.DEFAULT_PROM_PERC
        if new_utils.generic_type == 'normalised':
            prominence_percentage = utils.NORM_PROM_PERC
        dynamic_prominence = prominence_percentage * (raw_range if raw_range != 0 else 1.0)
        peaks, _ = find_peaks(df_plot_data[helper_utils.INT_col], prominence=dynamic_prominence)
    
    peak_nms = [float(df_plot_data.iloc[index][helper_utils.wl_col]) for index in peaks]
    peak_ints = [float(df_plot_data.iloc[index]["Norm_Int"]) for index in peaks]
    init_peak_label_y_posn = peak_label_y_position
    try:
        label_ys = utils.compute_label_positions(
            peak_nms,
            intensities=peak_ints,
            base_y=init_peak_label_y_posn,
            min_sep_nm=0.4,
            y_step=0.08,
            method="prefer_stronger_top",
            max_y=0.90,
        )
    except Exception:
        label_ys = [init_peak_label_y_posn] * len(peaks)

    if label_ys:
        max_label_y = max(label_ys)
        overflow = max(0, max_label_y - init_peak_label_y_posn)
        print("\noverflow:", overflow)
        print("o.g. peak label y pos'n:", init_peak_label_y_posn)
        if overflow > 0:
            new_height = fig_height_base + overflow * fig_height_overflow_scale
            new_fig_height = new_height
            fig.set_figheight(new_height)
            current_needle_height_in = max_needle_y * new_height
            new_needle_height = (max_needle_y * fig_height_base) / new_height 
            max_needle_y_scale = new_needle_height
            new_peak_y_posn = (init_peak_label_y_posn * fig_height_base) / new_height
            peak_label_y_position = new_peak_y_posn
            
            print("needle height goal:", new_needle_height, "\n \t inches:", new_needle_height*new_height)
            print("current needle height (in):", current_needle_height_in)
            print("height:", new_height, "max label y:", max_label_y)
            print("\npeak label y pos'n goal:", new_peak_y_posn, "\nnew fig height:", new_fig_height)      
        else:
            print("Labels fit — no expansion needed")
            max_needle_y_scale = max_needle_y
            print("peak label y pos'n:", peak_label_y_position)
    else:
        max_needle_y_scale = max_needle_y
        print("No labels on this spectrum")
    print(f"DEBUG: max_label_y = {max(label_ys) if label_ys else 'N/A'}")

    try:
        label_ys = utils.compute_label_positions(
            peak_nms,
            intensities=peak_ints,
            base_y=peak_label_y_position,   # now uses updated value
            min_sep_nm=1.5,
            y_step=0.08,
            method="prefer_stronger_top",
            max_y=0.85,
        )
    except Exception:
        label_ys = [peak_label_y_position] * len(peaks)
    print("\n new peak label pos'n:", peak_label_y_position)

    # Render every transition as a faint needle (increase visibility for verification)
    _bg_y_top = max_needle_y_scale  # use full height for visibility
    _bg_y = np.linspace(0, _bg_y_top, 40)
    for _idx, _row in df_plot_data.iterrows():
        _nm = float(_row[nm_col])
        _ni = float(_row.get('Norm_Int', 0.0))
        _base_rgb = utils.wavelength_to_rgb(_nm)
        _final_scale = new_utils.final_scale(min_brightness, _ni)
        _color = (_base_rgb[0] * _final_scale, _base_rgb[1] * _final_scale, _base_rgb[2] * _final_scale)
        _width_mult = float(_row.get('_width_mult', 1.0))
        _bg_base_width = min_needle_max_width_nm * 1.0 * _width_mult   # make background lines thicker for test
        _bg_widths = _bg_base_width * np.ones_like(_bg_y)
        _x_left = new_utils.left_x(_nm, _bg_widths)
        _x_right = new_utils.right_x(_nm, _bg_widths)
        ax.fill_betweenx(_bg_y, _x_left, _x_right, facecolor=_color, alpha=glow_alpha, edgecolor='none', linewidth=0, zorder=0)

    # Plot sharp distinct lines for each identified peak using fill_betweenx for needle shape
    for j, peak_index in enumerate(peaks):
        peak_nm = df_plot_data.iloc[peak_index][nm_col]
        peak_norm_int = df_plot_data.iloc[peak_index]['Norm_Int']
        base_rgb = utils.wavelength_to_rgb(peak_nm)

        # Emphasize peaks: gentle gamma + emphasis multiplier for labeled peaks
        _peak_gamma = 0.8
        if has_any_nist or new_utils.generic_type == 'raw':
            _peak_emphasis = utils.DEFAULT_PEAK_EMPHASIS
            min_brightness = utils.DEFAULT_MIN_BRIGHT
        elif new_utils.generic_type == 'normalised':
            _peak_emphasis = utils.NORM_PEAK_EMPHASIS
            min_brightness = utils.NORM_MIN_BRIGHT
        pre_int_scale = min_brightness + (1 - min_brightness) * (peak_norm_int ** _peak_gamma)
        final_int_scale = min(1.0, pre_int_scale * _peak_emphasis)
        color_rgb = new_utils.colored_rgb(base_rgb, final_int_scale)

        # Scale the maximum width of the needle based on normalized intensity
        base_width = min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * peak_norm_int
        width_mult = df_plot_data.iloc[peak_index].get('_width_mult', 1.0)

        # boost peak widths so labeled peaks stand out
        _peak_width_boost = 1.6
        scaled_max_width_nm = base_width * width_mult * _peak_width_boost
        
        # Calculate the actual height the needle should reach (fraction of 0-1)
        current_peak_render_height = max_needle_y_scale

        # Define y-coordinates for the needle shape, spanning from 0 to current_peak_render_height
        y_coords_render = np.linspace(0, current_peak_render_height, 120)
        # Calculate normalized y-coordinates for the width profile
        y_coords_normalized_for_width = (y_coords_render / current_peak_render_height if current_peak_render_height > 0 else np.zeros_like(y_coords_render))

        # Use a power-law profile for the width, making tips slimmer
        width_profile_factor = (4 * y_coords_normalized_for_width * (1 - y_coords_normalized_for_width)) ** needle_shape_power

        # --- Plot the GLOW effect first ---
        glow_current_widths_nm = scaled_max_width_nm * glow_width_multiplier * width_profile_factor
        glow_x_left = new_utils.left_x(peak_nm, glow_current_widths_nm)
        glow_x_right = new_utils.right_x(peak_nm, glow_current_widths_nm)
        ax.fill_betweenx(
            y_coords_render,
            glow_x_left,
            glow_x_right,
            facecolor=color_rgb,
            alpha=glow_alpha,
            edgecolor='none',
            linewidth=0,
            antialiased=True,
            zorder=1,
        )

        # --- Plot the main NEEDLE on top of the glow ---
        current_widths_nm = new_utils.dynamic_prominence(scaled_max_width_nm, width_profile_factor)
        x_left = new_utils.left_x(peak_nm, current_widths_nm)
        x_right = new_utils.right_x(peak_nm, current_widths_nm)
        ax.fill_betweenx(
            y_coords_render,
            x_left,
            x_right,
            facecolor=color_rgb,
            edgecolor='none',
            linewidth=0,
            antialiased=True,
            zorder=2,
        )

        # Add text label for the peak wavelength with rotation and stroke for readability
        if show_peak_labels and peak_norm_int >= label_min_norm_int:
            y_for_label = label_ys[j] if j < len(label_ys) else peak_label_y_position
            ax.text(
                peak_nm,
                y_for_label,
                f"{peak_nm:.2f}",
                color="white",
                ha="left",
                va="bottom",
                fontsize=8,
                rotation=60,
                rotation_mode="anchor",
                zorder=3,
                path_effects=[pe.withStroke(linewidth=1.5, foreground="black")],
            )

    if has_any_nist or new_utils.generic_type == 'raw':
        pad = 15
    else:
        pad = 10
    plt.tight_layout(rect=[0, 0, 1, 0.92])

    if new_utils.generic_type is not None:
        plt.title(f'{new_utils.generic_type.capitalize()} Emission Spectrum Visualization ({new_utils.mode.capitalize()} Mode)', color=new_utils.colour, y=0.98, pad=pad)
    else:
        plt.title(f'Emission Spectrum Visualization ({new_utils.mode.capitalize()} Mode)', color=new_utils.colour, y=0.98, pad=pad)
    plt.subplots_adjust(top=subplots_adjust_top)

    print("\nDEBUG: fig height = ", fig.get_figheight(), "\n current needle height = ", current_peak_render_height)
    return fig, ax


# =========================
# Other Plot Functions
# =========================

def gaussian_iteration(df_plot_data, peak_wavelengths=None,):
    
    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = df_plot_data,)
    if should_exit_early:
        fig, ax = plt.subplots(figsize=helper_utils.fig_size, dpi=utils.DPI)
        ax.set_axis_off()
        print("Ending Rendering Early.")
        return fig

    if peak_wavelengths is not None:
        nm_vals = df_plot_data[helper_utils.wl_col].values
        peaks_indices = []
        for pw in peak_wavelengths:
            try:
                pv = float(pw)
            except Exception:
                continue
            idx = int(np.argmin(np.abs(nm_vals - pv)))
            peaks_indices.append(idx)
        peaks_indices = sorted(set(peaks_indices))
    elif has_any_nist:
        peaks_indices = peaks_indices, properties = find_peaks(df_plot_data['_adj_int'], prominence=utils.DEFAULT_PROM_PERC)
    else:
        dyn_prominence = new_utils.dynamic_prominence(helper_utils.prominence, prep_utils.int_range)
        peaks_indices, properties = find_peaks(df_plot_data[helper_utils.INT_col], prominence=dyn_prominence)

    int_vals = df_plot_data['_raw_int'].values
    y_max = int_vals.max()
    rounded_y_max = new_utils.round_to_multiple(y_max, 50)        # this is what y_max should be

    # Create a new, denser wavelength array for plotting the synthetic spectrum
    x_synthetic = np.linspace(400, 750, 1000) # 1000 points for a smooth synthetic curve
    y_synthetic = np.zeros_like(x_synthetic) 

    for i, peak_idx in enumerate(peaks_indices):
        peak_nm = float(df_plot_data.iloc[peak_idx][helper_utils.wl_col])
        peak_amplitude = float(df_plot_data.iloc[peak_idx]['_adj_int'])
        normalized_amplitude = float(df_plot_data.iloc[peak_idx]['Norm_Int'])

        # Scale sigma based on normalized intensity (higher intensity = broader peak)
        sigma = helper_utils.base_sigma_nm + (helper_utils.max_sigma_multiplier - 1) * helper_utils.base_sigma_nm * normalized_amplitude

        # Create a Gaussian curve for this peak
        gaussian_curve = peak_amplitude * np.exp(-((x_synthetic - peak_nm)**2) / (2 * sigma**2))
        y_synthetic += gaussian_curve

    # Normalize the synthetic spectrum intensities for coloring (if desired, not strictly necessary for area plot)
    min_y_synthetic = y_synthetic.min()
    max_y_synthetic = y_synthetic.max()
    if (max_y_synthetic - min_y_synthetic) == 0:
        normalized_y_synthetic = np.ones_like(y_synthetic)
    else:
        normalized_y_synthetic = (y_synthetic - min_y_synthetic) / (max_y_synthetic - min_y_synthetic)
    
    # Iterate through each segment of the synthetic spectrum to apply color and alpha
    for i in range(len(x_synthetic) - 1):
        wavelength_start = x_synthetic[i]
        wavelength_end = x_synthetic[i+1]
        base_rgb = helper_utils.rgb(wavelength_start, gamma=helper_utils.gamma_factor)
        if new_utils.mode == 'dark':
            ALPHA = 0.1
        if new_utils.mode == 'light':
            ALPHA = 0.8
        alpha = new_utils.final_scale(ALPHA, normalized_y_synthetic[i])
        plt.fill_between([wavelength_start, wavelength_end],
                        [0, 0],
                        [y_synthetic[i], y_synthetic[i+1]],
                        color=base_rgb,
                        alpha=alpha,
                        linewidth=0)

    plt.ylim (0, rounded_y_max)
            
    print('\n\ny lim = ', plt.ylim())
    print('\nMin y synthetic = ', min_y_synthetic, '\nmax y synthetic = ', max_y_synthetic, '\n y max (from int_vals) = ', y_max, "\nnorm'd y synth = ", normalized_y_synthetic[i])



def line_plot_iteration(data_df):
    for i in range(len(data_df) - 1):
        wavelength_start = float(data_df.iloc[i][helper_utils.wl_col])
        wavelength_end = float(data_df.iloc[i+1][helper_utils.wl_col])
        int_factor = float(data_df.iloc[i]['Norm_Int'])
        base_rgb = helper_utils.rgb(wavelength_start)
        if new_utils.SCALE_BY_INT == 'y' or new_utils.SCALE_BY_INT == 'yes':
            final_intensity_scale = new_utils.final_scale(helper_utils.min_bright, int_factor)     # this is what does the brightness intensity
        else:
            final_intensity_scale = 1.0
        color_rgb = new_utils.colored_rgb(base_rgb, final_intensity_scale)       # trying at 1.0, changed from final_intensity_scale. 
        plt.plot([wavelength_start, wavelength_end],
                [data_df.iloc[i][helper_utils.INT_col], data_df.iloc[i+1][helper_utils.INT_col]],
                color=color_rgb,
                linewidth=2)
        
def filled_plot(data_df):
    for i in range(len(data_df) - 1):
        wavelength_start = data_df.iloc[i][helper_utils.wl_col]
        wavelength_end = data_df.iloc[i+1][helper_utils.wl_col]
        base_rgb = helper_utils.rgb(wavelength_start)
        alpha_factor = data_df.iloc[i]['Norm_Int']  # this is what does the brightness intensity
        if new_utils.SCALE_BY_INT == 'y' or new_utils.SCALE_BY_INT == 'yes':
            alpha = new_utils.final_scale(helper_utils.min_alpha, alpha_factor)
        else:
            alpha = 1.0    # for NO dimming, alpha has to = 1.0. want this to be optional for filled plots.

        if helper_utils.plot_type == 'Smoothed':
            plt.fill_between([wavelength_start, wavelength_end],
                     [0, 0], # Base of the fill is y=0
                     [data_df.iloc[i]['Smoothed_int'], data_df.iloc[i+1]['Smoothed_int']], # Top of the fill
                     color=base_rgb,
                     alpha=alpha,        #smoothed only shows properly for dimmed alphas
                     linewidth=0) # No line for the fill edges
        else:
            plt.fill_between([wavelength_start, wavelength_end],
                        [0, 0], # Base of the fill is y=0
                        [data_df.iloc[i][helper_utils.INT_col], data_df.iloc[i+1][helper_utils.INT_col]], # Top of the fill
                        color=base_rgb,
                        alpha=alpha,        # alpha has to be rly low to see the top outline. might only be reasonable to do for dimmed plots.
                        linewidth=0) # No line for the fill edges
            
            # Plot the line on top for clarity, using the base color for the line itself
            plt.plot([wavelength_start, wavelength_end],
                    [data_df.iloc[i][helper_utils.INT_col], data_df.iloc[i+1][helper_utils.INT_col]],
                    color=base_rgb,
                    linewidth=2) # Thicker line for better visibility on top of fill        # this should only be for non-smoothed
            
def scatter_iteration(data_df):
    alpha_factor = data_df['Norm_Int']
    sizes = helper_utils.base_marker_size + (helper_utils.max_marker_size_factor * alpha_factor)
    if new_utils.SCALE_BY_INT == 'y' or new_utils.SCALE_BY_INT == 'yes':
        alphas = new_utils.final_scale(helper_utils.min_alpha_scatter, alpha_factor)       # this does the dimming
    else:
        alphas = 1.0
    rgba_colors = []
    for i in range(len(data_df)):
        wavelength = data_df.iloc[i][helper_utils.wl_col]
        r, g, b = helper_utils.rgb(wavelength)
        if new_utils.SCALE_BY_INT == 'y' or new_utils.SCALE_BY_INT == 'yes':
            a = alphas.iloc[i]
        else:
            a = alphas
        rgba_colors.append((r, g, b, a))
    plt.scatter(
        x=data_df[helper_utils.wl_col],
        y=data_df[helper_utils.INT_col],
        c=rgba_colors,
        s=sizes,
        edgecolors='none',
        label='Emission Data'
    )

def bar_iteration(data_df):
    bar_colors = []
    for index, row in data_df.iterrows():
        wavelength = row[helper_utils.wl_col]
        normalized_intensity = row['Norm_Int']
        if new_utils.mode == 'dark':
            BRIGHT = 0.1
        if new_utils.mode == 'light':
            BRIGHT = 0.7
        base_rgb = helper_utils.rgb(wavelength)
        if new_utils.SCALE_BY_INT == 'y' or new_utils.SCALE_BY_INT == 'yes':
            final_intensity_scale = new_utils.final_scale(BRIGHT, normalized_intensity)     # this does the dimming
        else:
            final_intensity_scale = 1.0
        color_rgb = new_utils.colored_rgb(base_rgb, final_intensity_scale)        # changed to 1.0 from final_intensity_scale. want this to be optional
        bar_colors.append(color_rgb)
    plt.bar(
        x=data_df[helper_utils.wl_col],
        height=data_df[helper_utils.INT_col],
        width=helper_utils.bar_width,
        color=bar_colors,
        edgecolor='none' # No edge color for bars
    )


=================
prep_utils.py
=================

import numpy as np
import pandas as pd
import utils
import nist_codes
import helper_utils


def run_nist_check(data_df, force_nist=None):
    helper_utils.res_col_names(data_df=data_df, nm_col=None, int_col=None,)
    df_data = data_df.copy()
    df_data[helper_utils.wl_col] = pd.to_numeric(df_data[helper_utils.wl_col], errors='coerce')
    has_any_nist, nist_diag = nist_codes.detect_nist_values(df_data[helper_utils.INT_col], force_nist=force_nist)
    return df_data, has_any_nist



def prep_with_nist(data_df, x_min = helper_utils.x_min, x_max = helper_utils.x_max, apply_descriptor_adjustments = False):
    global int_range

    df_plot_data, has_any_nist = run_nist_check(data_df=data_df)
    if has_any_nist:
        df_plot_data = nist_codes.prepare_nist_spectrum(df_plot_data, helper_utils.INT_col, apply_descriptor_adjustments)
        print('NIST Destriptors Detected. Preparing NIST Rendering.')
    else:
        df_plot_data = utils.prepare_generic_spectrum(df_plot_data, helper_utils.INT_col, apply_descriptor_adjustments)
        print('No NIST Destriptors Detected. Preparing Generic Rendering.')

    # parse NIST-style cells
    parsed_intensity = df_plot_data[helper_utils.INT_col].apply(nist_codes.parse_nist_intensity)
    df_plot_data['_raw_int'] = parsed_intensity.apply(lambda t: t[0])
    df_plot_data['_descriptor'] = parsed_intensity.apply(lambda t: t[1])

    # drop rows missing wavelength or numeric intensity
    df_plot_data = df_plot_data.dropna(subset=[helper_utils.wl_col, '_raw_int']).copy()
    df_plot_data = df_plot_data[(df_plot_data[helper_utils.wl_col] >= x_min) & (df_plot_data[helper_utils.wl_col] <= x_max)].copy()
    df_plot_data = df_plot_data.sort_values(by=helper_utils.wl_col).reset_index(drop=True)

    # returns empty flag for empty datasets
    if df_plot_data.empty:
        return None, True 

    # Normalize using adjusted intensity
    min_int_val = df_plot_data['_adj_int'].min()
    max_int_val = df_plot_data['_adj_int'].max()
    int_range = max_int_val - min_int_val
    
    if int_range == 0 or np.isnan(int_range):
        df_plot_data['Norm_Int'] = 1.0
    else:
        df_plot_data['Norm_Int'] = (df_plot_data['_adj_int'] - min_int_val) / int_range

    return df_plot_data, False, has_any_nist



def prep_other(data_df, x_min = helper_utils.x_min, x_max = helper_utils.x_max):
    global int_range
    global y_max

    helper_utils.res_col_names(data_df=data_df, nm_col=None, int_col=None,)
    df_filtered = data_df.copy()
    df_filtered = df_filtered[(df_filtered[helper_utils.wl_col] >= x_min) & (df_filtered[helper_utils.wl_col] <= x_max)].copy()
    df_filtered = df_filtered.sort_values(by=helper_utils.wl_col).reset_index(drop=True)

    if helper_utils.plot_type == 'Smoothed':
        df_filtered['Smoothed_int'] = df_filtered[helper_utils.INT_col].rolling(window=helper_utils.smoothing_window, center=True).mean().fillna(df_filtered[helper_utils.INT_col])
        min_int = df_filtered['Smoothed_int'].min()
        max_int = df_filtered['Smoothed_int'].max()
    else:
        min_int = df_filtered[helper_utils.INT_col].min()
        max_int = df_filtered[helper_utils.INT_col].max()

    int_range = max_int - min_int
    int_vals = df_filtered[helper_utils.INT_col]
    y_max = int_vals.max()
    print('(prep_other) ymax = ', y_max)

    if int_range == 0:
        df_filtered['Norm_Int'] = 1.0
    else:
        if helper_utils.plot_type == 'Smoothed':
            df_filtered['Norm_Int'] = (df_filtered['Smoothed_int'] - min_int) / int_range
        else:
            df_filtered['Norm_Int'] = (df_filtered[helper_utils.INT_col] - min_int) / int_range

    if df_filtered.empty:
        return None, True 

    return df_filtered, False