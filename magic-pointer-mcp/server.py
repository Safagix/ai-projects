#!/usr/bin/env python3
"""Magic Pointer MCP Server - AI cursor that sees, thinks, and acts on your desktop."""

import json
import sys
import time
import traceback
from typing import Any

import screen
import vision
import action
import config
from overlay import show_confirmation, draw_indicator

VISION = vision.VisionClient()

MODE = config.MAGIC_MODE


def _needs_confirmation(action_name: str, x: int = 0, y: int = 0) -> bool:
    if MODE != "guided":
        return False
    return show_confirmation(x, y, action_name)


def _error_response(id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


def _success_response(id: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": id, "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}}


TOOLS = [
    {
        "name": "magic_screenshot",
        "description": "Capture the current screen. Returns base64 PNG, dimensions, and timestamp.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "region": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "width": {"type": "integer"}, "height": {"type": "integer"}}, "description": "Optional region to capture"}
            },
        },
    },
    {
        "name": "magic_see",
        "description": "Analyze the current screen with a vision model. Returns a detailed description of UI elements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Optional question about the screen. If omitted, describes everything."}
            },
        },
    },
    {
        "name": "magic_find",
        "description": "Find a UI element on screen by description. Returns x,y coordinates and confidence.",
        "inputSchema": {
            "type": "object",
            "required": ["element"],
            "properties": {
                "element": {"type": "string", "description": "Description of the UI element to find, e.g. 'Submit button', 'search bar'"}
            },
        },
    },
    {
        "name": "magic_click",
        "description": "Click at coordinates or find and click a UI element by description.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "element": {"type": "string", "description": "UI element description (alternative to x,y)"},
                "button": {"type": "string", "enum": ["left", "right"], "default": "left"},
            },
        },
    },
    {
        "name": "magic_double_click",
        "description": "Double-click at the given coordinates.",
        "inputSchema": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
        },
    },
    {
        "name": "magic_type",
        "description": "Type text into the active field using clipboard paste (fast and reliable).",
        "inputSchema": {
            "type": "object",
            "required": ["text"],
            "properties": {"text": {"type": "string"}},
        },
    },
    {
        "name": "magic_press",
        "description": "Press a single key (e.g., 'enter', 'tab', 'escape', 'backspace').",
        "inputSchema": {
            "type": "object",
            "required": ["key"],
            "properties": {"key": {"type": "string"}},
        },
    },
    {
        "name": "magic_hotkey",
        "description": "Press a key combination (e.g., ctrl+c, alt+tab, ctrl+shift+esc).",
        "inputSchema": {
            "type": "object",
            "required": ["keys"],
            "properties": {"keys": {"type": "array", "items": {"type": "string"}, "description": "List of keys, e.g. ['ctrl', 'c']"}},
        },
    },
    {
        "name": "magic_move",
        "description": "Move the mouse to the given coordinates.",
        "inputSchema": {
            "type": "object",
            "required": ["x", "y"],
            "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
        },
    },
    {
        "name": "magic_scroll",
        "description": "Scroll up (positive) or down (negative).",
        "inputSchema": {
            "type": "object",
            "required": ["amount"],
            "properties": {"amount": {"type": "integer"}, "x": {"type": "integer"}, "y": {"type": "integer"}},
        },
    },
    {
        "name": "magic_drag",
        "description": "Click and drag from one point to another.",
        "inputSchema": {
            "type": "object",
            "required": ["x1", "y1", "x2", "y2"],
            "properties": {"x1": {"type": "integer"}, "y1": {"type": "integer"}, "x2": {"type": "integer"}, "y2": {"type": "integer"}, "duration": {"type": "number"}},
        },
    },
    {
        "name": "magic_wait",
        "description": "Wait for a specified number of seconds.",
        "inputSchema": {
            "type": "object",
            "required": ["seconds"],
            "properties": {"seconds": {"type": "number"}},
        },
    },
    {
        "name": "magic_position",
        "description": "Get the current mouse cursor position.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "magic_screen_size",
        "description": "Get the screen/display dimensions.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "magic_window",
        "description": "Window operations: get active window, focus a window by title, or list all windows.",
        "inputSchema": {
            "type": "object",
            "required": ["action"],
            "properties": {
                "action": {"type": "string", "enum": ["active", "focus", "list"]},
                "title": {"type": "string", "description": "Window title (required for 'focus' action)"},
            },
        },
    },
    {
        "name": "magic_status",
        "description": "Get server status including mode, Ollama health, and available models.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def handle_initialize(params: dict) -> dict:
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "magic-pointer", "version": "1.0.0"},
    }


