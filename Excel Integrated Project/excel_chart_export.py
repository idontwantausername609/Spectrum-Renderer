from pathlib import Path
import win32com.client
import sys
proj = Path(__file__).resolve().parent
wb_path = proj / 'sample_workbook.xlsm'
out = proj / 'outputs' / 'excel_chart.png'
excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb = excel.Workbooks.Open(str(wb_path))
    sht = wb.Worksheets(1)
    used = sht.UsedRange
    # assume first two columns are x and y
    rng = sht.Range(sht.Cells(1,1), sht.Cells(used.Rows.Count, 2))
    chartObj = sht.ChartObjects().Add(Left=100, Top=100, Width=800, Height=300)
    chart = chartObj.Chart
    chart.ChartType = 4  # xlLine = 4
    ser = chart.SeriesCollection().NewSeries()
    ser.Name = '="Series1"'
    ser.Values = sht.Range(sht.Cells(1,2), sht.Cells(used.Rows.Count, 2))
    ser.XValues = sht.Range(sht.Cells(1,1), sht.Cells(used.Rows.Count, 1))
    # formatting: match Excel defaults
    chart.HasTitle = True
    chart.ChartTitle.Text = 'Annotated Spectrum (Excel-rendered)'
    # export
    out.parent.mkdir(parents=True, exist_ok=True)
    chart.Export(str(out))
    # clean up: delete chart object
    chartObj.Delete()
    wb.Close(SaveChanges=False)
finally:
    excel.Quit()
print('Exported', out)
