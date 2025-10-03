<#
Simple helper to open the combined HTML in the default browser on Windows.
Run from PowerShell in the project folder:
    .\serve.ps1
#>
$file = Resolve-Path .\combined.html -ErrorAction SilentlyContinue
if (-not $file) {
    Write-Error "combined.html not found in the current folder: $(Get-Location)"
    exit 1
}

Write-Host "Opening combined.html in default browser..."
Start-Process $file

Write-Host "If you'd like a static server, install Python and run: python -m http.server 8000"
