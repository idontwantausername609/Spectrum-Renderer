## This file contains all original matplotlib codes before plotly rewrite. 

# =================================================================================
# plot_funcs.py
# =================================================================================

import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
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

def plot_trad(
    df_plot_data,
    scale_mode,
    detect_columns,
    nm_col,
    has_any_nist,
    #mode,
    show_peak_labels,
    title,
    random_title,
    show_grid = False,
    scale_by_int = None,
    save_path = None,
    prominence_percentage=0,     
    fig_size=helper_utils.FIG_SIZE,
    min_brightness=0,
    peak_wavelengths=None,
    x_min=helper_utils.X_MIN,
    x_max=helper_utils.X_MAX,
    min_needle_max_width_nm=helper_utils.MIN_NEEDLE_WIDTH,
    max_needle_max_width_nm=helper_utils.MAX_NEEDLE_WIDTH,
    needle_shape_power=helper_utils.NEEDLE_POWER_SHAPE,
    glow_width_multiplier=helper_utils.GLOW_WIDTH_MULT,
    glow_alpha=0,
    max_needle_y_scale=0,
    dpi=helper_utils.DPI,
    peak_label_y_position=0,
    label_min_norm_int=helper_utils.LABEL_NORM_INT,
    subplots_adjust_top = 0.90,
    max_needle_y = helper_utils.MAX_Y_SCALE,
    fig_height_overflow_scale = helper_utils.fig_height_overflow_scale,
    fig_height_base = helper_utils.FIG_HEIGHT_BASE,
):

    if show_peak_labels is False:
        max_needle_y_scale = 0.98
    else:
        max_needle_y_scale = helper_utils.MAX_Y_SCALE

    fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
    new_utils.trad_spec_labels(fig=fig, ax=ax, x_min=x_min, x_max=x_max, title=title, random_title=random_title, has_any_nist=has_any_nist, scale_mode=scale_mode)

    if has_any_nist:
        scale_mode = None
        min_brightness = helper_utils.DEFAULT_MIN_BRIGHT
        glow_alpha = helper_utils.DEFAULT_GLOW_ALPHA
        prominence_percentage = helper_utils.DEFAULT_PROM_PERC
        peak_label_y_position = helper_utils.DEFAULT_PEAK_LABEL_POSN
    else:
        if scale_mode == 'raw':
            glow_alpha = helper_utils.DEFAULT_GLOW_ALPHA
            peak_label_y_position = helper_utils.DEFAULT_PEAK_LABEL_POSN
        elif scale_mode == 'normalize':
            glow_alpha = helper_utils.NORM_GLOW_ALPHA
            peak_label_y_position = helper_utils.NORM_PEAK_LABEL_POSN

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
        print ("DEBUG: has nist plot trad", has_any_nist)
        peaks = nist_codes.identify_spectral_peaks(df_plot_data.reset_index(drop=True), prominence_percentage, peak_wavelengths=peak_wavelengths)
    else:
        raw_min = df_plot_data[detection_col].min()
        raw_max = df_plot_data[detection_col].max()
        raw_range = raw_max - raw_min
        if scale_mode == 'raw':
            prominence_percentage = helper_utils.DEFAULT_PROM_PERC
        if scale_mode == 'normalize':
            prominence_percentage = helper_utils.NORM_PROM_PERC
        dynamic_prominence = prominence_percentage * (raw_range if raw_range != 0 else 1.0)
        peaks, _ = find_peaks(df_plot_data[helper_utils.INT_col], prominence=dynamic_prominence)
    
    peak_nms = [float(df_plot_data.iloc[index][helper_utils.wl_col]) for index in peaks]
    peak_ints = [float(df_plot_data.iloc[index]["Norm_Int"]) for index in peaks]
    init_peak_label_y_posn = peak_label_y_position

    if show_peak_labels is True:
        try:
            label_ys = helper_utils.compute_label_positions(
                peak_nms,
                intensities=peak_ints,
                base_y=init_peak_label_y_posn,
                min_sep_nm=0.6,
                y_step=0.04,
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
                print("\npeak label y pos'n goal:", new_peak_y_posn, "\nnew fig height:", new_fig_height,)      
            else:
                print("Labels fit — no expansion needed")
                max_needle_y_scale = max_needle_y
                print("peak label y pos'n:", peak_label_y_position)
        else:
            max_needle_y_scale = max_needle_y
            print("No labels on this spectrum")
        print(f"DEBUG: max_label_y = {max(label_ys) if label_ys else 'N/A'}")

        try:
            label_ys = helper_utils.compute_label_positions(
                peak_nms,
                intensities=peak_ints,
                base_y=peak_label_y_position,   # now uses updated value
                min_sep_nm=0.4,
                y_step=0.08,
                method="prefer_stronger_top",
                max_y=0.90,
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
        _base_rgb = helper_utils.rgb(_nm)
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
        base_rgb = helper_utils.rgb(peak_nm)

        # Emphasize peaks: gentle gamma + emphasis multiplier for labeled peaks
        _peak_gamma = 0.8
        if has_any_nist or scale_mode == 'raw':   
            _peak_emphasis = helper_utils.DEFAULT_PEAK_EMPHASIS
            min_brightness = helper_utils.DEFAULT_MIN_BRIGHT
        elif scale_mode == 'normalize':
            _peak_emphasis = helper_utils.NORM_PEAK_EMPHASIS
            min_brightness = helper_utils.NORM_MIN_BRIGHT
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

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    return fig, ax


# =========================
# Other Plot Functions
# =========================

def gaussian_iteration(
        df_plot_data, 
        show_peak_labels,
        show_label_colour,
        detect_columns,
        nm_col,
        int_col,
        #mode,
        save_path=None,
        scale_by_int=False,
        scale_mode = None, 
        peak_wavelengths=None,
):
    
    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = df_plot_data, detect_columns=detect_columns, nm_col=nm_col, int_col=int_col,)
    if should_exit_early:
        fig, ax = plt.subplots(figsize=helper_utils.fig_size, dpi=helper_utils.DPI)
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
        peaks_indices = peaks_indices, _properties = find_peaks(df_plot_data['_adj_int'], prominence=helper_utils.DEFAULT_PROM_PERC) 
        plt.figure(figsize=helper_utils.fig_size)
    else:
        dyn_prominence = new_utils.dynamic_prominence(helper_utils.DEFAULT_PROM_PERC, prep_utils.int_range)
        peaks_indices, _properties = find_peaks(df_plot_data[helper_utils.INT_col], prominence=dyn_prominence)

    int_vals = df_plot_data['_raw_int'].values
    y_max = int_vals.max()

    #print("\nDEBUG:", int_vals)

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
        alpha = new_utils.final_scale(helper_utils.min_alpha, normalized_y_synthetic[i])
        plt.fill_between([wavelength_start, wavelength_end],
                        [0, 0],
                        [y_synthetic[i], y_synthetic[i+1]],
                        color=base_rgb,
                        alpha=alpha,
                        linewidth=0)

    if show_peak_labels is True:
        new_utils.peak_labels(data_df=df_plot_data, show_label_colour=show_label_colour, has_any_nist=has_any_nist,)

    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=helper_utils.DPI)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=helper_utils.DPI)
            
    print('\n\ny lim = ', plt.ylim())
    print('\nMin y synthetic = ', min_y_synthetic, '\nmax y synthetic = ', max_y_synthetic, '\n y max (from int_vals) = ', y_max, "\nnorm'd y synth = ", normalized_y_synthetic[i])



