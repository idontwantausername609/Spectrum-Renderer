# =======================================================================
# In "nist_codes"
# =======================================================================

- detect_nist_values
- parse_nist_intensity
- prepare_nist_spectrum
- _effects_from_desc
- identify_spectral_peaks

# =======================================================================
# In "utils"
# =======================================================================

- generate_random_title
- normalize_header
- clean_title
- looks_like_number
- lambda_tokens
- int_tokens
- major_locator
- minor_locator
- X_MIN, X_MAX, FIG_SIZE, MIN_NEEDLE_WIDTH, MAX_NEEDLE_WIDTH, DPI, MAX_Y_SCALE, NEEDLE_POWER_SHAPE, LABEL_NORM_INT, GLOW_WIDTH_INT
- NORM_PROM_PERC, NORM_MIN_BRIGHT, NORM_GLOW_ALPHA, NORM_PEAK_EMPHASIS, NORM_PEAK_LABEL_POSN
- DEFAULT_PROM_PERC, DEFAULT_MIN_BRIGHT, DEFAULT_GLOW_ALPHA, DEFAULT_PEAK_EMPHASIS, DEFAULT_PEAK_LABEL_POSN
- fig_height_overflow_scale
- generate_random_title
- resolve_column
- wavelength_to_rgb
- prepare_generic_spectrum
- compute_label_positions

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
# In "webapp2"
# =======================================================================

- index
- get_sheets
- render
  
# =======================================================================
# In "new_loader"
# =======================================================================

- _open_workbook_from_input
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
- lambda_tokens
- int_tokens
- major_locator
- minor_locator
- X_MIN, X_MAX, FIG_SIZE, MIN_NEEDLE_WIDTH, MAX_NEEDLE_WIDTH, DPI, MAX_Y_SCALE, NEEDLE_POWER_SHAPE, LABEL_NORM_INT, GLOW_WIDTH_INT
- NORM_PROM_PERC, NORM_MIN_BRIGHT, NORM_GLOW_ALPHA, NORM_PEAK_EMPHASIS, NORM_PEAK_LABEL_POSN
- DEFAULT_PROM_PERC, DEFAULT_MIN_BRIGHT, DEFAULT_GLOW_ALPHA, DEFAULT_PEAK_EMPHASIS, DEFAULT_PEAK_LABEL_POSN
- fig_height_overflow_scale
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

- prepare_generic_spectrum

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
# In "nist_helper"
# =======================================================================

- NIST_DESCRIPTORS
- DESCRIPTOR_EFFECTS
- _DESCRIPTOR_KEYS_SORTED
- compute_descriptor_effects
  -   -     """
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

- _open_workbook_from_input
  -     """Open an openpyxl Workbook from a path, bytes, or file-like object.

    Returns: openpyxl.Workbook
    """

- list_sheets
  -     """
    List all sheet names in an Excel file.
    
    Args:
        excel_file_path (str): Path to Excel workbook
    
    Returns:
        list[str]: Sheet names
    """