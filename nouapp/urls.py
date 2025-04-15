from django.contrib import admin
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('superadmin/', super_admin , name='superadmin_dashboard'),

    # public urls ----------------------------------------------------------------


    path('', home, name="home"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
    path("check_username_availability", check_username_availability,
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

    

    path('load_branches/', load_branches, name='load_branches'),
    path('load_years/', load_years, name='load_years'),
    path('save_enquiry/', save_enquiry, name="save_enquiry"),

    
    


# student urls---------------------------------------------
    path('student/add_student_details/', StudentViews.add_student_details, name="add_student_details"),
    path('student/add_student_details/load_branches/', load_branches, name='load_branches'),
    path('student/add_student_details/load_years/', load_years, name='load_years'),
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
    path('student/load_branches/', load_branches, name='load_branches'),
    path('student/load_years/', load_years, name='load_years'),
 

    # guest urls ----------------------------------------------------------------

    path("guest/dashboard/", GuestViews.dashboard, name="guest_dashboard"),
    path("guest/profile/", GuestViews.profile, name="guest_profile"),
    path("guest/study_material/", GuestViews.study_material, name="guest_study_material"),
    path("guest/feedbacks/", GuestViews.feedbacks, name="guest_feedbacks"),
    path("guest/lectures/", GuestViews.lectures, name="guest_lectures"),
    path("guest/assessment", GuestViews.assessment, name="guest_assessment"),
    path("guest/update_profile", GuestViews.update_profile, name="guest_update_profile"),




    # teacher urls --------------------------------
    path('teacher/add_teacher_details/', TeacherViews.add_teacher_details, name="add_teacher_details"),
    path("teacher/dashboard/", TeacherViews.dashboard, name="teacher_dashboard"),
    path("teacher/delete_profile/<int:id>/", AdminViews.delete_user, name="delete_profile"),
    path("teacher/upload_studymaterial",TeacherViews.upload_studymaterial, name="upload_studymaterial_teacher"),
    path("teacher/upload_lectures",TeacherViews.upload_lectures, name="upload_lectures_teacher"),
    path("teacher/upload_assesments",TeacherViews.upload_assesments, name="upload_assesments_teacher"),
    path('teacher/load_branches/', load_branches, name='load_branches'),
    path('teacher/load_years/', load_years, name='load_years'),
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
    path("admin/view_feedback",AdminViews.view_feedback, name="view_feedback"),
    path("admin/view_complaint",AdminViews.view_complaint, name="view_complaint"),
    path("admin/view_enquries",AdminViews.view_enquries, name="view_enquries"),
    path("admin/view_feedback",AdminViews.view_feedback, name="view_feedback"),
    path("admin/add_notification",AdminViews.add_notification, name="add_notification"),
    path("admin/show_programs", AdminViews.show_programs, name="show_programs"),
    path("admin/delete_user/<int:id>/",AdminViews.delete_user, name="delete_user"),
    path("admin/delete_student/<int:id>/",AdminViews.delete_student, name="delete_student"),
    path("admin/delete_teacher/<int:id>/",AdminViews.delete_teacher, name="delete_teacher"),
    path("admin/delete_admin/<int:id>/",AdminViews.delete_admin, name="delete_admin"),
    path("admin/edit_student/<int:id>/",AdminViews.edit_student, name="edit_student"),
    path ("admin/delete_notification/<int:id>/",AdminViews.delete_notification, name="delete_notification"),
    path("admin/verify_user/<int:id>/",AdminViews.verify_user, name="verify_user"),
    path("admin/verify_teacher/<int:id>/", AdminViews.verify_teacher, name="verify_teacher"),
    path("admin/verify_admin/<int:id>/", AdminViews.verify_admin, name="verify_admin"),
    
    



    path('admin/add_program/', AdminViews.add_program, name='add_program'),
    path('admin/add_branch/', AdminViews.add_branch, name='add_branch'),
    path('admin/add_year/', AdminViews.add_year, name='add_year'),
    path('admin/load_branches/', load_branches, name='load_branches'),
    path('admin/load_years/', load_years, name='load_years'),
    path('admin/edit_student/<int:id>/load_branches/', load_branchese, name='load_branches'),
    path('admin/edit_student/<int:id>/load_years/', load_yearse, name='load_years'),


]