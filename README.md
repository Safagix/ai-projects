# AI Projects

This repository is a public-safe map of Digital Lab's AI experiments: local assistants, memory systems, retrieval prototypes, agent interfaces, learning tools, and small automation engines.

The work here is not a single product. It is a laboratory notebook written in code. Each folder captures a different attempt to answer the same larger question:

> How can AI become useful on a real machine, with real memory, real tools, and a personality that feels like it belongs to the workspace?

## What This Repository Explores

- local-first AI assistants
- personal memory and context systems
- Markdown and document-based RAG
- Telegram assistant workflows
- voice, avatar, and chat interfaces
- AI learning tools
- screen/pointer automation
- human-like typing experiments
- desktop app prototypes
- agent tool routing

The repository is intentionally broad. Some projects are polished enough to run as prototypes. Others are research fragments, migration experiments, or architectural sketches.

## Project Map

### `Eira`

The original Eira assistant work: personality design, memory notes, development logs, and early assistant architecture.

Eira is treated as more than a chatbot. It is a character system, a memory surface, and a local companion interface for Digital Lab.

### `Eira V2`

Second-generation experiments around Eira, including legacy Python assistant code and a Leon-based assistant exploration.

This folder shows the process of comparing assistant architectures, voice systems, skills, and local runtime strategies.

### `Eira_App`

A desktop-style Eira application prototype. It combines a visual interface, module-based tools, notes, habits, calendar concepts, news modules, and Tauri app structure.

In the public export, API keys were removed and replaced with environment-variable based reads.

### `Eira_Chat`

Chat and avatar interface work for Eira. This includes Python UI experiments, visual styling, state reporting, and a Tauri/Vite interface direction.

### `Eira_Nexos_Client`

A client-oriented variant of the Eira chat interface, structured around the same assistant and avatar ideas.

### `Eira_Nexus`

Nexus-style assistant architecture experiments: identity, adapters, memory modules, and bridge concepts for connecting Eira to other systems.

### `EiraLearn`

A learning assistant concept focused on study workflows, cognitive coaching, and AI-supported education interfaces.

### `Heira`

A local-first Telegram assistant prototype with tool routing, app control concepts, local model support, and a memory database design.

The private runtime database and `.env` files are not included in this public export.

### `local-rag-md`

A local Markdown RAG system. It explores document ingestion, SQLite/FTS retrieval, Ollama-oriented local models, a web UI, routing logic, and practical retrieval over personal notes.

The public version includes source code and configuration examples, not private indexes, embeddings, or document databases.

### `human-typer`

A research project for human-like typing behavior: timing distributions, typo modeling, profile training, and controlled text output.

### `magic-pointer-mcp`

An MCP-style experiment for screen-aware pointer control. It explores how an assistant could inspect a screen, reason about targets, and perform guided or automatic pointer actions.

## Design Philosophy

These projects are built around a practical idea: AI should not stay trapped in a chat box.

The strongest direction in this repo is AI as an operating layer:

- it remembers useful context
- it reads local knowledge
- it routes actions to tools
- it talks through familiar interfaces
- it works with the user's real environment
- it can become visual, vocal, and interactive

That direction is messy by nature. The repository keeps that mess visible because the process matters: failed builds, alternate architectures, and unfinished prototypes all show how the system evolved.

## Public Export

This is a cleaned source-level export, not a full machine backup.

Before publishing, the following were excluded or sanitized:

- `.env` files and secrets
- hardcoded API keys
- local databases and memory stores
- RAG indexes and embeddings
- logs and crash dumps
- virtual environments
- dependency folders
- build outputs
- packaged binaries
- generated voice files
- machine-specific local paths

See `SECURITY_PUBLISH_NOTES.md` for the publishing audit notes.
