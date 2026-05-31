export const getCurrentTimeTool = {
    type: "function" as const,
    function: {
        name: "get_current_time",
        description: "Obtiene la hora y fecha actual del sistema local donde se ejecuta Heira.",
        parameters: {
            type: "object",
            properties: {},
            required: []
        }
    }
};

export async function getCurrentTime(_args: any): Promise<string> {
    const formatter = new Intl.DateTimeFormat('es-AR', {
        dateStyle: 'full',
        timeStyle: 'long',
    });
    return formatter.format(new Date());
}
