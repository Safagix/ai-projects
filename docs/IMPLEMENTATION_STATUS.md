# Estado de implementación — 2026-09-15

## Implementado y verificado

- Raíz, cachés, entornos y artefactos confinados a `D:\Digital Lab\FashionCAD`.
- API FastAPI, SQLite, revisiones de `DesignDocument`, operaciones y validación de laptop por dimensiones físicas.
- Mockup técnico paramétrico GLB con metadatos de revisión, generado localmente.
- Patrón SVG físico, PDF A4 tiled, PDF A0, control de 100 mm y metadatos de piezas; los componentes cambian las piezas de una revisión nueva.
- Tech Pack PDF/XLSX: Summary, BOM, POM, Construction, Grading, Labels/Packaging, Material Evidence y Revision History. Los datos inciertos se marcan como pendientes.
- Biblioteca documental segura en `data\library`; TXT, Markdown y PDF textual, FTS y citas.
- LanceDB instalado en `data\lancedb`; BGE-M3 validado en CPU y usado para recuperación semántica local.
- Rebuild LanceDB atómico y cancelable: cada índice se construye en tabla temporal con identidad estable SHA-256 por fragmento; el puntero SQLite cambia sólo al terminar y se retira la tabla anterior. Los resultados incluyen fuente, página, número e ID de fragmento.
- Benchmark BGE-M3: 1.024 dimensiones, carga 3.31 s, consulta 0.69 s, RSS 1.94 GB. Peso principal SHA-256 verificado en `models\embeddings\bge-m3\model-provenance.json`.
- Cola SQLite con exclusión de GPU, progreso/error/cancelación y herramientas MCP de consulta/cancelación.
- MCP cerrado para diseños, RAG, mockup, patrones, Tech Pack, consentimiento y operador; sin shell ni acceso general al disco.
- Consentimiento cloud por activo, propósito, proveedor, coste y auditoría. El modo local privado lo rechaza.
- Studio Operator endurecido y aún desactivado por defecto: auditoría SQLite por sesión/acción, pausa durable al perder foco, reanudación explícita, banner nativo visible, atajo global `Ctrl+Alt+Pause` y confirmación de un solo uso (60 s) para exportar, imprimir, cloud o sobrescribir. La prueba automatizada simula la UI; queda pendiente probar físicamente banner/atajo en una sesión Windows supervisada antes de habilitarlo para uso real.
- La UI usa `brief_analyze_local` al crear y analizar briefs; propaga componentes, materiales y medidas confirmadas sin inventar dimensiones. Para bolso muestra un campo de ancho × alto × espesor en mm.
- Un bolso sin sus tres dimensiones físicas ahora no puede exportar mockup, patrón ni Tech Pack: la API y la UI lo bloquean explícitamente.
- Al exportar un mockup, la UI carga el GLB real servido desde `artifacts` y sólo lo conserva en el visor mientras corresponde al mismo diseño y revisión. También ofrece descargas del último grupo de artefactos.
- Studio ofrece FTS o BGE-M3, muestra procedencia del fragmento y permite iniciar/cancelar el rebuild semántico mientras informa su progreso.
- Studio ya no es sólo visual: el asistente local conversacional convierte órdenes acotadas en operaciones/revisiones persistentes (componentes, materiales y medidas) y cada modo se guarda en el diseño. Híbrido y cloud conservan la barrera de consentimiento; no simulan proveedor ni envío.
- La biblioteca privada del usuario quedó organizada en `KNOWLEDGE_BASE_STUDIO\01…06`, fuera de GitHub/Vercel; la API sólo importa desde allí. El plan de contexto y licencias está en `docs\KNOWLEDGE_BASE_PLAN.md`.
- Entrega reproducible documentada en `docs\MVP_DELIVERY.md`; `scripts\verify-mvp.ps1` corre pruebas, builds y el rebuild BGE-M3 real en un directorio aislado bajo `cache`.

## Pendiente por recurso externo, no simulado

| Componente | Bloqueo real | Próximo paso seguro |
|---|---|---|
| Qwen2.5-VL 3B Q4 | No hay runtime Ollama/llama.cpp instalado dentro de `D:` | Instalar runtime portable en `runtime`, descargar `qwen2.5vl:3b` al almacén de FashionCAD y medir VRAM/latencia |
| SigLIP2 | Pesos no descargados | Descargar con licencia/checksum; indexar imágenes en LanceDB cuando CPU/GPU lo apruebe |
| RapidOCR | Runtime/pesos no instalados | Añadir OCR de PDFs escaneados con página y confianza |
| faster-whisper | Runtime/pesos no instalados | Añadir comandos de voz CPU INT8 con cola y prueba de latencia |
| Blender headless | Blender no instalado en `runtime` | Instalar LTS portable y conectar render/GLB como motor opcional |
| Cloud real y túnel MCP | Requiere claves/configuración del usuario | Configurar sólo después de revisar proveedor, coste y túnel saliente |
| Validación de costura | Requiere impresión, modista/taller y muestra física | Medir cuadrado 100 ± 1 mm, cortar, coser y retroalimentar el patrón |

## Evidencia de calidad

- API: 19 pruebas automatizadas pasadas.
- MCP: compilación TypeScript correcta.
- Studio web: compilación Vite correcta. El chunk diferido de Three.js mide 925.28 kB al incluir el cargador GLB; es funcional pero queda optimización de carga como tarea de rendimiento.
- Rebuild BGE-M3 real: dos reconstrucciones consecutivas de un fragmento, búsqueda posterior y deduplicación comprobadas en 21.45 s dentro de `cache\delivery-verification`; no se modificó la biblioteca del usuario.
- QA de Studio local: brief de bolso solicita las tres medidas físicas y el selector BGE-M3/búsqueda responde sin errores con biblioteca vacía. La UI es deliberadamente desktop (`min-width: 1100px`), no responsive móvil.
- Espacio después de BGE-M3: 87.89 GB libres en `D:`. FashionCAD sigue por debajo del límite de 45 GB.

## Autoevaluación

| Eje | Nota | Evidencia y mejora |
|---|---:|---|
| Exactitud | 4/5 | Exportaciones, guardias y rebuild BGE real tienen evidencia; falta validación física del kill switch/overlay y de patrones. |
| Completitud | 4/5 | El MVP local definido está entregable; Qwen-VL, SigLIP2, OCR, voz, Blender y cloud son extensiones explícitamente fuera de esta entrega. |
| Claridad | 5/5 | `MVP_DELIVERY.md` separa arranque, verificación, aceptación manual y límites. |
| Accionabilidad | 5/5 | `verify-mvp.ps1` deja una comprobación única y reproducible sin tocar datos de usuario. |
| Concisión | 4/5 | La documentación separa visión, plan y estado; se podrá condensar cuando el MVP estabilice. |

Puntaje global: **4.3/5**. El MVP local está listo para entregar tras ejecutar `scripts\verify-mvp.ps1`; el siguiente bloque opcional es runtime multimodal portable y su benchmark, sin confundirlo con una dependencia del MVP.
