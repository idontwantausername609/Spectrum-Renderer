# =======================================================================
# In "nist_codes"
# =======================================================================

- detect_nist_values
- parse_nist_intensity
- clean_nist_row
- nist_descriptor_adjustments
- nist_to_dataframe
- extract_and_sanitize_data
- prepare_nist_spectrum
- _effects_from_desc
- identify_spectral_peaks
- render_spectrum_canvas

# =======================================================================
# In "utils"
# =======================================================================

- generate_random_title
- normalize_header
- clean_title
- looks_like_number
- choose_scale_mode
- lambda_tokens
- int_tokens
- major_locator
- minor_locator
- X_MIN, X_MAX, FIG_SIZE, MIN_NEEDLE_WIDTH, MAX_NEEDLE_WIDTH, DPI, MAX_Y_SCALE, NEEDLE_POWER_SHAPE, LABEL_NORM_INT, GLOW_WIDTH_INT
- NORM_PROM_PERC, NORM_MIN_BRIGHT, NORM_GLOW_ALPHA, NORM_PEAK_EMPHASIS, NORM_PEAK_LABEL_POSN
- DEFAULT_PROM_PERC, DEFAULT_MIN_BRIGHT, DEFAULT_GLOW_ALPHA, DEFAULT_PEAK_EMPHASIS, DEFAULT_PEAK_LABEL_POSN
- generate_random_title
- resolve_column
- wavelength_to_rgb
- compute_label_positions

# =======================================================================
# In "generic_render"
# =======================================================================

- prepare_generic_spectrum
- plot_emission_spectrum
- get_spectra

# =======================================================================
# In "nist_helper"
# =======================================================================

- NIST_DESCRIPTORS
- DESCRIPTOR_EFFECTS
- _DESCRIPTOR_KEYS_SORTED
- compute_descriptor_effects
  -     """
    Compute include_flag, intensity_multiplier, width_multiplier, actions, confidence, shared_hint.

    - tokens: list of descriptor tokens (e.g. ['bl','*'] or ['a'])
    - group_size: optional integer indicating how many lines share intensity when '*' present.
                 If provided and '*' is in tokens, intensity will be divided by group_size.
                 If None, shared_hint=True is returned so caller can decide.

    Returns:
      {
        "include": bool,
        "intensity_multiplier": float,
        "width_multiplier": float,
        "actions": list[str],
        "confidence": str,    # 'high'|'medium'|'low'|'excluded'
        "shared_hint": bool,  # True if '*' present and group_size not given
      }
    """

# =======================================================================
# In "new_renderer"
# =======================================================================

- plot_spec
- get_spec

# =======================================================================
# In "webapp2"
# =======================================================================

- index
- get_sheets
- render
  
# =======================================================================
# In "new_loader"
# =======================================================================

- find_spectral_sheet
- _open_workbook_from_input
- load_spectral_data
- list_sheets















# =======================================================================
# In "nist_codes"
# =======================================================================

- detect_nist_values
  -     """
    Return (bool has_any_nist, dict diagnostics).
    Diagnostics: {'numeric_fraction', 'contains_tokens', 'contains_descriptor_chars'}
    """
- parse_nist_intensity
  -     """
    Parse a NIST intensity cell that may include descriptor characters.

    Returns:
        (numeric_value_or_nan, descriptor_string)
    """
- clean_nist_row
  -     """
    Cleans NIST formatting flags like '*', 'bl', and spaces.
    Force-casts numeric types to string first to handle clean Excel data.
    Returns (float wavelength, float intensity) or (None, None) if invalid.
    """
- nist_descriptor_adjustments
  -     """
    Intensity-only multipliers from the NIST descriptor reference.
    This is safe for your aesthetics because it does not change the renderer style,
    only the brightness input values.
    """
- nist_to_dataframe
- extract_and_sanitize_data
  -     """
    Cleans raw dataframe strings, extracts intensities, binds doublets/triplets
    by 4-decimal rounding, and normalizes them uniformly via exposure compression.
    """
