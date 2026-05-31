import { ENV } from "../config.js";

type Message = {
    role: "system" | "user" | "assistant";
    content: string;
};

const OLLAMA_TIMEOUT_MS = 45000;

async function callOllama(messages: Message[], model?: string): Promise<string> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), OLLAMA_TIMEOUT_MS);

    const response = await fetch(`${ENV.OLLAMA_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        signal: controller.signal,
        body: JSON.stringify({
            model: model || ENV.LOCAL_LLM_MODEL,
            stream: false,
            messages,
            keep_alive: "5m",
            options: {
                num_ctx: 2048,
                num_predict: 256,
                temperature: 0.1
            }
        })
    }).finally(() => clearTimeout(timeout));

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Ollama devolvió ${response.status}: ${text}`);
    }

    const data = await response.json() as any;
    const content = data?.message?.content?.trim();

    if (!content) {
        throw new Error("El modelo local no devolvió contenido.");
    }

    return content;
}

export async function chatLocalModel(messages: Message[], model?: string): Promise<string> {
    return callOllama(messages, model);
}

export const askLocalModelTool = {
    type: "function" as const,
    function: {
        name: "ask_local_model",
        description: "Consulta el modelo local de Ollama para tareas ligeras y privadas como clasificar, resumir, reformular, extraer datos o proponer pasos cortos.",
        parameters: {
            type: "object",
            properties: {
                prompt: {
                    type: "string",
                    description: "Solicitud concreta para el modelo local."
                },
                system: {
                    type: "string",
                    description: "Instrucción de sistema opcional para guiar el comportamiento."
                },
                model: {
                    type: "string",
                    description: "Modelo local opcional. Si se omite, usa el configurado por defecto."
                }
            },
            required: ["prompt"]
        }
    }
};

export async function askLocalModel(
    { prompt, system, model }: { prompt: string; system?: string; model?: string }
): Promise<string> {
    const messages: Message[] = [];

    if (system?.trim()) {
        messages.push({ role: "system", content: system.trim() });
    }

    messages.push({ role: "user", content: prompt.trim() });

    try {
        return await callOllama(messages, model);
    } catch (error: any) {
        if (error?.name === "AbortError") {
            return "Error consultando el modelo local: tiempo de espera agotado.";
        }
        return `Error consultando el modelo local: ${error.message}`;
    }
}

export const localModelStatusTool = {
    type: "function" as const,
    function: {
        name: "local_model_status",
        description: "Verifica la conectividad del backend local de Ollama y reporta el modelo por defecto configurado.",
        parameters: {
            type: "object",
            properties: {},
            required: []
        }
    }
};

export async function localModelStatus(_args: any): Promise<string> {
    try {
        const response = await fetch(`${ENV.OLLAMA_BASE_URL}/api/tags`);
        if (!response.ok) {
            return `Ollama no respondió correctamente. HTTP ${response.status}.`;
        }

        const data = await response.json() as any;
        const names = Array.isArray(data?.models)
            ? data.models.map((model: any) => model.name).join(", ")
            : "";

        return `Ollama activo. Modelo local por defecto: ${ENV.LOCAL_LLM_MODEL}. Modelos disponibles: ${names || "sin datos"}`;
    } catch (error: any) {
        return `No se pudo contactar Ollama: ${error.message}`;
    }
}
