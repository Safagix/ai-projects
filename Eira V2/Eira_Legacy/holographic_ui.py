import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush

class HoloWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # --- 1. Window Configuration for "Hologram" Effect ---
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Get screen geometry to place it in the corner or center
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 400, 50, 350, 600) # Top Right Corner
        
        # --- 2. Main Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # --- 3. UI Elements ---
        
        # Title / Header
        self.lbl_title = QLabel("STARLIGHT SYSTEM")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet("color: #00FFFF; font-family: 'Segoe UI'; font-size: 16px; letter-spacing: 2px; font-weight: bold;")
        self.layout.addWidget(self.lbl_title)
        
        # Arc Reactor (Placeholder Visual)
        self.reactor_widget = ReactorWidget()
        self.layout.addWidget(self.reactor_widget)
        
        # Status Text
        self.lbl_status = QLabel("SYSTEM: ONLINE\nWAITING FOR INPUT...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: rgba(0, 255, 255, 0.8); font-family: 'Consolas'; font-size: 12px;")
        self.layout.addWidget(self.lbl_status)
        
        self.layout.addStretch()

        # Add Neon Glow Effect
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(20)
        self.glow.setColor(QColor(0, 255, 255))
        self.glow.setOffset(0, 0)
        self.central_widget.setGraphicsEffect(self.glow)

        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)
        
    def update_animation(self):
        self.reactor_widget.rotate()

class ReactorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self.angle = 0
        
    def rotate(self):
        self.angle += 2
        if self.angle >= 360: self.angle = 0
        self.update() # Trigger repaint
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center point
        center = QPoint(100, 100)
        
        # Glow color
        cyan_glow = QColor(0, 255, 255, 100)
        cyan_core = QColor(200, 255, 255)
        
        # Save context
        painter.save()
        painter.translate(center)
        painter.rotate(self.angle)
        
        # Draw Outer Ring (Rotating)
        pen = QPen(cyan_glow)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw some segments
        painter.drawArc(-80, -80, 160, 160, 0, 100 * 16)
        painter.drawArc(-80, -80, 160, 160, 120 * 16, 100 * 16)
        painter.drawArc(-80, -80, 160, 160, 240 * 16, 100 * 16)
        
        painter.restore()
        
        # Draw Core (Static pulsating or inner rotation)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(cyan_core))
        painter.drawEllipse(center, 15, 15)
        
        # Inner Ring
        pen.setWidth(4)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, 50, 50)

def main():
    app = QApplication(sys.argv)
    
    # Global stylesheet for Glassmorphism
    app.setStyleSheet("""
        QMainWindow {
            background: rgba(0, 20, 40, 150);
            border: 1px solid rgba(0, 255, 255, 0.5);
            border-radius: 15px;
        }
    """)
    
    window = HoloWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
