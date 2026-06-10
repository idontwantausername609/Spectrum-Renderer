# PowerShell launcher for Spectrum webapp
# Usage: Right-click -> Run with PowerShell, or run from terminal:
#   powershell -ExecutionPolicy Bypass -File .\run_webapp2.ps1

$ErrorActionPreference = 'Stop'

# Try to initialize conda (modern installers provide condabin hook)
$condaHook = Join-Path $env:USERPROFILE "anaconda3\shell\condabin\conda-hook.ps1"
if (Test-Path $condaHook) {
    . $condaHook
    conda activate base
} else {
    Write-Output "Could not find conda hook at $condaHook. Proceeding without activating conda."
}

# Start the webapp in a new window and open the browser
$pythonExe = "python"
Start-Process -FilePath $pythonExe -ArgumentList "webapp2.py" -WorkingDirectory (Get-Location)
Start-Sleep -Seconds 1
Start-Process "http://localhost:8000/"

Write-Output "Webapp started; browser should open shortly."
