import threading
import tkinter as tk
from typing import Callable

_confirm_result = None
_confirm_event = None


def show_confirmation(x: int, y: int, action_label: str, timeout: float = 15.0) -> bool:
    global _confirm_result, _confirm_event
    _confirm_event = threading.Event()
    _confirm_result = None

    def _ui():
        root = tk.Tk()
        root.title("Magic Pointer - Confirm Action")
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.92)
        root.resizable(False, False)

        canvas = tk.Canvas(root, width=320, height=180, bg="#1a1a2e", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_rectangle(2, 2, 318, 178, outline="#00d4ff", width=2)

        canvas.create_text(160, 30, text="MAGIC POINTER", fill="#00d4ff", font=("Consolas", 12, "bold"))
        canvas.create_text(160, 60, text="Action:", fill="#888", font=("Consolas", 10))
        canvas.create_text(160, 85, text=action_label, fill="#ffffff", font=("Consolas", 11, "bold"))
        canvas.create_text(160, 110, text=f"Target: ({x}, {y})", fill="#aaa", font=("Consolas", 9))

        canvas.create_text(160, 140, text="[Enter] Execute   [Esc] Cancel", fill="#00d4ff", font=("Consolas", 10))

        indicator = canvas.create_oval(145, 155, 155, 165, fill="#00ff88", outline="")
        canvas.itemconfig(indicator, fill="#00ff88")

        def on_key(e):
            global _confirm_result
            if e.keysym in ("Return", "KP_Enter", "space"):
                _confirm_result = True
                canvas.itemconfig(indicator, fill="#00ff88")
                root.destroy()
            elif e.keysym == "Escape":
                _confirm_result = False
                canvas.itemconfig(indicator, fill="#ff4444")
                root.destroy()

        root.bind("<Key>", on_key)
        root.after(int(timeout * 1000), lambda: root.destroy() if not _confirm_event.is_set() else None)
        root.mainloop()
        _confirm_event.set()

    t = threading.Thread(target=_ui, daemon=True)
    t.start()
    _confirm_event.wait(timeout=timeout + 1)
    return _confirm_result if _confirm_result is not None else False


def draw_indicator(x: int, y: int, label: str, duration: float = 2.0):
    def _ui():
        root = tk.Tk()
        root.title("")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", "black")
        root.attributes("-alpha", 0.8)

        canvas = tk.Canvas(root, width=60, height=60, bg="black", highlightthickness=0)
        canvas.pack()

        canvas.create_oval(5, 5, 55, 55, outline="#ff4444", width=3)
        canvas.create_oval(25, 25, 35, 35, fill="#ff4444")
        canvas.create_text(30, 58, text=label[:20], fill="#ffffff", font=("Consolas", 8))

        root.geometry(f"+{x - 30}+{y - 30}")
        root.after(int(duration * 1000), root.destroy)
        root.mainloop()

    t = threading.Thread(target=_ui, daemon=True)
    t.start()
