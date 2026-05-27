"""
Excel-integrated peak annotator (xlwings)

Usage:
- From Excel: assign a button/macro to run
  RunPython("import annotator; annotator.run()")

- From command line for testing:
  python -m annotator

This script reads a selected two-column range (wavelength, intensity),
detects peaks, plots the spectrum with annotations, saves the image to
`outputs/annotated.png` and inserts it into the active sheet.
"""

import os
import subprocess
import sys
import math
import json
import numpy as np
import matplotlib.pyplot as plt

try:
    import xlwings as xw
except Exception:
    xw = None


def detect_peaks_from_arrays(wl, inten, sensitivity='medium'):
    """Detect peaks given wavelength and intensity arrays.
    Returns list of dicts: {'wavelength_nm':, 'intensity':, 'index':}
    """
    wl = np.asarray(wl)
    inten = np.asarray(inten)
    if wl.size == 0 or inten.size == 0:
        return []

    # Interpolate to uniform grid for robust peak detection
    resolution = 4096
    wl_min, wl_max = float(np.min(wl)), float(np.max(wl))
    wl_grid = np.linspace(wl_min, wl_max, resolution)
    inten_grid = np.interp(wl_grid, wl, inten)

    raw_max = np.max(inten_grid) if inten_grid.size else 0.0

    peaks_idx = np.array([], dtype=int)
    try:
        from scipy.signal import find_peaks, peak_prominences
        # Medium sensitivity default
        height_thr = raw_max * 0.02
        peaks, props = find_peaks(inten_grid, height=height_thr, distance=1)
        if peaks.size:
            prominences = peak_prominences(inten_grid, peaks)[0]
            prom_thr = np.percentile(prominences, 40) if prominences.size else 0.0
            peaks = peaks[prominences >= prom_thr]
        peaks_idx = np.sort(peaks)
    except Exception:
        # Simple local maxima + threshold
        s = inten_grid
        if s.size >= 3:
            candidates = np.where((s[1:-1] > s[:-2]) & (s[1:-1] > s[2:]))[0] + 1
            if candidates.size:
                height_thr = raw_max * 0.02
                peaks_idx = np.sort(candidates[s[candidates] >= height_thr])
            else:
                peaks_idx = np.array([], dtype=int)

    # Map detected grid indices back to nearest original input wavelength indices
    detected = []
    for p in peaks_idx:
        detected_wl = float(wl_grid[p])
        # find nearest input index
        diffs = np.abs(wl - detected_wl)
        if diffs.size:
            i = int(np.argmin(diffs))
            detected.append({'index': i, 'wavelength_nm': float(wl[i]), 'intensity': float(inten[i])})

    # Deduplicate by input index (keep highest intensity if collision)
    by_idx = {}
    for d in detected:
        idx = d['index']
        if idx not in by_idx or d['intensity'] > by_idx[idx]['intensity']:
            by_idx[idx] = d
    out = [by_idx[k] for k in sorted(by_idx.keys())]
    return out


def make_annotated_plot(wl, inten, peaks, out_path='outputs/annotated.png'):
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    try:
        plt.style.use('seaborn-darkgrid')
    except Exception:
        plt.style.use('default')
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(wl, inten, color='tab:blue', linewidth=1.25)
    ax.set_xlabel('Wavelength (nm)')
    ax.set_ylabel('Intensity')
    ax.set_title('Annotated Spectrum')

    # mark peaks
    for p in peaks:
        x = p['wavelength_nm']
        y = p['intensity']
        ax.plot(x, y, marker='v', color='red')
        label = f"{x:.5f} nm\n{y:.4g}"
        ax.annotate(label, xy=(x, y), xytext=(0, 8), textcoords='offset points',
                    ha='center', va='bottom', fontsize=8, color='black', bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8))

    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def run(book=None, sheet=None):
    """Entry point: reads selection or named ranges and inserts annotated plot.
    If xlwings is unavailable, prints instructions.
    """
    if xw is None:
        print('xlwings not installed. To run from Excel, install xlwings and use RunPython.')
        return

    # If Book not provided, use caller (when called from Excel)
    if book is None:
        try:
            book = xw.Book.caller()
        except Exception:
            # fallback to active workbook
            app = xw.apps.active
            if app is None:
                print('No active Excel app found.')
                return
            book = app.books.active

    if sheet is None:
        sht = book.sheets.active
    else:
        sht = sheet

    # Check selection: expect two columns (wavelength, intensity)
    sel = sht.api.Selection
    try:
        rng = xw.Range(sel.address)
    except Exception:
        rng = sht.range('A1').expand()

    vals = rng.options(ndim=2).value
    # if selection is a single column, try to use named ranges
    if not vals or len(vals) == 0:
        print('Selection empty. Please select a two-column range (wavelength, intensity).')
        return

    arr = np.array(vals)
    if arr.ndim == 1:
        # single row/col: attempt to use named ranges
        try:
            wl = [c[0] for c in book.names['Wavelengths'].refers_to_range.value]
            inten = [c[0] for c in book.names['Intensities'].refers_to_range.value]
        except Exception:
            print('Could not read data from selection or named ranges.')
            return
    else:
        # assume first two columns
        if arr.shape[1] < 2:
            print('Selection must contain at least two columns: wavelength and intensity.')
            return
        wl = arr[:, 0].astype(float)
        inten = arr[:, 1].astype(float)

    peaks = detect_peaks_from_arrays(wl, inten)
    out_path = make_annotated_plot(wl, inten, peaks, out_path='outputs/annotated.png')

    # Insert picture into sheet (top-left cell below data)
    pic_top = rng.row + rng.shape[0] + 1
    try:
        sht.pictures.add(out_path, left=sht.range((pic_top, 1)).left, top=sht.range((pic_top, 1)).top)
        # Also write detected peaks to a JSON in outputs
        with open('outputs/detected_from_excel.json', 'w') as jf:
            json.dump(peaks, jf, indent=2)
        print('Inserted annotated image and saved detected peaks to outputs/detected_from_excel.json')
    except Exception as e:
        print('Saved annotated image to', out_path, 'but failed to insert into sheet:', e)


