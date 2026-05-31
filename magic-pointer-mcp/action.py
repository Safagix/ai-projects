import random
import time

import pyautogui
import pyperclip
from config import CLICK_PAUSE, TYPE_INTERVAL_MIN, TYPE_INTERVAL_MAX, MOVE_DURATION, SAFETY_MARGIN_PX

pyautogui.FAILSAFE = True


def _safe_coords(x: int, y: int) -> tuple[int, int]:
    w, h = pyautogui.size()
    x = max(SAFETY_MARGIN_PX, min(x, w - SAFETY_MARGIN_PX))
    y = max(SAFETY_MARGIN_PX, min(y, h - SAFETY_MARGIN_PX))
    return x, y


def click(x: int | None = None, y: int | None = None, button: str = "left") -> dict:
    if x is not None and y is not None:
        x, y = _safe_coords(x, y)
        pyautogui.moveTo(x, y, duration=MOVE_DURATION * 0.5)
        time.sleep(CLICK_PAUSE)
        pyautogui.click(x, y, button=button)
    else:
        pyautogui.click(button=button)
    pos = pyautogui.position()
    return {"action": f"{button}_click", "x": pos.x, "y": pos.y}


def double_click(x: int, y: int) -> dict:
    x, y = _safe_coords(x, y)
    pyautogui.moveTo(x, y, duration=MOVE_DURATION * 0.5)
    time.sleep(CLICK_PAUSE)
    pyautogui.doubleClick(x, y)
    pos = pyautogui.position()
    return {"action": "double_click", "x": pos.x, "y": pos.y}


def right_click(x: int, y: int) -> dict:
    x, y = _safe_coords(x, y)
    pyautogui.moveTo(x, y, duration=MOVE_DURATION * 0.5)
    time.sleep(CLICK_PAUSE)
    pyautogui.rightClick(x, y)
    pos = pyautogui.position()
    return {"action": "right_click", "x": pos.x, "y": pos.y}


def type_text(text: str) -> dict:
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    return {"action": "type", "text": text, "method": "clipboard_paste"}


def type_text_keystroke(text: str) -> dict:
    for ch in text:
        pyautogui.write(ch)
        time.sleep(random.uniform(TYPE_INTERVAL_MIN, TYPE_INTERVAL_MAX))
    return {"action": "type_keystroke", "text": text}


def press(key: str) -> dict:
    pyautogui.press(key)
    return {"action": "press", "key": key}


def hotkey(*keys: str) -> dict:
    pyautogui.hotkey(*keys)
    return {"action": "hotkey", "keys": list(keys)}


def move(x: int, y: int, duration: float | None = None) -> dict:
    x, y = _safe_coords(x, y)
    pyautogui.moveTo(x, y, duration=duration or MOVE_DURATION)
    pos = pyautogui.position()
    return {"action": "move", "x": pos.x, "y": pos.y}


def scroll(amount: int, x: int | None = None, y: int | None = None) -> dict:
    if x is not None and y is not None:
        x, y = _safe_coords(x, y)
        pyautogui.scroll(amount, x=x, y=y)
    else:
        pyautogui.scroll(amount)
    return {"action": "scroll", "amount": amount}


def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> dict:
    x1, y1 = _safe_coords(x1, y1)
    x2, y2 = _safe_coords(x2, y2)
    pyautogui.moveTo(x1, y1, duration=0.2)
    time.sleep(0.1)
    pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
    pos = pyautogui.position()
    return {"action": "drag", "from": {"x": x1, "y": y1}, "to": {"x": pos.x, "y": pos.y}}


def get_position() -> dict:
    pos = pyautogui.position()
    return {"x": pos.x, "y": pos.y}


def get_screen_size() -> dict:
    w, h = pyautogui.size()
    return {"width": w, "height": h}


def wait(seconds: float) -> dict:
    time.sleep(seconds)
    return {"action": "wait", "seconds": seconds}


def get_active_window() -> dict:
    try:
        import pygetwindow as gw
        win = gw.getActiveWindow()
        if win:
            return {"title": win.title, "left": win.left, "top": win.top, "width": win.width, "height": win.height}
    except Exception:
        pass
    return {"title": "unknown"}


def focus_window(title_contains: str) -> dict:
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle(title_contains)
        if windows:
            windows[0].activate()
            time.sleep(0.3)
            return {"action": "focus_window", "title": windows[0].title, "success": True}
    except Exception:
        pass
    return {"action": "focus_window", "title": title_contains, "success": False}


def list_windows() -> dict:
    try:
        import pygetwindow as gw
        return {"windows": [w.title for w in gw.getAllWindows() if w.title.strip()]}
    except Exception:
        return {"windows": []}
