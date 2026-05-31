import fs from "fs";
import path from "path";

export interface RegisteredApp {
    description: string;
    target: string;
    type?: "path" | "url";
}

type RegisteredAppsMap = Record<string, RegisteredApp>;

const PROJECT_ROOT = process.cwd();
const WORKSPACE_ROOT = path.resolve(PROJECT_ROOT, "..");
const APPDATA = process.env.APPDATA || "";
const START_MENU_PROGRAMS = APPDATA
    ? path.join(APPDATA, "Microsoft", "Windows", "Start Menu", "Programs")
    : "";
const APPS_CONFIG_PATH = path.join(PROJECT_ROOT, "heirabot.apps.json");

const DEFAULT_APPS: RegisteredAppsMap = {
    antigravity: {
        description: "Abre Antigravity desde el acceso directo del menu Inicio.",
        target: path.join(START_MENU_PROGRAMS, "Antigravity", "Antigravity.lnk"),
        type: "path",
    },
    youtube_music: {
        description: "Abre YouTube Music en el navegador predeterminado.",
        target: "https://music.youtube.com/",
        type: "url",
    },
    digital_lab: {
        description: "Abre la carpeta principal Digital Lab.",
        target: WORKSPACE_ROOT,
        type: "path",
    },
    heira_project: {
        description: "Abre la carpeta del proyecto Heira.",
        target: PROJECT_ROOT,
        type: "path",
    },
};

function normalizeApp(id: string, app: RegisteredApp): RegisteredApp {
    const type = app.type || (app.target.startsWith("http") ? "url" : "path");

    return {
        description: app.description || `App registrada: ${id}`,
        target: app.target,
        type,
    };
}

export function loadRegisteredApps(): RegisteredAppsMap {
    const registry: RegisteredAppsMap = { ...DEFAULT_APPS };

    if (!fs.existsSync(APPS_CONFIG_PATH)) {
        return registry;
    }

    try {
        const raw = fs.readFileSync(APPS_CONFIG_PATH, "utf-8");
        const parsed = JSON.parse(raw) as RegisteredAppsMap;

        for (const [id, app] of Object.entries(parsed)) {
            if (!app?.target) {
                continue;
            }
            registry[id] = normalizeApp(id, app);
        }
    } catch (error) {
        console.warn(`No se pudo cargar ${APPS_CONFIG_PATH}:`, error);
    }

    return registry;
}

export function getRegisteredApp(appId: string): RegisteredApp | null {
    const registry = loadRegisteredApps();
    return registry[appId] || null;
}

export function describeRegisteredApps(): string {
    const registry = loadRegisteredApps();

    return Object.entries(registry)
        .map(([id, app]) => `- ${id}: ${app.description} -> ${app.target}`)
        .join("\n");
}
