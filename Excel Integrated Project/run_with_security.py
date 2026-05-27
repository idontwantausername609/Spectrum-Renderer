import win32com.client, os, time
import xlwings
addinx = os.path.join(os.path.dirname(xlwings.__file__), 'addin', 'xlwings.xlam')
wbpath = os.path.abspath('sample_workbook.xlsm')
excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = True
# lower automation security
try:
    prev = excel.AutomationSecurity
except Exception:
    prev = None
try:
    excel.AutomationSecurity = 1
except Exception:
    pass

try:
    wb_addin = excel.Workbooks.Open(addinx)
    wb = excel.Workbooks.Open(wbpath)
    time.sleep(0.5)
    try:
        print('RunPython ->', excel.Run('RunPython','import sys; print("xlwings loaded")'))
    except Exception as e:
        print('RunPython failed:', e)
finally:
    # restore security if possible
    try:
        if prev is not None:
            excel.AutomationSecurity = prev
    except Exception:
        pass
# keep excel open for inspection
print('Done')
