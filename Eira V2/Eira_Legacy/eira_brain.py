import asyncio
import edge_tts
import os
import speech_recognition as sr
import pygame
import time
import requests
import json
import re
import noisereduce as nr
import numpy as np

# --- CONFIGURATION FOR EIRA V2 ---
# AUTOMATION OVERRIDE: User is running LM Studio manually on 1234.
USE_LM_STUDIO = True 
LM_STUDIO_URL = "http://localhost:1234/v1"
TARGET_MODEL = "qwen2.5:3b"

ANYTHING_LLM_URL = "http://localhost:3001/api/v1" 
ANYTHING_LLM_KEY = os.environ.get("ANYTHING_LLM_KEY", "YOUR_API_KEY") 

# Import the new Skill Manager
from skills.skill_manager import SkillLoader

if USE_LM_STUDIO:
    from openai import OpenAI
    # Point to OLLAMA pretending to be LM Studio
    client = OpenAI(base_url=LM_STUDIO_URL, api_key="ollama")

class AnythingLLMClient:
    """Connector for AnythingLLM RAG features"""
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def query(self, prompt):
        # Placeholder for actual AnythingLLM API chat endpoint
        pass

class EiraAssistant:
    def __init__(self):
        print("\n🔵 EIRA V3 (MODULAR BRAIN) INITIALIZING...")
        
        # 0. Setup Paths to ProjectStarlight
        import sys
        # FIXED PATH: ../../ProjectStarlight (Sibling of Eira V2)
        starlight_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ProjectStarlight"))
        if starlight_path not in sys.path:
            sys.path.append(starlight_path)
            
        # 1. Start Mobile Server & Load New Brain
        try:
            from skills.system.server import server
            print("🧠 BRAIN: Connecting to Modular Hybrid Router...")
            
            # Start the Web Server (Phone connectivity)
            server.start_server_thread()
            
            # Hook into the Brain
            self.router = server.router
            self.loader = server.loader
            print("🚀 Mobile Server: ONLINE (http://192.168.0.x:5000)")
            
        except ImportError as e:
            print(f"❌ CRITICAL ERROR: Could not load Modular Brain: {e}")
            print(f"   Debug Path: {starlight_path}")
            self.router = None

        # 2. Setup Ears & Mouth (Preserve Legacy Hardware)
        self.recognizer = sr.Recognizer()
        try:
            pygame.mixer.init()
            print("🔊 Audio System: Online")
        except Exception as e:
            print(f"🔊 Audio System Error: {e}")
            
        self.cleanup_temp_files()

    # --- MULTILINGUAL STATE (From Eira Poliglota) ---
        self.current_lang = "es"
        self.voice_id = "es-MX-DaliaNeural"
        self.stt_lang = "es-ES"

    def cleanup_temp_files(self):
        try:
            for file in os.listdir():
                if file.startswith("voice_") and file.endswith(".mp3"):
                    try: os.remove(file)
                    except: pass
        except: pass

    def load_memory(self):
        return "" 

    async def speak(self, text):
        """Synthesize text to speech using current language voice."""
        if not text:
            print("⚠️ speak() called with empty text")
            return

        # --- TERMINAL CHAT LOG (User Request) ---
        print(f"\n🗣️ Eira: {text}\n")

        import random
        # We also save a 'last_response.mp3' for the user to inspect
        debug_audio_path = os.path.abspath("last_response.mp3")
        
        output_file = f"voice_{int(time.time())}_{random.randint(0,1000)}.mp3"
        absolute_path = os.path.abspath(output_file)
        
        try:
            # Use dynamic voice_id configured by language state
            communicate = edge_tts.Communicate(str(text), self.voice_id)
            await communicate.save(output_file)
            
            # play
            pygame.mixer.music.load(absolute_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            time.sleep(0.3)
            
            # Update Debug File (Copy)
            import shutil
            shutil.copy(absolute_path, debug_audio_path)
            
        except Exception as e:
            print(f"❌ Audio Error: {e}")
        
        try:
            if os.path.exists(output_file): os.remove(output_file)
        except: pass

    def listen(self):
        """Listen using current STT language."""
        with sr.Microphone() as source:
            print(f"Escuchando ({self.current_lang.upper()})...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                # Increased timeout slightly
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                text = self.recognizer.recognize_google(audio, language=self.stt_lang)
                print(f"User: {text}")
                return text
            except Exception:
                return None

    def think(self, user_text):
        """Process text through Hybrid Router with Language Context."""
        if not user_text: return None

        # 1. LANGUAGE SWITCHING LOGIC (Running locally in the Body)
        text_lower = user_text.lower()
        
        # ES -> EN
        if any(chk in text_lower for chk in ["switch to english", "cambia a ingl", "cambiar a ingl", "in english"]):
            self.current_lang = "en"
            self.voice_id = "en-US-JennyNeural"
            self.stt_lang = "en-US"
            return "Understood. Switching to English mode."
            
        # EN -> ES
        elif any(chk in text_lower for chk in ["switch to spanish", "cambia a espa", "cambiar a espa", "en español"]):
            self.current_lang = "es"
            self.voice_id = "es-MX-DaliaNeural"
            self.stt_lang = "es-ES"
            return "Entendido. Volviendo al español."

        # 2. CHECK CONNECTION
        if not self.router: 
            return "Lo siento, mi cerebro modular no está conectado."
        
        print(f"🤔 Thinking about: '{user_text}'")
        
        # 3. PREPARE PROMPT WITH LANGUAGE INSTRUCTION
        # We inject the language constraint so the LLM respects it
        lang_instruction = ""
        if self.current_lang == "en":
            lang_instruction = "IMPORTANT: Answer in English. "
        else:
            lang_instruction = "IMPORTANTE: Responde en Español. "
            
        full_query = f"{lang_instruction} {user_text}"
        
        try:
            # Delegate to the new Router
            result = self.router.process(full_query)
            
            if result['type'] == 'skill':
                intent = result['intent']
                module = self.loader.get_action_module(intent['domain'], intent['skill'], intent['action'])
                if module:
                    exec_result = module.run({'utterance': user_text})
                    return exec_result.get('text', "Accion ejecutada.")
                return "Encontré la habilidad pero no el módulo."
                
            elif result['type'] == 'chat':
                return result['response']
                
            return "No estoy segura de qué hacer."
            
        except Exception as e:
            return f"Error en el cerebro: {e}"
