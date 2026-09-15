# NEW CHAT CONTEXT — Fashion CAD Studio

## Cómo usar este documento

Este archivo está hecho para que un chat nuevo pueda continuar el proyecto sin historia previa. Primero leer este archivo, luego `docs/IMPLEMENTATION_PLAN.md`, `docs/IMPLEMENTATION_STATUS.md` y `docs/SESSION_HANDOFF.md`; después auditar el árbol real y ejecutar las verificaciones. No repetir instalaciones ni asumir que un requisito está hecho sólo porque aparezca en un plan.

## Prompt de arranque para pegar en un chat nuevo

```text
Continuá el proyecto local-first Fashion CAD Studio en D:\Digital Lab\FashionCAD. Antes de modificar nada, leé docs\NEW_CHAT_CONTEXT.md, docs\SESSION_HANDOFF.md, docs\IMPLEMENTATION_PLAN.md y docs\IMPLEMENTATION_STATUS.md; inspeccioná git status y ejecutá las verificaciones indicadas. El usuario dio full access y espera que hagas el trabajo autónomamente; pedí ayuda sólo para credenciales reales, una decisión de proveedor, una impresora/taller o una validación física. No reutilices ni modifiques proyectos vecinos/antiguos de D:\Digital Lab. Conservá el modo local-first, todo en D:, y no conviertas fallbacks o pruebas en capacidades supuestamente terminadas. Priorizá primero corregir las brechas de seguridad/coherencia enumeradas y luego el siguiente bloque del roadmap. Actualizá este archivo y docs\IMPLEMENTATION_STATUS.md al terminar cada hito.
```

---

## 1. Objetivo de producto que no debe cambiar

Construir un estudio de diseño de moda industrial, local-first y cloud-enhanced, estilo CAD conversacional. El MVP sólo fabrica dos familias:

1. Camiseta unisex regular (`upper_garment`).
2. Bolso/funda para laptop (`laptop_bag`).

De un mismo `DesignDocument` versionado deben derivarse mockup técnico 3D, patrón 1:1 y Tech Pack. Sin Internet debe permitir edición, exportación y RAG local. Cloud sólo mejora análisis creativo/visual y razonamiento complejo, con consentimiento por activo; nunca sustituye la ruta local.

Regla física crucial: “laptop de 16 pulgadas” no basta. Exigir ancho, alto y espesor máximos en mm o modelo exacto; nunca inventar esas medidas a partir de fotos/bocetos.

---

## 2. Límites, preferencias y seguridad del usuario

- Raíz única: `D:\Digital Lab\FashionCAD`.
- No tocar ni reutilizar directamente otros proyectos de `D:\Digital Lab`; eran proyectos viejos/vibecoded y pueden tener decisiones inseguras/obsoletas.
- Modelos, pesos, cachés, entornos, datos y artefactos deben quedar bajo la raíz de FashionCAD. Variables configuradas: `HF_HOME`, `TRANSFORMERS_CACHE`, `TORCH_HOME`, `PIP_CACHE_DIR`, `npm_config_cache`, `TEMP`, `TMP`, `OLLAMA_MODELS` apuntan a `D:` desde `scripts\setup-local.ps1`.
- Presupuesto: FashionCAD máximo 45 GB; nunca descargar si `D:` quedaría con menos de 30 GB libres. Última medición: 87.89 GB libres; proyecto aprox. 4.55 GB después de BGE-M3.
- Hardware conocido: GTX 1060 6 GB, Ryzen 3 3200G (4 hilos), 16 GB RAM. Confirmar con `scripts\benchmark-models.ps1` antes de cambiar estrategia; no asumir driver/versiones antiguas.
- Máximo un trabajo GPU exclusivo a la vez. BGE-M3 usa CPU y debe ser único por memoria/CPU en esta PC.
- El usuario valora evidencia/medición, no recomendaciones genéricas. No declarar un modelo, driver, instalación o patrón como exitoso sin prueba verificable.
- El usuario prefiere autonomía. Usar acciones directas dentro del alcance; pedir intervención sólo cuando sea imposible evitar una decisión externa o una acción física.

---

## 3. Estado real del repositorio

