import * as fs from "fs/promises";
import * as path from "path";

export const readFileTool = {
    type: "function" as const,
    function: {
        name: "read_file",
        description: "Lee el contenido de texto de un archivo en el sistema.",
        parameters: {
            type: "object",
            properties: {
                filePath: {
                    type: "string",
                    description: "Ruta absoluta o relativa al archivo a leer."
                }
            },
            required: ["filePath"]
        }
    }
};

export async function readFile({ filePath }: { filePath: string }): Promise<string> {
    try {
        const resolvedPath = path.resolve(filePath);
        const data = await fs.readFile(resolvedPath, "utf-8");
        return data;
    } catch (error: any) {
        return `Error leyendo archivo: ${error.message}`;
    }
}

export const writeFileTool = {
    type: "function" as const,
    function: {
        name: "write_file",
        description: "Escribe o sobrescribe un archivo con nuevo contenido.",
        parameters: {
            type: "object",
            properties: {
                filePath: {
                    type: "string",
                    description: "Ruta absoluta o relativa donde guardar el archivo."
                },
                content: {
                    type: "string",
                    description: "El contenido a escribir en el archivo."
                }
            },
            required: ["filePath", "content"]
        }
    }
};

export async function writeFile({ filePath, content }: { filePath: string, content: string }): Promise<string> {
    try {
        const resolvedPath = path.resolve(filePath);
        // Asegurar que el directorio padre existe
        await fs.mkdir(path.dirname(resolvedPath), { recursive: true });
        await fs.writeFile(resolvedPath, content, "utf-8");
        return `Archivo guardado exitosamente en: ${resolvedPath}`;
    } catch (error: any) {
        return `Error escribiendo archivo: ${error.message}`;
    }
}

export const listDirectoryTool = {
    type: "function" as const,
    function: {
        name: "list_directory",
        description: "Lista los archivos y carpetas dentro de un directorio específico.",
        parameters: {
            type: "object",
            properties: {
                dirPath: {
                    type: "string",
                    description: "Ruta del directorio a listar (Usa '.' para el directorio actual)."
                }
            },
            required: ["dirPath"]
        }
    }
};

export async function listDirectory({ dirPath }: { dirPath: string }): Promise<string> {
    try {
        const resolvedPath = path.resolve(dirPath);
        const files = await fs.readdir(resolvedPath, { withFileTypes: true });
        const result = files.map(f => `${f.isDirectory() ? "[DIR]" : "[FILE]"} ${f.name}`);
        return `Contenido de ${resolvedPath}:\n${result.join("\n")}`;
    } catch (error: any) {
        return `Error listando directorio: ${error.message}`;
    }
}
