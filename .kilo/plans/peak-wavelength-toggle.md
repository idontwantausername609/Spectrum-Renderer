# Add Peak Wavelength Display Toggle Option

## Overview
Add a checkbox in the webapp UI that allows users to control whether peak wavelength labels are displayed on the rendered spectrum image.

## Current State Analysis
- **`new_renderer.py:40`** - `plot_spec()` already has a `show_peak_labels=True` parameter
- **`new_renderer.py:328`** - Labels are conditionally rendered based on `show_peak_labels and peak_norm_int >= label_min_norm_int`
- **`webapp2.py:70-77`** - The `/api/render` endpoint calls `plot_spec()` but does NOT pass any `show_peak_labels` parameter
- **`templates/index.html`** - No UI control exists for this option

## Implementation Plan

### 1. Backend: webapp2.py (line 41-77)
- Read a `show_peak_labels` form parameter (checkbox)
- Default to `True` if parameter not provided (maintain backward compatibility)
- Pass `show_peak_labels` to `new_renderer.plot_spec()` call

### 2. Frontend: templates/index.html
- Add a checkbox in the "Render Image Modes" section (around line 39-56)
- Label: "Show Peak Wavelength Labels"
- Default: checked (to maintain current behavior)
- Include `show_peak_labels` in the FormData for both dark and light mode renders

## Files to Modify
| File | Changes |
|------|---------|
| `webapp2.py` | Add form parameter reading and pass to renderer |
| `templates/index.html` | Add checkbox UI control and include in form submission |

## Behavior
- When checked (default): Peak wavelength values are displayed on the image (current behavior)
- When unchecked: The peaks are still rendered visually but no numeric labels appear