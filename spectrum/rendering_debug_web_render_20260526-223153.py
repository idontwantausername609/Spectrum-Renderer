"""
Backup of rendering.py corresponding to debug_web_render.png (2026-05-26 22:31)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .utils import generate_random_title
from matplotlib.ticker import MultipleLocator

def choose_scale_mode(raw_min, raw_max, eps=1e-10):
    try:
        raw_min_f = float(raw_min)
        raw_max_f = float(raw_max)
    except Exception:
        return 'normalize'
    rng = raw_max_f - raw_min_f
    if raw_max_f <= 0 or rng <= eps:
        return 'raw'
    if raw_max_f / (rng + eps) > 100.0:
        return 'log'
    if raw_max_f > 1000.0:
        return 'sqrt'
    return 'normalize'

BASE_SIGMA = 0.12
BROAD_FACTOR = 1.20
BLEND_FACTOR = 0.70
BLEND_INTENSITY = 0.95
GLOW_STRENGTH = 0.14
ACTION_INTENSITY_FACTOR = 0.50

def build_spectrum_array(wavelengths, intensities, width_factors, actions,
                         wl_min=400, wl_max=750, resolution=4096,
                         scale_mode='raw', keep_top_n=0):
    wl_array = np.linspace(wl_min, wl_max, resolution)
    spectrum = np.zeros_like(wl_array, dtype=float)
    component_counts = {}
    min_sep_nm = 0.0

    for wl, intensity, width_mult, action in zip(wavelengths, intensities,
                                                   width_factors, actions):
        if wl < wl_min or wl > wl_max:
            continue
        action_key = action if action else 'line'
        component_counts[action_key] = component_counts.get(action_key, 0) + 1
        if 'broad' in action_key.lower():
            intensity = intensity * ACTION_INTENSITY_FACTOR
        sigma_base = BASE_SIGMA
        if 'broad' in action_key.lower():
            sigma = sigma_base * width_mult * BROAD_FACTOR
        elif 'blend' in action_key.lower():
            sigma = sigma_base * width_mult * BLEND_FACTOR
        else:
            sigma = sigma_base * width_mult
        core = intensity * np.exp(-0.5 * ((wl_array - wl) / sigma) ** 2)
        glow_sigma = sigma * 1.8
        glow = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - wl) / glow_sigma) ** 2)
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
        if 'broad' in action_key.lower():
            intensity = intensity * ACTION_INTENSITY_FACTOR
        sigma_base = BASE_SIGMA
        if 'broad' in action_key.lower():
            sigma = sigma_base * width_mult * BROAD_FACTOR
        elif 'blend' in action_key.lower():
            sigma = sigma_base * width_mult * BLEND_FACTOR
        else:
            sigma = sigma_base * width_mult
        core = intensity * np.exp(-0.5 * ((wl_array - wl) / sigma) ** 2)
        glow_sigma = sigma * 1.8
        glow = (intensity * GLOW_STRENGTH) * np.exp(-0.5 * ((wl_array - wl) / glow_sigma) ** 2)
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

    if keep_top_n and keep_top_n > 0:
        s = spectrum.copy()
        dw = wl_array[1] - wl_array[0]
        min_sep_idx = max(1, int(round(min_sep_nm / dw)))
        idx_desc = np.argsort(s)[::-1]
        idx_desc = idx_desc[s[idx_desc] > 0]
        accepted = []
        for idx in idx_desc:
            if all(abs(idx - a) > min_sep_idx for a in accepted):
                accepted.append(int(idx))
                if len(accepted) >= keep_top_n:
                    break
        if len(accepted) < keep_top_n:
            for idx in idx_desc:
                if int(idx) not in accepted:
                    accepted.append(int(idx))
                    if len(accepted) >= keep_top_n:
                        break
        mask = np.zeros_like(s, dtype=bool)
        for a in accepted:
            lo = max(0, a - min_sep_idx)
            hi = min(len(s), a + min_sep_idx + 1)
            mask[lo:hi] = True
        spectrum = s * mask.astype(float)    

    raw_max = float(spectrum.max() if spectrum.size else 0.0)
    raw_min = float(spectrum.min() if spectrum.size else 0.0)
    background_thresh = raw_max * 0.005
    if background_thresh > 0:
        spectrum[spectrum < background_thresh] = 0.0
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
    spectrum_normalized = np.power(spectrum_normalized, 1.6)
    diagnostics = {'raw_max': raw_max, 'raw_min': raw_min}
    return wl_array, spectrum_normalized, component_counts, diagnostics


def wavelength_to_rgb(wl):
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
    gamma = 0.8
    r, g, b = r ** gamma, g ** gamma, b ** gamma
    return (r, g, b)

# Full `render_spectrum` logic copied from `rendering.py` to preserve exact behavior
# for reproducing `debug_web_render.png`.

def render_spectrum(spectral_data, dark_mode=True, figsize=(14, 4), scale_mode='normalize'):
    title = spectral_data['title']
    if not title or title is None:
        title = generate_random_title()
    keep_top_n = int(spectral_data.get('keep_top_n', 0) or 0)
    wl_array, spectrum_normalized, component_counts, raw_stats = build_spectrum_array(
        spectral_data['wavelengths'],
        spectral_data['intensities'],
        spectral_data['width_factors'],
        spectral_data['actions'],
        scale_mode='raw',
        keep_top_n=0
    )

    if keep_top_n == 0:
        raw_max = float(raw_stats.get('raw_max', 0.0) or 0.0)
        raw_s = spectrum_normalized * (raw_max if raw_max > 0 else 1.0)
        auto_n = 0
        try:
            from scipy.signal import find_peaks, savgol_filter
            dw = wl_array[1] - wl_array[0]
            min_sep_nm = 0.0
            min_sep_idx = int(round(min_sep_nm / dw)) if dw > 0 else 0
            smooth_window = int(spectral_data.get('detection_smooth_window', 41))
            polyorder = int(spectral_data.get('detection_smooth_polyorder', 3))
            if raw_s.size <= 3:
                raw_s_for_detect = raw_s.copy()
            else:
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

            prominence_percentage = 0.08
            grey_val_range = float(raw_s.max() - raw_s.min()) if raw_s.size else 0.0
            dynamic_prominence = prominence_percentage * grey_val_range
            peaks, props = find_peaks(raw_s_for_detect, prominence=dynamic_prominence, distance=min_sep_idx)
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
                    valley = float(np.min(raw_s_for_detect[lo:hi+1]))
                    last_peak_val = float(raw_s_for_detect[cur[-1]])
                    this_peak_val = float(raw_s_for_detect[p])
                    smaller = min(last_peak_val, this_peak_val)
                    if smaller > 0 and (valley / smaller) >= valley_rel_thresh:
                        cur.append(p)
                    else:
                        clusters.append(cur)
                        cur = [p]
                clusters.append(cur)
                chosen = []
                for cl in clusters:
                    vals = raw_s[np.array(cl)]
                    chosen_idx = cl[int(np.argmax(vals))]
                    chosen.append(int(chosen_idx))
                peaks = np.array(chosen, dtype=int)
            auto_n = int(peaks.size)
        except Exception:
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

    if scale_mode in (None, 'auto'):
        chosen_mode = choose_scale_mode(raw_stats.get('raw_min', 0.0), raw_stats.get('raw_max', 0.0))
    else:
        chosen_mode = scale_mode

    if scale_mode in (None, 'auto'):
        chosen_mode = choose_scale_mode(raw_stats.get('raw_min', 0.0), raw_stats.get('raw_max', 0.0))
    else:
        chosen_mode = scale_mode

    apply_keep = keep_top_n if chosen_mode == 'normalize' else 0
    wl_array, spectrum_normalized, component_counts, raw_stats = build_spectrum_array(
        spectral_data['wavelengths'],
        spectral_data['intensities'],
        spectral_data['width_factors'],
        spectral_data['actions'],
        scale_mode=chosen_mode,
        keep_top_n=apply_keep
    )    

    diagnostics = spectral_data.get('diagnostics', {})
    diagnostics.update({
        'spectrum_raw_max': raw_stats.get('raw_max'),
        'spectrum_raw_min': raw_stats.get('raw_min'),
        'spectrum_scale_mode': chosen_mode,
        'spectrum_auto_requested': (scale_mode in (None, 'auto'))
    })
    spectral_data['diagnostics'] = diagnostics
    colab_peaks = []
    try:
        input_wls = np.array(spectral_data.get('wavelengths', []))
        input_vals = np.array(spectral_data.get('intensities', []))
        if input_wls.size and input_vals.size and input_wls.size == input_vals.size:
            mask = (input_wls >= wl_array.min()) & (input_wls <= wl_array.max())
            input_wls_f = input_wls[mask]
            input_vals_f = input_vals[mask]
            if input_vals_f.size:
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
                if peaks_idx.size:
                    peak_vals = input_vals_f[np.array(peaks_idx, dtype=int)]
                    peak_max = float(peak_vals.max()) if peak_vals.size else 0.0
                    peak_min = float(peak_vals.min()) if peak_vals.size else 0.0
                else:
                    peak_max = 0.0
                    peak_min = 0.0

                for pi in np.atleast_1d(peaks_idx):
                    iv = float(input_vals_f[int(pi)])
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
    keep_only_colab = bool(spectral_data.get('colab_highlight_only', True))
    colab_keep_width_nm = float(spectral_data.get('colab_keep_width_nm', 0.0))
    if keep_only_colab and colab_peaks:
        show_heatmap = bool(spectral_data.get('colab_show_heatmap', False))
        if not show_heatmap:
            peak_components = []
            dw = wl_array[1] - wl_array[0]
            default_width_nm = float(spectral_data.get('colab_default_width_nm', 0.6))
            glow_strength = float(spectral_data.get('colab_glow_strength', 1.0))
            shine_exp = float(spectral_data.get('colab_shine_exponent', 1.6))
            for p in colab_peaks:
                try:
                    center = float(p['wl'])
                    rel = float(p.get('peak_norm', p.get('norm', 1.0)))
                    try:
                        rel = float(rel) ** float(shine_exp)
                    except Exception:
                        pass
                    width_nm = colab_keep_width_nm if colab_keep_width_nm > 0 else default_width_nm
                    width_scale = float(spectral_data.get('colab_width_scale', 1.0))
                    sigma = max(1e-6, width_nm * (1.0 + width_scale * rel))
                    gauss = np.exp(-0.5 * ((wl_array - center) / sigma) ** 2)
                    glow_sigma = sigma * 2.2
                    glow = np.exp(-0.5 * ((wl_array - center) / glow_sigma) ** 2)
                    horiz = gauss + (glow_strength * 0.35) * glow
                    peak_components.append((horiz, rel))
                except Exception:
                    continue
            spectrum_display = np.clip(sum(h for h, _ in peak_components) if peak_components else np.zeros_like(spectrum_normalized), 0.0, 1.0)
            diagnostics['suppress_colab_vlines'] = True
            diagnostics['colab_peak_components_count'] = len(peak_components)
        else:
            mask = np.zeros_like(spectrum_normalized, dtype=bool)
            dw = wl_array[1] - wl_array[0]
            if colab_keep_width_nm <= 0:
                for p in colab_peaks:
                    idx = int(np.argmin(np.abs(wl_array - float(p['wl']))))
                    mask[idx] = True
            else:
                half_idx = max(1, int(round((colab_keep_width_nm / 2.0) / dw))) if dw > 0 else 1
                for p in colab_peaks:
                    idx = int(np.argmin(np.abs(wl_array - float(p['wl']))))
                    lo = max(0, idx - half_idx)
                    hi = min(len(mask), idx + half_idx + 1)
                    mask[lo:hi] = True
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
    num_rows = int(spectral_data.get('colab_num_rows', 200))
    heatmap = np.tile(spectrum_display, (num_rows, 1))
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread")
        fig, ax = plt.subplots(figsize=figsize)
    rgb_image = np.zeros((num_rows, len(wl_array), 3))
    for i, wl in enumerate(wl_array):
        r, g, b = wavelength_to_rgb(wl)
        rgb_image[:, i, :] = [r, g, b]
    v_core_sigma = float(spectral_data.get('colab_vert_core_sigma', 0.045))
    v_glow_sigma = float(spectral_data.get('colab_vert_glow_sigma', 0.16))
    v_glow_amp = float(spectral_data.get('colab_vert_glow_amp', 1.1))
    v_core_amp = float(spectral_data.get('colab_vert_core_amp', 1.2))
    y = np.linspace(0.0, 1.0, num_rows)
    core_profile = v_core_amp * np.exp(-0.5 * ((y - 0.5) / v_core_sigma) ** 2)
    glow_profile = v_glow_amp * np.exp(-0.5 * ((y - 0.5) / v_glow_sigma) ** 2)
    base_profile = core_profile + glow_profile
    tip_cut_amp = float(spectral_data.get('colab_vert_tip_cut_amp', 0.95))
    tip_cut_sigma = float(spectral_data.get('colab_vert_tip_cut_sigma', 0.012))
    top_tip = tip_cut_amp * np.exp(-0.5 * ((y - 1.0) / tip_cut_sigma) ** 2)
    bot_tip = tip_cut_amp * np.exp(-0.5 * ((y - 0.0) / tip_cut_sigma) ** 2)
    vertical_profile = base_profile - (top_tip + bot_tip)
    vertical_profile = np.clip(vertical_profile, 0.0, None)
    if vertical_profile.max() > 0:
        vertical_profile = vertical_profile / float(vertical_profile.max())
    if diagnostics.get('suppress_colab_vlines', False) and 'peak_components' in locals():
        profile2d = np.zeros((num_rows, len(wl_array)))
        for horiz, rel in peak_components:
            profile2d += vertical_profile[:, None] * (rel * horiz)[None, :]
        if profile2d.max() > 0:
            profile2d = profile2d / float(profile2d.max())
        for i in range(3):
            rgb_image[:, :, i] *= profile2d
    else:
        profile2d = heatmap * vertical_profile[:, None]
        for i in range(3):
            rgb_image[:, :, i] *= profile2d
    ax.imshow(rgb_image, aspect='auto', extent=[wl_array.min(), wl_array.max(), 0, 1])
    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_yticks([])
    major_ticks = [400, 450, 500, 550, 600, 650, 700, 750]
    ax.set_xticks(major_ticks)
    ax.xaxis.set_minor_locator(MultipleLocator(10))
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
    min_brightness = float(spectral_data.get('colab_min_brightness', 0.1))
    min_lw = float(spectral_data.get('colab_min_linewidth', 1.0))
    max_lw = float(spectral_data.get('colab_max_linewidth', 6.0))
    suppress_vlines = diagnostics.get('suppress_colab_vlines', False)
    if not suppress_vlines:
        for p in colab_peaks:
            try:
                base_rgb = wavelength_to_rgb(p['wl'])
                rel = float(p.get('peak_norm', p.get('norm', 1.0)))
                final_intensity_scale = min_brightness + (1.0 - min_brightness) * rel
                colored_rgb = (base_rgb[0] * final_intensity_scale,
                               base_rgb[1] * final_intensity_scale,
                               base_rgb[2] * final_intensity_scale)
                lw = float(min_lw + (max_lw - min_lw) * rel)
                ax.vlines(x=p['wl'], ymin=0, ymax=1, color=colored_rgb, linewidth=lw)
            except Exception:
                continue
    else:
        rim_alpha = float(spectral_data.get('colab_synthetic_rim_alpha', 0.12))
        rim_lw = float(spectral_data.get('colab_synthetic_rim_lw', 1.0))
        for p in colab_peaks:
            try:
                base_rgb = wavelength_to_rgb(p['wl'])
                rim_col = (base_rgb[0] * rim_alpha, base_rgb[1] * rim_alpha, base_rgb[2] * rim_alpha)
                ax.vlines(x=p['wl'], ymin=0, ymax=1, color=rim_col, linewidth=rim_lw)
            except Exception:
                continue
    plt.tight_layout()
    return fig
