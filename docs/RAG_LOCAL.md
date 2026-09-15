# RAG local: biblioteca e índice

Coloca los documentos que quieras indexar únicamente bajo `D:\Digital Lab\FashionCAD\data\library`. La API y el MCP aceptan rutas relativas a esa carpeta; rechazan rutas absolutas, `..`, enlaces que escapen y archivos mayores de 25 MB.

Formatos del MVP: `.txt`, `.md` y PDF con capa de texto. Los PDF escaneados se rechazan de forma explícita hasta integrar RapidOCR; no se inventa texto ausente.

Cada archivo se fragmenta en bloques con solape y se indexa primero en SQLite FTS. La fuente queda como `library/ruta/archivo.ext`, por lo que las respuestas pueden citarla. LanceDB es el siguiente motor vectorial y se activará únicamente después del benchmark de BGE-M3 y SigLIP2; por ahora no se presenta una búsqueda lexical como si fuera multimodal.

Ejemplo vía MCP: `rag_import_local_file` con `relative_path: "materiales/nylon-reciclado.pdf"`.