# =======================================================================
# In "nist_codes"
# =======================================================================

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

# =======================================================================
# In "new_renderer"
# =======================================================================

- is_nist_descriptor




# =======================================================================
# In "nist_codes"
# =======================================================================

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

- is_nist_descriptor