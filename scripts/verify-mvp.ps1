[CmdletBinding()]
param([switch]$SkipModelVerification)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot 'environments\api-venv\Scripts\python.exe'
$Npm = (Get-Command npm.cmd -ErrorAction Stop).Source
if (-not (Test-Path $Python)) { throw "No existe el entorno API local. Ejecutar .\scripts\setup-local.ps1 primero." }

& "$PSScriptRoot\setup-local.ps1" -BenchmarkOnly
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Push-Location $ProjectRoot
try {
    $pytestTemp = Join-Path $ProjectRoot ("cache\temp\verify-mvp-" + [guid]::NewGuid().ToString('N'))
    & $Python -m pytest apps/api/tests -q --basetemp $pytestTemp
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Push-Location (Join-Path $ProjectRoot 'apps\mcp-server')
    try {
        & $Npm run build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally { Pop-Location }

    Push-Location (Join-Path $ProjectRoot 'apps\studio-web')
    try {
        & $Npm run build
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally { Pop-Location }

    if (-not $SkipModelVerification) {
        & "$PSScriptRoot\verify-semantic-rebuild.ps1"
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
} finally { Pop-Location }

Write-Host 'MVP local verificado. La validacion fisica de patrones y Studio Operator sigue siendo un paso humano obligatorio.'
