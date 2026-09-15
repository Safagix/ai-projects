# Arquitectura

`DesignDocument` es la fuente de verdad. API, mockup, patrón y Tech Pack trabajan sobre la misma revisión. SQLite persiste metadatos y cola; LanceDB se añadirá como índice multimodal cuando los modelos locales hayan superado benchmark.

El frontend usa React/Three.js. FastAPI produce artefactos locales. El MCP traduce herramientas tipadas hacia la API. El Studio Operator es un adaptador separado y desactivado por defecto.
