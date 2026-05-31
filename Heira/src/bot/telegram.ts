import { Bot } from "grammy";
import { ENV } from "../config.js";
import { processUserMessage } from "../ai/agent.js";

export const bot = new Bot(ENV.TELEGRAM_BOT_TOKEN);
const BOT_STARTED_AT_UNIX = Math.floor(Date.now() / 1000);
const activeUsers = new Set<string>();

// Middleware de Seguridad Estricta: Whitelist
bot.use(async (ctx, next) => {
    const userId = ctx.from?.id.toString();
    if (!userId) return;

    if (!ENV.TELEGRAM_ALLOWED_USER_IDS.includes(userId)) {
        console.warn(`[SECURITY] Bloqueado intento de acceso no autorizado desde User ID: ${userId} (@${ctx.from?.username || "unknown"})`);
        return; // Ignora el mensaje silenciosamente
    }

    await next();
});

bot.command("start", async (ctx) => {
    await ctx.reply("Hola, soy Heira. Estoy lista y en línea. ¿En qué te puedo ayudar?");
});

async function runTextRequest(userId: string, text: string): Promise<string> {
    if (activeUsers.has(userId)) {
        return "Sigo procesando tu solicitud anterior. Espera unos segundos y vuelve a intentar si hace falta.";
    }

    activeUsers.add(userId);

    try {
        return await processUserMessage(userId, text);
    } finally {
        activeUsers.delete(userId);
    }
}

// Manejador Principal de Mensajes
bot.on("message:text", async (ctx) => {
    // Evita ejecutar mensajes viejos acumulados mientras el bot estaba apagado.
    if (ctx.message.date < BOT_STARTED_AT_UNIX) {
        console.log(`🧹 Ignorando mensaje pendiente previo al arranque: ${ctx.message.text}`);
        return;
    }

    const userId = ctx.from.id.toString();
    const text = ctx.message.text;

    // Enviar indicador visual de escritura en Telegram
    await ctx.replyWithChatAction("typing");

    try {
        const reply = await runTextRequest(userId, text);

        // Chunk long replies if necessary (Telegram limit is 4096)
        if (reply.length > 4000) {
            const chunks = reply.match(/.{1,4000}/g) || [];
            for (const chunk of chunks) {
                await ctx.reply(chunk);
            }
        } else {
            await ctx.reply(reply);
        }
    } catch (error: any) {
        console.error("Error al procesar mensaje en Telegram:", error);
        await ctx.reply(`⚠️ Ocurrió un error en mi procesamiento interno: ${error.message}`);
    }
});

bot.on(["message:voice", "message:audio"], async (ctx) => {
    if (ctx.message.date < BOT_STARTED_AT_UNIX) {
        return;
    }

    await ctx.reply("Todavía no proceso audios en esta versión. Envíame el mensaje en texto y te respondo.");
});

bot.on("message", async (ctx) => {
    if (ctx.message.date < BOT_STARTED_AT_UNIX) {
        return;
    }

    const hasText = "text" in ctx.message;
    const hasVoice = "voice" in ctx.message;
    const hasAudio = "audio" in ctx.message;

    if (!hasText && !hasVoice && !hasAudio) {
        await ctx.reply("Ahora mismo manejo texto. Si quieres una acción o consulta, envíamela escrita.");
    }
});
