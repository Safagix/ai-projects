
def execute(params=None):
    """
    Executes the 'Lock PC' skill.
    """
    import os
    import ctypes
    
    print("Skill [System]: Locking Workstation...")
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Bloqueando la estación de trabajo."
    except Exception as e:
        return f"Error al bloquear la PC: {e}"
