"""
Local browser-based spectrum renderer.
Run: python webapp3.py
Then navigate to http://localhost:8080 in your browser.
"""

import io
from flask import Flask, render_template, request, send_file, jsonify
import matplotlib.pyplot as plt
import pandas as pd
import loader 
import renderer
import prep_utils
import traceback
import helper_utils

app3 = Flask(__name__)
app3.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

@app3.route('/')
def index():
    return render_template('index.html')

@app3.route('/api/sheets', methods=['POST'])
def get_sheets():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read file bytes into memory to avoid filesystem locks
        file_bytes = file.read()
        sheets = loader.list_sheets(file_bytes)
        return jsonify({'sheets': sheets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app3.route('/api/nistCheck', methods=['POST'])
def nistCheck():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    detect_columns = request.form.get('detect_columns') == 'true'
    nm_col = request.form.get('nm_col')
    int_col = request.form.get('int_col')

    try:
        file_bytes = file.read()
        file.seek(0)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

    df = renderer.load_data(file_bytes)

    _, wl_col, INT_col, needs_manual_selection = helper_utils.res_col_names(
        data_df=df,
        detect_columns=detect_columns,
        nm_col=nm_col,
        int_col=int_col,
    )

    if needs_manual_selection:
        return jsonify({'needs_manual_selection': True}), 200

    is_nist, _, _ = prep_utils.nist_check(
        df,
        detect_columns=detect_columns,
        nm_col=wl_col,
        int_col=INT_col,
    )
    return jsonify({'is_nist': is_nist})

@app3.route('/api/render', methods=['POST'])
def render():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    sheet_name = request.form.get('sheet', None)
    user_title = request.form.get('title', None)
    random_title = 'random_title' in request.form
    show_peak_labels = 'show_peak_labels' in request.form
    show_label_colour = 'show_label_colour' in request.form
    scale_by_int = 'scale_by_int' in request.form
    show_grid = 'show_grid' in request.form
    detect_columns = request.form.get('detect_columns') == 'true'
    nm_col = request.form.get('nm_col')
    int_col = request.form.get('int_col')

    if sheet_name == '':
        sheet_name = None
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        file_bytes = file.read()
        df = renderer.load_data(file_bytes)

        _, wl_col, INT_col, needs_manual_selection = helper_utils.res_col_names(
            data_df=df,
            detect_columns=detect_columns,
            nm_col=nm_col,
            int_col=int_col,
        )

        if needs_manual_selection:
            return jsonify({'needs_manual_selection': True}), 200

        scale_mode = request.form.get('scale_mode', 'raw')
        graph_type = request.form.get('graph_type')

        fig = renderer.plot(
            df,
            detect_columns=detect_columns,
            nm_col=wl_col,
            int_col=INT_col,
            graph_type=graph_type,
            scale_mode=scale_mode,
            show_grid=show_grid,
            scale_by_int=scale_by_int,
            title=user_title,
            random_title=random_title,
            show_peak_labels=show_peak_labels,
            show_label_colour=show_label_colour,
        )

        img_io = io.BytesIO()
        plt.savefig(img_io, format='png', dpi=600, bbox_inches='tight')
        img_io.seek(0)
        plt.close(fig)

        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app3.run(debug=True, port=8080)