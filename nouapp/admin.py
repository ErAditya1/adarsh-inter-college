from django.contrib import admin
from .models import *

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'rollno', 'program', 'branch', 'year', 'admission_status', 'is_verified')
    search_fields = ('user__username', 'rollno', 'aadhar_number')
    list_filter = ('program', 'branch', 'year', 'admission_status')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'qualification', 'specialization', 'experience_years', 'designation', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('qualification', 'specialization', 'is_active')

@admin.register(Admin)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'office', 'is_verified')
    search_fields = ('user__username', 'employee_id', 'office')
    list_filter = ('is_verified',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject_code', 'year',  'branch', 'program',)
    search_fields = ('name', 'subject_code',)
    list_filter = ('year', 'program', 'branch')

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch_code', 'program')
    search_fields = ('name', 'branch_code')
    list_filter = ('program',)

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch')
    list_filter = ('branch',)

@admin.register(FeesType)
class FeesTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'year','branch','program')
    list_filter = ('year','program', 'branch')

@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_type', 'amount_paid', 'payment_method', 'payment_date')
    search_fields = ('student__rollno', 'fee_type__name', 'transaction_id')
    list_filter = ('fee_type', 'payment_method')

@admin.register(Entrance)
class EntranceAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'duration', 'year',  'branch','program')
    list_filter = ('year',  'program', 'branch')

@admin.register(TeacherInterest)
class TeacherInterestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'program', 'branch', 'year')
    list_filter = ('program', 'branch', 'year', 'subject')

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('subject', 'file_name', 'program', 'branch', 'year', 'is_protected')
    list_filter = ('program', 'branch', 'year', 'is_protected')

@admin.register(Assesment)
class AssesmentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'file_name', 'program', 'branch', 'year', 'is_protected')
    list_filter = ('program', 'branch', 'year', 'is_protected')

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('subject', 'file_name', 'link', 'program', 'branch', 'year', 'is_protected')
    list_filter = ('program', 'branch', 'year', 'is_protected')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'created_at')
    search_fields = ('student__rollno', 'subject')
    list_filter = ('created_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'created_at')
    search_fields = ('student__rollno', 'subject')
    list_filter = ('created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('admin', 'text', 'link', 'created_at')
    list_filter = ('created_at',)

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'created_at')
    search_fields = ('name', 'email', 'mobile')
    list_filter = ('created_at',)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)

