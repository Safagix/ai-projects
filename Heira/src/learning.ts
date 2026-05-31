import fs from "fs";
import path from "path";

export interface LearnedSkill {
    id: string;
    createdAt: string;
    updatedAt: string;
    taskPattern: string;
    procedure: string;
    tags: string[];
}

const LEARNING_PATH = path.join(process.cwd(), "heira_learnings.json");

function readLearnings(): LearnedSkill[] {
    if (!fs.existsSync(LEARNING_PATH)) {
        return [];
    }

    try {
        const raw = fs.readFileSync(LEARNING_PATH, "utf-8");
        const parsed = JSON.parse(raw) as LearnedSkill[];
        return Array.isArray(parsed) ? parsed : [];
    } catch {
        return [];
    }
}

function writeLearnings(learnings: LearnedSkill[]) {
    fs.writeFileSync(LEARNING_PATH, JSON.stringify(learnings, null, 2), "utf-8");
}

function tokenize(text: string): string[] {
    return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9\s]/g, " ")
        .split(/\s+/)
        .filter(Boolean);
}

export function getRelevantLearnings(task: string, limit: number = 5): LearnedSkill[] {
    const learnings = readLearnings();
    const queryTokens = new Set(tokenize(task));

    return learnings
        .map((learning) => {
            const tokens = new Set([
                ...tokenize(learning.taskPattern),
                ...learning.tags.flatMap(tokenize),
                ...tokenize(learning.procedure)
            ]);

            let score = 0;
            for (const token of queryTokens) {
                if (tokens.has(token)) {
                    score++;
                }
            }

            return { learning, score };
        })
        .filter((entry) => entry.score > 0)
        .sort((a, b) => b.score - a.score || b.learning.updatedAt.localeCompare(a.learning.updatedAt))
        .slice(0, limit)
        .map((entry) => entry.learning);
}

export function saveLearning(taskPattern: string, procedure: string, tags: string[] = []): LearnedSkill {
    const learnings = readLearnings();
    const now = new Date().toISOString();

    const normalizedTaskPattern = taskPattern.trim();
    const existing = learnings.find(
        (item) => item.taskPattern.toLowerCase() === normalizedTaskPattern.toLowerCase()
    );

    if (existing) {
        existing.updatedAt = now;
        existing.procedure = procedure.trim();
        existing.tags = Array.from(new Set(tags.map((tag) => tag.trim()).filter(Boolean)));
        writeLearnings(learnings);
        return existing;
    }

    const learning: LearnedSkill = {
        id: `skill_${Date.now()}`,
        createdAt: now,
        updatedAt: now,
        taskPattern: normalizedTaskPattern,
        procedure: procedure.trim(),
        tags: Array.from(new Set(tags.map((tag) => tag.trim()).filter(Boolean))),
    };

    learnings.unshift(learning);
    writeLearnings(learnings);
    return learning;
}

export function formatLearningsForPrompt(task: string): string {
    const relevant = getRelevantLearnings(task);

    if (relevant.length === 0) {
        return "No hay aprendizajes previos relevantes para esta tarea.";
    }

    return [
        "Aprendizajes previos relevantes:",
        ...relevant.map((item, index) =>
            `${index + 1}. Patron: ${item.taskPattern}\nProcedimiento: ${item.procedure}\nTags: ${item.tags.join(", ")}`
        )
    ].join("\n");
}
