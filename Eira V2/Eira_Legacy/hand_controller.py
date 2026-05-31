import cv2
import numpy as np
import math
import pyautogui
import time
# We will use cvzone's HandTrackingModule for simplicity as it was in your original idea
from cvzone.HandTrackingModule import HandDetector

# --- CONFIGURATION ---
CAM_W, CAM_H = 1280, 720
SCREEN_W, SCREEN_H = pyautogui.size()
FRAME_REDUCTION = 100  # Frame reduction to avoid reaching edges (makes it easier to reach corners)
SMOOTHING = 3          # REDUCED from 5 to 3 for snappier response (less floaty)

class StarlightHandController:
    def __init__(self):
        # --- OPTIMIZATION 1: REMOVE PYAUTOGUI LATENCY ---
        # Default is 0.1s (100ms) which CAPS fps at 10. 
        # Setting to 0 removes the delay completely.
        pyautogui.PAUSE = 0 
        pyautogui.FAILSAFE = False # Prevents crashing if mouse hits corner
        
        # Initialize Camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, CAM_W)
        self.cap.set(4, CAM_H)
        
        # Initialize Detector
        self.detector = HandDetector(maxHands=1, detectionCon=0.7)
        
        # Variables for Smoothing
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        
        print("Starlight Hand Controller Initialized...")
        print("Gestures: Index Up = Move | Index+Thumb Pinch = Left Click | Middle+Thumb Pinch = Right Click")

    def run(self):
        dragging = False 
        scrolling = False
        
        # System State
        self.paused = False
        self.last_toggle_time = 0
        
        # Hand Locking Variables
        self.locked_hand_id = None
        
        while True:
            success, img = self.cap.read()
            if not success:
                print("Failed to read camera.")
                continue
                
            img = cv2.flip(img, 1)
            
            # Detect Hands
            hands, img = self.detector.findHands(img, flipType=False)
            
            # --- TOGGLE PAUSE LOGIC (Spider-Man Gesture) 🤟 ---
            # We check this BEFORE locking logic to allow unlocking with any hand
            if hands:
                # Check the first hand for the toggle gesture
                # We can use any hand to unlock usually
                hand_toggle = hands[0]
                fingers_toggle = self.detector.fingersUp(hand_toggle)
                
                # Gesture: Index (1) and Pinky (4) UP. Middle (2) and Ring (3) DOWN.
                if fingers_toggle[1] == 1 and fingers_toggle[4] == 1 and fingers_toggle[2] == 0 and fingers_toggle[3] == 0:
                    current_time = time.time()
                    if current_time - self.last_toggle_time > 2.0: # 2 seconds debounce
                        self.paused = not self.paused
                        self.last_toggle_time = current_time
                        state_msg = "PAUSED" if self.paused else "ACTIVE"
                        print(f"System State: {state_msg}")

            # Draw Status
            if self.paused:
                cv2.putText(img, "SYSTEM LOCKED (Spider-Man to Unlock)", (50, 50), 
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
                cv2.imshow("Starlight Vision", img)
                if cv2.waitKey(1) & 0xFF == 27: break
                continue # SKIP MOUSE CONTROL

            cv2.putText(img, "SYSTEM ACTIVE", (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)


            # --- HAND LOCKING LOGIC ---
            target_hand = None
            
            if hands:
                # If we were tracking a hand, try to find it again (minimize distance jump)
                if self.locked_hand_id is not None:
                    # Find the hand closest to the previous cursor position (mapped back to cam space roughly)
                    # Or simpler: consistent tracking ID from cvzone (if available) or centroid distance.
                    # Cvzone hand object has 'center'.
                    
                    min_dist = float('inf')
                    best_hand = None
                    
                    # Previous center in Camera coordinates (approx)
                    # We store self.prev_cam_x, self.prev_cam_y for this
                    if not hasattr(self, 'prev_cam_x'): self.prev_cam_x, self.prev_cam_y = CAM_W // 2, CAM_H // 2

                    for hand in hands:
                        cx, cy = hand['center']
                        dist = math.hypot(cx - self.prev_cam_x, cy - self.prev_cam_y)
                        if dist < min_dist:
                            min_dist = dist
                            best_hand = hand
                    
                    # Threshold to prevent jumping to a hand far away
                    if min_dist < 400: # Pixel distance tolerance
                        target_hand = best_hand
                    else:
                        # Lost track or jump too big -> Reset lock or pick detection[0]
                        target_hand = hands[0] 
                else:
                    # No locked hand, pick the first one
                    target_hand = hands[0]
                
                # Update locks
                self.locked_hand_id = 1 # Dummy ID since cvzone doesn't give persistent IDs easily
                self.prev_cam_x, self.prev_cam_y = target_hand['center']
            
            else:
                self.locked_hand_id = None


            # Draw Region of Interest
            cv2.rectangle(img, (FRAME_REDUCTION, FRAME_REDUCTION), 
                          (CAM_W - FRAME_REDUCTION, CAM_H - FRAME_REDUCTION), 
                          (255, 0, 255), 2)
            
            if target_hand:
                hand = target_hand
                lmList = hand["lmList"]
                
                x1, y1 = lmList[8][0], lmList[8][1]   # Index
                x2, y2 = lmList[12][0], lmList[12][1] # Middle
                x3, y3 = lmList[4][0], lmList[4][1]   # Thumb
                
                fingers = self.detector.fingersUp(hand)
                # fingers: [Thumb, Index, Middle, Ring, Pinky]

                # Coordinates Mapping
                x3_screen = np.interp(x1, (FRAME_REDUCTION, CAM_W - FRAME_REDUCTION), (0, SCREEN_W))
                y3_screen = np.interp(y1, (FRAME_REDUCTION, CAM_H - FRAME_REDUCTION), (0, SCREEN_H))
                
                # Smoothing
                self.curr_x = self.prev_x + (x3_screen - self.prev_x) / SMOOTHING
                self.curr_y = self.prev_y + (y3_screen - self.prev_y) / SMOOTHING
                self.prev_x, self.prev_y = self.curr_x, self.curr_y
                
                # --- LOGICA DE GESTOS ---
                
                # 1. SCROLL (Peace Sign / Scissors) ✌️
                # Index and Middle UP, others DOWN.
                if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                    # Calculate vertical movement relative to center or previous frame could be tricky
                    # Better aproach: Map hand Y position to Scroll Speed?
                    # Or simpler: Peace sign + Move Up = Scroll Up, Peace + Move Down = Scroll Down
                    # We use relative movement
                    
                    # Distance between Index and Middle (ensure it's not a pinch/right click)
                    dist_peace, _, _ = self.detector.findDistance((x1, y1), (x2, y2), img)
                    
                    if dist_peace > 40: # Fingers separated
                        scrolling = True
                        
                        # Calculate delta Y (Movement speed)
                        # We use raw y1 coordinate. 
                        # To scroll, we can map the Y position to speed
                        # Top of screen = Scroll Up, Bottom = Scroll Down, Center = Stop
                        
                        # Deadzone in the middle (300 to 420)
                        if y1 < 300:
                            pyautogui.scroll(20) # Scroll UP
                            cv2.putText(img, "SCROLL UP", (400, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                        elif y1 > 420:
                            pyautogui.scroll(-20) # Scroll DOWN
                            cv2.putText(img, "SCROLL DOWN", (400, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                        else:
                            cv2.putText(img, "SCROLL MODE", (400, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                # 2. DRAG (Fist) ✊
                elif fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    if not dragging:
                        pyautogui.mouseDown()
                        dragging = True
                    # Move while dragging
                    pyautogui.moveTo(self.curr_x, self.curr_y)
                    cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                
                else: 
                    # Reset States
                    if dragging:
                        pyautogui.mouseUp()
                        dragging = False
                    
                    scrolling = False

                    # 3. RIGHT CLICK (Middle + Thumb logic relaxed) 🖕
                    # Check distance between Middle (12) and Thumb (4)
                    dist_rclick, info_rclick, _ = self.detector.findDistance((x2, y2), (x3, y3), img)
                    
                    # We allow Right Click even if Index is not perfectly straight
                    # But to avoid confusion, Index should probably be UP or Relaxed.
                    if dist_rclick < 45 and fingers[2] == 1: 
                        cv2.circle(img, (info_rclick[4], info_rclick[5]), 15, (0, 255, 255), cv2.FILLED)
                        pyautogui.rightClick()
                        time.sleep(0.3)

                    # 4. LEFT CLICK (Index + Thumb) 👌
                    elif fingers[1] == 1:
                        dist_click, info_click, _ = self.detector.findDistance((x1, y1), (x3, y3), img)
                        
                        # Move mouse only if not clicking (to stabilize click)
                        if dist_click > 45:
                            pyautogui.moveTo(self.curr_x, self.curr_y)
                            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                        else:
                            # Click
                            cv2.circle(img, (info_click[4], info_click[5]), 15, (0, 255, 0), cv2.FILLED)
                            pyautogui.click()
                            time.sleep(0.2)
                            
            # Display
            cv2.imshow("Starlight Vision", img)
            
            # Exit Key
            if cv2.waitKey(1) & 0xFF == 27: # ESC
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = StarlightHandController()
    controller.run()
