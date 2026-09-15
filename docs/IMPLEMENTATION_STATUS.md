# Estado de implementación — 2026-09-15

## Entregado localmente

- Studio desktop React/Vite/Three.js conectado a FastAPI local: crear/seleccionar proyecto, analizar brief, cambios rápidos, modo persistente, chat local de operaciones, búsqueda RAG y exportaciones.
- Chat local determinista y auditable: reconoce componentes, materiales y medidas de laptop; convierte cada cambio en una revisión. No representa un proveedor cloud ni transmite activos.
- Dos familias: camiseta unisex y bolso laptop. El bolso bloquea GLB, patrón y Tech Pack hasta tener ancho, alto y espesor físicos.
- Exportadores locales: mockup GLB técnico, SVG/PDF A4 tiled/PDF A0 con control de 100 mm y Tech Pack PDF/XLSX. Son borradores técnicos: faltan prueba física y revisión de taller.
- SQLite FTS y LanceDB/BGE-M3 local con rebuild atómico, cancelable y sin duplicados. El índice previo se mantiene activo hasta el swap completo.
- La reconstrucción semántica fue corregida para procesar cuatro fragmentos por lote; una prueba verifica secuencia `[4, 1]`.
- Biblioteca privada organizada como `KNOWLEDGE_BASE_STUDIO\01…06`, ignorada por Git/Vercel. Tres libros textuales y documentación interna quedaron importados (933 fragmentos antes del OCR nuevo).
- RapidOCR + ONNX Runtime + PyMuPDF están instalados dentro del entorno de FashionCAD. La importación OCR es explícita, local y registra página/confianza por fragmento; máximo 300 páginas por defecto. La corrida integral de 126 páginas se canceló sin escritura tras más de 15 min; no se declara indexada.
- Operator cerrado y deshabilitado por defecto; su prueba automática no sustituye validación física de banner, foco y `Ctrl+Alt+Pause`.
- GitHub: rama aislada `fashion-cad-studio` publicada en `Safagix/ai-projects`. Vercel está preparado para la SPA únicamente.

## Evidencia vigente

- Verificación integral: **21 passed** en `apps/api/tests`, MCP build, Studio build y rebuild BGE real aislado aprobados (siete warnings de deprecación upstream; warning no bloqueante de chunk Three.js 925.28 kB).
- QA del navegador: chat local creó un bolso con medidas/componentes/material y habilitó exportación; el modo híbrido persistió como nueva revisión.
- BGE-M3 previo: carga 3.31 s, consulta 0.69 s, vector 1024, RSS 1.94 GB.
- RapidOCR verificó extracción local de primera página de los PDF escaneados; la importación completa debe comprobarse por fuente/fragmento/confianza antes de declararla terminada.

## Operación

```powershell
Set-Location 'D:\Digital Lab\FashionCAD'
.\scripts\run-api.ps1          # terminal 1
.\scripts\run-web.ps1          # terminal 2
```

Para recarga de API: `./scripts/run-api.ps1 -Reload`.

```powershell
.\scripts\import-knowledge-base.ps1
.\scripts\import-knowledge-base.ps1 -Ocr -MaxOcrPages 300
.\scripts\verify-mvp.ps1
```

No correr OCR y BGE-M3 simultáneamente en esta PC de 16 GB RAM.

## Pendiente o requiere decisión externa

| Tema | Estado real | Próximo paso seguro |
|---|---|---|
| OCR de `Bag Design` | La corrida integral de 126 páginas se canceló sin fragmentos tras más de 15 min. | Agregar progreso/reanudación; no iniciar `Patternmaking` (848 páginas) sin reservar tiempo y límite explícito. |
| Rebuild BGE completo | Lote 4 llegó a 12/933 en 63 s y fue cancelado, ~80 min estimados. | Optimizar/medir antes de un rebuild completo; FTS sigue disponible. |
| Vercel público | Solo SPA preparada. API local, BGE y biblioteca privada no se pueden desplegar tal cual. | Elegir backend persistente, configurar CORS/identidad/almacenamiento; confirmar justo antes de publicar. |
| Qwen-VL/SigLIP2/voz/Blender | No instalados ni simulados. | Preflight de licencia, espacio, RAM/VRAM y benchmark en `D:`. |
| Producción industrial | No validada físicamente. | Imprimir control 100 ± 1 mm, cortar/coser y corregir con patronista/taller. |

## Cierre requerido de este hito

1. Agregar progreso/reanudación si se decide OCR integral; mantener la importación explícita y auditable.
2. Optimizar el rebuild BGE completo antes de consumir ~80 min de CPU.
3. Confirmar que el commit más reciente esté enviado a `ai-projects/fashion-cad-studio` antes de seguir con otra fase.
