import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
from generic_render import get_spectra

# Ensure local package dir is first on sys.path
p = Path(__file__).resolve().parent
if str(p) not in sys.path:
    sys.path.insert(0, str(p))

def main():
    inp = p / 'oxygen nist 2.xlsx'
    if not inp.exists():
        raise SystemExit(f'Missing input workbook: {inp}')

    df = pd.read_excel(inp, sheet_name=0)

    out_dir = p / 'outputs'
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')

    for mode in ('dark', 'light'):
        fname = out_dir / f'local_render_{mode}_{ts}.png'
        fig = get_spectra(
            df,
            mode=mode,
            save_path=fname,
        )
    
        try:
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception:
            pass
    
        print('Wrote', fname)


if __name__ == '__main__':
    main()
