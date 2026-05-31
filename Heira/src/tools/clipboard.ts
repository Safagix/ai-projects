import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export const readClipboardTool = {
    type: "function" as const,
    function: {
        name: "read_clipboard",
        description: "Obtiene el texto que el usuario copió recientemente en su portapapeles de Windows.",
        parameters: {
            type: "object",
            properties: {},
            required: []
        }
    }
};

export async function readClipboard(_args: any): Promise<string> {
    try {
        // Usa powershell para obtener el portapapeles nativamente en Windows
        const { stdout } = await execAsync("powershell -command Get-Clipboard");
        const content = stdout.trim();

        if (!content) {
            return "El portapapeles está vacío o no contenía texto.";
        }
        return `[Contenido del Portapapeles]:\n${content}`;
    } catch (error: any) {
        return `No se pudo leer el portapapeles: ${error.message}`;
    }
}
