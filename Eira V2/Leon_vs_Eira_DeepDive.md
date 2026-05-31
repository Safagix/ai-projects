# Deep Dive: Leon AI vs. Eira Legacy
>
> **Análisis detallado de capacidades y arquitectura**

## 1. ¿Qué es Leon AI?

Leon es un asistente personal **open-source** diseñado para vivir en servidores (Node.js). A diferencia de Eira Legacy (que es un script monolítico en Python), Leon es una **plataforma modular**.

### Arquitectura de "Cerebro Servidor"

Leon funciona como un servidor web. Tú no "corres el script", tú "enciendes el servidor" y luego interactúas con él a través de:

- Aplicación Web (Dashboard)
- API (HTTP/WebSocket)
- Puente de Python (Python Bridge)

### Capacidades Nativas de Leon (Que Eira no tiene aún)

1. **NLU (Natural Language Understanding):**
    - Leon usa clasificadores NLP reales para entender "intenciones" (Intents).
    - Eira Legacy usa "búsqueda de palabras clave" (si "hora" in texto -> show_time). Leon entiende "Dime qué hora es", "Reloj", "¿Es tarde?" usando modelos de lenguaje entrenados.

2. **Sistema de Módulos (Packages):**
    - Tiene una "tienda" de habilidades. Puedes instalar módulos como:
        - `checker`: Revisa si webs están caídas.
        - `video-downloader`: Descarga videos de YouTube.
        - `translator`: Traducción real.
    - Todo esto ya está programado en su ecosistema.

3. **Sincronización Multi-Dispositivo:**
    - Como es un servidor, puedes hablarle desde tu PC, desde tu móvil (si abres puertos) o desde una web. Eira Legacy solo vive en tu ventana de Python.

4. **Loop Infinito Robusto:**
    - Node.js maneja eventos mejor que un `while True` de Python. No se "congela" si una tarea tarda mucho.

---

## 2. Comparativa: Eira Legacy vs. Leon AI

| Característica | Eira Legacy (Actual) | Leon AI (Meta) |
| :--- | :--- | :--- |
| **Núcleo** | Script Python (`while True`) | Servidor Node.js (Event-driven) |
| **Entendimiento** | LLM Directo (Lento/Caro) o Palabras Clave (Tonto) | NLU NLP.js (Rápido y Local) + LLM opcional |
| **Habilidades** | Fáciles de escribir (Python simple) | Estructuradas (Requieren JSON de configuración + código) |
| **Interfaz** | Ventana CV2 (Visión) + Consola | Web Dashboard + Voz |
| **Visión** | **NATIVA y AVANZADA (Códice)** | Inexistente (Ciega) |
| **Control PC** | **TOTAL (PyAutoGUI, Kernel)** | Limitado (Diseñado para servidores, no para controlar el mouse) |

---

## 3. El Plan Híbrido: "Eira V2"

No vamos a borrar Leon. Vamos a usar **lo mejor de ambos mundos**:

1. **Cuerpo y Ojos (Python):** Eira Legacy se queda con la Visión (Códice) y el Control del Mouse, porque Python es REY en esto.
2. **Cerebro Lógico (Leon/Node):** Usaremos Leon para procesar las órdenes complejas y manejar la lógica de "Asistente".
3. **Puente:** Eira (Python) le mandará texto a Leon (Node) vía API, Leon decidirá qué hacer, y si necesita mover el mouse, le responderá a Eira "Mueve el mouse".

### ¿Por qué instalar Node.js?

Para encender el cerebro de Leon. Node.js es el motor que permite ejecutar JavaScript fuera del navegador, necesario para el núcleo de Leon.