- Repositorio Git independiente inicializado en `D:\Digital Lab\FashionCAD`, rama `main`, sin commits. Todos los archivos siguen nuevos/no confirmados. **No ejecutar reset/clean/checkout destructivo.** Revisar `git status --short` antes de editar.
- No hay servidores API/Vite activos al cierre de este checkpoint.
- Se usó el Python del sistema para crear `environments\api-venv`; las dependencias, cachés y pesos del proyecto están en `D:`. Aún no existe distribución portable completa de Python/Node bajo `runtime`; es una deuda de empaquetado, no una capacidad terminada.

### Estructura principal

```text
apps/api/fashion_cad_api/   FastAPI, dominio, SQLite, RAG, mockup, patrón, Tech Pack, operador
apps/api/tests/             19 pruebas API
apps/mcp-server/            MCP stdio TypeScript tipado
apps/studio-web/            React + Vite + Three/R3F
scripts/                    setup, benchmark, run API/web y verificación de entrega
models/                     manifiesto y BGE-M3 verificado
data/                       SQLite y LanceDB; biblioteca privada en KNOWLEDGE_BASE_STUDIO
artifacts/                  exportaciones por diseño/revisión
docs/                       arquitectura, plan, estado, relevo y este contexto
```

### Archivos críticos y su responsabilidad

| Archivo | Responsabilidad | Riesgos/deudas relevantes |
|---|---|---|
| `repository.py` | SQLite: diseños, revisiones, FTS, trabajos, consentimientos y puntero semántico | Conservar el swap atómico; no publicar una tabla Lance incompleta |
| `schemas.py` | Pydantic y límites de entrada | Mantener validación estricta al agregar assets/cloud/voice |
| `briefs.py` | Fallback determinista local | No analiza imagen; no reemplazar con texto inventado |
| `assistant.py` | Intérprete conversacional local acotado | Cambia revisiones auditables; no fingir LLM/cloud hasta benchmark y proveedor real |
| `ingestion.py` | TXT/MD/PDF textual seguro desde `data\library` | No OCR, no imágenes; límite 25 MB |
| `vector_store.py` | BGE-M3 CPU + LanceDB | Rebuild temporal/deduplicado; un proceso a la vez por RAM/CPU |
| `mockups.py` | GLB técnico paramétrico via Trimesh | No es reconstrucción fotorealista ni Blender |
| `patterns.py` | SVG, A4 tiled, A0, metadata | Plantillas geométricas MVP; sin validación de patronista/grading industrial |
| `techpack.py` | PDF/XLSX Tech Pack | Campos no confirmados correctamente dicen `Por confirmar` |
| `operator.py` | Allowlist/foco/sesión de teclado y mouse | Auditoría SQLite, overlay, pausa por foco, confirmaciones y kill switch implementados; falta validación física Windows supervisada antes de habilitarlo |
| `main.py` | API y contratos de ruta | Mantener endpoints internos locales por defecto |
| `apps/mcp-server/src/index.ts` | Herramientas MCP cerradas | No agregar shell, navegación general ni paths arbitrarios |
| `apps/studio-web/src/Scene.tsx` | Preview Three.js actual | Carga GLB exportado por diseño/revisión; el chunk sigue pesado (925.28 kB) |

---

## 4. Capacidades implementadas y evidencia

### Diseño, exportación y producción

- `DesignDocument` en SQLite: nombre, tipo, modo, medidas, materiales, componentes, revisión, estado y confianza.
- Operaciones versionadas: agregar/quitar componente, materiales, medida y descripción.
- `POST /exports/mockup`: GLB binario técnico + JSON de metadata. Validado por prueba con firma `glTF`.
- `POST /exports/pattern`: SVG físico, PDF A4 tiled con solape de 10 mm, PDF A0, cuadrado de 100 mm y metadata de piezas. Una operación `add_component` de bolsillo crea revisión 2 y añade pieza al patrón.
- `POST /exports/techpack`: PDF/XLSX con Summary, BOM, POM, Construction, Grading, Labels_Packaging, Material_Evidence y Revision_History.
- Esto es un MVP técnico. Ningún patrón se debe prometer como listo para producción hasta imprimir, medir 100 ± 1 mm, cortar, coser y corregir con modista/taller.

### RAG

