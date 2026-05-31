import cv2
import numpy as np
import math
import pyautogui
import time
import threading
import queue
from cvzone.HandTrackingModule import HandDetector
import sys, os
from filterpy.kalman import KalmanFilter
from collections import deque
# Add path to the 'cuerpo' folder so we can import the avatar module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cuerpo"))
from eira_avatar import EiraAvatar

# Import Eira
try:
    from eira_brain import EiraAssistant
except ImportError:
    print("Eira Brain not found. Running in Vision Only mode.")
    EiraAssistant = None

# --- CONFIGURATION ---
CAM_W, CAM_H = 1280, 720
SCREEN_W, SCREEN_H = pyautogui.size()
FRAME_REDUCTION = 100
SMOOTHING = 3

# --- CODICE INNOVATIONS ---
class HandKalmanFilter:
    """Innovation: Kalman Filter to smooth hand tracking and reduce jitter"""
    def __init__(self):
        self.kf = KalmanFilter(dim_x=4, dim_z=2)  # State: [x, y, vx, vy], Measurement: [x, y]
        dt = 0.033  # ~30fps
        self.kf.F = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]])
        self.kf.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
        self.kf.Q *= 0.01
        self.kf.R *= 5
        self.kf.x = np.array([0., 0., 0., 0.])
        self.initialized = False
    
    def update(self, x, y):
        if not self.initialized:
            self.kf.x = np.array([x, y, 0., 0.])
            self.initialized = True
            return x, y
        self.kf.predict()
        self.kf.update(np.array([x, y]))
        return self.kf.x[0], self.kf.x[1]

class GestureValidator:
    """Innovation: Prevent false positives by requiring temporal persistence"""
    def __init__(self, persistence_ms=300, history_size=10):
        self.persistence_ms = persistence_ms
        self.current_gesture = "None"
        self.gesture_start_time = None
    
    def validate(self, gesture_name):
        current_time = time.time() * 1000
        if gesture_name != self.current_gesture:
            self.current_gesture = gesture_name
            self.gesture_start_time = current_time
            return None
        if current_time - self.gesture_start_time >= self.persistence_ms:
            return gesture_name
        return None

