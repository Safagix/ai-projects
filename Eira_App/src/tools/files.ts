import { readTextFile, writeTextFile, readDir, mkdir } from '@tauri-apps/plugin-fs';

export const readFile = async (path: string): Promise<string> => {
    try {
        return await readTextFile(path);
    } catch (e: any) {
        return `Error reading file: ${e.message}`;
    }
};

export const writeFile = async (path: string, content: string): Promise<string> => {
    try {
        await writeTextFile(path, content);
        return "File written successfully.";
    } catch (e: any) {
        return `Error writing file: ${e.message}`;
    }
};

export const listDir = async (path: string): Promise<string> => {
    try {
        const entries = await readDir(path);
        return entries.map((e: any) => `${e.name} (${e.isDirectory ? 'DIR' : 'FILE'})`).join('\n');
    } catch (e: any) {
        return `Error listing directory: ${e.message}`;
    }
};

export const makeDir = async (path: string): Promise<string> => {
    try {
        await mkdir(path, { recursive: true });
        return "Directory created.";
    } catch (e: any) {
        return `Error creating directory: ${e.message}`;
    }
};
