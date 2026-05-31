# PRD: Eira Productivity Suite (Notion-Lite)

## 1. Vision

Transform Eira from a simple AI chat interface into a centralized productivity hub. A "Notion-style" workspace that feels lightweight, transparent, and futuristic, integrated with Eira's neural link.

## 2. Target Modules

### 2.1 Notes Module

- **Requirement**: Create, edit, and delete text notes.
- **Style**: Clean workspace, Markdown support (lite), and "infinite" canvas feel.
- **Integration**: Eira can "read" these notes to gain context.

### 2.2 Calendar Module

- **Requirement**: View days of the month, add/view simple events/reminders.
- **Style**: Minimalist grid, transparent glass background.
- **Integration**: Notifications via Eira's brain panel.

### 2.3 Habit Tracker Module

- **Requirement**: Define daily habits, check them off, view weekly progress.
- **Style**: Progress bars, neon-glow indicators for streaks.
- **Integration**: Eira encourages the user based on streak status.

## 3. UI/UX Principles

- **Aesthetic**: Notion-lite (block-based layout) + Eira-Glass (transparency, liquid elements).
- **Navigation**: Sidebar or tabbed interface for switching between Chat, Notes, Calendar, and Habits.
- **Speed**: Instant switching with soft transitions.

## 4. Success Metrics

- Performance: Switching between modules in <200ms.
- Storage: All data saved locally via `tauri-plugin-fs`.
