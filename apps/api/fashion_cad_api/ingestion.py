from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import settings
from .repository import Repository

ALLOWED_SUFFIXES = {".txt", ".md", ".pdf"}
MAX_FILE_BYTES = 200 * 1024 * 1024
MAX_PDF_PAGES = 1_500
MAX_EXTRACTED_CHARACTERS = 8_000_000
DEFAULT_MAX_OCR_PAGES = 300
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


@dataclass(frozen=True)
class ExtractedPage:
    number: int | None
    text: str
    ocr_confidence: float | None = None


def resolve_library_file(relative_path: str) -> Path:
    requested = Path(relative_path)
    if requested.is_absolute() or ".." in requested.parts:
        raise IngestionError("La ruta debe ser relativa a KNOWLEDGE_BASE_STUDIO y no puede salir de esa carpeta.")
    if requested.suffix.lower() not in ALLOWED_SUFFIXES:
        allowed = ", ".join(sorted(ALLOWED_SUFFIXES))
        raise IngestionError(f"Formato no permitido. Formatos locales admitidos: {allowed}.")

    root = settings.library_dir.resolve()
    candidate = (root / requested).resolve()
    if not candidate.is_relative_to(root):
        raise IngestionError("La ruta solicitada queda fuera de KNOWLEDGE_BASE_STUDIO.")
    if not candidate.is_file():
        raise IngestionError("No se encontró el archivo dentro de KNOWLEDGE_BASE_STUDIO.")
    if candidate.stat().st_size > MAX_FILE_BYTES:
        raise IngestionError("El archivo supera el límite de 200 MB para la ingesta local.")
    return candidate


def _extract_textual_pdf_pages(path: Path) -> list[ExtractedPage]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - setup dependency validation
        raise IngestionError("Falta pypdf. Ejecuta scripts\\setup-local.ps1 para habilitar PDF local.") from exc
    reader = PdfReader(path)
    if len(reader.pages) > MAX_PDF_PAGES:
        raise IngestionError(f"El PDF supera el límite seguro de {MAX_PDF_PAGES} páginas.")
    pages: list[ExtractedPage] = []
    extracted = 0
    for number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        extracted += len(text)
        if extracted > MAX_EXTRACTED_CHARACTERS:
            raise IngestionError("El PDF supera el límite seguro de texto extraíble; dividirlo antes de indexar.")
        pages.append(ExtractedPage(number, text))
    return pages


def _ocr_pdf_pages(path: Path, max_pages: int) -> list[ExtractedPage]:
    try:
        import numpy as np
        import pymupdf
        from rapidocr import RapidOCR
    except ImportError as exc:  # pragma: no cover - setup dependency validation
        raise IngestionError("Falta el runtime OCR local. Ejecuta scripts\\setup-local.ps1 para instalar RapidOCR.") from exc
    document = pymupdf.open(path)
    try:
        if document.page_count > MAX_PDF_PAGES:
            raise IngestionError(f"El PDF supera el límite seguro de {MAX_PDF_PAGES} páginas.")
        if document.page_count > max_pages:
            raise IngestionError(
                f"El PDF tiene {document.page_count} páginas y supera el máximo OCR solicitado de {max_pages}. "
                "Aumenta max_ocr_pages sólo si vas a esperar el procesamiento local."
            )
        engine = RapidOCR()
        pages: list[ExtractedPage] = []
        for number, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(1.5, 1.5), colorspace=pymupdf.csGRAY, alpha=False
            )
            image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width)
            output = engine(image)
            texts = tuple(getattr(output, "txts", ()) or ())
            scores = tuple(getattr(output, "scores", ()) or ())
            text = " ".join(str(item).strip() for item in texts if str(item).strip())
            confidence = round(sum(float(score) for score in scores) / len(scores), 5) if scores else None
            pages.append(ExtractedPage(number, text, confidence))
        return pages
    finally:
        document.close()


def extract_pages(path: Path, *, use_ocr: bool = False, max_ocr_pages: int = DEFAULT_MAX_OCR_PAGES) -> list[ExtractedPage]:
    if path.suffix.lower() in {".txt", ".md"}:
        return [ExtractedPage(None, path.read_text(encoding="utf-8", errors="replace"))]
    try:
        pages = _extract_textual_pdf_pages(path)
    except IngestionError:
        raise
    except Exception as exc:
        if not use_ocr:
            raise IngestionError("No fue posible leer el PDF. Volvé a importar con OCR explícito si es un escaneo.") from exc
        return _ocr_pdf_pages(path, max_ocr_pages)
    if any(chunk_text(page.text) for page in pages):
        return pages
    if not use_ocr:
        raise IngestionError("El documento no contiene texto extraíble. Volvé a importar con OCR explícito si es un escaneo.")
    return _ocr_pdf_pages(path, max_ocr_pages)


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


def ingest_local_file(
    relative_path: str,
    repository: Repository,
    *,
    use_ocr: bool = False,
    max_ocr_pages: int = DEFAULT_MAX_OCR_PAGES,
) -> IngestionResult:
    path = resolve_library_file(relative_path)
    pages = extract_pages(path, use_ocr=use_ocr, max_ocr_pages=max_ocr_pages)
    chunks_by_page = [
        (page.number, chunk, page.ocr_confidence)
        for page in pages
        for chunk in chunk_text(page.text)
    ]
    if not chunks_by_page:
        raise IngestionError("El documento no contiene texto extraíble. Usa OCR para un escaneo o verifica el archivo.")

    source = f"library/{path.relative_to(settings.library_dir.resolve()).as_posix()}"
    total = len(chunks_by_page)
    repository.delete_rag_documents_by_source(source)
    for number, (page, chunk, ocr_confidence) in enumerate(chunks_by_page, start=1):
        page_note = f" · página {page}" if page else ""
        repository.add_rag_document(
            f"{path.stem}{page_note} — fragmento {number}/{total}",
            chunk,
            source,
            source_page=page,
            chunk_number=number,
            ocr_confidence=ocr_confidence,
        )
    return IngestionResult(path.name, source, total, sum(len(page.text) for page in pages))