def line_plot_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int):
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False)

    for i in range(len(data_df) - 1):
        wavelength_start = float(data_df.iloc[i][helper_utils.wl_col])
        wavelength_end = float(data_df.iloc[i+1][helper_utils.wl_col])
        int_factor = float(data_df.iloc[i]['Norm_Int'])
        base_rgb = helper_utils.rgb(wavelength_start)
        if scale_by_int is True:
            final_intensity_scale = new_utils.final_scale(helper_utils.DEFAULT_MIN_BRIGHT, int_factor)     # this is what does the brightness intensity
        else:
            final_intensity_scale = 1.0
        color_rgb = new_utils.colored_rgb(base_rgb, final_intensity_scale)       # trying at 1.0, changed from final_intensity_scale. 
        plt.plot([wavelength_start, wavelength_end],
                [data_df.iloc[i][helper_utils.INT_col], data_df.iloc[i+1][helper_utils.INT_col]],
                color=color_rgb,
                linewidth=2)
    
        
def filled_plot(data_df, show_peak_labels, show_label_colour, scale_by_int):
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False)

    for i in range(len(data_df) - 1):
        wavelength_start = data_df.iloc[i][helper_utils.wl_col]
        wavelength_end = data_df.iloc[i+1][helper_utils.wl_col]
        base_rgb = helper_utils.rgb(wavelength_start)
        alpha_factor = data_df.iloc[i]['Norm_Int']  # this is what does the brightness intensity
        if scale_by_int is True:
            alpha = new_utils.final_scale(helper_utils.min_alpha, alpha_factor)
        else:
            alpha = 1.0    # for NO dimming, alpha has to = 1.0. want this to be optional for filled plots.

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
                    linewidth=2) # Thicker line for better visibility on top of fill

            
