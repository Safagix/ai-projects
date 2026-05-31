# EiraLearn: Backend & Data Structure Document

La estructura será alojada enteramente en el Free Tier de **Supabase (PostgreSQL)**.

## 📊 1. Core Schema Definition

**`users` table**
- `id` (uuid, PK, ref auth.users)
- `created_at` (timestamp)
- `mext_specialty` (text) - Ej. Física, Informática, Química.

**`sessions` table** (Agrupa ejercicios o chats)
- `id` (uuid, PK)
- `user_id` (uuid, FK users)
- `mode_type` (varchar) - 'survival', 'collision', 'socratic'
- `created_at` (timestamp)

**`messages` table** (El contenido de la sesión)
- `id` (uuid, PK)
- `session_id` (uuid, FK sessions)
- `role` (varchar) - 'user' | 'assistant' | 'system'
- `content` (text)
- `image_url` (text, nullable) - Link público del Supabase Storage si subió foto.
- `created_at` (timestamp)

## 🗄️ 2. Supabase Storage (Free 1GB)
- **Bucket `exercises_images`:** Configurado estrictamente para guardar las capturas, PDFs de una sola página y recortes de problemas matemáticos.
- **Políticas RLS:** Los usuarios solo pueden visualizar o eliminar los archivos que subieron con su propio `auth.uid()`.

## ⚡ 3. Edge Functions (Optativo)
Para evitar saturar los Server Actions pesados, podemos usar Supabase Edge Functions con Deno en caso de necesitar procesar y recortar imágenes brutalmente grandes antes de pasarlas a Gemini. O directamente redimensionar la imagen en el cliente web antes de subirla.
