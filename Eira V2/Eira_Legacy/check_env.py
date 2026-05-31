import sys
print(f"Python Executable: {sys.executable}")
print("Checking imports...")

try:
    import cv2
    print(" [OK] cv2")
except ImportError as e:
    print(f" [FAIL] cv2: {e}")

try:
    import pygame
    print(" [OK] pygame")
except ImportError as e:
    print(f" [FAIL] pygame: {e}")

try:
    import mediapipe
    print(" [OK] mediapipe")
except ImportError as e:
    print(f" [FAIL] mediapipe: {e}")

try:
    import cvzone
    print(" [OK] cvzone")
except ImportError as e:
    print(f" [FAIL] cvzone: {e}")

try:
    import pyautogui
    print(" [OK] pyautogui")
except ImportError as e:
    print(f" [FAIL] pyautogui: {e}")

try:
    import google.generativeai
    print(" [OK] google.generativeai")
except ImportError as e:
    print(f" [FAIL] google.generativeai: {e}")

try:
    import speech_recognition
    print(" [OK] speech_recognition")
except ImportError as e:
    print(f" [FAIL] speech_recognition: {e}")

try:
    import edge_tts
    print(" [OK] edge_tts")
except ImportError as e:
    print(f" [FAIL] edge_tts: {e}")

print("Check finished.")
