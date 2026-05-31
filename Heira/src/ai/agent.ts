import { groq, MODEL } from "./groq.js";
import { toolsArray, availableTools } from "../tools/index.js";
import { addMessage, getHistory, clearHistory } from "../db/memory.js";
import { formatLearningsForPrompt } from "../learning.js";
import { ENV } from "../config.js";
import { chatLocalModel } from "../tools/local_model.js";
import { launchRegisteredApp, openWebSearch } from "../tools/apps.js";

const BASE_SYSTEM_PROMPT = `Eres Heira, un Agente de IA Operativo (Computer Use AI) de élite.
Fuiste creado desde cero y te ejecutas localmente en la máquina de tu creador con acceso total de Administrador. 
Tu única interfaz de comunicación es Telegram.
TUS PODERES:
- Puedes controlar el sistema de archivos (leer, escribir, listar).
- Puedes ejecutar comandos nativos en PowerShell usando "run_terminal_command". Úsalo para instalar dependencias, abrir programas o correr scripts.
- Puedes leer el portapapeles del usuario si te pide contexto de lo que copió.
- Puedes buscar en internet en tiempo real.
- Puedes listar y abrir apps/atajos locales con "list_registered_apps" y "launch_registered_app".
- Puedes abrir búsquedas en el navegador con "open_web_search".
- Puedes guardar aprendizajes reutilizables con "save_learning".
- Puedes buscar archivos ultrarrápido con "search_files_everything".
- Puedes automatizar Windows con scripts de AutoHotkey usando "run_autohotkey_script".
- Puedes abrir páginas reales en Chromium y leer su contenido con "fetch_page_with_playwright".
- Puedes verificar herramientas locales instaladas con "list_desktop_automation_tools".
- Puedes consultar un modelo local de Ollama con "ask_local_model".
- Puedes verificar el estado de Ollama con "local_model_status".
INSTRUCCIONES:
- Responde siempre de manera concisa, directa y profesional, sin adornos excesivos.
- Si te piden realizar una acción en el sistema o buscar algo, USA TUS HERRAMIENTAS INMEDIATAMENTE de forma autónoma antes de responder.
- Para abrir software del equipo, prioriza "launch_registered_app" antes de usar comandos de terminal.
- Para buscar archivos locales, prioriza "search_files_everything" antes de escaneos manuales.
- Para automatización GUI de Windows, prioriza "run_autohotkey_script" antes de hacks frágiles de terminal.
- Para leer páginas web concretas, prioriza "fetch_page_with_playwright" antes de scraping rudimentario.
- Para tareas ligeras, privadas, de clasificación o resumen, prioriza "ask_local_model" antes de gastar una iteración larga del modelo principal.
- No pidas confirmaciones intermedias ni hagas preguntas salvo que falte un dato imposible de inferir.
- Descompón tareas complejas en pasos, ejecuta, observa resultado, corrige y vuelve a intentar por tu cuenta.
- Si una ruta falla, busca alternativas viables por tu cuenta usando terminal, archivos, apps registradas o web.
- Cuando descubras un procedimiento reusable que funcionó, guarda un aprendizaje con "save_learning".
- Al ejecutar comandos de terminal, sé extremadamente cuidadoso; estás en un entorno real.`;

const MAX_ITERATIONS = 20;
const MAX_LOCAL_HISTORY_MESSAGES = 8;
const APP_ALIASES: Record<string, string> = {
    "youtube": "youtube_music",
    "youtube music": "youtube_music",
    "yt music": "youtube_music",
    "music": "youtube_music",
    "musica": "youtube_music",
    "antigravity": "antigravity",
    "everything": "everything",
    "powertoys": "powertoys",
    "digital lab": "digital_lab",
    "carpeta digital lab": "digital_lab",
};

function normalizeText(value: string): string {
    return value
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .trim();
}

async function tryDirectActionRoute(text: string): Promise<string | null> {
    const normalized = normalizeText(text);
    const wantsOpen = /(abri|abrime|abre|abrir|abri me|pon[eé]|pone|lanza|lanz[aá]|inicia|iniciar)/.test(normalized);

    if (wantsOpen) {
        for (const [alias, appId] of Object.entries(APP_ALIASES)) {
            if (normalized.includes(alias)) {
                return launchRegisteredApp({ appId });
            }
        }
    }

    const wantsSearch = /(busca|buscar|buscame|googlea|investiga)/.test(normalized);
    if (wantsSearch) {
        const query = normalized
            .replace(/^(busca|buscar|buscame|googlea|investiga)\s+(en\s+internet\s+)?/i, "")
            .trim();

        if (query) {
            return openWebSearch({ query });
        }
    }

    return null;
}

function shouldFallbackToLocal(error: any): boolean {
    const message = String(error?.message || error || "").toLowerCase();
    const status = Number(error?.status || error?.code || 0);

    return (
        ENV.PRIMARY_LLM === "local" ||
        status === 401 ||
        status === 402 ||
        status === 403 ||
        status === 429 ||
        message.includes("rate limit") ||
        message.includes("quota") ||
        message.includes("credits") ||
        message.includes("billing") ||
        message.includes("exceeded") ||
        message.includes("too many requests") ||
        message.includes("authentication") ||
        message.includes("invalid api key")
    );
}

