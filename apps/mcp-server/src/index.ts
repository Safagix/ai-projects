import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { z } from 'zod'

const apiBase = process.env.FASHION_CAD_API_URL ?? 'http://127.0.0.1:8000'

async function api(path: string, method = 'GET', body?: unknown) {
  const response = await fetch(`${apiBase}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  const result = await response.json().catch(() => ({ detail: response.statusText }))
  if (!response.ok) throw new Error(result.detail ?? `Fashion CAD API error ${response.status}`)
  return result
}

const text = (value: unknown) => ({ content: [{ type: 'text' as const, text: JSON.stringify(value, null, 2) }] })
const server = new McpServer({ name: 'fashion-cad-studio', version: '0.1.0' })

server.tool('system_capabilities', 'Muestra modelos locales, modos y disponibilidad.', {}, async () => text(await api('/api/capabilities')))

server.tool('brief_analyze_local', 'Analiza offline un brief y señala medidas faltantes sin inventarlas.', {
  description: z.string().min(3).max(4000), product_type: z.enum(['upper_garment', 'laptop_bag']).optional(),
}, async (input) => text(await api('/api/briefs/local', 'POST', input)))

server.tool('project_create', 'Crea un diseño local. Para laptop_bag, pedir medidas físicas cuando falten.', {
  name: z.string().min(2), product_type: z.enum(['upper_garment', 'laptop_bag']), description: z.string().default(''), mode: z.enum(['local_private', 'hybrid', 'cloud_creative']).default('local_private'),
}, async (input) => text(await api('/api/projects', 'POST', input)))

server.tool('design_apply_change', 'Aplica una operación reversible al diseño.', {
  project_id: z.string().uuid(), kind: z.enum(['add_component', 'remove_component', 'set_materials', 'set_measurement', 'set_description']), value: z.union([z.string(), z.number(), z.array(z.string())]), note: z.string().default(''),
}, async ({ project_id, ...operation }) => text(await api(`/api/projects/${project_id}/operations`, 'POST', operation)))
server.tool('cloud_consent_record', 'Registra consentimiento informado; no envía el activo ni llama al proveedor.', {
  project_id: z.string().uuid(), asset_id: z.string().min(1).max(200).regex(/^[A-Za-z0-9._ -]+$/), provider: z.enum(['openai', 'deepseek', 'trellis_provider']), purpose: z.string().min(3).max(500), estimated_cost_usd: z.number().min(0).max(1000), approved: z.boolean(),
}, async ({ project_id, ...payload }) => text(await api(`/api/projects/${project_id}/cloud-consents`, 'POST', payload)))

server.tool('mockup_generate', 'Genera un GLB técnico local y metadatos desde la revisión actual.', { project_id: z.string().uuid() }, async ({ project_id }) => text(await api(`/api/projects/${project_id}/exports/mockup`, 'POST')))
server.tool('pattern_export', 'Genera SVG y PDF A4 tiled 1:1.', { project_id: z.string().uuid() }, async ({ project_id }) => text(await api(`/api/projects/${project_id}/exports/pattern`, 'POST')))
server.tool('techpack_generate', 'Genera Tech Pack PDF y XLSX.', { project_id: z.string().uuid() }, async ({ project_id }) => text(await api(`/api/projects/${project_id}/exports/techpack`, 'POST')))
server.tool('job_status', 'Consulta estado de un trabajo local; no inicia comandos arbitrarios.', { job_id: z.string().uuid() }, async ({ job_id }) => text(await api(`/api/jobs/${job_id}`)))
server.tool('job_cancel', 'Cancela un trabajo en cola o ejecución antes de que publique resultados nuevos.', { job_id: z.string().uuid() }, async ({ job_id }) => text(await api(`/api/jobs/${job_id}`, 'DELETE')))
server.tool('rag_semantic_search', 'Busca en LanceDB con BGE-M3 local cuando el benchmark/modelo estén disponibles.', { query: z.string().min(2) }, async ({ query }) => text(await api(`/api/rag/semantic/search?query=${encodeURIComponent(query)}`)))
server.tool('rag_semantic_reindex', 'Encola un rebuild atómico de la biblioteca con BGE-M3 local. La búsqueda mantiene el índice anterior hasta completarse; consultar job_status. No llama cloud.', {}, async () => text(await api('/api/rag/semantic/reindex', 'POST')))
server.tool('rag_search', 'Busca conocimiento local indexado.', { query: z.string().min(2) }, async ({ query }) => text(await api(`/api/rag/search?query=${encodeURIComponent(query)}`)))
server.tool('rag_import_local_file', 'Indexa un TXT, Markdown o PDF desde data\\library. No acepta rutas fuera de la biblioteca local.', {
  relative_path: z.string().min(1).max(300),
}, async (input) => text(await api('/api/rag/import', 'POST', input)))

server.tool('studio_session_start', 'Activa un operador visible y temporal. Solo para ventanas de Fashion CAD.', {
  requested_windows: z.array(z.enum(['Fashion CAD Studio', 'Blender', 'Fashion CAD Pattern Viewer'])).min(1),
}, async (input) => text(await api('/api/operator/sessions', 'POST', input)))

server.tool('studio_session_resume', 'Reanuda una sesión pausada solo si una ventana permitida recuperó el foco.', {
  session_id: z.string().uuid(),
}, async ({ session_id }) => text(await api(`/api/operator/sessions/${session_id}/resume`, 'POST')))

server.tool('studio_audit_log', 'Consulta el registro persistente y local de acciones del Studio Operator.', {
  session_id: z.string().uuid(),
}, async ({ session_id }) => text(await api(`/api/operator/sessions/${session_id}/audit`)))

server.tool('studio_confirm_sensitive_action', 'Registra confirmación humana explícita, válida por un minuto, para exportar, imprimir, enviar cloud o sobrescribir. No llamar sin confirmación humana.', {
  session_id: z.string().uuid(), window_name: z.enum(['Fashion CAD Studio', 'Blender', 'Fashion CAD Pattern Viewer']), intent: z.enum(['export', 'print', 'cloud', 'overwrite']), summary: z.string().min(3).max(300),
}, async (input) => text(await api('/api/operator/confirmations', 'POST', input)))

server.tool('studio_click', 'Hace click relativo a una ventana permitida de una sesión activa. Acciones sensibles requieren confirmación humana previa.', {
  session_id: z.string().uuid(), window_name: z.enum(['Fashion CAD Studio', 'Blender', 'Fashion CAD Pattern Viewer']), x: z.number().int().min(0).max(3840), y: z.number().int().min(0).max(2160), intent: z.enum(['edit', 'export', 'print', 'cloud', 'overwrite']).default('edit'), confirmation_id: z.string().uuid().optional(),
}, async (input) => text(await api('/api/operator/click', 'POST', input)))

server.tool('studio_keypress', 'Envía una tecla a la ventana permitida con foco. Acciones sensibles requieren confirmación humana previa.', {
  session_id: z.string().uuid(), window_name: z.enum(['Fashion CAD Studio', 'Blender', 'Fashion CAD Pattern Viewer']), key: z.string().min(1).max(40), intent: z.enum(['edit', 'export', 'print', 'cloud', 'overwrite']).default('edit'), confirmation_id: z.string().uuid().optional(),
}, async (input) => text(await api('/api/operator/keypress', 'POST', input)))

server.tool('studio_type', 'Escribe texto en una ventana permitida y enfocada. Acciones sensibles requieren confirmación humana previa.', {
  session_id: z.string().uuid(), window_name: z.enum(['Fashion CAD Studio', 'Blender', 'Fashion CAD Pattern Viewer']), text: z.string().min(1).max(200), intent: z.enum(['edit', 'export', 'print', 'cloud', 'overwrite']).default('edit'), confirmation_id: z.string().uuid().optional(),
}, async (input) => text(await api('/api/operator/type', 'POST', input)))

await server.connect(new StdioServerTransport())
