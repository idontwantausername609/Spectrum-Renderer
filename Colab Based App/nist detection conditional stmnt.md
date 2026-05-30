Optimized tool selectionI'll add a short TODO list for the change, then show the exact code snippet and where to insert it.

Created 3 todos

Progress: added a short TODO plan. Next: paste the exact helper + integration snippet and precise insertion point.

Insert this helper near the top of generic_render.py (or nist_codes.py) with your other small helpers:

```python
def is_nist_descriptor(descriptor, descriptor_tokens):
    if not descriptor:
        return False
    s = str(descriptor).lower()
    # tokens are short strings like 'bl','hfs','*' — match substring
    return any(tok.lower() in s for tok in descriptor_tokens)
```

Then, in your renderer, place the check immediately after these lines (the "right after parsing" spot):

- Locate these lines:
  ```python
  parsed_intensity = df_plot_data[intensity_col].apply(parse_nist_intensity)
  df_plot_data['_raw_intensity'] = parsed_intensity.apply(lambda t: t[0])
  df_plot_data['_descriptor'] = parsed_intensity.apply(lambda t: t[1])
  ```
- Insert the NIST-detection and branch right after them and before you drop NaNs / filter by x_min / normalization. Example insertion:

```python
# --- Quick NIST descriptor detection (insert here) ---
# get token list (fall back to any sorted keys if needed)
nist_tokens = []
if 'nist_helper' in globals() and getattr(nist_helper, 'NIST_DESCRIPTORS', None):
    nist_tokens = [str(t).lower() for t in nist_helper.NIST_DESCRIPTORS]
elif 'nist_helper' in globals() and getattr(nist_helper, '_DESCRIPTOR_KEYS_SORTED', None):
    nist_tokens = [str(t).lower() for t in nist_helper._DESCRIPTOR_KEYS_SORTED]

# boolean: does any input row contain a NIST descriptor token?
has_any_nist = df_plot_data['_descriptor'].fillna('').astype(str).str.lower().apply(
    lambda s: any(tok in s for tok in nist_tokens)
).any()

# Decide branch early: set a flag or call the appropriate prep function
if has_any_nist:
    use_nist_path = True
    # e.g. df_plot_data = prepare_nist_spectrum(df_plot_data, ...)
else:
    use_nist_path = False
    # e.g. df_plot_data = prepare_generic_spectrum(df_plot_data, ...)
# --- end insertion ---
```

Notes:
- Place this before `df_plot_data = df_plot_data.dropna(subset=[nm_col, '_raw_intensity']).copy()` so descriptor text isn't lost by earlier filtering.
- If you prefer mixed handling (some rows NIST, others generic), compute `df_plot_data['_is_nist'] = ...` per-row instead of a single `has_any_nist`, and branch/merge downstream accordingly.
- If `nist_helper` may be unavailable, the code safely falls back to `_DESCRIPTOR_KEYS_SORTED` or an empty list.