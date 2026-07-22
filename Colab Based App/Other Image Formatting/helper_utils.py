'''
this module has the predefined variables, get_graph_type(), set_grid(), the intensity column resolving, and the rgb conversion functions. 
'''

import re
import matplotlib.ticker as ticker

y_title = 'Intensity'
x_title = 'Wavelength (nm)'
fig_size = (15,6)
prominence = 0.08       # changed from 0.12
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
plot_type = None
show_grid = True


major_locator = ticker.MultipleLocator(50)
minor_locator = ticker.MultipleLocator(10)


lambda_tokens = ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm", "Observed", "Observed Wavelength", "obs", "wave", "w"]

int_tokens =["Grey Val", "grey val", "gray val", "grayscale", "gray value", "intensity", "signal", "counts", "value", "int", "rel. int.", "grey", "Rel. Int.", "Relative Intensity", "Rel Int", "Intensity", "A", "Aki", "gA", "gf", "weighted f", "f", "Intensity/Counts", 'rel', 'count', 'flux', 'grey value', 'i']


def get_graph_type():
    global graph_type, rgb_type
    RGB_TYPE = input("Render as RGB Spectrum? Choose: Yes or No").lower()
    if RGB_TYPE == 'yes' or RGB_TYPE == 'y':
        rgb_type = 'yes'
        GRAPH_TYPE = input("Choose Graph Type: Line, Bar, Scatter, Gaussian, Traditional").lower()
        if GRAPH_TYPE == 'bar' or GRAPH_TYPE == 'b':
            graph_type = 'bar'
        elif GRAPH_TYPE == 'scatter' or GRAPH_TYPE == 's':
            graph_type = 'scatter'
        elif GRAPH_TYPE == 'gaussian' or GRAPH_TYPE == 'g':
            graph_type = 'gaussian'
        elif GRAPH_TYPE == 'line' or GRAPH_TYPE == 'l':
            FILL_TYPE = input("Filled Graph? Choose: Yes or No").lower()
            if FILL_TYPE == 'yes' or FILL_TYPE == 'y':
                graph_type = 'filled line'
            else:
                graph_type = 'line'           
        elif GRAPH_TYPE == 'traditional' or GRAPH_TYPE == 'trad' or GRAPH_TYPE == 't':
            graph_type = 'traditional'
        return GRAPH_TYPE
    elif RGB_TYPE == 'no' or RGB_TYPE == 'n':
        rgb_type = 'no'
        graph_type = 'non rgb line'

    return RGB_TYPE



def resolve_column(df, candidates, label):
    headers = [(str(col).strip(), str(col).strip().lower()) for col in df.columns]

    # Build a flat keyword list from all candidates.
    # Each candidate may be a phrase; we split on non-alphanumeric characters.
    keywords = []
    for candidate in candidates:
        text = str(candidate).strip().lower()
        if not text:
            continue
        parts = [part for part in re.split(r'[^a-z0-9]+', text) if part]
        keywords.extend(parts if parts else [text])

    # Prefer exact matches first, then keyword containment.
    for original, normalized in headers:
        for candidate in candidates:
            candidate_norm = str(candidate).strip().lower()
            if candidate_norm and normalized == candidate_norm:
                return original
    for original, normalized in headers:
        for keyword in keywords:
            if keyword and keyword in normalized:
                return original
    raise KeyError("Could not find a", label, "column. Available columns:", (df.head()))       # want this to show like print(df.head()). df.head() needs to start on a new line. 


def res_col_names(data_df, nm_col = None, int_col = None,):
    global wl_col
    global INT_col
    if nm_col is None:
        wl_col = resolve_column(data_df, lambda_tokens, "wavelength",)
    if int_col is None:
        INT_col = resolve_column(data_df, int_tokens, "intensity",)
    return data_df, wl_col, INT_col


def rgb(wavelength, gamma=gamma_factor):
    wavelength = float(wavelength)
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
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    return (R, G, B)
