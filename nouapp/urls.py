from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('superadmin/', super_admin , name='superadmin_dashboard'),

    # public urls ----------------------------------------------------------------


    path('', home, name="home"),
    path("about/", about, name="about"),
    path("contact/", contact, name="contact"),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    
    

    path('load_branches/', load_branches, name='load_branches'),
    path('load_years/', load_years, name='load_years'),
    path('save_enquiry/', save_enquiry, name="save_enquiry"),

    
    


# student urls---------------------------------------------
    path('student/add_student_details/', add_student_details, name="add_student_details"),
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
    path("guest/update_profile", GuestViews.update_profile, name="guest_update_profile"),




    # teacher urls --------------------------------
    path('teacher/add_teacher_details/', add_teacher_details, name="add_teacher_details"),
    path("teacher/dashboard/", TeacherViews.dashboard, name="teacher_dashboard"),






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
    path("admin/view_feedback",AdminViews.view_feedback, name="view_feedback"),
    path("admin/view_complaint",AdminViews.view_complaint, name="view_complaint"),
    path("admin/view_enquries",AdminViews.view_enquries, name="view_enquries"),
    path("admin/view_feedback",AdminViews.view_feedback, name="view_feedback"),
    path("admin/add_notification",AdminViews.add_notification, name="add_notification"),
    path("admin/show_programs", AdminViews.show_programs, name="show_programs"),




    path('admin/add_program/', AdminViews.add_program, name='add_program'),
    path('admin/add_branch/', AdminViews.add_branch, name='add_branch'),
    path('admin/add_year/', AdminViews.add_year, name='add_year'),
    path('admin/load_branches/', load_branches, name='load_branches'),
    path('admin/load_years/', load_years, name='load_years'),

]