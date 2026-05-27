import sys
from pathlib import Path
import traceback
try:
    import win32com.client
except Exception as e:
    print('pywin32 missing:', e); sys.exit(1)
proj = Path(__file__).resolve().parent
wb = proj / 'sample_workbook.xlsm'
excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb_obj = excel.Workbooks.Open(str(wb))
    sht = wb_obj.Worksheets(1)
    # write sample data (wavelength, intensity)
    data = [
        (400, 10),
        (410, 15),
        (420, 8),
        (430, 20),
        (440, 5),
        (450, 12)
    ]
    for i, (w, inten) in enumerate(data, start=1):
        sht.Cells(i,1).Value = w
        sht.Cells(i,2).Value = inten
    # select the data range
    rng = sht.Range(sht.Cells(1,1), sht.Cells(len(data),2))
    rng.Select()
    try:
        print('Running macro...')
        excel.Application.Run('RunAnnotatorModule.RunAnnotator')
        print('Macro run completed')
    except Exception:
        print('Exception when running macro:')
        traceback.print_exc()
    finally:
        wb_obj.Save()
        wb_obj.Close(SaveChanges=True)
finally:
    excel.Quit()
print('Done')
