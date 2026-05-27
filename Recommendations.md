## Recommendations


# webapp.py #
**High Priority**
- **Case-insensitive descriptors:** Prefer exact-case descriptor lookup, then fallback to case-insensitive matches to avoid missed tokens. Example:
  ```
  t = token.strip()
  rule = DESCRIPTORS.get(t) or DESCRIPTORS.get(t.lower())
  ```
- **Persist in-memory workbook handling:** Keep using byte/file-like inputs and ensure `wb.close()` in every code path to avoid WinError 32.
- **Dual-mode export (light+dark):** Add a server-side option to render and return both light and dark PNGs (or a ZIP) so users can download both regardless of UI theme.
- **Unit tests for token variants & Windows locking:** Add focused tests for descriptor casing, unknown-token behavior, and loader behavior when file-like objects are provided (simulate file-lock scenarios).

**Medium Priority**
- **Server-side ZIP endpoint:** Implement `/api/batch_render` that renders multiple sheets or modes and returns a ZIP for convenient bulk download.
- **E2E browser tests:** Add Playwright or Selenium tests for upload → sheet-select → render → download flows to catch regressions.
- **Structured logging & diagnostics:** Add configurable logging (JSON-friendly) and include `diagnostics` in API responses for easier tuning of rendering rules.
- **Configurable rendering constants:** Move visual constants in rendering.py to a small config (`pyproject`, `config.yaml`, or `env`) so non-dev users can tune appearance without editing code.

**Low Priority**
- **CLI entrypoint & packaging:** Provide `python -m spectrum` or a console script for local use, and add `pyproject.toml`/`setup.cfg` to ease installation.
- **Type checking & linting CI:** Add `mypy` and GitHub Actions for tests + flake8 to enforce quality on PRs.
- **More descriptor tests & docs:** Expand `NIST Descriptors Reference.ipynb` into concise markdown docs with examples and expected intensity outcomes for each descriptor.
- **Performance guardrails:** For very large sheets, add server-side limits, a render queue, or background worker (Celery/RQ) to avoid blocking the Flask process.

**Tuning & UX**
- **Default heuristics:** Log and display the header token match rates (e.g., % parsed, % unknown) in UI to help users fix spreadsheet columns.
- **Sheet auto-detection improvements:** Allow user overrides and a preview of parsed first N lines before rendering.
- **Save presets:** Let users save rendering presets (sigma, broad/blend factors, glow) per-project.


# nist_descriptors.py
Why it can fail on arbitrary input (common examples)
- Scientific notation: `1e3` or `1E+03` → the `'e'` is not allowed by the char test, so numeric_part becomes `'1'`, descriptor `'e3'` → parse fails or misinterprets.
- Commas/locale numbers: `1,000` → comma stops numeric scan, numeric_part `'1'` instead of `1000`.
- Whitespace or parentheses: `100 (bl*)` or `100 bl*` → numeric_part extraction stops before space? Current loop allows only digits and .+- so space breaks numeric scan, numeric_part parsed OK (since it will stop before space, numeric_part='100') — descriptor_text starts with `(bl*)` which `split_descriptor_tokens` will try to match keys from start; a leading `(` will cause unknown character handling, producing tokens like `'('` then next chars — not ideal.
- Pure descriptor (no numeric): `'bl*'` → numeric_part empty → returns None numeric; loader skips rows with None numeric (may be OK, but you might prefer fallback).
- Case variants: `'BL*'` or `'Bl'` → `split_descriptor_tokens` matches against `DESCRIPTOR_KEYS` which are case-sensitive; uppercase vs lowercase tokens may be missed.
- Units or trailing text: `'100 counts'` → descriptor becomes `'counts'` (unknown); but that's tolerable.
- Leading ± signs, parentheses, or Unicode dashes may break detection.

Safe, practical robustness improvements (recommended)
1. Numeric parsing using a regex that supports:
   - integers, decimals, optional sign
   - optional exponent (scientific notation)
   - optional thousands separators (commas) — strip commas before parse
   - allow optional whitespace between number and descriptor
   - Example regex: r'^[\s]*([+-]?(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?)'
2. Accept descriptors separated by whitespace or enclosed in parentheses:
   - After extracting numeric match, strip common punctuation from descriptor_text: `.strip(" ()[]")`
3. Case‑insensitive descriptor lookup:
   - Create a lowercased descriptor map once (e.g., `NIST_DESCRIPTORS_LOWER = {k.lower(): v for k, v in NIST_DESCRIPTORS.items()}`) and use fallback lookup: `rule = NIST_DESCRIPTORS.get(token) or NIST_DESCRIPTORS_LOWER.get(token.lower())`.
   - Also make `split_descriptor_tokens()` match on a lowercased `remaining` while preserving original token text if you need to report it.
4. Tolerate commas in numbers: remove commas before float conversion, or rely on regex that captures them then `numeric_part.replace(',', '')`.
5. Optional fallback when numeric missing:
   - Decide policy: either return `None` (current behavior) or treat missing numeric as `1.0` (or `np.nan`) and record in `unknown_tokens`. I recommend keeping `None` as loader currently skips those rows; if you want to keep them, set a flag and handle in loader.
