import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import math
import random
import string
import helper_utils
import prep_utils

#show_grid = None

# ===============
# From utils.py
# ===============

def generate_random_title():
    random_code = ''.join(random.choices(string.digits, k=4))
    return f'Spectrum-{random_code}'

'''
# not called at all. to be deleted

def normalize_header(value):
    return str(value).strip().lower() if value is not None else ''

def clean_title(text):
    text = str(text).strip() if text is not None else ''
    if not text:
        return None
    return text.split()[0]

def looks_like_number(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False
'''

# ===========================
# Prompting Functions
# ===========================

def scale_by_int():
    global SCALE_BY_INT
    scale = input("Scale brightness by intensity? Yes or No").lower()
    if scale == 'yes' or scale == 'y':
        SCALE_BY_INT = 'yes'
    elif scale == 'no' or scale == 'n':
        SCALE_BY_INT = 'no'
    print('\nScale brightness:', SCALE_BY_INT.capitalize())

def get_mode():
    global mode
    inp = input("Choose Mode: Dark or Light").lower()
    if inp == 'dark' or inp == 'd':
        mode = 'dark'
    elif inp == 'light' or inp == 'l':
        mode = 'light'
    return mode

def text_colour(mode):
    global colour
    global bg
    if mode == 'dark':
        colour = 'white'
        bg = 'black'
    if mode == 'light':
        colour = 'black'
        bg = 'white'
    return colour, bg

def show_peak_labels():
    global SHOW_PEAKS, show_rgb_peaks
    show_labels = input("Show Peak Labels? Yes or No").lower()
    if show_labels == 'yes' or show_labels == 'y':
        SHOW_PEAKS = 'yes'
        show_rgb = input("Show Peak Labels in Colour? Yes or No").lower()
        if show_rgb == 'yes' or show_rgb == 'y':
            show_rgb_peaks = 'yes'
        if show_rgb == 'no' or show_rgb == 'n':
            show_rgb_peaks = 'no'
    if show_labels == 'no' or show_labels == 'n':
        SHOW_PEAKS = 'no'




# =======================
# Calculation Functions
# =======================

def dynamic_prominence(prominence, int_range):
    dyn_prom = prominence * int_range
    return dyn_prom

# for final_alpha AND final_intensity_scale
def final_scale(min, factor):
    final = min + (1 - min) * factor
    return final

def left_x(a, b):
    xleft = a - b / 2
    return xleft

def right_x(a, b):
    xright = a + b / 2
    return xright

def round_to_multiple(num, mult):
    rounded = math.ceil(num / mult) * mult 
    return rounded

def colored_rgb(base_rgb, final_intensity_scale):
    colored_rgb = (base_rgb[0] * final_intensity_scale,
                   base_rgb[1] * final_intensity_scale,
                   base_rgb[2] * final_intensity_scale)
    return colored_rgb

def set_y_lim(graph_type, show_peak_labels):
    if graph_type == 'scatter' or show_peak_labels is True:
        if prep_utils.Y_MAX > 230:
            y_max = round_to_multiple(prep_utils.Y_MAX, 100)
        else:
            y_max = round_to_multiple(prep_utils.Y_MAX, 50)
    else:
        y_max = round_to_multiple(prep_utils.Y_MAX, 50)
    print('(set_y_lim)', y_max)
    return y_max



# ==================================
# Other Image Formatiing Functions
# ==================================

def peak_labels(data_df, show_label_colour, ):
    peaks, _ = find_peaks(data_df[helper_utils.INT_col], prominence=dynamic_prominence(helper_utils.DEFAULT_PROM_PERC, prep_utils.int_range)) # Using dynamic prominence
    # Label the identified sharp peaks
    for peak_index in peaks:
        row = data_df.iloc[peak_index]
        wl_labels = float(data_df.iloc[peak_index][helper_utils.wl_col])
        base_rgb = helper_utils.rgb(wl_labels)
        final_intensity_scale = 1.0
        color_rgb = colored_rgb(base_rgb, final_intensity_scale)
        
        if show_label_colour is True: #and mode == 'dark':
            plt.annotate(f"{row[helper_utils.wl_col]:.2f} nm", # Formatted nm to two decimal places
                        (row[helper_utils.wl_col], row[helper_utils.INT_col]),
                        textcoords="offset points", # Offset the text
                        xytext=(0,10), # Distance from point to label
                        ha='center', # Horizontal alignment
                        color=color_rgb,        # this makes the text rgb
                        )
        else:
            plt.annotate(f"{row[helper_utils.wl_col]:.2f} nm", # Formatted nm to two decimal places
                        (row[helper_utils.wl_col], row[helper_utils.INT_col]),
                        textcoords="offset points", # Offset the text
                        xytext=(0,10), # Distance from point to label
                        ha='center', # Horizontal alignment
                        color = helper_utils.COLOUR,
                        )
