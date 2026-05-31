"""CLI interface for Eira Brain Chat."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from local_rag.config import settings
from local_rag.db import init_db
from local_rag.indexer import discover_markdown_files, ingest_paths
from local_rag.ollama_client import get_ollama
from local_rag.retrieval import answer, search


def _print_json(data: dict[str, Any] | list[dict[str, Any]]) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _db_stats() -> dict[str, int]:
    from local_rag.db import get_connection

    init_db()
    with get_connection() as conn:
        documents = conn.execute("SELECT count(*) FROM documents").fetchone()[0]
        chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    return {"documents": int(documents), "chunks": int(chunks)}


def _doctor() -> int:
    print("Eira Brain doctor")
    print(f"- SQLite DB: {settings.sqlite_db_path}")

    missing_dirs = [p for p in settings.rag_knowledge_dirs if not Path(p).exists()]
    if missing_dirs:
        print("- Knowledge dirs: ERROR")
        for path in missing_dirs:
            print(f"  Missing: {path}")
        return 1

    files = discover_markdown_files()
    print(f"- Markdown files discovered: {len(files)}")

    client = get_ollama()
    health = client.health()
    if health.get("status") != "ok":
        print(f"- Ollama: ERROR ({health.get('error')})")
        print("  Start Ollama Desktop or run: ollama serve")
        return 1

    installed = set(health.get("models", []))
    installed_aliases = installed | {name.removesuffix(":latest") for name in installed}
    required = {
        settings.ollama_embed_model,
        settings.router_model,
        settings.model_fast,
        settings.model_thinker,
        settings.model_coder,
    }
    missing_models = sorted(m for m in required if m not in installed_aliases)
    if missing_models:
        print("- Ollama models: ERROR")
        for model in missing_models:
            print(f"  Missing: {model}")
            print(f"  Install with: ollama pull {model}")
        return 1

    stats = _db_stats()
    print(f"- Indexed documents: {stats['documents']}")
    print(f"- Indexed chunks: {stats['chunks']}")
    print("- Status: ok")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="local-rag",
        description="Eira Brain Chat — Local RAG for your knowledge base.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init-db
    subparsers.add_parser("init-db", help="Create the SQLite database and tables.")

    # ingest
    ingest_p = subparsers.add_parser("ingest", help="Index Markdown files into the vector store.")
    ingest_p.add_argument("paths", nargs="*", help="Optional file or directory paths.")
    ingest_p.add_argument("--max-files", type=int, help="Index only the first N discovered files.")

    # search
    search_p = subparsers.add_parser("search", help="Search raw chunks by query.")
    search_p.add_argument("question", help="Search query.")
    search_p.add_argument("--limit", type=int, default=8)

    # ask
    ask_p = subparsers.add_parser("ask", help="Ask a question and get a RAG-grounded answer.")
    ask_p.add_argument("question", help="Question to answer.")

    # serve
    serve_p = subparsers.add_parser("serve", help="Start the web server with chat UI.")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8000)
    serve_p.add_argument("--reload", action="store_true", help="Enable uvicorn reload for development.")

    # stats
    stats_p = subparsers.add_parser("stats", help="Show database document/chunk counts.")
    stats_p.add_argument("--field", choices=["documents", "chunks"], help="Print only one numeric field.")

    # doctor
    subparsers.add_parser("doctor", help="Check paths, Ollama, models, and index state.")

    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
        print("✅ Database initialized.")
        return

    if args.command == "ingest":
        init_db()
        result = ingest_paths(args.paths or None, max_files=args.max_files)
        print(f"✅ Indexed {result['documents']} documents, {result['chunks']} chunks.")
        return

    if args.command == "search":
        _print_json(search(args.question, limit=args.limit))
        return

    if args.command == "ask":
        result = answer(args.question)
        print(f"\n🧠 Respuesta:\n{result['answer']}\n")
        if result["citations"]:
            print("📚 Fuentes:")
            for c in result["citations"]:
                print(f"  • {c['path']} — {c['heading']} (score: {c['score']:.4f})")
        return

    if args.command == "serve":
        import uvicorn
        print(f"\n🧠 Eira Brain Chat → http://{args.host}:{args.port}\n")
        uvicorn.run("local_rag.api:app", host=args.host, port=args.port, reload=args.reload)
        return

    if args.command == "stats":
        stats = _db_stats()
        if args.field:
            print(stats[args.field])
        else:
            _print_json(stats)
        return

    if args.command == "doctor":
        sys.exit(_doctor())
        return


if __name__ == "__main__":
    main()
