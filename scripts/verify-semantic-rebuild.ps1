[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot 'environments\api-venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw "No existe el entorno API local. Ejecutar .\scripts\setup-local.ps1 primero." }

$runId = [guid]::NewGuid().ToString('N')
$verificationRoot = Join-Path $ProjectRoot "cache\delivery-verification\$runId"
$env:FASHION_CAD_ROOT = $ProjectRoot
$env:FASHION_CAD_DATA_DIR = Join-Path $verificationRoot 'data'
$env:FASHION_CAD_ARTIFACTS_DIR = Join-Path $verificationRoot 'artifacts'
$env:PYTHONPATH = Join-Path $ProjectRoot 'apps\api'

$verification = @'
import time
import uuid

from fashion_cad_api.repository import Repository
from fashion_cad_api.vector_store import BgeM3Embedder, LanceSemanticStore

repository = Repository()
repository.initialize()
repository.add_rag_document(
    "Ficha de verificacion nylon",
    "El nylon reciclado para un bolso requiere evidencia de origen y resistencia a la abrasion.",
    "delivery-verification.md",
    chunk_number=1,
)
rows = repository.list_rag_documents()
embedder = BgeM3Embedder()
started = time.perf_counter()
embedder.ensure_available()
store = LanceSemanticStore()

first = store.build(rows, job_id=str(uuid.uuid4()), embedder=embedder, should_cancel=lambda: False, on_progress=lambda *_: None)
previous = repository.activate_semantic_index(first.table_name, first.source_count)
store.drop_managed_table(previous)
active = repository.get_semantic_index()
assert active and active["table_name"] == first.table_name
assert LanceSemanticStore(first.table_name).count() == 1

second = store.build(rows, job_id=str(uuid.uuid4()), embedder=embedder, should_cancel=lambda: False, on_progress=lambda *_: None)
previous = repository.activate_semantic_index(second.table_name, second.source_count)
store.drop_managed_table(previous)
assert previous == first.table_name
assert LanceSemanticStore(second.table_name).count() == 1
hits = LanceSemanticStore(second.table_name).search(embedder.embed_query("nylon reciclado bolso"), 1)
assert len(hits) == 1 and hits[0].chunk_id and hits[0].source == "delivery-verification.md"
print(f"BGE-M3 rebuild real aprobado: {second.source_count} fragmento, {time.perf_counter() - started:.2f} s")
'@

# PowerShell can split a multiline value passed to Python's -c option. Keep the
# probe self-contained, but execute it from its isolated verification directory.
New-Item -ItemType Directory -Force -Path $verificationRoot | Out-Null
$verificationScript = Join-Path $verificationRoot 'verify_semantic_rebuild.py'
[System.IO.File]::WriteAllText($verificationScript, $verification, [System.Text.UTF8Encoding]::new($false))
& $Python $verificationScript
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Datos de verificacion aislados en: $verificationRoot"
