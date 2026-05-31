# Guía de Configuración Cerebral: Qwen 2.5 (Eira V2)

**Modelo Seleccionado:** Qwen 2.5 3B Instruct
**Hardware Target:** AMD Ryzen 3 3200G (Vega 8)
**Objetivo:** Fluidez en Español y Japonés con respuesta rápida.

## 1. Descarga en LM Studio

1. Abre **LM Studio**.
2. Ve a la pestaña de **Búsqueda (Lupa)**.
3. Escribe: `Qwen 2.5 3B Instruct`.
4. Busca los resultados subidos por `bartowski` o `lmstudio-community` (son los más fiables).
5. En el panel derecho, busca la versión **Q4_K_M.gguf**.
    * *Tamaño aprox:* ~2.0 GB.
    * *Razón:* Es el balance perfecto entre velocidad e inteligencia. No bajes Q8 (muy pesado).
6. Haz clic en **Download**.

## 2. Carga y Configuración (Importante)

Una vez descargado, ve a la pestaña **AI Chat** (bocadillo de diálogo):

1. **Select Model:** Elige `Qwen 2.5 3B Instruct` que acabas de bajar.
2. **System Prompt:** (Copia y pega esto en "System settings" a la derecha):

    ```text
    Eres Eira, una asistente virtual avanzada. 
    Tu personalidad es servicial, inteligente y cálida.
    Hablas español fluido y puedes hablar japonés si se requiere.
    Tus respuestas son concisas y directas (máximo 2 frases).
    ```

3. **Hardware Settings (Panel Derecho - "Advance" o "GPU"):**
    * **GPU Offload:** Marca la casilla.
    * **Offload Ratio:** Mueve la barra al **MÁXIMO (Max)**. (Tu Vega 8 puede ayudar).
    * *Nota:* Si notas que la PC se congela, baja la barra a 0 y usa solo CPU Threads: 4.

## 3. Iniciar Servidor

1. Ve a la pestaña **Local Server** (icono `<->` doble flecha).
2. Asegúrate que el puerto sea `1234`.
3. Haz clic en **Start Server**.

✅ **Listo.** Ahora ejecuta `main_eira_lab.py` y Eira usará este nuevo cerebro.