def enhance_frame(frame):
    """Innovation: Apply CV optimizations (Histogram Eq)"""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    enhanced = cv2.merge([l, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

class EiraDigitalLab:
    def __init__(self):
        # 1. Setup Vision
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, CAM_W)
        self.cap.set(4, CAM_H)
        self.detector = HandDetector(maxHands=1, detectionCon=0.7)
        
        # 2. Setup Input/Output Optimizations
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        
        # INNOVATION: Initialize Filters
        self.kalman = HandKalmanFilter()
        self.gesture_validator = GestureValidator()
        
        # 2a. Setup Qt Application (REQUIRED for Avatar)
        from PyQt6.QtWidgets import QApplication
        if QApplication.instance() is None:
            self.qt_app = QApplication(sys.argv)
        else:
            self.qt_app = QApplication.instance()

        # 3. Setup Eira (The Soul)
        try:
            self.eira = EiraAssistant() if EiraAssistant else None
        except Exception as e:
            print(f"ERROR: Eira Brain failed to initialize: {e}")
            self.eira = None
        self.eira_status = "IDLE" # IDLE, LISTENING, THINKING, SPEAKING
        self.audio_queue = queue.Queue()
        self.cmd_queue = queue.Queue()
        
        # Initialize the avatar UI
        self.avatar = EiraAvatar()
        # Ensure avatar is hidden behind main window if needed
        self.avatar.show()
        
        # States
        self.paused = False # Mouse Lock
        self.listening_mode = False # Voice Active Mode
        self.palm_start = 0

        print("--- EIRA DIGITAL LAB: SYSTEM ONLINE ---")

        # Force Window Creation
        cv2.namedWindow("EIRA DIGITAL LAB", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("EIRA DIGITAL LAB", cv2.WND_PROP_TOPMOST, 1)

        # Thread control (START LAST to avoid AttributeErrors)
        self.running = True
        self.voice_thread = threading.Thread(target=self.eira_loop, daemon=True)
        self.voice_thread.start()

    def eira_loop(self):
        """Background thread for Voice Logic to avoid freezing video."""
        while self.running:
            if self.listening_mode and self.eira:
                # Logic start
 
                try:
                    # 1. Update UI Status
                    self.eira_status = "LISTENING"
                    
                    # 2. Listen
                    text = self.eira.listen() # This blocks for 5 seconds max
                    
                    if text:
                        self.eira_status = "THINKING"
                        response = self.eira.think(text)
                        
                        self.eira_status = "SPEAKING"
                        # We run speak in a blocking way here in the thread, perfectly fine
                        # But we need an async wrapper call if speak is async def
                        # In eira_brain.py, speak IS async.
                        import asyncio
                        asyncio.run(self.eira.speak(response))
                    else:
                        pass # Noise or silence
                    
                except Exception as e:
                    print(f"ERROR in Eira loop: {e}")
                    self.eira_status = "ERROR"
                finally:
                    # Reset to IDLE after turn (or error)
                    self.listening_mode = False 
                    if self.eira_status != "ERROR": # Don't overwrite a persistent error status
                        self.eira_status = "IDLE"
            
            time.sleep(0.1)

    # --- VISUALIZER HELPERS ---
    def get_audio_level(self):
        """Simulate audio level and forward to avatar for lip‑sync."""
        # Active Listening/Speaking = High activity
        if self.eira_status == "LISTENING" or self.eira_status == "SPEAKING":
            level = np.random.randint(20, 150)
        # Idle but unmuted = Low 'alive' jitter
        elif not self.mic_muted:
            level = np.random.randint(2, 10)
        else:
            level = 0
        # Map level (0‑150) to RMS 0‑10 for avatar
        rms = int(min(max(level / 15, 0), 10))
        if hasattr(self, "avatar"):
            self.avatar.set_volume(rms)
        return level

    def draw_ui(self, img):
        """Draws the HUD and Status Indicators."""
        # Top Left: Eira Status
        
        # Color coding
        if self.eira_status == "IDLE":
            color = (200, 200, 200) # Gray
            icon = "MICRO: STANDBY"
            bar_color = (100, 100, 100)
        elif self.eira_status == "LISTENING":
            color = (0, 255, 0) # Green
            icon = "MICRO: LISTENING..."
            bar_color = (0, 255, 0)
        elif self.eira_status == "THINKING":
            color = (0, 255, 255) # Yellow/Cyan
            icon = "EIRA: THINKING..."
            bar_color = (0, 255, 255)
        elif self.eira_status == "SPEAKING":
            color = (255, 0, 255) # Purple
            icon = "EIRA: SPEAKING..."
            bar_color = (255, 0, 255)
        elif self.eira_status == "ERROR":
            color = (0, 0, 255) # Red
            icon = "MICRO: ERROR (Chk Console)"
            bar_color = (0, 0, 255)
        
        if self.mic_muted:
             icon = "MICRO: MUTED (M)"
             color = (0, 0, 255)
             bar_color = (50, 0, 0)

        # Draw Background Box for Text
        cv2.rectangle(img, (10, 10), (450, 100), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, icon, (30, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Audio Visualizer Bar
        level = self.get_audio_level()
        # Draw dynamic bars
        cv2.rectangle(img, (30, 60), (30 + level * 3, 80), bar_color, cv2.FILLED)
        cv2.rectangle(img, (30, 60), (330, 80), (255, 255, 255), 2) # Frame

        # Mute Instruction
        cv2.putText(img, "Toggle Mute: 'M' Key", (30, 95), cv2.FONT_HERSHEY_PLAIN, 1, (150, 150, 150), 1)
        
        # Mouse Lock Status
        if self.paused:
             cv2.rectangle(img, (0,0), (CAM_W, CAM_H), (0, 0, 255), 5) # Red Border
             cv2.putText(img, "SYSTEM LOCKED (Gestures Paused)", (300, 400), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    def run(self):
        dragging = False
        self.mic_muted = False
        
        while self.running:
            # 1. VISION LOOP
            # Pump Qt Events (Keep Avatar Alive)
            if hasattr(self, 'qt_app'):
                self.qt_app.processEvents()

            success, img = self.cap.read()
            if not success: continue
            img = cv2.flip(img, 1)
            
            # INNOVATION: Enhance Frame (Low Light Fix)
            img = enhance_frame(img)
            
            # Draw Hand only if ACTIVE (Hide if LOCKED)
            draw_hand = not self.paused
            hands, img = self.detector.findHands(img, flipType=False, draw=draw_hand)
            
            # 2. DRAW UI
            self.draw_ui(img)
            
            # 5. KEYBOARD CONTROLS (Moved up for 'F' Key Priority)
            key = cv2.waitKey(1)
            
            # F KEY TRIGGER (Push-to-Talk)
            if (key == ord('f') or key == ord('F')) and self.eira:
                 if not self.listening_mode:
                     self.listening_mode = True
                     print("KEY TRIGGER: Start Listening...")
                     # Visual Confirmation
                     cv2.circle(img, (CAM_W//2, CAM_H//2), 50, (0, 255, 0), cv2.FILLED)
                     cv2.putText(img, "LISTENING (KEY)", (CAM_W//2-100, CAM_H//2+80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            
            # Check if User Closed Window (X Button) OR pressed ESC
            if (cv2.getWindowProperty("EIRA DIGITAL LAB", cv2.WND_PROP_VISIBLE) < 1) or (key & 0xFF == 27):
                self.running = False
                print("🛑 SHUTDOWN: Stopping Systems...")
                break
            
            elif key == ord('m'): # Mute Toggle
                self.mic_muted = not self.mic_muted
                print(f"Mic Muted: {self.mic_muted}")
            
            # 3. HAND LOGIC
            if hands:
                hand = hands[0]
                fingers = self.detector.fingersUp(hand)
                lmList = hand['lmList']
                x1, y1 = lmList[8][0], lmList[8][1] # Index
                x2, y2 = lmList[12][0], lmList[12][1] # Middle
                x3, y3 = lmList[4][0], lmList[4][1]   # Thumb
                
                # INNOVATION: Kalman Filter for Index Finger
                x1_filtered, y1_filtered = self.kalman.update(x1, y1)
                x1, y1 = int(x1_filtered), int(y1_filtered)
                
                # A. VOICE TRIGGER (Open Palm -> 1s)
                # Only if not muted
                if fingers == [1, 1, 1, 1, 1] and not self.mic_muted:  
                     if self.eira:
                         if self.listening_mode:
                             cv2.putText(img, "VOICE: ACTIVE", (x1-60, y1-40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                             cv2.circle(img, (x1, y1), 30, (0, 255, 0), cv2.FILLED)
                         else:
                             # Timer Logic
                             if not hasattr(self, 'palm_start'): self.palm_start = 0
                             if self.palm_start == 0: self.palm_start = time.time()
                             elapsed = time.time() - self.palm_start
                             
                             # Visual Feedback
                             perc = int((elapsed/1.0)*100)
                             if perc > 100: perc = 100
                             
                             cv2.circle(img, (x1, y1), 30, (0, 255, 0), 2)
                             cv2.putText(img, f"VOICE: {perc}%", (x1-40, y1-40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
                             
                             if elapsed > 1.0:
                                 self.listening_mode = True
                                 self.palm_start = 0
                                 print("TRIGGER: Start Listening...")
                                 try:
                                     import winsound
                                     winsound.Beep(1000, 200) # High Pitch Beep
                                 except: pass
                     else:
                         cv2.putText(img, "BRAIN OFFLINE", (x1-60, y1-40), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)

                else:
                     if not self.listening_mode:
                        self.palm_start = 0

                # B. LOCK TOGGLE (Spider-Man 🤟)  
                if fingers[1] == 1 and fingers[4] == 1 and fingers[2] == 0:
                     if not hasattr(self, 'lock_cooldown'): self.lock_cooldown = 0
                     if time.time() - self.lock_cooldown < 3.0: 
                         pass
                     else:
                         if not hasattr(self, 'lock_timer'): self.lock_timer = 0
                         if self.lock_timer == 0: self.lock_timer = time.time()
                         
                         elapsed_lock = time.time() - self.lock_timer
                         msg = "UNLOCKING..." if self.paused else "LOCKING..."
                         cv2.putText(img, msg, (x1, y1-50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                         cv2.circle(img, (x1, y1), 30, (0, 0, 255), 2)
                         
                         if elapsed_lock > 1.5:
                             self.paused = not self.paused
                             self.lock_timer = 0
                             self.lock_cooldown = time.time()
                             state = "PAUSED" if self.paused else "RESUMED"
                             print(f"SYSTEM STATE: {state}")
                             try:
                                 import winsound
                                 winsound.Beep(500, 300)
                             except: pass
                else:
                     self.lock_timer = 0

                # C. MOUSE CONTROL (CODICE STRICT LOGIC)
                if not self.paused:
                   # Coordinates Mapping
                   x3_screen = np.interp(x1, (FRAME_REDUCTION, CAM_W-FRAME_REDUCTION), (0, SCREEN_W))
                   y3_screen = np.interp(y1, (FRAME_REDUCTION, CAM_H-FRAME_REDUCTION), (0, SCREEN_H))
                   
                   # Kalman Smoothing applied earlier to x1, y1 but we smooth screen coords here
                   self.curr_x = self.prev_x + (x3_screen - self.prev_x) / SMOOTHING
                   self.curr_y = self.prev_y + (y3_screen - self.prev_y) / SMOOTHING
                   self.prev_x, self.prev_y = self.curr_x, self.curr_y

                   x3, y3 = lmList[4][0], lmList[4][1]   # Thumb

                   # 1. MOVE MOUSE (Index Up, Middle Down)
                   if fingers[1] == 1 and fingers[2] == 0:
                        pyautogui.moveTo(self.curr_x, self.curr_y)
                        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
                   
                   # 2. SCROLL (Peace Sign: Index + Middle)
                   elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                        dist_peace, _, _ = self.detector.findDistance((x1, y1), (x2, y2), img)
                        if dist_peace > 40:
                            if y1 < 300: pyautogui.scroll(20)
                            elif y1 > 420: pyautogui.scroll(-20)
                            cv2.putText(img, "SCROLL", (x1, y1-20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

                   # 3. DRAG (Fist)
                   elif fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                        if not dragging:
                            pyautogui.mouseDown()
                            dragging = True
                        pyautogui.moveTo(self.curr_x, self.curr_y)
                        cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                   elif dragging:
                        pyautogui.mouseUp()
                        dragging = False

                   # 4. CLICKS (With Validation)
                   if fingers[1] == 1 and fingers[2] == 0: # Only check Left Click in Point Mode (or similar)
                        # Actually Códice checks left click even in Index Up
                        dist_l, info, _ = self.detector.findDistance((x1, y1), (x3, y3), img)
                        if dist_l < 40:
                            pyautogui.click()
                            cv2.circle(img, (info[4], info[5]), 15, (0, 255, 0), cv2.FILLED)
                            time.sleep(0.2)

                   if fingers[1] == 1 and fingers[2] == 1: # Check Right Click in Peace Mode (implicit)
                        # Right Click (Middle + Thumb)
                        dist_r, _, _ = self.detector.findDistance((x2, y2), (x3, y3), img)
                        if dist_r < 40:
                            pyautogui.rightClick()
                            cv2.circle(img, (x2, y2), 15, (0, 255, 255), cv2.FILLED)
                            time.sleep(0.3)

                   # 5. DESKTOP (Shaka 🤙)
                   if fingers[0] == 1 and fingers[4] == 1 and fingers[1] == 0:
                       if not hasattr(self, 'shaka_timer'): self.shaka_timer = 0
                       if time.time() - self.shaka_timer > 2.0:
                           pyautogui.hotkey('win', 'd')
                           self.shaka_timer = time.time()
                           cv2.putText(img, "DESKTOP", (x1, y1), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
            
             # 4. SHOW IMAGE
            cv2.imshow("EIRA DIGITAL LAB", img)

        # CLEANUP
        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ SYSTEM OFFLINE.")
        import sys
        sys.exit(0) # Force Kill to stop all threads


if __name__ == "__main__":
    lab = EiraDigitalLab()
    lab.run()
