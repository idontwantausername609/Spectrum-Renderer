import re
import importlib
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import utils


try:
    nist_helper = importlib.import_module("nist_helper")
except Exception:
    try:
        from . import nist_helper
    except Exception as e:
        print("Warning: NIST descriptor handler unavailable — falling back to default rendering. Error:", e)
        nist_helper = None

# =======================================================================
# Specifically for handling NIST Descriptors
# =======================================================================

def parse_nist_intensity(raw_value):
    """
    Parse a NIST intensity cell that may include descriptor characters.

    Returns:
        (numeric_value_or_nan, descriptor_string)
    """
    if pd.isna(raw_value):
        return (np.nan, "")
    s = str(raw_value).strip()
    m = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', s)
    if not m:
        return (np.nan, s)
    try:
        num = float(m.group(0))
    except Exception:
        num = np.nan
    before = s[:m.start()].strip()
    after = s[m.end():].strip()
    descriptor = (before + " " + after).strip()
    descriptor = re.sub(r'[\s,]+', ' ', descriptor)
    return (num, descriptor)

def clean_nist_row(wavelength_str, rel_int_str):
    """
    Cleans NIST formatting flags like '*', 'bl', and spaces.
    Force-casts numeric types to string first to handle clean Excel data.
    Returns (float wavelength, float intensity) or (None, None) if invalid.
    """
    try:
        # Convert any raw floats/ints from Excel safely into text strings
        w_clean = str(wavelength_str).replace('*', '').replace('bl', '').strip()
        i_clean = str(rel_int_str).replace('*', '').replace('bl', '').replace('?', '').strip()
        
        # Check for empty cells or pandas NaN strings
        if not w_clean or w_clean.lower() == 'nan':
            return None, None
            
        # Extract numeric value for intensity
        # Handles cases where intensity might be a clean integer/float or a string like "9*"
        intensity = 0.0
        if i_clean and i_clean.lower() != 'nan':
            # Remove anything that isn't a digit or a decimal point
            i_numeric = ''.join(c for c in i_clean if c.isdigit() or c == '.')
            if i_numeric:
                intensity = float(i_numeric)
                
        return float(w_clean), intensity
    except ValueError:
        return None, None

def nist_descriptor_adjustments():
    """
    Intensity-only multipliers from the NIST descriptor reference.
    This is safe for your aesthetics because it does not change the renderer style,
    only the brightness input values.
    """
    return {
        '*': 1.0,
        ':': 1.0,
        '-': 0.8,
        'a': 0.5,
        'b': 1.0,
        'bl': 1.5,
        'B': 1.0,
        'c': 1.0,
        'd': 1.0,
        'D': 1.0,
        'E': 0.9,
        'f': 1.0,
        'g': 1.0,
        'G': 1.0,
        'H': 0.7,
        'h': 1.0,
        'hfs': 1.0,
        'i': 0.6,
        'j': 1.0,
        'l': 1.0,
        'm': 0.0,
        'p': 0.8,
        'q': 1.0,
        'r': 1.0,
        's': 1.0,
        't': 0.7,
        'u': 0.75,
        'w': 1.0,
        'x': 1.0,
    }

