import asyncio
import sys
import os

# Ensure we can import from local directory even if run from elsewhere
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from eira_brain import EiraAssistant
except ImportError:
    print("CRITICAL ERROR: Could not import Eira Brain.")
    input("Press Enter to exit...")
    sys.exit(1)

async def voice_feedback(eira, text):
    """Async wrapper to speak without blocking the main loop excessively."""
    await eira.speak(text)

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("===================================================")
    print("      EIRA TRAINING CONSOLE (CHAT MODE)            ")
    print("===================================================")
    print("Initializing Brain...")
    
    try:
        eira = EiraAssistant()
        print("\n🧠 MEMORY LOADED:")
        print(eira.load_memory())
        print("---------------------------------------------------")
        print("EIRA IS READY. TYPE YOUR MESSAGE. (Type 'exit' to quit)")
        print("---------------------------------------------------")
        
        while True:
            user_input = input("\nYOU > ")
            
            # --- COMMANDS ---
            if user_input.lower() in ["exit", "quit", "salir"]:
                break
                
            if user_input.lower().startswith("/learn") or user_input.lower().startswith("/aprender"):
                # Save previous interaction
                if 'response' in locals():
                    concept = user_input.replace("/learn", "").replace("/aprender", "").strip()
                    if not concept: concept = f"User asked: '{last_user_input}' -> Eira answered: '{response}'"
                    
                    success = eira.remember(concept)
                    if success: print("✅ Lección guardada en Neural_Patterns.md")
                    continue
                else:
                    print("⚠️ No hay nada que aprender aún. Habla primero.")
                    continue

            if not user_input.strip():
                continue

            # Store for learning context
            last_user_input = user_input

            print("Eira is thinking...")
            response = eira.think(user_input)
            
            print(f"\nEIRA > {response}")
            
            # Speak Response
            asyncio.run(voice_feedback(eira, response))
            
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\nTraining Session Ended.")
    input("Press Enter to close.")

if __name__ == "__main__":
    main()
