
class SkillLoader:
    def __init__(self):
        self.skills = {}
        self.load_skills()
    
    def load_skills(self):
        """Dynamic loading could go here, for now we map manually or use simple import"""
        # In a full Leon implementation, this would scan folders.
        # For Eira V2, we import explicitly for stability first.
        from skills.productivity import open_app
        from skills.system import lock_pc
        from skills.system import time_date
        
        self.skills['open_app'] = open_app
        self.skills['lock_pc'] = lock_pc
        self.skills['time_date'] = time_date
        self.skills['show_time'] = time_date # Alias
        self.skills['show_date'] = time_date # Alias
        
    def execute_skill(self, skill_name, params=None):
        if skill_name in self.skills:
            return self.skills[skill_name].execute(params)
        return "Habilidad no encontrada."
        