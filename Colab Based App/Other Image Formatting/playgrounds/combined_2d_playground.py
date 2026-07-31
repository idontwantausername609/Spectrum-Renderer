import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import new_utils

rgb = new_utils.rgb
HE_SHEET = "he test.xlsx"

df = pd.read_excel(HE_SHEET)
new_utils.res_col_names(data_df=df, nm_col=None, int_col=None)

# default df_filtered
df_filtered = df[(df[new_utils.wl_col] >= 400) & (df[new_utils.wl_col] <= 750)].copy()
df_filtered = df_filtered.sort_values(by=new_utils.wl_col).reset_index(drop=True)
print("DataFrame loaded successfully. Here are the first 5 rows:")
print(df.head())

# smoothed df_filtered
df_filtered['Smoothed_int'] = df_filtered[new_utils.INT_col].rolling(window=new_utils.smoothing_window, center=True).mean().fillna(df_filtered[new_utils.INT_col])

if new_utils.plot_type == 'Smoothed':
    min_int = df_filtered['Smoothed_int'].min
    max_int = df_filtered['Smoothed_int'].max
else:
    min_int = df_filtered[new_utils.INT_col].min()
    max_int = df_filtered[new_utils.INT_col].max()

int_range = max_int - min_int

if int_range == 0:
    df_filtered['Normalized_int'] = 1.0
else:
    if new_utils.plot_type == 'Smoothed':
        df_filtered['Normalized_int'] = (df_filtered['Smoothed_int'] - min_int) / int_range
    else:
        df_filtered['Normalized_int'] = (df_filtered[new_utils.INT_col] - min_int) / int_range


def line_plot_iteration():  
    
    for i in range(len(df_filtered) - 1):
        wavelength_start = df_filtered.iloc[i]['nm']
        wavelength_end = df_filtered.iloc[i+1]['nm']

        int_factor = df_filtered.iloc[i]['Normalized_int']
        base_rgb = new_utils.rgb(wavelength_start)
        final_intensity_scale = new_utils.final_scale(new_utils.min_bright, int_factor)
        
        color_rgb = new_utils.colored_rgb(base_rgb, final_intensity_scale)

        plt.plot([wavelength_start, wavelength_end],
                [df_filtered.iloc[i][new_utils.INT_col], df_filtered.iloc[i+1][new_utils.INT_col]],
                color=color_rgb,
                linewidth=2)
    

def filled_plot():
    
    for i in range(len(df_filtered) - 1):
        wavelength_start = df_filtered.iloc[i]['nm']
        wavelength_end = df_filtered.iloc[i+1]['nm']

        base_rgb = new_utils.rgb(wavelength_start)

        alpha_factor = df_filtered.iloc[i]['Normalized_int']
        alpha = new_utils.final_scale(new_utils.min_alpha, alpha_factor)

        if new_utils.plot_type == 'Smoothed':
            plt.fill_between([wavelength_start, wavelength_end],
                     [0, 0], # Base of the fill is y=0
                     [df_filtered.iloc[i]['Smoothed_int'], df_filtered.iloc[i+1]['Smoothed_int']], # Top of the fill
                     color=base_rgb,
                     alpha=alpha,
                     linewidth=0) # No line for the fill edges
        else:
            plt.fill_between([wavelength_start, wavelength_end],
                        [0, 0], # Base of the fill is y=0
                        [df_filtered.iloc[i][new_utils.INT_col], df_filtered.iloc[i+1][new_utils.INT_col]], # Top of the fill
                        color=base_rgb,
                        alpha=alpha,
                        linewidth=0) # No line for the fill edges

            # Plot the line on top for clarity, using the base color for the line itself
            plt.plot([wavelength_start, wavelength_end],
                    [df_filtered.iloc[i][new_utils.INT_col], df_filtered.iloc[i+1][new_utils.INT_col]],
                    color=base_rgb,
                    linewidth=2) # Thicker line for better visibility on top of fill
            

