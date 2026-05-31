import datetime

def execute(params=None):
    """
    Returns current time or date.
    """
    now = datetime.datetime.now()
    
    # Simple logic to handle both or specific
    # If params contain 'date', show date. Else time.
    # Actually the skill name from LLM determines it.
    
    # We can handle multiple "virtual" skills in one file or mapped via manager.
    # For now, let's assume this script handles 'show_time' and 'show_date' 
    # if mapped correctly, or we make the manager smarter.
    
    # Let's make it return a generic nice string.
    
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A %d de %B de %Y")
    
    # Basic localization mapping (optional)
    days = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    months = {
        "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
        "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
        "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }
    
    for en, es in days.items(): date_str = date_str.replace(en, es)
    for en, es in months.items(): date_str = date_str.replace(en, es)

    return f"Son las {time_str} del {date_str}."
