from __future__ import annotations

import json
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .briefs import analyze_local_brief
from .assistant import plan_local_message
from .domain import missing_fields, to_response
from .ingestion import IngestionError, ingest_local_file
from .mockups import export_mockup
from .operator import OperatorGuard
from .patterns import export_pattern
from .repository import GpuBusyError, Repository
from . import vector_store
from .schemas import (
    CapabilityResponse,
    BriefRequest,
    AssistantRequest,
    AssistantResponse,
    CloudConsentRequest,
    CloudConsentResponse,
    CreateDesignRequest,
    DesignResponse,
    ExportResponse,
    JobCreateRequest,
    JobResponse,
    OperationRequest,
    OperatorSessionRequest,
    OperatorSessionResponse,
    OperatorActionRequest,
    OperatorAuditResponse,
    OperatorConfirmationRequest,
    OperatorConfirmationResponse,
    RagDocumentRequest,
    RagImportRequest,
    RagResult,
    ProductBrief,
)
from .techpack import export_techpack

repository = Repository()
operator_guard = OperatorGuard(lambda: repository)
artifacts_static = StaticFiles(directory=settings.artifacts_dir)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
    artifacts_static.directory = str(settings.artifacts_dir)
    artifacts_static.all_directories = [str(settings.artifacts_dir)]
    repository.initialize()
    yield
    operator_guard.shutdown()


app = FastAPI(title="Fashion CAD Studio API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
app.mount("/artifacts", artifacts_static, name="artifacts")


def require_design(design_id: str) -> dict:
    document = repository.get_design(design_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado.")
    return document


def require_export_ready(document: dict) -> None:
    if document["product_type"] != "laptop_bag":
        return
    if missing_fields(document):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El bolso requiere ancho, alto y espesor máximos de la laptop en mm antes de fabricar o exportar.",
        )


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-first"}


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "service": "Fashion CAD Studio API", "docs": "/docs"}


@app.get("/api/capabilities", response_model=CapabilityResponse)
async def capabilities() -> CapabilityResponse:
    manifest = json.loads(settings.model_manifest_path.read_text(encoding="utf-8"))
    models = []
    for model in manifest["models"]:
        location = settings.project_root / model["target_directory"]
        models.append({**model, "installed": location.exists()})
    return CapabilityResponse(local_mode=True, cloud_mode=True, operator_enabled=settings.operator_enabled, models=models)