'''
        elif show_label_colour is True and mode == 'light':
            plt.annotate(f"{row[helper_utils.wl_col]:.2f} nm", # Formatted nm to two decimal places
                        (row[helper_utils.wl_col], row[helper_utils.INT_col]),
                        textcoords="offset points", # Offset the text
                        xytext=(0,10), # Distance from point to label
                        ha='center', # Horizontal alignment
                        bbox=dict(boxstyle="round,pad=0.3", fc=color_rgb, ec=color_rgb, lw=0.5, alpha=0.7),           # this makes the bbox rgb
                        )
'''
                        

def axis_labels(
    fig_size = helper_utils.fig_size,
    reverse_x = helper_utils.reverse_x,
    x_min = helper_utils.X_MIN,
    x_max = helper_utils.X_MAX,
    x_title = helper_utils.X_TITLE,
    y_title = helper_utils.Y_TITLE,
    text = None,
    y_min = 0,
    y_max = 0,
    mode = 'dark'
):
    
    plt.figure(figsize=fig_size)
    ax = plt.gca()
    text_colour(mode=mode)
    show = input("Show Grid? Yes or No").lower()

    if mode == 'dark':
        fig_bg = bg
        text = colour
        plt.gcf().set_facecolor(fig_bg)
        for spine in ax.spines.values():        # new block. may have to take out or decrease linewidth. 
            spine.set_linewidth(0.3)
            spine.set_color('darkgrey')
        if show == 'yes' or show == 'y':
            plt.grid(True, color='darkgrey', linewidth=0.25)   # took out 'linestyle = ':' '    may have to add back in. 
        elif show == 'no' or show == 'n':
            plt.grid(False)
    else:
        fig_bg = bg
        text = colour
        for spine in ax.spines.values():       # new block
            spine.set_linewidth(0.5)
        if show == 'yes' or show == 'y':
            plt.grid(True)
        elif show == 'no' or show == 'n':
            plt.grid(False)

    reverse_x = (input("Reverse x-axis? Yes or No")).lower()
    if reverse_x == 'yes' or reverse_x == 'y':
        reverse_x is True
        plt.xlim(x_max, x_min)
    else:
        reverse_x is False
        plt.xlim(x_min, x_max)

    y_max = set_y_lim()

    ax.set_facecolor(fig_bg)
    plt.xlabel(x_title, color=text)
    plt.ylabel(y_title, color=text)
    plt.xticks(color=text)
    plt.yticks(color=text)
    ax.yaxis.set_major_locator(helper_utils.major_locator)
    plt.title(f'{helper_utils.graph_type.title()} Plot', color = colour)        # set_title()
    plt.ylim(y_min, y_max)


'''
# need to make this so that it works with web code

def set_title():
    t = input("Choose: Custom or Random Title?").lower()
    if t == 'c':
        title = input("Enter Custom Title")
        plt.title(str(title).strip(), color=new_utils.colour, y=1.0, pad=10)
    if t == 'r':
        plt.title(new_utils.generate_random_title(), color=new_utils.colour, y=1.0, pad=10)
'''
    

# =============================
# Traditional Spec Codes
# =============================

def get_generic_type():
    global generic_type
    gen_type = (input('Choose Rendering: Raw or Normalised')).lower()
    if gen_type == 'raw' or gen_type == 'r':
        generic_type = 'raw'
    elif gen_type == 'normalised' or gen_type == 'norm' or gen_type == 'n':
        generic_type = 'normalised'
    print ('Rendering Type: ', generic_type)
    return generic_type

def trad_spec_labels(fig, ax, x_min, x_max, figure_bg_color = helper_utils.BG, text_color = helper_utils.COLOUR):

    fig.patch.set_facecolor(figure_bg_color)
    ax.set_facecolor('black')  
    ax.yaxis.set_visible(False)
    ax.set_xlabel(helper_utils.X_TITLE, color=text_color)
    ax.xaxis.set_major_locator(helper_utils.major_locator)
    ax.xaxis.set_minor_locator(helper_utils.minor_locator)
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0,1)


    #text_colour(mode=mode)

'''
    global figure_bg_color
    global text_color

    if mode == 'dark':
        figure_bg_color = 'black'
        text_color = colour
    elif mode == 'light':
        figure_bg_color = 'white'
        text_color = colour
'''

