
import React, { useState, useEffect, useMemo } from 'react';
import { loadData, saveData } from '../../services/storage';

// --- Types ---
interface CalendarEvent {
    id: string;
    title: string;
    date: string; // YYYY-MM-DD
    type: 'meeting' | 'deadline' | 'reminder' | 'task';
    completed: boolean;
}

// --- Helper Functions ---
const getDaysInMonth = (year: number, month: number): Date[] => {
    const days: Date[] = [];
    const lastDay = new Date(year, month + 1, 0).getDate();
    for (let d = 1; d <= lastDay; d++) {
        days.push(new Date(year, month, d));
    }
    return days;
};

const getMonthName = (month: number): string => {
    const names = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    return names[month];
};

const getDateKey = (date: Date): string => {
    return date.toISOString().split('T')[0];
};

export const CalendarModule: React.FC = () => {
    const [events, setEvents] = useState<CalendarEvent[]>([]);
    const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
    const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
    const [selectedDate, setSelectedDate] = useState<string | null>(null);

    // Modal State
    const [showEventModal, setShowEventModal] = useState(false);
    const [newEventTitle, setNewEventTitle] = useState('');
    const [newEventType, setNewEventType] = useState<CalendarEvent['type']>('task');

    // Load Data
    useEffect(() => {
        loadData<CalendarEvent[]>('calendar.json', []).then(setEvents);
    }, []);

    // Save Data
    useEffect(() => {
        if (events.length > 0) { // Avoid saving empty if initial load hasn't happened? 
            // Better to just save whenever events change after initial load
            // But for simplicity, we rely on loadData returning defaults.
            // We should add a loaded flag to prevent overwriting with [] on first render before load.
            // However, with the current logic, loadData runs once. 
            // We'll wrap save in a function that we call on updates.
        }
    }, [events]);

    const saveEvents = async (updatedEvents: CalendarEvent[]) => {
        setEvents(updatedEvents);
        await saveData('calendar.json', updatedEvents);
    };

    const daysInMonth = useMemo(() => getDaysInMonth(currentYear, currentMonth), [currentYear, currentMonth]);
    const firstDayOfWeek = useMemo(() => new Date(currentYear, currentMonth, 1).getDay(), [currentYear, currentMonth]);

    const handleCreateEvent = () => {
        if (!newEventTitle.trim() || !selectedDate) return;
        const newEvent: CalendarEvent = {
            id: Date.now().toString(),
            title: newEventTitle,
            date: selectedDate,
            type: newEventType,
            completed: false
        };
        saveEvents([...events, newEvent]);
        setNewEventTitle('');
        setShowEventModal(false);
    };

    const deleteEvent = (id: string) => {
        saveEvents(events.filter(e => e.id !== id));
    };

    const prevMonth = () => {
        if (currentMonth === 0) {
            setCurrentMonth(11);
            setCurrentYear(y => y - 1);
        } else {
            setCurrentMonth(m => m - 1);
        }
    };

    const nextMonth = () => {
        if (currentMonth === 11) {
            setCurrentMonth(0);
            setCurrentYear(y => y + 1);
        } else {
            setCurrentMonth(m => m + 1);
        }
    };

    return (
        <div className="chat-area calendar-module" style={{ display: 'flex', gap: '20px', padding: '20px' }}>
            {/* Calendar Grid Section */}
            <div style={{ flex: 2, display: 'flex', flexDirection: 'column' }}>
                <div className="calendar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <button className="cal-nav-btn" onClick={prevMonth}>&lt;</button>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{getMonthName(currentMonth)} {currentYear}</h2>
                    <button className="cal-nav-btn" onClick={nextMonth}>&gt;</button>
                </div>

                <div className="calendar-grid" style={{ flex: 1 }}>
                    {/* Headers */}
                    {['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'].map(day => (
                        <div key={day} className="calendar-day-header">{day}</div>
                    ))}

                    {/* Empty Cells */}
                    {Array.from({ length: firstDayOfWeek }).map((_, i) => (
                        <div key={`empty-${i}`} className="calendar-cell empty" />
                    ))}

                    {/* Days */}
                    {daysInMonth.map(date => {
                        const dateKey = getDateKey(date);
                        const dayEvents = events.filter(e => e.date === dateKey);
                        const isSelected = selectedDate === dateKey;
                        const isToday = dateKey === getDateKey(new Date());

                        return (
                            <div
                                key={dateKey}
                                className={`calendar-cell ${isSelected ? 'selected' : ''} ${isToday ? 'today' : ''}`}
                                onClick={() => { setSelectedDate(dateKey); }}
                                style={{
                                    position: 'relative',
                                    cursor: 'pointer',
                                    border: isSelected ? '1px solid var(--cyan-accent)' : '1px solid rgba(255,255,255,0.1)'
                                }}
                            >
                                <span className="cell-date">{date.getDate()}</span>
                                <div className="day-dots" style={{ display: 'flex', gap: '2px', position: 'absolute', bottom: '5px', left: '50%', transform: 'translateX(-50%)' }}>
                                    {dayEvents.map(e => (
                                        <div key={e.id} style={{
                                            width: '4px', height: '4px', borderRadius: '50%',
                                            backgroundColor: e.type === 'deadline' ? '#ff6b9d' : '#4fc3f7'
                                        }} />
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Side Panel: Selected Day */}
            <div className="calendar-sidebar" style={{ flex: 1, background: 'rgba(0,0,0,0.2)', borderRadius: '16px', padding: '20px', border: '1px solid var(--glass-border)' }}>
                {selectedDate ? (
                    <>
                        <h3>{selectedDate}</h3>
                        <div className="events-list" style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {events.filter(e => e.date === selectedDate).map(e => (
                                <div key={e.id} className="event-item" style={{
                                    background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '8px',
                                    display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                                }}>
                                    <div>
                                        <div style={{ fontSize: '0.9em', fontWeight: 'bold' }}>{e.title}</div>
                                        <div style={{ fontSize: '0.7em', opacity: 0.7, textTransform: 'uppercase' }}>{e.type}</div>
                                    </div>
                                    <button onClick={() => deleteEvent(e.id)} style={{ background: 'transparent', border: 'none', color: '#ff6b9d', cursor: 'pointer' }}>×</button>
                                </div>
                            ))}
                            {events.filter(e => e.date === selectedDate).length === 0 && <p style={{ opacity: 0.5 }}>No events</p>}
                        </div>

                        <button
                            className="add-event-btn"
                            onClick={() => setShowEventModal(true)}
                            style={{ marginTop: '20px', width: '100%', padding: '10px', background: 'var(--cyan-accent)', border: 'none', borderRadius: '8px', color: 'black', fontWeight: 'bold', cursor: 'pointer' }}
                        >
                            + Add Event
                        </button>
                    </>
                ) : (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', opacity: 0.5 }}>
                        Select a date
                    </div>
                )}
            </div>

            {/* Modal */}
            {showEventModal && (
                <div className="habit-modal-overlay" onClick={() => setShowEventModal(false)}>
                    <div className="habit-modal" onClick={e => e.stopPropagation()}>
                        <h2>New Event</h2>
                        <input
                            value={newEventTitle}
                            onChange={e => setNewEventTitle(e.target.value)}
                            placeholder="Event Title"
                            className="habit-modal-input"
                        />
                        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                            {['meeting', 'deadline', 'task'].map(t => (
                                <button
                                    key={t}
                                    onClick={() => setNewEventType(t as any)}
                                    style={{
                                        flex: 1, padding: '8px',
                                        background: newEventType === t ? 'var(--cyan-accent)' : 'rgba(255,255,255,0.1)',
                                        color: newEventType === t ? 'black' : 'white',
                                        border: 'none', borderRadius: '6px', cursor: 'pointer'
                                    }}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                        <div className="habit-modal-actions">
                            <button className="habit-modal-cancel" onClick={() => setShowEventModal(false)}>Cancel</button>
                            <button className="habit-modal-create" onClick={handleCreateEvent}>Save</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
