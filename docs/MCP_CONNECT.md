# Conectar Fashion CAD con una IA por MCP

## Qué queda disponible hoy

El conector local `apps/mcp-server` ya expone herramientas de diseño, chat local, exportaciones y RAG. No contiene claves, no ejecuta shell arbitrario y sólo habla con la API local `127.0.0.1:8000`.

1. En una terminal, iniciar `./scripts/run-api.ps1`.
2. Compilar una vez: `npm --prefix apps/mcp-server run build`.
3. Copiar `mcp-configs/fashion-cad.local.mcp.json` en la configuración MCP del cliente y cambiar `D:\\YOUR_FASHION_CAD_FOLDER` por la ruta real.
4. Reiniciar el cliente MCP y comprobar `system_capabilities`.

Los clientes que admiten MCP por proceso local (por ejemplo Claude Desktop, Cursor u otros clientes compatibles) pueden usar esa configuración. Cada usuario ejecuta su propia API y su propia biblioteca: sus PDFs no se comparten entre personas.

## ChatGPT y acceso remoto

ChatGPT conecta a servidores MCP **remotos**, no directamente a `localhost`. Para ofrecerlo a personas desde ChatGPT se necesita un endpoint Streamable HTTP público con autenticación por usuario, control de origen, autorización por biblioteca y backend persistente. No se publica un endpoint anónimo porque podría exponer diseños, búsquedas o gastos de terceros.

La implementación posterior debe separar:

| Superficie | Dónde | Datos permitidos |
|---|---|---|
| Web Vercel | Vercel | Interfaz, autenticación, proyectos del usuario autenticado |
| MCP remoto `/mcp` | Vercel/servicio compatible | Herramientas autenticadas y datos autorizados por usuario |
| Biblioteca personal | Equipo del usuario o almacenamiento privado | Nunca se envía por defecto |
| BGE-M3/OCR pesado | Equipo del usuario o worker dedicado | No en Vercel Function |

Antes de habilitar el MCP remoto, elegir proveedor de identidad/base de datos y definir si cada usuario tendrá biblioteca propia, compartida por equipo, o ambas. Para ChatGPT Business/Enterprise/Edu, un admin configura el endpoint en Developer Mode y revisa/publica las acciones. Los permisos de escritura deben seguir solicitando confirmación.

## Herramientas principales

- `design_chat_local`: interpreta una orden en español y deja revisiones auditables.
- `design_apply_change`: cambio reversible, incluso `set_mode`.
- `rag_search` / `rag_semantic_search`: búsqueda con procedencia local.
- `rag_import_local_file`: importación confinada a `KNOWLEDGE_BASE_STUDIO`; OCR siempre explícito.
- `mockup_generate`, `pattern_export`, `techpack_generate`: artefactos locales vinculados a revisión.

No pedir al modelo contraseñas, rutas externas, shell ni automatización de Windows fuera de la allowlist del Studio Operator.