@app.post("/api/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobCreateRequest) -> dict:
    try:
        return repository.create_job(payload.kind, payload.payload, payload.gpu_exclusive)
    except GpuBusyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def job_status(job_id: str) -> dict:
    job = repository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajo no encontrado.")
    return job


@app.delete("/api/jobs/{job_id}", response_model=JobResponse)
async def cancel_job(job_id: str) -> dict:
    cancelled = repository.cancel_job(job_id)
    if cancelled:
        return cancelled
    if not repository.get_job(job_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajo no encontrado.")
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El trabajo ya terminó y no puede cancelarse.")


@app.post("/api/briefs/local", response_model=ProductBrief)
async def local_brief(payload: BriefRequest) -> dict:
    return analyze_local_brief(payload)


@app.post("/api/projects", response_model=DesignResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: CreateDesignRequest) -> dict:
    return to_response(repository.create_design(payload))


@app.get("/api/projects", response_model=list[DesignResponse])
async def list_projects() -> list[dict]:
    return [to_response(document) for document in repository.list_designs()]


@app.get("/api/projects/{design_id}", response_model=DesignResponse)
async def get_project(design_id: str) -> dict:
    return to_response(require_design(design_id))


@app.post("/api/projects/{design_id}/cloud-consents", response_model=CloudConsentResponse, status_code=status.HTTP_201_CREATED)
async def record_cloud_consent(design_id: str, payload: CloudConsentRequest) -> dict:
    document = require_design(design_id)
    if document["mode"] == "local_private":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El modo local privado no permite consentimiento ni envíos cloud.")
    return repository.record_cloud_consent(design_id, payload.asset_id, payload.provider, payload.purpose, payload.estimated_cost_usd, payload.approved)


@app.get("/api/projects/{design_id}/cloud-consents", response_model=list[CloudConsentResponse])
async def list_cloud_consents(design_id: str) -> list[dict]:
    require_design(design_id)
    return repository.list_cloud_consents(design_id)


@app.post("/api/projects/{design_id}/operations", response_model=DesignResponse)
async def apply_operation(design_id: str, operation: OperationRequest) -> dict:
    try:
        document = repository.apply_operation(design_id, operation)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado.")
    return to_response(document)


@app.post("/api/projects/{design_id}/assistant", response_model=AssistantResponse)
async def local_assistant(design_id: str, payload: AssistantRequest) -> AssistantResponse:
    document = require_design(design_id)
    operations, message = plan_local_message(to_response(document), payload.message)
    actions: list[str] = []
    for operation in operations:
        document = repository.apply_operation(design_id, operation)
        if document is None:  # defensive: the design was present before planning.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado.")
        actions.append(operation.kind)
    response = to_response(document)
    if document["mode"] == "cloud_creative":
        message += " El modo cloud sigue bloqueado hasta registrar consentimiento y configurar un proveedor; no se envió ningún activo."
    elif document["mode"] == "hybrid":
        message += " Se aplicó localmente; el modo híbrido pedirá consentimiento antes de cualquier proveedor futuro."
    return AssistantResponse(message=message, actions=actions, design=response)


@app.post("/api/projects/{design_id}/exports/mockup", response_model=ExportResponse)
async def mockup_export(design_id: str) -> ExportResponse:
    document = require_design(design_id)
    require_export_ready(document)
    return ExportResponse(project_id=design_id, revision=document["revision"], artifacts=export_mockup(document))


@app.post("/api/projects/{design_id}/exports/pattern", response_model=ExportResponse)
async def pattern_export(design_id: str) -> ExportResponse:
    document = require_design(design_id)
    require_export_ready(document)
    return ExportResponse(project_id=design_id, revision=document["revision"], artifacts=export_pattern(document))


@app.post("/api/projects/{design_id}/exports/techpack", response_model=ExportResponse)
async def techpack_export(design_id: str) -> ExportResponse:
    document = require_design(design_id)
    require_export_ready(document)
    return ExportResponse(project_id=design_id, revision=document["revision"], artifacts=export_techpack(document))


def _run_semantic_reindex(job_id: str) -> None:
    rows = repository.list_rag_documents()
    if not repository.mark_job_running(job_id, total=len(rows), message="Preparando rebuild semántico local."):
        return
    try:
        build = vector_store.semantic_reindex(
            rows,
            job_id=job_id,
            should_cancel=lambda: repository.is_job_cancelled(job_id),
            on_progress=lambda current, total: repository.update_job_progress(
                job_id, current, total, f"Indexando fragmento {current}/{total}."
            ),
        )
        if repository.is_job_cancelled(job_id):
            vector_store.LanceSemanticStore().drop_managed_table(build.table_name)
            return
        previous_table = repository.activate_semantic_index(build.table_name, build.source_count)
        vector_store.LanceSemanticStore().drop_managed_table(previous_table)
        repository.complete_job(job_id, message=f"Rebuild semántico listo: {build.source_count} fragmentos.")
    except vector_store.SemanticReindexCancelled:
        return
    except vector_store.SemanticUnavailable as exc:
        repository.fail_job(job_id, str(exc))
    except Exception as exc:  # pragma: no cover - defensive boundary for the background worker
        repository.fail_job(job_id, f"{type(exc).__name__}: {exc}")


@app.post("/api/rag/semantic/reindex", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def semantic_rag_reindex() -> dict:
    try:
        vector_store.BgeM3Embedder().ensure_available()
    except vector_store.SemanticUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    try:
        job = repository.create_job("embedding_index", {"engine": "lancedb_bge_m3", "mode": "atomic_rebuild"}, False)
    except GpuBusyError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    threading.Thread(target=_run_semantic_reindex, args=(job["id"],), name=f"fashion-cad-reindex-{job['id'][:8]}", daemon=True).start()
    return job


@app.get("/api/rag/semantic/search", response_model=list[RagResult])
async def semantic_rag_search(query: str = Query(min_length=2, max_length=500)) -> list[dict]:
    try:
        state = repository.get_semantic_index()
        return [result.__dict__ for result in vector_store.semantic_search(query, state["table_name"] if state else None)]
    except vector_store.SemanticUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@app.post("/api/rag/documents", status_code=status.HTTP_201_CREATED)
async def add_rag_document(payload: RagDocumentRequest) -> dict[str, str]:
    repository.add_rag_document(payload.title, payload.content, payload.source)
    return {"status": "indexed", "engine": "sqlite_fts"}


@app.post("/api/rag/import", status_code=status.HTTP_201_CREATED)
async def import_rag_document(payload: RagImportRequest) -> dict[str, str | int]:
    try:
        result = ingest_local_file(
            payload.relative_path,
            repository,
            use_ocr=payload.use_ocr,
            max_ocr_pages=payload.max_ocr_pages,
        )
    except IngestionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return {
        "status": "indexed",
        "engine": "sqlite_fts",
        "source": result.source,
        "chunks": result.chunks,
        "extracted_characters": result.extracted_characters,
    }


@app.get("/api/rag/search", response_model=list[RagResult])
async def rag_search(query: str = Query(min_length=2, max_length=500)) -> list[dict]:
    return repository.search_rag(query)


@app.post("/api/operator/sessions", response_model=OperatorSessionResponse)
async def operator_start(payload: OperatorSessionRequest) -> OperatorSessionResponse:
    session = operator_guard.start(payload.requested_windows)
    return OperatorSessionResponse(
        session_id=session.session_id,
        expires_at=session.expires_at,
        operator_enabled=True,
        allowed_windows=sorted(session.allowed_windows),
        state=session.state,
    )


@app.delete("/api/operator/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def operator_stop(session_id: str) -> None:
    operator_guard.stop(session_id)


@app.post("/api/operator/sessions/{session_id}/resume", response_model=OperatorSessionResponse)
async def operator_resume(session_id: str) -> OperatorSessionResponse:
    session = operator_guard.resume(session_id)
    return OperatorSessionResponse(
        session_id=session.session_id,
        expires_at=session.expires_at,
        operator_enabled=True,
        allowed_windows=sorted(session.allowed_windows),
        state=session.state,
    )


@app.get("/api/operator/sessions/{session_id}/audit", response_model=list[OperatorAuditResponse])
async def operator_audit(session_id: str) -> list[dict]:
    return repository.list_operator_audit(session_id)


@app.post("/api/operator/confirmations", response_model=OperatorConfirmationResponse, status_code=status.HTTP_201_CREATED)
async def operator_confirmation(payload: OperatorConfirmationRequest) -> OperatorConfirmationResponse:
    confirmation = operator_guard.request_confirmation(
        payload.session_id, payload.window_name, payload.intent, payload.summary
    )
    return OperatorConfirmationResponse(confirmation_id=confirmation.confirmation_id, expires_at=confirmation.expires_at)


@app.post("/api/operator/click")
async def operator_click(payload: OperatorActionRequest) -> dict[str, str]:
    if payload.x is None or payload.y is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="click requiere x e y relativos a la ventana.")
    operator_guard.click(payload.session_id, payload.window_name, payload.x, payload.y, payload.intent, payload.confirmation_id)
    return {"status": "clicked"}


@app.post("/api/operator/keypress")
async def operator_keypress(payload: OperatorActionRequest) -> dict[str, str]:
    if not payload.key:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="keypress requiere key.")
    operator_guard.keypress(payload.session_id, payload.window_name, payload.key, payload.intent, payload.confirmation_id)
    return {"status": "pressed"}


@app.post("/api/operator/type")
async def operator_type(payload: OperatorActionRequest) -> dict[str, str]:
    if not payload.text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="type requiere text.")
    operator_guard.type_text(payload.session_id, payload.window_name, payload.text, payload.intent, payload.confirmation_id)
    return {"status": "typed"}
