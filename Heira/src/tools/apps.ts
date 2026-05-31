import fs from "fs";
import { execFile } from "child_process";
import { promisify } from "util";
import { describeRegisteredApps, getRegisteredApp } from "../apps.js";

const execFileAsync = promisify(execFile);

function toPowerShellLiteral(value: string): string {
    return `'${value.replace(/'/g, "''")}'`;
}

export const listRegisteredAppsTool = {
    type: "function" as const,
    function: {
        name: "list_registered_apps",
        description: "Lista las apps y accesos locales registrados que Heira puede abrir directamente.",
        parameters: {
            type: "object",
            properties: {},
            required: []
        }
    }
};

export async function listRegisteredApps(_args: any): Promise<string> {
    return `Apps registradas disponibles:\n${describeRegisteredApps()}`;
}

export const launchRegisteredAppTool = {
    type: "function" as const,
    function: {
        name: "launch_registered_app",
        description: "Abre una app, acceso directo, carpeta o URL registrada por su ID. Usa list_registered_apps si no conoces los IDs.",
        parameters: {
            type: "object",
            properties: {
                appId: {
                    type: "string",
                    description: "ID de la app registrada. Ejemplos: antigravity, youtube_music, digital_lab."
                }
            },
            required: ["appId"]
        }
    }
};

export async function launchRegisteredApp({ appId }: { appId: string }): Promise<string> {
    const app = getRegisteredApp(appId);

    if (!app) {
        return `No existe una app registrada con ID '${appId}'. Usa list_registered_apps para ver las disponibles.`;
    }

    if (app.type === "path" && !fs.existsSync(app.target)) {
        return `La ruta registrada para '${appId}' no existe: ${app.target}`;
    }

    try {
        await execFileAsync("powershell.exe", [
            "-NoProfile",
            "-Command",
            `Start-Process -FilePath ${toPowerShellLiteral(app.target)}`
        ]);

        return `Abierto '${appId}' correctamente.`;
    } catch (error: any) {
        return `No se pudo abrir '${appId}': ${error.message}`;
    }
}

export const openWebSearchTool = {
    type: "function" as const,
    function: {
        name: "open_web_search",
        description: "Abre una busqueda web en el navegador predeterminado del equipo.",
        parameters: {
            type: "object",
            properties: {
                query: {
                    type: "string",
                    description: "Texto a buscar en internet."
                }
            },
            required: ["query"]
        }
    }
};

export async function openWebSearch({ query }: { query: string }): Promise<string> {
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;

    try {
        await execFileAsync("powershell.exe", [
            "-NoProfile",
            "-Command",
            `Start-Process -FilePath ${toPowerShellLiteral(searchUrl)}`
        ]);

        return `Busqueda abierta en el navegador para: ${query}`;
    } catch (error: any) {
        return `No se pudo abrir la busqueda web: ${error.message}`;
    }
}
