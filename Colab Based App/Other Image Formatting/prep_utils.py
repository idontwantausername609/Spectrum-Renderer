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