6. Add unit tests for representative inputs:
   - `'100bl*'`, `'100 bl*'`, `'100 (bl*)'`, `'1e3bl'`, `'1,000 bl'`, `'BL*'`, `'bl*'`, `'100counts'`, `'–'`, `''`, `None`.

Minimal example of improved numeric extraction (concept)
```python
import re
NUM_RE = re.compile(r'^[\s]*([+-]?(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?)')
m = NUM_RE.match(value_str)
if not m:
    return None, descriptor_text, [], 1.0, 1.0, 'high', [], []
numeric_part = m.group(1).replace(',', '')
descriptor_text = value_str[m.end():].strip(" ()[]")
```

Case-insensitive lookup sketch inside `combine_descriptor_rules`
```python
# build once at module level
NIST_LOWER = {k.lower(): v for k, v in NIST_DESCRIPTORS.items()}

# inside loop
rule = NIST_DESCRIPTORS.get(token)
if rule is None:
    rule = NIST_LOWER.get(token.lower())
if rule is None:
    unknown_tokens.append(token)
    continue
# then process rule
```

I'll add a short TODO plan for making intensity parsing and normalization robust across arbitrary formats.

Created 4 todos

**Recommendations**

- **Robust numeric parsing:** Use a regex to extract the leading number (supports commas and scientific notation), strip commas, then float-convert. Example:
  - Regex: `NUM_RE = re.compile(r'^[\s]*([+-]?(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?)')`
  - After match: `num = m.group(1).replace(',', '') ; value = float(num)`
  - Rationale: handles `1e3`, `1,000`, `+12.5`, `-3.4E+2`.

- **Tolerant descriptor extraction:** Strip surrounding punctuation and whitespace before tokenizing:
  - `descriptor_text = value_str[m.end():].strip().strip('()[]{}')`
  - Allow a space between number and descriptor (e.g., `100 bl*`) and accept pure-descriptor cells gracefully (return numeric None but record descriptor).

- **Case-insensitive descriptor lookup:** Build a lowercase descriptor map and fall back to it when `NIST_DESCRIPTORS` misses a token:
  - `NIST_LOWER = {k.lower(): v for k, v in NIST_DESCRIPTORS.items()}`
  - Lookup: `rule = NIST_DESCRIPTORS.get(token) or NIST_LOWER.get(token.lower())`
  - Rationale: accepts `BL`, `Bl`, `bl`.

- **Graceful unknown tokens:** Do not fail on unknown descriptor tokens; record them in `unknown_tokens` (already done) and continue using numeric intensity. Consider logging top unknown tokens in `diagnostics` to help users clean data.

- **Flexible missing-numeric policy:** Keep current behavior (skip rows where numeric intensity is missing) but add a config flag (or loader parameter) like `treat_missing_as= None|'1.0'|'nan'` so callers can opt into including descriptor-only lines.

- **Normalization and rescaling (handle values >>400):**
  - Always preserve raw numeric values in `result['diagnostics']['raw_intensities']` or at least `min/max`.
  - Provide options when rendering:
    - `scale='raw'` → render raw values
    - `scale='normalize'` → divide by max: `i_norm = i / max(i)`
    - `scale='rescale'` with `target_max` → `i_rescaled = i / max(i) * target_max`
    - `scale='log'` → `i_log = np.log1p(i)` (good for high dynamic range)
  - Default suggestion: render normalized to 1.0 and allow UI toggle to download raw-scaled images. This ensures files with intensities like 400+ render visibly.

- **Clamp / sane limits:** Prevent extreme multipliers from blowing up visuals:
  - e.g., `intensity_multiplier = min(max(intensity_multiplier, 0.01), 100.0)`
  - `width_multiplier = min(max(width_multiplier, 0.1), 10.0)`

- **Expose diagnostics:** Include `min`, `max`, `median`, `unknown_tokens`, `skipped_masked` in `result['diagnostics']`. Surface these in the UI so users can pick appropriate scale mode.

- **Loader flexibility:** Accept the following fallbacks in `load_spectral_data()`:
  - Column name variants (already used) plus allow optional explicit column indices passed as parameters (`wavelength_idx`, `intensity_idx`) for files with no headers.
  - Allow a `preview_rows` mode that returns parsed diagnostics without rendering so users can confirm mapping.

- **Tests & example data:** Add unit tests for `parse_nist_intensity()` covering:
  - `100bl*`, `100 bl*`, `100 (bl*)`, `1e3bl`, `1,000 bl`, `BL*`, `100counts`, `None`, `''`.
  - Include cases with intensities >400 and extreme values to validate normalization and clamping.

- **UI controls:** Add a small control to index.html:
  - `Scale mode` selector: `Raw | Normalize (0-1) | Rescale (set max) | Log`
  - `Target max` input when `Rescale` selected.
  - Also show `diagnostics` summary after sheet selection.

- **Backwards compatibility:** Keep current return shape and behavior by default; add new optional parameters (e.g., `scale_mode`, `treat_missing_as`, `wavelength_idx`, `intensity_idx`) so callers (including webapp.py) can opt in without breaking existing code.