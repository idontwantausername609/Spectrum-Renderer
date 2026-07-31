import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import utils
import nist_codes
import matplotlib.patheffects as pe
import new_utils

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
show_grid = True
plot_type = None



HE_SHEET = "he test.xlsx"
NIST_SHEET = "oxygen nist 2.xlsx"


HE_DF = pd.read_excel(HE_SHEET)
NIST_DF = pd.read_excel(NIST_SHEET)

global df  
df = NIST_DF

detection_col = '_raw_int'
int_col = '_adj_int'

def round_to_multiple(num, mult=50):
    rounded = mult * round(num / mult)
    return rounded


def prep_trad_spec(data_df, force_nist, x_min, x_max, apply_descriptor_adjustments,):

    # Always parse NIST-style intensity cells first because descriptors are usually attached.
    df_plot_data = data_df.copy()
    df_plot_data[new_utils.wl_col] = pd.to_numeric(df_plot_data[new_utils.wl_col], errors='coerce')

    # run NIST detector
    has_any_nist, nist_diag = nist_codes.detect_nist_values(df_plot_data[new_utils.INT_col], force_nist=force_nist)

    if has_any_nist:
        df_plot_data = nist_codes.prepare_nist_spectrum(df_plot_data, new_utils.INT_col, apply_descriptor_adjustments)
        print('NIST Destriptors Detected. Preparing NIST Rendering.')
    else:
        df_plot_data = utils.prepare_generic_spectrum(df_plot_data, new_utils.INT_col, apply_descriptor_adjustments)
        print('No NIST Destriptors Detected. Preparing Generic Rendering.')

    # parse NIST-style cells
    parsed_intensity = df_plot_data[new_utils.INT_col].apply(nist_codes.parse_nist_intensity)
    df_plot_data['_raw_int'] = parsed_intensity.apply(lambda t: t[0])
    df_plot_data['_descriptor'] = parsed_intensity.apply(lambda t: t[1])

    # drop rows missing wavelength or numeric intensity
    df_plot_data = df_plot_data.dropna(subset=[new_utils.wl_col, '_raw_int']).copy()
    df_plot_data = df_plot_data[(df_plot_data[new_utils.wl_col] >= x_min) & (df_plot_data[new_utils.wl_col] <= x_max)].copy()
    df_plot_data = df_plot_data.sort_values(by=new_utils.wl_col).reset_index(drop=True)

    # returns empty flag for empty datasets
    if df_plot_data.empty:
        return None, True 

    global int_range
    # Normalize using the adjusted intensity
    min_int_val = df_plot_data['_adj_int'].min()
    max_int_val = df_plot_data['_adj_int'].max()
    int_range = max_int_val - min_int_val
    
    if int_range == 0 or np.isnan(int_range):
        df_plot_data['Norm_Int'] = 1.0
    else:
        df_plot_data['Norm_Int'] = (df_plot_data['_adj_int'] - min_int_val) / int_range

    return df_plot_data, False, has_any_nist


def gaussian_iteration(
    df_plot_data,
    nm_col = None,
    int_col = None,
    x_min=utils.X_MIN,
    x_max=utils.X_MAX,
    force_nist=None,
    apply_descriptor_adjustments = False,
    peak_wavelengths=None,
):
    
    new_utils.res_col_names(df_plot_data, nm_col=nm_col, int_col=int_col)
    
    df_plot_data, should_exit_early, has_any_nist = prep_trad_spec(data_df = df_plot_data, force_nist = force_nist, x_min = x_min, x_max = x_max, apply_descriptor_adjustments=apply_descriptor_adjustments,)
    if should_exit_early:
        fig, ax = plt.subplots(figsize=new_utils.fig_size, dpi=600)
        ax.set_axis_off()
        print("Ending Rendering Early.")
        return fig


    if has_any_nist:
        df_plot_data = nist_codes.prepare_nist_spectrum(df_plot_data, new_utils.INT_col, apply_descriptor_adjustments)

    else:
        df_plot_data = utils.prepare_generic_spectrum(df_plot_data, new_utils.INT_col, apply_descriptor_adjustments)

    if peak_wavelengths is not None:
        nm_vals = df_plot_data[new_utils.wl_col].values
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
        dyn_prominence = new_utils.dynamic_prominence(new_utils.prominence, int_range)
        peaks_indices, properties = find_peaks(df_plot_data[new_utils.INT_col], prominence=dyn_prominence)

    int_vals = df_plot_data['_raw_int'].values
    y_max = int_vals.max()
    rounded_y_max = round_to_multiple(y_max)        # this is what y_max should be

    # Create a new, denser wavelength array for plotting the synthetic spectrum
    x_synthetic = np.linspace(400, 750, 1000) # 1000 points for a smooth synthetic curve
    y_synthetic = np.zeros_like(x_synthetic) 

    for i, peak_idx in enumerate(peaks_indices):
        peak_nm = float(df_plot_data.iloc[peak_idx][new_utils.wl_col])
        peak_amplitude = float(df_plot_data.iloc[peak_idx]['_adj_int'])
        normalized_amplitude = float(df_plot_data.iloc[peak_idx]['Norm_Int'])

        # Scale sigma based on normalized intensity (higher intensity = broader peak)
        sigma = new_utils.base_sigma_nm + (new_utils.max_sigma_multiplier - 1) * new_utils.base_sigma_nm * normalized_amplitude

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
        base_rgb = new_utils.rgb(wavelength_start, gamma=new_utils.gamma_factor)
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

new_utils.axis_labels()
gaussian_iteration(df)
plt.show()

