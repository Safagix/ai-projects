[CmdletBinding()]
param([switch]$BenchmarkOnly)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$cache = Join-Path $ProjectRoot 'cache'
$env:HF_HOME = Join-Path $cache 'huggingface'
$env:TRANSFORMERS_CACHE = $env:HF_HOME
$env:TORCH_HOME = Join-Path $cache 'torch'
$env:PIP_CACHE_DIR = Join-Path $cache 'pip'
$env:npm_config_cache = Join-Path $cache 'npm'
$env:TEMP = Join-Path $cache 'temp'
$env:TMP = $env:TEMP
$env:OLLAMA_MODELS = Join-Path $ProjectRoot 'models\ollama'

$requiredDirectories = @(
  $cache,
  (Join-Path $ProjectRoot 'data\library'),
  (Join-Path $ProjectRoot 'data\lancedb'),
  (Join-Path $ProjectRoot 'artifacts')
)
New-Item -ItemType Directory -Force -Path $requiredDirectories | Out-Null

$drive = Get-Volume -DriveLetter D
$freeGb = [math]::Round($drive.SizeRemaining / 1GB, 2)
if ($freeGb -lt 30) { throw "Espacio insuficiente en D:. Libres: $freeGb GB; se requieren al menos 30 GB." }

Write-Host "Fashion CAD root: $ProjectRoot"
Write-Host "Espacio libre en D:: $freeGb GB"
Write-Host "Caché de modelos: $env:HF_HOME"
if ($BenchmarkOnly) { exit 0 }

$venv = Join-Path $ProjectRoot 'environments\api-venv'
if (-not (Test-Path $venv)) { python -m venv $venv }
& "$venv\Scripts\python.exe" -m pip install --upgrade pip
& "$venv\Scripts\python.exe" -m pip install -e "$ProjectRoot\apps\api[dev]"

Push-Location "$ProjectRoot\apps\studio-web"
& (Get-Command npm.cmd -ErrorAction Stop).Source install
Pop-Location

Push-Location "$ProjectRoot\apps\mcp-server"
& (Get-Command npm.cmd -ErrorAction Stop).Source install
Pop-Location
