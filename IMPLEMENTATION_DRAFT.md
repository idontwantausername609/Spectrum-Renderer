# Implementation Blueprint: Spectrum Graphing Tool
## Modular Architecture + Browser-Based Upload & Render

---

## Project Structure

```
spectrum/
├── __init__.py
├── nist_descriptors.py       # Descriptor constants and parsing
├── loader.py                 # Excel file loading and parsing
├── rendering.py              # Spectrum building and rendering
└── utils.py                  # Shared utilities

webapp.py                      # Flask server (local browser interface)
Cleaned up code.ipynb         # Working reference notebook
Fresh Notebook.ipynb          # Updated to use modules + user title input
```

---

## Module 1: `spectrum/nist_descriptors.py`

**Purpose:** Define NIST descriptor semantics and provide parsing utilities.

```python
# spectrum/nist_descriptors.py

"""
NIST descriptor constants and parsing functions.
Descriptor format: (include, intensity_multiplier, width_multiplier, confidence, visual_action)
"""

NIST_DESCRIPTORS = {
    # ... (all 29 descriptors as currently in Cleaned up code.ipynb)
    '*': (True, 1.0, 1.0, 'medium', 'line'),
    ':': (True, 1.0, 1.0, 'high', 'line'),
    # ... etc
}

DESCRIPTOR_KEYS = sorted(NIST_DESCRIPTORS.keys(), key=len, reverse=True)
CONFIDENCE_ORDER = {'high': 0, 'medium': 1, 'low': 2, 'excluded': 3}


def split_descriptor_tokens(descriptor_text):
    """
    Split composite descriptor strings like 'bl*' or 'w*' into known tokens.
    
    Args:
        descriptor_text (str): Raw descriptor suffix from intensity column
    
    Returns:
        list[str]: List of recognized descriptor tokens
    """
    # ... (existing implementation from Cleaned up code.ipynb)


def combine_descriptor_rules(tokens):
    """
    Combine multiple descriptor tokens into aggregate rules.
    
    Args:
        tokens (list[str]): Parsed descriptor tokens
    
    Returns:
        tuple: (include, intensity_multiplier, width_multiplier, confidence, actions, unknown_tokens)
    """
    # ... (existing implementation from Cleaned up code.ipynb)


def parse_nist_intensity(intensity_value):
    """
    Parse numeric intensity with optional descriptor suffix. Example: '100bl*'
    
    Args:
        intensity_value: Cell value from intensity column
    
    Returns:
        tuple: (numeric_intensity, raw_descriptor, tokens, intensity_multiplier, 
                width_multiplier, confidence, actions, unknown_tokens)
    """
    # ... (existing implementation from Cleaned up code.ipynb)
```

---

## Module 2: `spectrum/loader.py`

**Purpose:** Load and parse Excel workbooks; extract spectral data.

