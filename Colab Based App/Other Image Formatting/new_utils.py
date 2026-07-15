import matplotlib.pyplot as plt
import math
import helper_utils
import prep_utils

#show_grid = None

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

def set_y_lim():
    if helper_utils.graph_type == 'scatter':
        if prep_utils.y_max > 230:
            y_max = round_to_multiple(prep_utils.y_max, 100)
        else:
            y_max = round_to_multiple(prep_utils.y_max, 50)
    else:
        y_max = round_to_multiple(prep_utils.y_max, 50)
    print('(set_y_lim)', y_max)
    return y_max

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

def text_colour():
    global colour
    global bg
    if mode == 'dark':
        colour = 'white'
        bg = 'black'
    if mode == 'light':
        colour = 'black'
        bg = 'white'
    return colour, bg



# ==================================
# Other Image Formatiing Functions
# ==================================

def axis_labels(
    fig_size = helper_utils.fig_size,
    reverse_x = helper_utils.reverse_x,
    x_min = helper_utils.x_min,
    x_max = helper_utils.x_max,
    x_title = helper_utils.x_title,
    y_title = helper_utils.y_title,
    text = None,
    show_grid = helper_utils.show_grid,
    y_min = 0,
    y_max = 0,
):
    
    plt.figure(figsize=fig_size)
    ax = plt.gca()
    get_mode()
    text_colour()


    if mode == 'dark':
        fig_bg = bg
        text = colour
        plt.gcf().set_facecolor(fig_bg)
        if show_grid is True:
            plt.grid(show_grid, color='darkgrey', linewidth=0.25)   # took out 'linestyle = ':' '    may have to add back in. 
        for spine in ax.spines.values():        # new block. may have to take out or decrease linewidth. 
            spine.set_linewidth(0.3)
            spine.set_color('darkgrey')
    else:
        fig_bg = bg
        text = colour
        if show_grid is True:
            plt.grid(show_grid)
        for spine in ax.spines.values():       # new block
            spine.set_linewidth(0.5)


    print(show_grid)


    
    reverse_x = (input("Reverse x-axis? Yes or No")).lower()
    if reverse_x == 'yes' or reverse_x == 'y':
        reverse_x is True
        plt.xlim(x_max, x_min)
    else:
        reverse_x is False
        plt.xlim(x_min, x_max)

    print(reverse_x)

    y_max = set_y_lim()

    ax.set_facecolor(fig_bg)
    plt.xlabel(x_title, color=text)
    plt.ylabel(y_title, color=text)
    plt.xticks(color=text)
    plt.yticks(color=text)
    ax.yaxis.set_major_locator(helper_utils.major_locator)
    plt.title(f'{helper_utils.graph_type.title()} Plot', color = colour)
    plt.ylim(y_min, y_max)
    

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

def trad_spec_labels(fig, ax, x_min, x_max,):
    get_mode()
    text_colour()
    global figure_bg_color
    global text_color

    if mode == 'dark':
        figure_bg_color = 'black'
        text_color = colour
    elif mode == 'light':
        figure_bg_color = 'white'
        text_color = colour

    fig.patch.set_facecolor(figure_bg_color)
    ax.set_facecolor('black')  
    ax.yaxis.set_visible(False)
    ax.set_xlabel(helper_utils.x_title, color=text_color)
    ax.xaxis.set_major_locator(helper_utils.major_locator)
    ax.xaxis.set_minor_locator(helper_utils.minor_locator)
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0,1)

