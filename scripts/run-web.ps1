$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location "$ProjectRoot\apps\studio-web"
& (Get-Command npm.cmd -ErrorAction Stop).Source run dev
