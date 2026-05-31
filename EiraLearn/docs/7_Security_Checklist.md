# EiraLearn: Security Check List (SCL)

Dado que la aplicación procesará información de exámenes y estará en la nube gratis, hay que blindar todo abuso.

- [ ] **API Key Protection:** La API Key de Gemini (`GEMINI_API_KEY`) y la Service Key de Supabase estarán estrictamente en Variables de Entorno del Servidor (`.env.local` / Vercel Env Vars). NUNCA expuestas al cliente Next.js.
- [ ] **Data Sanitization:** Todos los textos inyectados por el usuario se purifican antes de guardarlos en PostgreSQL para prevenir SQL Injection (Supabase/Prisma lo hace por defecto, pero validaremos con Zod).
- [ ] **RLS Restrictions:** Row Level Security activado en todas las tablas de Supabase. Nadie puede leer las sesiones Socráticas de otro usuario.
- [ ] **Image Weight & Mime Limiting:** Límite draconiano en el frontend de 3MB por imagen (para proteger el 1GB mensual de Storage Gratis de Supabase). Solo se aceptan `.jpg, .png, .webp`. Evitamos PDFs completos en el MVP para ahorrar tokens y espacio.
- [ ] **Rate Limiting Local:** Como Gemini Free Tier soporta 15 RPM (Request por Minuto), el frontend incluirá un debouncer y bloqueo que obligue al usuario a esperar entre 10-15 segundos entre cada respuesta Socrática para no crashear la cuota global.
- [ ] **Auth Policy:** Obligar a que cada usuario verifique su mail por Supabase Auth para disuadir creación de bots masivos.
