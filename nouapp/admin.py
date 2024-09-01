from django.contrib import admin

# Register your models here.
from .models import User, Student, Teacher, Admin 
from .models import Feedback ,Complaint
from .models import StudyMaterial ,Assesment, Lecture,Notification

from .models import Year,Branch,Program,Enquiry
# USM :> Upload Study Material 
# UAS :> Upload Asignment
# Upload Lecture

admin.site.register(User)

admin.site.register(Student)

admin.site.register(Teacher)

admin.site.register(Admin)
# admin
admin.site.register(StudyMaterial)
admin.site.register(Assesment)
admin.site.register(Lecture)
admin.site.register(Notification)

# user

admin.site.register(Feedback)
admin.site.register(Complaint)

# guest
admin.site.register(Enquiry)

# daynamic select   
admin.site.register(Program)
admin.site.register(Branch)
admin.site.register(Year)
