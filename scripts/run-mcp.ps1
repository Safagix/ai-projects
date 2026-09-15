[CmdletBinding()]
param(
    [ValidatePattern('^https?://')]
    [string]$ApiUrl = 'http://127.0.0.1:8000'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Node = Get-Command node -ErrorAction SilentlyContinue
if (-not $Node) { throw 'Node.js no está disponible. Instalar Node antes de iniciar el conector MCP.' }

$Entry = Join-Path $ProjectRoot 'apps\mcp-server\dist\index.js'
if (-not (Test-Path -LiteralPath $Entry)) {
    & npm --prefix (Join-Path $ProjectRoot 'apps\mcp-server') run build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$env:FASHION_CAD_API_URL = $ApiUrl
& $Node.Source $Entry
