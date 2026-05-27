from spectrum.loader import load_spectral_data
import os
from collections import Counter

# Test with the Oxygen NIST Excel file
excel_file = "Oxygen NIST.xlsx"
if os.path.exists(excel_file):
    try:
        spectral_data = load_spectral_data(excel_file, user_title="Test Oxygen")
        print(f"✓ Successfully loaded {spectral_data['diagnostics']['total_lines']} spectral lines")
        print(f"  Sheet: {spectral_data['sheet_name']}")
        print(f"  Title: {spectral_data['title']}")
        print(f"  Action distribution: {Counter(spectral_data['actions'])}")
        if spectral_data['diagnostics']['raw_descriptors']:
            print(f"  Raw descriptors found: {list(spectral_data['diagnostics']['raw_descriptors'].keys())[:5]}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"✗ File not found: {excel_file}")
