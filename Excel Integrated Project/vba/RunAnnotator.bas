Attribute VB_Name = "RunAnnotatorModule"
Sub RunAnnotator()
    ' Requires xlwings add-in to be installed in Excel
    On Error Resume Next
    Dim sPath As String, sEsc As String, pyCmd As String
    Dim logf As String, fh As Integer
    logf = """" & ThisWorkbook.Path & "\\outputs\\run_annotator_log.txt" & """"
    fh = FreeFile()
    On Error Resume Next
    Open ThisWorkbook.Path & "\\outputs\\run_annotator_log.txt" For Append As #fh
    If Err.Number = 0 Then
        Print #fh, Now() & " - RunAnnotator start"
        Close #fh
    End If
    On Error Resume Next
    sPath = "C:\Users\viran\Downloads\indep. project\Graphing\Excel Integrated Project\sample_workbook.xlsm;C:\Users\viran\Downloads\indep. project\Graphing\Excel Integrated Project\.venv\Lib\site-packages\xlwings\addin\xlwings.xlam"
    sEsc = Replace(sPath, "\", "\\")
    pyCmd = "import xlwings as xw; xw.utils.prepare_sys_path('true;" & sEsc & ";;;;'); import runpython_probe; import annotator; annotator.launch_with_selection()"
    ' Prefer shell fallback for reliability
    fh = FreeFile()
    On Error Resume Next
    Open ThisWorkbook.Path & "\\outputs\\run_annotator_log.txt" For Append As #fh
    If Err.Number = 0 Then
        Print #fh, Now() & " - invoking Shell fallback"
        Close #fh
    End If
    Dim py As String, cmd As String
    py = ThisWorkbook.Path & "\\.venv\\Scripts\\python.exe"
    ' Export current selection to CSV for the external processor
    Dim sel As Object, r As Long, c As Long, rr As Long, cc As Long
    Dim csvPath As String, fnum As Integer, line As String
    csvPath = ThisWorkbook.Path & "\\outputs\\selection_from_vba.csv"
    On Error Resume Next
    Set sel = Application.Selection
    If sel Is Nothing Then
        ' nothing selected
        fh = FreeFile()
        Open ThisWorkbook.Path & "\\outputs\\run_annotator_log.txt" For Append As #fh
        Print #fh, Now() & " - no selection"
        Close #fh
        Exit Sub
    End If
    rr = sel.Rows.Count
    cc = sel.Columns.Count
    fnum = FreeFile()
    Open csvPath For Output As #fnum
    For r = 1 To rr
        line = ""
        For c = 1 To cc
            If c > 1 Then line = line & ","
            line = line & CStr(sel.Cells(r, c).Value)
        Next c
        Print #fnum, line
    Next r
    Close #fnum
    ' Call processing script with CSV path
    cmd = Chr(34) & py & Chr(34) & " " & Chr(34) & ThisWorkbook.Path & "\\process_selection.py" & Chr(34) & " " & Chr(34) & csvPath & Chr(34)
    Shell cmd, vbNormalFocus
    fh = FreeFile()
    On Error Resume Next
    Open ThisWorkbook.Path & "\\outputs\\run_annotator_log.txt" For Append As #fh
    If Err.Number = 0 Then
        Print #fh, Now() & " - Shell fallback invoked: " & cmd
        Close #fh
    End If
    Exit Sub
End Sub
