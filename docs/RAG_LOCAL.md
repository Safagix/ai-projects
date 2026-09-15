# RAG local: biblioteca e índice

Coloca los documentos únicamente bajo `D:\Digital Lab\FashionCAD\KNOWLEDGE_BASE_STUDIO`. La API y el MCP aceptan rutas relativas a esa carpeta; rechazan rutas absolutas, `..`, enlaces que escapen y archivos mayores de 200 MB.

Formatos: `.txt`, `.md` y PDF. Un PDF con capa de texto se importa directamente. Para un escaneo hay que solicitar OCR explícitamente (`use_ocr: true` en la API o `-Ocr` en el script); RapidOCR corre localmente y almacena fuente, página, número de fragmento y confianza media. El OCR no convierte un dato extraído en una medida confirmada.

Cada archivo se fragmenta en bloques con solape y se indexa primero en SQLite FTS. La fuente queda como `library/ruta/archivo.ext`, por lo que las respuestas pueden citarla. El importador limita PDFs a 1.500 páginas y 8 millones de caracteres textuales; OCR exige además un máximo explícito de páginas (300 por defecto) para proteger CPU/RAM.

LanceDB con BGE-M3 ya está disponible para búsqueda semántica local después de un rebuild atómico. No lanzar OCR y reconstrucción BGE-M3 simultáneamente en esta PC.

Ejemplo vía MCP: `rag_import_local_file` con `relative_path: "01_THEORY_BOOKS/README.md"`. Los CSV estructurados se consultan directamente por scripts; no se importan mediante este endpoint.
