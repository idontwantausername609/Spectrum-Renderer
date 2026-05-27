# okay. take a look at the code in the attached file. this is code from google colab. this code gave me the rendered image that i want. i want to implement this code into what i currently have. i want the visual aesthetic of this image, while still keeping my code universally usable 


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.ticker as ticker # Import ticker

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
    needle_shape_power=4, # Reverted to 4 as a good compromise
    glow_width_multiplier=1.5, # New parameter for glow width
    glow_alpha=0.25, # New parameter for glow transparency, increased for more prominent core
    dpi=600 # Increased resolution for output
):
    """
    Generates a traditional emission spectrum visualization from spectral data.

    The plot features a black background with sharp, distinct vertical lines at
    identified emission wavelengths. The color of each line corresponds to its
    wavelength, and its brightness and thickness are controlled by the intensity value at that
    wavelength, with an added subtle glow effect.

    Args:
        data_df (pd.DataFrame): The input DataFrame containing spectral data.
        nm_col (str, optional): The name of the column containing wavelength data in nanometers.
                                Defaults to 'nm'.
        intensity_col (str, optional): The name of the column containing intensity data.
                                       Defaults to 'Grey Val'.
        prominence_percentage (float, optional): The prominence threshold as a percentage
                                                 of the overall intensity range for peak detection.
                                                 A higher percentage identifies stronger peaks.
                                                 Defaults to 0.12.
        x_min (int, optional): The minimum wavelength for the X-axis range. Defaults to 400.
        x_max (int, optional): The maximum wavelength for the X-axis range. Defaults to 750.
        fig_size (tuple, optional): A tuple (width, height) specifying the figure size.
                                    Defaults to (15, 2).
        min_brightness (float, optional): A value between 0 and 1 controlling the minimum
                                          brightness of emission lines. Ensures even low-intensity
                                          lines are somewhat visible. Defaults to 0.1.
        save_path (str, optional): The file path to save the plot. If None, the plot is not saved.
                                   Defaults to None.
        min_needle_max_width_nm (float, optional): The minimum maximum width (in nm) for the
                                                   needle-shaped lines (for lowest intensity peaks).
                                                   Defaults to 0.2.
        max_needle_max_width_nm (float, optional): The maximum maximum width (in nm) for the
                                                   needle-shaped lines (for highest intensity peaks).
                                                   Defaults to 0.8.
        needle_shape_power (float, optional): Controls the slimness of the peak tips. A higher
                                              value (e.g., 2) makes the tips slimmer. Defaults to 4.
        glow_width_multiplier (float, optional): Multiplier for the needle's maximum width to determine
                                                 the glow's maximum width. Defaults to 1.5.
        glow_alpha (float, optional): The alpha (transparency) value for the glow effect. Defaults to 0.25.
        dpi (int, optional): The resolution in dots per inch for the saved image. Defaults to 600.
    """

    # Function to convert wavelength (nm) to RGB color
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

    # Create the plot
    plt.figure(figsize=fig_size)
    ax = plt.gca() # Get current axes

    # Set background color to black
    ax.set_facecolor('black')
    plt.gcf().set_facecolor('black') # Set figure background color as well

    # Remove Y-axis completely as intensity is shown by brightness/color
    ax.yaxis.set_visible(False)

    # Set X-axis labels and color
    plt.xlabel('Wavelength (nm)', color='white') # Set x-label color to white

    # Set major and minor tick locators
    major_locator = ticker.MultipleLocator(50) # Major ticks every 50nm
    minor_locator = ticker.MultipleLocator(10) # Minor ticks every 10nm
    ax.xaxis.set_major_locator(major_locator)
    ax.xaxis.set_minor_locator(minor_locator)

    # Set tick parameters for both major and minor ticks
    ax.tick_params(axis='x', which='major', colors='white', labelsize=10)
    ax.tick_params(axis='x', which='minor', colors='white', length=4, width=0.5)

    # Set X-axis limits
    plt.xlim(x_min, x_max)

    # Set a fixed y-range for the vertical lines to appear as a bar
    plt.ylim(0, 1) # All lines will span this fixed y-range

    # Plot sharp distinct lines for each identified peak using fill_betweenx for needle shape
    for peak_index in peaks:
        peak_nm = df_plot_data.iloc[peak_index][nm_col]
        peak_normalized_intensity = df_plot_data.iloc[peak_index]['Normalized_Intensity']

        # Get base RGB color for the peak wavelength
        base_rgb = wavelength_to_rgb(peak_nm)

        # Scale the intensity factor for brightness
        final_intensity_scale = min_brightness + (1 - min_brightness) * peak_normalized_intensity

        colored_rgb = (base_rgb[0] * final_intensity_scale,
                       base_rgb[1] * final_intensity_scale,
                       base_rgb[2] * final_intensity_scale)

        # Scale the maximum width of the needle based on normalized intensity
        scaled_max_width_nm = min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * peak_normalized_intensity

        # Define y-coordinates for the needle shape (from 0 to 1, the full height of the bar)
        y_coords = np.linspace(0, 1, 50) # 50 points to create a smooth curve
        # Use a power-law profile for the width, making tips slimmer
        width_profile_factor = (4 * y_coords * (1 - y_coords))**needle_shape_power # Ranges from 0 to 1

        # --- Plot the GLOW effect first ---
        glow_current_widths_nm = scaled_max_width_nm * glow_width_multiplier * width_profile_factor
        glow_x_left = peak_nm - glow_current_widths_nm / 2
        glow_x_right = peak_nm + glow_current_widths_nm / 2
        ax.fill_betweenx(y_coords, glow_x_left, glow_x_right, facecolor=colored_rgb, alpha=glow_alpha)

        # --- Plot the main NEEDLE on top of the glow ---
        current_widths_nm = scaled_max_width_nm * width_profile_factor
        x_left = peak_nm - current_widths_nm / 2
        x_right = peak_nm + current_widths_nm / 2
        ax.fill_betweenx(y_coords, x_left, x_right, facecolor=colored_rgb)

        # Add text label for the peak wavelength with rotation
        ax.text(peak_nm, 1.05, f'{peak_nm:.2f}',
                color='white', ha='center', va='bottom', fontsize=8,
                rotation=60, rotation_mode='anchor')

    plt.title('Traditional Emission Spectrum Visualization', color='white', y=1.1, pad=20) # Raised title with y parameter

    # Save the plot if a save_path is provided
    if save_path:
        plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)
        print(f"Plot saved to {save_path}")
        # Print the hyperlink to the saved image
        print(f"[Download Image]({save_path})")

    plt.show()

    print("This visualization shows the emission spectrum as a horizontal bar with sharp, distinct vertical lines.")
    print("Each line's color is determined by its wavelength, and its brightness and thickness reflect the intensity at that point, against a black background.")

# --- Example Usage ---
# Assuming df_filtered is available in the current environment from previous steps.
# If not, ensure you have a DataFrame with 'nm' and 'Grey Val' columns.
# For demonstration, let's use df_filtered as an example:

# Call the function to generate the emission spectrum and save it
plot_emission_spectrum(df_filtered, save_path='/content/He.png', min_needle_max_width_nm=0.2, max_needle_max_width_nm=0.8, needle_shape_power=4, glow_width_multiplier=1.5, glow_alpha=0.25, dpi=600)