def nist_to_dataframe(df_raw, wavelength_candidates=None, intensity_candidates=None, apply_descriptor_adjustments=False):
    if wavelength_candidates is None:
        wavelength_candidates = ["Observed", "Observed Wavelength", "obs", "wavelength", "lambda", "wl", "wavelength_nm", "lambda_nm", "nm"]
    if intensity_candidates is None:
        intensity_candidates = ["Rel. Int.", "Relative Intensity", "Rel Int", "Relative", "Intensity", "A", "Aki", "gA", "gf", "weighted f", "f", "Intensity/Counts", "value"]

    wl_col = utils.resolve_column(df_raw, wavelength_candidates, "wavelength")
    try:
        int_col = utils.resolve_column(df_raw, intensity_candidates, "intensity")
    except KeyError:
        int_col = None

    out_rows = []
    if int_col is None:
        # no intensities -> unit intensity, unit width
        for _, row in df_raw.iterrows():
            out_rows.append({"nm": pd.to_numeric(row[wl_col], errors="coerce"), "Grey Val": 1.0, "Width_Mult": 1.0})
    else:
        parsed = df_raw[int_col].apply(parse_nist_intensity)
        for i, (_, row) in enumerate(df_raw.iterrows()):
            nm = pd.to_numeric(row[wl_col], errors="coerce")
            val, desc = parsed.iloc[i]
            if pd.isna(nm) or pd.isna(val):
                continue
            intensity_mult = 1.0
            width_mult = 1.0
            include = True
            if nist_helper is not None and desc:
                # token-match longest-first from helper if available
                keys = getattr(nist_helper, "_DESCRIPTOR_KEYS_SORTED", None)
                tokens = []
                if keys:
                    for k in keys:
                        if k and k in desc:
                            tokens.append(k)
                else:
                    # fallback: split descriptor into chars/words
                    tokens = [t for t in re.split(r'[\s,]+', desc) if t]
                eff = nist_helper.compute_descriptor_effects(tokens)
                include = eff.get("include", True)
                intensity_mult = eff.get("intensity_multiplier", 1.0)
                width_mult = eff.get("width_multiplier", 1.0)
            if not include:
                continue
            adj_val = val * intensity_mult if apply_descriptor_adjustments else val
            out_rows.append({"nm": nm, "Grey Val": adj_val, "Width_Mult": width_mult})

    out = pd.DataFrame(out_rows)
    if out.empty:
        return out

    out = out.dropna(subset=["nm", "Grey Val"]).sort_values("nm").reset_index(drop=True)

    vmin = out["Grey Val"].min()
    vmax = out["Grey Val"].max()
    if vmax - vmin == 0 or np.isnan(vmax - vmin):
        out["Grey Val"] = 1.0
    else:
        out["Grey Val"] = (out["Grey Val"] - vmin) / (vmax - vmin)

    # keep Width_Mult (default 1.0) for rendering width scaling
    if "Width_Mult" not in out.columns:
        out["Width_Mult"] = 1.0

    return out

def extract_and_sanitize_data(data_df, nm_col, intensity_col, x_min, x_max):
    """
    Cleans raw dataframe strings, extracts intensities, binds doublets/triplets
    by 4-decimal rounding, and normalizes them uniformly via exposure compression.
    """
    df_working = data_df.copy()
    
    # Format to uniform string matrix structures
    df_working['_clean_nm'] = df_working[nm_col].astype(str).str.replace('*', '', regex=False).str.replace('bl', '', regex=False).str.strip()
    df_working['_clean_int'] = df_working[intensity_col].astype(str).str.replace('*', '', regex=False).str.replace('bl', '', regex=False).str.replace('?', '', regex=False).str.strip()
    df_working['_clean_nm'] = pd.to_numeric(df_working['_clean_nm'], errors='coerce')

    # Parse and extract core numeric values
    def inline_extractor(val_str):
        if not val_str or val_str.lower() == 'nan': return 0.0
        nums = ''.join(c for c in str(val_str) if c.isdigit() or c == '.')
        return float(nums) if nums else 0.0

    df_working['_raw_intensity'] = df_working['_clean_int'].apply(inline_extractor)
    
    # Process visibility window bounds
    df_working = df_working.dropna(subset=['_clean_nm', '_raw_intensity']).copy()
    df_working = df_working[(df_working['_clean_nm'] >= x_min) & (df_working['_clean_nm'] <= x_max)].copy()
    
    # Group data by rounded wavelengths to aggregate intensity totals
    df_working['_rounded_nm'] = df_working['_clean_nm'].round(4)
    aggregated_df = df_working.groupby('_rounded_nm', as_index=False).agg({'_raw_intensity': 'sum'})
    aggregated_df = aggregated_df.sort_values(by='_rounded_nm').reset_index(drop=True)
    
    # Apply global non-linear scaling (exposure boost) to lift faint lines
    aggregated_df['_compressed_intensity'] = np.sqrt(aggregated_df['_raw_intensity'])
    min_val = aggregated_df['_compressed_intensity'].min()
    max_val = aggregated_df['_compressed_intensity'].max()
    val_range = max_val - min_val
    
    if val_range == 0 or np.isnan(val_range):
        aggregated_df['Normalized_Intensity'] = 1.0
    else:
        aggregated_df['Normalized_Intensity'] = (aggregated_df['_compressed_intensity'] - min_val) / val_range
        
    return aggregated_df

# =======================================================================
# Tailored for handling NIST Descriptor data
# =======================================================================

def prepare_nist_spectrum(df, intensity_col, apply_descriptor_adjustments):
    parsed = df[intensity_col].apply(parse_nist_intensity)
    df['_raw_intensity'] = parsed.apply(lambda t: t[0])
    df['_descriptor'] = parsed.apply(lambda t: t[1])

