import numpy as np
from scipy.signal import find_peaks
import nist_codes
import plotly.express as px
import plotly.graph_objects as go
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
    show_peak_labels,
    title,
    random_title,
    #graph_type ='traditional',
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
    fig_height_overflow_scale = 9.0 * 80,
    fig_height_base = helper_utils.FIG_HEIGHT_BASE * 80,
):

    if has_any_nist:
        max_needle_y = 0.80
    else:
        max_needle_y = max_needle_y

    if show_peak_labels is False:
        max_needle_y_scale = 1.0
    else:
        max_needle_y_scale = max_needle_y

    trad_fig = go.Figure()

    if has_any_nist:
        scale_mode = None
        min_brightness = helper_utils.DEFAULT_MIN_BRIGHT
        glow_alpha = helper_utils.DEFAULT_GLOW_ALPHA
        prominence_percentage = helper_utils.DEFAULT_PROM_PERC
        peak_label_y_position = max_needle_y + 0.01
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

    print(peak_wavelengths)
    
    peak_nms = [float(df_plot_data.iloc[index][helper_utils.wl_col]) for index in peaks]
    peak_ints = [float(df_plot_data.iloc[index]["Norm_Int"]) for index in peaks]
    init_peak_label_y_posn = peak_label_y_position

    if show_peak_labels is True:
        try:
            label_ys = helper_utils.compute_label_positions(
                peak_nms,
                intensities=peak_ints,
                base_y=init_peak_label_y_posn,
                min_sep_nm=0.5,
                y_step=0.06,
                method="prefer_stronger_top",
                max_y=0.98,
            )
        except Exception:
            label_ys = [init_peak_label_y_posn] * len(peaks)

        if label_ys:
            max_label_y = max(label_ys)
            overflow = max(0, max_label_y - init_peak_label_y_posn)
            
            print("\noverflow:", overflow, "\n fig height:", fig_height_base)
            print("o.g. peak label y pos'n:", init_peak_label_y_posn)
            if overflow > 0:
                new_height = fig_height_base + overflow * fig_height_overflow_scale
                new_fig_height = new_height
                current_needle_height_in = max_needle_y * new_height
                new_needle_height = (max_needle_y * fig_height_base) / new_height 
                max_needle_y_scale = new_needle_height
                new_peak_y_posn = (init_peak_label_y_posn * fig_height_base) / new_height
                peak_label_y_position = new_peak_y_posn

                print("\nog max needle y:", max_needle_y, "\nmax label y:", max_label_y, "\ninit peak label y:", init_peak_label_y_posn)
                print("needle height goal:", new_needle_height, "\n \t inches:", new_needle_height*new_height)
                print("current needle height (in):", current_needle_height_in)
                print("height:", new_height, "max label y:", max_label_y)
                print("\npeak label y pos'n goal:", new_peak_y_posn, "\nnew fig height:", new_fig_height,)

                trad_fig.update_layout(
                        new_utils.trad_spec_labels(has_any_nist=has_any_nist, scale_mode=scale_mode, fig_height=new_fig_height, show_peak_labels=show_peak_labels, title=title, random_title=random_title))

            else:
                print("Labels fit — no expansion needed")
                if scale_mode == 'normalize':
                    max_needle_y_scale = max_needle_y + 0.13
                elif scale_mode == 'raw' or has_any_nist:
                    max_needle_y_scale = max_needle_y + 0.1
                peak_label_y_position = peak_label_y_position + 0.08
                print("peak label y pos'n:", peak_label_y_position, "\nmax needle y scale:", max_needle_y_scale)
                trad_fig.update_layout(
                        new_utils.trad_spec_labels(has_any_nist=has_any_nist, scale_mode=scale_mode, fig_height=fig_height_base, title=title, random_title=random_title, show_peak_labels=show_peak_labels))
        else:
            max_needle_y_scale = max_needle_y
            print("No labels on this spectrum")
        print(f"DEBUG: max_label_y = {max(label_ys) if label_ys else 'N/A'}")

        try:
            label_ys = helper_utils.compute_label_positions(
                peak_nms,
                intensities=peak_ints,
                base_y=peak_label_y_position,   # now uses updated value
                min_sep_nm=0.9,
                y_step=0.07,
                method="prefer_stronger_top",
                max_y=0.98,
            )
        except Exception:
            label_ys = [peak_label_y_position] * len(peaks)
        print("\n new peak label pos'n:", peak_label_y_position)
    elif show_peak_labels is False:
        trad_fig.update_layout(new_utils.trad_spec_labels(has_any_nist=has_any_nist, scale_mode=scale_mode, fig_height=fig_height_base, title=title, random_title=random_title, show_peak_labels=show_peak_labels))

    _bg_y_top = max_needle_y_scale # use full height for visibility
    print("\n bg y top", _bg_y_top)
    _bg_y = np.linspace(0, _bg_y_top, 40)
    for _idx, _row in df_plot_data.iterrows():
        _nm = float(_row[nm_col])
        _ni = float(_row.get('Norm_Int', 0.0))
        _base_rgb = helper_utils.rgb(_nm)
        _final_scale = new_utils.final_scale(min_brightness, _ni)
        _color = new_utils.colored_rgb(_base_rgb, _final_scale)
        _width_mult = float(_row.get('_width_mult', 1.0))
        _colour = f"rgb({int(_color[0])}, {int(_color[1])}, {int(_color[2])})"
        _bg_base_width = min_needle_max_width_nm * 1.0 * _width_mult  
        _bg_widths = _bg_base_width * np.ones_like(_bg_y)
        _x_left = new_utils.left_x(_nm, _bg_widths)
        _x_right = new_utils.right_x(_nm, _bg_widths)

        loop_x = list(_x_left) + list(_x_right)[::-1]
        loop_y = list(_bg_y) + list(_bg_y)[::-1]

        trad_fig.add_trace(go.Scatter(
            x=loop_x,
            y=loop_y,
            fill='toself',
            fillcolor=_colour,
            opacity=glow_alpha,
            line=dict(width=0),      # Equivalent to edgecolor='none', linewidth=0
            mode='none',             # Hides individual markers/lines, showing only the fill
            showlegend=False,
            hoverinfo='skip'         # Keeps background elements from triggering tooltips
        ))

    # Plot sharp distinct lines for each identified peak using fill_betweenx for needle shape
    for j, peak_index in enumerate(peaks):
        peak_nm = df_plot_data.iloc[peak_index][nm_col]
        peak_norm_int = df_plot_data.iloc[peak_index]['Norm_Int']
        base_rgb = helper_utils.rgb(peak_nm)

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

        base_width = min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * peak_norm_int
        width_mult = df_plot_data.iloc[peak_index].get('_width_mult', 1.0)
        _peak_width_boost = 1.6
        scaled_max_width_nm = base_width * width_mult * _peak_width_boost
        current_peak_render_height = max_needle_y_scale

        y_coords_render = np.linspace(0, current_peak_render_height, 120)
        y_coords_normalized_for_width = (y_coords_render / current_peak_render_height if current_peak_render_height > 0 else np.zeros_like(y_coords_render))
        width_profile_factor = (4 * y_coords_normalized_for_width * (1 - y_coords_normalized_for_width)) ** needle_shape_power

        # --- Plot the GLOW effect first ---
        glow_current_widths_nm = scaled_max_width_nm * glow_width_multiplier * width_profile_factor
        glow_x_left = new_utils.left_x(peak_nm, glow_current_widths_nm)
        glow_x_right = new_utils.right_x(peak_nm, glow_current_widths_nm)
        loop_x = np.concatenate([glow_x_left, glow_x_right[::-1]])
        loop_y = np.concatenate([y_coords_render, y_coords_render[::-1]])

        color_str = f"rgb({color_rgb[0]},{color_rgb[1]},{color_rgb[2]})" 

        trad_fig.add_trace(go.Scatter(
            x=loop_x,
            y=loop_y,
            fill='toself',
            fillcolor=color_str,
            opacity=glow_alpha,
            line=dict(width=0),
            mode='none',             # Hides the bounding lines completely
            showlegend=False,
            hoverinfo='skip'
        ))
            # --- Plot the main NEEDLE on top of the glow ---
        current_widths_nm = new_utils.dynamic_prominence(scaled_max_width_nm, width_profile_factor)
        x_left = new_utils.left_x(peak_nm, current_widths_nm)
        x_right = new_utils.right_x(peak_nm, current_widths_nm)
        loop_x = np.concatenate([x_left, x_right[::-1]])
        loop_y = np.concatenate([y_coords_render, y_coords_render[::-1]])

        trad_fig.add_trace(go.Scatter(
            x=loop_x,
            y=loop_y,
            fill='toself',
            fillcolor=color_str,
            line=dict(width=0),    
            mode='none',             # Smooth fill with no outline paths
            showlegend=False,
            hoverinfo='skip'
        ))

        # Add text label for the peak wavelength with rotation and stroke for readability
        if show_peak_labels and peak_norm_int >= label_min_norm_int:
            y_for_label = label_ys[j] if j < len(label_ys) else peak_label_y_position
            
            trad_fig.add_annotation(
                x=peak_nm,
                y=y_for_label,
                text=f"{peak_nm:.2f}",
                font=dict(color=helper_utils.COLOUR, size=10.5),
                showarrow=False,
                textangle=-60,      # Plotly rotates clockwise; -60 equivalent to +60 counter-clockwise
                xanchor="center",     
                yanchor="middle",   
                xshift=5,
                yshift=25,
                captureevents=False 
            )

    return trad_fig


