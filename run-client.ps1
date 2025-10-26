<#
Run the PyChat GUI client and connect to a server.

Usage (PowerShell):
  .\run-client.ps1                # uses default server ws://162.43.92.97:8765
  .\run-client.ps1 -Server ws://host:8765

This script will prefer the bundled venv at `.venv` if present.
#>

param(
    [string]$Server = "ws://162.43.92.97:8765"
)

Push-Location -LiteralPath (Split-Path -Path $MyInvocation.MyCommand.Definition -Parent)
try {
    $venvPy = Join-Path -Path (Get-Location) -ChildPath ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) {
        & $venvPy -m app.main --server $Server
    }
    else {
        python -m app.main --server $Server
    }
}
finally {
    Pop-Location
}
