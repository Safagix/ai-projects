# EiraLearn: Technical Document (Architecture Focus on FREE Tiers)

## 🏗️ 1. Technology Stack
Todo el stack está optimizado para operar **100% gratis**:
- **Frontend / Fullstack Framework:** Next.js (App Router). Despliegue en **Vercel (Free Hobby Tier)**. Provee computación Edge rápida.
- **Styling:** TailwindCSS + Framer Motion (para transiciones suaves).
- **Backend/Base de Datos:** **Supabase (Free Tier)**. Nos da una base de datos PostgreSQL de 500MB y 1GB de Storage gratuito, ideal para guardar las imágenes subidas de los problemas matemáticos y el texto de las sesiones socráticas.
- **Inteligencia Artificial:** **Google Gemini API (Gemini 1.5 Flash/Pro)**. Excelente Free Tier (15 RPM, 1M tokens/min) y capacidad multimodal nativa brutal para leer imágenes complejas, código y texto matemáticos con OCR integrado.

## 🔄 2. API Endpoints (Next.js Server Actions)
- `POST /api/chat/socratic`: Mantiene la cadena de contexto con Gemini.
- `POST /api/vision/collision`: Recibe la imagen subida, la manda a Supabase Storage (optativo), la pasa a Gemini 1.5 Flash para extraer los "2 conceptos", y retorna el desafío al usuario.
- `POST /api/generate/survival`: Procesa el prompt para extraer palabras de entorno y generar la palabra comodín.

## 🌐 3. Data Flow de Imágenes
1. Usuario "Pega" o "Arrastra" una imagen matemática en el cliente.
2. Next.js convierte el archivo (File) y lo sube al bucket gratuito de Supabase.
3. Se extrae la URL pública.
4. Se envía la URL a la API de Gemini 1.5 junto con el prompt: *"Extrae dos conceptos matemáticos de esta foto"*.
5. Gemini envía los conceptos y el Frontend inicia la cuenta regresiva.