def handle_tools_list(params: dict) -> dict:
    return {"tools": TOOLS}


def handle_tools_call(req: dict) -> dict:
    params = req.get("params", {})
    name = params.get("name", "")
    args = params.get("arguments", {})

    try:
        if name == "magic_screenshot":
            region = args.get("region")
            if region:
                img = screen.capture_region(region["x"], region["y"], region["width"], region["height"])
            else:
                img = screen.capture_full()
            img = screen.resize_for_vision(img)
            b64 = screen.img_to_base64(img)
            w, h = img.size
            return _success_response(req.get("id"), {"width": w, "height": h, "image": b64, "timestamp": time.time()})

        elif name == "magic_see":
            img = screen.capture_full()
            img = screen.resize_for_vision(img)
            b64 = screen.img_to_base64(img)
            question = args.get("question")
            if question:
                result = VISION.ask(b64, question)
            else:
                result = VISION.describe(b64)
            return _success_response(req.get("id"), {"analysis": result})

        elif name == "magic_find":
            element = args.get("element", "")
            img = screen.capture_full()
            img = screen.resize_for_vision(img)
            b64 = screen.img_to_base64(img)
            result = VISION.find_element(b64, element)
            return _success_response(req.get("id"), result)

        elif name == "magic_click":
            element = args.get("element")
            button = args.get("button", "left")
            if element:
                img = screen.capture_full()
                img = screen.resize_for_vision(img)
                b64 = screen.img_to_base64(img)
                found = VISION.find_element(b64, element)
                if found["confidence"] < 30:
                    return _error_response(req.get("id"), -32602, f"Could not find '{element}' with sufficient confidence")
                x, y = found["x"], found["y"]
            else:
                x, y = args.get("x"), args.get("y")
                if x is None or y is None:
                    return _error_response(req.get("id"), -32602, "Either 'element' or both 'x' and 'y' are required")

            if _needs_confirmation(f"click ({button}) at ({x},{y})", x, y):
                pass
            elif MODE == "guided":
                return _success_response(req.get("id"), {"status": "cancelled", "reason": "user declined"})

            draw_indicator(x, y, f"click {button}")
            result = action.click(x, y, button=button)
            return _success_response(req.get("id"), result)

        elif name == "magic_double_click":
            x, y = args.get("x"), args.get("y")
            if x is None or y is None:
                return _error_response(req.get("id"), -32602, "x and y required")
            if _needs_confirmation(f"double_click at ({x},{y})", x, y):
                pass
            elif MODE == "guided":
                return _success_response(req.get("id"), {"status": "cancelled"})
            draw_indicator(x, y, "double_click")
            result = action.double_click(x, y)
            return _success_response(req.get("id"), result)

        elif name == "magic_type":
            text = args.get("text", "")
            if _needs_confirmation(f"type '{text[:50]}'", 0, 0):
                pass
            elif MODE == "guided":
                return _success_response(req.get("id"), {"status": "cancelled"})
            result = action.type_text(text)
            return _success_response(req.get("id"), result)

        elif name == "magic_press":
            key = args.get("key", "")
            if _needs_confirmation(f"press '{key}'", 0, 0):
                pass
            elif MODE == "guided":
                return _success_response(req.get("id"), {"status": "cancelled"})
            result = action.press(key)
            return _success_response(req.get("id"), result)

        elif name == "magic_hotkey":
            keys = args.get("keys", [])
            if _needs_confirmation(f"hotkey {keys}", 0, 0):
                pass
            elif MODE == "guided":
                return _success_response(req.get("id"), {"status": "cancelled"})
            result = action.hotkey(*keys)
            return _success_response(req.get("id"), result)

        elif name == "magic_move":
            x, y = args.get("x"), args.get("y")
            if x is None or y is None:
                return _error_response(req.get("id"), -32602, "x and y required")
            draw_indicator(x, y, "move")
            result = action.move(x, y)
            return _success_response(req.get("id"), result)

        elif name == "magic_scroll":
            amount = args.get("amount", 0)
            x, y = args.get("x"), args.get("y")
            if _needs_confirmation(f"scroll {amount}", x or 0, y or 0):
                pass
            elif MODE == "guided":
                return _success_response(req.get("id"), {"status": "cancelled"})
            result = action.scroll(amount, x, y)
            return _success_response(req.get("id"), result)

        elif name == "magic_drag":
            x1, y1, x2, y2 = args.get("x1"), args.get("y1"), args.get("x2"), args.get("y2")
            if any(v is None for v in [x1, y1, x2, y2]):
                return _error_response(req.get("id"), -32602, "x1, y1, x2, y2 required")
            duration = args.get("duration", 0.5)
            if _needs_confirmation(f"drag ({x1},{y1})->({x2},{y2})", x1, y1):
                pass
            elif MODE == "guided":
                return _success_response(req.get("id"), {"status": "cancelled"})
            draw_indicator(x1, y1, "drag start")
            result = action.drag(x1, y1, x2, y2, duration)
            return _success_response(req.get("id"), result)

        elif name == "magic_wait":
            seconds = args.get("seconds", 0)
            result = action.wait(seconds)
            return _success_response(req.get("id"), result)

        elif name == "magic_position":
            result = action.get_position()
            return _success_response(req.get("id"), result)

        elif name == "magic_screen_size":
            result = action.get_screen_size()
            return _success_response(req.get("id"), result)

        elif name == "magic_window":
            act = args.get("action", "active")
            title = args.get("title", "")
            if act == "active":
                result = action.get_active_window()
            elif act == "focus":
                if not title:
                    return _error_response(req.get("id"), -32602, "title required for focus action")
                result = action.focus_window(title)
            elif act == "list":
                result = action.list_windows()
            else:
                return _error_response(req.get("id"), -32602, f"Unknown window action: {act}")
            return _success_response(req.get("id"), result)

        elif name == "magic_status":
            health = VISION.health()
            size = action.get_screen_size()
            return _success_response(req.get("id"), {
                "mode": MODE,
                "screen": size,
                "ollama": health,
                "vision_model": config.VISION_MODEL,
                "timestamp": time.time(),
            })

        else:
            return _error_response(req.get("id"), -32601, f"Unknown tool: {name}")

    except Exception as e:
        return _error_response(req.get("id"), -32603, f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}")


def handle_request(line: str) -> str | None:
    try:
        req = json.loads(line)
    except json.JSONDecodeError:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})

    method = req.get("method", "")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "initialize":
        result_data = handle_initialize(params)
        result = {"jsonrpc": "2.0", "id": req_id, "result": result_data}
    elif method == "tools/list":
        result_data = handle_tools_list(params)
        result = {"jsonrpc": "2.0", "id": req_id, "result": result_data}
    elif method == "tools/call":
        result = handle_tools_call(req)
    else:
        result = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

    if req_id is not None:
        return json.dumps(result)
    return None


def main():
    sys.stderr.write(f"[magic-pointer] Starting MCP server (mode={MODE}, ollama={config.OLLAMA_BASE_URL})\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            response = handle_request(line)
            if response:
                print(response, flush=True)
        except Exception as e:
            err = json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})
            print(err, flush=True)


if __name__ == "__main__":
    main()
