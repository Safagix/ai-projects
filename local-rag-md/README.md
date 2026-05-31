# local-rag-md

Eira Brain Chat: chat RAG local para consultar y escribir notas sobre `Eira's Library` y tu vault de Obsidian.

## Stack actual

- FastAPI + UI web en `static/`
- SQLite en `data/brain.db`
- SQLite FTS5 para busqueda por texto
- Embeddings de Ollama guardados como BLOB
- Fusion simple entre similitud semantica y busqueda lexical
- Modelos Ollama configurados en `.env`

No requiere Docker para funcionar.

## Arranque recomendado

Ejecuta:

```bat
start_brain.bat
```

El script hace estas validaciones:

- verifica que Ollama este corriendo
- crea `.venv` si no existe
- instala/actualiza el paquete local
- revisa rutas, modelos y estado del indice con `local-rag doctor`
- inicializa SQLite
- indexa automaticamente si la base esta vacia
- abre `http://127.0.0.1:8000`

## Modelos requeridos

Los modelos se leen desde `.env`. En esta maquina estan configurados:

```text
nomic-embed-text
llama3.2:1b
deepseek-r1:1.5b
qwen2.5-coder:1.5b
```

Si falta alguno:

```powershell
ollama pull nomic-embed-text
ollama pull llama3.2:1b
ollama pull deepseek-r1:1.5b
ollama pull qwen2.5-coder:1.5b
```

## Comandos utiles

```powershell
.venv\Scripts\python.exe -m local_rag.cli doctor
.venv\Scripts\python.exe -m local_rag.cli stats
.venv\Scripts\python.exe -m local_rag.cli ingest
.venv\Scripts\python.exe -m local_rag.cli ask "Que tengo documentado sobre RAG?"
.venv\Scripts\python.exe -m local_rag.cli serve
```

## Rutas de conocimiento

Se configuran en `.env`:

```text
RAG_KNOWLEDGE_DIRS=%DIGITAL_LAB%\Eira's Library;%DIGITAL_LAB%\Obsidian_Vault\Obsidian Vault
OBSIDIAN_VAULT_PATH=%DIGITAL_LAB%\Obsidian_Vault\Obsidian Vault
```

El modo "Agregar" escribe notas nuevas en la carpeta configurada por `OBSIDIAN_INBOX_FOLDER` y luego intenta indexarlas.
