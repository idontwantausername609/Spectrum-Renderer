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


# From plot_trad()
    '''

    if scale_mode is not None:
        plt.title(f'{scale_mode.capitalize()} Emission Spectrum Visualization', color=helper_utils.COLOUR, y=0.98, pad=pad)
    else:
        plt.title('Emission Spectrum Visualization', color=helper_utils.COLOUR, y=0.98, pad=pad)
    plt.subplots_adjust(top=subplots_adjust_top)

    print("\nDEBUG: fig height = ", fig.get_figheight(), "\n current needle height = ", current_peak_render_height)


    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)


 
    # Save the plot if a save_path is provided
    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)
    '''



def plot_other_spec(data_df, save_path=None):
    helper_utils.get_graph_type()       # needs to be able to use graph_type from webapp3.py / index.html
    if helper_utils.graph_type == 'traditional':
        trad_spec(data_df=data_df)
    else:
        data_df, should_exit_early = prep_utils.prep_other(data_df = data_df)
        if should_exit_early:
            fig, ax = plt.subplots(figsize=new_utils.fig_size, dpi=helper_utils.DPI)
            ax.set_axis_off()
            print("Ending Rendering Early.")
            return fig
        new_utils.show_peak_labels()
        new_utils.axis_labels()

        if helper_utils.rgb_type == 'yes':
            new_utils.scale_by_int()

        if helper_utils.graph_type == 'bar':
            plot_funcs.bar_iteration(data_df = data_df)
        elif helper_utils.graph_type == 'scatter':
            plot_funcs.scatter_iteration(data_df = data_df)
        elif helper_utils.graph_type == 'gaussian':
            plot_funcs.gaussian_iteration(df_plot_data= data_df)
        elif helper_utils.graph_type == 'line':
            plot_funcs.line_plot_iteration(data_df=data_df)
        elif helper_utils.graph_type == 'filled line':
            plot_funcs.filled_plot(data_df = data_df)
        elif helper_utils.graph_type == 'non rgb line':
            plot_funcs.non_rgb_iteration(data_df=data_df)

        if save_path:
            try:
                fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=helper_utils.dpi)
            except Exception:
                plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=helper_utils.dpi)



def detect_prep(
    data_df, 
    force_nist = None, 
    graph_type=None,
    title=None,
    random_title=None,
    mode = 'dark',
    show_peak_labels=True,
    scale_mode = 'auto',
):
    df_data, has_any_nist = prep_utils.run_nist_check(data_df=data_df, force_nist=force_nist)
    if has_any_nist is True:
        prep_type = 'nist'
        nist_plot_type = input("NIST Descriptors Detected. Choose NIST Graph Type: Gaussian or Traditional").lower()
        if nist_plot_type == 'gaussian' or nist_plot_type == 'g':
            helper_utils.graph_type = 'gaussian'
            new_utils.axis_labels()
            plot_funcs.gaussian_iteration(df_plot_data = df_data)
        if nist_plot_type == 'traditional' or nist_plot_type == 'trad' or nist_plot_type == 't':
            scale_mode = 'raw'
            helper_utils.graph_type = 'traditional'
            trad_spec(data_df = df_data)
    else:
        prep_type = 'generic'
        plot_other_spec(data_df=df_data)
    return prep_type, helper_utils.graph_type, scale_mode


def get_generic_type():
    global generic_type
    gen_type = (input('Choose Rendering: Raw or Normalised')).lower()
    if gen_type == 'raw' or gen_type == 'r':
        generic_type = 'raw'
    elif gen_type == 'normalised' or gen_type == 'norm' or gen_type == 'n':
        generic_type = 'normalised'
    print ('Rendering Type: ', generic_type)
    return generic_type


# from trad_spec()
'''
    global figure_bg_color
    global text_color

    text_colour(mode=mode)

    if mode == 'dark':
        figure_bg_color = 'black'
        text_color = colour
    elif mode == 'light':
        figure_bg_color = 'white'
        text_color = colour
'''


# from new_utils.py
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



# from peak_labels()
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

# ===========================
# Prompting Functions
# ===========================

# not used
def scale_by_int():
    global SCALE_BY_INT
    scale = input("Scale brightness by intensity? Yes or No").lower()
    if scale == 'yes' or scale == 'y':
        SCALE_BY_INT = 'yes'
    elif scale == 'no' or scale == 'n':
        SCALE_BY_INT = 'no'
    print('\nScale brightness:', SCALE_BY_INT.capitalize())

# not used
def get_mode():
    global mode
    inp = input("Choose Mode: Dark or Light").lower()
    if inp == 'dark' or inp == 'd':
        mode = 'dark'
    elif inp == 'light' or inp == 'l':
        mode = 'light'
    return mode

# not used
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

# not used
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




'''
# code breaks when this is used. prep functions don't pass properly, causing KeyErrors
def early_exit(data_df, has_any_nist, force_nist = None):
    df_data, has_any_nist = prep_utils.run_nist_check(data_df=data_df, force_nist=force_nist)
    if has_any_nist is True:
        df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = df_data)
        if should_exit_early:
            fig, ax = plt.subplots(figsize=helper_utils.fig_size, dpi=utils.DPI)
            ax.set_axis_off()
            print("Ending Rendering Early.")
            return fig
    else:
        data_df, should_exit_early = prep_utils.prep_other(data_df = df_data)
        if should_exit_early:
            fig, ax = plt.subplots(figsize=new_utils.fig_size, dpi=utils.DPI)
            ax.set_axis_off()
            print("Ending Rendering Early.")
            return fig
'''