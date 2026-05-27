"""
Spectrum building and rendering functions.
Gaussian core + glow halo with action-driven morphing.
"""

import numpy as np
import matplotlib
# Use a non-interactive backend for server-side rendering
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .utils import generate_random_title
from matplotlib.ticker import MultipleLocator

def choose_scale_mode(raw_min, raw_max, eps=1e-10):
    """
    Heuristic to pick a display scale mode.
    Returns one of: 'normalize', 'raw'
    """
    try:
        raw_min_f = float(raw_min)
        raw_max_f = float(raw_max)
    except Exception:
        return 'normalize'

    # If no dynamic range, present raw values
    rng = raw_max_f - raw_min_f
    if raw_max_f <= 0 or rng <= eps:
        return 'raw'

    # If extremely wide dynamic range, use log scaling
    if raw_max_f / (rng + eps) > 100.0:
        return 'log'

    # If absolute maxima are very large, sqrt helps with compression
    if raw_max_f > 1000.0:
        return 'sqrt'

    # Default: normalized display
    return 'normalize'


# Profile tightening parameters
BASE_SIGMA = 0.12          # nm, base Gaussian sigma
BROAD_FACTOR = 1.20        # width multiplier for broad class
BLEND_FACTOR = 0.70        # width multiplier for blend class
BLEND_INTENSITY = 0.95     # optional intensity scaling for blend
GLOW_STRENGTH = 0.14       # halo glow strength multiplier
ACTION_INTENSITY_FACTOR = 0.50  # Broad class intensity reduction


def build_spectrum_array(wavelengths, intensities, width_factors, actions,
                         wl_min=400, wl_max=750, resolution=4096,
                         scale_mode='raw', keep_top_n=0):
    """
    Build spectrum as continuous intensity array using Gaussian core + glow model.

    Returns:
        tuple: (wl_array, spectrum_array, component_counts)
    """
    # Build the wavelength grid and initialize spectrum
    wl_array = np.linspace(wl_min, wl_max, resolution)
    spectrum = np.zeros_like(wl_array, dtype=float)
    component_counts = {}

    # ensure minimum separation variable exists for optional top-N filtering
    min_sep_nm = 0.0

    for wl, intensity, width_mult, action in zip(wavelengths, intensities,
                                                   width_factors, actions):
        if wl < wl_min or wl > wl_max:
            continue

        action_key = action if action else 'line'
        component_counts[action_key] = component_counts.get(action_key, 0) + 1

        # Scale intensity based on broad class
        if 'broad' in action_key.lower():
            intensity = intensity * ACTION_INTENSITY_FACTOR

        # Build core (Gaussian)
        sigma_base = BASE_SIGMA
        if 'broad' in action_key.lower():
            sigma = sigma_base * width_mult * BROAD_FACTOR
        elif 'blend' in action_key.lower():
            sigma = sigma_base * width_mult * BLEND_FACTOR
        else:
            sigma = sigma_base * width_mult

        core = intensity * np.exp(-0.5 * ((wl_array - wl) / sigma) ** 2)

        # Build glow halo
        glow_sigma = sigma * 1.8
        glow = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - wl) / glow_sigma) ** 2)

        # Add components based on action
        spectrum += core + glow

        if 'doublet' in action_key:
            offset = 0.10
            core_off = intensity * np.exp(-0.5 * ((wl_array - (wl + offset)) / sigma) ** 2)
            glow_off = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - (wl + offset)) / glow_sigma) ** 2)
            spectrum += core_off + glow_off

        if 'cluster' in action_key:
            for offset in [-0.12, 0.12]:
                core_off = intensity * np.exp(-0.5 * ((wl_array - (wl + offset)) / sigma) ** 2)
                glow_off = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - (wl + offset)) / glow_sigma) ** 2)
                spectrum += core_off + glow_off
    wl_array = np.linspace(wl_min, wl_max, resolution)
    spectrum = np.zeros_like(wl_array, dtype=float)
    component_counts = {}
    
    for wl, intensity, width_mult, action in zip(wavelengths, intensities, 
                                                   width_factors, actions):
        if wl < wl_min or wl > wl_max:
            continue
        
        action_key = action if action else 'line'
        component_counts[action_key] = component_counts.get(action_key, 0) + 1
        
        # Scale intensity based on broad class
        if 'broad' in action_key.lower():
            intensity = intensity * ACTION_INTENSITY_FACTOR
        
        # Build core (Gaussian)
        sigma_base = BASE_SIGMA
        if 'broad' in action_key.lower():
            sigma = sigma_base * width_mult * BROAD_FACTOR
        elif 'blend' in action_key.lower():
            sigma = sigma_base * width_mult * BLEND_FACTOR
        else:
            sigma = sigma_base * width_mult
        
        core = intensity * np.exp(-0.5 * ((wl_array - wl) / sigma) ** 2)
        
        # Build glow halo
        glow_sigma = sigma * 1.8
        glow = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - wl) / glow_sigma) ** 2)
        
        # Add components based on action
        spectrum += core + glow
        
        if 'doublet' in action_key:
            offset = 0.10
            core_off = intensity * np.exp(-0.5 * ((wl_array - (wl + offset)) / sigma) ** 2)
            glow_off = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - (wl + offset)) / glow_sigma) ** 2)
            spectrum += core_off + glow_off
        
        if 'cluster' in action_key:
            for offset in [-0.12, 0.12]:
                core_off = intensity * np.exp(-0.5 * ((wl_array - (wl + offset)) / sigma) ** 2)
                glow_off = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - (wl + offset)) / glow_sigma) ** 2)
                spectrum += core_off + glow_off
    
    # If requested, keep only the top `keep_top_n` visible peaks (preserve a small neighborhood)
    if keep_top_n and keep_top_n > 0:
        s = spectrum.copy()
        # convert minimum separation in nm to index distance
        dw = wl_array[1] - wl_array[0]
        min_sep_idx = max(1, int(round(min_sep_nm / dw)))
        # indices sorted by descending intensity (only positive)
        idx_desc = np.argsort(s)[::-1]
        idx_desc = idx_desc[s[idx_desc] > 0]
        accepted = []
        # First pass: honor minimum separation
        for idx in idx_desc:
            if all(abs(idx - a) > min_sep_idx for a in accepted):
                accepted.append(int(idx))
                if len(accepted) >= keep_top_n:
                    break
        # If separation prevented collecting enough peaks, relax and fill with next-highest indices
        if len(accepted) < keep_top_n:
            for idx in idx_desc:
                if int(idx) not in accepted:
                    accepted.append(int(idx))
                    if len(accepted) >= keep_top_n:
                        break
        # Build mask preserving a neighborhood around each accepted peak
        mask = np.zeros_like(s, dtype=bool)
        for a in accepted:
            lo = max(0, a - min_sep_idx)
            hi = min(len(s), a + min_sep_idx + 1)
            mask[lo:hi] = True
        spectrum = s * mask.astype(float)    
        
    # Preserve raw stats for diagnostics and flexible scaling
    raw_max = float(spectrum.max() if spectrum.size else 0.0)
    raw_min = float(spectrum.min() if spectrum.size else 0.0)
    
    # Remove very small background contributions (0.5% of peak)
    background_thresh = raw_max * 0.005
    if background_thresh > 0:
        spectrum[spectrum < background_thresh] = 0.0
    
    # Recompute stats after thresholding
    raw_max = float(spectrum.max() if spectrum.size else 0.0)
    raw_min = float(spectrum.min() if spectrum.size else 0.0)
    
    eps = 1e-10
    if scale_mode == 'log':
        s = np.log1p(np.maximum(spectrum, 0.0))
        spectrum_normalized = s / (s.max() + eps)
    elif scale_mode == 'sqrt':
        s = np.sqrt(np.maximum(spectrum, 0.0))
        spectrum_normalized = s / (s.max() + eps)
    elif scale_mode == 'raw':
        spectrum_normalized = spectrum / (raw_max + eps)
    else:
        spectrum_normalized = spectrum / (raw_max + eps)
    
    # Make peaks crisper by boosting mid/high values slightly
    spectrum_normalized = np.power(spectrum_normalized, 1.6)
    
    diagnostics = {'raw_max': raw_max, 'raw_min': raw_min}
    
    return wl_array, spectrum_normalized, component_counts, diagnostics


