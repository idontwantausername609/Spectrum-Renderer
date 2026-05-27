import sys
import os
import json
from pathlib import Path
proj = Path(__file__).resolve().parent
sys.path.insert(0, str(proj))
from annotator import detect_peaks_from_arrays, make_annotated_plot
import numpy as np
import pandas as pd

def main():
    if len(sys.argv) < 2:
        print('Usage: process_selection.py <csv_path>')
        sys.exit(1)
    csv = sys.argv[1]
    df = pd.read_csv(csv, header=None)
    if df.shape[1] < 2:
        print('CSV must have at least two columns')
        sys.exit(1)
    wl = df.iloc[:,0].to_numpy(dtype=float)
    inten = df.iloc[:,1].to_numpy(dtype=float)
    peaks = detect_peaks_from_arrays(wl, inten)
    out_path = os.path.join(proj, 'outputs', 'annotated_from_shell.png')
    make_annotated_plot(wl, inten, peaks, out_path=out_path)
    out_json = os.path.join(proj, 'outputs', 'detected_from_shell.json')
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, 'w') as jf:
        json.dump(peaks, jf, indent=2)
    print('Wrote', out_path, out_json)

if __name__ == '__main__':
    main()