keys = getattr(nist_helper, "_DESCRIPTOR_KEYS_SORTED", None)

def _effects_from_desc(desc):
    if not desc:
        return (1.0, 1.0, True)
    if keys:
        tokens = [k for k in keys if k in desc]
    else:
        tokens = [t for t in re.split(r'[\s,]+', desc) if t]
    eff = nist_helper.compute_descriptor_effects(tokens)
    return (eff.get("intensity_multiplier", 1.0), eff.get("width_multiplier", 1.0), eff.get("include", True))

def identify_spectral_peaks(aggregated_df, prominence_percentage, peak_wavelengths=None):
    """
    Identifies index positions of prominent emission peaks. 
    Uses rolling neighborhood max windows to preserve dense multiplets.
    """
    if peak_wavelengths is not None:
        nm_vals = aggregated_df['_rounded_nm'].values
        peaks = []
        for pw in peak_wavelengths:
            try: pv = float(pw)
            except Exception: continue
            idx = int(np.argmin(np.abs(nm_vals - pv)))
            peaks.append(idx)
        return sorted(set(peaks))
        
    peaks = []
    window_radius = 0  
    intensity_floor = aggregated_df['Normalized_Intensity'].max() * (prominence_percentage * 0.2)
    
    for i in range(window_radius, len(aggregated_df) - window_radius):
        current_int = aggregated_df.iloc[i]['Normalized_Intensity']
        if current_int < intensity_floor:
            continue
            
        neighborhood = aggregated_df.iloc[i - window_radius : i + window_radius + 1]['Normalized_Intensity']
        if current_int == neighborhood.max():
            peaks.append(i)
            
    return peaks

def render_spectrum_canvas(
    aggregated_df, 
    peaks, 
    x_min, 
    x_max, 
    fig_size, 
    mode, 
    min_brightness, 
    max_needle_y_scale, 
    min_needle_max_width_nm, 
    glow_width_multiplier, 
    glow_alpha, 
    peak_label_y_position, 
    dpi
    ):
    """
    Assembles the physical Matplotlib figure layout, plots uniform vector bars, 
    applies neon atmospheric aura glow, and prints text labels.
    """
    fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
    text_color = 'white' if mode == 'dark' else 'black'

    fig.patch.set_facecolor('black' if mode == 'dark' else 'white')
    ax.set_facecolor('black')
    ax.yaxis.set_visible(False)
    ax.set_xlabel('Wavelength (nm)', color=text_color, fontweight='bold', labelpad=10)

    ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
    ax.tick_params(axis='x', which='major', colors=text_color, labelsize=10)
    ax.tick_params(axis='x', which='minor', colors=text_color, length=4, width=0.5)
    ax.grid(False)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, 1)

    for idx, row in aggregated_df.iterrows():
        nm_val = float(row['_rounded_nm'])
        norm_int = float(row['Normalized_Intensity'])
        base_rgb = np.array(utils.wavelength_to_rgb(nm_val))
        is_peak = idx in peaks
        
        if is_peak:
            final_scale = min_brightness + (1 - min_brightness) * (norm_int ** 0.8)
            final_scale = min(1.0, final_scale * 1.4)
            z_order = 3
        else:
            final_scale = (min_brightness + (1 - min_brightness) * norm_int) * 0.4
            z_order = 1

        colored_rgb = base_rgb * final_scale
        y_height = max_needle_y_scale if is_peak else max_needle_y_scale * 0.7
        y_steps = np.array([0, y_height])
        
        widths = min_needle_max_width_nm * np.ones_like(y_steps)
        x_left = nm_val - widths / 2
        x_right = nm_val + widths / 2
        
        ax.fill_betweenx(y_steps, x_left, x_right, facecolor=colored_rgb, alpha=1.0 if is_peak else 0.3, edgecolor='none', zorder=z_order)

        if is_peak and glow_width_multiplier > 1.0:
            glow_widths = widths * glow_width_multiplier
            g_left = nm_val - glow_widths / 2
            g_right = nm_val + glow_widths / 2
            ax.fill_betweenx(y_steps, g_left, g_right, facecolor=colored_rgb, alpha=glow_alpha, edgecolor='none', zorder=2)

        if is_peak:
            ax.text(
                x=nm_val, y=peak_label_y_position, s=f"{nm_val:.1f}", 
                color=text_color, fontsize=8, rotation=60, 
                ha='left', va='bottom', zorder=4, rotation_mode='anchor'
            )

    plt.tight_layout()
    return fig, ax