import json
import pandas as pd
from annotator import detect_peaks_from_arrays, make_annotated_plot

print('Loading he test.xlsx')
df = pd.read_excel('he test.xlsx')
if df.shape[1] < 2:
    raise SystemExit('Excel must have at least two columns: wavelength, intensity')
wl = df.iloc[:, 0].to_numpy(dtype=float)
inten = df.iloc[:, 1].to_numpy(dtype=float)
peaks = detect_peaks_from_arrays(wl, inten)
make_annotated_plot(wl, inten, peaks, out_path='outputs/annotated_cli.png')
with open('outputs/detected_from_excel.json', 'w') as jf:
    json.dump(peaks, jf, indent=2)
print('Wrote outputs/annotated_cli.png and outputs/detected_from_excel.json')
