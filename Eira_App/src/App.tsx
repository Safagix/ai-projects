import { useState, useEffect, useRef } from "react";
import { getCurrentWindow } from "@tauri-apps/api/window";
import "./App.css";
import { LiquidButton } from "./components/ui/liquid-glass-button";
import { NotesModule } from "./components/modules/NotesModule";
import { HabitsModule } from "./components/modules/HabitsModule";
import { CalendarModule } from "./components/modules/CalendarModule";
import { NewsModule } from "./components/modules/NewsModule";

// API Keys are read from Vite env vars in public builds.
const OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY || "";
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY || "";

// Model Configuration
const MODELS = {
    gemini: {
        id: "gemini-2.0-flash",
        name: "Gemini Flash",
        desc: "Creative",
        icon: "✨",
        provider: "google"
    },
    local: {
        id: "gemma2:2b",
        name: "Gemma Local",
        desc: "Offline",
        icon: "💻",
        provider: "ollama"
    },
    glm: {
        id: "z-ai/glm-4.5-air:free",
        name: "GLM 4.5 Air",
        desc: "Thinking",
        icon: "🌪️",
        provider: "openrouter"
    },
    qwen: {
        id: "qwen/qwen3-coder:free",
        name: "Qwen 3 Coder",
        desc: "Coding & Logic",
        icon: "🪐",
        provider: "openrouter"
    },
    venice: {
        id: "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        name: "Venice Research",
        desc: "Uncensored",
        icon: "🐬",
        provider: "openrouter"
    }
};

type ModelKey = keyof typeof MODELS;

// Icons
const Icons = {
    Plus: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
        </svg>
    ),
    Mic: ({ muted }: { muted: boolean }) => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="23" /><line x1="8" y1="23" x2="16" y2="23" />
            {muted && <line x1="1" y1="1" x2="23" y2="23" stroke="#ff5f57" strokeWidth="2" />}
        </svg>
    ),
    Voice: ({ active }: { active: boolean }) => (
        <svg viewBox="0 0 24 24" fill={active ? "#4fc3f7" : "none"} stroke="currentColor" strokeWidth="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            {active && <><path d="M8.5 8.5c-.5-1-.5-2 0-3" stroke="#4fc3f7" /><path d="M15.5 8.5c.5-1 .5-2 0-3" stroke="#4fc3f7" /></>}
        </svg>
    ),
    Eye: ({ active }: { active: boolean }) => (
        <svg viewBox="0 0 24 24" fill="none" stroke={active ? "#28c840" : "currentColor"} strokeWidth="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
            <circle cx="12" cy="12" r="3" fill={active ? "#28c840" : "none"} />
        </svg>
    ),
    Send: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
    ),
    Brain: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 2a4 4 0 0 0-4 4c0 1.5.5 2.5 1.5 3.5S11 11 11 12v1" />
            <path d="M12 2a4 4 0 0 1 4 4c0 1.5-.5 2.5-1.5 3.5S13 11 13 12v1" />
            <path d="M8 6a4 4 0 0 0-4 4c0 2 1 3 2 4s2 2 2 4" />
            <path d="M16 6a4 4 0 0 1 4 4c0 2-1 3-2 4s-2 2-2 4" />
            <path d="M9 22h6" />
        </svg>
    ),
    ChevronRight: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 18 15 12 9 6" />
        </svg>
    ),
    Chat: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
    ),
    Notes: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
        </svg>
    ),
    Calendar: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
        </svg>
    ),
    Habits: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
    ),
    News: () => (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2" />
            <path d="M18 14h-8" />
            <path d="M15 18h-5" />
            <path d="M10 6h8v4h-8V6Z" />
        </svg>
    )
};

// --- Mock Modules ---