```python
# spectrum/loader.py

"""
Load Excel workbooks and extract spectral line data with NIST descriptor parsing.
"""

import numpy as np
import openpyxl
import os
from collections import Counter
from .nist_descriptors import parse_nist_intensity, NIST_DESCRIPTORS
from .utils import clean_title, normalize_header, looks_like_number


def find_spectral_sheet(workbook):
    """
    Scan workbook for a sheet with recognizable wavelength and intensity columns.
    
    Args:
        workbook: openpyxl Workbook object
    
    Returns:
        tuple: (sheet, header_row, wavelength_col, intensity_col, title_col) 
               or (None, None, None, None, None) if not found
    """
    # ... (existing implementation from Cleaned up code.ipynb)


def load_spectral_data(excel_file_path, sheet_name=None, user_title=None):
    """
    Load spectral data from an Excel file.
    
    High-level function: given a file path, returns structured spectral data
    ready for rendering.
    
    Args:
        excel_file_path (str): Path to Excel workbook
        sheet_name (str, optional): Sheet to load; if None, uses first valid
        user_title (str, optional): User-provided spectrum title; if blank or None,
                                     infers from workbook or generates random code
    
    Returns:
        dict: {
            'wavelengths': np.array,      # Parsed wavelengths in nm
            'intensities': np.array,      # Corrected intensities (numeric × multiplier)
            'width_factors': np.array,    # Width multipliers per line
            'actions': list[str],         # Visual actions per line ('line', 'broad', etc.)
            'confidences': list[str],     # Confidence levels per line
            'title': str,                 # Final spectrum title
            'sheet_name': str,            # Name of loaded sheet
            'diagnostics': dict           # Parser diagnostics (raw counts, unknown tokens, etc.)
        }
    
    Raises:
        ValueError: If no valid sheet or spectral rows found
    """
    
    wb = openpyxl.load_workbook(excel_file_path, data_only=True)
    
    if sheet_name:
        ws = wb[sheet_name]
    else:
        ws, header_row, wl_col, int_col, title_col = find_spectral_sheet(wb)
        if ws is None:
            raise ValueError('No sheet with wavelength and intensity columns found')
    
    # Parse spectral rows (reuse existing Cleaned up code.ipynb Cell 4 logic)
    wavelengths = []
    intensities = []
    width_factors = []
    actions_list = []
    confidences = []
    title_candidates = []
    
    raw_descriptor_counts = Counter()
    parsed_descriptor_counts = Counter()
    unknown_descriptor_counts = Counter()
    skipped_masked_lines = 0
    
    # [Populate from existing loader logic in Cleaned up code.ipynb]
    
    if not wavelengths:
        raise ValueError(f'No spectral rows in {ws.title}')
    
    # Resolve spectrum title
    if user_title and user_title.strip():
        spectrum_title = user_title.strip()
    else:
        # Fallback: infer from sheet or candidates
        sheet_title = clean_title(ws.title)
        is_generic = ws.title.strip().lower().startswith('sheet')
        if sheet_title and not is_generic:
            spectrum_title = sheet_title
        elif title_candidates:
            spectrum_title = title_candidates[0]
        else:
            spectrum_title = None  # Will use random code at render time
    
    return {
        'wavelengths': np.array(wavelengths),
        'intensities': np.array(intensities, dtype=float),
        'width_factors': np.array(width_factors, dtype=float),
        'actions': actions_list,
        'confidences': confidences,
        'title': spectrum_title,
        'sheet_name': ws.title,
        'diagnostics': {
            'raw_descriptors': dict(raw_descriptor_counts),
            'parsed_tokens': dict(parsed_descriptor_counts),
            'unknown_tokens': dict(unknown_descriptor_counts),
            'skipped_masked': skipped_masked_lines,
            'total_lines': len(wavelengths)
        }
    }


def list_sheets(excel_file_path):
    """
    List all sheet names in an Excel file.
    
    Args:
        excel_file_path (str): Path to Excel workbook
    
    Returns:
        list[str]: Sheet names
    """
    wb = openpyxl.load_workbook(excel_file_path, data_only=True)
    return [ws.title for ws in wb.worksheets]
```

---

## Module 3: `spectrum/rendering.py`

**Purpose:** Build spectrum arrays and render to plots (dark/light modes).

