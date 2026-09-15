# Plan de implementación integral — Fashion CAD Studio MVP

## Resultado de esta implementación

Un estudio local-first en `D:\Digital Lab\FashionCAD` que maneja una camiseta regular y un bolso/funda de laptop como documentos de diseño versionados. Desde una misma revisión genera mockup técnico 3D, patrón vectorial 1:1 y Tech Pack. Funciona sin Internet para edición, exportación y búsqueda; la nube es opt-in por activo y queda auditada.

## Invariantes no negociables

- Todos los activos, modelos, cachés, entornos y artefactos permanecen bajo la raíz del proyecto en `D:`.
- El modo `local_private` no puede invocar ni preparar envíos cloud.
- Una medida inferida desde imagen nunca se marca como confirmada.
- Un bolso para laptop exige ancho, alto y espesor físicos o modelo exacto.
- Un único trabajo GPU exclusivo puede estar activo.
- El operador no obtiene shell, navegador, credenciales ni rutas externas al proyecto.
- Patrón, mockup y Tech Pack se derivan de la misma revisión inmutable de `DesignDocument`.

## Secuencia de entrega

| Fase | Entregable | Estado | Criterio de salida |
|---|---|---:|---|
| 0 | Raíz `D:`, cachés, límites de disco, manifiesto de modelos | Hecho | benchmark sin descarga y 30 GB libres mínimos |
| 1 | API, SQLite, revisiones, camiseta y bolso base | Hecho | cambios versionados y exportación reproducible |
| 2 | Patrón 1:1 enriquecido y controles de escala | Base hecha | A4/A0, SVG físico, tolerancia de cuadrado de control |
| 3 | Mockup paramétrico GLB técnico | Base hecha | GLB descargable y vinculado a revisión |
| 4 | RAG documental y vectorial | BGE/LanceDB hecho; visión/OCR pendiente | TXT/MD/PDF local; LanceDB tras benchmark BGE/SigLIP |
| 5 | Runtime de modelos locales y benchmark | BGE hecho; VL/voz pendiente | carga, VRAM, latencia y licencia registrados antes de adopción |
| 6 | Studio web con edición, voz y artefactos | En curso | interfaz operable sin cloud |
| 7 | Tech Pack industrial enriquecido | Base hecha | BOM, POM, tolerancias, grading, costuras, empaque y evidencia |
| 8 | MCP semántico y Studio Operator | En curso | allowlist, caducidad, kill switch, auditoría y pruebas |
| 9 | Cloud mejorado con consentimiento | Pendiente | consentimiento por activo, coste y auditoría |
| 10 | Validación física y endurecimiento | Pendiente | impresión, corte y medición 100 ± 1 mm |

## Fases detalladas y dependencias

### 2. Patrón industrial paramétrico

1. Añadir metadatos de pieza: talla, espejo, doblez, hilo, margen, piquetes y construcción.
2. Añadir PDF A0, registro de hojas A4 y control de escala repetido por hoja.
3. Registrar en artefacto el `design_id`, revisión, hash de entrada y motor de patrón.
4. Probar que cada cambio de componente cambia las piezas aplicables y que el PDF conserva unidades milimétricas.

Depende de: Fase 1. No depende de IA ni de cloud.

### 3. Mockup GLB paramétrico

1. Generar malla técnica local desde los componentes y medidas de `DesignDocument`.
2. Exportar GLB, material PBR simple, metadatos de revisión y captura de previsualización.
3. Usar Blender headless cuando esté instalado en `runtime\blender`; mantener generador Python como fallback reproducible.
4. Visualizar el GLB real en Three.js; no prometer reconstrucción fotorrealista a partir de una única foto.

Depende de: Fase 1. Se ejecuta con cola GPU exclusiva solo cuando Blender es el motor.

### 4. RAG multimodal

