[CmdletBinding()]
param([switch]$Reload)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$UvicornArgs = @('fashion_cad_api.main:app', '--app-dir', "$ProjectRoot\apps\api", '--host', '127.0.0.1', '--port', '8000')
if ($Reload) { $UvicornArgs += '--reload' }
& "$ProjectRoot\environments\api-venv\Scripts\python.exe" -m uvicorn @UvicornArgs
