import React, { useState, useMemo, useEffect } from 'react';
import { loadData, saveData } from '../../services/storage';

// --- Types ---
type CompletionState = 'completed' | 'partial' | 'acknowledged' | 'excused' | null;

interface HabitLog {
    date: string;
    state: CompletionState;
    note?: string;
}

interface Habit {
    id: string;
    identityAnchor: string;
    behavior: string;
    color: string;
    logs: HabitLog[];
    createdAt: string;
    archived: boolean;
}

// --- Color Options ---
const COLOR_OPTIONS = [
    { name: 'Cyan', value: '#4fc3f7' },
    { name: 'Purple', value: '#9b4dca' },
    { name: 'Green', value: '#28c840' },
    { name: 'Orange', value: '#ffbd44' },
    { name: 'Pink', value: '#ff6b9d' },
    { name: 'Blue', value: '#5c7cfa' },
];

// --- Helper Functions ---
const getDateKey = (date: Date = new Date()): string => {
    return date.toISOString().split('T')[0];
};

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

const getDayName = (day: number): string => {
    const names = ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'];
    return names[day];
};

const calculateMomentum = (logs: HabitLog[]): number => {
    if (logs.length === 0) return 0;
    const now = new Date();
    let score = 0;
    let totalWeight = 0;

    for (let i = 0; i < 30; i++) {
        const d = new Date(now);
        d.setDate(d.getDate() - i);
        const key = getDateKey(d);
        const log = logs.find(l => l.date === key);
        const weight = i < 7 ? 2 : i < 14 ? 1.5 : 1;
        totalWeight += weight;

        if (log?.state === 'completed') score += weight * 1;
        else if (log?.state === 'partial') score += weight * 0.6;
        else if (log?.state === 'acknowledged') score += weight * 0.3;
        else if (log?.state === 'excused') score += weight * 0.8;
    }

    return totalWeight > 0 ? Math.round((score / totalWeight) * 100) : 0;
};

