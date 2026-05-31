# Eira – Quick Context Summary

## Purpose & Scope

- Local AI assistant (Emotional Intelligence Reactive Assistant) with voice, gesture, and holographic UI.
- Works on modest hardware (Ryzen 3 3200G) using free/open‑source models.

## Core Architecture

1. **Input Layer** – Speech (SpeechRecognition/Whisper) + Hand‑tracking (OpenCV + cvzone).
2. **Brain Layer** – LLM (Gemma 2B via Ollama or Gemini 1.5 Flash). Handles language routing, memory lookup, and response generation.
3. **Output Layer** – Edge‑TTS for speech, pyautogui for mouse/keyboard control, PyQt6 avatar for visual feedback.

## Key Components

- `main_eira_lab.py` – Main loop, gesture handling, state machine.
- `eira_brain.py` – Wrapper around LLM, language switching, memory integration.
- `eira_skills.py` – Skill executor (open programs, web search, system commands).
- `eira_avatar.py` – PyQt6 avatar with blinking and lip‑sync.
- `holographic_ui.py` – Transparent HUD with neon glow.
- `Memory/` – Persistent patterns (`Neural_Patterns.md`).

## Tech Stack

- **Languages:** Python 3.12
- **Frameworks/Libraries:** OpenCV, cvzone, pyautogui, SpeechRecognition, edge‑tts, PyQt6, Ollama, Google‑Generative‑AI.
- **Models:** Gemma 2B (local), Gemini 1.5 Flash (cloud), Whisper (optional STT).

## Current Development State

- Voice, vision, gesture, and basic command execution fully functional.
- Avatar skeleton ready; assets still pending.
- Multilingual support (ES/EN/JA) partially implemented – language switching logic present.
- Memory system works for static patterns; learning commands (`/learn`) functional.

## Limitations

- No full avatar graphics yet.
- Whisper on‑device adds latency; fallback to Google STT used.
- Limited error recovery; occasional race conditions in gesture handling.

## Next Steps

- Add avatar PNG assets and integrate lip‑sync.
- Finalize multilingual pipeline (dynamic language IDs for STT/TTS).
- Refactor memory manager for auto‑persistence.
- Write unit tests for brain, skills, and avatar.

---
*This summary should be regenerated whenever `Eira_Development_Log.md` changes to keep the context up‑to‑date.*
