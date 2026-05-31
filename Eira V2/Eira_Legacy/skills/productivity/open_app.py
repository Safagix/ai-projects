
# Abstract Base Class for Skills if needed, or just simple functions.
# For simplicity and Pythonic style, we can just use functions or simple classes.

def execute(params):
    """
    Executes the 'Open App' skill.
    Expected params: App name (str)
    """
    import os
    import platform
    
    app_name = params.lower().strip()
    print(f"Skill [Productivity]: Opening {app_name}...")
    
    if platform.system() == "Windows":
        if "spotify" in app_name:
            os.system("start spotify")
            return "Abriendo Spotify."
        elif "chrome" in app_name or "navegador" in app_name:
            os.system("start chrome")
            return "Abriendo Google Chrome."
        elif "notepad" in app_name or "bloc de notas" in app_name:
            os.system("start notepad")
            return "Abriendo el Bloc de Notas."
        elif "calculator" in app_name or "calculadora" in app_name:
            os.system("calc")
            return "Abriendo la calculadora."
        else:
            # Generic try
            try:
                os.system(f"start {app_name}")
                return f"Intentando abrir {app_name}."
            except:
                return f"No pude encontrar la aplicación {app_name}."
    else:
        return "Lo siento, solo sé abrir apps en Windows por ahora."
