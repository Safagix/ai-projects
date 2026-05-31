# Backend Document: Data Schemas

## 1. Local Persistence (JSON)

### `notes.json`

```json
[
  {
    "id": "uuid",
    "title": "Project Starlight",
    "content": "Building the future of AI...",
    "updated_at": "ISO-TIMESTAMP"
  }
]
```

### `habits.json`

```json
[
  {
    "id": "habit-1",
    "name": "Drink Water",
    "streak": 5,
    "logs": {
      "2026-01-30": true,
      "2026-01-31": false
    }
  }
]
```

## 2. File Operations

Using `tauri-plugin-fs` commands:

- `readTextFile()` for loading modules.
- `writeTextFile()` for auto-save (debounce 1000ms).
- `mkdir()` for directory integrity.