# =========================
# Other Plot Functions
# =========================

def gaussian_iteration(
        df_plot_data, 
        title, 
        random_title,
        show_peak_labels,
        show_label_colour,
        detect_columns,
        nm_col,
        show_grid,
        int_col,
        reverse_x,
        save_path=None,
        scale_by_int=False,
        scale_mode = None, 
        peak_wavelengths=None,
):
    gauss_fig=go.Figure()

    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = df_plot_data, detect_columns=detect_columns, nm_col=nm_col, int_col=int_col,)
    #if should_exit_early:





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
        y_synthetic += gaussian_curve # Add to the total synthetic spectrum

    # Normalize the synthetic spectrum intensities for coloring
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
        y_val_start = y_synthetic[i]
        y_val_end = y_synthetic[i+1]

        base_rgb_tuple = helper_utils.rgb(wavelength_start)
        segment_alpha = new_utils.final_scale(helper_utils.min_alpha, normalized_y_synthetic[i])

        r, g, b = int(base_rgb_tuple[0]), int(base_rgb_tuple[1]), int(base_rgb_tuple[2])
        fill_color_str = f"rgba({r}, {g}, {b}, {segment_alpha})"

        gauss_fig.add_trace(go.Scatter(
            x=[wavelength_start, wavelength_end],
            y=[y_val_start, y_val_end],
            mode='lines',
            line=dict(color=fill_color_str, width=0), # Set width to 0 to remove segment outlines
            fill='tozeroy',
            fillcolor=fill_color_str,
            showlegend=False,
            hovertemplate=new_utils.hover_config(data_df=df_plot_data),        
        ))

    if show_peak_labels is True:
        gauss_fig.update_layout(annotations = new_utils.peak_labels(data_df=df_plot_data, show_label_colour=show_label_colour, has_any_nist=has_any_nist))
        
    gauss_fig.update_layout(new_utils.axis_labels(graph_type='gaussian', show_peak_labels=show_peak_labels, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title))
    print('\nMin y synthetic = ', min_y_synthetic, '\nmax y synthetic = ', max_y_synthetic, '\n y max (from int_vals) = ', y_max, "\nnorm'd y synth = ", normalized_y_synthetic[i])
    return gauss_fig
  



