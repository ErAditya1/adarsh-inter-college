from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

# Custom User admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Info', {
            'fields': ('user_type', 'avatar', 'mobile', 'is_verified', 'is_detailed')
        }),
    )
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_detailed', 'is_staff')
    search_fields = ('username', 'email', 'mobile')
    list_filter = ('user_type', 'is_verified', 'is_detailed')


# Inline for student fees
class StudentFeeInline(admin.TabularInline):
    model = StudentFee
    extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'rollno', 'admission_status', 'is_eligible_for_admission', 'school_class', 'section')
    search_fields = ('rollno', 'user__username', 'user__email')
    list_filter = ('admission_status', 'school_class', 'section')
    inlines = [StudentFeeInline]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'qualification', 'specialization', 'designation', 'is_active')
    search_fields = ('user__username', 'user__email')
    list_filter = ('qualification', 'designation', 'is_active')


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'office', 'is_verified')
    search_fields = ('employee_id', 'user__username')


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class')
    list_filter = ('school_class',)


@admin.register(FeesType)
class FeesTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'school_class', 'section')
    list_filter = ('school_class', 'section')


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_type', 'amount_paid', 'payment_method', 'payment_date')
    search_fields = ('student__rollno',)


@admin.register(Entrance)
class EntranceAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'school_class', 'section')
    list_filter = ('school_class', 'section')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject_code', 'school_class', 'section')
    list_filter = ('school_class', 'section')


@admin.register(TeacherInterest)
class TeacherInterestAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'school_class', 'section')


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('subject', 'file_name', 'school_class', 'section', 'is_protected')
    list_filter = ('school_class', 'section')


@admin.register(Assesment)
class AssesmentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'file_name', 'school_class', 'section', 'is_protected')
    list_filter = ('school_class', 'section')


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('subject', 'file_name', 'school_class', 'section', 'link')
    list_filter = ('school_class', 'section')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'created_at')
    search_fields = ('student__user__username', 'subject')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'created_at')
    search_fields = ('student__user__username', 'subject')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'created_at')
    search_fields = ('name', 'email', 'mobile')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('admin', 'text', 'link', 'created_at')
    search_fields = ('text',)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):

    list_display = ('name', 'start_time', 'end_time')

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display=("day",'period', 'school_class','section', 'subject', 'teacher')
    list_filter = ('day','period','school_class','teacher','subject')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'school_class', 'section', 'submitted_by')
    list_filter = ('school_class', 'section', 'status')
    search_fields = ('student__user__username',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('role', 'date_joined')
    # search_fields = ('employee__user__username')

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('employee', 'base_salary', 'allowances', 'bonuses', 'deductions', 'tax_percent')
    list_filter = ('employee__role',)

@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status')
    list_filter = ('status', 'date')

@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'base_salary', 'allowances', 'bonuses', 'deductions', 'net_salary')
    list_filter = ('date', 'employee__role')

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('salary_payment', 'generated_on')
