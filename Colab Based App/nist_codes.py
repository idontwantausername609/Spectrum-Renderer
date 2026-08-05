import re
import importlib
import numpy as np
import pandas as pd

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

def detect_nist_values(series, force_nist=None, nist_helper_module=nist_helper):
    s = series.astype(str).fillna("")
    numeric_fraction = float(pd.to_numeric(s, errors="coerce").notna().mean()) if len(s) else 0.0

    tokens = [t.lower() for t in getattr(nist_helper_module, "NIST_DESCRIPTORS", [])] if nist_helper_module else []
    token_pattern = "|".join(re.escape(t) for t in tokens if t)
    contains_tokens = bool(s.str.lower().str.contains(token_pattern, na=False).any()) if token_pattern else False
    contains_descriptor_chars = bool(s.str.contains(r"[A-Za-z*:\(\)\[\]/%]", na=False).any())

    if force_nist is True:
        has_any_nist = True
    elif force_nist is False:
        has_any_nist = False
    else:
        has_any_nist = bool(contains_tokens or (numeric_fraction < 0.6 and contains_descriptor_chars))

    print("DEBUG: detect_nist_values")

    return has_any_nist, {
        "numeric_fraction": numeric_fraction,
        "contains_tokens": contains_tokens,
        "contains_descriptor_chars": contains_descriptor_chars,
    }

def parse_nist_intensity(raw_value):
    if pd.isna(raw_value):
        return (np.nan, "")
    text = str(raw_value).strip()
    match = re.search(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', text)
    if not match:
        return (np.nan, text)
    try:
        num_val = float(match.group(0))
    except Exception:
        num_val = np.nan
    before = text[:match.start()].strip()
    after = text[match.end():].strip()
    descriptor = (before + " " + after).strip()
    descriptor = re.sub(r'[\s,]+', ' ', descriptor)

    print("\nDEBUG: parse_nist_intensity")


    return (num_val, descriptor)


# =======================================================================
# Tailored for handling NIST Descriptor data
# =======================================================================


def prepare_nist_spectrum(df, int_col, apply_descriptor_adjustments=False):
    df = df.copy()
    parsed = df[int_col].apply(parse_nist_intensity)
    df["_raw_int"] = parsed.apply(lambda t: t[0])
    df["_descriptor"] = parsed.apply(lambda t: t[1])

    effs = df["_descriptor"].apply(_effects_from_desc)
    df["_intensity_mult"] = effs.apply(lambda v: v[0])
    df["_width_mult"] = effs.apply(lambda v: v[1])
    df["_include"] = effs.apply(lambda v: v[2])

    df = df[df["_include"]].copy()
    if apply_descriptor_adjustments:
        df["_adj_int"] = df["_raw_int"] * df["_intensity_mult"]
    else:
        df["_adj_int"] = df["_raw_int"]

    print("\nDEBUG: prepare_nist_spectrum")

    return df

# normalized descriptor keys (module-level)
_KEYS_SORTED = getattr(nist_helper, "_DESCRIPTOR_KEYS_SORTED", None)
_KEYS_SORTED_LC = [k.lower() for k in _KEYS_SORTED] if _KEYS_SORTED else None

def _effects_from_desc(desc):
    if not desc or nist_helper is None:
        return 1.0, 1.0, True
    desc_text = str(desc).lower()
    if _KEYS_SORTED_LC:
        remaining = desc_text
        tokens = []
        for k in _KEYS_SORTED_LC:
            if k and k in remaining:
                tokens.append(k)
                remaining = remaining.replace(k, " ")
    else:
        tokens = [tok for tok in re.split(r"[\s,]+", desc_text) if tok]
    eff = nist_helper.compute_descriptor_effects(tokens)

    print("\nDEBUG: _effects_from_desc")
    
    return eff.get("intensity_multiplier", 1.0), eff.get("width_multiplier", 1.0), eff.get("include", True)

def identify_spectral_peaks(aggregated_df, prominence_percentage, peak_wavelengths=None):
    print("\nDEBUG: peak wavelengths (id spec peaks)", peak_wavelengths)
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
    intensity_floor = aggregated_df['Norm_Int'].max() * (prominence_percentage * 0.2)

    print("\nDEBUG: identify_spectral_peaks")
    
    for i in range(window_radius, len(aggregated_df) - window_radius):
        current_int = aggregated_df.iloc[i]['Norm_Int']
        if current_int < intensity_floor:
            continue
            
        neighborhood = aggregated_df.iloc[i - window_radius : i + window_radius + 1]['Norm_Int']
        if current_int == neighborhood.max():
            peaks.append(i)
            
    return peaks
