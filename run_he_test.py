from spectrum.loader import load_spectral_data
from spectrum.rendering import render_spectrum
import matplotlib.pyplot as plt
import csv

infile = 'he test.xlsx'
from datetime import datetime
ts = datetime.now().strftime('%Y%m%d-%H%M%S')
try:
    sd = load_spectral_data(infile, sheet_name=None, user_title='he test')
except Exception as e:
    print('Load error:', e)
    raise

# Render dark and save (timestamped)
fig = render_spectrum(sd, dark_mode=True, figsize=(14,4), scale_mode='auto')
dark_path = f'outputs/he_test_dark_colab_{ts}.png'
fig.savefig(dark_path, dpi=150, bbox_inches='tight')
plt.close(fig)

# Render light and save (timestamped)
fig2 = render_spectrum(sd, dark_mode=False, figsize=(14,4), scale_mode='auto')
light_path = f'outputs/he_test_light_colab_{ts}.png'
fig2.savefig(light_path, dpi=150, bbox_inches='tight')
plt.close(fig2)

# Export detected peaks from diagnostics
peaks = sd.get('diagnostics', {}).get('colab_detected_peaks', [])
csv_path = f'outputs/he_test_colab_peaks_{ts}.csv'
with open(csv_path, 'w', newline='') as f:
    # include peak-relative normalization (`peak_norm`) when available
    writer = csv.DictWriter(f, fieldnames=['wl','intensity','norm','peak_norm'])
    writer.writeheader()
    for p in peaks:
        writer.writerow(p)

print('Wrote', dark_path, light_path, csv_path)