```python
# spectrum/rendering.py

"""
Spectrum building and rendering functions.
Gaussian core + glow halo with action-driven morphing.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from .utils import generate_random_title


# Profile tightening parameters (from Fresh Notebook.ipynb, validated)
BASE_SIGMA = 0.12          # nm, base Gaussian sigma
BROAD_FACTOR = 1.20        # width multiplier for broad class
BLEND_FACTOR = 0.70        # width multiplier for blend class
BLEND_INTENSITY = 0.95     # optional intensity scaling for blend
GLOW_STRENGTH = 0.14       # halo glow strength multiplier
ACTION_INTENSITY_FACTOR = 0.50  # Broad class intensity reduction


def build_spectrum_array(wavelengths, intensities, width_factors, actions, 
                         wl_min=400, wl_max=700, resolution=4096):
    """
    Build spectrum as continuous intensity array using Gaussian core + glow model.
    
    Per-line morphing:
    - 'line':        narrow core, minimal glow
    - 'broad':       wider core, wider glow
    - 'blend':       narrow core, moderate glow (to simulate blended appearance)
    - 'doublet':     two narrow Gaussians offset ±0.10 nm
    - 'cluster':     three narrow Gaussians offset ±0.12 nm
    - 'band-edge':   asymmetric profile with long tail
    - Other:         standard line treatment
    
    Args:
        wavelengths (np.array): Wavelengths in nm
        intensities (np.array): Intensity values (pre-corrected with multipliers)
        width_factors (np.array): Width multiplier per line
        actions (list[str]): Visual action per line
        wl_min, wl_max (float): Wavelength range in nm
        resolution (int): Number of points in output array
    
    Returns:
        tuple: (wl_array, spectrum_array, component_counts)
               - wl_array: wavelengths for output array
               - spectrum_array: intensity values (0–1 normalized)
               - component_counts: dict of action counts for diagnostics
    """
    
    wl_array = np.linspace(wl_min, wl_max, resolution)
    spectrum = np.zeros_like(wl_array, dtype=float)
    component_counts = {}
    
    for wl, intensity, width_mult, action in zip(wavelengths, intensities, 
                                                   width_factors, actions):
        if wl < wl_min or wl > wl_max:
            continue
        
        action_key = action if action else 'line'
        component_counts[action_key] = component_counts.get(action_key, 0) + 1
        
        # Scale intensity based on broad class
        if 'broad' in action_key.lower():
            intensity *= ACTION_INTENSITY_FACTOR
        
        # Build core (Gaussian)
        sigma_base = BASE_SIGMA
        if 'broad' in action_key.lower():
            sigma = sigma_base * width_mult * BROAD_FACTOR
        elif 'blend' in action_key.lower():
            sigma = sigma_base * width_mult * BLEND_FACTOR
        else:
            sigma = sigma_base * width_mult
        
        core = intensity * np.exp(-0.5 * ((wl_array - wl) / sigma) ** 2)
        
        # Build glow halo
        glow_sigma = sigma * 3.0
        glow = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - wl) / glow_sigma) ** 2)
        
        # Add components based on action
        spectrum += core + glow
        
        if 'doublet' in action_key:
            offset = 0.10
            core_off = intensity * np.exp(-0.5 * ((wl_array - (wl + offset)) / sigma) ** 2)
            glow_off = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - (wl + offset)) / glow_sigma) ** 2)
            spectrum += core_off + glow_off
        
        if 'cluster' in action_key:
            for offset in [-0.12, 0.12]:
                core_off = intensity * np.exp(-0.5 * ((wl_array - (wl + offset)) / sigma) ** 2)
                glow_off = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - (wl + offset)) / glow_sigma) ** 2)
                spectrum += core_off + glow_off
    
    spectrum_normalized = spectrum / (spectrum.max() + 1e-10)
    
    return wl_array, spectrum_normalized, component_counts


def wavelength_to_rgb(wl):
    """
    Convert wavelength (nm) to approximate RGB color.
    
    Args:
        wl (float): Wavelength in nm (typically 400–700)
    
    Returns:
        tuple: (R, G, B) with values 0–1
    """
    if wl < 380 or wl > 750:
        return (0, 0, 0)
    
    if wl < 440:
        r = -(wl - 440) / (440 - 380)
        g, b = 0, 1
    elif wl < 490:
        r, g, b = 0, (wl - 440) / (490 - 440), 1
    elif wl < 510:
        r, g, b = 0, 1, -(wl - 510) / (510 - 490)
    elif wl < 580:
        r, g, b = (wl - 510) / (580 - 510), 1, 0
    elif wl < 645:
        r, g, b = 1, -(wl - 645) / (645 - 580), 0
    else:
        r, g, b = 1, 0, 0
    
    return (r, g, b)


def render_spectrum(spectral_data, dark_mode=True, figsize=(14, 4)):
    """
    Render spectrum as 2D heatmap image using wavelength-to-RGB mapping.
    
    Args:
        spectral_data (dict): Output from load_spectral_data()
        dark_mode (bool): If True, dark background; if False, light background
        figsize (tuple): Figure size (width, height)
    
    Returns:
        matplotlib.figure.Figure: Rendered figure
    """
    
    title = spectral_data['title']
    if not title or title is None:
        title = generate_random_title()
    
    wl_array, spectrum_normalized, component_counts = build_spectrum_array(
        spectral_data['wavelengths'],
        spectral_data['intensities'],
        spectral_data['width_factors'],
        spectral_data['actions']
    )
    
    # Build heatmap: rows = intensity over wavelength, columns = wavelength
    num_rows = 100
    heatmap = np.tile(spectrum_normalized, (num_rows, 1))
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Map each column to its wavelength color
    rgb_image = np.zeros((num_rows, len(wl_array), 3))
    for i, wl in enumerate(wl_array):
        r, g, b = wavelength_to_rgb(wl)
        rgb_image[:, i, :] = [r, g, b]
    
    # Apply intensity profile to brightness
    for i in range(3):
        rgb_image[:, :, i] *= heatmap
    
    ax.imshow(rgb_image, aspect='auto', extent=[wl_array.min(), wl_array.max(), 0, 1])
    
    # Configure axes
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_yticks([])
    
    # Tick marks: major labeled every 50 nm, minor every 10 nm
    major_ticks = np.arange(400, 750, 50)
    minor_ticks = np.arange(400, 750, 10)
    ax.set_xticks(major_ticks, minor=False)
    ax.set_xticks(minor_ticks, minor=True)
    
    # Background color
    if dark_mode:
        ax.set_facecolor('#1a1a1a')
        fig.patch.set_facecolor('#0d0d0d')
        ax.tick_params(colors='white', labelsize=10)
        ax.spines['bottom'].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')
    else:
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        ax.tick_params(colors='black', labelsize=10)
        ax.spines['bottom'].set_color('black')
        ax.xaxis.label.set_color('black')
        ax.title.set_color('black')
    
    plt.tight_layout()
    
    return fig
```