def gaussian_iteration():

    # Detect peaks
    dyn_prominence = new_utils.dynamic_prominence(new_utils.prominence, int_range)
    peaks_indices, properties = find_peaks(df_filtered[new_utils.INT_col], prominence=dyn_prominence)

    # Create a new, denser wavelength array for plotting the synthetic spectrum
    x_synthetic = np.linspace(400, 750, 1000) # 1000 points for a smooth synthetic curve
    y_synthetic = np.zeros_like(x_synthetic)

    for i, peak_idx in enumerate(peaks_indices):
        peak_nm = df_filtered.iloc[peak_idx]['nm']
        peak_amplitude = df_filtered.iloc[peak_idx][new_utils.INT_col]
        normalized_amplitude = df_filtered.iloc[peak_idx]['Normalized_int']

        # Scale sigma based on normalized intensity (higher intensity = broader peak)
        sigma = new_utils.base_sigma_nm + (new_utils.max_sigma_multiplier - 1) * new_utils.base_sigma_nm * normalized_amplitude

        # Create a Gaussian curve for this peak
        gaussian_curve = peak_amplitude * np.exp(-((x_synthetic - peak_nm)**2) / (2 * sigma**2))
        y_synthetic += gaussian_curve # Add to the total synthetic spectrum

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

        base_rgb = new_utils.rgb(wavelength_start, gamma=new_utils.gamma_factor)
        alpha = new_utils.final_scale(new_utils.min_alpha, normalized_y_synthetic[i])

        plt.fill_between([wavelength_start, wavelength_end],
                        [0, 0],
                        [y_synthetic[i], y_synthetic[i+1]],
                        color=base_rgb,
                        alpha=alpha,
                        linewidth=0)
        

def scatter_iteration():
    alpha_factor = df_filtered['Normalized_int']
    sizes = new_utils.base_marker_size + (new_utils.max_marker_size_factor * alpha_factor)
    alphas = new_utils.final_scale(new_utils.min_alpha_scatter, alpha_factor)

    rgba_colors = []
    for i in range(len(df_filtered)):
        wavelength = df_filtered.iloc[i]['nm']
        r, g, b = new_utils.rgb(wavelength)
        a = alphas.iloc[i]
        rgba_colors.append((r, g, b, a))

    plt.scatter(
        x=df_filtered['nm'],
        y=df_filtered[new_utils.INT_col],
        c=rgba_colors,
        s=sizes,
        edgecolors='none',
        label='Emission Data'
    )


def bar_iteration():
    bar_colors = []
    for index, row in df_filtered.iterrows():
        wavelength = row['nm']
        normalized_intensity = row['Normalized_int']

        if new_utils.mode == 'dark':
            BRIGHT = 0.1
        if new_utils.mode == 'light':
            BRIGHT = 0.7

        base_rgb = new_utils.rgb(wavelength)

        final_intensity_scale = new_utils.final_scale(BRIGHT, normalized_intensity)
        color_rgb = new_utils.colored_rgb(base_rgb, final_intensity_scale)
        bar_colors.append(color_rgb)

    plt.bar(
        x=df_filtered['nm'],
        height=df_filtered[new_utils.INT_col],
        width=new_utils.bar_width,
        color=bar_colors,
        edgecolor='none' # No edge color for bars
    )


def plot_graph():
    GRAPH_TYPE = input(print("Choose Graph Type: Line, Bar, Scatter, Gaussian")).lower()

    if GRAPH_TYPE == 'bar' or GRAPH_TYPE == 'b':
        bar_iteration()
        plt.title("Bar Chart", color = new_utils.colour)
    elif GRAPH_TYPE == 'scatter' or GRAPH_TYPE == 's':
        scatter_iteration()
        plt.title("Scatter Plot", color=new_utils.colour)
    elif GRAPH_TYPE == 'gaussian' or GRAPH_TYPE == 'g':
        gaussian_iteration()
        plt.title("Gaussian Plot", color = new_utils.colour)
    elif GRAPH_TYPE == 'line' or GRAPH_TYPE == 'l':
        FILL_TYPE = input(print("Filled Graph? Choose: Yes or No")).lower()
        if FILL_TYPE == 'yes' or FILL_TYPE == 'y':
            PLOT_TYPE = input(print("Smoothed Fill? Choose: Yes or No")).lower()
            if PLOT_TYPE == 'yes' or PLOT_TYPE == 'y':
                new_utils.plot_type == 'Smoothed'
                filled_plot()
                plt.title("Smoothed Plot", color = new_utils.colour)
            else:
                new_utils.plot_type is None
                filled_plot()
                plt.title("Filled Plot", color = new_utils.colour)
        else:
            line_plot_iteration()
            plt.title("Line Plot", color = new_utils.colour)


new_utils.axis_labels()
plot_graph()
plt.show() 