// --- Component ---
export const HabitsModule: React.FC = () => {
    const [habits, setHabits] = useState<Habit[]>([]);
    const [selectedHabit, setSelectedHabit] = useState<string | null>(null);

    // Persistence
    useEffect(() => {
        loadData<Habit[]>('habits.json', []).then(data => {
            setHabits(data);
            if (data.length > 0 && !selectedHabit) {
                setSelectedHabit(data[0].id);
            }
        });
    }, []);

    const saveHabits = (newHabits: Habit[]) => {
        setHabits(newHabits);
        saveData('habits.json', newHabits);
    };
    const [showNewHabitModal, setShowNewHabitModal] = useState(false);
    const [newIdentity, setNewIdentity] = useState('');
    const [newBehavior, setNewBehavior] = useState('');
    const [newColor, setNewColor] = useState(COLOR_OPTIONS[0].value);
    const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
    const [currentYear, setCurrentYear] = useState(new Date().getFullYear());

    const activeHabit = useMemo(() => habits.find(h => h.id === selectedHabit), [habits, selectedHabit]);
    const daysInMonth = useMemo(() => getDaysInMonth(currentYear, currentMonth), [currentYear, currentMonth]);
    const firstDayOfWeek = useMemo(() => new Date(currentYear, currentMonth, 1).getDay(), [currentYear, currentMonth]);

    const toggleDayState = (habitId: string, dateKey: string) => {
        const updatedHabits = habits.map(h => {
            if (h.id !== habitId) return h;
            const existingLog = h.logs.find(l => l.date === dateKey);

            if (existingLog) {
                // Cycle through states: completed -> partial -> acknowledged -> null
                const states: CompletionState[] = ['completed', 'partial', 'acknowledged', null];
                const currentIndex = states.indexOf(existingLog.state);
                const nextState = states[(currentIndex + 1) % states.length];

                if (nextState === null) {
                    return { ...h, logs: h.logs.filter(l => l.date !== dateKey) };
                }
                return { ...h, logs: h.logs.map(l => l.date === dateKey ? { ...l, state: nextState } : l) };
            }
            return { ...h, logs: [...h.logs, { date: dateKey, state: 'completed' as CompletionState }] };
        })
        saveHabits(updatedHabits);
    };

    const handleCreateHabit = () => {
        if (!newIdentity.trim() || !newBehavior.trim()) return;
        const newHabit: Habit = {
            id: Date.now().toString(),
            identityAnchor: newIdentity.trim(),
            behavior: newBehavior.trim(),
            color: newColor,
            logs: [],
            createdAt: new Date().toISOString(),
            archived: false
        };
        saveHabits([...habits, newHabit]);
        setSelectedHabit(newHabit.id);
        setNewIdentity('');
        setNewBehavior('');
        setNewColor(COLOR_OPTIONS[0].value);
        setShowNewHabitModal(false);
    };

    const getStateForDay = (habit: Habit, date: Date): CompletionState => {
        const key = getDateKey(date);
        return habit.logs.find(l => l.date === key)?.state || null;
    };

    const getStateColor = (state: CompletionState, baseColor: string): string => {
        switch (state) {
            case 'completed': return baseColor;
            case 'partial': return `${baseColor}80`;
            case 'acknowledged': return `${baseColor}40`;
            case 'excused': return 'rgba(255, 189, 68, 0.5)';
            default: return 'rgba(255, 255, 255, 0.06)';
        }
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

    const isToday = (date: Date): boolean => {
        const today = new Date();
        return date.getDate() === today.getDate() &&
            date.getMonth() === today.getMonth() &&
            date.getFullYear() === today.getFullYear();
    };

    return (
        <div className="chat-area habits-module">
            <div className="habits-container">
                {/* Habit List Sidebar */}
                <div className="habits-list">
                    <div className="habits-list-header">
                        <span className="habits-list-title">MIS HABITOS</span>
                        <button className="habit-add-btn" onClick={() => setShowNewHabitModal(true)}>+</button>
                    </div>
                    <div className="habits-list-items">
                        {habits.length === 0 ? (
                            <div className="habits-empty-list">
                                <p>No tienes habitos aun</p>
                                <button onClick={() => setShowNewHabitModal(true)}>Crear tu primer habito</button>
                            </div>
                        ) : (
                            habits.filter(h => !h.archived).map(habit => {
                                const momentum = calculateMomentum(habit.logs);
                                return (
                                    <div
                                        key={habit.id}
                                        className={`habit-list-item ${selectedHabit === habit.id ? 'active' : ''}`}
                                        onClick={() => setSelectedHabit(habit.id)}
                                    >
                                        <div className="habit-item-left">
                                            <div className="habit-color-dot" style={{ backgroundColor: habit.color }} />
                                            <div className="habit-item-text">
                                                <div className="habit-behavior">{habit.behavior}</div>
                                                <div className="habit-identity">{habit.identityAnchor}</div>
                                            </div>
                                        </div>
                                        <div className="habit-momentum" style={{ color: momentum > 60 ? '#28c840' : momentum > 30 ? '#ffbd44' : 'rgba(255,255,255,0.3)' }}>
                                            {momentum}%
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </div>
                </div>

                {/* Calendar View */}
                <div className="habit-detail">
                    {activeHabit ? (
                        <>
                            <div className="habit-detail-header">
                                <div className="habit-header-left">
                                    <div className="habit-color-indicator" style={{ backgroundColor: activeHabit.color }} />
                                    <div>
                                        <h2 className="habit-detail-behavior">{activeHabit.behavior}</h2>
                                        <p className="habit-detail-identity">{activeHabit.identityAnchor}</p>
                                    </div>
                                </div>
                                <div className="habit-momentum-badge">
                                    <span className="momentum-number">{calculateMomentum(activeHabit.logs)}</span>
                                    <span className="momentum-percent">%</span>
                                </div>
                            </div>

                            {/* Calendar Navigation */}
                            <div className="calendar-nav">
                                <button className="cal-nav-btn" onClick={prevMonth}>&lt;</button>
                                <span className="cal-nav-title">{getMonthName(currentMonth)} {currentYear}</span>
                                <button className="cal-nav-btn" onClick={nextMonth}>&gt;</button>
                            </div>

                            {/* Calendar Grid */}
                            <div className="calendar-grid">
                                {/* Day Headers */}
                                {['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'].map(day => (
                                    <div key={day} className="calendar-day-header">{day}</div>
                                ))}

                                {/* Empty cells for alignment */}
                                {Array.from({ length: firstDayOfWeek }).map((_, i) => (
                                    <div key={`empty-${i}`} className="calendar-cell empty" />
                                ))}

                                {/* Day cells */}
                                {daysInMonth.map(date => {
                                    const state = getStateForDay(activeHabit, date);
                                    const dateKey = getDateKey(date);
                                    const today = isToday(date);
                                    return (
                                        <div
                                            key={dateKey}
                                            className={`calendar-cell ${state || ''} ${today ? 'today' : ''}`}
                                            style={{ backgroundColor: getStateColor(state, activeHabit.color) }}
                                            onClick={() => toggleDayState(activeHabit.id, dateKey)}
                                            title={`${date.getDate()} - ${state || 'sin marcar'} (clic para cambiar)`}
                                        >
                                            <span className="cell-date">{date.getDate()}</span>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Legend */}
                            <div className="calendar-legend">
                                <div className="legend-item">
                                    <div className="legend-box" style={{ backgroundColor: activeHabit.color }} />
                                    <span>Completado</span>
                                </div>
                                <div className="legend-item">
                                    <div className="legend-box" style={{ backgroundColor: `${activeHabit.color}80` }} />
                                    <span>Parcial</span>
                                </div>
                                <div className="legend-item">
                                    <div className="legend-box" style={{ backgroundColor: `${activeHabit.color}40` }} />
                                    <span>Reconocido</span>
                                </div>
                                <div className="legend-item">
                                    <div className="legend-box" style={{ backgroundColor: 'rgba(255, 189, 68, 0.5)' }} />
                                    <span>Excusado</span>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="habit-empty">
                            <p>{habits.length === 0 ? 'Crea tu primer habito para comenzar' : 'Selecciona un habito para ver su calendario'}</p>
                        </div>
                    )}
                </div>
            </div>

            {/* New Habit Modal */}
            {showNewHabitModal && (
                <div className="habit-modal-overlay" onClick={() => setShowNewHabitModal(false)}>
                    <div className="habit-modal" onClick={(e) => e.stopPropagation()}>
                        <h2 className="habit-modal-title">Nuevo Habito</h2>

                        <div className="habit-modal-field">
                            <label>En quien te estas convirtiendo?</label>
                            <input
                                type="text"
                                value={newIdentity}
                                onChange={(e) => setNewIdentity(e.target.value)}
                                placeholder="Ej: Soy alguien que cuida su mente"
                                className="habit-modal-input"
                            />
                        </div>

                        <div className="habit-modal-field">
                            <label>Que comportamiento lo demuestra?</label>
                            <input
                                type="text"
                                value={newBehavior}
                                onChange={(e) => setNewBehavior(e.target.value)}
                                placeholder="Ej: Meditar 10 minutos"
                                className="habit-modal-input"
                            />
                        </div>

                        <div className="habit-modal-field">
                            <label>Color del habito</label>
                            <div className="color-picker">
                                {COLOR_OPTIONS.map(c => (
                                    <button
                                        key={c.value}
                                        className={`color-option ${newColor === c.value ? 'selected' : ''}`}
                                        style={{ backgroundColor: c.value }}
                                        onClick={() => setNewColor(c.value)}
                                        title={c.name}
                                    />
                                ))}
                            </div>
                        </div>

                        <div className="habit-modal-actions">
                            <button className="habit-modal-cancel" onClick={() => setShowNewHabitModal(false)}>Cancelar</button>
                            <button className="habit-modal-create" onClick={handleCreateHabit}>Crear Habito</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
