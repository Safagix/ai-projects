import fs from "fs";

const CANDIDATE_PATHS = {
    autohotkey: [
        "C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe",
        "C:\\Program Files\\AutoHotkey\\AutoHotkey64.exe",
    ],
    everything: [
        "C:\\Program Files\\Everything\\Everything.exe",
        "C:\\Program Files (x86)\\Everything\\Everything.exe",
    ],
    es: [
        "C:\\Users\\safag\\AppData\\Local\\Microsoft\\WinGet\\Links\\es.exe",
        "C:\\Program Files\\Everything\\es.exe",
        "C:\\Program Files (x86)\\Everything\\es.exe",
    ],
    powertoys: [
        "C:\\Program Files\\PowerToys\\PowerToys.exe",
        "C:\\Users\\safag\\AppData\\Local\\PowerToys\\PowerToys.exe",
    ],
} as const;

export type SystemToolName = keyof typeof CANDIDATE_PATHS;

export function resolveSystemTool(name: SystemToolName): string | null {
    for (const candidate of CANDIDATE_PATHS[name]) {
        if (fs.existsSync(candidate)) {
            return candidate;
        }
    }

    return null;
}

export function describeInstalledSystemTools(): string {
    return (Object.keys(CANDIDATE_PATHS) as SystemToolName[])
        .map((name) => `${name}: ${resolveSystemTool(name) || "no encontrado"}`)
        .join("\n");
}