def wavelength_to_rgb(wl):
    """
    Convert wavelength (nm) to approximate RGB color.
    
    Args:
        wl (float): Wavelength in nm (typically 400–750)
    
    Returns:
        tuple: (R, G, B) with values 0–1
    """
    if wl < 380 or wl > 750:
        return (0, 0, 0)
    
    if wl < 440:
        r = -(wl - 440) / (440 - 380)
        g, b = 0, 1
    elif wl < 490:
        r, g, b = 0, (wl - 440) / (490 - 440), 1
    elif wl < 510:
        r, g, b = 0, 1, -(wl - 510) / (510 - 490)
    elif wl < 580:
        r, g, b = (wl - 510) / (580 - 510), 1, 0
    elif wl < 645:
        r, g, b = 1, -(wl - 645) / (645 - 580), 0
    else:
        r, g, b = 1, 0, 0
    
    # Gamma correction for better visibility
    gamma = 0.8
    r, g, b = r ** gamma, g ** gamma, b ** gamma
    
    return (r, g, b)


def render_spectrum(spectral_data, dark_mode=True, figsize=(14, 4), scale_mode='normalize'):
    """
    Render spectrum as 2D heatmap image using wavelength-to-RGB mapping.
    
    Args:
        spectral_data (dict): Output from load_spectral_data()
        dark_mode (bool): If True, dark background; if False, light background
        figsize (tuple): Figure size (width, height)
    
    Returns:
        matplotlib.figure.Figure: Rendered figure
    """
    
    title = spectral_data['title']
    if not title or title is None:
        title = generate_random_title()
    
    # Always auto-detect top-N (server-side). Medium sensitivity rules:
    # - Use SciPy `find_peaks` if available (height threshold ~2% of max, prominence percentile 40)
    # - If SciPy missing, use a NumPy local-max + percentile fallback
    # - min_sep_nm = 0 (no enforced nm gap)
    keep_top_n = int(spectral_data.get('keep_top_n', 0) or 0)
    # first build (unfiltered) to get raw stats for auto-pick
    wl_array, spectrum_normalized, component_counts, raw_stats = build_spectrum_array(
        spectral_data['wavelengths'],
        spectral_data['intensities'],
        spectral_data['width_factors'],
        spectral_data['actions'],
        scale_mode='raw',
        keep_top_n=0
    )

    if keep_top_n == 0:
        # reconstruct raw (unnormalized) spectrum from returned normalized + raw_max
        raw_max = float(raw_stats.get('raw_max', 0.0) or 0.0)
        raw_s = spectrum_normalized * (raw_max if raw_max > 0 else 1.0)

        auto_n = 0
        try:
            from scipy.signal import find_peaks, savgol_filter
            dw = wl_array[1] - wl_array[0]
            min_sep_nm = 0.0
            min_sep_idx = int(round(min_sep_nm / dw)) if dw > 0 else 0

            # Use Savitzky-Golay smoothing for detection only (preserve raw mapping)
            smooth_window = int(spectral_data.get('detection_smooth_window', 41))
            polyorder = int(spectral_data.get('detection_smooth_polyorder', 3))
            if raw_s.size <= 3:
                raw_s_for_detect = raw_s.copy()
            else:
                # ensure window is odd and <= signal length
                if smooth_window >= raw_s.size:
                    smooth_window = int(raw_s.size) - (1 - (raw_s.size % 2))
                if smooth_window < 3:
                    smooth_window = 3
                if smooth_window % 2 == 0:
                    smooth_window += 1
                try:
                    raw_s_for_detect = savgol_filter(raw_s, smooth_window, polyorder)
                except Exception:
                    raw_s_for_detect = raw_s.copy()

            # Use dynamic prominence based on raw range but applied to smoothed signal
            prominence_percentage = 0.08
            grey_val_range = float(raw_s.max() - raw_s.min()) if raw_s.size else 0.0
            dynamic_prominence = prominence_percentage * grey_val_range
            peaks, props = find_peaks(raw_s_for_detect, prominence=dynamic_prominence, distance=min_sep_idx)

            # Cluster nearby peaks and keep only the single maximum per cluster
            if peaks.size:
                # Cluster nearby peaks but preserve true multiplets using valley-depth test.
                # For each adjacent pair within group_gap_nm we compute the valley (min between)
                # and only merge if the valley is sufficiently high relative to the smaller peak.
                group_gap_nm = 1.0
                valley_rel_thresh = 0.5  # merge when valley >= 50% of smaller peak height
                dw = wl_array[1] - wl_array[0]
                group_gap_idx = max(1, int(round(group_gap_nm / dw))) if dw > 0 else 1
                peaks_sorted = np.sort(peaks)
                clusters = []
                cur = [peaks_sorted[0]]
                for p in peaks_sorted[1:]:
                    # if far apart, finalize cluster
                    if p - cur[-1] > group_gap_idx:
                        clusters.append(cur)
                        cur = [p]
                        continue
                    # compute valley between last in cluster and this peak
                    lo = int(cur[-1])
                    hi = int(p)
                    if hi <= lo:
                        cur.append(p)
                        continue
                    # use the detection-space (smoothed) values for valley/peak comparisons
                    valley = float(np.min(raw_s_for_detect[lo:hi+1]))
                    last_peak_val = float(raw_s_for_detect[cur[-1]])
                    this_peak_val = float(raw_s_for_detect[p])
                    smaller = min(last_peak_val, this_peak_val)
                    # merge if valley is high relative to smaller peak (i.e., no deep notch)
                    if smaller > 0 and (valley / smaller) >= valley_rel_thresh:
                        cur.append(p)
                    else:
                        clusters.append(cur)
                        cur = [p]
                clusters.append(cur)
                # pick the strongest index in each cluster (by raw_s value)
                chosen = []
                for cl in clusters:
                    vals = raw_s[np.array(cl)]
                    chosen_idx = cl[int(np.argmax(vals))]
                    chosen.append(int(chosen_idx))
                peaks = np.array(chosen, dtype=int)

            auto_n = int(peaks.size)
        except Exception:
            # NumPy fallback: local maxima + 95th percentile height check
            s = raw_s
            auto_n = 0
            if s.size >= 3:
                candidates = np.where((s[1:-1] > s[:-2]) & (s[1:-1] > s[2:]))[0] + 1
                if candidates.size:
                    pos = s[s > 0]
                    height_thr = raw_max * 0.02 if raw_max > 0 else 0.0
                    perc_thr = np.percentile(pos, 95) if pos.size else 0.0
                    thr = max(height_thr, perc_thr)
                    peaks = candidates[s[candidates] >= thr]
                    # cluster nearby peaks similarly to SciPy branch using valley-depth merging
                    if peaks.size:
                        group_gap_nm = 1.0
                        valley_rel_thresh = 0.5
                        dw = wl_array[1] - wl_array[0]
                        group_gap_idx = max(1, int(round(group_gap_nm / dw))) if dw > 0 else 1
                        peaks_sorted = np.sort(peaks)
                        clusters = []
                        cur = [peaks_sorted[0]]
                        for p in peaks_sorted[1:]:
                            if p - cur[-1] > group_gap_idx:
                                clusters.append(cur)
                                cur = [p]
                                continue
                            lo = int(cur[-1])
                            hi = int(p)
                            if hi <= lo:
                                cur.append(p)
                                continue
                            valley = float(np.min(s[lo:hi+1]))
                            last_peak_val = float(s[cur[-1]])
                            this_peak_val = float(s[p])
                            smaller = min(last_peak_val, this_peak_val)
                            if smaller > 0 and (valley / smaller) >= valley_rel_thresh:
                                cur.append(p)
                            else:
                                clusters.append(cur)
                                cur = [p]
                        clusters.append(cur)
                        chosen = []
                        for cl in clusters:
                            vals = s[np.array(cl)]
                            chosen_idx = cl[int(np.argmax(vals))]
                            chosen.append(int(chosen_idx))
                        peaks = np.array(chosen, dtype=int)
                    auto_n = int(peaks.size)
                else:
                    auto_n = int((s > (raw_max * 0.02)).sum())
            else:
                auto_n = int((s > 0).sum())

        keep_top_n = max(0, int(auto_n))
        diagnostics = spectral_data.get('diagnostics', {})
        diagnostics['auto_keep_top_n'] = keep_top_n
        spectral_data['diagnostics'] = diagnostics

    # Auto-select scale if requested
    if scale_mode in (None, 'auto'):
        chosen_mode = choose_scale_mode(raw_stats.get('raw_min', 0.0), raw_stats.get('raw_max', 0.0))
    else:
        chosen_mode = scale_mode

    # Auto-select scale if requested
    if scale_mode in (None, 'auto'):
        chosen_mode = choose_scale_mode(raw_stats.get('raw_min', 0.0), raw_stats.get('raw_max', 0.0))
    else:
        chosen_mode = scale_mode

    # apply top-N filtering only when using 'normalize'
    apply_keep = keep_top_n if chosen_mode == 'normalize' else 0
    wl_array, spectrum_normalized, component_counts, raw_stats = build_spectrum_array(
        spectral_data['wavelengths'],
        spectral_data['intensities'],
        spectral_data['width_factors'],
        spectral_data['actions'],
        scale_mode=chosen_mode,
        keep_top_n=apply_keep
    )    

    # Expose raw stats and the chosen mode for the UI / diagnostics
    diagnostics = spectral_data.get('diagnostics', {})
    diagnostics.update({
        'spectrum_raw_max': raw_stats.get('raw_max'),
        'spectrum_raw_min': raw_stats.get('raw_min'),
        'spectrum_scale_mode': chosen_mode,
        'spectrum_auto_requested': (scale_mode in (None, 'auto'))
    })
    spectral_data['diagnostics'] = diagnostics
    
    # Colab-style detection on the discrete input intensities (preserve original mapping)
    colab_peaks = []
    try:
        input_wls = np.array(spectral_data.get('wavelengths', []))
        input_vals = np.array(spectral_data.get('intensities', []))
        if input_wls.size and input_vals.size and input_wls.size == input_vals.size:
            mask = (input_wls >= wl_array.min()) & (input_wls <= wl_array.max())
            input_wls_f = input_wls[mask]
            input_vals_f = input_vals[mask]
            if input_vals_f.size:
                # Ensure data are ordered by wavelength (Colab sorts by nm)
                order = np.argsort(input_wls_f)
                input_wls_f = input_wls_f[order]
                input_vals_f = input_vals_f[order]
                min_g = float(np.min(input_vals_f))
                max_g = float(np.max(input_vals_f))
                rng = max_g - min_g
                if rng == 0:
                    norm_vals = np.ones_like(input_vals_f)
                else:
                    norm_vals = (input_vals_f - min_g) / (rng if rng != 0 else 1.0)

                prom_pct = float(spectral_data.get('colab_prominence', 0.12))
                dyn_prom = prom_pct * rng
                from scipy.signal import find_peaks as _find_peaks
                peaks_idx, props = _find_peaks(input_vals_f, prominence=dyn_prom)

                # Compute peak-relative normalization so brightness is relative
                # to other detected peaks (peak with max intensity -> 1.0)
                if peaks_idx.size:
                    peak_vals = input_vals_f[np.array(peaks_idx, dtype=int)]
                    peak_max = float(peak_vals.max()) if peak_vals.size else 0.0
                    peak_min = float(peak_vals.min()) if peak_vals.size else 0.0
                else:
                    peak_max = 0.0
                    peak_min = 0.0

                for pi in np.atleast_1d(peaks_idx):
                    iv = float(input_vals_f[int(pi)])
                    # norm across entire input (keeps old diagnostic) and peak-relative norm
                    global_norm = float(norm_vals[int(pi)])
                    peak_norm = (iv / peak_max) if peak_max > 0 else global_norm
                    colab_peaks.append({
                        'wl': float(input_wls_f[int(pi)]),
                        'intensity': iv,
                        'norm': global_norm,
                        'peak_norm': float(peak_norm)
                    })
    except Exception:
        colab_peaks = []

    diagnostics['colab_detected_peaks'] = colab_peaks
    spectral_data['diagnostics'] = diagnostics

    # Optionally highlight only the Colab-detected primary peaks in the heatmap
    keep_only_colab = bool(spectral_data.get('colab_highlight_only', True))
    colab_keep_width_nm = float(spectral_data.get('colab_keep_width_nm', 0.0))

    if keep_only_colab and colab_peaks:
        # Optionally disable the continuous heatmap entirely so only vlines remain
        show_heatmap = bool(spectral_data.get('colab_show_heatmap', False))
        if not show_heatmap:
            # Build a synthetic display composed only of detected peaks with
            # per-peak Gaussian cores + glow. Each peak's amplitude is
            # scaled by `peak_norm` so brightness is relative to detected
            # peaks (max -> 1.0).
            # Instead of building a single 1D spectrum display, collect
            # each peak's horizontal component (gauss+glow) without applying
            # the peak-relative amplitude. We'll composite vertically later
            # so the vertical 'shine' can be scaled per-peak by `peak_norm`.
            peak_components = []  # list of (h_array, rel)
            dw = wl_array[1] - wl_array[0]
            # default glow/core width (nm) when keep width not provided
            default_width_nm = float(spectral_data.get('colab_default_width_nm', 0.6))
            glow_strength = float(spectral_data.get('colab_glow_strength', 1.0))
            # allow tuning how strongly the shine scales with peak intensity
            shine_exp = float(spectral_data.get('colab_shine_exponent', 1.6))
            for p in colab_peaks:
                try:
                    center = float(p['wl'])
                    rel = float(p.get('peak_norm', p.get('norm', 1.0)))
                    # amplify contrast by exponentiating rel (>1 increases contrast)
                    try:
                        rel = float(rel) ** float(shine_exp)
                    except Exception:
                        pass
                    # choose sigma from user-provided keep width or default
                    width_nm = colab_keep_width_nm if colab_keep_width_nm > 0 else default_width_nm
                    # scale horizontal width by peak-relative strength so
                    # brighter peaks render slightly wider (configurable)
                    width_scale = float(spectral_data.get('colab_width_scale', 1.0))
                    sigma = max(1e-6, width_nm * (1.0 + width_scale * rel))
                    # gaussian across wavelength grid (unscaled)
                    gauss = np.exp(-0.5 * ((wl_array - center) / sigma) ** 2)
                    # add a slightly broader glow component (unscaled)
                    glow_sigma = sigma * 2.2
                    glow = np.exp(-0.5 * ((wl_array - center) / glow_sigma) ** 2)
                    horiz = gauss + (glow_strength * 0.35) * glow
                    peak_components.append((horiz, rel))
                except Exception:
                    continue
            # store for later composite; build a conservative 1D sum for diagnostics
            spectrum_display = np.clip(sum(h for h, _ in peak_components) if peak_components else np.zeros_like(spectrum_normalized), 0.0, 1.0)
            diagnostics['suppress_colab_vlines'] = True
            diagnostics['colab_peak_components_count'] = len(peak_components)
        else:
            # build mask over wl_array preserving small neighborhoods around detected peaks
            mask = np.zeros_like(spectrum_normalized, dtype=bool)
            dw = wl_array[1] - wl_array[0]
            # If keep width <= 0, only preserve the exact wavelength index for each detected peak
            if colab_keep_width_nm <= 0:
                for p in colab_peaks:
                    idx = int(np.argmin(np.abs(wl_array - float(p['wl']))))
                    mask[idx] = True
            else:
                half_idx = max(1, int(round((colab_keep_width_nm / 2.0) / dw))) if dw > 0 else 1
                for p in colab_peaks:
                    # find nearest index
                    idx = int(np.argmin(np.abs(wl_array - float(p['wl']))))
                    lo = max(0, idx - half_idx)
                    hi = min(len(mask), idx + half_idx + 1)
                    mask[lo:hi] = True
            # Build simple multiplet groups for diagnostics: peaks within 0.5 nm
            try:
                group_gap_nm = float(spectral_data.get('colab_multiplet_gap_nm', 0.5))
                peak_wls = np.array([p['wl'] for p in colab_peaks])
                multiplet_groups = []
                if peak_wls.size:
                    order = np.argsort(peak_wls)
                    sorted_wls = peak_wls[order]
                    cur = [sorted_wls[0]]
                    for w in sorted_wls[1:]:
                        if w - cur[-1] <= group_gap_nm:
                            cur.append(w)
                        else:
                            multiplet_groups.append(cur)
                            cur = [w]
                    multiplet_groups.append(cur)
                diagnostics['colab_multiplet_groups'] = multiplet_groups
            except Exception:
                diagnostics['colab_multiplet_groups'] = []
            spectrum_display = spectrum_normalized * mask.astype(float)
    
    else:
        spectrum_display = spectrum_normalized

    # Build heatmap: rows = intensity over wavelength, columns = wavelength
    # Increase vertical resolution for nicer vertical glow rendering
    num_rows = int(spectral_data.get('colab_num_rows', 200))
    heatmap = np.tile(spectrum_display, (num_rows, 1))
    
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread")
        fig, ax = plt.subplots(figsize=figsize)
    
    # Map each column to its wavelength color
    rgb_image = np.zeros((num_rows, len(wl_array), 3))
    for i, wl in enumerate(wl_array):
        r, g, b = wavelength_to_rgb(wl)
        rgb_image[:, i, :] = [r, g, b]
    
    # Apply intensity profile to brightness with a vertical Gaussian envelope
    # so each detected peak appears as a tall luminous column with a bright
    # central core and a softer outer glow.
    # Vertical envelope parameters (fractions of image height)
    v_core_sigma = float(spectral_data.get('colab_vert_core_sigma', 0.045))
    v_glow_sigma = float(spectral_data.get('colab_vert_glow_sigma', 0.16))
    v_glow_amp = float(spectral_data.get('colab_vert_glow_amp', 1.1))
    v_core_amp = float(spectral_data.get('colab_vert_core_amp', 1.2))

    y = np.linspace(0.0, 1.0, num_rows)
    core_profile = v_core_amp * np.exp(-0.5 * ((y - 0.5) / v_core_sigma) ** 2)
    glow_profile = v_glow_amp * np.exp(-0.5 * ((y - 0.5) / v_glow_sigma) ** 2)
    base_profile = core_profile + glow_profile
    # Subtract narrow tip Gaussians at top and bottom to create a slim-top,
    # fat-middle, slim-bottom silhouette similar to the reference image.
    tip_cut_amp = float(spectral_data.get('colab_vert_tip_cut_amp', 0.95))
    tip_cut_sigma = float(spectral_data.get('colab_vert_tip_cut_sigma', 0.012))
    top_tip = tip_cut_amp * np.exp(-0.5 * ((y - 1.0) / tip_cut_sigma) ** 2)
    bot_tip = tip_cut_amp * np.exp(-0.5 * ((y - 0.0) / tip_cut_sigma) ** 2)
    vertical_profile = base_profile - (top_tip + bot_tip)
    # clamp and normalize
    vertical_profile = np.clip(vertical_profile, 0.0, None)
    if vertical_profile.max() > 0:
        vertical_profile = vertical_profile / float(vertical_profile.max())

    # User-tunable: allow subtle reduction of the diffuse glow and boost of
    # the sharp core so colors appear crisper. Conservative defaults keep
    # prior behaviour but let you tune via `spectral_data`.
    colab_glow_reduce = float(spectral_data.get('colab_glow_reduce', 1.0))
    colab_core_boost = float(spectral_data.get('colab_core_boost', 1.0))
    if (colab_glow_reduce != 1.0) or (colab_core_boost != 1.0):
        core_profile_adj = v_core_amp * colab_core_boost * np.exp(-0.5 * ((y - 0.5) / v_core_sigma) ** 2)
        glow_profile_adj = (v_glow_amp * colab_glow_reduce) * np.exp(-0.5 * ((y - 0.5) / v_glow_sigma) ** 2)
        base_profile_adj = core_profile_adj + glow_profile_adj
        vertical_profile = base_profile_adj - (top_tip + bot_tip)
        vertical_profile = np.clip(vertical_profile, 0.0, None)
        if vertical_profile.max() > 0:
            vertical_profile = vertical_profile / float(vertical_profile.max())

    # If we built per-peak components earlier (synthetic display), composite
    # a 2D profile where each peak's vertical envelope is scaled by its rel.
    if diagnostics.get('suppress_colab_vlines', False) and 'peak_components' in locals():
        profile2d = np.zeros((num_rows, len(wl_array)))
        for horiz, rel in peak_components:
            # each peak contributes rel * horiz horizontally, modulated by the
            # same vertical_profile (so shine scales with rel)
            profile2d += vertical_profile[:, None] * (rel * horiz)[None, :]
        # normalize composite to [0,1]
        if profile2d.max() > 0:
            profile2d = profile2d / float(profile2d.max())
        for i in range(3):
            rgb_image[:, :, i] *= profile2d
    else:
        profile2d = heatmap * vertical_profile[:, None]
        for i in range(3):
            rgb_image[:, :, i] *= profile2d

    # Increase color saturation slightly (configurable) to make peak hues
    # appear sharper without changing hue. Defaults are conservative.
    try:
        colab_sat_scale = float(spectral_data.get('colab_sat_scale', 1.15))
    except Exception:
        colab_sat_scale = 1.0
    if colab_sat_scale != 1.0:
        from matplotlib import colors as mcolors
        # reshape to Nx3 for conversion
        flat = rgb_image.reshape(-1, 3)
        try:
            hsv = mcolors.rgb_to_hsv(flat.copy())
            hsv[:, 1] = np.clip(hsv[:, 1] * colab_sat_scale, 0.0, 1.0)
            rgb_sharp = mcolors.hsv_to_rgb(hsv)
            rgb_image = np.clip(rgb_sharp.reshape(rgb_image.shape), 0.0, 1.0)
        except Exception:
            pass
    
    ax.imshow(rgb_image, aspect='auto', extent=[wl_array.min(), wl_array.max(), 0, 1], origin='lower')
    
    # Configure axes
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('')
    # raise title slightly to keep it above rotated/attached labels
    ax.set_title(title, fontsize=14, fontweight='bold', y=1.06)
    ax.set_yticks([])
    
    # Tick marks: major labeled every 50 nm, minor every 10 nm
    major_ticks = [400, 450, 500, 550, 600, 650, 700, 750]
    ax.set_xticks(major_ticks)
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    
    # Background color
    if dark_mode:
        ax.set_facecolor('#1a1a1a')
        fig.patch.set_facecolor('#0d0d0d')
        ax.tick_params(colors='white', labelsize=10)
        ax.spines['bottom'].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')
        ax.tick_params(which='minor', length=4, colors='white')
    else:
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        ax.tick_params(colors='black', labelsize=10)
        ax.spines['bottom'].set_color('black')
        ax.xaxis.label.set_color('black')
        ax.title.set_color('black')
    
    # allow a bit of vertical headroom so labels above the peaks are visible
    try:
        ax.set_ylim(-0.02, 1.12)
    except Exception:
        pass

    # Draw Colab-style vertical peak lines (do not mutate original intensities)
    min_brightness = float(spectral_data.get('colab_min_brightness', 0.1))
    # linewidth range when scaled by peak intensity
    min_lw = float(spectral_data.get('colab_min_linewidth', 1.0))
    max_lw = float(spectral_data.get('colab_max_linewidth', 6.0))
    # Optional peak labels (configurable)
    show_labels = bool(spectral_data.get('colab_show_labels', True))
    label_field = spectral_data.get('colab_label_field', 'wl')
    label_fmt = spectral_data.get('colab_label_format', '{:.1f} nm')
    try:
        label_fontsize = float(spectral_data.get('colab_label_fontsize', 9))
    except Exception:
        label_fontsize = 9
    try:
        label_offset = float(spectral_data.get('colab_label_offset', 0.02))
    except Exception:
        label_offset = 0.02
    # ensure a minimal offset so labels aren't clipped by tight layout
    if label_offset < 0.03:
        label_offset = 0.04
    try:
        label_rotation = float(spectral_data.get('colab_label_rotation', 60.0))
    except Exception:
        label_rotation = 60.0
    try:
        label_xoffset_nm = float(spectral_data.get('colab_label_xoffset_nm', 2.0))
    except Exception:
        label_xoffset_nm = 2.0
    # If diagnostics requested suppression (we've rendered synthetic glows), skip vlines
    suppress_vlines = diagnostics.get('suppress_colab_vlines', False)
    if not suppress_vlines:
        for p in colab_peaks:
            try:
                base_rgb = wavelength_to_rgb(p['wl'])
                # prefer peak-relative normalization if available
                rel = float(p.get('peak_norm', p.get('norm', 1.0)))
                final_intensity_scale = min_brightness + (1.0 - min_brightness) * rel
                colored_rgb = (base_rgb[0] * final_intensity_scale,
                               base_rgb[1] * final_intensity_scale,
                               base_rgb[2] * final_intensity_scale)
                # scale linewidth so brighter peaks draw thicker lines
                lw = float(min_lw + (max_lw - min_lw) * rel)
                ax.vlines(x=p['wl'], ymin=0, ymax=1, color=colored_rgb, linewidth=lw)
                if show_labels:
                    try:
                        # build label text
                        if label_field == 'wl':
                            txt = label_fmt.format(float(p['wl']))
                        elif label_field == 'intensity':
                            txt = label_fmt.format(float(p.get('intensity', 0.0)))
                        elif label_field == 'both':
                            txt = '{} / {}'.format(label_fmt.format(float(p['wl'])), label_fmt.format(float(p.get('intensity', 0.0))))
                        else:
                            txt = str(p.get(label_field, p.get('wl')))

                        # decide color for label
                        label_color_override = spectral_data.get('colab_label_color', None)
                        if label_color_override:
                            col = label_color_override
                        else:
                            b = wavelength_to_rgb(p['wl'])
                            rel2 = float(p.get('peak_norm', p.get('norm', 1.0)))
                            final_intensity_scale2 = min_brightness + (1.0 - min_brightness) * rel2
                            col = (b[0] * final_intensity_scale2, b[1] * final_intensity_scale2, b[2] * final_intensity_scale2)
                            if dark_mode and sum(col) < 0.12:
                                col = 'white'

                        # attach label to the top of the visible peak using the
                        # rendered profile (preferred) or fall back to rgb brightness
                        try:
                            idx = int(np.argmin(np.abs(wl_array - float(p['wl']))))
                        except Exception:
                            idx = 0
                        try:
                            if 'profile2d' in locals():
                                col_profile = np.asarray(profile2d)[:, idx]
                            else:
                                col_profile = rgb_image[:, idx, :].mean(axis=1)
                            j = int(np.nanargmax(col_profile))
                            # find the top edge of the peak (highest row above threshold)
                            peak_max = float(np.nanmax(col_profile)) if np.nanmax(col_profile) > 0 else 0.0
                            thresh = peak_max * 0.2
                            try:
                                inds = np.where(col_profile > thresh)[0]
                                if inds.size:
                                    top_idx = int(np.nanmax(inds))
                                else:
                                    top_idx = j
                            except Exception:
                                top_idx = j
                            y_val = float(top_idx) / float(max(1, num_rows - 1))
                        except Exception:
                            y_val = 0.6
                        # place label slightly above the peak top
                        y_pos = min(1.05, y_val + max(0.02, label_offset))
                        # prefer theme-contrasting color and add an outline
                        try:
                            pix = rgb_image[j, idx, :]
                            lum = 0.2126 * pix[0] + 0.7152 * pix[1] + 0.0722 * pix[2]
                        except Exception:
                            lum = 0.0
                        if dark_mode:
                            lab_col = 'white'
                            stroke_col = 'black'
                        else:
                            lab_col = 'black'
                            stroke_col = 'white'
                        # follow Colab: center-aligned at peak wavelength, slightly above top
                        x_pos = float(p['wl']) + float(spectral_data.get('colab_label_xoffset_nm', 0.0))
                        txt_obj = ax.text(x_pos, y_pos, txt,
                            fontsize=label_fontsize, ha='center', va='bottom',
                            color='white', rotation=label_rotation, rotation_mode='anchor',
                            transform=ax.transData, clip_on=False)
                        try:
                            import matplotlib.patheffects as pe
                            txt_obj.set_path_effects([pe.Stroke(linewidth=2, foreground=stroke_col), pe.Normal()])
                        except Exception:
                            pass
                    except Exception:
                        pass
            except Exception:
                continue
    else:
        # draw faint outer rim if desired (keeps silhouette but doesn't block glow)
        rim_alpha = float(spectral_data.get('colab_synthetic_rim_alpha', 0.12))
        rim_lw = float(spectral_data.get('colab_synthetic_rim_lw', 1.0))
        for p in colab_peaks:
            try:
                base_rgb = wavelength_to_rgb(p['wl'])
                rim_col = (base_rgb[0] * rim_alpha, base_rgb[1] * rim_alpha, base_rgb[2] * rim_alpha)
                ax.vlines(x=p['wl'], ymin=0, ymax=1, color=rim_col, linewidth=rim_lw)
                if show_labels:
                    try:
                        # simple label text (wavelength)
                        txt = label_fmt.format(float(p['wl'])) if label_field in ('wl', 'both') else str(p.get(label_field, p.get('wl')))
                        col = 'white' if dark_mode else 'black'
                        try:
                            if 'profile2d' in locals():
                                col_profile = np.asarray(profile2d)[:, idx]
                            else:
                                col_profile = rgb_image[:, idx, :].mean(axis=1)
                            j = int(np.nanargmax(col_profile))
                            peak_max = float(np.nanmax(col_profile)) if np.nanmax(col_profile) > 0 else 0.0
                            thresh = peak_max * 0.2
                            try:
                                inds = np.where(col_profile > thresh)[0]
                                if inds.size:
                                    top_idx = int(np.nanmax(inds))
                                else:
                                    top_idx = j
                            except Exception:
                                top_idx = j
                            y_val = float(top_idx) / float(max(1, num_rows - 1))
                        except Exception:
                            y_val = 0.6
                        y_pos = min(1.05, y_val + max(0.02, label_offset))
                        try:
                            pix = rgb_image[j, idx, :]
                            lum = 0.2126 * pix[0] + 0.7152 * pix[1] + 0.0722 * pix[2]
                        except Exception:
                            lum = 0.0
                        if dark_mode:
                            lab_col = 'white'
                            stroke_col = 'black'
                        else:
                            lab_col = 'black'
                            stroke_col = 'white'
                        x_pos = float(p['wl']) + float(spectral_data.get('colab_label_xoffset_nm', 0.0))
                        txt_obj = ax.text(x_pos, y_pos, txt,
                            fontsize=label_fontsize, ha='center', va='bottom',
                            color='white', rotation=label_rotation, rotation_mode='anchor',
                            transform=ax.transData, clip_on=False)
                        try:
                            import matplotlib.patheffects as pe
                            txt_obj.set_path_effects([pe.Stroke(linewidth=2, foreground=stroke_col), pe.Normal()])
                        except Exception:
                            pass
                    except Exception:
                        pass
            except Exception:
                continue

    plt.tight_layout()
    
    return fig
