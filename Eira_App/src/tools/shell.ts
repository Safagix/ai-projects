import { Command } from '@tauri-apps/plugin-shell';

export const runShell = async (command: string): Promise<string> => {
    try {
        console.log(`[Shell] Executing: ${command}`);
        // We use powershell -Command to run arbitrary commands
        const child = await Command.create('powershell', ['-Command', command]);
        const output = await child.execute();

        if (output.code !== 0) {
            return `Exit Code: ${output.code}\nStderr: ${output.stderr}`;
        }
        return output.stdout;
    } catch (error: any) {
        return `Error executing command: ${error.message}`;
    }
};
