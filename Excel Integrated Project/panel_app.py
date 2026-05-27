"""
Minimal HoloViz + Datashader panel app for interactive spectrum inspection.
Usage: call `create_app(wb_path)` from `panel_server.py` or run panel_server.py

Features:
- Loads first two columns from an Excel file (wavelength, intensity)
- Datashader-rendered line for large-data performance
- Button to run peak detection (server-side) and overlay markers
"""

import os
import pandas as pd
import numpy as np
import holoviews as hv
from holoviews.operation.datashader import datashade, shade
import panel as pn
hv.extension('bokeh')
pn.extension()

from annotator import detect_peaks_from_arrays


def _load_dataframe(path):
    if not path or not os.path.exists(path):
        return None
    # support CSV or Excel
    try:
        if str(path).lower().endswith('.csv'):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path, engine='openpyxl')
    except Exception:
        return None
    if df.shape[1] < 1:
        return None
    return df


def create_app(wb_path=None):
    df = _load_dataframe(wb_path)
    if df is None:
        return pn.Column(pn.pane.Markdown('No valid workbook found.'), width=900)
    # provide column selection widgets because structure may vary
    cols = list(df.columns)

    def auto_detect_columns(df):
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols:
            # try converting columns to numeric
            conv = [c for c in cols if pd.to_numeric(df[c], errors='coerce').notna().sum() > 0]
            num_cols = conv
        # heuristic: wavelength likely in typical nm ranges (100-2000)
        wl_candidate = None
        inten_candidate = None
        for c in num_cols:
            vals = pd.to_numeric(df[c], errors='coerce').dropna()
            if vals.size == 0:
                continue
            mn, mx = vals.min(), vals.max()
            # prefer column with values in nm range
            if 100.0 <= mn <= 4000.0 and 100.0 <= mx <= 4000.0 and wl_candidate is None:
                wl_candidate = c
        if wl_candidate is None and num_cols:
            wl_candidate = num_cols[0]
        # intensity likely non-negative and has higher variance
        best = None
        best_var = -1
        for c in num_cols:
            vals = pd.to_numeric(df[c], errors='coerce').dropna()
            if vals.size == 0:
                continue
            var = float(vals.var())
            if var > best_var:
                best_var = var
                best = c
        inten_candidate = best if best is not None else (num_cols[1] if len(num_cols) > 1 else num_cols[0])
        return wl_candidate, inten_candidate

    suggested_wl, suggested_int = auto_detect_columns(df)

    wl_select = pn.widgets.Select(name='Wavelength column', options=cols, value=suggested_wl)
    int_select = pn.widgets.Select(name='Intensity column', options=cols, value=suggested_int)

    info = pn.pane.Markdown('Select which columns represent wavelength and intensity, then press `Apply`.')
    apply_btn = pn.widgets.Button(name='Apply selection', button_type='primary')

    def get_curve():
        try:
            wl = pd.to_numeric(df[wl_select.value], errors='coerce').to_numpy(dtype=float)
            inten = pd.to_numeric(df[int_select.value], errors='coerce').to_numpy(dtype=float)
            # drop NaNs
            mask = ~np.isnan(wl) & ~np.isnan(inten)
            wl = wl[mask]
            inten = inten[mask]
        except Exception:
            return hv.Curve([], 'Wavelength (nm)', 'Intensity')
        return hv.Curve((wl, inten), 'Wavelength (nm)', 'Intensity')

    dmap = hv.DynamicMap(lambda: datashade(get_curve(), aggregator='mean', cmap='lightblue')).opts(width=1000, height=360)

    peak_store = pn.State([])

    def run_detection(event=None):
        # use current selection
        curve = get_curve()
        try:
            xs = np.array(curve.data[0]) if hasattr(curve, 'data') else np.array([])
            ys = np.array(curve.data[1]) if hasattr(curve, 'data') else np.array([])
        except Exception:
            xs = np.array([]); ys = np.array([])
        peaks = detect_peaks_from_arrays(xs, ys)
        peak_store.param.set_param(value=peaks)

    def peaks_pane():
        peaks = peak_store.value
        if not peaks:
            return pn.pane.Markdown('No peaks detected')
        rows = ['- {} nm — {}'.format(p['wavelength_nm'], p['intensity']) for p in peaks]
        return pn.pane.Markdown('\n'.join(rows))

    detect_btn = pn.widgets.Button(name='Detect Peaks', button_type='primary')
    detect_btn.on_click(run_detection)

    # Overlay scatter when peaks available
    def overlay():
        peaks = peak_store.value
        if not peaks:
            return hv.NdOverlay({})
        xs = [p['wavelength_nm'] for p in peaks]
        ys = [p['intensity'] for p in peaks]
        pts = hv.Points((xs, ys), 'Wavelength (nm)', 'Intensity')
        return pts.opts(color='red', size=6)

    overlay_dmap = hv.DynamicMap(lambda: overlay())
    layered = (dmap * overlay_dmap).opts(toolbar='above')

    controls = pn.Column(info, pn.Row(wl_select, int_select, apply_btn), pn.Spacer(height=6), detect_btn)

    layout = pn.Column(
        pn.Row(pn.pane.Markdown(f'**File:** {os.path.basename(wb_path)}'), pn.Spacer(width=20), controls),
        pn.Row(pn.panel(layered), pn.Column(pn.pane.Markdown('**Detected Peaks**'), pn.bind(peaks_pane))),
    )

    return layout


if __name__ == '__main__':
    app = create_app('he test.xlsx')
    pn.serve(app, port=5006, show=True)
