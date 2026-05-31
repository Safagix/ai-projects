import sys
import os
import asyncio
import subprocess
import socket
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QScrollArea, QLabel, QFrame, QSizePolicy, QComboBox, QDialog, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter

# Import Brain
try:
    from eira_chat_brain import EiraChatBrain
except ImportError:
    # Fallback to avoid crash if brain file is broken, though normally we want to see the error.
    # For now, just print logic. 
    print("CRITICAL: Could not import EiraChatBrain")
    EiraChatBrain = None

ASSETS_DIR = r"%DIGITAL_LAB%\cuerpo\assets\ava_anime"

class SettingsDialog(QDialog):
    """Dialog to edit Persona keys and System Prompt directly."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Eira Settings (Persona & Behavior)")
        self.resize(600, 500)
        
        self.layout = QVBoxLayout(self)
        
        # 1. System Prompt Editor
        self.layout.addWidget(QLabel("<b>System Prompt (Persona Core):</b>"))
        self.layout.addWidget(QLabel("<i>Edit Eira's personality here. Use {user_profile} and {context} tags.</i>"))
        
        self.txt_prompt = QTextEdit()
        self.layout.addWidget(self.txt_prompt)
        
        # 2. Features
        self.chk_web = QCheckBox("Enable Web Search")
        self.layout.addWidget(self.chk_web)
        
        self.chk_media = QCheckBox("Enable Media Integration")
        self.layout.addWidget(self.chk_media)
        
        # 3. Persona Controls
        self.chk_nsfw = QCheckBox("Enable NSFW/Uncensored Mode")
        self.chk_nsfw.setStyleSheet("color: #ff5555; font-weight: bold;")
        self.layout.addWidget(self.chk_nsfw)
        
        self.layout.addWidget(QLabel("<b>Content Restrictions / Guidelines:</b>"))
        self.txt_restrict = QTextEdit()
        self.txt_restrict.setFixedHeight(80)
        self.layout.addWidget(self.txt_restrict)
        
        # Buttons
        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Save & Reload Brain")
        self.btn_save.clicked.connect(self.save_settings)
        btn_box.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(self.btn_cancel)
        
        self.layout.addLayout(btn_box)
        
        self._load_current_settings()
        
    def _load_current_settings(self):
        # Read from file directly to get fresh state or use brain's config if accessible
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                data = json.load(f)
                
            persona = data.get("persona", {})
            features = data.get("features", {})
            
            self.txt_prompt.setPlainText(persona.get("system_prompt", ""))
            self.chk_web.setChecked(features.get("web_enabled", True))
            self.chk_media.setChecked(features.get("media_enabled", True))
            
            # New Fields
            self.chk_nsfw.setChecked(persona.get("nsfw_mode", False))
            self.txt_restrict.setPlainText(persona.get("content_restrictions", ""))
            
        except Exception as e:
            self.txt_prompt.setPlainText(f"Error reading config: {e}")

    def save_settings(self):
        new_prompt = self.txt_prompt.toPlainText()
        
        # Basic validation
        if "{user_profile}" not in new_prompt:
             QMessageBox.warning(self, "Warning", "Your prompt is missing {user_profile}. Eira might forget who you are!")
        
        new_config = {
            "persona": {
                "system_prompt": new_prompt,
                "nsfw_mode": self.chk_nsfw.isChecked(),
                "content_restrictions": self.txt_restrict.toPlainText(),
                "custom_rules": []
            },
            "features": {
                "web_enabled": self.chk_web.isChecked(),
                "media_enabled": self.chk_media.isChecked()
            },
             # Preserve existing LLM config if possible, but simplest is to read-modify-write. 
             # Since we know the struct, we include it, or better: read existing first.
        }
        
        # Read existing to preserve llm
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                existing = json.load(f)
                if "llm" in existing:
                    new_config["llm"] = existing["llm"]
        except: pass
        
        try:
            with open("config.json", "w", encoding='utf-8') as f:
                json.dump(new_config, f, indent=4)
                
            # Reload Brain
            if self.parent():
                self.parent().brain.reload_config()
                
            QMessageBox.information(self, "Saved", "Settings saved and Brain reloaded!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save config: {e}")

class AvatarWidget(QWidget):
    """Sidebar-embedded Avatar Display."""
    def __init__(self):
        super().__init__()
        self.setFixedHeight(350) 
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl)
        
        # Load Base
        self.base_pix = QPixmap(os.path.join(ASSETS_DIR, "base_neutral.png"))
        self.update_face("neutral")
        
    def update_face(self, expression="neutral"):
        if not self.base_pix.isNull():
            # Scale to fit width of sidebar (approx 230px)
            scaled = self.base_pix.scaledToWidth(230, Qt.TransformationMode.SmoothTransformation)
            
            # Simplified overlay logic for now
            if expression != "neutral":
                print(f"DEBUG: Expression switched to {expression}")
                # Ideally we overlay face assets here if layers exist
                    
            self.lbl.setPixmap(scaled)

class WorkerThread(QThread):
    """Async worker to handle blocking Brain tasks (Think/Speak/Listen)."""
    result_ready = pyqtSignal(str, str) # type (response/listen), content

    def __init__(self, brain, task_type, payload=None):
        super().__init__()
        self.brain = brain
        self.task_type = task_type
        self.payload = payload

    def run(self):
        if self.task_type == "think":
            response_text, actions = self.brain.think(self.payload)
            # Emit structured result: "response", json_dump_of_content
            # To avoid changing signal signature, we pack it
            res_payload = json.dumps({"text": response_text, "actions": actions})
            self.result_ready.emit("response", res_payload)
            
            # Auto-speak after thinking
            asyncio.run(self.brain.speak(response_text))
            
        elif self.task_type == "listen":
            text = self.brain.listen()
            if text:
                self.result_ready.emit("user_audio", text)
            else:
                self.result_ready.emit("error", "No speech detected.")

class ChatBubble(QFrame):
    """Custom Widget for Chat Messages with Media Support."""
    def __init__(self, text, is_user=True, image_path=None):
        super().__init__()
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5) 
        self.setLayout(layout)
        
        # Content Container (Vertical for Text + Image)
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. Image (If present)
        if image_path and os.path.exists(image_path):
            img_lbl = QLabel()
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaledToHeight(300, Qt.TransformationMode.SmoothTransformation)
                img_lbl.setPixmap(scaled)
                img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                content_layout.addWidget(img_lbl)
        
        # 2. Text
        self.lbl = QLabel(text)
        self.lbl.setWordWrap(True)
        self.lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl.setFont(QFont("Segoe UI", 11))
        self.lbl.setStyleSheet("border: none; background: transparent;") # Reset style for label inside frame
        content_layout.addWidget(self.lbl)
        
        # Styling Wrapper
        if is_user:
            layout.addStretch()
            content_frame.setStyleSheet("""
                background-color: #313244; 
                color: #cdd6f4;
                border-radius: 15px;
            """)
            layout.addWidget(content_frame)
        else:
            content_frame.setStyleSheet("""
                background-color: #89b4fa;
                color: #1e1e2e; 
                border-radius: 15px;
            """)
            layout.addWidget(content_frame)
            layout.addStretch()

class EiraChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eira Chat - Alexandria Edition")
        self.resize(1100, 750) 
        
        # Initialize Brain
        self.brain = EiraChatBrain()
        self.voice_mode = False
        self.processing = False
        
        # Load Styles
        self._load_styles()
        
        # Main Layout setup
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- SIDEBAR (Left) ---
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        
        lbl_title = QLabel("EIRA CHAT")
        lbl_title.setObjectName("header")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(lbl_title)
        
        # Controls
        sidebar_layout.addWidget(QLabel("Language:"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["Spanish (Español)", "English", "Japanese (日本語)"])
        self.combo_lang.currentIndexChanged.connect(self.change_language)
        self.combo_lang.currentIndexChanged.connect(self.change_language)
        sidebar_layout.addWidget(self.combo_lang)
        
        # Settings Button
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.btn_settings) 
        
        # --- NEW AVATAR WIDGET ---
        sidebar_layout.addSpacing(10)
        self.avatar = AvatarWidget()
        sidebar_layout.addWidget(self.avatar)
        
        sidebar_layout.addStretch()
        
        lbl_info = QLabel("Powered by\nLiquid AI 2.5\n& Ollama")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_info.setStyleSheet("color: #6c7086; font-size: 10px;")
        sidebar_layout.addWidget(lbl_info)
        
        main_layout.addWidget(sidebar)
        
        # --- CHAT AREA (Right) ---
        chat_container = QWidget()
        chat_container.setObjectName("chat_container")
        chat_layout = QVBoxLayout(chat_container)
        
        # 1. Scroll Area for Messages
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        
        chat_layout.addWidget(self.scroll)
        
        # 2. Input Area
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.voice_btn = QPushButton("🎤")
        self.voice_btn.setFixedSize(40, 40)
        self.voice_btn.setObjectName("voice_btn_off")
        self.voice_btn.clicked.connect(self.toggle_voice_mode)
        input_layout.addWidget(self.voice_btn)
        
        self.txt_input = QTextEdit()
        self.txt_input.setPlaceholderText("Message Eira...")
        self.txt_input.setFixedHeight(50)
        self.txt_input.installEventFilter(self) # For Enter key
        input_layout.addWidget(self.txt_input)
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setObjectName("send_btn")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        chat_layout.addWidget(input_frame)
        main_layout.addWidget(chat_container)

        # Welcome Message
        self.add_bubble("Hola. Soy Eira. ¿En qué te ayudo hoy?", is_user=False)

    def _load_styles(self):
        try:
            with open("eira_style.qss", "r") as f:
                self.setStyleSheet(f.read())
        except: pass

    def change_language(self, index):
        codes = ["es", "en", "ja"]
        lang = codes[index]
        self.brain.set_language(lang)
        self.add_bubble(f"<i>Language switched to {lang.upper()}.</i>", is_user=False)

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def toggle_voice_mode(self):
        self.voice_mode = not self.voice_mode
        if self.voice_mode:
            self.voice_btn.setObjectName("voice_btn_on")
            self.listen_loop() # Start Listening
        else:
            self.voice_btn.setObjectName("voice_btn_off")
        
        # Reload style to update button color
        self._load_styles()

    def listen_loop(self):
        if not self.voice_mode or self.processing: return
        
        self.worker = WorkerThread(self.brain, "listen")
        self.worker.result_ready.connect(self.handle_voice_result)
        self.worker.start()

    def handle_voice_result(self, type, content):
        if type == "user_audio":
            self.add_bubble(content, is_user=True)
            self.process_input(content)
        elif type == "error":
            # If error (silence), just try again if voice mode is still on
            if self.voice_mode:
                self.listen_loop()

    def eventFilter(self, obj, event):
        if obj == self.txt_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def send_message(self):
        text = self.txt_input.toPlainText().strip()
        if not text: return
        
        self.add_bubble(text, is_user=True)
        self.txt_input.clear()
        self.process_input(text)

    def process_input(self, text):
        self.processing = True
        self.add_bubble("...", is_user=False) # Temp loading bubble
        
        self.worker = WorkerThread(self.brain, "think", text)
        self.worker.result_ready.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, type, content):
        # Remove "..." bubble (last item)
        last_item = self.scroll_layout.itemAt(self.scroll_layout.count() - 1)
        if last_item and last_item.widget().lbl.text() == "...":
            last_item.widget().deleteLater()
            
        final_text = content
        media_path = None
        
        if type == "response":
            try:
                data = json.loads(content)
                final_text = data["text"]
                actions = data.get("actions", {}) # Expecting dict or list
                
                # Handle Dict (new V5 structure) or List (legacy)
                if isinstance(actions, list):
                    action_list = actions
                else:
                    action_list = actions.get('visual', [])
                    media_path = actions.get('media_path', None)
                
                # Update embedded avatar
                if action_list:
                    if "happy" in action_list[0]: self.avatar.update_face("happy")
                    elif "think" in action_list[0]: self.avatar.update_face("thinking")
                    elif "surprise" in action_list[0]: self.avatar.update_face("surprise")
            except:
                pass 
            
        self.add_bubble(final_text, is_user=False, image_path=media_path)
        self.processing = False
        
        if self.voice_mode:
            self.listen_loop()

    def add_bubble(self, text, is_user, image_path=None):
        bubble = ChatBubble(text, is_user, image_path)
        self.scroll_layout.addWidget(bubble)
        # Auto scroll to bottom
        QTimer_singleShot = 100 
        # self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()) (Needs delay)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        # Style
        app.setStyle("Fusion")
        window = EiraChatWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"\n❌ CRITICAL UI CRASH: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to Exit...")
