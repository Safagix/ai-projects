from __future__ import annotations

import argparse

from .config import settings
from .ingestion import IngestionError, ingest_local_file
from .repository import Repository

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Indexa la biblioteca privada local de Fashion CAD.")
    parser.add_argument("--all", action="store_true", help="Indexa TXT, Markdown y PDF textuales de KNOWLEDGE_BASE_STUDIO.")
    parser.add_argument("--ocr", action="store_true", help="Usa RapidOCR local sólo como fallback para PDF escaneado.")
    parser.add_argument("--max-ocr-pages", type=int, default=300, help="Límite explícito de páginas OCR por PDF (1-1500).")
    parser.add_argument("paths", nargs="*", help="Rutas relativas a KNOWLEDGE_BASE_STUDIO.")
    args = parser.parse_args()
    if not args.all and not args.paths:
        parser.error("Indicar --all o una o más rutas relativas.")
    paths = (
        [path.relative_to(settings.library_dir).as_posix() for path in settings.library_dir.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS]
        if args.all
        else args.paths
    )
    repository = Repository()
    repository.initialize()
    successes = 0
    for relative_path in sorted(paths):
        try:
            result = ingest_local_file(
                relative_path,
                repository,
                use_ocr=args.ocr,
                max_ocr_pages=args.max_ocr_pages,
            )
            print(f"INDEXED {result.source}: {result.chunks} fragmentos")
            successes += 1
        except IngestionError as exc:
            print(f"SKIPPED {relative_path}: {exc}")
    print(f"Biblioteca local: {successes}/{len(paths)} archivos indexados.")
    return 0 if successes == len(paths) else 1


if __name__ == "__main__":
    raise SystemExit(main())
