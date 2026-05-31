
import { BaseDirectory, readTextFile, writeTextFile, mkdir, exists } from '@tauri-apps/plugin-fs';

const DATA_DIR = "data";

// Type wrapper
interface StorageResult<T> {
    success: boolean;
    data?: T;
    error?: string;
}

// Ensure data directory exists
const ensureDataDir = async () => {
    try {
        const dirExists = await exists(DATA_DIR, { baseDir: BaseDirectory.AppLocalData });
        if (!dirExists) {
            await mkdir(DATA_DIR, { baseDir: BaseDirectory.AppLocalData, recursive: true });
        }
    } catch (e) {
        console.error("Error creating data dir", e);
    }
};

export const loadData = async <T>(filename: string, defaultValue: T): Promise<T> => {
    try {
        await ensureDataDir();
        const fileExists = await exists(`${DATA_DIR}/${filename}`, { baseDir: BaseDirectory.AppLocalData });
        if (!fileExists) {
            // Create with default if not exists
            await saveData(filename, defaultValue);
            return defaultValue;
        }

        const content = await readTextFile(`${DATA_DIR}/${filename}`, { baseDir: BaseDirectory.AppLocalData });
        return JSON.parse(content) as T;
    } catch (e) {
        console.error(`Error loading ${filename}`, e);
        return defaultValue;
    }
};

export const saveData = async <T>(filename: string, data: T): Promise<boolean> => {
    try {
        await ensureDataDir();
        const content = JSON.stringify(data, null, 2);
        await writeTextFile(`${DATA_DIR}/${filename}`, content, { baseDir: BaseDirectory.AppLocalData });
        return true;
    } catch (e) {
        console.error(`Error saving ${filename}`, e);
        return false;
    }
};
