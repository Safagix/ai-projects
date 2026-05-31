# 🌐 EIRA MULTILINGUAL ARCHITECTURE REPORT (ZERO COST)

Este documento define la arquitectura técnica para dotar a Eira de **poliglotismo fluido** utilizando herramientas de código abierto y APIs gratuitas, optimizadas para hardware modesto (Ryzen 3).

---

## 1. REQUISITO FUNCIONAL

El usuario podrá cambiar el idioma de todo el sistema (Oídos y Voz) con un simple comando verbal.

* **Español (Base):** "Eira, cámbiate a inglés."
* **Inglés:** "Eira, switch to Japanese."
* **Japonés:** "Eira, switch to Spanish." (o comando en japonés)

---

## 2. PILA TECNOLÓGICA & CONFIGURACIÓN

### 👂 OÍDOS: OpenAI Whisper (Local)

Actualmente usamos `SpeechRecognition` (Google API). Para este requerimiento, **debemos migrar a `openai-whisper` (Python)** corriendo localmente ("base" o "small").

* **Configuración Clave:** El parámetro `language`.
* **Por defecto:** Whisper intenta detectar el idioma (`None`), pero esto añade latencia y error.
* **Estrategia:** Forzaremos el parámetro `language` según la variable de estado global de Eira.

**Código de Implementación:**

```python
import whisper

# Cargar modelo una sola vez (al inicio)
model = whisper.load_model("base") 

# Al escuchar (bucle principal)
# 'current_lang' es una variable global: "es", "en", "ja"
result = model.transcribe("audio_temp.wav", language=current_lang, fp16=False)
user_text = result["text"]
```

### 🧠 CEREBRO: Ollama / Gemini

No necesitamos re-entrenar. Solo inyectar la instrucción en el `System Prompt` dinámicamente.

**Lógica de Prompting:**
Cuando detectamos un cambio de idioma, actualizamos el `system_prompt` que se envía a Ollama:

* **ES:** "Eres Eira... Responde siempre en Español."
* **EN:** "You are Eira... Always answer in English."
* **JA:** "あなたはエイラです... 常に日本語で答えてください。"

### 🗣️ VOZ: Edge-TTS

Edge-TTS soporta todos los idiomas requeridos con calidad neuronal gratuita.

**IDs de Voces Seleccionadas:**

* 🇪🇸 **Español:** `es-MX-DaliaNeural` (Cálida y clara)
* 🇺🇸 **Inglés:** `en-US-JennyNeural` (Estándar, muy fluida)
* 🇯🇵 **Japonés:** `ja-JP-NanamiNeural` (Natural y popular)

---

## 3. LÓGICA DE DETECCIÓN (PSEUDOCÓDIGO)

El flujo se integra en `eira_brain.py` dentro de la función `think()` o un pre-procesador.

```python
# VARIABLES GLOBALES
CURRENT_LANG = "es"
VOICE_ID = "es-MX-DaliaNeural"

def process_command(user_text):
    global CURRENT_LANG, VOICE_ID
    
    # 1. DETECTOR DE CAMBIO DE IDIOMA (Simple Keyword Matching)
    text_lower = user_text.lower()
    
    if "switch to english" in text_lower or "cambiate a ingles" in text_lower:
        CURRENT_LANG = "en"
        VOICE_ID = "en-US-JennyNeural"
        return "Acknowledged. Switching to English mode."
        
    elif "switch to japanese" in text_lower or "cambiate a japones" in text_lower:
        CURRENT_LANG = "ja"
        VOICE_ID = "ja-JP-NanamiNeural"
        return "承知いたしました。日本語モードに切り替えます。" # (Entendido. Cambio a modo japonés)
        
    elif "switch to spanish" in text_lower or "cambia a español" in text_lower:
        CURRENT_LANG = "es"
        VOICE_ID = "es-MX-DaliaNeural"
        return "Entendido. Volviendo al español."

    # 2. SI NO ES COMANDO, PASAR AL CEREBRO (LLM)
    # Inyectar instrucción de idioma en el prompt
    response = llm.generate(prompt=user_text, system_lang=CURRENT_LANG)
    return response

# 3. HABLAR (TTS)
def speak(text):
    edge_tts.Communicate(text, VOICE_ID).save("audio.mp3")
    play("audio.mp3")
```

---

## 4. RIESGOS IDENTIFICADOS

1. **Latencia de Carga (Whisper):**
    * El modelo `base` de Whisper es rápido, pero la transcripción local *siempre* será más lenta que la API de Google actual (especialmente en CPU Ryzen 3).
    * *Mitigación:* Usar `faster-whisper` (librería optimizada) o mantener Google Speech (`SpeechRecognition`) y cambiar dinámicamente el parámetro `language="es-ES"`, `en-US` o `ja-JP`. **Investigación adicional:** `SpeechRecognition` de Python TAMBIÉN soporta códigos de idioma. Podríamos no necesitar Whisper si Google Speech funciona bien en Japonés.

2. **Confusión de Idioma (Code Switching):**
    * Si Eira está en modo "Japonés" y tú le hablas en Español, Whisper (forzado a `ja`) intentará transcribir sonidos españoles como palabras japonesas sin sentido.
    * *Solución:* El usuario debe ser disciplinado. Si está en modo Japonés, debe hablar Japonés (o decir el comando de cambio en Japonés/Inglés muy claro).

3. **Caracteres Japoneses en Consola:**
    * Windows CMD a veces falla mostrando Kanji.
    * *Solución:* Asegurar que la consola use fuente compatible (MS Gothic, NSimSun) o encoding UTF-8 forzado (`chcp 65001`).

---
**RECOMENDACIÓN DE IMPLEMENTACIÓN:**
Mantener `SpeechRecognition` (Google) inicialmente, pasando el parámetro `language` dinámico, ya que es "Zero Cost" y mucho más ligero para la CPU que Whisper. Solo migrar a Whisper si la detección de Google falla en japonés.
