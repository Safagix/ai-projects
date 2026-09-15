from __future__ import annotations

import ctypes
import os
import queue
import threading
import uuid
from ctypes import wintypes
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Callable

from fastapi import HTTPException, status

from .config import settings

ALLOWED_WINDOWS = {"Fashion CAD Studio", "Blender", "Fashion CAD Pattern Viewer"}
SENSITIVE_INTENTS = {"export", "print", "cloud", "overwrite"}
HOTKEY_ID = 0xFACA
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
VK_PAUSE = 0x13
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012


@dataclass
class OperatorSession:
    session_id: str
    expires_at: datetime
    allowed_windows: set[str]
    state: str = "active"
    pause_reason: str | None = None


@dataclass
class OperatorConfirmation:
    confirmation_id: str
    session_id: str
    window_name: str
    intent: str
    expires_at: datetime


class DesktopOverlay:
    """A small native safety banner, intentionally independent of the web UI."""

    def __init__(self) -> None:
        self._commands: queue.Queue[str | None] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def show(self, text: str) -> None:
        if os.name != "nt":
            return
        with self._lock:
            if not self._thread or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._run, name="fashion-cad-operator-overlay", daemon=True)
                self._thread.start()
        self._commands.put(text)

    def close(self) -> None:
        if self._thread and self._thread.is_alive():
            self._commands.put(None)

    def _run(self) -> None:
        try:
            import tkinter as tk

            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.attributes("-alpha", 0.96)
            root.configure(background="#b73227")
            root.geometry("430x58-28+28")
            label = tk.Label(
                root,
                background="#b73227",
                foreground="white",
                font=("Segoe UI", 10, "bold"),
                justify="left",
                padx=14,
                pady=9,
                anchor="w",
                text="STUDIO OPERATOR ACTIVO\\nCtrl+Alt+Pause detiene toda automatización",
            )
            label.pack(fill="both", expand=True)

            def poll() -> None:
                try:
                    while True:
                        command = self._commands.get_nowait()
                        if command is None:
                            root.destroy()
                            return
                        label.configure(text=command)
                except queue.Empty:
                    pass
                root.after(150, poll)

            root.after(0, poll)
            root.mainloop()
        except Exception:
            # A failed overlay must never make desktop automation less safe; the API remains disabled by default.
            return


class KillSwitchMonitor:
    """Registers the process-wide Ctrl+Alt+Pause kill switch on Windows."""

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._callback: Callable[[], None] | None = None
        self._ready = threading.Event()
        self._registered = False

    def start(self, callback: Callable[[], None]) -> bool:
        if os.name != "nt":
            return False
        if self._thread and self._thread.is_alive():
            return self._registered
        self._callback = callback
        self._ready.clear()
        self._registered = False
        self._thread = threading.Thread(target=self._run, name="fashion-cad-kill-switch", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=2)
        return self._registered

    def stop(self) -> None:
        if os.name == "nt" and self._thread_id:
            ctypes.windll.user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)

    def _run(self) -> None:
        self._thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        user32 = ctypes.windll.user32
        if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_PAUSE):
            self._ready.set()
            return
        self._registered = True
        self._ready.set()
        message = wintypes.MSG()
        try:
            while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                if message.message == WM_HOTKEY and message.wParam == HOTKEY_ID and self._callback:
                    self._callback()
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID)
            self._registered = False
            self._thread_id = None


