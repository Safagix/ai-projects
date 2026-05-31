from __future__ import annotations

import threading
from collections.abc import Callable

from human_typer.engine.typer import HumanTyper

SpeedCallback = Callable[[float], None]
VoidCallback = Callable[[], None]


class HotkeyController:
    def __init__(
        self,
        typer: HumanTyper,
        *,
        on_speed_change: SpeedCallback | None = None,
    ) -> None:
        self._typer = typer
        self._on_speed_change = on_speed_change
        self._thread: threading.Thread | None = None

    def _listen_keys(self) -> None:
        try:
            import keyboard
        except ImportError:
            return
        try:
            keyboard.add_hotkey("p", self._on_toggle_pause)
            keyboard.add_hotkey("s", self._on_stop)
            keyboard.add_hotkey("ctrl+o", self._on_speed_up)
            keyboard.add_hotkey("ctrl+l", self._on_speed_down)
            keyboard.wait()
        except Exception:
            pass

    def _on_toggle_pause(self) -> None:
        paused = self._typer.toggle_pause()
        state = "PAUSADA" if paused else "REANUDADA"
        print(
            f"\n[Control] Escritura {state}. "
            "(P: pausa/reanuda, S: detener, Ctrl+O/L: velocidad)"
        )

    def _on_stop(self) -> None:
        self._typer.stop()
        print("\n[Control] Escritura DETENIDA.")

    def _on_speed_up(self) -> None:
        new = min(5.0, self._typer.speed_multiplier + 0.25)
        self._typer.speed_multiplier = new
        print(f"\n[Control] Velocidad: x{new:.2f}")
        if self._on_speed_change:
            self._on_speed_change(new)

    def _on_speed_down(self) -> None:
        new = max(0.1, self._typer.speed_multiplier - 0.25)
        self._typer.speed_multiplier = new
        print(f"\n[Control] Velocidad: x{new:.2f}")
        if self._on_speed_change:
            self._on_speed_change(new)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._listen_keys, daemon=True)
        self._thread.start()
        print("\n═══ Controles activos (aseg\u00farate de tener la ventana de edici\u00f3n enfocada) ═══")
        print("  [P]         Pausar / Reanudar")
        print("  [S]         Detener escritura")
        print("  [Ctrl+O]    +25% velocidad")
        print("  [Ctrl+L]    -25% velocidad")
        print("═══════════════════════════════════════════════════════════════════════════\n")
