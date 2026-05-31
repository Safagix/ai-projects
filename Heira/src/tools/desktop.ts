import fs from "fs/promises";
import os from "os";
import path from "path";
import { execFile } from "child_process";
import { promisify } from "util";
import { describeInstalledSystemTools, resolveSystemTool } from "../system-tools.js";

const execFileAsync = promisify(execFile);

async function ensureEverythingRunning(): Promise<void> {
    const everythingPath = resolveSystemTool("everything");
    if (!everythingPath) {
        throw new Error("Everything.exe no está instalado.");
    }

    try {
        await execFileAsync("powershell.exe", [
            "-NoProfile",
            "-Command",
            `if (-not (Get-Process Everything -ErrorAction SilentlyContinue)) { Start-Process -FilePath '${everythingPath.replace(/'/g, "''")}' }`
        ]);
    } catch {
        await execFileAsync(everythingPath, []);
    }

    await new Promise((resolve) => setTimeout(resolve, 2000));
}

export const listDesktopAutomationToolsTool = {
    type: "function" as const,
    function: {
        name: "list_desktop_automation_tools",
        description: "Muestra qué herramientas locales de automatización de Windows están instaladas para Heira.",
        parameters: {
            type: "object",
            properties: {},
            required: []
        }
    }
};

export async function listDesktopAutomationTools(_args: any): Promise<string> {
    return `Herramientas locales detectadas:\n${describeInstalledSystemTools()}`;
}

export const searchFilesEverythingTool = {
    type: "function" as const,
    function: {
        name: "search_files_everything",
        description: "Busca archivos o carpetas locales de Windows usando Everything, mucho más rápido que un escaneo normal.",
        parameters: {
            type: "object",
            properties: {
                query: {
                    type: "string",
                    description: "Consulta de Everything. Ejemplos: *.exe youtube, ext:pdf factura, d:\\Digital Lab"
                },
                maxResults: {
                    type: "number",
                    description: "Máximo de resultados devueltos."
                }
            },
            required: ["query"]
        }
    }
};

export async function searchFilesEverything(
    { query, maxResults = 20 }: { query: string; maxResults?: number }
): Promise<string> {
    const esPath = resolveSystemTool("es");
    let stdout = "";
    let usedFallback = false;

    if (esPath) {
        for (let attempt = 0; attempt < 2; attempt++) {
            try {
                await ensureEverythingRunning();

                const result = await execFileAsync(esPath, [
                    "-n",
                    String(Math.max(1, Math.min(maxResults, 50))),
                    query
                ], {
                    timeout: 15000
                });

                stdout = result.stdout;
                break;
            } catch {
                if (attempt === 1) {
                    usedFallback = true;
                }
            }
        }
    } else {
        usedFallback = true;
    }

    if (usedFallback) {
        const escaped = query.replace(/'/g, "''");
        const psCommand = [
            "$roots = @('D:\\Digital Lab', $env:USERPROFILE, 'C:\\Program Files', 'C:\\Program Files (x86)') | Where-Object { $_ -and (Test-Path $_) }",
            `$pattern = '*${escaped}*'`,
            "$results = foreach ($root in $roots) { Get-ChildItem -Path $root -Recurse -ErrorAction SilentlyContinue -Force | Where-Object { $_.Name -like $pattern } | Select-Object -ExpandProperty FullName }",
            `$results | Select-Object -First ${Math.max(1, Math.min(maxResults, 50))}`
        ].join("; ");

        const fallbackResult = await execFileAsync("powershell.exe", [
            "-NoProfile",
            "-Command",
            psCommand
        ], {
            timeout: 30000
        });

        stdout = fallbackResult.stdout;
    }

    const lines = stdout
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean);

    if (lines.length === 0) {
        return usedFallback
            ? `No se encontraron resultados locales para: ${query}`
            : `No se encontraron resultados en Everything para: ${query}`;
    }

    const header = usedFallback
        ? `Resultados locales para '${query}' (fallback sin IPC de Everything):`
        : `Resultados de Everything para '${query}':`;

    return `${header}\n${lines.join("\n")}`;
}

export const runAutoHotkeyScriptTool = {
    type: "function" as const,
    function: {
        name: "run_autohotkey_script",
        description: "Ejecuta un script temporal de AutoHotkey v2 para automatizar ventanas, teclas, clicks o lanzar apps de Windows.",
        parameters: {
            type: "object",
            properties: {
                script: {
                    type: "string",
                    description: "Código AutoHotkey v2 completo. Debe incluir una secuencia corta y segura."
                },
                timeoutMs: {
                    type: "number",
                    description: "Tiempo máximo de espera antes de abortar."
                }
            },
            required: ["script"]
        }
    }
};

export async function runAutoHotkeyScript(
    { script, timeoutMs = 15000 }: { script: string; timeoutMs?: number }
): Promise<string> {
    const ahkPath = resolveSystemTool("autohotkey");
    if (!ahkPath) {
        return "AutoHotkey v2 no está instalado.";
    }

    const tempPath = path.join(os.tmpdir(), `heira_${Date.now()}.ahk`);
    const wrappedScript = `#Requires AutoHotkey v2.0\n${script}\n`;

    await fs.writeFile(tempPath, wrappedScript, "utf-8");

    try {
        const { stdout, stderr } = await execFileAsync(ahkPath, [tempPath], {
            timeout: Math.max(1000, timeoutMs)
        });

        const output = [stdout, stderr].filter(Boolean).join("\n").trim();
        return output || "Script AutoHotkey ejecutado correctamente.";
    } catch (error: any) {
        return `Error ejecutando AutoHotkey: ${error.message}`;
    } finally {
        await fs.unlink(tempPath).catch(() => undefined);
    }
}
