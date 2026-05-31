export const searchWebTool = {
    type: "function" as const,
    function: {
        name: "search_web",
        description: "Realiza una búsqueda básica en internet usando duckduckgo html para obtener fragmentos de información reciente.",
        parameters: {
            type: "object",
            properties: {
                query: {
                    type: "string",
                    description: "El término o pregunta a buscar en internet."
                }
            },
            required: ["query"]
        }
    }
};

export async function searchWeb({ query }: { query: string }): Promise<string> {
    try {
        const response = await fetch(`https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`, {
            headers: {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        });

        const html = await response.text();

        // Extracción rudimentaria de resultados para no requerir dependencias pesadas como cheerio
        const snipppets: string[] = [];
        const regex = /<a class="result__snippet[^>]*>(.*?)<\/a>/gi;
        let match;
        let count = 0;

        while ((match = regex.exec(html)) !== null && count < 5) {
            // Limpia tags HTML básicos de la respuesta
            let text = match[1].replace(/<b>/g, '').replace(/<\/b>/g, '').replace(/<[^>]*>?/gm, '');
            snipppets.push(`- ${text.trim()}`);
            count++;
        }

        if (snipppets.length === 0) {
            return "No se encontraron resultados claros o DuckDuckGo bloqueó la petición automatizada.";
        }

        return `Resultados de la búsqueda web para '${query}':\n${snipppets.join("\n")}`;
    } catch (error: any) {
        return `Error buscando en internet: ${error.message}`;
    }
}
