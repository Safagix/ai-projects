import Database from "better-sqlite3";
import { ENV } from "../config.js";

const db = new Database(ENV.DB_PATH);

// Initialize schema
db.exec(`
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant', 'tool')),
        content TEXT NOT NULL,
        tool_call_id TEXT,
        name TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_thread_id ON messages(thread_id);
`);

export { db };
