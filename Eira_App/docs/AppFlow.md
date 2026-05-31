# App Flow: Eira Workspace

```mermaid
graph TD
    A[Launch App] --> B{View Controller}
    B -- Default --> C[Chat View]
    B -- Select Icons --> D[Notes View]
    B -- Select Icons --> E[Calendar View]
    B -- Select Icons --> F[Habit View]
    
    D --> D1[Search Notes]
    D --> D2[Edit/Save Note]
    
    E --> E1[View Month]
    E --> E2[Add Event]
    
    F --> F1[Tick Habit]
    F --> F2[View Weekly Heatmap]
```

## Navigation Logic

- **Sidebar persist**: The sidebar remains visible regardless of the current module.
- **State persistence**: If the user is writing a note and switches to chat, the note content stays in state until saved/closed.
