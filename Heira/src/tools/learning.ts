import { saveLearning } from "../learning.js";

export const saveLearningTool = {
    type: "function" as const,
    function: {
        name: "save_learning",
        description: "Guarda un aprendizaje reutilizable cuando descubres una forma efectiva de completar una tarea.",
        parameters: {
            type: "object",
            properties: {
                taskPattern: {
                    type: "string",
                    description: "Patron breve de la tarea resuelta. Ejemplo: abrir YouTube Music local."
                },
                procedure: {
                    type: "string",
                    description: "Procedimiento breve y reutilizable que funciono."
                },
                tags: {
                    type: "array",
                    items: { type: "string" },
                    description: "Etiquetas cortas para recuperar este aprendizaje despues."
                }
            },
            required: ["taskPattern", "procedure"]
        }
    }
};

export async function saveLearningToolHandler(
    { taskPattern, procedure, tags }: { taskPattern: string; procedure: string; tags?: string[] }
): Promise<string> {
    const learning = saveLearning(taskPattern, procedure, tags || []);
    return `Aprendizaje guardado con ID ${learning.id}.`;
}
