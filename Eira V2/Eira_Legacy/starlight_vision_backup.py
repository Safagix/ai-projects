import cv2
import numpy as np
import math
import pyautogui
import time
from cvzone.HandTrackingModule import HandDetector

# --- CONFIGURATION ---
CAM_W, CAM_H = 1280, 720
SCREEN_W, SCREEN_H = pyautogui.size()
FRAME_REDUCTION = 100
SMOOTHING = 3

class StarlightVisionBackup:
    def __init__(self):
        # Optimization
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False
        
        # Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, CAM_W)
        self.cap.set(4, CAM_H)
        
        # Detector
        self.detector = HandDetector(maxHands=1, detectionCon=0.7)
        
        # Variables
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        self.paused = False
        self.lock_timer = 0
        
        print("--- STARLIGHT VISION (BACKUP): ONLINE ---")

    def run(self):
        dragging = False
        
        while True:
            success, img = self.cap.read()
            if not success: continue
            img = cv2.flip(img, 1)
            hands, img = self.detector.findHands(img, flipType=False)
            
            # Draw Status
            if self.paused:
                cv2.putText(img, "LOCKED", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            else:
                cv2.putText(img, "ACTIVE", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

            if hands:
                hand = hands[0]
                fingers = self.detector.fingersUp(hand)
                lmList = hand['lmList']
                x1, y1 = lmList[8][0], lmList[8][1]
                x2, y2 = lmList[12][0], lmList[12][1]
                x3, y3 = lmList[4][0], lmList[4][1]

                # --- MOUSE CONTROL ---
                if not self.paused:
                    # Move (Index Up)
                    if fingers[1] == 1 and fingers[2] == 0:
                        x3_sc = np.interp(x1, (FRAME_REDUCTION, CAM_W-FRAME_REDUCTION), (0, SCREEN_W))
                        y3_sc = np.interp(y1, (FRAME_REDUCTION, CAM_H-FRAME_REDUCTION), (0, SCREEN_H))
                        self.curr_x = self.prev_x + (x3_sc - self.prev_x) / SMOOTHING
                        self.curr_y = self.prev_y + (y3_sc - self.prev_y) / SMOOTHING
                        pyautogui.moveTo(self.curr_x, self.curr_y)
                        self.prev_x, self.prev_y = self.curr_x, self.curr_y
                        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)

                    # Click Left (Index+Thumb)
                    dist, _, _ = self.detector.findDistance((x1, y1), (x3, y3), img)
                    if dist < 30:
                        pyautogui.click()
                        time.sleep(0.2)

                    # Click Right (Middle+Thumb)
                    dist_r, _, _ = self.detector.findDistance((x2, y2), (x3, y3), img)
                    if dist_r < 40 and fingers[2] == 1:
                        pyautogui.rightClick()
                        time.sleep(0.3)
                    
                    # Scroll (Peace)
                    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                        dist_p, _, _ = self.detector.findDistance((x1, y1), (x2, y2), img)
                        if dist_p > 40:
                            if y1 < 300: pyautogui.scroll(20)
                            elif y1 > 420: pyautogui.scroll(-20)

                    # Drag (Fist)
                    if fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                        if not dragging:
                            pyautogui.mouseDown()
                            dragging = True
                        pyautogui.moveTo(self.curr_x, self.curr_y)
                    elif dragging:
                        pyautogui.mouseUp()
                        dragging = False
                    
                    # Desktop (Shaka)
                    if fingers[0] == 1 and fingers[4] == 1 and fingers[1] == 0:
                         if not hasattr(self, 'shaka_t'): self.shaka_t = 0
                         if time.time() - self.shaka_t > 2.0:
                             pyautogui.hotkey('win', 'd')
                             self.shaka_t = time.time()

                # Lock Toggle (Spider-Man)
                if fingers[1] == 1 and fingers[4] == 1 and fingers[2] == 0:
                     if not hasattr(self, 'lock_t'): self.lock_t = 0
                     if self.lock_t == 0: self.lock_t = time.time()
                     if time.time() - self.lock_t > 1.5:
                         self.paused = not self.paused
                         self.lock_t = 0
                else:
                     self.lock_t = 0

            cv2.imshow("Starlight Vision (BACKUP)", img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = StarlightVisionBackup()
    app.run()
