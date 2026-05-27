from spectrum.loader import load_spectral_data
from spectrum.rendering import render_spectrum
import matplotlib.pyplot as plt
from datetime import datetime

infile = 'he test.xlsx'
try:
    sd = load_spectral_data(infile, sheet_name=None, user_title='he emulate')
except Exception as e:
    print('Load error:', e)
    raise

# Tweak parameters to emulate provided image: crisper core, less diffuse glow, higher saturation
overrides = {
    'colab_sat_scale': 1.6,
    'colab_glow_reduce': 0.55,
    'colab_core_boost': 1.35,
    'colab_width_scale': 0.25,
    'colab_default_width_nm': 0.4,
    'colab_vert_core_sigma': 0.03,
    'colab_vert_glow_sigma': 0.14,
    'colab_vert_tip_cut_amp': 0.98,
    'colab_shine_exponent': 1.6,
    'colab_min_brightness': 0.2,
    'colab_min_linewidth': 0.6,
    'colab_max_linewidth': 3.0,
    'colab_synthetic_rim_alpha': 0.0,
    'colab_show_heatmap': False,
    'colab_highlight_only': True
}

sd.update(overrides)

ts = datetime.now().strftime('%Y%m%d-%H%M%S')

# Render dark
fig = render_spectrum(sd, dark_mode=True, figsize=(14,4), scale_mode='auto')
dark_path = f'outputs/he_emulate_dark_{ts}.png'
fig.savefig(dark_path, dpi=150, bbox_inches='tight')
plt.close(fig)

# Render light
fig2 = render_spectrum(sd, dark_mode=False, figsize=(14,4), scale_mode='auto')
light_path = f'outputs/he_emulate_light_{ts}.png'
fig2.savefig(light_path, dpi=150, bbox_inches='tight')
plt.close(fig2)

print('Wrote', dark_path, light_path)
