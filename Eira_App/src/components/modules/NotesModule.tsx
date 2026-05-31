import React, { useState } from 'react';

interface Note {
    id: string;
    title: string;
    content: string;
    timestamp: string;
}

export const NotesModule: React.FC = () => {
    const [notes, setNotes] = useState<Note[]>([
        { id: '1', title: 'Bienvenido a Eira Notes', content: 'Aquí puedes guardar tus ideas neurales...', timestamp: new Date().toLocaleDateString() }
    ]);
    const [activeId, setActiveId] = useState<string | null>('1');

    const activeNote = notes.find(n => n.id === activeId);

    const addNote = () => {
        const newNote: Note = {
            id: Date.now().toString(),
            title: 'Sin título',
            content: '',
            timestamp: new Date().toLocaleDateString()
        };
        setNotes([newNote, ...notes]);
        setActiveId(newNote.id);
    };

    const updateNote = (field: 'title' | 'content', value: string) => {
        setNotes(prev => prev.map(n => n.id === activeId ? { ...n, [field]: value } : n));
    };

    return (
        <div className="chat-area" style={{ padding: 0 }}>
            <div className="notes-container">
                <div className="notes-list">
                    <div className="chat-header" style={{ borderRadius: 0, border: 'none', borderBottom: '1px solid var(--glass-border)' }}>
                        <span style={{ fontSize: '10px', opacity: 0.6 }}>ARCHIVOS NEURALES</span>
                        <button className="model-btn active" onClick={addNote} style={{ width: 24, height: 24, fontSize: 14 }}>+</button>
                    </div>
                    <div className="messages-area" style={{ padding: 0 }}>
                        {notes.map(note => (
                            <div
                                key={note.id}
                                className={`note-item ${activeId === note.id ? 'active' : ''}`}
                                onClick={() => setActiveId(note.id)}
                            >
                                <div className="note-title">{note.title || 'Sin título'}</div>
                                <div className="note-preview">{note.content.substring(0, 30) || 'Vacío...'}</div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="note-editor">
                    {activeNote ? (
                        <>
                            <input
                                className="note-editor-title"
                                value={activeNote.title}
                                onChange={(e) => updateNote('title', e.target.value)}
                                placeholder="Título de la nota"
                            />
                            <textarea
                                className="note-editor-content"
                                value={activeNote.content}
                                onChange={(e) => updateNote('content', e.target.value)}
                                placeholder="Escribe tus pensamientos aquí..."
                            />
                        </>
                    ) : (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', opacity: 0.4 }}>
                            Selecciona o crea una nota
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
