import glob,csv
csvs = glob.glob('outputs/he_test_colab_peaks_*.csv')
print('csvs', sorted(csvs))
if not csvs:
    raise SystemExit('no csvs')
latest = sorted(csvs)[-1]
print('latest', latest)
with open(latest,newline='') as f:
    r=csv.DictReader(f)
    rows=list(r)
print('rows:', len(rows))
for row in rows:
    print(row)
