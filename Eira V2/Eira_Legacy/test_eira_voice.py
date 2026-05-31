import asyncio
from eira_brain import EiraAssistant

async def main():
    print("--- TESTING EIRA VOICE ---")
    try:
        eira = EiraAssistant()
        print("1. Brain Initialized.")
        
        test_phrase = "Hola, soy Eira. Mis sistemas de audio están operativos."
        print(f"2. Generating Audio for: '{test_phrase}'")
        
        await eira.speak(test_phrase)
        print("3. Audio Playback Finished.")
        print("SUCCESS: Voice works!")
        
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
