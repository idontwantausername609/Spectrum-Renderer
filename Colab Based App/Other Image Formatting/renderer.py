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


def trad_spec(
    data_df, 
    #mode,
    scale_mode,
    show_peak_labels,
    title = None,
    random_title = None,
    show_grid = False,
    show_label_colour = None,
    scale_by_int = None,
    fig_size=helper_utils.FIG_SIZE, 
    dpi=helper_utils.DPI,
):
    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = data_df)
    if should_exit_early:
        fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
        ax.set_axis_off()
        print("Ending Rendering Early.")
        return fig
    fig, ax = plot_funcs.plot(
        df_plot_data = df_plot_data, 
        nm_col = helper_utils.wl_col, 
        has_any_nist=has_any_nist,
        #mode=mode,
        scale_mode=scale_mode,
        show_peak_labels=show_peak_labels,
    )
    return fig



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
    save_path=None,
    dpi = helper_utils.DPI,
    fig_size = helper_utils.fig_size,
    reverse_x = helper_utils.reverse_x,
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

    #reverse_x = (input("Reverse x-axis? Yes or No")).lower()
    #if reverse_x == 'yes' or reverse_x == 'y':
    #    reverse_x is True
    #    plt.xlim(x_max, x_min)
    #else:
    #    reverse_x is False
    #    plt.xlim(x_min, x_max)

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



def plot(
    data_df,
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
    df_data, has_any_nist = prep_utils.run_nist_check(data_df=data_df, force_nist=force_nist)
    if has_any_nist is True:
        prep_type = 'nist'
        nist_plot_type = 'g' or 'gaussian' or 't' or 'traditional'
        if nist_plot_type == 'g' or nist_plot_type == 'gaussian':
            graph_type = 'gaussian'
            axis_labels(graph_type=graph_type, show_grid=show_grid, show_peak_labels=show_peak_labels, title=title, random_title=random_title)
            plot_funcs.gaussian_iteration(df_plot_data=df_data, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, )
        if nist_plot_type =='t' or nist_plot_type == 'traditional':
            scale_mode = 'raw'
            graph_type = 'traditional'
            trad_spec(data_df=data_df, scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title)

    else:
        prep_type = 'generic'
        if graph_type == 'traditional':
            trad_spec(data_df=data_df,  scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title)

        else:
            data_df, should_exit_early = prep_utils.prep_other(data_df = data_df)
            if should_exit_early:
                fig, ax = plt.subplots(figsize=new_utils.fig_size, dpi=helper_utils.DPI)
                ax.set_axis_off()
                print("Ending Rendering Early.")
                return fig

            axis_labels(graph_type=graph_type, show_grid=show_grid, show_peak_labels=show_peak_labels, title=title, random_title=random_title)
            get_rgb_type(graph_type=graph_type)
            if rgb_type == 'yes':
                scale_by_int=scale_by_int


            if graph_type == 'bar':
                plot_funcs.bar_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'scatter':
                plot_funcs.scatter_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'gaussian':
                plot_funcs.gaussian_iteration(df_plot_data=data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=False)
            elif graph_type == 'line':
                plot_funcs.line_plot_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'filled line':
                plot_funcs.filled_plot(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int)
            elif graph_type == 'non rgb line':
                plot_funcs.non_rgb_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour,)
