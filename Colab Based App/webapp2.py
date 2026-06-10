"""
Local browser-based spectrum renderer.
Run: python webapp2.py
Then navigate to http://localhost:8000 in your browser.
"""

import io
import os
from flask import Flask, render_template, request, send_file, jsonify
import matplotlib.pyplot as plt
import pandas as pd
from new_loader import list_sheets
import new_renderer
import utils


app2 = Flask(__name__)
app2.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

@app2.route('/')
def index():
    """Serve main upload form."""
    return render_template('index.html')


@app2.route('/api/sheets', methods=['POST'])
def get_sheets():
    """
    List sheets in uploaded Excel file.
    
    Form data:
        file: Uploaded Excel file
    
    JSON response:
        {'sheets': [...]}
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read file bytes into memory to avoid filesystem locks
        file_bytes = file.read()
        sheets = list_sheets(file_bytes)
        return jsonify({'sheets': sheets})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app2.route('/api/render', methods=['POST'])
def render():
    """
    Load spectrum and render to image.
    
    Form data:
        file: Uploaded Excel file
        sheet: Sheet name (can be empty for auto-detect)
        title: User-entered spectrum title (can be empty for random fallback)
        dark_mode: 'on' or not present (checked state)
    
    Response:
        PNG image data or error JSON
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    sheet_name = request.form.get('sheet', None)
    user_title = request.form.get('title', None)
    random_title = 'random_title' in request.form
    mode = 'dark' if 'dark_mode' in request.form else 'light'
    
    # Convert empty string sheet to None
    if sheet_name == '':
        sheet_name = None
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        file_bytes = file.read()

        # Read Excel bytes directly into a pandas DataFrame
        df = pd.read_excel(io.BytesIO(file_bytes),
            sheet_name=sheet_name if sheet_name is not None else 0,
            engine='openpyxl')

        fig_size = utils.FIG_SIZE
        scale_mode = request.form.get('scale_mode', 'raw')

        fig = new_renderer.plot_spec(
            df,
            mode=mode,
            fig_size=fig_size,
            scale_mode=scale_mode,
            title=user_title,
            random_title=random_title
        )

        img_io = io.BytesIO()
        fig.savefig(img_io, format='png', dpi=150, bbox_inches='tight')
        img_io.seek(0)
        plt.close(fig)

        return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app2.run(debug=True, port=8000)