# =======================================================================
# In "nist_codes"
# =======================================================================

- detect_nist_values
  - new_renderer

- parse_nist_intensity
  - new renderer
  - new_loader

- prepare_nist_spectrum
  - new_renderer

- _effects_from_desc
  - nist_codes (called by prepare_nist_spectrum)

- identify_spectral_peaks
  - new_renderer

# =======================================================================
# In "utils"
# =======================================================================

- generate_random_title
  - new_renderer

- normalize_header
  - new_loader

- clean_title
  - new_loader

- looks_like_number
  - new_loader

- choose_scale_mode

- lambda_tokens
  - new_renderer
  - new_loader

- int_tokens
  - new_renderer
  - new_loader

- major_locator
  - new_renderer

- minor_locator
  - new_renderer

- X_MIN, X_MAX, FIG_HERIGHT_BASE, FIG_WIDTH, FIG_SIZE, MIN_NEEDLE_WIDTH, MAX_NEEDLE_WIDTH, DPI, MAX_Y_SCALE, NEEDLE_POWER_SHAPE, LABEL_NORM_INT, GLOW_WIDTH_INT
  - new_renderer

- NORM_PROM_PERC, NORM_MIN_BRIGHT, NORM_GLOW_ALPHA, NORM_PEAK_EMPHASIS, NORM_PEAK_LABEL_POSN
  - new_renderer

- DEFAULT_PROM_PERC, DEFAULT_MIN_BRIGHT, DEFAULT_GLOW_ALPHA, DEFAULT_PEAK_EMPHASIS, DEFAULT_PEAK_LABEL_POSN
  - new_renderer

- fig_height_overflow_scale
  - new_renderer

- generate_random_title
  - new_renderer

- resolve_column
  - new_renderer

- wavelength_to_rgb
  - new_renderer

- prepare_generic_spectrum
  - new_renderer

- compute_label_positions
  - new_renderer

# =======================================================================
# In "nist_helper"
# =======================================================================

- NIST_DESCRIPTORS
  - nist_codes

- DESCRIPTOR_EFFECTS
  - nist_helper

- _DESCRIPTOR_KEYS_SORTED
  - nist_codes

- compute_descriptor_effects
  - nist_codes

# =======================================================================
# In "new_renderer"
# =======================================================================

- plot_spec
  - webapp2

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
  - webapp2