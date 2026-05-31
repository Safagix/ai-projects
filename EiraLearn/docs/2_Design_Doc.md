# EiraLearn: Design Document (Aesthetics & UI/UX)

*Nota: La dirección estética precisa será debatida y definida en una etapa posterior con el usuario. Esta es la base estructural.*

## 👁️ 1. Look & Feel (Pendiente de iteración)
- **Concepto Inicial:** Interfaz limpia, cero distracciones, modo oscuro por defecto. Debe sentirse como la terminal de una nave espacial y no como una aburrida plataforma escolar.
- **Aesthetic Markers:** Glassmorphism sutil para destacar el contenido en foco, tipografía de alta legibilidad (ej. Inter o Roboto Mono para matemática).

## 🧩 2. Estructura de Interfaz (Wireframing)
- **Área de Entrada Híbrida (Input Zone):** Un cuadro central expansible donde el usuario puede tipear texto o directamente Soltar (Drag & Drop) una imagen (screens, fotos de cuadernos).
- **Selector de Modo:** Navegación minimalista para elegir entre `[Supervivencia]`, `[Colisión]` y `[Socrático]`.
- **Área de Feedback (AI Zone):** El chat/respuesta donde Eira cuestiona y evalúa.

## 🎨 3. Component Library
- **Tailwind CSS:** Para utilidades rápidas y responsivas.
- **Radix UI o Shadcn/ui:** Accesibilidad nativa y componentes destilados para construir rápido la UI free.
