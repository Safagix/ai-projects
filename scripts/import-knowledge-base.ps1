[CmdletBinding()]
param(
    [switch]$Ocr,
    [ValidateRange(1, 1500)]
    [int]$MaxOcrPages = 300
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot 'environments\api-venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw "No existe el entorno API local. Ejecutar .\scripts\setup-local.ps1 primero." }

$env:FASHION_CAD_ROOT = $ProjectRoot
$env:PYTHONPATH = Join-Path $ProjectRoot 'apps\api'
$CliArgs = @('--all')
if ($Ocr) {
    $CliArgs += '--ocr'
    $CliArgs += '--max-ocr-pages'
    $CliArgs += $MaxOcrPages
}
& $Python -m fashion_cad_api.knowledge_cli @CliArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Biblioteca textual actualizada. En Studio, usar RECONSTRUIR ÍNDICE SEMÁNTICO para publicar el índice BGE-M3.'