class OperatorGuard:
    def __init__(self, repository_provider: Callable[[], Any]) -> None:
        self.sessions: dict[str, OperatorSession] = {}
        self.confirmations: dict[str, OperatorConfirmation] = {}
        self._repository_provider = repository_provider
        self._lock = threading.RLock()
        self._overlay = DesktopOverlay()
        self._kill_switch = KillSwitchMonitor()

    def _audit(
        self, session_id: str, action: str, outcome: str, *, window_name: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        self._repository_provider().record_operator_audit(
            session_id, action, outcome, window_name=window_name, details=details
        )

    def _overlay_text(self, state: str, session_count: int) -> str:
        return (
            f"STUDIO OPERATOR {state.upper()} · {session_count} sesión(es)\\n"
            "Ctrl+Alt+Pause detiene toda automatización"
        )

    def _refresh_overlay(self) -> None:
        with self._lock:
            active = [session for session in self.sessions.values() if session.state == "active"]
            paused = [session for session in self.sessions.values() if session.state == "paused"]
        if active:
            self._overlay.show(self._overlay_text("activo", len(active)))
        elif paused:
            self._overlay.show(self._overlay_text("pausado", len(paused)))
        else:
            self._overlay.close()

    def start(self, requested_windows: list[str]) -> OperatorSession:
        if not settings.operator_enabled:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Studio Operator está desactivado.")
        requested = set(requested_windows)
        if not requested or not requested.issubset(ALLOWED_WINDOWS):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ventana no permitida.")
        if not self._kill_switch.start(lambda: self.stop_all(reason="kill switch Ctrl+Alt+Pause")):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo registrar Ctrl+Alt+Pause; el operador permanece desactivado.")
        session = OperatorSession(
            session_id=str(uuid.uuid4()),
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
            allowed_windows=requested,
        )
        with self._lock:
            self.sessions[session.session_id] = session
        self._audit(session.session_id, "session_started", "allowed", details={"allowed_windows": sorted(requested)})
        self._refresh_overlay()
        return session

    def stop(self, session_id: str, *, reason: str = "requested") -> None:
        with self._lock:
            session = self.sessions.pop(session_id, None)
            self.confirmations = {
                confirmation_id: confirmation
                for confirmation_id, confirmation in self.confirmations.items()
                if confirmation.session_id != session_id
            }
        if session:
            self._audit(session_id, "session_stopped", "allowed", details={"reason": reason})
        self._refresh_overlay()

    def stop_all(self, *, reason: str) -> None:
        with self._lock:
            session_ids = list(self.sessions)
            self.sessions.clear()
            self.confirmations.clear()
        for session_id in session_ids:
            self._audit(session_id, "session_stopped", "allowed", details={"reason": reason})
        self._refresh_overlay()

    def shutdown(self) -> None:
        self.stop_all(reason="API shutdown")
        self._kill_switch.stop()

    def require(self, session_id: str, requested_window: str) -> OperatorSession:
        with self._lock:
            session = self.sessions.get(session_id)
        if not session or session.expires_at <= datetime.now(UTC):
            self.stop(session_id, reason="expired")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sesión de operador vencida o inexistente.")
        if session.state == "paused":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sesión de operador pausada; recuperá el foco y reanudala explícitamente.")
        if requested_window not in session.allowed_windows:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La ventana no pertenece a esta sesión.")
        if self.foreground_window() != requested_window:
            self.pause(session, "focus_lost", requested_window)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La ventana permitida no tiene foco; automatización pausada.")
        return session

    def pause(self, session: OperatorSession, reason: str, requested_window: str) -> None:
        with self._lock:
            if session.state == "paused":
                return
            session.state = "paused"
            session.pause_reason = reason
        self._audit(session.session_id, reason, "blocked", window_name=requested_window)
        self._refresh_overlay()

    def resume(self, session_id: str) -> OperatorSession:
        with self._lock:
            session = self.sessions.get(session_id)
        if not session or session.expires_at <= datetime.now(UTC):
            self.stop(session_id, reason="expired")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sesión de operador vencida o inexistente.")
        foreground = self.foreground_window()
        if foreground not in session.allowed_windows:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Recuperá el foco de una ventana permitida antes de reanudar.")
        with self._lock:
            session.state = "active"
            session.pause_reason = None
        self._audit(session_id, "session_resumed", "allowed", window_name=foreground)
        self._refresh_overlay()
        return session

    def request_confirmation(self, session_id: str, window_name: str, intent: str, summary: str) -> OperatorConfirmation:
        self.require(session_id, window_name)
        confirmation = OperatorConfirmation(
            confirmation_id=str(uuid.uuid4()),
            session_id=session_id,
            window_name=window_name,
            intent=intent,
            expires_at=datetime.now(UTC) + timedelta(minutes=1),
        )
        with self._lock:
            self.confirmations[confirmation.confirmation_id] = confirmation
        self._audit(
            session_id, "confirmation_requested", "allowed", window_name=window_name,
            details={"intent": intent, "summary": summary, "expires_at": confirmation.expires_at.isoformat()},
        )
        return confirmation

    def _require_confirmation(self, session_id: str, window_name: str, intent: str, confirmation_id: str | None) -> None:
        if intent not in SENSITIVE_INTENTS:
            return
        if not confirmation_id:
            self._audit(session_id, "sensitive_action", "blocked", window_name=window_name, details={"intent": intent, "reason": "missing_confirmation"})
            raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail="La acción sensible requiere confirmación explícita y vigente.")
        with self._lock:
            confirmation = self.confirmations.pop(confirmation_id, None)
        if (
            not confirmation
            or confirmation.expires_at <= datetime.now(UTC)
            or confirmation.session_id != session_id
            or confirmation.window_name != window_name
            or confirmation.intent != intent
        ):
            self._audit(session_id, "sensitive_action", "blocked", window_name=window_name, details={"intent": intent, "reason": "invalid_confirmation"})
            raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail="La confirmación sensible no es válida, coincide con otra acción o venció.")

    @staticmethod
    def foreground_window() -> str:
        if os.name != "nt":
            return ""
        handle = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(handle)
        buffer = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(handle, buffer, length + 1)
        title = buffer.value
        for allowed in ALLOWED_WINDOWS:
            if allowed.lower() in title.lower():
                return allowed
        return ""

    @staticmethod
    def window_bounds() -> tuple[int, int, int, int]:
        handle = ctypes.windll.user32.GetForegroundWindow()
        rect = wintypes.RECT()
        if not ctypes.windll.user32.GetWindowRect(handle, ctypes.byref(rect)):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se pudo obtener la geometría de la ventana.")
        return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top

    @staticmethod
    def automation() -> Any:
        try:
            import pyautogui
        except ImportError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="PyAutoGUI no está instalado.") from exc
        return pyautogui

    def _complete_action(self, session_id: str, window_name: str, action: str, details: dict[str, Any], execute: Callable[[Any], None]) -> None:
        self.require(session_id, window_name)
        try:
            execute(self.automation())
        except HTTPException:
            raise
        except Exception as exc:
            self._audit(session_id, action, "failed", window_name=window_name, details={"error": type(exc).__name__})
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No se pudo ejecutar la acción del operador.") from exc
        self._audit(session_id, action, "allowed", window_name=window_name, details=details)

    def click(self, session_id: str, window_name: str, x: int, y: int, intent: str, confirmation_id: str | None) -> None:
        self.require(session_id, window_name)
        self._require_confirmation(session_id, window_name, intent, confirmation_id)
        origin_x, origin_y, width, height = self.window_bounds()
        if x >= width or y >= height:
            self._audit(session_id, "click", "blocked", window_name=window_name, details={"reason": "outside_window", "x": x, "y": y})
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El click queda fuera de la ventana permitida.")
        self._complete_action(session_id, window_name, "click", {"x": x, "y": y, "intent": intent}, lambda pyautogui: pyautogui.click(origin_x + x, origin_y + y))

    def keypress(self, session_id: str, window_name: str, key: str, intent: str, confirmation_id: str | None) -> None:
        self.require(session_id, window_name)
        self._require_confirmation(session_id, window_name, intent, confirmation_id)
        self._complete_action(session_id, window_name, "keypress", {"key": key, "intent": intent}, lambda pyautogui: pyautogui.press(key))

    def type_text(self, session_id: str, window_name: str, text: str, intent: str, confirmation_id: str | None) -> None:
        self.require(session_id, window_name)
        self._require_confirmation(session_id, window_name, intent, confirmation_id)
        self._complete_action(session_id, window_name, "type", {"characters": len(text), "intent": intent}, lambda pyautogui: pyautogui.write(text, interval=0.01))
