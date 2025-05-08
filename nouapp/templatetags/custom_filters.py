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

@register.filter
def get_item(dictionary, key):
    # print(key)
    if dictionary:

        return dictionary.get(key)
    return None

@register.filter
def get_timetable(timetable, key):
    """Return timetable[(class_id, section_id)]"""
    # print(timetable.get(key))
  
    return timetable.get(key)