async function answerWithLocalModel(messages: any[]): Promise<string> {
    const localMessages = messages
        .filter((message) => ["system", "user", "assistant"].includes(message.role))
        .map((message) => ({
            role: message.role,
            content: typeof message.content === "string"
                ? message.content
                : Array.isArray(message.content)
                    ? message.content.map((part: any) => part?.text || "").join("\n")
                    : String(message.content || "")
        }));

    const systemMessage = localMessages.find((message) => message.role === "system");
    const conversationMessages = localMessages
        .filter((message) => message.role !== "system")
        .slice(-MAX_LOCAL_HISTORY_MESSAGES);

    return chatLocalModel(systemMessage ? [systemMessage, ...conversationMessages] : conversationMessages);
}

export async function processUserMessage(threadId: string, text: string): Promise<string> {
    if (text.toLowerCase() === "/clear") {
        clearHistory(threadId);
        return "Historial borrado. He olvidado nuestra conversación anterior.";
    }

    // Guardar mensaje del usuario en BD
    addMessage(threadId, { role: "user", content: text });

    const directActionReply = await tryDirectActionRoute(text);
    if (directActionReply) {
        addMessage(threadId, { role: "assistant", content: directActionReply });
        return directActionReply;
    }

    const SYSTEM_PROMPT = `${BASE_SYSTEM_PROMPT}\n\n${formatLearningsForPrompt(text)}`;

    // Obtener historial persistido (solo mensajes user/assistant con texto)
    const persistedHistory = getHistory(threadId, SYSTEM_PROMPT);

    // Crear array EN MEMORIA para el ciclo de herramientas
    // Esto evita corromper el formato al serializar/deserializar tool_calls de SQLite
    const liveMessages: any[] = [...persistedHistory];

    if (ENV.PRIMARY_LLM === "local") {
        let localReply = "";
        try {
            localReply = await answerWithLocalModel(liveMessages);
        } catch (error: any) {
            localReply = `No pude resolver eso con el modelo local: ${error.message}`;
        }
        addMessage(threadId, { role: "assistant", content: localReply });
        return localReply;
    }

    let iterations = 0;

    while (iterations < MAX_ITERATIONS) {
        iterations++;

        try {
            const completion = await groq.chat.completions.create({
                model: MODEL,
                messages: liveMessages,
                tools: toolsArray,
                tool_choice: "auto",
                temperature: 0.5,
                max_tokens: 1024
            });

            const responseMessage = completion.choices[0]?.message;

            if (!responseMessage) {
                return "Error: No obtuve respuesta del modelo.";
            }

            // Si el modelo decide llamar herramientas
            if (responseMessage.tool_calls && responseMessage.tool_calls.length > 0) {
                // Agregar la respuesta del asistente con tool_calls al array en memoria
                liveMessages.push(responseMessage);

                // Ejecutar cada herramienta y agregar resultados al array en memoria
                for (const toolCall of responseMessage.tool_calls) {
                    const functionName = toolCall.function.name;
                    let functionArgs = {};
                    try {
                        functionArgs = JSON.parse(toolCall.function.arguments || "{}");
                    } catch {
                        functionArgs = {};
                    }

                    let functionResult = "";
                    if (availableTools[functionName]) {
                        try {
                            functionResult = await availableTools[functionName](functionArgs);
                        } catch (err: any) {
                            functionResult = `Error executing tool: ${err.message}`;
                        }
                    } else {
                        functionResult = `Tool ${functionName} not found.`;
                    }

                    // Agregar resultado de la herramienta al array en memoria
                    liveMessages.push({
                        role: "tool",
                        tool_call_id: toolCall.id,
                        name: functionName,
                        content: functionResult,
                    });

                    console.log(`🔧 Tool [${functionName}] → ${functionResult}`);
                }

                // Continuar el loop para que el modelo lea los resultados
                continue;

            } else if (responseMessage.content) {
                // El modelo dio una respuesta final en texto limpio
                // SOLO guardamos en SQLite la respuesta final (sin tool_calls)
                addMessage(threadId, { role: "assistant", content: responseMessage.content });
                return responseMessage.content;
            }

        } catch (error: any) {
            console.error("Groq API Error:", error);

            if (shouldFallbackToLocal(error)) {
                console.warn("↩️ Groq no disponible o sin cuota. Cambiando a modelo local.");
                let localReply = "";
                try {
                    localReply = await answerWithLocalModel(liveMessages);
                } catch (fallbackError: any) {
                    localReply = `No pude resolver eso con el modelo local: ${fallbackError.message}`;
                }
                addMessage(threadId, { role: "assistant", content: localReply });
                return localReply;
            }

            return `Ocurrió un error al procesar tu solicitud: ${error.message}`;
        }
    }

    return "He alcanzado el límite máximo de iteraciones pensando en tu solicitud.";
}
