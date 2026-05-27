import pandas as pd
import numpy as np
from scipy.signal import find_peaks

fn = 'he test.xlsx'
# try common sheet names
xls = pd.read_excel(fn, sheet_name=None)
print('sheets:', list(xls.keys()))
# pick first sheet
df = pd.read_excel(fn, sheet_name=0)
print('columns:', df.columns.tolist()[:10])
# attempt to find nm and Grey Val columns
cols = [c.lower() for c in df.columns]
nm_col = None
val_col = None
for c in df.columns:
    cl = str(c).lower()
    if nm_col is None and ('nm' in cl or 'wavelength' in cl or 'wave' in cl or 'lambda' in cl):
        nm_col = c
    if val_col is None and ('grey' in cl or 'grey val' in cl or 'intensity' in cl or 'value' in cl):
        val_col = c
print('nm_col, val_col:', nm_col, val_col)
if nm_col is None or val_col is None:
    print('Could not auto-detect columns; show first rows:')
    print(df.head())
    raise SystemExit(1)

# Filter range
df_filtered = df[(df[nm_col] >= 400) & (df[nm_col] <= 750)].copy()
df_filtered = df_filtered.sort_values(by=nm_col).reset_index(drop=True)

min_grey_val = df_filtered[val_col].min()
max_grey_val = df_filtered[val_col].max()
grey_val_range = max_grey_val - min_grey_val
print('min,max,range:', min_grey_val, max_grey_val, grey_val_range)

if grey_val_range == 0:
    df_filtered['Normalized_Grey_Val'] = 1.0
else:
    df_filtered['Normalized_Grey_Val'] = (df_filtered[val_col] - min_grey_val) / grey_val_range

prominence_percentage = 0.12
dynamic_prominence = prominence_percentage * grey_val_range

peaks, props = find_peaks(df_filtered[val_col].values, prominence=dynamic_prominence)
print('peaks count:', peaks.size)
peaks_rows = df_filtered.iloc[peaks][[nm_col, val_col, 'Normalized_Grey_Val']]
print(peaks_rows)
peaks_rows.to_csv('outputs/he_test_colab_repro_peaks.csv', index=False)
print('wrote outputs/he_test_colab_repro_peaks.csv')