- `POST /api/rag/documents`: texto manual a SQLite FTS.
- `POST /api/rag/import`: importa ruta relativa bajo `KNOWLEDGE_BASE_STUDIO`; soporta `.txt`, `.md`, `.pdf` con texto. Rechaza rutas absolutas, `..`, symlink que sale de biblioteca, formatos no permitidos y >25 MB. La carpeta es privada e ignorada por Git.
- `GET /api/rag/search`: FTS con fuente/cita.
- LanceDB existe bajo `data\lancedb`.
- `POST /api/rag/semantic/reindex` encola un rebuild BGE-M3; `GET /api/jobs/{id}` informa progreso y `DELETE /api/jobs/{id}` lo cancela. Cada fragmento tiene SHA-256 estable; LanceDB usa una tabla temporal por job y SQLite publica el nuevo puntero sólo al terminar. El índice anterior se mantiene buscable durante la reconstrucción y se elimina después del swap.
- `GET /api/rag/semantic/search` entrega fuente, página, número e ID de fragmento. **No es fallback de FTS:** si falta modelo devuelve 503 de modo explícito.
- Las filas antiguas de benchmark quedan fuera del puntero administrado nuevo. No borrar datos heredados sin revisión.

### BGE-M3: instalación verificable

- Modelo: `BAAI/bge-m3`, commit `5617a9f61b028005a4858fdac845db406aefb181`.
- Ubicación: `models\embeddings\bge-m3`.
- Binario principal: 2,271,145,830 bytes, SHA-256 `b5e0ce3470abf5ef3831aa1bd5553b486803e83251590ab7ff35a117cf6aad38`.
- Evidencia completa: `models\embeddings\bge-m3\model-provenance.json`.
- Runtime aprobado: `FlagEmbedding_cpu`, `BGEM3FlagModel(... devices="cpu", use_fp16=False)`, un worker/batch 1.
- Benchmark real: carga 3.31 s, una consulta 0.69 s, vector 1024, RSS 1943.3 MB. Usar cola/carga secuencial; no cargarlo en paralelo con tareas pesadas de RAM/GPU.
- Paquetes reales: `torch 2.14.0+cpu`, `FlagEmbedding 1.4.2`, `lancedb 0.38.0`, `trimesh 4.12.2`, `pypdf 5.9.0`, `fastapi 0.141.1`.
- `fastembed 0.8.0` fue instalado para investigar, pero **no** enumera `BAAI/bge-m3`; no usarlo para este modelo. No aparece en `pyproject.toml`; eliminarlo o declararlo sólo si un futuro uso lo justifica.

### MCP, trabajos, operador y cloud

Herramientas MCP actuales: `system_capabilities`, `brief_analyze_local`, `project_create`, `design_apply_change`, `cloud_consent_record`, `mockup_generate`, `pattern_export`, `techpack_generate`, `job_status`, `job_cancel`, `rag_semantic_search`, `rag_semantic_reindex`, `rag_search`, `rag_import_local_file`, `studio_session_start`, `studio_session_resume`, `studio_audit_log`, `studio_confirm_sensitive_action`, `studio_click`, `studio_keypress`, `studio_type`.

- Cola SQLite: tipos `model_inference`, `embedding_index`, `blender_render`, `voice_transcription`; la segunda tarea `gpu_exclusive` recibe 409 mientras la primera está queued/running.
- Cloud: `POST/GET /api/projects/{id}/cloud-consents` guarda activo, proveedor (`openai`, `deepseek`, `trellis_provider`), propósito, coste estimado, decisión y hora. `local_private` rechaza consentimientos. No hay credenciales, proveedor, túnel, ni transferencia cloud implementada.
- Operator: sólo títulos Fashion CAD Studio, Blender y Fashion CAD Pattern Viewer; sesiones 30 min, exige foco. `PyAutoGUI 0.9.54` está instalado y el operador se desactiva por defecto (`FASHION_CAD_OPERATOR_ENABLED=false`). Hay auditoría SQLite por sesión/acción, pausa durable por pérdida de foco, reanudación explícita, overlay nativo visible, atajo global `Ctrl+Alt+Pause` y confirmaciones de un uso/vigencia 60 s para exportar, imprimir, cloud o sobrescribir. La prueba automatizada usa UI simulada: falta validar físicamente overlay/atajo/foco en Windows supervisado antes de habilitarlo. No ampliar su alcance.

### Interfaz web

