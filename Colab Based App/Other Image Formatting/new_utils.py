from scipy.signal import find_peaks
import math
import random
import string
import helper_utils
import prep_utils


# ==========================
# Image Resolution Config
# ==========================

def img_config(title, random_title):

    if title:
        save_title = str(title).strip().replace(" ", "_")        # want to have it add underscores between words 
    if random_title:
        save_title = str(generate_random_title())
    else:
        save_title = str(generate_random_title())

    config = {
        'displaylogo': False,
        'displayModeBar': 'hover',
        'scrollZoom': True,
        'toImageButtonOptions': {
            'format': 'png',
            'scale': 10.0,
            'filename': f"{save_title}" 
        }
    }

    return config

# ===============
# From utils.py
# ===============

def generate_random_title():
    random_code = ''.join(random.choices(string.digits, k=4))
    return f'Spectrum-{random_code}'

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

def round_to_multiple(y_max, mult):
    num = y_max % 100
    base = (y_max // 100) * 100
    rounded = math.ceil(num / mult) * mult 
    new_y_max = base + rounded
    return new_y_max

def colored_rgb(base_rgb, final_intensity_scale):
    colored_rgb = (base_rgb[0] * final_intensity_scale,
                   base_rgb[1] * final_intensity_scale,
                   base_rgb[2] * final_intensity_scale)
    return colored_rgb

def set_y_lim(graph_type, show_peak_labels):
    if graph_type == 'scatter' or show_peak_labels is True:
        if prep_utils.Y_MAX % 100 > 80:
            y_max = round_to_multiple(prep_utils.Y_MAX, 150)
        elif prep_utils.Y_MAX % 100 > 30:
            y_max = round_to_multiple(prep_utils.Y_MAX, 100)
        else:
            y_max = round_to_multiple(prep_utils.Y_MAX, 50)
    else:
        y_max = round_to_multiple(prep_utils.Y_MAX, 50)
    print('(set_y_lim)', y_max)
    return y_max


def margin_corrs(graph_type, title, random_title, show_peak_labels, has_any_nist, scale_mode):

    if title:
        plot_title = str(title).strip()
        top_margin = 65
    elif random_title:
        plot_title= str(generate_random_title())
        if graph_type == 'traditional':
            top_margin = 35
        elif graph_type != 'traditional':
            top_margin = 65
    else:
        plot_title = None
        if graph_type != 'traditional':
            top_margin = 30
        else:
            if scale_mode == 'raw' or has_any_nist:
                top_margin = 10
            elif scale_mode == 'normalize':
                top_margin = 0

    if show_peak_labels is True and graph_type =='traditional':
        if has_any_nist is False:
            top_margin += 15
        elif has_any_nist is True:
            top_margin -= 15

    return top_margin, plot_title

def set_major_y_ticks(y_max):
    if 150 <= y_max <= 350:
        major_y_tick = 50
    elif 400 <= y_max <= 800:
        major_y_tick = 100
    elif 900 <= y_max <= 1400:
        major_y_tick = 200
    elif 1500 <= y_max <= 3500:
        major_y_tick = 500
    elif 4000 <= y_max <= 8000:
        major_y_tick = 1000

    return major_y_tick

# ==================================
# Other Image Formatiing Functions
# ==================================

def hover_config(data_df):
    hover = (
        f"{helper_utils.wl_col} = %{{x}}<br>"
        f"{helper_utils.INT_col} = %{{y}}<extra></extra>"
    )
    return hover

def axis_labels(
    graph_type,
    show_peak_labels,
    reverse_x,
    show_grid,
    title,
    random_title,
    x_title=helper_utils.X_TITLE,
    y_title=helper_utils.Y_TITLE,
    x_min = helper_utils.X_MIN,
    x_max=helper_utils.X_MAX,
    bg_colour = helper_utils.BG,
    text_colour=helper_utils.COLOUR,
    grid_color=helper_utils.GRID_COLOUR,
    grid_width=0.1,
    grid_dash='dot',
    line_color=helper_utils.LINE_COLOUR,
    line_width=0.2,
    major_ticks=helper_utils.MAJOR_TICKS, 
    fig_width=helper_utils.fig_size[0] * 70, # will have to keep adjusting
    fig_height=helper_utils.fig_size[1] * 97,
    tick_padding = 7,
):

    y_max = set_y_lim(graph_type=graph_type, show_peak_labels=show_peak_labels)
    y_range = [0, y_max]
    range_x = [400, 750]
    dtick_y = set_major_y_ticks(y_max=y_max)

    if reverse_x is True:
        x_range = [range_x[1], range_x[0]]
    elif reverse_x is False:
        x_range=range_x

    top_margin, plot_title = margin_corrs(graph_type=graph_type, title=title, random_title=random_title, show_peak_labels=show_peak_labels, has_any_nist=None, scale_mode=None)

    layout_config = dict(
        dragmode='pan',
        plot_bgcolor=bg_colour,
        paper_bgcolor=bg_colour,
        font=dict(color=text_colour, family='Roboto'),
        width=fig_width,
        height=fig_height,
        xaxis=dict(
            title=x_title,
            range=x_range,
            showgrid=show_grid,
            gridcolor=grid_color,
            gridwidth=grid_width,
            griddash=grid_dash,
            showline=True,
            linecolor=line_color,
            linewidth=line_width,
            mirror=True,
            tickfont=dict(color=text_colour),
            dtick=major_ticks,
            ticklabelstandoff = tick_padding
        ),
        
        yaxis=dict(
            title=y_title,
            range=y_range, 
            showgrid=show_grid,
            gridcolor=grid_color,
            gridwidth=grid_width,
            griddash=grid_dash,
            showline=True,
            linecolor=line_color,
            linewidth=line_width,
            mirror=True,
            tickfont=dict(color=text_colour),
            dtick=dtick_y,
            ticklabelstandoff = tick_padding
        ),

        title=dict(
            text=plot_title, 
            automargin=True,
            yref='container', 
            xref='paper', 
            yanchor='top', 
            xanchor='center', 
            y=0.96, 
            x=0.5,
            font=dict(size=20)),
        margin=dict(t=top_margin, b=70, l=80, r=40, pad=0),
        meta={'modebar_style': 'vertical'},
        modebar_orientation = 'v',
    )

    if not show_grid:
        layout_config['xaxis']['showgrid'] = False
        layout_config['yaxis']['showgrid'] = False

    return layout_config


def peak_labels(data_df, show_label_colour, has_any_nist):

    print("\n\nDEBUG: peak_labels\nhas nist:", has_any_nist)

    if has_any_nist is False:
        peaks, _ = find_peaks(data_df[helper_utils.INT_col], prominence=dynamic_prominence(helper_utils.DEFAULT_PROM_PERC, prep_utils.int_range)) 
        int_col = helper_utils.INT_col
    else:
        peaks, _ = find_peaks(data_df['_raw_int'].astype(int), prominence=helper_utils.NORM_PROM_PERC)
        int_col = ['_raw_int']

    print("DEBUG: int col:", int_col)

    labels = []
    for peak_index in peaks:
        row = data_df.iloc[peak_index]
        #wavelength = row[helper_utils.wl_col]
        wl_labels = float(data_df.iloc[peak_index][helper_utils.wl_col])
        base_rgb=helper_utils.rgb(wl_labels)
        final_int_scale = 1.0
        colour_rgb=colored_rgb(base_rgb, final_int_scale)
        color_str = f"rgb({int(colour_rgb[0])}, {int(colour_rgb[1])}, {int(colour_rgb[2])})"
        if show_label_colour is False:
            font_colour = helper_utils.COLOUR
        else:
            font_colour = color_str
        label_config = dict(
            x=row[helper_utils.wl_col],
            y=float(row[int_col]),
            text=f"{row[helper_utils.wl_col]:.2f} nm",
            showarrow=False,
            yshift=15,
            opacity=1,
            font=dict(color=font_colour)
        )
        labels.append(label_config)

    return labels

# =============================
# Traditional Spec Codes
# =============================

def trad_spec_labels(
    has_any_nist,
    scale_mode,
    fig_height,
    title,
    random_title,
    #plot_title,
    show_peak_labels,
    graph_type = 'traditional',
    x_title=helper_utils.X_TITLE,
    show_grid=False,
    bg_colour = helper_utils.BG,
    text_colour=helper_utils.COLOUR,
    major=helper_utils.MAJOR_TICKS,
    ):

    top_margin, plot_title = margin_corrs(graph_type=graph_type, title=title, random_title=random_title, show_peak_labels=show_peak_labels, has_any_nist=has_any_nist, scale_mode=scale_mode)

    print("\nDEBUG: plot title (trad spec labels)", plot_title, "\ntop margin:", top_margin)

    layout_config = dict (
        plot_bgcolor=bg_colour,
        paper_bgcolor=bg_colour,
        width = helper_utils.FIG_WIDTH * 80,
        height = fig_height,
        title=dict(
            text=plot_title, 
            yref='container', 
            xref='paper', 
            yanchor='top', 
            xanchor='center', 
            y=0.96, 
            x=0.5),
        margin=dict(l=15, r=15, b=40, t=top_margin), 
        font=dict(
            color=text_colour,
            family = 'Roboto',
            ),
        xaxis=dict(
            range=[helper_utils.X_MIN, helper_utils.X_MAX],
            gridcolor=bg_colour,
            showgrid=show_grid,
            title=dict(text=x_title, standoff=4),
            dtick=major,
            ticks='outside',
            tickcolor=text_colour,
            minor = dict(dtick=10, ticks='outside', tickcolor=text_colour, tickwidth=0.5),
            showline=False,
            automargin=True,
        ),
        yaxis=dict(
            range=[0,1],
            visible=False,
            automargin=True,
        ),
        meta={'modebar_style': 'shifted_horizontal'}
    )

    return layout_config