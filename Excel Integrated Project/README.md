xlwings Peak Annotator
======================

A small xlwings-based helper to detect peaks from a two-column Excel range (wavelength, intensity) and insert an annotated plot back into the workbook.

Quickstart
----------
1. Create and activate a Python environment (recommend venv or conda) and install requirements:

```bash
python -m pip install -r requirements.txt
```

2. Install the xlwings add-in (makes `RunPython` available in Excel):

```powershell
xlwings addin install
```

3. Open Excel, open your workbook containing two columns (wavelength, intensity). Select the two columns or place the cursor inside the table.

4. Add a button / macro that calls:

```
RunPython("import annotator; annotator.run()")
```

Or run from Python for testing:

```bash
python -m annotator
```

Files
-----
- `annotator.py`: main code. Reads selection or named ranges `Wavelengths`/`Intensities`, detects peaks, creates annotated PNG, and inserts image into the active sheet.
- `requirements.txt`: dependencies
- `outputs/`: folder where annotated images are saved.

Notes
-----
- Detection uses SciPy `find_peaks` if available, with medium sensitivity (height ~2% of max, prominence filtering). Falls back to a NumPy local-max approach if SciPy is unavailable.
- The script preserves and annotates the original input intensities.

If you want, I can now run and test this scaffold with your `he test.xlsx` (in a copied workspace) and produce an annotated workbook/image. Otherwise, I can continue adding a sample Excel workbook with a pre-bound button.

Interactive HoloViz prototype
-----------------------------
I added a minimal HoloViz + Datashader prototype (`panel_app.py`) and a launcher (`panel_server.py`).

To run the interactive server (recommended inside the `.venv`):

```powershell
.\.venv\Scripts\python panel_server.py "he test.xlsx"
```

From Excel you can start the server with:

```
RunPython("import annotator; annotator.launch_panel()")
```

This opens a browser UI that uses Datashader for high-performance rendering and runs peak detection server-side. See `requirements.txt` for additional packages.
