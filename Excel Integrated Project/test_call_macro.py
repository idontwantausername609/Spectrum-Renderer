import sys
import traceback
from pathlib import Path
try:
    import win32com.client
except Exception as e:
    print('pywin32 missing:', e)
    sys.exit(1)
proj = Path(__file__).resolve().parent
wb = proj / 'sample_workbook.xlsm'
if not wb.exists():
    print('Workbook not found:', wb)
    sys.exit(1)

excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb_obj = excel.Workbooks.Open(str(wb))
    try:
        print('Attempting Application.Run RunAnnotatorModule.RunAnnotator')
        excel.Application.Run('RunAnnotatorModule.RunAnnotator')
        print('Run completed (no exception)')
    except Exception:
        print('Exception when running macro:')
        traceback.print_exc()
    finally:
        wb_obj.Close(SaveChanges=False)
finally:
    excel.Quit()
print('Done')
