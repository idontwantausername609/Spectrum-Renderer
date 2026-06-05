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