---

## Module 4: `spectrum/utils.py`

**Purpose:** Shared utility functions.

```python
# spectrum/utils.py

"""
Shared utility functions for loading, parsing, and rendering.
"""

import random
import string


def clean_title(text):
    """
    Extract first word from text as title candidate.
    
    Args:
        text: Text value (may be None or numeric)
    
    Returns:
        str or None: First word, or None if empty
    """
    text = str(text).strip() if text is not None else ''
    if not text:
        return None
    return text.split()[0]


def normalize_header(value):
    """
    Normalize column header for comparison.
    
    Args:
        value: Header value
    
    Returns:
        str: Lowercase, whitespace-stripped
    """
    return str(value).strip().lower() if value is not None else ''


def looks_like_number(value):
    """
    Check if a value can be parsed as numeric.
    
    Args:
        value: Value to test
    
    Returns:
        bool: True if numeric
    """
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def generate_random_title():
    """
    Generate a random spectrum title code (e.g., 'Spectrum-4821').
    
    Returns:
        str: Random title in format 'Spectrum-XXXX'
    """
    random_code = ''.join(random.choices(string.digits, k=4))
    return f'Spectrum-{random_code}'
```

---

## Browser Application: `webapp.py`

**Purpose:** Local Flask server for upload, render, and display.

