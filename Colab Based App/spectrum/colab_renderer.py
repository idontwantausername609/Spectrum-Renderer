import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.signal import find_peaks
import pandas as pd


def wavelength_to_rgb(wavelength, gamma=0.8):
    R = G = B = 0.0
    if 380 <= wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif 440 <= wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0 ** gamma
    elif 490 <= wavelength <= 510:
        R = 0.0
        G = 1.0 ** gamma
        B = ((-(wavelength - 510) / (510 - 490))) ** gamma
    elif 510 <= wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0 ** gamma
        B = 0.0
    elif 580 <= wavelength <= 645:
        R = 1.0 ** gamma
        G = ((-(wavelength - 645) / (645 - 580))) ** gamma
        B = 0.0
    elif 645 <= wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    return (max(0.0, min(1.0, R)), max(0.0, min(1.0, G)), max(0.0, min(1.0, B)))


def plot_emission_spectrum_colab_style(
    df,
    nm_col='nm',
    intensity_col='Grey Val',
    prominence_percentage=0.12,
    x_min=400,
    x_max=750,
    fig_size=(15, 2),
    min_brightness=0.1,
    min_needle_max_width_nm=0.2,
    max_needle_max_width_nm=0.8,
    needle_shape_power=4,
    glow_width_multiplier=1.5,
    glow_alpha=0.25,
    dpi=600,
    dark_mode=True,
    label_y=1.05,
    label_rotation=60,
    label_fontsize=8,
    title_y=1.10,
):
    """Render a Colab-style emission spectrum.

    This function is pure with respect to I/O: it returns the Matplotlib
    Figure object and a DataFrame of detected peaks. Saving is the
    caller's responsibility.
    """
    df2 = df[(df[nm_col] >= x_min) & (df[nm_col] <= x_max)].copy().sort_values(by=nm_col).reset_index(drop=True)
    minv = df2[intensity_col].min()
    maxv = df2[intensity_col].max()
    rng = maxv - minv
    if rng == 0 or np.isnan(rng):
        df2['Normalized_Intensity'] = 1.0
    else:
        df2['Normalized_Intensity'] = (df2[intensity_col] - minv) / rng

    dynamic_prominence = prominence_percentage * (rng if rng > 0 else 1.0)
    peaks, props = find_peaks(df2[intensity_col].values, prominence=dynamic_prominence)

    fig, ax = plt.subplots(figsize=fig_size)

    # spectrum box always black; page background depends on mode
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black' if dark_mode else 'white')

    axis_text_color = 'white'
    title_color = 'white' if dark_mode else 'black'
    stroke_col = 'black' if dark_mode else 'white'

    plt.subplots_adjust(top=0.82, bottom=0.12, left=0.03, right=0.97)
    ax.set_position([0.03, 0.12, 0.94, 0.70])

    ax.yaxis.set_visible(False)
    ax.set_xlabel('Wavelength (nm)', color=axis_text_color)
    major_locator = ticker.MultipleLocator(50)
    minor_locator = ticker.MultipleLocator(10)
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_minor_locator(minor_locator)
    ax.tick_params(axis='x', which='major', colors=axis_text_color, labelsize=10, pad=6)
    ax.tick_params(axis='x', which='minor', colors=axis_text_color, length=4, width=0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, 1)

    y_coords = np.linspace(0, 1, 60)
    label_fontsize = int(label_fontsize)

    for p_idx in peaks:
        peak_nm = float(df2.iloc[p_idx][nm_col])
        peak_norm = float(df2.iloc[p_idx]['Normalized_Intensity'])

        base_rgb = wavelength_to_rgb(peak_nm)
        final_scale = min_brightness + (1 - min_brightness) * peak_norm
        colored_rgb = (base_rgb[0] * final_scale, base_rgb[1] * final_scale, base_rgb[2] * final_scale)

        scaled_max_width_nm = min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * peak_norm
        width_profile = (4 * y_coords * (1 - y_coords)) ** needle_shape_power

        # glow
        glow_widths = scaled_max_width_nm * glow_width_multiplier * width_profile
        left = peak_nm - glow_widths / 2
        right = peak_nm + glow_widths / 2
        ax.fill_betweenx(y_coords, left, right, facecolor=colored_rgb, alpha=glow_alpha, linewidth=0)

        # core needle
        core_widths = scaled_max_width_nm * width_profile
        left2 = peak_nm - core_widths / 2
        right2 = peak_nm + core_widths / 2
        ax.fill_betweenx(y_coords, left2, right2, facecolor=colored_rgb, linewidth=0)

        # label with stroke
        label = f"{peak_nm:.2f}"
        txt = ax.text(peak_nm, label_y, label,
                      color=axis_text_color, ha='center', va='bottom',
                      fontsize=label_fontsize, rotation=label_rotation, rotation_mode='anchor',
                      clip_on=False)
        try:
            import matplotlib.patheffects as pe
            txt.set_path_effects([pe.Stroke(linewidth=2, foreground=stroke_col), pe.Normal()])
        except Exception:
            pass

    ax.set_title('Colab-style Emission Spectrum', color=title_color, y=title_y)

    peaks_df = df2.iloc[peaks].copy()
    peaks_df = peaks_df.rename(columns={nm_col: 'wl', intensity_col: 'intensity'})
    peaks_df['norm'] = peaks_df['Normalized_Intensity']

    return fig, peaks_df