def scatter_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int):
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False)

    alpha_factor = data_df['Norm_Int']
    sizes = helper_utils.base_marker_size + (helper_utils.max_marker_size_factor * alpha_factor)
    if scale_by_int is True:
        alphas = new_utils.final_scale(helper_utils.min_alpha_scatter, alpha_factor)       # this does the dimming
    else:
        alphas = 1.0
    rgba_colors = []
    for i in range(len(data_df)):
        wavelength = data_df.iloc[i][helper_utils.wl_col]
        r, g, b = helper_utils.rgb(wavelength)
        if scale_by_int is True:
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

def bar_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int):
    bar_colors = []
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False)

    for index, row in data_df.iterrows():
        wavelength = row[helper_utils.wl_col]
        normalized_intensity = row['Norm_Int']

        base_rgb = helper_utils.rgb(wavelength)
        if scale_by_int is True:
            final_intensity_scale = new_utils.final_scale(helper_utils.DEFAULT_MIN_BRIGHT, normalized_intensity)     # this does the dimming
        else:
            final_intensity_scale = 1.0
        color_rgb = new_utils.colored_rgb(base_rgb, final_intensity_scale)
        bar_colors.append(color_rgb)
    plt.bar(
        x=data_df[helper_utils.wl_col],
        height=data_df[helper_utils.INT_col],
        width=helper_utils.bar_width,
        color=bar_colors,
        edgecolor='none' # No edge color for bars
    )

def non_rgb_iteration(data_df, show_peak_labels, show_label_colour):
    plt.plot(data_df[helper_utils.wl_col], data_df[helper_utils.INT_col], marker=None)
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False)



# =================================================================================
# helper_utils.py
# =================================================================================
'''
this module has the predefined variables, compute_label_positions() (used ONLY for plot_trad()) the intensity column resolving, and the rgb conversion functions. 
'''

import re
import matplotlib.ticker as ticker

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
MAX_Y_SCALE = 0.75
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
#prominence = 0.08       # changed from 0.12
#min_bright = 0.1
min_alpha = 0.1
min_alpha_scatter = 0.2
base_marker_size = 5
max_marker_size_factor = 95
gamma_factor = 0.8
bar_width = 1
smoothing_window = 5    # Increase this value to control the degree of smoothing
base_sigma_nm = 0.5 # Base width of the Gaussian (for low intensity peaks)
max_sigma_multiplier = 4.0 # How much wider the highest intensity peaks can be
reverse_x = True
plot_type = None
show_grid = True


