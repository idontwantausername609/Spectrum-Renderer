"""
Local browser-based spectrum renderer.
Run: python webapp.py
Then navigate to http://localhost:5000 in your browser.
"""

import os
import tempfile
from flask import Flask, render_template, request, send_file, jsonify
from spectrum.loader import load_spectral_data, list_sheets
from spectrum.rendering import render_spectrum
import io
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload


@app.route('/')
def index():
    """Serve main upload form."""
    return render_template('index.html')


@app.route('/api/sheets', methods=['POST'])
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


@app.route('/api/render', methods=['POST'])
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
    dark_mode = 'dark_mode' in request.form  # Checkbox value
    
    # Convert empty string sheet to None
    if sheet_name == '':
        sheet_name = None
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read file bytes into memory and pass bytes to loader
        file_bytes = file.read()

        spectral_data = load_spectral_data(file_bytes, sheet_name=sheet_name, user_title=user_title)

        # read form param (add near other request.form reads)
        scale_mode = request.form.get('scale_mode', 'auto')
        
        # use a default figure size
        figsize = (14, 4)

        # Always auto-detect top-N server-side. Do not accept user-supplied N.
        spectral_data['keep_top_n'] = 0
        
        # pass it when calling render_spectrum()
        fig = render_spectrum(spectral_data, dark_mode=dark_mode, figsize=figsize, scale_mode=scale_mode)

        # Return as PNG
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
    app.run(debug=True, port=5000)
