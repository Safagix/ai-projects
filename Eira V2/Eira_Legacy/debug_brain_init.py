import sys
import os
import traceback

print("🔍 DIAGNOSTIC: Testing Eira Brain Initialization...")

try:
    print("1. Attempting to import eira_brain...")
    import eira_brain
    print("   ✅ Import Successful.")
except ImportError as e:
    print(f"   ❌ IMPORT ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"   ❌ UNKNOWN ERROR DURING IMPORT: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Attempting to instantiate EiraAssistant...")
    brain = eira_brain.EiraAssistant()
    print("   ✅ Instantiation Successful.")
    print("   🧠 Brain Status: ONLINE")
except Exception as e:
    print(f"   ❌ INSTANTIATION ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

print("✅ DIAGNOSTIC COMPLETE: No critical errors found.")