def line_plot_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int, reverse_x, title, random_title, show_grid):
    line_fig = go.Figure()

    for i in range(len(data_df) - 1):
        wavelength_start = float(data_df.iloc[i][helper_utils.wl_col])
        wavelength_end = float(data_df.iloc[i+1][helper_utils.wl_col])
        int_factor = float(data_df.iloc[i]['Norm_Int'])
        base_rgb_val = helper_utils.rgb(wavelength_start)

        if scale_by_int is True:
            final_intensity_scale = new_utils.final_scale(helper_utils.DEFAULT_MIN_BRIGHT, int_factor)
        else:
            final_intensity_scale = 1.0

        color_rgb_float = new_utils.colored_rgb(base_rgb_val, final_intensity_scale)
        color_str = f"rgb({int(color_rgb_float[0])}, {int(color_rgb_float[1])}, {int(color_rgb_float[2])})"

        line_fig.add_trace(go.Scatter(
            x=[wavelength_start, wavelength_end],
            y=[data_df.iloc[i][helper_utils.INT_col], data_df.iloc[i+1][helper_utils.INT_col]],
            mode='lines',
            line=dict(color=color_str, width=2),
            showlegend=False,
            hovertemplate=new_utils.hover_config(data_df=data_df),
        ))

    if show_peak_labels is True:
        line_fig.update_layout(annotations = new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False))    

    line_fig.update_layout(new_utils.axis_labels(graph_type='line', show_peak_labels=show_peak_labels, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title))
    return line_fig

    
        