major_locator = ticker.MultipleLocator(50)
minor_locator = ticker.MultipleLocator(10)


lambda_tokens = ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm", "Observed", "Observed Wavelength", "obs", "wave", "w"]

int_tokens =["Grey Val", "grey val", "gray val", "grayscale", "gray value", "intensity", "signal", "counts", "value", "int", "rel. int.", "grey", "Rel. Int.", "Relative Intensity", "Rel Int", "Intensity", "A", "Aki", "gA", "gf", "weighted f", "f", "Intensity/Counts", 'rel', 'count', 'flux', 'grey value', 'i']


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
    raise KeyError("Could not find a", label, "column. Available columns:", (df.head()))


def res_col_names(data_df, detect_columns, nm_col, int_col):
    global wl_col
    global INT_col

    def normalize_selected_col(value):
        if value is None:
            return None

        text = str(value).strip()
        if text == "":
            return None

        if text.isdigit():
            index = int(text)
            if 0 <= index < len(data_df.columns):
                return data_df.columns[index]
            return None

        for col in data_df.columns:
            if str(col).strip() == text:
                return col

        for col in data_df.columns:
            if str(col).strip().lower() == text.lower():
                return col
        #return None

    if detect_columns is True:
        wl_col = normalize_selected_col(nm_col)
        INT_col = normalize_selected_col(int_col)
        if wl_col is None or INT_col is None:
            return data_df, None, None, True

        return data_df, wl_col, INT_col, False

    try:
        wl_col = resolve_column(data_df, lambda_tokens, "wavelength")
        INT_col = resolve_column(data_df, int_tokens, "intensity")
        return data_df, wl_col, INT_col, False
    except KeyError:
        return data_df, None, None, True


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


def compute_label_positions(peak_nms, intensities=None, base_y=None, min_sep_nm=0.5, y_step=0.04, method="prefer_stronger_top", max_y=0.98):
    if not peak_nms:
        return []

    # prepare indices sorted by wavelength
    idx_sorted = sorted(range(len(peak_nms)), key=lambda i: peak_nms[i])
    result = [base_y] * len(peak_nms)

    # build clusters of peaks closer than min_sep_nm
    clusters = []
    cur = [idx_sorted[0]]
    for i in idx_sorted[1:]:
        if abs(peak_nms[i] - peak_nms[cur[-1]]) <= min_sep_nm:
            cur.append(i)
        else:
            clusters.append(cur)
            cur = [i]
    clusters.append(cur)

    for cluster in clusters:
        if len(cluster) == 1:
            result[cluster[0]] = base_y
            continue

        if method == "prefer_stronger_top" and intensities is not None:
            cluster_sorted = sorted(cluster, key=lambda k: -float(intensities[k]))
            n = len(cluster_sorted)
            if n == 1:
                result[cluster_sorted[0]] = base_y
            else:
                step = min(y_step, (max_y - base_y) / (n - 1))
                for pos, idx in enumerate(cluster_sorted):
                    result[idx] = base_y + pos * step
    return result



# =================================================================================
# new_utils.py
# =================================================================================
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import math
import random
import string
import helper_utils
import prep_utils
import nist_codes

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

