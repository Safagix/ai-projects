"""
Eira Nexus - Unified Sidecar Adapter
====================================
This adapter bridges the Eira Nexus cognitive core with the Windows App (Tauri).
It implements the full communication protocol defined in the fusion architecture.

Communication Protocol:
- Commands (App → Nexus): JSON via stdin
- Events (Nexus → App): JSON via stdout
"""
import sys
import os
import json
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the vision/interface layer from Eira Poliglota
from Eira_Poliglota.main_eira_lab import EiraDigitalLab

# Import the centralized memory
from core.memory import get_memory


class EiraNexusAdapter(EiraDigitalLab):
    """
    Unified adapter that bridges the Nexus (mind) with the App (body).
    
    Responsibilities:
    - Receives commands from the Windows App via stdin
    - Sends status/response events to the Windows App via stdout
    - Delegates all cognitive decisions to EiraAssistant.think()
    - Uses centralized memory for all read/write operations
    """
    
    def __init__(self):
        super().__init__()
        self.last_status = None
        self.memory = get_memory()
        self._load_identity()
    
    def _load_identity(self):
        """Load identity configuration."""
        identity_path = os.path.join(os.path.dirname(__file__), "identity.json")
        if os.path.exists(identity_path):
            with open(identity_path, "r", encoding="utf-8") as f:
                self.identity = json.load(f)
                print(f"🆔 Identity loaded: {self.identity.get('name', 'Eira')}")
        else:
            self.identity = {"name": "Eira"}
    
    def emit(self, event_type: str, data: dict):
        """
        Send an event to the Windows App via stdout.
        This is the ONLY way to communicate with the frontend.
        """
        event = {"type": event_type, "data": data}
        print(json.dumps(event), flush=True)
    
    def emit_status(self):
        """Send current status to the App."""
        status_data = {
            "status": self.eira_status,
            "listening": self.listening_mode,
            "paused": self.paused,
            "mic_muted": self.mic_muted,
            "audio_level": self.get_audio_level()
        }
        
        # Only emit if status changed (to reduce traffic)
        if status_data != self.last_status:
            self.emit("status", status_data)
            self.last_status = status_data.copy()
    
    def emit_response(self, text: str):
        """Send a cognitive response to the App for display."""
        self.emit("response", {"text": text})
    
    def emit_memory(self, key: str, value: str):
        """Send a memory value to the App."""
        self.emit("memory", {"key": key, "value": value})
    
    def emit_error(self, message: str):
        """Send an error message to the App."""
        self.emit("error", {"message": message})
    
    # --- Override draw_ui to use JSON events instead of OpenCV ---
    def draw_ui(self, img):
        """Instead of drawing on OpenCV, emit JSON status."""
        self.emit_status()
    
    # --- Command Handlers ---
    def handle_command(self, cmd: dict):
        """
        Process a command received from the Windows App.
        This is the central dispatch for all App → Nexus communication.
        """
        action = cmd.get("action", "")
        
        try:
            if action == "think":
                # Cognitive request - delegate to EiraAssistant
                user_text = cmd.get("text", "")
                if user_text and hasattr(self, "eira") and self.eira:
                    response = self.eira.think(user_text)
                    if response:
                        self.emit_response(response)
                else:
                    self.emit_error("Cognitive core not initialized")
            
            elif action == "trigger_voice":
                # Activate voice listening mode
                self.listening_mode = True
            
            elif action == "toggle_mute":
                self.mic_muted = not self.mic_muted
            
            elif action == "toggle_lock":
                self.paused = not self.paused
            
            elif action == "get_memory":
                # Memory read request
                key = cmd.get("key", "")
                if key:
                    value = self.memory.get(key)
                    self.emit_memory(key, value)
                else:
                    # Return all memory
                    all_memory = self.memory.load_all()
                    self.emit_memory("all", all_memory[:1000])  # Truncate for transport
            
            elif action == "get_status":
                # Explicit status request
                self.emit_status()
            
            elif action == "shutdown":
                self.running = False
                sys.exit(0)
            
            else:
                self.emit_error(f"Unknown action: {action}")
        
        except Exception as e:
            self.emit_error(str(e))
    
    def stdin_listener(self):
        """
        Background thread that listens for commands from the Windows App.
        Each line is expected to be a JSON command object.
        """
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                cmd = json.loads(line)
                self.handle_command(cmd)
            except json.JSONDecodeError as e:
                self.emit_error(f"Invalid JSON: {e}")
            except Exception as e:
                self.emit_error(f"Command error: {e}")
    
    def run_sidecar(self):
        """
        Main entry point for sidecar execution.
        Starts the stdin listener and runs the vision loop.
        """
        # Start command listener in background
        threading.Thread(target=self.stdin_listener, daemon=True).start()
        
        # Emit initial startup event
        self.emit("startup", {
            "name": self.identity.get("name", "Eira"),
            "version": self.identity.get("version", "2.0.0"),
            "memory_status": self.memory.get_stats()
        })
        
        # Run the main vision/interface loop
        self.run()


if __name__ == "__main__":
    adapter = EiraNexusAdapter()
    adapter.run_sidecar()
