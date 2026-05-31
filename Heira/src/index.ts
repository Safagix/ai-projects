import { bot } from "./bot/telegram.js";
import { ENV } from "./config.js";
import { db } from "./db/index.js";

async function main() {
    console.log("=========================================");
    console.log("🧠 Iniciando Heira - Agente de IA Local");
    console.log("=========================================");
    console.log(`🛡️  Lista Blanca Activa: ${ENV.TELEGRAM_ALLOWED_USER_IDS.join(", ")}`);
    console.log(`💾 Base de Datos lista: ${ENV.DB_PATH}`);

    // Configurar cerrado agraciado (Graceful Shutdown)
    process.once("SIGINT", () => {
        console.log("Apagando Heira...");
        bot.stop();
        db.close();
    });
    process.once("SIGTERM", () => {
        console.log("Apagando Heira...");
        bot.stop();
        db.close();
    });

    console.log("📡 Conectando con Telegram...");
    await bot.api.deleteWebhook({ drop_pending_updates: true });

    await bot.start({
        onStart: (botInfo) => {
            console.log(`✅ Heira está viva y escuchando comandos en Telegram como @${botInfo.username}`);
        }
    });
}

main().catch(err => {
    console.error("❌ Error Crítico en el inicio:", err);
    process.exit(1);
});
