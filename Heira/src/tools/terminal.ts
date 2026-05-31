import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export const runTerminalCommandTool = {
    type: "function" as const,
    function: {
        name: "run_terminal_command",
        description: "Ejecuta un comando en la consola (PowerShell/CMD). Útil para instalar paquetes, mover archivos, crear carpetas o correr scripts. Retorna el stdout/stderr.",
        parameters: {
            type: "object",
            properties: {
                command: {
                    type: "string",
                    description: "El comando a ejecutar. Por ejemplo: 'dir', 'npm install axios', 'mkdir test'"
                }
            },
            required: ["command"]
        }
    }
};

export async function runTerminalCommand({ command }: { command: string }): Promise<string> {
    try {
        const { stdout, stderr } = await execAsync(command, {
            // Damos un timeout por seguridad (30 segundos max para evitar colgar al bot perpétuamente)
            timeout: 30000
        });

        let output = "";
        if (stdout) output += `[STDOUT]\n${stdout}\n`;
        if (stderr) output += `[STDERR]\n${stderr}\n`;

        return output.trim() || "Comando ejecutado con éxito, sin salida en consola.";
    } catch (error: any) {
        return `Error ejecutando comando: ${error.message}\n${error.stdout ? `\n[STDOUT]: ${error.stdout}` : ""}`;
    }
}
