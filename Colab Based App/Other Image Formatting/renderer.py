import pandas as pd
import csv
import plotly.graph_objects as go
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
    show_peak_labels,
    scale_mode,
    nm_col,
    int_col,
    detect_columns,
    title = None,
    random_title = None,
    show_grid = False,
    show_label_colour = None,
    scale_by_int = None,
):
    df_plot_data, should_exit_early, has_any_nist = prep_utils.prep_with_nist(data_df = data_df, nm_col=nm_col, int_col=int_col, detect_columns=detect_columns)


    #if should_exit_early:

    FIG = go.Figure()
    FIG = plot_funcs.plot_trad(
        df_plot_data = df_plot_data, 
        nm_col = helper_utils.wl_col, 
        has_any_nist=has_any_nist,
        scale_mode=scale_mode,
        show_peak_labels=show_peak_labels,
        detect_columns=detect_columns,
        title=title,
        random_title=random_title,
    )
    return FIG


# ====================================================================================================================================

def get_rgb_type(graph_type):
    global rgb_type
    if graph_type != 'non rgb line':
        rgb_type = 'yes'
    else:
        rgb_type = 'no'


def plot(
    data_df,
    detect_columns,
    nm_col,
    int_col,
    reverse_x,
    title,
    random_title,
    force_nist = None,
    graph_type = None,
    scale_mode = 'auto',
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
            fig = plot_funcs.gaussian_iteration(df_plot_data=df_data, detect_columns=detect_columns,show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, int_col=int_col, nm_col=nm_col, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title)
        if graph_type == 'traditional':
            scale_mode = 'raw'
            fig = trad_spec(data_df=data_df, detect_columns=detect_columns, scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title, nm_col=nm_col, int_col=int_col)

    else:
        prep_type = 'generic'
        if graph_type == 'traditional':
            fig = trad_spec(data_df=data_df, detect_columns=detect_columns, scale_mode=scale_mode, show_peak_labels=show_peak_labels, title=title, random_title=random_title, nm_col=nm_col, int_col=int_col)

        else:
            data_df, should_exit_early = prep_utils.prep_other(data_df = data_df, detect_columns=detect_columns, int_col=int_col, nm_col=nm_col)

            get_rgb_type(graph_type=graph_type)
            if rgb_type == 'yes':
                scale_by_int=scale_by_int

            if graph_type == 'bar':
                fig = plot_funcs.bar_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int, reverse_x=reverse_x, show_grid=show_grid,title=title, random_title=random_title)
            elif graph_type == 'scatter':
                fig = plot_funcs.scatter_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title)
            elif graph_type == 'gaussian':
                fig = plot_funcs.gaussian_iteration(df_plot_data=df_data, detect_columns=detect_columns,show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, int_col=int_col, nm_col=nm_col, scale_by_int=False, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title)
            elif graph_type == 'line':
                fig = plot_funcs.line_plot_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title)
            elif graph_type == 'filled line':
                fig = plot_funcs.filled_plot(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, scale_by_int=scale_by_int, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title)
            elif graph_type == 'non rgb line':
                fig = plot_funcs.non_rgb_iteration(data_df = data_df, show_peak_labels=show_peak_labels, show_label_colour=show_label_colour, reverse_x=reverse_x, show_grid=show_grid, title=title, random_title=random_title)

    config = new_utils.img_config(title=title, random_title=random_title)
    return fig, config