- prepare_nist_spectrum
- _effects_from_desc
- identify_spectral_peaks
  -     """
    Identifies index positions of prominent emission peaks. 
    Uses rolling neighborhood max windows to preserve dense multiplets.
    """
- render_spectrum_canvas
  -     """
    Assembles the physical Matplotlib figure layout, plots uniform vector bars, 
    applies neon atmospheric aura glow, and prints text labels.
    """

# =======================================================================
# In "utils"
# =======================================================================

- generate_random_title
- choose_scale_mode
  -     """
    Heuristic to pick a display scale mode.
    Returns one of: 'normalize', 'raw'
    """
- lambda_tokens
- int_tokens
- major_locator
- minor_locator
- X_MIN, X_MAX, FIG_SIZE, MIN_NEEDLE_WIDTH, MAX_NEEDLE_WIDTH, DPI, MAX_Y_SCALE, NEEDLE_POWER_SHAPE, LABEL_NORM_INT, GLOW_WIDTH_INT
- NORM_PROM_PERC, NORM_MIN_BRIGHT, NORM_GLOW_ALPHA, NORM_PEAK_EMPHASIS, NORM_PEAK_LABEL_POSN
- DEFAULT_PROM_PERC, DEFAULT_MIN_BRIGHT, DEFAULT_GLOW_ALPHA, DEFAULT_PEAK_EMPHASIS, DEFAULT_PEAK_LABEL_POSN
- generate_random_title
- resolve_column
  -     """
    Find the first column whose name contains any keyword from the candidates.

    This is keyword-based matching, not exact phrase matching.
    Example:
    - candidate "relative intensity" matches headers containing
      "relative", "intensity", or both
    - candidate "wavelength_nm" matches headers containing "wavelength" or "nm"
    """
- wavelength_to_rgb
  -     """
    Converts a wavelength in nanometers to an RGB color tuple (0-1 range).
    Based on code by Dan Bruton.
    """
- compute_label_positions
  -     """
    Compute per-peak Y positions so labels for nearby peaks stack/stagger instead of overlapping.

    Args:
        peak_nms: list[float] - peak wavelengths (nm) in the same order you'll iterate peaks.
        intensities: optional list[float] - normalized intensities (same order), used by some methods.
        base_y: float - default label baseline (same as peak_label_y_position).
        min_sep_nm: float - minimum horizontal separation (nm) before labels considered "colliding".
        y_step: float - vertical step size to stack/stagger labels.
        method: "stack" | "stagger" | "prefer_stronger_top"
        max_y: float - clamp y so labels don't run off the top.

    Returns:
        list[float] - y position for each input peak (same order).
    """

# =======================================================================
# In "generic_render"
# =======================================================================

- prepare_generic_spectrum
- plot_emission_spectrum
- get_spectra

# =======================================================================
# In "nist_helper"
# =======================================================================

- NIST_DESCRIPTORS
- DESCRIPTOR_EFFECTS
- _DESCRIPTOR_KEYS_SORTED
- compute_descriptor_effects

# =======================================================================
# In "new_renderer"
# =======================================================================

- plot_spec
- get_spec

# =======================================================================
# In "webapp2.py"
# =======================================================================

- index
  -     """Serve main upload form."""
- get_sheets
  -     """
    List sheets in uploaded Excel file.
    
    Form data:
        file: Uploaded Excel file
    
    JSON response:
        {'sheets': [...]}
    """
- render
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

# =======================================================================
# In "new_loader"
# =======================================================================

- find_spectral_sheet
- _open_workbook_from_input
  -     """Open an openpyxl Workbook from a path, bytes, or file-like object.

    Returns: openpyxl.Workbook
    """
- load_spectral_data
  -     """
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
- list_sheets
  -     """
    List all sheet names in an Excel file.
    
    Args:
        excel_file_path (str): Path to Excel workbook
    
    Returns:
        list[str]: Sheet names
    """