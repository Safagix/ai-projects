# Plan corregido de base de conocimiento — 2026-09-15

## Principio clave

Los libros, PDFs e imágenes del usuario sirven para **recuperación local con citas (RAG)**. No entrenan automáticamente a ChatGPT ni a un modelo local. Un fine-tuning responsable requiere un dataset propio/licenciado, ejemplos entrada→salida, separación train/evaluación y una evaluación de regresión.

## Estructura local

`KNOWLEDGE_BASE_STUDIO` queda fuera de GitHub, Vercel y cualquier despliegue cloud. La clasificación es:

| Carpeta | Contenido permitido | Procesamiento |
|---|---|---|
| `01_THEORY_BOOKS` | Libros/PDF del usuario | extracción textual local + BGE-M3, citando página/fragmento |
| `02_TECH_PACKS_REALES` | propios, públicos con licencia o autorizados | extracción estructurada de BOM/POM; conservar fuente/licencia |
| `03_SUSTAINABLE_MATERIALS` | CSV/JSON con fecha y fuente | lectura determinista, sin inventar precio/disponibilidad |
| `04_PATTERN_VECTOR` | SVG/DXF con licencia | validación de unidades/escala y plantillas, nunca copia ciega |
| `05_VISUAL_DICTIONARY` | detalles técnicos etiquetados | pendiente de visión local/SigLIP2; guardar derechos y etiquetas |
| `06_SIZE_CHARTS` | tablas y regla tiled | lectura determinista y prueba de 100 mm |

## Correcciones al plan original

1. No descargar “Tech Packs reales” desde Google/Pinterest sin licencia: sirven como descubrimiento, no como autorización de reutilización. Priorizar plantillas propias, documentación pública de fabricantes y ejemplos con licencia explícita.
2. `availability_paraguay` y `cost_band` deben tener URL, fecha y proveedor. Si no existe evidencia, usar `por_confirmar`.
3. SVG/DXF deben tener licencia, unidades y talla base. Los patrones de Seamly2D/Valentina son referencias de formato; no habilitan redistribuir patrones de terceros.
4. Fotos deben incluir autor/origen/permiso. La visión puede sugerir componentes, pero no confirmar medidas, composición ni especificaciones de fábrica.
5. Para un futuro fine-tuning: crear primero un set de 100–300 briefs propios con el Tech Pack revisado por humano como salida, y un conjunto de evaluación separado. RAG + reglas siguen siendo la ruta inicial más segura y barata en este hardware.

## Próximo flujo operativo

1. Copiar archivos propios a su categoría.
2. Registrar metadatos mínimos: título, tipo, licencia/origen, fecha, idioma y producto.
3. Importar los PDF textuales a la biblioteca local y ejecutar rebuild BGE-M3.
4. Revisar citas antes de usar material, POM o tolerancia en una exportación.
5. Agregar OCR/visión sólo después de benchmark, licencia y preflight de espacio/RAM.