- UI estilizada local, selector de modo persistente, proyectos, cambios rápidos, chat local de operaciones, FTS/BGE-M3 con estado de job, botón de exportación mockup/patrón/Tech Pack y botón de operador. Es una superficie CAD desktop intencional (`min-width: 1100px`), no una interfaz móvil.
- El botón de mockup carga el GLB exportado en `Scene.tsx`, lo etiqueta como revisión verificada y lo invalida al cambiar la revisión. La UI ofrece descargas de los últimos artefactos. El brief llama a `POST /api/briefs/local`, propaga componentes/materiales/medidas confirmadas y solicita el ancho × alto × espesor del bolso en mm. API y UI rechazan exportar bolso sin esas dimensiones.
- Build funciona, con chunk diferido Three.js de 925.28 kB (warning no bloqueante por el cargador GLB). Optimizar después de endurecer LanceDB y completar el flujo de activos locales.

---

## 5. API actual

```text
GET  /api/health
GET  /api/capabilities
POST /api/jobs
GET  /api/jobs/{job_id}
DELETE /api/jobs/{job_id}
POST /api/briefs/local
POST /api/projects
GET  /api/projects
GET  /api/projects/{design_id}
POST /api/projects/{design_id}/cloud-consents
GET  /api/projects/{design_id}/cloud-consents
POST /api/projects/{design_id}/operations
POST /api/projects/{design_id}/assistant
POST /api/projects/{design_id}/exports/mockup
POST /api/projects/{design_id}/exports/pattern
POST /api/projects/{design_id}/exports/techpack
POST /api/rag/semantic/reindex
GET  /api/rag/semantic/search
POST /api/rag/documents
POST /api/rag/import
GET  /api/rag/search
POST /api/operator/sessions
DELETE /api/operator/sessions/{session_id}
POST /api/operator/sessions/{session_id}/resume
GET  /api/operator/sessions/{session_id}/audit
POST /api/operator/confirmations
POST /api/operator/click
POST /api/operator/keypress
POST /api/operator/type
```

---

## 6. Verificaciones de arranque

Ejecutar desde PowerShell, sin reiniciar descargas ni borrar caches:

```powershell
Set-Location 'D:\Digital Lab\FashionCAD'
Get-Content .\docs\NEW_CHAT_CONTEXT.md
Get-Content .\docs\IMPLEMENTATION_PLAN.md
Get-Content .\docs\IMPLEMENTATION_STATUS.md
git status --short
.\scripts\benchmark-models.ps1
.\scripts\verify-mvp.ps1
```

Última evidencia: `19 passed`; MCP build pasa; Vite build pasa con un chunk Three.js de 925.28 kB. El chat local aplica componentes/materiales/medidas como revisiones y los modos se persisten. `scripts\verify-semantic-rebuild.ps1` cargó BGE-M3 local, construyó y publicó dos índices consecutivos de un fragmento, verificó la búsqueda y el recuento único en 21.45 s; usa un root de datos único bajo `cache\delivery-verification`, sin tocar datos de usuario. `verify-mvp.ps1` usa un `--basetemp` único para evitar el aviso de permisos de pytest en Windows.

Para iniciar servicios:

```powershell
.\scripts\run-api.ps1
.\scripts\run-web.ps1
```

API: `127.0.0.1:8000`; web: `127.0.0.1:5173`.

---

## 7. Qué falta y orden recomendado

### MVP entregable: bloqueos humanos que permanecen

1. Studio Operator: la automatización sigue desactivada hasta validar físicamente banner/atajo/foco en Windows supervisado; mantener sin shell, navegador, email, passwords, configuración Windows ni paths externos.
2. Patrón: antes de producción real, imprimir, medir 100 ± 1 mm, cortar/coser y corregir con modista/taller.
3. Empaquetado: esta entrega corre en este equipo con Python/Node existentes; aún no hay distribución portable completa bajo `runtime`.

El rebuild LanceDB, el vínculo de GLB/revisión y el análisis local con medidas obligatorias están cerrados para el MVP. Usar `docs\MVP_DELIVERY.md` para la aceptación.

La biblioteca de usuario usa `KNOWLEDGE_BASE_STUDIO\01_THEORY_BOOKS` a `06_SIZE_CHARTS`; no se versiona ni se publica. `docs\KNOWLEDGE_BASE_PLAN.md` corrige el plan de RAG, licencias y futuro fine-tuning.

### P1 — completar visión y activos locales

