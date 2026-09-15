$ProjectRoot = Split-Path -Parent $PSScriptRoot
& "$ProjectRoot\environments\api-venv\Scripts\python.exe" -m uvicorn fashion_cad_api.main:app --app-dir "$ProjectRoot\apps\api" --reload --host 127.0.0.1 --port 8000
