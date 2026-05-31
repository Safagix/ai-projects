import { config } from "dotenv";

config();

function getEnvVar(name: string, required: boolean = true): string {
    const value = process.env[name];
    if (required && !value) {
        throw new Error(`Environment variable ${name} is missing.`);
    }
    return value || "";
}

export const ENV = {
    TELEGRAM_BOT_TOKEN: getEnvVar("TELEGRAM_BOT_TOKEN"),
    TELEGRAM_ALLOWED_USER_IDS: getEnvVar("TELEGRAM_ALLOWED_USER_IDS")
        .split(",")
        .map(id => id.trim())
        .filter(Boolean),
    GROQ_API_KEY: getEnvVar("GROQ_API_KEY"),
    DB_PATH: getEnvVar("DB_PATH", false) || "./memory.db",
    OLLAMA_BASE_URL: getEnvVar("OLLAMA_BASE_URL", false) || "http://127.0.0.1:11434",
    LOCAL_LLM_MODEL: getEnvVar("LOCAL_LLM_MODEL", false) || "heira-local",
    PRIMARY_LLM: getEnvVar("PRIMARY_LLM", false) || "auto",
};

if (ENV.TELEGRAM_ALLOWED_USER_IDS.length === 0) {
    throw new Error("TELEGRAM_ALLOWED_USER_IDS must contain at least one valid User ID.");
}
