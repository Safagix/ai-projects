import { db } from "./index.js";

export interface Message {
    role: "system" | "user" | "assistant" | "tool";
    content: string;
    tool_call_id?: string;
    name?: string;
}

const MAX_HISTORY_MESSAGES = 50;

export function addMessage(threadId: string, msg: Message) {
    const stmt = db.prepare(`
        INSERT INTO messages (thread_id, role, content, tool_call_id, name)
        VALUES (?, ?, ?, ?, ?)
    `);

    stmt.run(
        threadId,
        msg.role,
        msg.content || "",
        msg.tool_call_id || null,
        msg.name || null
    );
}

export function getHistory(threadId: string, systemPrompt?: string): Message[] {
    // Solo recuperamos mensajes user y assistant (texto limpio)
    // Las tool_calls intermedias se manejan en memoria durante el agent loop
    const stmt = db.prepare(`
        SELECT role, content
        FROM messages 
        WHERE thread_id = ? AND role IN ('user', 'assistant')
        ORDER BY created_at DESC 
        LIMIT ?
    `);

    const rows = stmt.all(threadId, MAX_HISTORY_MESSAGES) as any[];

    // Reverse to chronological order
    const history = rows.reverse().map(row => ({
        role: row.role,
        content: row.content
    }));

    if (systemPrompt) {
        history.unshift({ role: "system", content: systemPrompt });
    }

    return history;
}

export function clearHistory(threadId: string) {
    const stmt = db.prepare(`DELETE FROM messages WHERE thread_id = ?`);
    stmt.run(threadId);
}
