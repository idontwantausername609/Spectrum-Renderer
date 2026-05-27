import xlwings, os, win32com.client, time
print('xlwings package at', xlwings.__file__)
addinx = os.path.join(os.path.dirname(xlwings.__file__), 'addin', 'xlwings.xlam')
print('Looking for add-in at', addinx)
if not os.path.exists(addinx):
    print('Add-in not found at expected location')
else:
    excel = win32com.client.DispatchEx('Excel.Application')
    excel.Visible = True
    try:
        wb_addin = excel.Workbooks.Open(addinx)
        print('Opened add-in workbook', wb_addin.Name)
        time.sleep(0.5)
        try:
            print('RunPython test ->', excel.Run('RunPython','import sys; print("xlwings loaded")'))
        except Exception as e:
            print('RunPython call failed:', e)
    finally:
        # do not close addin so it remains loaded
        pass