1. Diseñar importador de fotos/bocetos a `data\incoming` con hashes, orientación, metadatos, referencias a revisión y paths estrictamente internos.
2. Instalar runtime VLM portable **dentro de `runtime`**. `ollama` no existe en el PATH actual; no instalar una aplicación que guarde modelos/runtimes en C:. Elegir llama.cpp/Ollama portable sólo tras investigar el soporte real de Qwen2.5-VL 3B Q4 y su proyector visual.
3. Descargar Qwen sólo con commit, licencia, tamaño, checksum y benchmark. GTX 1060 6 GB: contexto 4096, un proceso GPU, límite de VRAM 4.5 GB; CPU fallback explícito. El fallback actual en `briefs.py` sigue siendo obligatorio.
4. Instalar/medir SigLIP2 para imágenes en LanceDB; no etiquetar una búsqueda como multimodal hasta tener embeddings de imagen reales.
5. RapidOCR para PDFs escaneados; guardar página/confianza y no usar OCR silenciosamente para afirmar contenido.
6. faster-whisper base INT8 CPU para voz; encolar, limitar a 4 hilos y no coincidir con GPU pesada.

### P2 — Blender, cloud y validación industrial

1. Instalar Blender LTS portable en `runtime\blender`, detectarlo mediante configuración y correr headless como job GPU exclusivo. Mantener Trimesh como fallback reproducible.
2. Diseñar proveedor cloud desacoplado. Sólo enviar tras consentimiento por activo registrado; asociar respuesta cloud a revisión con `cloud_assisted`, nunca a medidas confirmadas. Configurar túnel saliente sólo con credenciales/proveedor real elegidos por usuario.
3. Agregar adapter DXF posterior; antes fortalecer tolerancias, grading, margenes/curvas/piquetes y construcción.
4. Imprimir A4/A0, medir cuadrado 100 ± 1 mm, cortar/coser camiseta y bolso, registrar fit/errores y corregir plantillas. Esta validación requiere al usuario/taller y no puede simularse.

---

## 8. Errores/deudas conocidas y decisiones que no deben revertirse sin motivo

- No usar Docker en este MVP: hardware/RAM favorece procesos directos + SQLite.
- No reusar/mover modelos Ollama existentes. No hay Ollama instalado en este host ahora.
- No descargar Qwen/SigLIP/RapidOCR/Whisper hasta su preflight; BGE ya pasó su propio proceso.
- No cambiar BGE a FastEmbed: versión instalada no soporta ese modelo. Si se busca ONNX luego, verificar versión y modelo antes.
- No exponer MCP/API fuera de localhost ni abrir puerto público. El túnel seguro requiere configuración adicional.
- No añadir shell arbitrario a MCP u operador para “facilitar” automatización.
- `pyautogui` está instalado, pero no significa que se autorizó el operador; variable de entorno lo mantiene off.
- El Tech Pack y patrones son borrador técnico; no afirmar cumplimiento de fábrica internacional ni exactitud de grada sin muestra física/patronista.
- La prueba PDF utiliza ReportLab y la prueba GLB usa Trimesh; ambas ya pasaron. El warning Starlette/httpx es upstream/deprecación y no un fallo funcional actual.

---

## 9. Documentos complementarios

- `PROJECT_CHARTER.md`: visión y público.
- `ARCHITECTURE.md`: decisiones estructurales.
- `DATA_PRIVACY.md`: límites local/cloud.
- `OPERATIONS.md`: setup y operación.
- `FACTORY_EXPORT_GUIDE.md`: impresión básica.
- `RAG_LOCAL.md`: límites de biblioteca RAG.
- `IMPLEMENTATION_PLAN.md`: roadmap por fases.
- `IMPLEMENTATION_STATUS.md`: estado y autoevaluación de la sesión anterior.
- `SESSION_HANDOFF.md`: relevo conciso previo; este archivo lo reemplaza como referencia principal para un chat fresco.
- `MVP_DELIVERY.md`: arranque, verificación reproducible, aceptación manual y límites de la entrega MVP.

## 10. Regla de cierre de cada siguiente hito

1. Actualizar `IMPLEMENTATION_STATUS.md` y este archivo con decisión, métrica, comandos y límites.
2. Ejecutar pruebas estrechas y luego API/MCP/web builds si tocaron esas capas.
3. Revisar espacio libre y cachés en D: antes de nuevos pesos.
4. No hacer commit, reset ni limpieza destructiva sin pedirlo explícitamente.
5. Si el nuevo contexto vuelve a acercarse al límite, actualizar este archivo primero y recién después compactar/cambiar de chat.
