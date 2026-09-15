# Fashion CAD Studio

MVP local-first para convertir briefs, bocetos y referencias en diseños editables, patrones 1:1 y Tech Packs. El sistema funciona offline para las operaciones técnicas; la nube es opcional y siempre requiere consentimiento por activo.

## Entrega MVP

La entrega y sus límites verificables están en [docs/MVP_DELIVERY.md](docs/MVP_DELIVERY.md). Para validar el conjunto antes de usarlo:

```powershell
.\scripts\verify-mvp.ps1
```

El comando ejecuta pruebas, builds y un rebuild real aislado de BGE-M3; no modifica la biblioteca ni el índice del usuario.

## Estado

Implementado en este primer corte:

- API FastAPI local con proyectos, revisiones y operaciones reversibles.
- Plantillas paramétricas de camiseta y bolso para laptop.
- Exportación SVG, PDF A4 tiled y Tech Pack PDF/XLSX.
- Catálogo de modelos, capacidades locales y política de almacenamiento en `D:`.
- Interfaz React/Three.js y servidor MCP preparados.
- Chat local que convierte instrucciones acotadas en revisiones persistentes (componentes, materiales, medidas y modo).

No se descargan pesos de IA automáticamente. Ejecutá el benchmark antes de descargar un modelo mediante `scripts\setup-local.ps1`.

## Arranque de desarrollo

```powershell
Copy-Item .env.example .env
.\scripts\setup-local.ps1
.\scripts\run-api.ps1
.\scripts\run-web.ps1
```

Abrí `http://127.0.0.1:5173`. La API se documenta en `http://127.0.0.1:8000/docs`.
Para desarrollo con recarga automática de la API: `./scripts/run-api.ps1 -Reload`.

## Biblioteca privada y OCR local

La carpeta privada `KNOWLEDGE_BASE_STUDIO` organiza libros, Tech Packs, materiales, moldes, diccionario visual y tablas de talles. Está excluida de Git y de Vercel. Para actualizar el índice textual:

```powershell
.\scripts\import-knowledge-base.ps1
```

Para un PDF escaneado, el OCR es explícito y local; conserva página y confianza media por fragmento:

```powershell
.\scripts\import-knowledge-base.ps1 -Ocr -MaxOcrPages 300
```

Después, iniciar **Reconstruir índice semántico** desde Studio. No correr OCR y BGE-M3 a la vez en este equipo.

## Vercel

`vercel.json` deja preparada la interfaz Vite para desplegarse como SPA. En Vercel, configurar `VITE_FASHION_CAD_API` con la URL HTTPS de un backend API público separado y volver a desplegar. Esa variable es visible por el navegador: nunca colocar tokens, claves ni rutas locales allí.

La API local completa, BGE-M3 y `KNOWLEDGE_BASE_STUDIO` **no se despliegan en Vercel**: el modelo pesa más que el límite de función y la biblioteca es privada. Para una web funcional pública hace falta elegir y configurar un backend persistente separado; el Studio local sigue funcionando en `127.0.0.1` sin subir datos.

## Conectar una IA por MCP

El conector local MCP está listo para clientes compatibles. Iniciar API, compilar MCP y usar la plantilla [mcp-configs/fashion-cad.local.mcp.json](mcp-configs/fashion-cad.local.mcp.json), cambiando la ruta de ejemplo. La guía completa, incluyendo el límite entre MCP local y un conector remoto para ChatGPT, está en [docs/MCP_CONNECT.md](docs/MCP_CONNECT.md).

## Seguridad

El Studio Operator está desactivado por defecto. Aun al habilitarse, solamente podrá actuar en una sesión visible y en ventanas autorizadas del estudio. No expone shell genérico ni acceso a carpetas personales.
