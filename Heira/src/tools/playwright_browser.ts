import { chromium } from "playwright";

export const fetchPageWithPlaywrightTool = {
    type: "function" as const,
    function: {
        name: "fetch_page_with_playwright",
        description: "Abre una página con Playwright/Chromium y devuelve título, URL final y texto visible resumido.",
        parameters: {
            type: "object",
            properties: {
                url: {
                    type: "string",
                    description: "URL completa a visitar."
                }
            },
            required: ["url"]
        }
    }
};

export async function fetchPageWithPlaywright({ url }: { url: string }): Promise<string> {
    const browser = await chromium.launch({ headless: true });

    try {
        const page = await browser.newPage();
        await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
        await page.waitForTimeout(1500);

        const title = await page.title();
        const finalUrl = page.url();
        const text = await page.locator("body").innerText().catch(() => "");
        const compact = text.replace(/\s+/g, " ").trim().slice(0, 2500);

        return [
            `Titulo: ${title || "(sin titulo)"}`,
            `URL final: ${finalUrl}`,
            `Contenido visible:`,
            compact || "(sin texto visible extraido)"
        ].join("\n");
    } finally {
        await browser.close();
    }
}
