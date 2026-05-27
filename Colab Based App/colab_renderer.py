import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt


def wavelength_to_rgb(wavelength, gamma=0.8):
    """
    Converts a wavelength in nanometers to an RGB color tuple (0-1 range).
    Based on code by Dan Bruton (astro.sfasu.edu/sfop03/bruton.htm)
    """
    R, G, B = 0.0, 0.0, 0.0

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
    # Wavelengths outside 380-750 nm will be black (0,0,0) by default initialization

    # Ensure values are within 0-1 range
    return (max(0.0, min(1.0, R)), max(0.0, min(1.0, G)), max(0.0, min(1.0, B)))

def plot_emission_spectrum(
    data_df,
    nm_col='nm',
    intensity_col='Grey Val',
    prominence_percentage=0.12,
    x_min=400,
    x_max=750,
    fig_size=(15, 2),
    min_brightness=0.1,
    save_path=None,
    min_needle_max_width_nm=0.2,
    max_needle_max_width_nm=0.8,
    needle_shape_power=4,
    glow_width_multiplier=1.5,
    glow_alpha=0.25,
    dpi=600,
    mode='dark',
    show_grid=True,
    peak_label_y_position=0.9,
    max_needle_y_scale=0.8,
):

    # Filter the DataFrame for 'nm' values within the specified range
    df_plot_data = data_df[(data_df[nm_col] >= x_min) & (data_df[nm_col] <= x_max)].copy()
    df_plot_data = df_plot_data.sort_values(by=nm_col).reset_index(drop=True)

    # Normalize Intensity (Grey Val) for intensity scaling
    min_intensity_val = df_plot_data[intensity_col].min()
    max_intensity_val = df_plot_data[intensity_col].max()
    intensity_range = max_intensity_val - min_intensity_val

    if intensity_range == 0:
        df_plot_data['Normalized_Intensity'] = 1.0
    else:
        df_plot_data['Normalized_Intensity'] = (df_plot_data[intensity_col] - min_intensity_val) / intensity_range

    # --- Peak Detection ---
    dynamic_prominence = prominence_percentage * intensity_range
    peaks, _ = find_peaks(df_plot_data[intensity_col], prominence=dynamic_prominence)

    # Create the plot (use explicit Figure/Axis to avoid side-effects)
    fig, ax = plt.subplots(figsize=fig_size)
    ax = plt.gca() # Get current axes

    # Set figure background and text colors based on mode
    if mode == 'dark':
        figure_bg_color = 'black'
        text_color = 'white'
        grid_color = 'darkgrey'
    else:  # light mode
        figure_bg_color = 'white'
        text_color = 'black'
        grid_color = 'lightgrey'

    plt.gcf().set_facecolor(figure_bg_color) # Set figure background color
    ax.set_facecolor('black') # Always keep the spectrum plot area (axes) background black

    # Remove Y-axis completely as intensity is shown by brightness/color
    ax.yaxis.set_visible(False)

    # Set X-axis labels and color
    plt.xlabel('Wavelength (nm)', color=text_color)

    # Set major and minor tick locators
    major_locator = ticker.MultipleLocator(50)
    minor_locator = ticker.MultipleLocator(10)
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_minor_locator(minor_locator)

    # Set tick parameters for both major and minor ticks
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)

    # Set X-axis limits
    plt.xlim(x_min, x_max)

    # Set a fixed y-range for the vertical lines to appear as a bar
    plt.ylim(0, 1)

    # Plot sharp distinct lines for each identified peak using fill_betweenx for needle shape
    for peak_index in peaks:
        peak_nm = df_plot_data.iloc[peak_index][nm_col]
        peak_normalized_intensity = df_plot_data.iloc[peak_index]['Normalized_Intensity']

        # Get base RGB color for the peak wavelength
        base_rgb = wavelength_to_rgb(peak_nm)

        # Scale the intensity factor for brightness
        final_intensity_scale = min_brightness + (1 - min_brightness) * peak_normalized_intensity

        colored_rgb = (
            base_rgb[0] * final_intensity_scale,
            base_rgb[1] * final_intensity_scale,
            base_rgb[2] * final_intensity_scale,
        )

        # Scale the maximum width of the needle based on normalized intensity
        scaled_max_width_nm = (
            min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * peak_normalized_intensity
        )

        # Calculate the actual height the needle should reach. Now fixed by max_needle_y_scale.
        current_peak_render_height = max_needle_y_scale

        # Define y-coordinates for the needle shape, spanning from 0 to current_peak_render_height
        y_coords_render = np.linspace(0, current_peak_render_height, 50)
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
        ax.fill_betweenx(y_coords_render, glow_x_left, glow_x_right, facecolor=colored_rgb, alpha=glow_alpha)

        # --- Plot the main NEEDLE on top of the glow ---
        current_widths_nm = scaled_max_width_nm * width_profile_factor
        x_left = peak_nm - current_widths_nm / 2
        x_right = peak_nm + current_widths_nm / 2
        ax.fill_betweenx(y_coords_render, x_left, x_right, facecolor=colored_rgb)

        # Add text label for the peak wavelength with rotation, always white
        ax.text(peak_nm, peak_label_y_position, f'{peak_nm:.2f}',
                color='white', ha='center', va='bottom', fontsize=8,
                rotation=60, rotation_mode='anchor')
        
    plt.title(f'Traditional Emission Spectrum Visualization ({mode.capitalize()} Mode)', color=text_color, y=1.0, pad=10) # Raised title with y parameter
    if show_grid:
        plt.grid(True, color=grid_color, linestyle=':', linewidth=0.5) # Grid color based on mode

    # Save the plot if a save_path is provided
    if save_path:
        plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)
        print(f"Plot saved to {save_path}")
        print(f"[Download Image]({save_path})")

    plt.show()

    print(f"This {mode} mode visualization shows the emission spectrum as a horizontal bar with sharp, distinct vertical lines.\n")
    print("Each line's color is determined by its wavelength, and its brightness and thickness reflect the intensity at that point, and its height is uniformly set by the 'max_needle_y_scale' parameter, against a black background.")
    if mode == 'dark':
        print("The overall figure and text are optimized for a dark theme.")
    else:
        print("The overall figure and text are optimized for a light theme.")


def plot_emission_spectrum_colab_style(*args, save_path=None, headless=True, dpi=300, **kwargs):
    import matplotlib
    if headless:
        matplotlib.use('Agg')      # Switch to non-interactive backend for safe saving
    import matplotlib.pyplot as plt

    # Call your notebook function (keeps notebook behavior)
    fig = plot_emission_spectrum(*args, **kwargs)

    # If the notebook version already saved to save_path internally, this will overwrite harmlessly;
    # otherwise save the current figure.
    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)

    if headless:
        plt.close('all')

    return fig