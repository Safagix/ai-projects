import traceback
try:
    import eira_brain
    print("SUCCESS: eira_brain imported")
except ImportError:
    print("ERROR: Could not import eira_brain")
    traceback.print_exc()
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