function App() {
    const [activeView, setActiveView] = useState<'chat' | 'notes' | 'calendar' | 'habits' | 'news'>('chat');
    const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([
        { role: "system", content: "Eira system online. Neural link established." }
    ]);
    const [input, setInput] = useState("");
    const [isThinking, setIsThinking] = useState(false);
    const [currentModel, setCurrentModel] = useState<ModelKey>("gemini"); // Default to Gemini which is reliable
    const [micMuted, setMicMuted] = useState(false);
    const [voiceActive, setVoiceActive] = useState(false);
    const [cameraActive, setCameraActive] = useState(false);
    const [brainPanelOpen, setBrainPanelOpen] = useState(false);
    const [latency, setLatency] = useState(0);
    const [errorMessage, setErrorMessage] = useState("");

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Window Controls
    const handleMinimize = async () => { try { await getCurrentWindow().minimize(); } catch (e) { console.error(e); } };
    const handleMaximize = async () => { try { await getCurrentWindow().toggleMaximize(); } catch (e) { console.error(e); } };
    const handleClose = async () => { try { await getCurrentWindow().close(); } catch (e) { console.error(e); } };

    useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

    // OpenRouter API call
    const callOpenRouter = async (modelId: string, messageList: Array<{ role: string; content: string }>): Promise<string> => {
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
                "Content-Type": "application/json",
                "HTTP-Referer": "https://eira.app",
                "X-Title": "Eira AI"
            },
            body: JSON.stringify({ model: modelId, messages: messageList })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData?.error?.message || `HTTP ${response.status}`);
        }

        const data = await response.json();
        return data.choices?.[0]?.message?.content || "No response.";
    };

    // Google Gemini API call (direct)
    const callGemini = async (prompt: string, history: Array<{ role: string; content: string }>): Promise<string> => {
        const { GoogleGenerativeAI } = await import("@google/generative-ai");
        const genAI = new GoogleGenerativeAI(GOOGLE_API_KEY);
        const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

        const chat = model.startChat({
            history: history.map(m => ({
                role: m.role === "assistant" ? "model" : "user",
                parts: [{ text: m.content }]
            }))
        });

        const result = await chat.sendMessage(prompt);
        return result.response.text();
    };

    // Ollama Local API call with Tool Calling
    const callOllama = async (modelId: string, prompt: string, history: Array<{ role: string; content: string }>): Promise<string> => {
        const { TOOLS, TOOL_DEFINITIONS } = await import("./tools");

        const toolsPrompt = `
You have access to the following tools to control the computer:
${JSON.stringify(TOOL_DEFINITIONS, null, 2)}

To use a tool, you MUST respond with ONLY a JSON object in this format:
{ "tool": "tool_name", "params": { "key": "value" } }

Example: { "tool": "run_shell", "params": { "command": "dir" } }
If no tool is needed, respond normally.
`;

        const messages = [
            { role: "system", content: "Eres Eira, una IA con control total del sistema. " + toolsPrompt },
            ...history.map(m => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.content })),
            { role: "user", content: prompt }
        ];

        try {
            const response = await fetch("http://localhost:11434/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ model: modelId, messages, stream: false })
            });

            if (!response.ok) throw new Error(`Ollama error: ${response.status}`);
            const data = await response.json();
            let content = data.message?.content || "";

            // Simple JSON parsing for tool calls
            const toolMatch = content.match(/\{[\s\S]*"tool"[\s\S]*\}/);
            if (toolMatch) {
                try {
                    const jsonStr = toolMatch[0];
                    const toolCall = JSON.parse(jsonStr);

                    if (toolCall.tool && TOOLS[toolCall.tool as keyof typeof TOOLS]) {
                        setMessages(prev => [...prev, { role: "assistant", content: `Executing tool: ${toolCall.tool}...` }]);

                        // Execute tool
                        let result = "";
                        const fn = TOOLS[toolCall.tool as keyof typeof TOOLS];

                        if (toolCall.tool === "write_file") {
                            // @ts-ignore
                            result = await fn(toolCall.params.path, toolCall.params.content);
                        } else {
                            // @ts-ignore
                            result = await fn(toolCall.params.command || toolCall.params.path || toolCall.params);
                        }

                        return `${content}\n\n[TOOL RESULT]:\n${result}`;
                    }
                } catch (e) {
                    console.error("Failed to parse tool call:", e);
                }
            }

            return content;
        } catch (error: any) {
            return `Error: ${error.message}`;
        }
    };

    // Main send function
    const sendMessage = async () => {
        if (!input.trim() || isThinking) return;
        const text = input.trim();
        setInput("");
        setErrorMessage("");
        setMessages(prev => [...prev, { role: "user", content: text }]);
        setIsThinking(true);

        const startTime = Date.now();
        const modelConfig = MODELS[currentModel];

        try {
            console.log(`[Eira] Sending to ${modelConfig.name} (${modelConfig.provider})...`);

            let response: string;

            if (modelConfig.provider === "google") {
                // Use Google Gemini directly
                const history = messages.filter(m => m.role !== "system").slice(-8).map(m => ({
                    role: m.role,
                    content: m.content
                }));
                response = await callGemini(text, history);
            } else if (modelConfig.provider === "ollama") {
                // Use local Ollama
                const history = messages.filter(m => m.role !== "system").slice(-8).map(m => ({
                    role: m.role,
                    content: m.content
                }));
                response = await callOllama(modelConfig.id, text, history);
            } else {
                // Use OpenRouter
                const systemPrompt = `Eres Eira. Identidad: ${modelConfig.name}. Modo: ${modelConfig.desc}. Tono: Profesional, futurista. Idioma: Español. Sin emojis. Concisa.`;
                const messageList = [
                    { role: "system", content: systemPrompt },
                    ...messages.filter(m => m.role !== "system").slice(-8).map(m => ({
                        role: m.role === "assistant" ? "assistant" : "user",
                        content: m.content
                    })),
                    { role: "user", content: text }
                ];
                response = await callOpenRouter(modelConfig.id, messageList);
            }

            setMessages(prev => [...prev, { role: "assistant", content: response }]);
            setLatency(Date.now() - startTime);

        } catch (error: any) {
            console.error("[Eira] Error:", error);
            const errMsg = error.message || "Unknown error";
            setErrorMessage(errMsg);
            setMessages(prev => [...prev, { role: "assistant", content: `Error: ${errMsg}` }]);
        } finally {
            setIsThinking(false);
        }
    };

    const handleFileUpload = () => { fileInputRef.current?.click(); };
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) console.log("Files selected:", files);
    };
    const toggleVoiceMode = () => { setVoiceActive(!voiceActive); };
    const toggleCamera = () => { setCameraActive(!cameraActive); };

    return (
        <div className="app-container">
            <div className="window-titlebar">
                <span className="window-title">EIRA // {MODELS[currentModel].name}</span>
                <div className="window-controls">
                    <button className="window-btn minimize" onClick={handleMinimize} />
                    <button className="window-btn maximize" onClick={handleMaximize} />
                    <button className="window-btn close" onClick={handleClose} />
                </div>
            </div>

            <div className="main-content">
                <nav className="nav-sidebar">
                    <button className={`nav-item ${activeView === 'chat' ? 'active' : ''}`} onClick={() => setActiveView('chat')} title="Neural Chat">
                        <Icons.Chat />
                    </button>
                    <button className={`nav-item ${activeView === 'notes' ? 'active' : ''}`} onClick={() => setActiveView('notes')} title="Notes">
                        <Icons.Notes />
                    </button>
                    <button className={`nav-item ${activeView === 'calendar' ? 'active' : ''}`} onClick={() => setActiveView('calendar')} title="Calendar">
                        <Icons.Calendar />
                    </button>
                    <button className={`nav-item ${activeView === 'habits' ? 'active' : ''}`} onClick={() => setActiveView('habits')} title="Habits">
                        <Icons.Habits />
                    </button>
                    <button className={`nav-item ${activeView === 'news' ? 'active' : ''}`} onClick={() => setActiveView('news')} title="Intel">
                        <Icons.News />
                    </button>
                </nav>

                {activeView === 'chat' && (
                    <div className="chat-area">
                        <div className="chat-header" data-tauri-drag-region>
                            <div className="model-selector">
                                {(Object.keys(MODELS) as ModelKey[]).map(key => (
                                    <button
                                        key={key}
                                        className={`model-btn ${currentModel === key ? "active" : ""}`}
                                        onClick={() => setCurrentModel(key)}
                                        title={`${MODELS[key].name} (${MODELS[key].provider})`}
                                    >
                                        {MODELS[key].icon}
                                    </button>
                                ))}
                            </div>
                            <button
                                className={`brain-toggle ${brainPanelOpen ? "open" : ""}`}
                                onClick={() => setBrainPanelOpen(!brainPanelOpen)}
                                title="Neural Status"
                            >
                                <Icons.Brain />
                            </button>
                        </div>

                        <div className="messages-area">
                            {messages.map((m, i) => (
                                <div key={i} className={`message ${m.role}`}>{m.content}</div>
                            ))}
                            {isThinking && <div className="message assistant thinking">Procesando...</div>}
                            <div ref={messagesEndRef} />
                        </div>

                        {errorMessage && <div className="error-banner">{errorMessage}</div>}

                        <div className="input-bar">
                            <input type="file" ref={fileInputRef} onChange={handleFileChange} hidden multiple />
                            <button className="input-icon plus" onClick={handleFileUpload} title="Subir archivos">
                                <Icons.Plus />
                            </button>
                            <input
                                type="text"
                                className="input-field"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                                placeholder="Pregunta lo que quieras..."
                                disabled={isThinking}
                            />
                            <button className={`input-icon mic ${micMuted ? "muted" : ""}`} onClick={() => setMicMuted(!micMuted)} title={micMuted ? "Activar micrófono" : "Silenciar"}>
                                <Icons.Mic muted={micMuted} />
                            </button>
                            <button className={`input-icon voice ${voiceActive ? "active" : ""}`} onClick={toggleVoiceMode} title="Modo conversación">
                                <Icons.Voice active={voiceActive} />
                            </button>
                            <button className={`input-icon eye ${cameraActive ? "active" : ""}`} onClick={toggleCamera} title="Activar cámara">
                                <Icons.Eye active={cameraActive} />
                            </button>
                            <LiquidButton variant="default" size="icon" onClick={sendMessage} disabled={isThinking} className="send-btn-liquid">
                                <Icons.Send />
                            </LiquidButton>
                        </div>
                    </div>
                )}

                {activeView === 'notes' && <NotesModule />}
                {activeView === 'calendar' && <CalendarModule />}
                {activeView === 'habits' && <HabitsModule />}
                {activeView === 'news' && <NewsModule />}

                <div className={`brain-panel ${brainPanelOpen ? "open" : ""}`}>
                    <div className="brain-panel-header">
                        <span>Neural Status</span>
                        <button onClick={() => setBrainPanelOpen(false)}><Icons.ChevronRight /></button>
                    </div>
                    <div className="brain-panel-content">
                        <div className="brain-stat"><span className="label">MODEL</span><span className="value">{MODELS[currentModel].name}</span></div>
                        <div className="brain-stat"><span className="label">PROVIDER</span><span className="value">{MODELS[currentModel].provider.toUpperCase()}</span></div>
                        <div className="brain-stat"><span className="label">LATENCY</span><span className="value">{latency}ms</span></div>
                        <div className="brain-stat"><span className="label">STATUS</span><span className={`value ${isThinking ? "thinking" : "idle"}`}>{isThinking ? "THINKING" : "IDLE"}</span></div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
