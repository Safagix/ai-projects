# Arquitectura Eira V2: Análisis Comparativo (Leon AI vs Eira Legacy)

**Fecha:** Diciembre 2024  
**Objetivo:** Análisis de migración hacia **Leon AI** como framework base para Eira V2.

---

## 1. Resumen Ejecutivo

**Eira Legacy (Actual):**
Sistema monolítico en Python centrado en un bucle infinito (`main_eira_lab.py`). Combina visión (cvzone), lógica (LLM), y voz (STT/TTS) en un solo proceso. Es fácil de modificar pero difícil de escalar y propenso a bloqueos (GIL de Python).

**Leon AI (Target):**
Framework modular cliente-servidor. El núcleo corre en **Node.js**, delegando tareas pesadas o skills específicas a **Python** mediante un "Bridge". Está diseñado para ser un asistente personal extensible, con sistema de NLU (Natural Language Understanding) propio.

---

## 2. Comparativa Técnica

| Característica | Eira Legacy (Project Starlight) | Leon AI (Eira V2 Candidate) |
| :--- | :--- | :--- |
| **Lenguaje Core** | Python 3.10+ (Puro) | Node.js (Core) + Python (Skills) |
| **Arquitectura** | Monolítica (Single Script Loop) | Micro-Kernels / Modular (TCP/WebSockets) |
| **Skill System** | Regex en `eira_brain.py` + `skills.py` | Carpeta `skills/` estructurada + Brain.js NLU |
| **NLU / Entendimiento** | LLM (Ollama/Gemini) directo | NLP.js / NLU interno (Intents & Entities) |
| **Voz (STT/TTS)** | `speech_recognition` + `edge_tts` | Módulos plug-in (Google, Watson, Offline, etc.) |
| **Interfaz (UI)** | OpenCV / Holographic UI | Web App (React/Vue) + CLI |
| **Gestión de Procesos** | Threading simple (propenso a race conditions) | Node.js Event Loop (Non-blocking I/O) |
| **Escalabilidad** | Baja (Código espagueti potencial) | Alta (Módulos aislados) |

---

## 3. Análisis de Componentes

### 3.1 Kernel & Loop Principal

* **Eira:** Depende de `while self.running:` en `main_eira_lab.py`. Si la visión falla, el cerebro muere. Si el cerebro piensa lento, la visión se congela (aunque se mitigó con hilos).
* **Leon:** Usa un servidor Node.js que escucha eventos. La visión (si se integra) sería un cliente o módulo separado que envía datos, no bloqueando el núcleo.

### 3.2 Sistema de Habilidades (Skills)

* **Eira:** "Si el usuario dice 'abrir spotify', ejecuta `os.system(...)`". Todo hardcodeado o dependiente del LLM alucinando comandos.
* **Leon:** Estructura rígida:

    ```
    skills/
      music/
        interaction.json  (Definición de intents)
        index.js          (Lógica Node)
        python/           (Lógica Python)
    ```

    Permite entrenar frases específicas ("Pon música", "Dale play") sin gastar tokens de LLM.

### 3.3 Bridges (Puentes)

* **Leon:** Tiene una carpeta `bridges/python`. Esto es **CRÍTICO** para nosotros. Permite que Leon (Node) ejecute scripts de Python.
  * *Ventaja:* Podemos reutilizar `hand_controller.py` y `eira_brain.py` como módulos de Python que Leon invoca.

---

## 4. Veredicto: ¿Migrar o No?

### **Ventajas de Migrar a Leon:**

1. **Estabilidad:** Node.js es superior para gestionar I/O (entras/salidas) asíncronas (WebSockets, HTTP, Voz).
2. **Estructura:** Te obliga a ordenar el código en Skills.
3. **UI Web:** Viene con una interfaz de chat web lista para usar (reemplazo potencial del HUD de OpenCV para debug).
4. **Offline-First:** Diseñado para privacidad.

### **Desafíos de Migrar:**

1. **Curva de Aprendizaje:** Requiere saber JavaScript/Node.js.
2. **Refactorización Total:** Eira Legacy no es "plug-and-play" en Leon. Hay que reescribir la lógica de visión como un "Input Module".
3. **LLM Integration:** Leon usa NLU clásico (NLP.js). Integrar Ollama para "charla libre" requiere crear un Skill de "Fallback" que capture lo que no sea un comando.

### **Recomendación Estratégica:**

**ADOPTAR ARQUITECTURA HÍBRIDA.**
No eliminar Python, sino usar Leon como el "Cerebro/Orquestador" y dejar a Python como el "Cuerpo/Sentidos".

* **Leon (Node.js):** Maneja el estado, la voz (STT/TTS), y la lógica de decisión.
* **Python (Legacy):** Se convierte en un servicio de Visión (Códice) y un Skill de LLM (Ollama).

---

## 5. Roadmap de Migración (Eira V2)

1. **Fase 1: Hello World en Leon**
    * Levantar servidor Leon.
    * Crear un Skill simple en Python ("Hola Eira").

2. **Fase 2: Integración de Cerebro (Ollama)**
    * Crear un Skill "Chat" en Leon que delegue a `eira_brain.py` (modificado) cuando no hay comandos específicos.

3. **Fase 3: Integración de Sentidos (Códice)**
    * Hacer que `main_Codice.py` envíe eventos a Leon vía WebSocket (p.ej. "Usuario Saludando").
    * Leon recibe evento -> Ejecuta acción TTS "Hola Ingeniero".

4. **Fase 4: Voz Neural**
    * Reemplazar TTS nativo de Leon con nuestro módulo `edge_tts` o `GPT-SoVITS` (vía Python Bridge).
