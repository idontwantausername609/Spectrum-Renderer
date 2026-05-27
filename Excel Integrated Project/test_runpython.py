import win32com.client, time, os
p = os.path.abspath('sample_workbook.xlsm')
# start Excel and allow macros to run for this automation
excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = True
# Temporarily lower automation security to allow macros (1 = msoAutomationSecurityLow)
prev_sec = None
try:
    prev_sec = excel.AutomationSecurity
except Exception:
    prev_sec = None
try:
    excel.AutomationSecurity = 1
except Exception:
    pass
wb = excel.Workbooks.Open(p)
# small pause
time.sleep(0.5)
try:
    res = excel.Run('RunPython', 'import sys; print("xlwings ok")')
    print('RunPython returned:', res)
except Exception as e:
    print('RunPython failed:', e)
finally:
    # restore security
    try:
        if prev_sec is not None:
            excel.AutomationSecurity = prev_sec
    except Exception:
        pass
