from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import settings
from .repository import Repository

ALLOWED_SUFFIXES = {".txt", ".md", ".pdf"}
MAX_FILE_BYTES = 25 * 1024 * 1024
CHUNK_SIZE = 1_200
CHUNK_OVERLAP = 160


class IngestionError(ValueError):
    """Raised when a document is outside the intentionally narrow local library."""


@dataclass(frozen=True)
class IngestionResult:
    title: str
    source: str
    chunks: int
    extracted_characters: int


def resolve_library_file(relative_path: str) -> Path:
    requested = Path(relative_path)
    if requested.is_absolute() or ".." in requested.parts:
        raise IngestionError("La ruta debe ser relativa a data\\library y no puede salir de esa carpeta.")
    if requested.suffix.lower() not in ALLOWED_SUFFIXES:
        allowed = ", ".join(sorted(ALLOWED_SUFFIXES))
        raise IngestionError(f"Formato no permitido. Formatos locales admitidos: {allowed}.")

    root = settings.library_dir.resolve()
    candidate = (root / requested).resolve()
    if not candidate.is_relative_to(root):
        raise IngestionError("La ruta solicitada queda fuera de data\\library.")
    if not candidate.is_file():
        raise IngestionError("No se encontró el archivo dentro de data\\library.")
    if candidate.stat().st_size > MAX_FILE_BYTES:
        raise IngestionError("El archivo supera el límite de 25 MB para la ingesta del MVP.")
    return candidate


def extract_pages(path: Path) -> list[tuple[int | None, str]]:
    if path.suffix.lower() in {".txt", ".md"}:
        return [(None, path.read_text(encoding="utf-8", errors="replace"))]
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - setup dependency validation
        raise IngestionError("Falta pypdf. Ejecuta scripts\\setup-local.ps1 para habilitar PDF local.") from exc
    try:
        return [(number, page.extract_text() or "") for number, page in enumerate(PdfReader(path).pages, start=1)]
    except Exception as exc:
        raise IngestionError("No fue posible extraer texto del PDF. Los escaneos requieren OCR en la siguiente fase.") from exc


def chunk_text(text: str) -> list[str]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + CHUNK_SIZE, len(cleaned))
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start, end)
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary
        chunks.append(cleaned[start:end])
        if end == len(cleaned):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def ingest_local_file(relative_path: str, repository: Repository) -> IngestionResult:
    path = resolve_library_file(relative_path)
    pages = extract_pages(path)
    chunks_by_page = [(page, chunk) for page, text in pages for chunk in chunk_text(text)]
    if not chunks_by_page:
        raise IngestionError("El documento no contiene texto extraíble. Usa OCR para un escaneo o verifica el archivo.")

    source = f"library/{path.relative_to(settings.library_dir.resolve()).as_posix()}"
    total = len(chunks_by_page)
    for number, (page, chunk) in enumerate(chunks_by_page, start=1):
        page_note = f" · página {page}" if page else ""
        repository.add_rag_document(
            f"{path.stem}{page_note} — fragmento {number}/{total}",
            chunk,
            source,
            source_page=page,
            chunk_number=number,
        )
    return IngestionResult(path.name, source, total, sum(len(text) for _, text in pages))
