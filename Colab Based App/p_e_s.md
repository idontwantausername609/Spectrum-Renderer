```python

def plot_emission_spectrum(
    data_df,
    nm_col=None,
    intensity_col=None,
    prominence_percentage=0.12,
    x_min=400,
    x_max=750,
    fig_size=(15, 3),
    min_brightness=0.1,
    save_path=None,
    min_needle_max_width_nm=0.1,
    max_needle_max_width_nm=0.3,
    needle_shape_power=4,
    glow_width_multiplier=1.3,
    glow_alpha=0.35,
    dpi=600,
    mode='dark',
    show_grid=False,
    peak_label_y_position=0.77,
    max_needle_y_scale=0.75,
    peak_wavelengths=None,
    apply_descriptor_adjustments=False,
    show_peak_labels=True,
    label_min_normalized_intensity=0.20,
):
    # Resolve column names at runtime (accept many common aliases)
    if nm_col is None:
        nm_col = resolve_column(
            data_df,
            ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm"],
            "wavelength",
        )
    if intensity_col is None:
        intensity_col = resolve_column(
            data_df,
            [
                "Grey Val",
                "grey val",
                "gray val",
                "grayscale",
                "gray value",
                "intensity",
                "signal",
                "counts",
                "value",
                "int",
                "rel. int.",
                "grey",
            ],
            "intensity",
        )

    # Always parse NIST-style intensity cells first because descriptors are usually attached.
    df_plot_data = data_df.copy()
    df_plot_data[nm_col] = pd.to_numeric(df_plot_data[nm_col], errors='coerce')

    # parse NIST-style cells
    parsed_intensity = df_plot_data[intensity_col].apply(parse_nist_intensity)
    df_plot_data['_raw_intensity'] = parsed_intensity.apply(lambda t: t[0])
    df_plot_data['_descriptor'] = parsed_intensity.apply(lambda t: t[1])

    # quick boolean: any row looks NIST-like?
    nist_tokens = [t.lower() for t in getattr(nist_helper, "NIST_DESCRIPTORS", [])] if nist_helper else []
    has_any_nist = df_plot_data['_descriptor'].fillna('').astype(str).str.lower().apply(
        lambda s: any(tok in s for tok in nist_tokens)
    ).any()

    if has_any_nist:
        # compute per-row NIST effects (fills _intensity_mult, _width_mult, _include)
        def _effects_from_desc(desc):
            if not desc: return (1.0, 1.0, True)
            keys = getattr(nist_helper, "_DESCRIPTOR_KEYS_SORTED", None)
            tokens = [k for k in keys if k in desc] if keys else [t for t in re.split(r'[\s,]+', desc) if t]
            eff = nist_helper.compute_descriptor_effects(tokens)
            return (eff.get("intensity_multiplier",1.0), eff.get("width_multiplier",1.0), eff.get("include",True))

        effs = df_plot_data['_descriptor'].apply(lambda d: _effects_from_desc(d))
        df_plot_data['_intensity_mult'] = effs.apply(lambda x: x[0])
        df_plot_data['_width_mult']     = effs.apply(lambda x: x[1])
        df_plot_data['_include']       = effs.apply(lambda x: x[2])
        df_plot_data = df_plot_data[df_plot_data['_include']].copy()
    else:
        # generic defaults
        df_plot_data['_intensity_mult'] = 1.0
        df_plot_data['_width_mult']     = 1.0
        df_plot_data['_include']        = True

    # drop rows missing wavelength or numeric intensity
    df_plot_data = df_plot_data.dropna(subset=[nm_col, '_raw_intensity']).copy()
    df_plot_data = df_plot_data[(df_plot_data[nm_col] >= x_min) & (df_plot_data[nm_col] <= x_max)].copy()
    df_plot_data = df_plot_data.sort_values(by=nm_col).reset_index(drop=True)
    

    # Create adjusted intensity column used for normalization/detection
    if apply_descriptor_adjustments:
        df_plot_data['_adj_intensity'] = df_plot_data['_raw_intensity'] * df_plot_data['_intensity_mult']
    else:
        df_plot_data['_adj_intensity'] = df_plot_data['_raw_intensity']

    # Normalize using the adjusted intensity
    min_intensity_val = df_plot_data['_adj_intensity'].min()
    max_intensity_val = df_plot_data['_adj_intensity'].max()
    intensity_range = max_intensity_val - min_intensity_val
    if intensity_range == 0 or np.isnan(intensity_range):
        df_plot_data['Normalized_Intensity'] = 1.0
    else:
        df_plot_data['Normalized_Intensity'] = (df_plot_data['_adj_intensity'] - min_intensity_val) / intensity_range

    # Detection must always use raw numeric intensities; rendering uses adjusted values.
    detection_col = '_raw_intensity'
    intensity_col = '_adj_intensity'  # used for normalization/rendering
    
    # --- Peak Detection (raw data) ---
    if peak_wavelengths is not None:
        nm_vals = df_plot_data[nm_col].values
        peaks = []
        for pw in peak_wavelengths:
            try:
                pv = float(pw)
            except Exception:
                continue
            idx = int(np.argmin(np.abs(nm_vals - pv)))
            peaks.append(idx)
        peaks = sorted(set(peaks))
    else:
        raw_min = df_plot_data[detection_col].min()
        raw_max = df_plot_data[detection_col].max()
        raw_range = raw_max - raw_min
        dynamic_prominence = prominence_percentage * (raw_range if raw_range != 0 else 1.0)
        
        peaks = identify_spectral_peaks(
            df_plot_data.reset_index(drop=True),
            prominence_percentage=prominence_percentage,
            peak_wavelengths=peak_wavelengths,
        )

                # --- compute per-peak label Y positions to avoid overlap ---
        peak_nms = [float(df_plot_data.iloc[i][nm_col]) for i in peaks]
        peak_ints = [float(df_plot_data.iloc[i]['Normalized_Intensity']) for i in peaks]
        try:
            label_ys = compute_label_positions(
                peak_nms,
                intensities=peak_ints,
                base_y=peak_label_y_position,
                min_sep_nm=0.4,   # tune: nm distance considered "collision"
                y_step=0.08,     # tune: vertical step between stacked labels
                method="prefer_stronger_top",
                max_y=0.90,
            )
        except Exception:
            label_ys = [peak_label_y_position] * len(peaks)

    # Create the plot (use explicit Figure/Axis to avoid side-effects)
    fig, ax = plt.subplots(figsize=fig_size)

    # Set figure background and text colors based on mode
    if mode == 'dark':
        figure_bg_color = 'black'
        text_color = 'white'
        grid_color = 'darkgrey'
    else:  # light mode
        figure_bg_color = 'white'
        text_color = 'black'
        grid_color = 'lightgrey'

    fig.patch.set_facecolor(figure_bg_color)
    ax.set_facecolor('black')  # Always keep the spectrum plot area (axes) background black

    # Remove Y-axis completely as intensity is shown by brightness/color
    ax.yaxis.set_visible(False)

    # Set X-axis labels and color
    ax.set_xlabel('Wavelength (nm)', color=text_color)

    # Set major and minor tick locators
    major_locator = ticker.MultipleLocator(50)
    minor_locator = ticker.MultipleLocator(10)
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_minor_locator(minor_locator)

    # Set tick parameters for both major and minor ticks
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)

    # Set X-axis limits
    ax.set_xlim(x_min, x_max)

    # Set a fixed y-range for the vertical lines to appear as a bar
    ax.set_ylim(0, 1)
   
    # Render every transition as a faint needle (increase visibility for verification)
    _bg_y_top = max_needle_y_scale  # use full height for visibility
    _bg_y = np.linspace(0, _bg_y_top, 40)
    for _idx, _row in df_plot_data.iterrows():
        _nm = float(_row[nm_col])
        _ni = float(_row.get('Normalized_Intensity', 0.0))
        _base_rgb = wavelength_to_rgb(_nm)
        _final_scale = min_brightness + (1 - min_brightness) * _ni
        _color = (_base_rgb[0] * _final_scale, _base_rgb[1] * _final_scale, _base_rgb[2] * _final_scale)
        _width_mult = float(_row.get('_width_mult', 1.0))
        _bg_base_width = min_needle_max_width_nm * 1.0 * _width_mult   # make background lines thicker for test
        _bg_widths = _bg_base_width * np.ones_like(_bg_y)
        _x_left = _nm - _bg_widths / 2
        _x_right = _nm + _bg_widths / 2
        ax.fill_betweenx(_bg_y, _x_left, _x_right, facecolor=_color, alpha=0.28, edgecolor='none', linewidth=0, zorder=0)

    # Plot sharp distinct lines for each identified peak using fill_betweenx for needle shape
    for j, peak_index in enumerate(peaks):
        peak_nm = df_plot_data.iloc[peak_index][nm_col]
        peak_normalized_intensity = df_plot_data.iloc[peak_index]['Normalized_Intensity']

        # Get base RGB color for the peak wavelength
        base_rgb = wavelength_to_rgb(peak_nm)

        # Emphasize peaks: gentle gamma + emphasis multiplier for labeled peaks
        _peak_gamma = 0.8
        _peak_emphasis = 1.4
        final_intensity_scale = min_brightness + (1 - min_brightness) * (peak_normalized_intensity ** _peak_gamma)
        final_intensity_scale = min(1.0, final_intensity_scale * _peak_emphasis)

        colored_rgb = (
            base_rgb[0] * final_intensity_scale,
            base_rgb[1] * final_intensity_scale,
            base_rgb[2] * final_intensity_scale,
        )

        # Scale the maximum width of the needle based on normalized intensity

        base_width = min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * peak_normalized_intensity
        width_mult = df_plot_data.iloc[peak_index].get('_width_mult', 1.0)
        # boost peak widths so labeled peaks stand out
        _peak_width_boost = 1.6
        scaled_max_width_nm = base_width * width_mult * _peak_width_boost
        

        # Calculate the actual height the needle should reach (fraction of 0-1)
        current_peak_render_height = max_needle_y_scale

        # Define y-coordinates for the needle shape, spanning from 0 to current_peak_render_height
        y_coords_render = np.linspace(0, current_peak_render_height, 120)
        # Calculate normalized y-coordinates for the width profile
        y_coords_normalized_for_width = (
            y_coords_render / current_peak_render_height if current_peak_render_height > 0 else np.zeros_like(y_coords_render)
        )

        # Use a power-law profile for the width, making tips slimmer
        width_profile_factor = (4 * y_coords_normalized_for_width * (1 - y_coords_normalized_for_width)) ** needle_shape_power

        # --- Plot the GLOW effect first ---
        glow_current_widths_nm = scaled_max_width_nm * glow_width_multiplier * width_profile_factor
        glow_x_left = peak_nm - glow_current_widths_nm / 2
        glow_x_right = peak_nm + glow_current_widths_nm / 2
        ax.fill_betweenx(
            y_coords_render,
            glow_x_left,
            glow_x_right,
            facecolor=colored_rgb,
            alpha=glow_alpha,
            edgecolor='none',
            linewidth=0,
            antialiased=True,
            zorder=1,
        )

        # --- Plot the main NEEDLE on top of the glow ---
        current_widths_nm = scaled_max_width_nm * width_profile_factor
        x_left = peak_nm - current_widths_nm / 2
        x_right = peak_nm + current_widths_nm / 2
        ax.fill_betweenx(
            y_coords_render,
            x_left,
            x_right,
            facecolor=colored_rgb,
            edgecolor='none',
            linewidth=0,
            antialiased=True,
            zorder=2,
        )

        # Add text label for the peak wavelength with rotation and stroke for readability
        y_for_label = label_ys[j] if j < len(label_ys) else peak_label_y_position
        should_label = show_peak_labels and peak_normalized_intensity >= label_min_normalized_intensity
        if should_label:
            ax.text(
                peak_nm, 
                y_for_label, 
                f"{peak_nm:.2f}", 
                color="white", 
                ha="left", 
                va="bottom",
                fontsize=6, 
                rotation=60, 
                rotation_mode="anchor", 
                zorder=3,
                path_effects=[pe.withStroke(linewidth=1.5, foreground="black")])

    plt.title(f'Traditional Emission Spectrum Visualization ({mode.capitalize()} Mode)', color=text_color, y=1.0, pad=10)

    if show_grid:
        ax.grid(True, color=grid_color, linestyle=':', linewidth=0.5)

    # Save the plot if a save_path is provided
    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)

    # Return the Figure for callers to save/close as desired
    return fig