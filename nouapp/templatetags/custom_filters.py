from django import template
from datetime import datetime
register = template.Library()

@register.filter
def get_attendance_status(dictionary, key_str):
    
    try:
        student_id_str, date_str = key_str.split('|')
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        key = (int(student_id_str), date_obj)
        
        return dictionary.get(key)
    except Exception as e:
        print("Error in get_attendance:", e)
        return None