1. Ingesta actual: TXT, Markdown y PDF textual, fragmentos y FTS con citas.
2. Añadir LanceDB en `data\lancedb` con interfaz de índice separada y migración reanudable.
3. Medir BGE-M3 ONNX INT8 para texto y SigLIP2 para imágenes; indexar solo si la latencia/memoria entran en presupuesto.
4. Añadir RapidOCR para PDFs escaneados y guardar texto, página, confianza y fuente.
5. Evaluar recuperación con un conjunto local de consultas en español, portugués e inglés; no activar cloud por una búsqueda.

Depende de: Fase 0. La adopción de pesos depende del benchmark de Fase 5.

### 5. Runtime local de IA

1. Resolver pesos únicamente usando `models/manifest.json`, licencia, checksum, tamaño y espacio libre.
2. Probar Qwen2.5-VL-3B Q4 en un único proceso, contexto máximo 4096, con guardia de VRAM de 4.5 GB.
3. Mantener analizador determinista como fallback cuando no haya peso, memoria o confianza suficiente.
4. Ejecutar voz con faster-whisper base INT8 solo cuando GPU esté libre; CPU es el valor por defecto.
5. Registrar benchmark de carga, VRAM, RAM, tokens/s y fallos, sin reusar ni mover modelos de Ollama existentes.

Depende de: Fase 0. Ninguna descarga ocurre si baja de 30 GB libres.

### 6. Studio web

1. Mostrar estado de modelos, cola, fuente de RAG y origen de cada resultado.
2. Permitir importar archivos a `data\library` mediante selector restringido y ver citas RAG.
3. Usar GLB generado en la escena y seleccionar componentes con raycast.
4. Implementar chat/voz local, edición con preview y aplicar/undo sobre revisiones.
5. Mostrar una barrera de consentimiento antes de enviar cualquier activo a cloud.

Depende de: Fases 3, 4 y 5 para las capacidades correspondientes.

### 7. Tech Pack

1. Generar flat técnico, BOM, POM, tolerancias, grading, costuras, SPI, avíos, etiquetas, empaque y revisión.
2. Generar PDF y XLSX con trazabilidad de fuente; los campos desconocidos deben decir `por confirmar`.
3. Incorporar evidencia de materiales reciclados como cita RAG, no como afirmación inventada.

Depende de: Fases 1 y 4.

### 8. MCP y operador

1. Exponer solamente herramientas tipadas de proyecto, activos, diseños, patrones, mockup, Tech Pack, RAG y trabajos.
2. Implementar cola SQLite, exclusión de GPU, cancelación y estado de trabajo.
3. Aplicar operador con título de ventana allowlist, caducidad de 30 min, overlay, registro, foco estricto y `Ctrl+Alt+Pause`.
4. Requerir confirmación para impresión, exportación, sobreescritura, cloud o salida de directorio permitido.
5. Conectar cloud mediante túnel saliente autenticado solo después de revisar configuración; sin puertos públicos.

Depende de: Fases 1, 3, 4 y 6.

### 9. Cloud mejorado

1. Crear un adaptador de proveedor desacoplado de la API local.
2. Exigir consentimiento que incluya activo, propósito, proveedor y estimación antes de cada envío.
3. Guardar resultado cloud como evidencia de revisión, diferenciada de datos confirmados.
4. Enrutar: local primero; cloud solo por baja confianza, ambigüedad o solicitud explícita.

Depende de: Fases 5, 6 y 8. Requiere credenciales del usuario; no se simulan ni se almacenan en el repositorio.

### 10. Aceptación y lanzamiento del MVP

- Ejecutar offline con red desactivada.
- Validar patrón impreso: cuadrado de 100 mm dentro de 100 ± 1 mm.
- Coser y medir una camiseta y un bolso con taller/modista.
- Verificar que un cambio de bolsillo produce una nueva revisión coherente de los tres artefactos.
- Ejecutar pruebas de ventana prohibida, caducidad y kill switch del operador.
- Validar instalación limpia desde `scripts\setup-local.ps1` con cachés en `D:`.

## Protocolo de actualización

Cada fase cambia este archivo con fecha, métricas y evidencia de pruebas. Una fase que requiera pesos, credenciales, una impresora o validación física se marca como bloqueada por recurso externo, nunca como terminada por simulación.