def peak_labels(data_df, show_label_colour, has_any_nist):
    if has_any_nist is False:
        peaks, _ = find_peaks(data_df[helper_utils.INT_col], prominence=dynamic_prominence(helper_utils.DEFAULT_PROM_PERC, prep_utils.int_range)) # Using dynamic prominence
        int_col = helper_utils.INT_col
    else:
        peaks, _ = find_peaks(data_df['_raw_int'], prominence=helper_utils.DEFAULT_PROM_PERC)
        int_col = ['_raw_int']
    
    # Label the identified sharp peaks
    for peak_index in peaks:
        row = data_df.iloc[peak_index]
        wl_labels = float(data_df.iloc[peak_index][helper_utils.wl_col])
        base_rgb = helper_utils.rgb(wl_labels)
        final_intensity_scale = 1.0
        color_rgb = colored_rgb(base_rgb, final_intensity_scale)
        
        if show_label_colour is True: #and mode == 'dark':
            plt.annotate(f"{row[helper_utils.wl_col]:.2f} nm", # Formatted nm to two decimal places
                        (row[helper_utils.wl_col], row[int_col]),
                        textcoords="offset points", # Offset the text
                        xytext=(0,10), # Distance from point to label
                        ha='center', # Horizontal alignment
                        color=color_rgb,        # this makes the text rgb
                        )
        else:
            plt.annotate(f"{row[helper_utils.wl_col]:.2f} nm", # Formatted nm to two decimal places
                        (row[helper_utils.wl_col], row[int_col]),
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


# =================================================================================
# renderer.py
# =================================================================================
import pandas as pd
import csv
import matplotlib.pyplot as plt
import new_utils
import prep_utils
import plot_funcs
import helper_utils
import io


def load_data(file_path):
    """Automatically loads CSV or Excel files into a pandas DataFrame."""
    if not isinstance(file_path, (bytes, bytearray)):
        raise TypeError("load_data expects raw bytes or a bytearray as input.")
    
    if file_path.startswith(b'PK\x03\x04'):
        excel_dict = pd.read_excel(
            io.BytesIO(file_path), 
            sheet_name=None, 
            engine='openpyxl'
        )
        combined_df = pd.concat(excel_dict.values(), ignore_index=True)
        return combined_df
    
    else:
        try:
            text_content = file_path.decode('utf-8-sig') 
            csv_stream = io.StringIO(text_content)
            dialect = csv.Sniffer().sniff(csv_stream.read(2048))
            csv_stream.seek(0)
            df = pd.read_csv(csv_stream, sep=dialect.delimiter)
            return df

        except Exception as e:
            raise ValueError("File content could not be parsed as an XLSX or CSV file.") from e


def trad_spec(
    data_df, 
    #mode,
    scale_mode,
    show_peak_labels,
    nm_col,
    int_col,
    detect_columns,
    title = None,
    random_title = None,
    show_grid = False,
    show_label_colour = None,
    scale_by_int = None,
    fig_size=helper_utils.FIG_SIZE, 
    dpi=helper_utils.DPI,
):
    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = data_df, nm_col=nm_col, int_col=int_col, detect_columns=detect_columns)
    if should_exit_early:
        fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
        ax.set_axis_off()
        print("Ending Rendering Early.")
        return fig
    fig, ax = plot_funcs.plot_trad(
        df_plot_data = df_plot_data, 
        nm_col = helper_utils.wl_col, 
        has_any_nist=has_any_nist,
        #mode=mode,
        scale_mode=scale_mode,
        show_peak_labels=show_peak_labels,
        detect_columns=detect_columns,
        title=title,
        random_title=random_title,
    )
    return fig

# ====================================================================================================================================

def get_rgb_type(graph_type):
    global rgb_type
    if graph_type != 'non rgb line':
        rgb_type = 'yes'
    else:
        rgb_type = 'no'


