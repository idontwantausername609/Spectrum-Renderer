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

# updated to work with trad_spec().

def plot(
    df_plot_data,
    scale_mode,
    detect_columns,
    nm_col,
    has_any_nist,
    #mode,
    show_grid = False,
    scale_by_int = None,
    save_path = None,
    prominence_percentage=0,     
    fig_size=helper_utils.FIG_SIZE,
    min_brightness=0,
    peak_wavelengths=None,
    show_peak_labels=True,
    x_min=helper_utils.X_MIN,
    x_max=helper_utils.X_MAX,
    min_needle_max_width_nm=helper_utils.MIN_NEEDLE_WIDTH,
    max_needle_max_width_nm=helper_utils.MAX_NEEDLE_WIDTH,
    needle_shape_power=helper_utils.NEEDLE_POWER_SHAPE,
    glow_width_multiplier=helper_utils.GLOW_WIDTH_MULT,
    glow_alpha=0,
    dpi=helper_utils.DPI,
    peak_label_y_position=0,
    label_min_norm_int=helper_utils.LABEL_NORM_INT,
    subplots_adjust_top = 0.90,
    max_needle_y = helper_utils.MAX_Y_SCALE,
    fig_height_overflow_scale = helper_utils.fig_height_overflow_scale,
    fig_height_base = helper_utils.FIG_HEIGHT_BASE,
    #title=None,
    #random_title=None,
    #save_path = None,
):

    fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
    new_utils.trad_spec_labels(fig=fig, ax=ax, x_min=x_min, x_max=x_max,)

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
        peaks = nist_codes.identify_spectral_peaks(df_plot_data.reset_index(drop=True), prominence_percentage, peak_wavelengths=None)
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
    try:
        label_ys = helper_utils.compute_label_positions(
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
        label_ys = helper_utils.compute_label_positions(
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

    if has_any_nist or scale_mode == 'raw':     # scale_mode == 'raw':
        pad = 15
    else:
        pad = 10
    plt.tight_layout(rect=[0, 0, 1, 0.92])

    '''

    # should go in new_utils?

    # Title logic: custom > random fallback > skip
    if title and str(title).strip():
        plt.title(str(title).strip(), color=new_utils.colour, y=0.98, pad=pad)
    if random_title:
        plt.title(new_utils.generate_random_title(), color=new_utils.colour, y=0.98, pad=pad)
    # else: no title at all
    '''

    if scale_mode is not None:
        plt.title(f'{scale_mode.capitalize()} Emission Spectrum Visualization', color=helper_utils.COLOUR, y=0.98, pad=pad)
    else:
        plt.title('Emission Spectrum Visualization', color=helper_utils.COLOUR, y=0.98, pad=pad)
    plt.subplots_adjust(top=subplots_adjust_top)

    print("\nDEBUG: fig height = ", fig.get_figheight(), "\n current needle height = ", current_peak_render_height)


    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)


    '''
    # Save the plot if a save_path is provided
    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)
    '''

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
    else:
        dyn_prominence = new_utils.dynamic_prominence(helper_utils.DEFAULT_PROM_PERC, prep_utils.int_range)
        peaks_indices, _properties = find_peaks(df_plot_data[helper_utils.INT_col], prominence=dyn_prominence)

    int_vals = df_plot_data['_raw_int'].values
    y_max = int_vals.max()

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
        new_utils.peak_labels(data_df=df_plot_data, show_label_colour=show_label_colour, )

    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=helper_utils.DPI)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=helper_utils.DPI)
            
    print('\n\ny lim = ', plt.ylim())
    print('\nMin y synthetic = ', min_y_synthetic, '\nmax y synthetic = ', max_y_synthetic, '\n y max (from int_vals) = ', y_max, "\nnorm'd y synth = ", normalized_y_synthetic[i])



def line_plot_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int):
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour)

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
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour)

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
                    linewidth=2) # Thicker line for better visibility on top of fill        # this should only be for non-smoothed
            
def scatter_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int):
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour)

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
        new_utils.peak_labels(data_df=data_df,  show_label_colour=show_label_colour)

    for index, row in data_df.iterrows():
        wavelength = row[helper_utils.wl_col]
        normalized_intensity = row['Norm_Int']

        base_rgb = helper_utils.rgb(wavelength)
        if scale_by_int is True:
            final_intensity_scale = new_utils.final_scale(helper_utils.DEFAULT_MIN_BRIGHT, normalized_intensity)     # this does the dimming
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


def non_rgb_iteration(data_df, show_peak_labels, show_label_colour):
    plt.plot(data_df[helper_utils.wl_col], data_df[helper_utils.INT_col], marker=None)
    if show_peak_labels is True:
        new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour)
