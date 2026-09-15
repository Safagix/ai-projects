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

No se descargan pesos de IA automáticamente. Ejecutá el benchmark antes de descargar un modelo mediante `scripts\setup-local.ps1`.

## Arranque de desarrollo

```powershell
Copy-Item .env.example .env
.\scripts\setup-local.ps1
.\scripts\run-api.ps1
.\scripts\run-web.ps1
```

Abrí `http://127.0.0.1:5173`. La API se documenta en `http://127.0.0.1:8000/docs`.

## Seguridad

El Studio Operator está desactivado por defecto. Aun al habilitarse, solamente podrá actuar en una sesión visible y en ventanas autorizadas del estudio. No expone shell genérico ni acceso a carpetas personales.