def axis_labels(
    graph_type,
    show_grid,
    show_peak_labels,
    title,
    random_title,
    reverse_x,
    save_path=None,
    dpi = helper_utils.DPI,
    fig_size = helper_utils.fig_size,
    x_min = helper_utils.X_MIN,
    x_max = helper_utils.X_MAX,
    x_title = helper_utils.X_TITLE,
    y_title = helper_utils.Y_TITLE,
    y_min = 0,
    y_max = 0,
    fig_bg = helper_utils.BG,
    text = helper_utils.COLOUR,
):
    
    plt.figure(figsize=fig_size)
    ax = plt.gca()

    plt.gcf().set_facecolor(fig_bg)
    for spine in ax.spines.values():        # new block. may have to take out or decrease linewidth. 
        spine.set_linewidth(0.3)
        spine.set_color('darkgrey')
    if show_grid is True:
        plt.grid(True, color='darkgrey', linewidth=0.25)   # took out 'linestyle = ':' '    may have to add back in. 
    elif show_grid is False:
        plt.grid(False)

    if reverse_x is True:
        plt.xlim(x_max, x_min)
    else:
        plt.xlim(x_min, x_max)

    y_max = new_utils.set_y_lim(graph_type=graph_type, show_peak_labels=show_peak_labels)

    if title:
        plt.title(str(title).strip(), color = text)
    if random_title:
        plt.title(str(new_utils.generate_random_title()), color=text)

    ax.set_facecolor(fig_bg)
    plt.xlabel(x_title, color=text)
    plt.ylabel(y_title, color=text)
    plt.xticks(color=text)
    plt.yticks(color=text)
    ax.yaxis.set_major_locator(helper_utils.major_locator)
    plt.ylim(y_min, y_max)

    if save_path:
        try:
            ax.savefig(save_path, facecolor=ax.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)

def plot(
    data_df,
    detect_columns,
    nm_col,
    int_col,
    reverse_x,
    force_nist = None,
    graph_type = None,
    scale_mode = 'auto',
    title = None,
    random_title = None,
    show_peak_labels = None,
    show_grid = True,
    show_label_colour = None,
    scale_by_int = None,
    save_path=None,
):
    df_data, has_any_nist, _, _, _ = prep_utils.run_nist_check(data_df=data_df, detect_columns=detect_columns, force_nist=force_nist, nm_col=nm_col, int_col=int_col)

    if has_any_nist is True:
        prep_type = 'nist'
        nist_plot_type = 'g' or 'gaussian' or 't' or 'traditional'
        if graph_type == 'gaussian':
            plot_funcs.gaussian_iteration(df_plot_data=df_data, detect_columns=detect_columns,show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, int_col=int_col, nm_col=nm_col)
            axis_labels(graph_type=graph_type, show_grid=show_grid, show_peak_labels=show_peak_labels, title=title, random_title=random_title, reverse_x=reverse_x)
        if graph_type == 'traditional':
            scale_mode = 'raw'
            trad_spec(data_df=data_df, detect_columns=detect_columns, scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title, nm_col=nm_col, int_col=int_col)

    else:
        prep_type = 'generic'
        if graph_type == 'traditional':
            trad_spec(data_df=data_df, detect_columns=detect_columns, scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title, nm_col=nm_col, int_col=int_col)

        else:
            data_df, should_exit_early = prep_utils.prep_other(data_df = data_df, detect_columns=detect_columns, int_col=int_col, nm_col=nm_col)
            if should_exit_early:
                fig, ax = plt.subplots(figsize=new_utils.fig_size, dpi=helper_utils.DPI)
                ax.set_axis_off()
                print("Ending Rendering Early.")
                return fig

            axis_labels(graph_type=graph_type, show_grid=show_grid, show_peak_labels=show_peak_labels, title=title, random_title=random_title, reverse_x=reverse_x)
            get_rgb_type(graph_type=graph_type)
            if rgb_type == 'yes':
                scale_by_int=scale_by_int

            if graph_type == 'bar':
                plot_funcs.bar_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'scatter':
                plot_funcs.scatter_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'gaussian':
                plot_funcs.gaussian_iteration(df_plot_data=df_data, detect_columns=detect_columns,show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, int_col=int_col, nm_col=nm_col, scale_by_int=False)
            elif graph_type == 'line':
                plot_funcs.line_plot_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'filled line':
                plot_funcs.filled_plot(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'non rgb line':
                plot_funcs.non_rgb_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour,)