def launch_panel(book=None):
    """Launch the Panel datashader app in a background process and open the browser.
    If called from Excel, attempts to use the workbook path; otherwise uses cwd he test.xlsx.
    """
    # determine workbook path
    wb_path = None
    try:
        if book is not None:
            wb_path = getattr(book, 'fullname', None) or getattr(book, 'name', None)
    except Exception:
        wb_path = None

    # prefer file under current project if no workbook provided
    if not wb_path or not os.path.exists(wb_path):
        candidate = os.path.join(os.getcwd(), 'he test.xlsx')
        wb_path = candidate if os.path.exists(candidate) else None

    # find python executable: prefer .venv if present
    venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable

    script = os.path.join(os.getcwd(), 'panel_server.py')
    if not os.path.exists(script):
        print('panel_server.py not found in project. Cannot launch interactive app.')
        return

    cmd = [python_exe, script]
    if wb_path:
        cmd.append(wb_path)

    try:
        # start detached background process
        subprocess.Popen(cmd, cwd=os.getcwd())
        print('Launched interactive Panel app (should open in your browser).')
    except Exception as e:
        print('Failed to launch Panel app:', e)


def export_selection_to_csv(book=None, sheet=None, out_path='outputs/selection.csv'):
    """Export the current Excel selection (or named ranges) to CSV and return the path.
    This keeps Excel light — the Panel app can load the CSV and ask which columns to use.
    """
    if xw is None:
        raise RuntimeError('xlwings not available')

    # determine workbook and sheet
    try:
        if book is None:
            book = xw.Book.caller()
    except Exception:
        app = xw.apps.active
        if app is None:
            raise RuntimeError('No active Excel app')
        book = app.books.active

    if sheet is None:
        sht = book.sheets.active
    else:
        sht = sheet

    sel = sht.api.Selection
    try:
        rng = xw.Range(sel.address)
    except Exception:
        rng = sht.range('A1').expand()

    vals = rng.options(ndim=2).value
    if not vals:
        raise RuntimeError('Selection empty')

    import pandas as _pd
    df = _pd.DataFrame(vals)
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    df.to_csv(out_path, index=False, header=False)
    return os.path.abspath(out_path)


def launch_with_selection(book=None):
    """Export selection and launch Panel pointed at the exported CSV."""
    try:
        path = export_selection_to_csv(book=book)
    except Exception as e:
        print('Failed to export selection:', e)
        return

    # call panel_server with CSV path
    venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    script = os.path.join(os.getcwd(), 'panel_server.py')
    if not os.path.exists(script):
        print('panel_server.py not found; cannot launch interactive app.')
        return
    try:
        subprocess.Popen([python_exe, script, path], cwd=os.getcwd())
        print('Launched Panel app with selection.')
    except Exception as e:
        print('Failed to launch Panel app:', e)


if __name__ == '__main__':
    # CLI test runner: open a workbook named he test.xlsx in parent folder
    import sys as _sys
    print('Running annotator in CLI mode (will look for he test.xlsx in parent folder).')
    wb_path = _sys.argv[1] if len(_sys.argv) > 1 else '../he test.xlsx'
    if os.path.exists(wb_path):
        if xw is None:
            print('xlwings not installed; CLI mode requires xlwings to open workbook.'); _sys.exit(1)
        book = xw.Book(wb_path)
        run(book=book)
        book.save()
        book.close()
    else:
        print('No workbook found at', wb_path)