def filled_plot(data_df, show_peak_labels, show_label_colour, scale_by_int, reverse_x, title, random_title, show_grid):
    filled_fig=go.Figure()

    for i in range(len(data_df) - 1):
        wavelength_start = data_df.iloc[i][helper_utils.wl_col]
        wavelength_end = data_df.iloc[i+1][helper_utils.wl_col]
        y_val_start = data_df.iloc[i][helper_utils.INT_col]
        y_val_end = data_df.iloc[i+1][helper_utils.INT_col]

        base_rgb_tuple = helper_utils.rgb(wavelength_start) 

        alpha_factor = data_df.iloc[i]['Norm_Int']
        if scale_by_int is True:
            alpha = new_utils.final_scale(helper_utils.min_alpha, alpha_factor)
        else:
            alpha = 1.0

        r, g, b = int(base_rgb_tuple[0]), int(base_rgb_tuple[1]), int(base_rgb_tuple[2])
        fill_color_str = f"rgba({r}, {g}, {b}, {alpha})"

        line_color_str = f"rgb({r}, {g}, {b})"

        filled_fig.add_trace(go.Scatter(
            x=[wavelength_start, wavelength_end],
            y=[y_val_start, y_val_end],
            mode='lines',
            line=dict(color=line_color_str, width=2), # linewidth=2 from line_plot_iteration
            fill='tozeroy', # Fill area below the line to y=0
            fillcolor=fill_color_str,
            showlegend=False,
            hovertemplate=new_utils.hover_config(data_df=data_df),
        ))

    if show_peak_labels is True:
        filled_fig.update_layout(annotations = new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False))

    filled_fig.update_layout(new_utils.axis_labels(graph_type='filled line', show_peak_labels=show_peak_labels, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title))
    return filled_fig

            
def scatter_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int, reverse_x, title, random_title, show_grid):
    scatter_fig=go.Figure()
    alpha_factor = data_df['Norm_Int']
    sizes = helper_utils.base_marker_size + (helper_utils.max_marker_size_factor * alpha_factor)

    if scale_by_int is True:
        alphas = new_utils.final_scale(helper_utils.min_alpha_scatter, alpha_factor)
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
        rgba_colors.append(f"rgba({int(r)}, {int(g)}, {int(b)}, {a})")

    scatter_fig.add_trace(go.Scatter(
        x=data_df[helper_utils.wl_col],
        y=data_df[helper_utils.INT_col],
        mode='markers',
        marker=dict(
            color=rgba_colors,
            size=sizes,
            line=dict(width=0)
        ),
        showlegend=False,
        hovertemplate=new_utils.hover_config(data_df=data_df),
    ))    

    if show_peak_labels is True:
        scatter_fig.update_layout(annotations = new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False))
    scatter_fig.update_layout(new_utils.axis_labels(graph_type='scatter', show_peak_labels=show_peak_labels, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title))
    return scatter_fig


def bar_iteration(data_df, show_peak_labels, show_label_colour, scale_by_int, reverse_x, title, random_title, show_grid):
    fig_bar = go.Figure()
    bar_colors = []
    for index, row in data_df.iterrows():
        wavelength = row[helper_utils.wl_col]
        normalized_intensity = row['Norm_Int']
        base_rgb=helper_utils.rgb(wavelength)

        if scale_by_int is True:
            final_intensity_scale=new_utils.final_scale(helper_utils.DEFAULT_MIN_BRIGHT, normalized_intensity)
        else:
            final_intensity_scale = 1.0

        color_rgb_float=new_utils.colored_rgb(base_rgb, final_intensity_scale)
        r, g, b = int(color_rgb_float[0]), int(color_rgb_float[1]), int(color_rgb_float[2])
        bar_colors.append(f"rgba({r}, {g}, {b}, {1.0})")

    fig_bar.add_trace(go.Bar(
        x=data_df[helper_utils.wl_col],
        y=data_df[helper_utils.INT_col],
        marker=dict(color=bar_colors), # Use marker dict for color
        marker_line_color=bar_colors,
        marker_line_width=0,
        showlegend=False,
        hovertemplate=new_utils.hover_config(data_df=data_df),
    ))

    if show_peak_labels is True:
        fig_bar.update_layout(annotations = new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False))

    fig_bar.update_layout(new_utils.axis_labels(graph_type='bar', show_peak_labels=show_peak_labels, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title))
    return fig_bar


def non_rgb_iteration(data_df, show_peak_labels, show_label_colour, reverse_x, title, random_title, show_grid):
    non_rgb_fig=go.Figure()
    non_rgb_fig = px.line(data_df, x=data_df[helper_utils.wl_col], y=data_df[helper_utils.INT_col], color_discrete_sequence=['#1f77b4']) # Matching Matplotlib's default blue
    if show_peak_labels is True:
        non_rgb_fig.update_layout(annotations = new_utils.peak_labels(data_df=data_df, show_label_colour=show_label_colour, has_any_nist=False))
    non_rgb_fig.update_layout(new_utils.axis_labels(graph_type='non rgb line', show_peak_labels=show_peak_labels, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title))
    return non_rgb_fig

