import win32com.client, os
excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
print('AddIns:')
for i in range(1, excel.AddIns.Count+1):
    a = excel.AddIns.Item(i)
    try:
        print(i, a.Name, 'Installed=', a.Installed, 'FullName=', a.FullName)
    except Exception as e:
        print('err', e)

print('\nCOMAddIns:')
for i in range(1, excel.COMAddIns.Count+1):
    c = excel.COMAddIns.Item(i)
    try:
        print(i, c.Description, 'ProgId=', c.ProgId, 'Connect=', c.Connect)
    except Exception as e:
        print('err', e)

# look for xlwings.xlam loaded
for i in range(1, excel.Workbooks.Count+1):
    print('Workbook', i, excel.Workbooks(i).Name)

excel.Quit()
