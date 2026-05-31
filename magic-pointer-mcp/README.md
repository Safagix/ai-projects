# Magic Pointer MCP Server

AI cursor that sees your screen, thinks with a vision model, and acts on your desktop.

## Architecture

```
OpenCode ──stdin/stdout (JSON-RPC 2.0)──> magic-pointer-mcp/
                                              ├── server.py       (MCP protocol handler)
                                              ├── screen.py       (mss screen capture)
                                              ├── vision.py       (Ollama moondream client)
                                              ├── action.py       (PyAutoGUI wrapper)
                                              ├── overlay.py      (guided mode confirmations)
                                              └── config.py       (.env settings)
```

## See → Think → Act Loop

1. **See**: `magic_screenshot` captures the screen
2. **Think**: `magic_see` analyzes with moondream vision model
3. **Act**: `magic_click`, `magic_type`, `magic_press`, etc.

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- `moondream` model: `ollama pull moondream:latest`

### Install

```bash
# Run the setup script
setup.bat

# Or manually:
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
```

### Run

```bash
.venv\Scripts\python.exe server.py
```

## Configuration (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama API endpoint |
| `VISION_MODEL` | `moondream:latest` | Vision model name |
| `MAGIC_MODE` | `auto` | `auto` or `guided` |
| `CLICK_PAUSE` | `0.3` | Seconds before clicking |
| `TYPE_INTERVAL_MIN` | `0.03` | Min keystroke delay |
| `TYPE_INTERVAL_MAX` | `0.08` | Max keystroke delay |
| `MOVE_DURATION` | `0.3` | Mouse move animation time |
| `SCREENSHOT_MAX_DIM` | `1920` | Max dimension for vision |
| `SAFETY_MARGIN_PX` | `10` | Edge safety margin |

## Tools (16 total)

| Tool | Description |
|------|-------------|
| `magic_screenshot` | Capture screen, return base64 PNG + dimensions |
| `magic_see` | Analyze screen with vision model (describe or ask questions) |
| `magic_find` | Locate UI element by description, return x,y coordinates |
| `magic_click` | Click at coordinates or find and click by description |
| `magic_double_click` | Double-click at coordinates |
| `magic_type` | Type text via clipboard paste |
| `magic_press` | Press a single key (enter, tab, escape, etc.) |
| `magic_hotkey` | Press key combination (ctrl+c, alt+tab, etc.) |
| `magic_move` | Move mouse to coordinates |
| `magic_scroll` | Scroll up/down |
| `magic_drag` | Click and drag between two points |
| `magic_wait` | Wait for specified seconds |
| `magic_position` | Get current mouse position |
| `magic_screen_size` | Get display dimensions |
| `magic_window` | Get active window, focus window, or list all windows |
| `magic_status` | Get server status, Ollama health, available models |

## Modes

### Auto Mode (default)

Tools execute immediately without confirmation. Best for automation workflows.

### Guided Mode

Before each action, a confirmation dialog appears. User presses Enter to execute or Esc to cancel. Best for testing and debugging.

Change mode in `.env`: `MAGIC_MODE=guided`

## OpenCode Integration

Registered in `%USERPROFILE%\.opencode\opencode.json`:

```json
{
  "mcpServers": {
    "magic-pointer": {
      "command": "D:\\Digital Lab\\magic-pointer-mcp\\.venv\\Scripts\\python.exe",
      "args": ["D:\\Digital Lab\\magic-pointer-mcp\\server.py"]
    }
  }
}
```

## Example Workflows

### Open an app and type text
```
1. magic_screenshot
2. magic_see (question: "What apps are visible on the taskbar?")
3. magic_click (element: "Notepad icon")
4. magic_wait (seconds: 1)
5. magic_type (text: "Hello from Magic Pointer!")
```

### Navigate a website
```
1. magic_screenshot
2. magic_see (question: "What is the URL in the address bar?")
3. magic_click (element: "address bar")
4. magic_hotkey (keys: ["ctrl", "a"])
5. magic_type (text: "https://example.com")
6. magic_press (key: "enter")
```

### Find and click a button
```
1. magic_find (element: "Submit button")
2. magic_click (x: result.x, y: result.y)
```

## Resource Usage

| Component | RAM |
|-----------|-----|
| Windows idle | ~3GB |
| Ollama + moondream | ~2.5GB |
| OpenCode + Node | ~1GB |
| Magic Pointer Python | ~200MB |
| **Free headroom** | **~5GB** |

Moondream inference on CPU: ~2-5 seconds per screenshot query.

## Troubleshooting

- **Ollama not running**: Run `ollama serve` or start Ollama Desktop
- **moondream not found**: Run `ollama pull moondream:latest`
- **Screenshot fails**: Ensure display is active (not locked)
- **PyAutoGUI failsafe**: Move mouse to top-left corner to abort any action
