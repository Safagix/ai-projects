# Eira System State Report - Phase 4 (Hybrid Convergence)

**Date**: 2026-01-18
**System Architecture**: Cognitive V4 (Tiered Memory + Web Hybrid)

---

## 1. Core Component Metadata

- **Brain (LLM)**: Ollama (`qwen2.5:3b`) - Optimized for Ryzen 3 3200G.
- **Frontend**: Python 3.12 / PyQt6 (Native Desktop App).
- **Voice (TTS)**: `edge-tts` (Microsoft Neural Voices).
- **Input (STT)**: `SpeechRecognition` (Google Web API).
- **Communication**: Asynchronous `requests` for Ollama; `asyncio` for UI/Voice.

---

## 2. Tiered Memory Model

Eira maintains information across four distinct layers to ensure continuity and efficiency:

1. **Tier 1: Working Memory (RAM)**:
    - Sliding window of the last 20 conversation turns.
    - Handled by `MemoryManager` in `eira_chat_brain.py`.

2. **Tier 2: Associative Memory (Local RAG)**:
    - **Source**: `%DIGITAL_LAB%\Eira's Library`.
    - **Mechanism**: **Inverted Index** (Dictionary of Keywords -> File Paths).
    - **Scalability**: High. Content is loaded lazily from disk on match.

3. **Tier 3: Episodic/Semantic Memory (Persistent)**:
    - **File**: `%DIGITAL_LAB%\Eira's Library\Core_Memory\User_Profile.md`.
    - **Structure**: Markdown sections for **## FACTS**, **## PREFERENCES**, **## CONSTRAINTS**.
    - **Dynamic Learning**: Eira parses specific tags (`[MEMORY_FACT]`, `[MEMORY_PREF]`, `[MEMORY_CONST]`) from her own outputs and appends them to the correct sections.

4. **Tier 4: External Memory (Web Hybrid)**:
    - **Engine**: `duckduckgo-search` (DDGS).
    - **Capability**: Real-time search and web scraping (BeautifulSoup4).
    - **Web Inbox**: `%DIGITAL_LAB%\Eira's Library\Web_Inbox`. Saves cleaned Markdown versions of requested URLs.

---

## 3. Cognitive Loop & Reasoning

Eira uses a **Dual-Pass Reasoning System**:

1. **Initial Thought**: Captures user intent and searches local library.
2. **Action Detection**: If `[SEARCH: "query"]` is detected in the first LLM output, the system pauses, executes the search, and **re-prompts** the model with the web results before generating the final answer.
3. **Chain-of-Thought**: Uses `<thought>` tags for internal planning (hidden from UI but logged).

---

## 4. File-System Layout

```bash
%DIGITAL_LAB%\
├── Eira_Chat\
│   ├── eira_chat_brain.py   # Core Intelligence & Memory Logic
│   ├── eira_chat_ui.py      # Main PyQt6 App + Integrated Avatar
│   ├── Start_Eira_Ava.bat   # Admin Launcher
│   └── (Assets/Scripts)     # Image processing (remove_bg, etc.)
└── Eira's Library\
    ├── Core_Memory\
    │   └── User_Profile.md  # Long-term semantic data
    ├── Web_Inbox\           # Downloaded web articles
    ├── Eira_V3_Manual.md    # User guide
    └── (Knowledge Base)     # System Prompts Catalog, Hubs, etc.
```

---

## 5. Persona & Constraints

- **Identity**: Sovereign Local AI / Cybernetic Companion.
- **Tone**: Professional, technical, concise, Cyberpunk/Elite aesthetic.
- **Language**: English/Spanish/Japanese (Auto-Detection).
- **Strict Constraint**: 100% Local code (Python/PyQt6), no Cloud APIs for reasoning, no Java allowed (per User Constraint).

---

## 6. Current Status: STABLE

- **Web module**: Online.
- **RAG Index**: Functional (118+ files).
- **Persistent Memory**: Active (Successfully recording preferences).
- **UI/Avatar**: Integrated in sidebar with expression cross-fading and lip-sync.