```python
# webapp.py

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
        # Save to temp location
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file.save(tmp.name)
            sheets = list_sheets(tmp.name)
            os.unlink(tmp.name)
        
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
        dark_mode: 'true' or 'false'
    
    Response:
        PNG image data or error JSON
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    sheet_name = request.form.get('sheet', None)
    user_title = request.form.get('title', None)
    dark_mode = request.form.get('dark_mode', 'true').lower() == 'true'
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save to temp location
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            file.save(tmp.name)
            
            # Load spectral data
            spectral_data = load_spectral_data(tmp.name, sheet_name=sheet_name, 
                                                user_title=user_title)
            
            # Render
            fig = render_spectrum(spectral_data, dark_mode=dark_mode)
            
            # Return as PNG
            img_io = io.BytesIO()
            fig.savefig(img_io, format='png', dpi=150, bbox_inches='tight')
            img_io.seek(0)
            plt.close(fig)
            
            os.unlink(tmp.name)
            
            return send_file(img_io, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## Browser Template: `templates/index.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Spectrum Renderer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input[type="file"],
        input[type="text"],
        select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
        }
        input[type="file"]:focus,
        input[type="text"]:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .checkbox-group {
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }
        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 0;
            cursor: pointer;
        }
        input[type="checkbox"] {
            width: auto;
            cursor: pointer;
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        #result {
            margin-top: 30px;
            text-align: center;
        }
        #result img {
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .error {
            color: #d32f2f;
            background: #ffebee;
            padding: 12px;
            border-radius: 6px;
            margin-top: 15px;
            font-size: 14px;
        }
        .loading {
            text-align: center;
            color: #667eea;
            margin-top: 15px;
            font-size: 14px;
        }
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Spectrum Renderer</h1>
        <p class="subtitle">Upload your Excel workbook and render spectra with NIST descriptor support</p>
        
        <form id="renderForm">
            <div class="form-group">
                <label for="file">Excel File *</label>
                <input type="file" id="file" name="file" accept=".xlsx,.xls" required>
            </div>
            
            <div class="form-group">
                <label for="sheet">Sheet Name (leave blank for auto-detect)</label>
                <select id="sheet" name="sheet">
                    <option value="">Auto-detect</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="title">Spectrum Title (leave blank for random code)</label>
                <input type="text" id="title" name="title" placeholder="e.g., Oxygen NIST">
            </div>
            
            <div class="form-group">
                <label>Render Options</label>
                <div class="checkbox-group">
                    <label>
                        <input type="checkbox" name="dark_mode" value="dark" checked>
                        Dark Mode
                    </label>
                </div>
            </div>
            
            <button type="submit">Render Spectrum</button>
        </form>
        
        <div id="result"></div>
    </div>

    <script>
        const fileInput = document.getElementById('file');
        const sheetSelect = document.getElementById('sheet');
        const renderForm = document.getElementById('renderForm');
        const resultDiv = document.getElementById('result');

        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/sheets', { method: 'POST', body: formData });
                const data = await response.json();
                
                sheetSelect.innerHTML = '<option value="">Auto-detect</option>';
                data.sheets.forEach(sheet => {
                    const option = document.createElement('option');
                    option.value = sheet;
                    option.textContent = sheet;
                    sheetSelect.appendChild(option);
                });
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Error loading sheets: ${error.message}</div>`;
            }
        });

        renderForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const file = fileInput.files[0];
            if (!file) {
                resultDiv.innerHTML = '<div class="error">Please select a file</div>';
                return;
            }

            const formData = new FormData(renderForm);
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Rendering...</div>';

            try {
                const response = await fetch('/api/render', { method: 'POST', body: formData });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Unknown error');
                }

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                resultDiv.innerHTML = `<img src="${url}" alt="Rendered Spectrum">`;
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
```

---

## Integration Back to Notebook: `Fresh Notebook.ipynb` Updates

**Changes needed:**

1. **New Cell (after imports):** Import modules
   ```python
   import sys
   sys.path.insert(0, '/path/to/spectrum')  # Adjust to your project folder
   
   from spectrum.loader import load_spectral_data
   from spectrum.rendering import render_spectrum
   ```

