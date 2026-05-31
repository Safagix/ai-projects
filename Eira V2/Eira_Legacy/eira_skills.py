import os
import webbrowser
import subprocess
import time

class EiraSkills:
    """
    Hands for the Digital Soul.
    Executes actual commands on the Windows Host.
    """
    
    def __init__(self):
        # Common App Paths (Can be expanded)
        self.app_map = {
            "spotify": "spotify", # Usually in PATH or Start
            "chrome": "chrome",
            "notepad": "notepad",
            "calculator": "calc",
            "explorer": "explorer",
            "cmd": "cmd",
            "code": "code", # VS Code
        }

    def execute_skill(self, command_tag):
        """
        Parses a command tag like '[[OPEN: spotify]]' or '[[SEARCH: quantum mechanics]]'
        Returns a text response for Eira to say.
        """
        print(f"⚙️ EXECUTING SKILL: {command_tag}")
        
        try:
            # 1. CLEANUP INPUT
            content = command_tag.replace("[[", "").replace("]]", "").strip()
            
            # 2. PARSE ACTION
            if content.startswith("OPEN:"):
                app_name = content.split(":", 1)[1].strip().lower()
                return self.open_program(app_name)
                
            elif content.startswith("SEARCH:"):
                query = content.split(":", 1)[1].strip()
                return self.web_search(query)
                
            elif content.startswith("SYSTEM:"):
                action = content.split(":", 1)[1].strip().lower()
                # Basic system controls could go here (Volume etc)
                return "Comando de sistema no implementado aún."
                
            else:
                return "Comando desconocido."
                
        except Exception as e:
            print(f"❌ Skill Error: {e}")
            return f"Falló la ejecución del comando: {e}"

    def open_program(self, app_name):
        """Opens a program using Windows 'start' command."""
        try:
            # Special Cleanups
            if "google" in app_name or "chrome" in app_name: target = "chrome"
            elif "spotify" in app_name: target = "spotify"
            elif "bloc de notas" in app_name: target = "notepad"
            elif "calculadora" in app_name: target = "calc"
            elif "vscode" in app_name or "visual studio" in app_name: target = "code"
            else: target = app_name

            print(f"🚀 Launching: {target}")
            # 'start' command in shell is robust for registered apps
            os.system(f"start {target}")
            return f"Abriendo {target}."
            
        except Exception as e:
            return f"No pude abrir {app_name}. Error: {e}"

    def web_search(self, query):
        """Opens default browser with Google search."""
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Buscando '{query}' en la red."
