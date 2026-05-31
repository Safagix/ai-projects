# Technical Document: Eira Suite Architecture

## 1. Stack

- **Frontend**: React (Vite) + TypeScript.
- **Styling**: Vanilla CSS (Variables) + Glass Utilities.
- **Storage**: `tauri-plugin-fs` (Local JSON persistence).
- **Icons**: Lucide React or SVG custom icons.

## 2. State Management

- **View Controller**: `view` state in `App.tsx` (enum: 'chat' | 'notes' | 'calendar' | 'habits').
- **Data Persistence**:
  - `notes.json`: Store array of `{id, title, content, updated_at}`.
  - `calendar.json`: Store array of `{date, event_name, type}`.
  - `habits.json`: Store array of `{id, name, logs: {date: boolean}}`.

## 3. Core Components (Proposed)

- `AppContainer`: Main wrapper with sidebar.
- `ChatModule`: Existing chat logic.
- `NotesModule`: List view + Editor view.
- `CalendarModule`: Custom grid renderer.
- `HabitModule`: Streak grid (GitHub-style progress).

## 4. File System Structure

Data will be stored in `$APP_DATA/eira/`:

- `/notes/`
- `/memory/` (LLM context)
- `user_config.json`