2. **Replace Loader Cell:** Replace existing loader (cell 4) with:
   ```python
   # User input for title and file
   excel_file = "[YOUR_EXCEL_FILE_PATH]"
   user_title_input = ""  # User types here or leave blank for random
   
   # Load spectral data
   spectral_data = load_spectral_data(excel_file, user_title=user_title_input or None)
   
   # Diagnostics
   print(f"Loaded from: {spectral_data['sheet_name']}")
   print(f"Title: {spectral_data['title']}")
   print(f"Total lines: {spectral_data['diagnostics']['total_lines']}")
   if spectral_data['diagnostics']['raw_descriptors']:
       print(f"Raw descriptors: {spectral_data['diagnostics']['raw_descriptors']}")
   if spectral_data['diagnostics']['parsed_tokens']:
       print(f"Parsed tokens: {spectral_data['diagnostics']['parsed_tokens']}")
   if spectral_data['diagnostics']['unknown_tokens']:
       print(f"Unknown tokens: {spectral_data['diagnostics']['unknown_tokens']}")
   ```

3. **Replace Dark Render Cell:** 
   ```python
   fig = render_spectrum(spectral_data, dark_mode=True)
   plt.show()
   ```

4. **Replace Light Render Cell:**
   ```python
   fig = render_spectrum(spectral_data, dark_mode=False)
   plt.show()
   ```

---

## Setup Instructions

### 1. Create Module Structure
```
mkdir spectrum
touch spectrum/__init__.py
touch spectrum/nist_descriptors.py
touch spectrum/loader.py
touch spectrum/rendering.py
touch spectrum/utils.py
touch webapp.py
mkdir templates
touch templates/index.html
```

### 2. Populate Modules
Paste code from sections above into corresponding files.

### 3. Install Dependencies (if needed)
```bash
pip install flask openpyxl numpy matplotlib
```

### 4. Run Browser App
```bash
cd /path/to/project
python webapp.py
```
Then open `http://localhost:5000` in your browser.

### 5. Update Fresh Notebook
Replace loader and render cells with imports and calls to `load_spectral_data()` and `render_spectrum()`.

---

## Verification Checklist

- [ ] **Module imports:** Verify no circular imports; each module imports only dependencies needed
- [ ] **Loader function:** `load_spectral_data()` accepts file path, sheet name, user title; returns dict with all spectral data + diagnostics
- [ ] **Rendering function:** `render_spectrum()` accepts spectral_data dict and dark_mode bool; returns matplotlib Figure
- [ ] **Title logic:** User entry respected if non-empty; random code generated if blank or None
- [ ] **Browser app routes:**
  - GET `/` serves HTML form
  - POST `/api/sheets` returns sheet list
  - POST `/api/render` returns PNG image
- [ ] **HTML form:** File upload, sheet selector (auto-populated), title input, dark/light toggle, render button
- [ ] **Notebook integration:** Fresh Notebook.ipynb updated with module imports; loader and render cells simplified
- [ ] **Diagnostic output:** Loader prints descriptor counts, unknown tokens, action counts (parity with original notebook)
- [ ] **Visual parity:** Dark/light renders from modules match output from Fresh Notebook.ipynb (same parameters)
- [ ] **End-to-end test:** Upload Excel file via browser, enter title, toggle dark/light, verify output matches notebook

---

## File Layout Summary

```
project_root/
├── spectrum/
│   ├── __init__.py
│   ├── nist_descriptors.py       (Descriptor constants + parsing)
│   ├── loader.py                 (Load Excel, build spectral_data dict)
│   ├── rendering.py              (Build spectrum array, render to plot)
│   └── utils.py                  (Shared utilities, random title gen)
├── templates/
│   └── index.html                (Upload form, file upload, render UI)
├── webapp.py                      (Flask server)
├── Fresh Notebook.ipynb          (Updated to use modules)
├── Cleaned up code.ipynb         (Working reference, can be archived)
└── NIST Descriptors Reference.ipynb  (Semantic reference)
```

---

**Next Steps:**
1. Copy this blueprint into a file (e.g., `IMPLEMENTATION.md`)
2. Populate each module file with the code snippets above
3. Test module imports in a scratch notebook cell
4. Run Flask webapp and test upload → render workflow
5. Update Fresh Notebook.ipynb to use modules
6. Verify visual and diagnostic parity between notebook and webapp

Similar code found with 1 license type