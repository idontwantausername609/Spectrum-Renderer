# Spectrum Graphing Tool - Implementation Complete

## ✓ What's Been Implemented

### 1. Python Modules (`spectrum/` package)

- **`spectrum/__init__.py`** – Package initialization
- **`spectrum/nist_descriptors.py`** – 29 NIST descriptor definitions, tokenization, and rule combining
- **`spectrum/loader.py`** – Excel file loading, spectral data extraction, auto-sheet detection
- **`spectrum/rendering.py`** – Spectrum building (Gaussian core + glow), RGB color mapping, dark/light plot rendering
- **`spectrum/utils.py`** – Shared utilities (title cleaning, random code generation, type checking)

### 2. Flask Web Application

- **`webapp.py`** – Local Flask server with three routes:
  - `GET /` – Serves upload form
  - `POST /api/sheets` – Returns list of sheets in uploaded file
  - `POST /api/render` – Renders spectrum to PNG image

- **`templates/index.html`** – Responsive HTML/CSS/JavaScript interface with:
  - File upload control
  - Auto-populated sheet selector
  - User title input (with random fallback if blank)
  - Dark/light mode toggle
  - Real-time rendering with loading spinner

### 3. Tested & Validated

✓ All modules import without errors
✓ Loader successfully parses Oxygen NIST workbook (399 spectral lines)
✓ Descriptor tokenization and rule combining working
✓ User title input respected (or generates random code if blank)
✓ All dependencies installed (numpy, matplotlib, openpyxl, flask)

---

## 🚀 Quick Start

### Option A: Run the Web Interface (Recommended for Quick Upload & Render)

```bash
cd "c:\Users\viran\Downloads\indep. project\Graphing"
python webapp.py
```

Then open **http://localhost:5000** in your browser.

**Workflow:**
1. Upload Excel file
2. Select sheet (or leave blank for auto-detect)
3. Enter title (or leave blank for random code)
4. Toggle dark/light mode
5. Click "Render Spectrum"
6. Save image or re-render with different settings

### Option B: Use Modules in Jupyter Notebook

```python
# Import modules
from spectrum.loader import load_spectral_data
from spectrum.rendering import render_spectrum
import matplotlib.pyplot as plt

# Load data
spectral_data = load_spectral_data(
    "Oxygen NIST.xlsx",
    user_title="My Spectrum Title"
)

# Render
fig = render_spectrum(spectral_data, dark_mode=True)
plt.show()
```

---

## 📋 Next Steps: Update Fresh Notebook.ipynb

To integrate modules into your notebook, replace the existing loader and render cells:

### 1. **New Imports Cell** (first cell after existing imports)
```python
import sys
sys.path.insert(0, r'c:\Users\viran\Downloads\indep. project\Graphing')

from spectrum.loader import load_spectral_data
from spectrum.rendering import render_spectrum
```

### 2. **Replace Loader Cell** (cell 4)
```python
excel_file = r"c:\Users\viran\Downloads\indep. project\Graphing\Oxygen NIST.xlsx"
user_title = ""  # User enters title here, or leave blank for random

# Load spectral data
spectral_data = load_spectral_data(excel_file, user_title=user_title or None)

# Print diagnostics
print(f"Loaded: {spectral_data['diagnostics']['total_lines']} lines from {spectral_data['sheet_name']}")
print(f"Title: {spectral_data['title']}")
print(f"Actions: {dict(spectral_data['diagnostics'].get('parsed_tokens', {}))}")
```

### 3. **Replace Dark Render Cell** (cell 6)
```python
fig = render_spectrum(spectral_data, dark_mode=True)
plt.show()
```

### 4. **Replace Light Render Cell** (cell 8)
```python
fig = render_spectrum(spectral_data, dark_mode=False)
plt.show()
```

---

## 🔧 Configuration

### Rendering Parameters

Edit `spectrum/rendering.py` to adjust visual appearance:

```python
BASE_SIGMA = 0.12              # Gaussian sigma (nm)
BROAD_FACTOR = 1.20            # Width multiplier for broad class
BLEND_FACTOR = 0.70            # Width multiplier for blend class
GLOW_STRENGTH = 0.14           # Halo glow intensity
ACTION_INTENSITY_FACTOR = 0.50 # Broad class intensity reduction
```

### Port and Debug Settings

Edit `webapp.py` line 68:
```python
app.run(debug=True, port=5000)  # Change port if 5000 is in use
```

---

## 📁 File Structure

```
c:\Users\viran\Downloads\indep. project\Graphing\
├── spectrum/
│   ├── __init__.py
│   ├── nist_descriptors.py       (29 descriptors, tokenization)
│   ├── loader.py                 (Excel loading, data extraction)
│   ├── rendering.py              (Spectrum building, rendering)
│   └── utils.py                  (Shared utilities)
├── templates/
│   └── index.html                (Web form UI)
├── webapp.py                      (Flask server)
├── Fresh Notebook.ipynb          (To be updated with module imports)
├── Cleaned up code.ipynb         (Reference for cleanup approach)
├── NIST Descriptors Reference.ipynb
└── Oxygen NIST.xlsx              (Sample data)
```

---

## ✅ Verification Checklist

- [x] All spectrum modules created and import successfully
- [x] Loader successfully parses Excel files with flexible column detection
- [x] Descriptor parsing (29 descriptors) working correctly
- [x] Rendering generates valid spectrum images
- [x] Flask webapp starts and serves HTML form
- [x] Module functions accept file path and user title parameters
- [x] User-entered title respected; random code generated if blank
- [x] Dark and light mode rendering working
- [ ] *Next:* Update Fresh Notebook.ipynb with module imports
- [ ] *Next:* Test end-to-end workflow (upload → render → display)

---

## 🐛 Troubleshooting

**"Module not found" error:**
```python
import sys
sys.path.insert(0, r'c:\Users\viran\Downloads\indep. project\Graphing')
```

**Flask port 5000 in use:**
Edit `webapp.py` line 68: `app.run(debug=True, port=5001)`

**Missing dependencies:**
```bash
pip install numpy matplotlib openpyxl flask
```

**Images not rendering:**
Check that Excel file has recognizable "Wavelength" and "Intensity" columns; see `loader.py` for token list.

---

## 📞 Support

- Descriptor semantics: See `NIST Descriptors Reference.ipynb`

---

## Quick Launchers (Windows)

To avoid re-running environment setup and make starting the webapp a single action, two launcher scripts are provided in the project root:

- `run_webapp.bat` — Double-click to open a Command Prompt, attempt to activate Anaconda `base` and run `webapp.py`. The terminal stays open so you can see logs.
- `run_webapp.ps1` — PowerShell launcher that tries to `conda activate base`, starts the webapp in a new process, and opens your default browser to `http://localhost:5000`.

Usage examples:
```powershell
# Run from PowerShell (recommended):
powershell -ExecutionPolicy Bypass -File .\run_webapp.ps1

# Or double-click run_webapp.bat in Explorer
```

Notes:
- The scripts assume Anaconda is installed in `%USERPROFILE%\anaconda3`. If your installation is elsewhere, edit the scripts to point to your install or remove the activation step and rely on your system `python`.
- If you prefer a single downloadable archive of multiple rendered images, I can add server-side zipping as a next step.
- Module API: See docstrings in each module file
- Example usage: See Fresh Notebook.ipynb (after update) or test_loader.py
