from django.contrib import admin
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('superadmin/', super_admin , name='superadmin_dashboard'),

    # public urls ----------------------------------------------------------------


    path('', home, name="home"),
    path("about/", about, name="about"),
    path("services/", services, name="services"),
    path("contact/", contact, name="contact"),
    path("gallery/", gallery, name="gallery"),
    path("check_username_availability/", check_username_availability,
         name="check_username_availability"),
    path("check_email_availability", check_email_availability,
         name="check_email_availability"),
    path("check_mobile_availability", check_mobile_availability,
         name="check_mobile_availability"),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    path('reset_password/', reset_password, name='reset_password'),
    path('reset/<uidb64>/<token>/', reset_confirm, name='reset_confirm'),

    

    path('ajax/load_branches/', load_branches, name='load_branches'),
     path('ajax/load_years/', load_years, name='load_years'),
     path('ajax/load_subjects/', load_subjects, name='load_subjects'),

     path('save_enquiry/', save_enquiry, name="save_enquiry"),

    
    


# student urls---------------------------------------------
 

    path("student/dashboard/", StudentViews.dashboard, name="student_dashboard"),
    path("student/profile/", StudentViews.profile, name="student-profile"),
    path("student/study_material/", StudentViews.study_material, name="study_material"),
    path("student/doubt_session/", StudentViews.doubt_session, name="doubt_session"),
    path("student/register_complaint/", StudentViews.register_complaint, name="register_complaint"),
    path("student/feedbacks/", StudentViews.feedbacks, name="feedbacks"),
    path("student/assesments/", StudentViews.assesments, name="assesments"),
    path("student/lectures/", StudentViews.lectures, name="lectures"),
    path("student/update_profile", StudentViews.update_profile, name="update_profile"),
    path("student/notifications/", StudentViews.read_notifications, name="notifications"),
  

    # guest urls ----------------------------------------------------------------

    path("guest/dashboard/", GuestViews.dashboard, name="guest_dashboard"),
    path("guest/admission_apply/", GuestViews.admission_apply, name="admission_apply"),
    path("guest/drop_admission/", GuestViews.drop_admission, name="drop_admission"),
    path("guest/teaching_apply/", GuestViews.teaching_apply, name="teaching_apply"),

    path("guest/profile/", GuestViews.profile, name="guest_profile"),
    path("guest/study_material/", GuestViews.study_material, name="guest_study_material"),
    path("guest/feedbacks/", GuestViews.feedbacks, name="guest_feedbacks"),
    path("guest/lectures/", GuestViews.lectures, name="guest_lectures"),
    path("guest/assessment", GuestViews.assessment, name="guest_assessment"),
    path("guest/update_profile", GuestViews.update_profile, name="guest_update_profile"),




    # teacher urls --------------------------------
    path("teacher/dashboard/", TeacherViews.dashboard, name="teacher_dashboard"),
    path("teacher/delete_profile/<int:id>/", AdminViews.delete_user, name="delete_profile"),
    path("teacher/upload_studymaterial",TeacherViews.upload_studymaterial, name="upload_studymaterial_teacher"),
    path("teacher/upload_lectures",TeacherViews.upload_lectures, name="upload_lectures_teacher"),
    path("teacher/upload_assesments",TeacherViews.upload_assesments, name="upload_assesments_teacher"),
    path('teacher/add_intrested_subjects/', TeacherViews.add_intrested_subjects, name='add_intrested_subjects'),
    path('teacher/delete_intrested_subjects/<int:subject_id>/', TeacherViews.delete_intrested_subjects, name='delete_intrested_subjects'),
    path('teacher/profile/', TeacherViews.profile, name='teacher_profile'),
    path('teacher/update_profile/', TeacherViews.update_profile, name='update_profile_teacher'),




    # admin urls ----------------------------------
    path("admin/dashboard/", AdminViews.dashboard, name="admin_dashboard"),
    path("admin/manage_user/", AdminViews.manage_user, name="manage_user"),
    path("admin/edit_user/<int:id>/", AdminViews.edit_user, name="edit_user"),
    path("admin/manage_student/", AdminViews.manage_student, name="manage_student"),
    path("admin/manage_teacher/", AdminViews.manage_teacher, name="manage_teacher"),
    path("admin/manage_admin/", AdminViews.manage_admin, name="manage_admin"),
    path("admin/upload_studymaterial",AdminViews.upload_studymaterial, name="upload_studymaterial"),
    path("admin/upload_lectures",AdminViews.upload_lectures, name="upload_lectures"),
    path("admin/upload_assesments",AdminViews.upload_assesments, name="upload_assesments"),
    path("admin/delete_study_material/<int:id>/",AdminViews.delete_study_material, name="delete_study_material"),
    path("admin/delete_assessment/<int:id>/",AdminViews.delete_assessment, name="delete_assessment"),
    path("admin/delete_lecture/<int:id>/",AdminViews.delete_lecture, name="delete_lecture"),
    path("admin/view_complaint",AdminViews.view_complaint, name="view_complaint"),
    path("admin/view_enquries",AdminViews.view_enquries, name="view_enquries"),
    path("admin/view_feedback",AdminViews.view_feedback, name="view_feedback"),
    path("admin/add_notification",AdminViews.add_notification, name="add_notification"),
    path("admin/delete_user/<int:id>/",AdminViews.delete_user, name="delete_user"),
    path("admin/delete_student/<int:id>/",AdminViews.delete_student, name="delete_student"),
    path("admin/delete_teacher/<int:id>/",AdminViews.delete_teacher, name="delete_teacher"),
    path("admin/delete_admin/<int:id>/",AdminViews.delete_admin, name="delete_admin"),
    path("admin/edit_student/<int:id>/",AdminViews.edit_student, name="edit_student"),
    path ("admin/delete_notification/<int:id>/",AdminViews.delete_notification, name="delete_notification"),
    path("admin/verify_user/<int:id>/",AdminViews.verify_user, name="verify_user"),
    path("admin/verify_teacher/<int:id>/", AdminViews.verify_teacher, name="verify_teacher"),
    path("admin/verify_admin/<int:id>/", AdminViews.verify_admin, name="verify_admin"),
    
    



    path('admin/add_programs/', AdminViews.add_programs, name='add_programs'),
    path('admin/delete_program/<int:program_id>/', AdminViews.delete_program, name='delete_program'),
    path('admin/add_branches/<int:program_id>/', AdminViews.add_branches, name='add_branches'),
    path('admin/delete_branch/<int:branch_id>/', AdminViews.delete_branch, name='delete_branch'),
    path('admin/add_years/<int:program_id>/<int:branch_id>/', AdminViews.add_years, name='add_years'),
    path('admin/delete_year/<int:year_id>/', AdminViews.delete_year, name='delete_year'),
    path('admin/add_fees/<int:program_id>/<int:branch_id>/<int:year_id>/', AdminViews.add_fees, name='add_fees'),
    path('admin/delete_fees/<int:fee_id>/', AdminViews.delete_fees, name='delete_fees'),
    path('admin/add_entrance/<int:program_id>/<int:branch_id>/<int:year_id>/', AdminViews.add_entrance, name='add_entrance'),
    path('admin/delete_entrance/<int:subject_id>/', AdminViews.delete_subject, name='delete_entrance'),
    path('admin/add_subjects/<int:program_id>/<int:branch_id>/<int:year_id>/', AdminViews.add_subjects, name='add_subjects'),
    path('admin/delete_subject/<int:subject_id>/', AdminViews.delete_subject, name='delete_subject'),
    path('admin/add_admission_eligibility/', AdminViews.add_admission_eligibility, name='add_admission_eligibility'),
    path('admin/add_admission_eligibility_save/<int:student_id>/', AdminViews.add_admission_eligibility_save, name='add_admission_eligibility_save'),
    path('admin/add_entrance_exam_score/<int:student_id>/', AdminViews.add_entrance_exam_score, name='add_entrance_exam_score'),
    path('admin/students_admission_verification/', AdminViews.students_admission_verification, name='students_admission_verification'),
    path('admin/verify_admission/<int:student_id>/', AdminViews.verify_admission, name='verify_admission'),
    path('admin/add_gallery', AdminViews.add_gallery, name='add_gallery'),


]