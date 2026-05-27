import glob
import csv
import os
from datetime import datetime
from spectrum.rendering import wavelength_to_rgb

# find latest peaks CSV
csvs = glob.glob('outputs/he_test_colab_peaks_*.csv')
if not csvs:
    raise SystemExit('No peaks CSV found in outputs/')
latest = sorted(csvs)[-1]

peaks = []
with open(latest, newline='') as f:
    reader = csv.DictReader(f)
    for r in reader:
        try:
            peaks.append({'wl': float(r.get('wl')), 'peak_norm': float(r.get('peak_norm'))})
        except Exception:
            continue

if not peaks:
    raise SystemExit('no peaks read')

import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(15, 2))
ax.set_facecolor('black')
plt.xlim(400, 750)
plt.ylim(0, 1)
ax.set_yticks([])

num_rows = 200
y_coords = np.linspace(0.0, 1.0, num_rows)
min_needle_max_width_nm = 0.2
max_needle_max_width_nm = 0.8
needle_shape_power = 4.0
glow_width_multiplier = 1.5
glow_alpha = 0.25
width_profile_factor = (4.0 * y_coords * (1.0 - y_coords)) ** needle_shape_power

for p in peaks:
    peak_nm = p['wl']
    rel = p['peak_norm']
    final_intensity_scale = 0.1 + (1.0 - 0.1) * rel
    base_rgb = wavelength_to_rgb(peak_nm)
    colored_rgb = (base_rgb[0] * final_intensity_scale,
                   base_rgb[1] * final_intensity_scale,
                   base_rgb[2] * final_intensity_scale)

    scaled_max_width_nm = min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * rel

    glow_current_widths_nm = scaled_max_width_nm * glow_width_multiplier * width_profile_factor
    glow_x_left = peak_nm - glow_current_widths_nm / 2.0
    glow_x_right = peak_nm + glow_current_widths_nm / 2.0
    ax.fill_betweenx(y_coords, glow_x_left, glow_x_right, facecolor=colored_rgb, alpha=glow_alpha)

    current_widths_nm = scaled_max_width_nm * width_profile_factor
    x_left = peak_nm - current_widths_nm / 2.0
    x_right = peak_nm + current_widths_nm / 2.0
    ax.fill_betweenx(y_coords, x_left, x_right, facecolor=colored_rgb)

ts = datetime.now().strftime('%Y%m%d-%H%M%S')
out_path = os.path.join('outputs', f'emulate_colab_dark_{ts}.png')
fig.savefig(out_path, dpi=300, bbox_inches='tight')
print('Wrote', out_path)
