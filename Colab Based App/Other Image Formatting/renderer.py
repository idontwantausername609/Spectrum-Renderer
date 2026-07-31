import pandas as pd
import csv
import matplotlib.pyplot as plt
import new_utils
import prep_utils
import plot_funcs
import helper_utils
import io


def load_data(file_path):
    """Automatically loads CSV or Excel files into a pandas DataFrame."""
    if not isinstance(file_path, (bytes, bytearray)):
        raise TypeError("load_data expects raw bytes or a bytearray as input.")
    
    if file_path.startswith(b'PK\x03\x04'):
        excel_dict = pd.read_excel(
            io.BytesIO(file_path), 
            sheet_name=None, 
            engine='openpyxl'
        )
        combined_df = pd.concat(excel_dict.values(), ignore_index=True)
        return combined_df
    
    else:
        try:
            text_content = file_path.decode('utf-8-sig') 
            csv_stream = io.StringIO(text_content)
            dialect = csv.Sniffer().sniff(csv_stream.read(2048))
            csv_stream.seek(0)
            df = pd.read_csv(csv_stream, sep=dialect.delimiter)
            return df

        except Exception as e:
            raise ValueError("File content could not be parsed as an XLSX or CSV file.") from e


def trad_spec(
    data_df, 
    #mode,
    scale_mode,
    show_peak_labels,
    nm_col,
    int_col,
    detect_columns,
    title = None,
    random_title = None,
    show_grid = False,
    show_label_colour = None,
    scale_by_int = None,
    fig_size=helper_utils.FIG_SIZE, 
    dpi=helper_utils.DPI,
):
    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = data_df, nm_col=nm_col, int_col=int_col, detect_columns=detect_columns)
    if should_exit_early:
        fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
        ax.set_axis_off()
        print("Ending Rendering Early.")
        return fig
    fig, ax = plot_funcs.plot_trad(
        df_plot_data = df_plot_data, 
        nm_col = helper_utils.wl_col, 
        has_any_nist=has_any_nist,
        #mode=mode,
        scale_mode=scale_mode,
        show_peak_labels=show_peak_labels,
        detect_columns=detect_columns,
        title=title,
        random_title=random_title,
    )
    return fig

# ====================================================================================================================================

def get_rgb_type(graph_type):
    global rgb_type
    if graph_type != 'non rgb line':
        rgb_type = 'yes'
    else:
        rgb_type = 'no'


def axis_labels(
    graph_type,
    show_grid,
    show_peak_labels,
    title,
    random_title,
    reverse_x,
    save_path=None,
    dpi = helper_utils.DPI,
    fig_size = helper_utils.fig_size,
    x_min = helper_utils.X_MIN,
    x_max = helper_utils.X_MAX,
    x_title = helper_utils.X_TITLE,
    y_title = helper_utils.Y_TITLE,
    y_min = 0,
    y_max = 0,
    fig_bg = helper_utils.BG,
    text = helper_utils.COLOUR,
):
    
    plt.figure(figsize=fig_size)
    ax = plt.gca()

    plt.gcf().set_facecolor(fig_bg)
    for spine in ax.spines.values():        # new block. may have to take out or decrease linewidth. 
        spine.set_linewidth(0.3)
        spine.set_color('darkgrey')
    if show_grid is True:
        plt.grid(True, color='darkgrey', linewidth=0.25)   # took out 'linestyle = ':' '    may have to add back in. 
    elif show_grid is False:
        plt.grid(False)

    if reverse_x is True:
        plt.xlim(x_max, x_min)
    else:
        plt.xlim(x_min, x_max)

    y_max = new_utils.set_y_lim(graph_type=graph_type, show_peak_labels=show_peak_labels)

    if title:
        plt.title(str(title).strip(), color = text)
    if random_title:
        plt.title(str(new_utils.generate_random_title()), color=text)

    ax.set_facecolor(fig_bg)
    plt.xlabel(x_title, color=text)
    plt.ylabel(y_title, color=text)
    plt.xticks(color=text)
    plt.yticks(color=text)
    ax.yaxis.set_major_locator(helper_utils.major_locator)
    plt.ylim(y_min, y_max)

    if save_path:
        try:
            ax.savefig(save_path, facecolor=ax.get_facecolor(), bbox_inches='tight', dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches='tight', dpi=dpi)

def plot(
    data_df,
    detect_columns,
    nm_col,
    int_col,
    reverse_x,
    force_nist = None,
    graph_type = None,
    scale_mode = 'auto',
    title = None,
    random_title = None,
    show_peak_labels = None,
    show_grid = True,
    show_label_colour = None,
    scale_by_int = None,
    save_path=None,
):
    df_data, has_any_nist, _, _, _ = prep_utils.run_nist_check(data_df=data_df, detect_columns=detect_columns, force_nist=force_nist, nm_col=nm_col, int_col=int_col)

    if has_any_nist is True:
        prep_type = 'nist'
        nist_plot_type = 'g' or 'gaussian' or 't' or 'traditional'
        if graph_type == 'gaussian':
            plot_funcs.gaussian_iteration(df_plot_data=df_data, detect_columns=detect_columns,show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, int_col=int_col, nm_col=nm_col)
            axis_labels(graph_type=graph_type, show_grid=show_grid, show_peak_labels=show_peak_labels, title=title, random_title=random_title, reverse_x=reverse_x)
        if graph_type == 'traditional':
            scale_mode = 'raw'
            trad_spec(data_df=data_df, detect_columns=detect_columns, scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title, nm_col=nm_col, int_col=int_col)

    else:
        prep_type = 'generic'
        if graph_type == 'traditional':
            trad_spec(data_df=data_df, detect_columns=detect_columns, scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title, nm_col=nm_col, int_col=int_col)

        else:
            data_df, should_exit_early = prep_utils.prep_other(data_df = data_df, detect_columns=detect_columns, int_col=int_col, nm_col=nm_col)
            if should_exit_early:
                fig, ax = plt.subplots(figsize=new_utils.fig_size, dpi=helper_utils.DPI)
                ax.set_axis_off()
                print("Ending Rendering Early.")
                return fig

            axis_labels(graph_type=graph_type, show_grid=show_grid, show_peak_labels=show_peak_labels, title=title, random_title=random_title, reverse_x=reverse_x)
            get_rgb_type(graph_type=graph_type)
            if rgb_type == 'yes':
                scale_by_int=scale_by_int

            if graph_type == 'bar':
                plot_funcs.bar_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'scatter':
                plot_funcs.scatter_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'gaussian':
                plot_funcs.gaussian_iteration(df_plot_data=df_data, detect_columns=detect_columns,show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, int_col=int_col, nm_col=nm_col, scale_by_int=False)
            elif graph_type == 'line':
                plot_funcs.line_plot_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'filled line':
                plot_funcs.filled_plot(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'non rgb line':
                plot_funcs.non_rgb_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour,)

