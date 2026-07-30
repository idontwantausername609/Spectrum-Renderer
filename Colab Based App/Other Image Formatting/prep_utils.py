import numpy as np
import pandas as pd
import nist_codes
import helper_utils


def nist_check(data_df, detect_columns, nm_col, int_col, force_nist=None):
    df_data = data_df.copy()
    helper_utils.res_col_names(data_df=data_df, detect_columns=detect_columns, nm_col=nm_col, int_col=int_col,)
    df_data[helper_utils.wl_col] = pd.to_numeric(df_data[helper_utils.wl_col], errors='coerce')
    has_any_nist, nist_diag = nist_codes.detect_nist_values(df_data[helper_utils.INT_col], force_nist=force_nist)
    if has_any_nist:
        has_nist = True
    else:
        has_nist = False
    return has_nist, nm_col, int_col

def run_nist_check(data_df, detect_columns, nm_col, int_col, force_nist=None):
    helper_utils.res_col_names(data_df=data_df, detect_columns=detect_columns, nm_col=nm_col, int_col=int_col,)
    df_data = data_df.copy()
    df_data[helper_utils.wl_col] = pd.to_numeric(df_data[helper_utils.wl_col], errors='coerce')
    has_any_nist, nist_diag = nist_codes.detect_nist_values(df_data[helper_utils.INT_col], force_nist=force_nist)
    return df_data, has_any_nist, detect_columns, nm_col, int_col


def prepare_generic_spectrum(df, int_col, apply_descriptor_adjustments=False):
    df = df.copy()
    df['_raw_int'] = pd.to_numeric(df[int_col], errors='coerce')
    df['_descriptor'] = ''
    df['_intensity_mult'] = 1.0
    df['_width_mult'] = 1.0
    df['_include'] = True
    df['_adj_int'] = df['_raw_int']
    return df


def prep_with_nist(data_df, detect_columns, nm_col, int_col, x_min = helper_utils.X_MIN, x_max = helper_utils.X_MAX, apply_descriptor_adjustments = False):
    global int_range

    df_plot_data, has_any_nist, _, _, _ = run_nist_check(data_df=data_df, detect_columns=detect_columns, nm_col=nm_col, int_col=int_col,)
    if has_any_nist:
        df_plot_data = nist_codes.prepare_nist_spectrum(df_plot_data, helper_utils.INT_col, apply_descriptor_adjustments)
        print('NIST Destriptors Detected. Preparing NIST Rendering.')
    else:
        df_plot_data = prepare_generic_spectrum(df_plot_data, helper_utils.INT_col, apply_descriptor_adjustments)
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
        return None, True, False 

    # Normalize using adjusted intensity
    min_int_val = df_plot_data['_adj_int'].min()
    max_int_val = df_plot_data['_adj_int'].max()
    int_range = max_int_val - min_int_val
    
    if int_range == 0 or np.isnan(int_range):
        df_plot_data['Norm_Int'] = 1.0
    else:
        df_plot_data['Norm_Int'] = (df_plot_data['_adj_int'] - min_int_val) / int_range

    return df_plot_data, False, has_any_nist



def prep_other(data_df, detect_columns, nm_col, int_col, x_min = helper_utils.X_MIN, x_max = helper_utils.X_MAX):
    global int_range
    global Y_MAX

    helper_utils.res_col_names(data_df=data_df, detect_columns=detect_columns, nm_col=nm_col, int_col=int_col,)
    df_filtered = data_df.copy()
    df_filtered = df_filtered[(df_filtered[helper_utils.wl_col] >= x_min) & (df_filtered[helper_utils.wl_col] <= x_max)].copy()
    df_filtered = df_filtered.sort_values(by=helper_utils.wl_col).reset_index(drop=True)

    min_int = df_filtered[helper_utils.INT_col].min()
    max_int = df_filtered[helper_utils.INT_col].max()

    int_range = max_int - min_int
    int_vals = df_filtered[helper_utils.INT_col]
    Y_MAX = int_vals.max()
    print('(prep_other) ymax = ', Y_MAX)

    if int_range == 0:
        df_filtered['Norm_Int'] = 1.0
    else:
        df_filtered['Norm_Int'] = (df_filtered[helper_utils.INT_col] - min_int) / int_range

    if df_filtered.empty:
        return None, True 

    return df_filtered, False