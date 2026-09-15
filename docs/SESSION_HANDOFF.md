# Session handoff — Fashion CAD Studio

> Read this file first after any context compaction or when continuing the project.
> Last checkpoint: 2026-09-14, America/Asuncion.

## Scope and user constraints

- Project root: `D:\Digital Lab\FashionCAD` only. Do not reuse or alter sibling/older vibecoded projects in `D:\Digital Lab`.
- User has granted full access and prefers us to perform the work; only present a simple action when an external credential, physical device, installer decision or human validation is genuinely required.
- Preserve the local-first rule. Cloud is opt-in by per-asset consent and must not replace local functionality.
- Do not put FashionCAD models, caches or artifacts outside project root. At last measurement, `D:` had 87.89 GB free and project size was below 45 GB budget.
- Do not claim a measurement inferred from photo as confirmed. Laptop bag requires physical width, height and depth or exact model.

## Current verified state

- API is FastAPI in `apps/api/fashion_cad_api`; frontend React/Vite/Three in `apps/studio-web`; typed stdio MCP in `apps/mcp-server`.
- SQLite stores DesignDocument revisions, FTS RAG, cloud consent audit and a GPU-exclusive job queue.
- Parametric local exports:
  - GLB + metadata: `mockups.py`.
  - SVG physical, A4 tiled, A0, 100 mm calibration + pattern metadata: `patterns.py`.
  - PDF/XLSX Tech Pack with BOM, POM, Construction, Grading, Labels/Packaging, Material Evidence and Revision History: `techpack.py`.
- RAG local supports TXT/MD/PDF textual under `data\library` only. It rejects absolute paths, traversal, escapes and files over 25 MB.
- LanceDB is installed and BGE-M3 semantic search works locally. `vector_store.py` is intentionally explicit: it fails rather than fake semantic vectors when model/runtime is absent.
- BGE-M3 is in `models\embeddings\bge-m3`; provenance/checksum/benchmark are in `models\embeddings\bge-m3\model-provenance.json`.
  - revision `5617a9f61b028005a4858fdac845db406aefb181`
  - main binary SHA-256 `b5e0ce3470abf5ef3831aa1bd5553b486803e83251590ab7ff35a117cf6aad38`
  - CPU benchmark: 1024 dims, 3.31 s load, 0.69 s single query, RSS 1943.3 MB.
- Direct LanceDB benchmark indexed Nylon recycled + Cotton and ranked nylon first for a laptop-bag recycled-material query.
- Cloud consent routes exist, but there is no provider credential, cloud call, public endpoint or secure tunnel configured.
- Studio Operator is off by default and constrained; no unrestricted desktop/browser/shell control was added.

## Last verification commands and results

```powershell
cd 'D:\Digital Lab\FashionCAD'
.\environments\api-venv\Scripts\python.exe -m pytest .\apps\api\tests -q
npm.cmd --prefix .\apps\mcp-server run build
npm.cmd --prefix .\apps\studio-web run build
.\scripts\benchmark-models.ps1
```

- Last API result: `13 passed` (four upstream Starlette/httpx deprecation warnings).
- MCP TypeScript build: passed.
- Web production build: passed. Known nonblocking warning: deferred Three.js scene chunk is 878.59 kB.
- Benchmark model status: BGE-M3 installed; Qwen VL, SigLIP2 and faster-whisper not installed.

## Important implementation caveats

- The test fixture uses an empty temporary model root. Therefore `/api/rag/semantic/reindex` returns 503 under automated tests by design. In the real project root BGE-M3 works.
- Existing API tests validate generation and safety guards, but there is not yet a full HTTP E2E test against the installed BGE model because it would add a 2 GB model load to each run.
- The pattern templates are a manufacturable MVP basis, not approved production grading. Physical sample validation remains mandatory.
- No Blender is installed in `runtime`; the current GLB comes from local parametric Trimesh generation.
- No Ollama binary exists on this PC (`ollama` command was unavailable). Do not install one to C:; use an explicitly portable/runtime-contained path under `runtime` or document the external install decision.
- FastEmbed 0.8.0 did not list `BAAI/bge-m3`; do not use it for BGE-M3. Current working BGE runtime is `FlagEmbedding_cpu`.

## Next execution order

1. Add portable local VLM runtime under `runtime` without violating D-only policy; download Qwen2.5-VL 3B Q4 only after its actual model manifest/checksum/license/preflight are known. Benchmark with GTX 1060 6 GB, 4096 context and one GPU job.
2. Integrate Qwen structured ProductBrief adapter with deterministic fallback and image asset import. Never make critical dimensions confirmed automatically.
3. Install and benchmark SigLIP2 for image/text LanceDB rows; add image asset ingestion and citations.
4. Add RapidOCR for scanned PDFs, then faster-whisper base INT8 CPU for voice commands.
5. Install portable Blender LTS under `runtime` and attach headless jobs to the existing job queue.
6. Add UI flows for library import, semantic search, GLB artifact loading, cloud-consent review and job status; then reduce Three.js lazy chunk.
7. Configure cloud adapter/tunnel only after real credentials and the user’s provider choice; never store credentials in repository.
8. Print/cut/sew both MVP products and log actual 100 mm calibration, fit and construction corrections.

## Read before editing

- `docs/IMPLEMENTATION_PLAN.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/ARCHITECTURE.md`
- `models/manifest.json`
- This file

## Git state

Independent repository initialized at project root. All files are currently uncommitted/new; do not reset, clean or overwrite unrelated files. Inspect `git status --short` before edits.