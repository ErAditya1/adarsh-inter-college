from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseServerError
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
import random
from .models import *
from .decorators import user_type_required
import logging
from collections import Counter , defaultdict
from datetime import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .utils import send_registration_success_email, send_password_reset_email ,send_notification_email,send_admin_registration_confirmation_email,send_admin_teacher_registration_email
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import TruncDate
from .forms import *
from django.db.models import Sum
from django.utils.timezone import now
from django.db import transaction
from django.db.models import Q
from datetime import timedelta
from django.db.models import Max


# Create your views here.
# @login_required(login_url='login')

def super_admin():
    return redirect('/superadmin/')

def home(request):
    return render(request, 'pages/home.html')

# Create your views here.
def about(request):
    return render(request, 'pages/about.html')

def services(request):
    return render(request, 'pages/services.html')



def contact(request):
    return render(request, 'pages/contact.html')

@csrf_exempt
def check_username_availability(request):
    print("Request Received")
    username = request.POST.get("username")
    print(username)
    try:
        user = User.objects.filter(username=username).exists()
        print("Checked")
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)

@csrf_exempt
def check_email_availability(request):
    
    email = request.POST.get("email")

    try:
        user = User.objects.filter(email=email).exists()
       
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)
@csrf_exempt
def check_mobile_availability(request):
    
    mobile = request.POST.get("mobile")

    try:
        user = User.objects.filter(mobile=mobile).exists()
       
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)

def get_logged_in_student(request):

    sudent = Student.objects.filter(user_id=request.user.id).exists()
    if not sudent:
        # messages.error(request, "You are not a student")
        return None
        # return redirect('login')
    return get_object_or_404(Student, user_id=request.user.id)

def get_logged_in_teacher(request):
    if not Teacher.objects.filter(user_id=request.user.id).exists():
        return None
    return get_object_or_404(Teacher, user_id=request.user.id)

def register(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        try:
            validate_password(password1)
        except ValidationError as e:
            messages.error(request, e)
            return render(request, 'registration/signup.html')
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'registration/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'registration/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'registration/signup.html')
        if User.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered!")
            return render(request, 'registration/signup.html')
        # Create the user
        password_hashed = make_password(password1)

      

        
        user = User(username=username, email=email, first_name = first_name , last_name = last_name , mobile = mobile, password= password_hashed)
        print(user)
        user.save()


        # Add success message and redirect
        messages.success(request, 'Registration successful! Please check your email for confirmation.')
        

       

        login(request, user)

       

        # Send email
        send_registration_success_email(email, username)
        
        if user.user_type == 'guest':
            
            return redirect('guest_dashboard')
        

    return render(request, 'registration/signup.html')



   

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
       
        user=authenticate(request,username=username,password=password)
        
        print("User:",user)
      
            
        if user is not None:
            print("Authenticated")
            login(request,user)

            
            
                # Redirect to a success page
            
            if user.user_type =='guest':
                return redirect('guest_dashboard')
            if user.user_type =='student':

                return redirect('student_dashboard')
            
            if user.user_type == 'admin':
                if not user.is_staff:
                    logout(request)
                    messages.error(request, 'You are not verified')
                    return redirect('login')
                return redirect('admin_dashboard')
            if user.user_type == 'teacher':
                
                if not user.is_staff:
                    logout(request)
                    messages.error(request, 'You are not verified')
                    return redirect('login')
                return redirect('teacher_dashboard')
            messages.success(request,'Login Successfully')
                
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
        

  

    return render(request, 'registration/login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = get_object_or_404(User,email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = request.build_absolute_uri(f'/reset/{uid}/{token}/')
            send_password_reset_email(user.email,user, reset_url)
            
            messages.success(request,"Reset password link has been sent ! Please Check your Email")

        except User.DoesNotExist:
            messages.error(request,'No user found with this email address.')
            

        

    return render(request, 'registration/reset_password.html')

def reset_confirm(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(User,pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None


    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            try:
                validate_password(password)
            except ValidationError as e:
                messages.error(request, e)
                return redirect("reset_confirm")

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successfully')
                return redirect('login')
                # return HttpResponse('Your password has been reset successfully.')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect("reset_confirm")
        return render(request, 'registration/confirm_reset.html')
    else:
        return HttpResponse('The password reset link is invalid, possibly because it has already been used.')





def load_sections(request):
    school_class_id = request.GET.get('school_class_id')
    sections = Section.objects.filter(school_class_id=school_class_id).all()
    return JsonResponse(list(sections.values('id', 'name')), safe=False)

def load_subjects(request):
    section_id = request.GET.get('section_id')
    subjects = Subject.objects.filter(section_id=section_id).all()
    return JsonResponse(list(subjects.values('id', 'name')), safe=False)




def save_enquiry(request):
    
    name = request.POST.get('name')
    # name = request.POST['name']
    gender = request.POST.get('gender')
    address = request.POST.get('address')
    email = request.POST.get('email')
    mobile = request.POST.get('mobile')
    text = request.POST.get('text')
    user = request.user
    if user.is_authenticated:
        pass
    else:
        user=None
    enquiry = Enquiry(user = user, name=name, gender=gender, address=address, email=email, mobile=mobile, text=text)
    enquiry.save()
    messages.success(request, 'Enquiry submitted successfully')
    return redirect('contact')


def generate_roll_number(school_class_id, section_id):
    current_year = datetime.now().year

    school_class = get_object_or_404(SchoolClass, pk=school_class_id)
    section = get_object_or_404(Section, pk=section_id)

    # Format prefix
    prefix = f"S{current_year}{school_class.id:02d}{section.id:02d}"

    # Get the latest roll number for this class and section
    last_student = Student.objects.filter(
        school_class=school_class,
        section=section,
        rollno__startswith=prefix
    ).order_by('-rollno').first()

    if last_student and last_student.rollno:
        last_number = int(last_student.rollno[-3:])  # Last 3 digits
        new_number = last_number + 1
    else:
        new_number = 1

    formatted_number = f"{new_number:03d}"
    rollno = f"{prefix}{formatted_number}"
    
    return rollno

def gallery(request):
    # Fetch all the images from the database
    images = Gallery.objects.all()
    return render(request, 'pages/gallery.html',{'images': images})

# Student Dashboard ----------------------------------------------------------------

# @user_type_required('student')

class StudentViews():

  
    

    def dashboard(request):

        
        allAssesment = Assesment.objects.count()
        allLecture = Lecture.objects.count()
        allStudyMaterial = StudyMaterial.objects.count()
        allUser = User.objects.count()
        allNotification = Notification.objects.count()
    
        return render(request, 'pages/student/home.html',{'allAssesment':allAssesment,'allLecture':allLecture,'allStudyMaterial':allStudyMaterial,'allNotification':allNotification})





    def profile(request):
        
        user = request.user  
        print(user)
        
        student = get_object_or_404(Student,user_id=user.id)
        return render(request, 'pages/student/profile.html', {'user': user, 'student': student})
       


    def update_profile(request):
        classes = SchoolClass.objects.all()
        user = request.user
        student = get_logged_in_student(request)

        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            fname = request.POST.get('fname')
            mname = request.POST.get('mname')
            age = request.POST.get('age')
            avatar = request.FILES.get('avatar')
            address = request.POST.get('address')
            gender = request.POST.get('gender')
            school_class = request.POST.get('school_class')
            section = request.POST.get('section')
            year = request.POST.get('year')

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.mobile = mobile
            if avatar:
                user.avatar = avatar
            user.save()

            student.name = f"{first_name} {last_name}"
            student.address = address
            student.gender = gender
            student.age = age
            student.fname = fname
            student.mname = mname

            if school_class:
                student.school_class = get_object_or_404(SchoolClass, pk=school_class)
            if section:
                student.section = get_object_or_404(Section, pk=section)
            

            student.save()

            messages.success(request, "Profile updated successfully")
            return redirect('student-profile')

        return render(request, 'pages/student/update_profile.html', {
            'classes': classes,
            'student': student,
            'user': user
        })



    def study_material(request):

        student = get_object_or_404(Student, user_id=request.user.id)
        studymaterials = StudyMaterial.objects.filter(school_class=student.school_class, section=student.section)

        return render(request, 'pages/student/study_material.html',{'studymaterials':studymaterials})

    def assesments(request):
        student = get_object_or_404(Student, user_id=request.user.id)
        assesments = Assesment.objects.filter(school_class=student.school_class, section=student.section)

        return render(request, 'pages/student/assignments.html',{'assesments': assesments})


    def lectures(request):
        student = get_object_or_404(Student, user_id=request.user.id)
        lectures = Lecture.objects.filter(school_class=student.school_class, section=student.section)

        return render(request, 'pages/student/lectures.html',{'lectures':lectures})

    def doubt_session(request):
        return render(request, 'pages/student/doubts_session.html')


    def register_complaint(request):
        
        
        try:
            student = get_object_or_404(Student,user_id=request.user.id)
            complains = Complaint.objects.filter(student_id=student.id)
            if request.method == 'POST':
                subject = request.POST.get('subject')
                comp = request.POST.get('comp')
                
                complain = Complaint(student=student, subject=subject, comp=comp)
                complain.save()
                
                messages.success(request, "Complaints submitted successfully")
                return redirect('register_complaint')
            return render(request, 'pages/student/register_complaint.html',{'complains':complains})

        except :
            return render(request, 'pages/student/register_complaint.html', {})

    def feedbacks(request):


        
        try:
            student = get_object_or_404(Student, user_id=request.user.id)

            if request.method == 'POST':
                subject = request.POST.get('subject')
                feed = request.POST.get('feed')
                Feedback.objects.create(student=student, subject=subject, feed=feed)
                messages.success(request, "Feedback submitted successfully")
                return redirect('feedbacks')

            feedbacks = Feedback.objects.filter(student_id=student.id)
            return render(request, 'pages/student/feedbacks.html', {'feedbacks': feedbacks})

        except :
            return render(request, 'pages/student/feedbacks.html', {})
        # return render(request, 'pages/student/feedbacks.html',{'feedbacks':feedbacks})

    def read_notifications(request):
        notifications = Notification.objects.all()
        return render(request, 'pages/student/notifications.html', {'notifications': notifications})
    
    def timetable_list(request):

        student = Student.objects.get(user=request.user)
        print(student.school_class)


        classes = SchoolClass.objects.all()
        school_class = get_object_or_404(SchoolClass, id=student.school_class.id)
        section = get_object_or_404(Section, id=student.section.id)
        timetable_entries = TimetableEntry.objects.filter(
            school_class=school_class,
            section=section
        ).select_related('subject', 'teacher', 'period')

        # Organize entries by day and period.id
        timetable = defaultdict(dict)
        for entry in timetable_entries:

            timetable[entry.day][entry.period.id] = entry
    

        context = {
            'classes':classes,
            'school_class': school_class,
            'section': section,
            'timetable': dict(timetable),
            'days': DayChoices.choices,  # E.g. [(1, "Monday"), (2, "Tuesday"), ...]
            'periods': Period.objects.all().order_by('start_time'),
        }
        return render(request, 'pages/student/timetable_list.html', context)

   
    



# Guest Dash board ------------------------------------------------------------

class GuestViews():

    def dashboard(request):
        user = request.user
        try:
            # Attempt to get the student based on the logged-in user
            

            

            # Render the dashboard template with student and subjects
            return render(request, 'pages/guest/home.html')

        except Student.DoesNotExist:
            classes = SchoolClass.objects.all()
            # If no student is found, redirect to a different template or page
            return render(request, 'pages/guest/home.html',{'classes': classes})



    
    def profile(request):
        
        user = request.user  
        
        return render(request, 'pages/guest/profile.html', {'user': user})
       

    def admission_apply(request):
        user = request.user
        classes = SchoolClass.objects.all()

        try:
            student = get_logged_in_student(request)
            if student:
                messages.info(request, 'You have already applied for admission.')
                return redirect('guest_dashboard')

            if request.method == 'POST':
                date_of_birth = request.POST.get('date_of_birth')
                fname = request.POST.get('fname')
                mname = request.POST.get('mname')
                gender = request.POST.get('gender')
                aadhar_number = request.POST.get('aadhar_number')

                address_line_1 = request.POST.get('address_line_1')
                address_line_2 = request.POST.get('address_line_2')
                city = request.POST.get('city')
                state = request.POST.get('state')
                country = request.POST.get('country')
                postal_code = request.POST.get('postal_code')

                school_class_id = request.POST.get('school_class')
                section_id = request.POST.get('section')

                previous_school = request.POST.get('previous_school')
                last_qualification = request.POST.get('last_qualification')
                year_of_passing = request.POST.get('year_of_passing')
                grade = request.POST.get('grade')

                image = request.FILES.get('image')
                aadhar_image = request.FILES.get('aadhar_image')

                school_class = get_object_or_404(SchoolClass, pk=school_class_id)
                section = get_object_or_404(Section, pk=section_id)

                rollnumber = generate_roll_number(school_class_id, section_id)

                admission = Student(
                    user=user,
                    rollno=rollnumber,
                    date_of_birth=date_of_birth,
                    fname=fname,
                    mname=mname,
                    gender=gender,
                    school_class=school_class,
                    section=section,
                    aadhar_number=aadhar_number,
                    previous_school=previous_school,
                    last_qualification=last_qualification,
                    year_of_passing=year_of_passing,
                    grade=grade,
                    city=city,
                    state=state,
                    country=country,
                    postal_code=postal_code,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    image=image,
                    aadhar_imag=aadhar_image,
                )
                admission.save()

                messages.success(request, "Admission application submitted successfully.")
                return redirect('admission_apply')

            return render(request, 'pages/guest/admission_apply.html', {
                "classes": classes,
            })

        except Student.DoesNotExist:
            print("Student does not exist")
   
            
    
    def drop_admission(request):
        user = request.user
        student = get_object_or_404(Student, user=user)
        
        student.delete()
           
        messages.success(request, "Admission dropped successfully")
        return redirect('guest_dashboard')
        
    def teaching_apply(request):
        user = request.user

        try:
            teacher = get_logged_in_teacher(request)
            if teacher:
                messages.info(request, 'You have already applied as a teacher.')
                return redirect('guest_dashboard')

            if request.method == 'POST':
                dob = request.POST.get('dob')
                gender = request.POST.get('gender')
                aadhar_number = request.POST.get('aadhar_number')
                
                address1 = request.POST.get('address1')
                address2 = request.POST.get('address2')
                city = request.POST.get('city')
                postal_code = request.POST.get('postal_code')
                state = request.POST.get('state')
                country = request.POST.get('country')
                qualification = request.POST.get('qualification')
                specialization = request.POST.get('specialization')
                experience = request.POST.get('experience')
                designation = request.POST.get('designation')

                image = request.FILES.get('image')
                aadhar_doc = request.FILES.get('aadhar_doc')
                qualification_doc = request.FILES.get('qualification_doc')

                teacher = Teacher.objects.create(
                    user=user,
                    date_of_birth=dob,
                    gender=gender,
                    aadhar_number=aadhar_number,
                    address_line_1=address1,
                    address_line_2=address2,
                    city=city,
                    postal_code=postal_code,
                    state=state,
                    country=country,
                    qualification=qualification,
                    specialization=specialization,
                    experience_years=experience,
                    designation=designation,
                    image=image,
                    aadhar_imag=aadhar_doc,
                    qualification_doc=qualification_doc
                )

                messages.success(request, "Teacher profile registered successfully.")
                return redirect('guest_dashboard')

            return render(request, 'pages/guest/teaching_apply.html')

        except Teacher.DoesNotExist:
            print("Teacher does not exist")


    def update_profile(request):
        user = request.user
        if request.method =='POST':
            username = request.POST.get('username')
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email =request.POST.get("email")
            mobile = request.POST.get("mobile")
            avatar = request.FILES.get("avatar")

            
            user.first_name = first_name
        
            user.last_name = last_name
        
            user.email = email
        
            user.mobile = mobile
            print(avatar)
            if avatar:
                user.avatar = avatar
            
            user.save()


            

            print(first_name, last_name, email, mobile, avatar)
            return redirect('guest_profile')


        return render(request, 'pages/guest/update_profile.html')


    
    def study_material(request):
        study_material = StudyMaterial.objects.all()
        return render(request, 'pages/guest/study_material.html',{'studymaterial': study_material})

    def lectures(request):
        lectures = Lecture.objects.all()
        return render(request, 'pages/guest/lectures.html',{'lectures':lectures})

    def assessment(request):
        assesments = Assesment.objects.all()
        return render(request, 'pages/guest/assignments.html',{'assesments':assesments})


    def feedbacks(request):
        if request.method == 'POST':
            subject = request.POST.get('subject')
            feed = request.POST.get('feed')
            feedback = Feedback( subject=subject, feed=feed)
            feedback.save()
            print(feedback)
            messages.success(request, "Feedback submitted successfully")
            return redirect('feedbacks')
        return render(request, 'pages/guest/feedbacks.html')

    
    
    
  



# Teachers dash views ------------------------------------------------------------

# @user_type_required('teacher')
class TeacherViews():
    
    def add_intrested_subjects(request):
        user = request.user
        teacher = get_object_or_404(Teacher,user=user)
        if request.method == 'POST':
            sc = request.POST.get('school_class')
            sec = request.POST.get('section')
            sub = request.POST.get('subject')

            

            subject = get_object_or_404(Subject,pk=sub)
            school_class = get_object_or_404(SchoolClass, pk=sc)
            section = get_object_or_404(Section, pk=sec)

            TeacherInterest.objects.create(
                teacher=teacher,
                subject=subject,
                school_class=school_class,
                section=section,
            )
            messages.success(request, "Teacher subject added successfully")
            return redirect('add_intrested_subjects')
        classes = SchoolClass.objects.all()
        
        subjects = teacher.interests.all()
        
        return render(request, 'pages/teacher/add_intrested_subjects.html',{'classes':classes,"subjects":subjects})
      
    def delete_intrested_subjects(request, subject_id):
        
        subject = get_object_or_404(TeacherInterest,pk=subject_id)
        subject.delete()
        messages.success(request, "Subject deleted successfully")
        return redirect('add_intrested_subjects')
    
    def dashboard(request):

    
        allAssesment = Assesment.objects.count()
        allLecture = Lecture.objects.count()
        allStudyMaterial = StudyMaterial.objects.count()
        allUser = User.objects.count()
        allNotification = Notification.objects.count()
    
        return render(request, 'pages/teacher/home.html',{'allAssesment':allAssesment,'allLecture':allLecture,'allStudyMaterial':allStudyMaterial,'allNotification':allNotification})

    def upload_studymaterial(request):
        classes = SchoolClass.objects.all()
        if request.method == 'POST':
            school_class_id = request.POST.get('school_class')
            section_id = request.POST.get('section')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            if is_protected == 'False':
                is_protected = False
            print(file)
            
            school_class = get_object_or_404(SchoolClass, pk=school_class_id)
        
            section = get_object_or_404(Section, pk=section_id)
        

            study_material = StudyMaterial(user=request.user,school_class=school_class, section=section, subject=subject, file_name=file_name, file=file,is_protected=is_protected)
            print(study_material)
            study_material.save()
            return redirect('upload_studymaterial_teacher')

        allStudyMaterials = StudyMaterial.objects.all()

        return render(request, 'pages/teacher/upload_study.html',{'classes':classes,  'studymaterials':allStudyMaterials})

    def delete_study_material(request,id):
        
        study_material = get_object_or_404(StudyMaterial,pk=id)
        study_material.delete()
        return redirect('upload_studymaterial')

    def upload_lectures(request):
        
        classes = SchoolClass.objects.all()
        if request.method == 'POST':
            school_class_id = request.POST.get('school_class')
            section_id = request.POST.get('section')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            link = request.POST.get('link')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False
            school_class = get_object_or_404(SchoolClass, pk=school_class_id)
        
            section = get_object_or_404(Section, pk=section_id)
        

            lecture = Lecture(user=request.user, school_class=school_class, section=section,  subject=subject, file_name=file_name, link=link, is_protected=is_protected)
            print(lecture)
            lecture.save()
            return redirect('upload_lectures_teacher')
        allLectures = Lecture.objects.all()
        return render(request, 'pages/teacher/upload_lectures.html',{'classes':classes, "lectures":allLectures})

    def delete_lecture(request,id):
        
        lecture = get_object_or_404(Lecture,pk=id)
        lecture.delete()
        return redirect('upload_lectures')

    def upload_assesments(request):
        classes = SchoolClass.objects.all()
        if request.method == 'POST':
            school_class_id = request.POST.get('school_class')
            section_id = request.POST.get('section')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False

            school_class = get_object_or_404(SchoolClass, pk=school_class_id)
        
            section = get_object_or_404(Section, pk=section_id)
        
    

            assessment = Assesment(user=request.user, school_class=school_class, section=section,  subject=subject, file_name=file_name, file=file, is_protected=is_protected)
            print(assessment)
            assessment.save()
            return redirect('upload_assesments_teacher')
        allAssessments = Assesment.objects.all()

        return render(request, 'pages/teacher/upload_assesments.html',{'classes':classes, 'assessments':allAssessments})

    def delete_assessment(request,id):
        
        assessment = get_object_or_404(Assesment,pk=id)
        assessment.delete()
        return redirect('upload_assesments')




    def profile(request):
        
        user = request.user  
        print(user)
        teacher = None
        try:    

            teacher = get_object_or_404(Teacher,user_id=user.id)
            # student = get_object_or_404(Student,user_id=user.id)
            return render(request, 'pages/teacher/profile.html', {'user': user, 'teacher': teacher})
        
        except Teacher.DoesNotExist:
            if user.user_type != 'teacher':
                messages.error(request, "You are not a teacher")
                return redirect('login')
            # If no student is found, redirect to a different template or page
            return render(request, 'pages/teacher/profile.html', {'user': user})
        
    


    def update_profile(request):
        classes = SchoolClass.objects.all()
        user = request.user
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
           

            

                
            user.first_name = first_name
        
            user.last_name = last_name
        
            user.email = email
        
            user.mobile = mobile

            user.save()

        
        
        
            
            
            print("Student saved")

            messages.success(request, "Profile updated successfully")
            return redirect('teacher_profile')
            # return redirect('student_dashboard')
                
            

        return render(request, 'pages/teacher/updateprofile.html', {'classes': classes,  'user':user})

    def save_profile(request):
        classes = SchoolClass.objects.all()
        user = request.user
        student = get_logged_in_student(request)
    
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        fname = request.POST.get('fname')
        mname = request.POST.get('mname')
        age = request.POST.get('age')
        avatar = request.FILES.get('avatar')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        school_class_id = request.POST.get('school_class')
        section_id = request.POST.get('section')
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if mobile:
            user.mobile = mobile
        user.save()

        
        if avatar :
            student.avatar = avatar
        if first_name or last_name:
            student.name = first_name + ' ' + last_name
        if mobile:
            student.mobile = mobile
        if address:
            student.address = address
        if gender:
            student.gender = gender
        if school_class_id:
            student.school_class = get_object_or_404(SchoolClass, pk=school_class_id)
            
        if age :
            student.age = age
        if fname:
            student.fname = fname
        if mname:
            student.mname = mname
        if section_id:
            student.section = get_object_or_404(Section, pk=section_id)
        student.save()
        print("Student saved")

        messages.success(request, "Profile updated successfully")
        # return redirect('student_profile')
        return render(request, 'pages/student/update_profile.html', {'classes': classes, 'user':user})
        # return redirect('student_dashboard')
            
            

    def doubt_session(request):
        return render(request, 'pages/student/doubts_session.html')


    def feedbacks(request):


        if request.method == 'POST':
            subject = request.POST.get('subject')
            feed = request.POST.get('feed')
            student = get_object_or_404(Student,user_id=request.user.id)
            feedback = Feedback(student=student, subject=subject, feed=feed)
            feedback.save()
            
            messages.success(request, "Feedback submitted successfully")
            return redirect('feedbacks')
        try:
            student = get_object_or_404(Student,user_id=request.user.id)
            feedbacks = Feedback.objects.filter(student_id=student.id)
            return render(request, 'pages/student/feedbacks.html',{'feedbacks':feedbacks})

        except :
            return render(request, 'pages/student/feedbacks.html', {})
        # return render(request, 'pages/student/feedbacks.html',{'feedbacks':feedbacks})

    def read_notifications(request):
        notifications = Notification.objects.all()
        return render(request, 'pages/student/notifications.html', {'notifications': notifications})


    def attendance_report(request):
        # Get all students
        classes = SchoolClass.objects.all()
        students = Student.objects.select_related('user').filter(admission_status='approved')
        is_filtered = False
        if request.method == 'GET':
            
            school_class = request.GET.get('school_class')
            section = request.GET.get('section')
            subject = request.GET.get('subject')
            
            if school_class:
                is_filtered = True
                students = students.filter(school_class=school_class)
            if section:
                students = students.filter(section=section)
            
            if subject:
                students = students.filter(subject=subject)

        if request.method == 'POST':
            is_filtered = False
        # getting values from form
            student_ids = request.POST.getlist('student_ids')   # list of student IDs
            school_class_id = request.GET.get('school_class')
            section_id = request.GET.get('section')

            if not student_ids or not school_class_id or not section_id :
                messages.error(request, "Please select students and class details")
                return redirect('attendance_report')
            
            section = get_object_or_404(Section, pk=section_id)
            school_class = get_object_or_404(SchoolClass, pk=school_class_id)
            

            for student_id in student_ids:

                status = request.POST.get(f'status_{student_id}') == 'present'  # status_present / status_absent
                is_attendance_exists = Attendance.objects.filter(student_id=student_id, school_class=school_class, section=section,date__date=datetime.now().date()).exists()
                if is_attendance_exists:
                    attendance = Attendance.objects.get(student_id=student_id,  school_class=school_class, section=section, date__date=datetime.now().date())
                    attendance.status = status
                    attendance.submitted_by = request.user
                    attendance.save()
                else:
                    Attendance.objects.create(
                        student_id=student_id,
                        school_class=school_class, 
                        section=section,
                        status=status,
                        submitted_by=request.user,
                        
                    )
            
            messages.success(request, "Attendance submitted successfully")
        
            return redirect('attendance_report') 
            

        # Get unique attendance dates
        dates = Attendance.objects.annotate(date_only=TruncDate('date')) \
                                .values_list('date_only', flat=True) \
                                .distinct() \
                                .order_by('date_only')

        # Build a dictionary: { (student_id, date): status }
        attendance_data = {}
        attendances = Attendance.objects.annotate(date_only=TruncDate('date')).all()

        for attendance in attendances:
            
            key = (attendance.student_id, attendance.date_only)
            
            attendance_data[key] = attendance.status  # True or False
           
          
        
        

        return render(request, 'pages/teacher/attendance_report.html', {
            'students': students,
            'dates': dates,
            'attendance_data': attendance_data,
            'classes': classes,
            'is_filtered': is_filtered,
        })
    

    def teacher_timetable(request):
        
        teacher = Teacher.objects.get(user=request.user)
        periods = Period.objects.all().order_by('start_time')

        # Structure: {teacher: {day: {period_id: entry}}}
        teacher_timetable = {}

    
        
        timetable_entries = TimetableEntry.objects.filter(teacher=teacher).select_related(
            'subject', 'school_class', 'section', 'period'
        )

        day_period_map = defaultdict(dict)
        for entry in timetable_entries:
            day_period_map[entry.day][entry.period.id] = entry

        teacher_timetable = dict(day_period_map)

        context = {
            'periods': periods,
            'days': DayChoices.choices,
            'teacher_timetable': teacher_timetable,
        }
        return render(request, 'pages/teacher/timetable_list.html', context)




   




# Admin Dashboard and views --------------------------------------------------------
# @user_type_required('admin')
class AdminViews():

    
    
    
    def dashboard(request):
       
        allStudent = Student.objects.count() 
        allTeacher = Teacher.objects.count()
        allAssesment = Assesment.objects.count()
        allLecture = Lecture.objects.count()
        allStudyMaterial = StudyMaterial.objects.count()
        allUser = User.objects.count()
        allComplain = Complaint.objects.count()
        allFeedback = Feedback.objects.count()
        allNotification = Notification.objects.count()

        return render(request, 'pages/admin/home.html',{'admin':request.user, 'allStudent':allStudent, 'allTeacher': allTeacher, 'allAssesment':allAssesment, 'allLecture': allLecture, 'allStudyMaterial': allStudyMaterial, 'allUser': allUser, 'allNotification': allNotification, "allFeedback":allFeedback})

    def verify_user(request,id):
        user = get_object_or_404(User,pk=id)
        if user.is_verified:
            user.is_verified = False
        else:
            user.is_verified = True
        user.save()
        return redirect('manage_user')

    def manage_user(request):
        users = User.objects.all()
        return render(request, 'pages/admin/manage_user.html', {'users': users})


    def edit_user(request,id):
        u = get_object_or_404(User,pk=id)
        if request.method == 'POST':
            u.first_name = request.POST.get('first_name')
            u.last_name = request.POST.get('last_name')
            u.email = request.POST.get('email')
            u.mobile = request.POST.get('mobile')
            u.save()
            return redirect('manage_user')
        return render(request, 'pages/admin/edit_user.html', {'user': u})

    
    def delete_user(request,id):
        u = get_object_or_404(User,pk=id)
        u.delete()
        return redirect('manage_user')
    
    def add_admission_eligibility(request):
        students = Student.objects.filter(is_verified=False, admission_status="pending" )
           
        return render(request, 'pages/admin/add_admission_eligibility.html', {'students': students})
    
    def add_admission_eligibility_save(request,student_id):
        student = get_object_or_404(Student,pk=student_id)
        print(not student.is_eligible_for_admission)
        
        student.is_eligible_for_admission = not student.is_eligible_for_admission
        student.save()
        messages.success(request, "Admission eligibility updated successfully")
        return redirect('add_admission_eligibility')
    
    def add_entrance_exam_score(request,student_id):
        student = get_object_or_404(Student,pk=student_id)
        if request.method == 'POST':
            entrance_exam_score = request.POST.get('entrance_exam_score')
            student.entrance_exam_score = entrance_exam_score
            
            student.save()
            messages.success(request, "Admission eligibility updated successfully")
            return redirect('add_admission_eligibility')
        
    def students_admission_verification(request):
        students = Student.objects.all()
        
        return render(request, 'pages/admin/students_admission_verification.html', {'students': students})

    def verify_admission(request,student_id):
        student = get_object_or_404(Student,pk=student_id)

        if request.method == 'POST':
            student.admission_status = request.POST.get('admission_status')
            if student.admission_status == 'rejected' or student.admission_status == 'pending':
                student.is_verified = False
                student.user.user_type = 'guest'
            elif student.admission_status == 'approved':
                student.user.user_type = 'student'
                student.is_verified = True
                student.user.is_verified = True
            print(student.user.user_type)
            student.user.save()
            student.save()
            
            messages.success(request, "Admission status updated successfully")
            return redirect('students_admission_verification')
        
        
    def register_student(request):
        
        classes = SchoolClass.objects.all()  # for populating the class dropdown

        if request.method == "POST":
            # Basic user data
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            password =get_random_string(10)



            mobile = request.POST.get("mobile")

            # Personal Info
            date_of_birth = request.POST.get("date_of_birth")
            fname = request.POST.get("fname")
            mname = request.POST.get("mname")
            gender = request.POST.get("gender")
            aadhar_number = request.POST.get("aadhar_number")

            # Address
            address_line_1 = request.POST.get("address_line_1")
            address_line_2 = request.POST.get("address_line_2")
            city = request.POST.get("city")
            state = request.POST.get("state")
            postal_code = request.POST.get("postal_code")
            country = request.POST.get("country")

            # Education
            school_class_id = request.POST.get("school_class")
            section_id = request.POST.get("section")

            # Qualification
            previous_school = request.POST.get("previous_school")
            last_qualification = request.POST.get("last_qualification")
            year_of_passing = request.POST.get("year_of_passing")
            grade = request.POST.get("grade")

            # File uploads
            image = request.FILES.get("image")
            aadhar_image = request.FILES.get("aadhar_image")

            try:
                # Create user
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    mobile=mobile,
                    password=make_password(password),
                    user_type="student",
                    is_verified=True,  # Set to True for admin-created users
                    is_detailed=True,  # Set to True for admin-created users
                    avatar = image,
                )


                rollnumber = generate_roll_number(school_class_id, section_id)
                print(rollnumber)
                # Create student
                student = Student.objects.create(
                    user=user,
                    rollno=rollnumber,
                    admission_status="approved",

                    date_of_birth=date_of_birth,
                    fname=fname,
                    mname=mname,
                    gender=gender,
                    aadhar_number=aadhar_number,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    state=state,
                    postal_code=postal_code,
                    country=country,
                    school_classid=school_class_id,
                    section=section_id,
                    previous_school=previous_school,
                    last_qualification=last_qualification,
                    year_of_passing=year_of_passing,
                    grade=grade,
                    image=image,
                    aadhar_imag=aadhar_image,
                    is_verified=True,  # Set to True for admin-created students

                )

                messages.success(request, "Student registered successfully.")
                send_admin_registration_confirmation_email(user_email=email, user_name=f'{first_name} {last_name}', username=username, password=password)
                return redirect("register_student")  # Replace with your desired redirect
            except Exception as e:
                messages.error(request, f"Error occurred: {e}")

        return render(request, "pages/admin/register_student.html", {"classes": classes})
           
    def register_teacher(request):
        
        if request.method == 'POST':
            # Get user credentials
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            mobile = request.POST.get('mobile')
            password =get_random_string(10)



            # Personal Info
            dob = request.POST.get('date_of_birth')
            gender = request.POST.get('gender')
            aadhar_number = request.POST.get('aadhar_number')
            address1 = request.POST.get('address1')
            address2 = request.POST.get('address2')
            city = request.POST.get('city')
            postal_code = request.POST.get('postal_code')
            state = request.POST.get('state')
            country = request.POST.get('country')

            # Professional Info
            qualification = request.POST.get('qualification')
            specialization = request.POST.get('specialization')
            experience = request.POST.get('experience')
            designation = request.POST.get('designation')

            # Documents
            image = request.FILES.get('image')
            aadhar_doc = request.FILES.get('aadhar_doc')
            qualification_doc = request.FILES.get('qualification_doc')

            try:
                 # Create user
                user = User.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    mobile=mobile,
                    password=make_password(password),
                    is_active=True,
                    is_staff=True,  # Set to True for admin-created users
                    user_type="teacher",
                )

                
                # Create teacher profile
                Teacher.objects.create(
                    user=user,
                    date_of_birth=dob,
                    gender=gender,
                    aadhar_number=aadhar_number,
                    address_line_1=address1,
                    address_line_2=address2,
                    city=city,
                    postal_code=postal_code,
                    state=state,
                    country=country,
                    qualification=qualification,
                    specialization=specialization,
                    experience_years=experience,
                    designation=designation,
                    image=image,
                    aadhar_imag=aadhar_doc,
                    qualification_doc=qualification_doc
                )

                # Optionally, send confirmation email to teacher
                Employee.objects.create(
                    user=user,
                    role=user.user_type
                )
                messages.success(request, f"Teacher {first_name} registered successfully.")
                send_admin_teacher_registration_email(user_email=email, user_name=f"{first_name} {last_name}", username=username, password=password, login_url=None)
                return redirect('register_teacher')  # Replace with your actual view
            except Exception as e:
                messages.error(request, f"Error occurred: {e}")


        return render(request, "pages/admin/register_teacher.html")
    
    def profile(request):
        user = request.user
        
        return render(request, 'pages/admin/profile.html', {'admin_user': user})
    
    def user_profile(request, username):
        print(username)
        if not username:
            messages.error(request, "Username not provided")
            return redirect('admin_profile')
        admin_user = request.user
        user = get_object_or_404(User, username=username)

        if user.user_type == 'student':
            student = get_object_or_404(Student, user=user)
            return render(request, 'pages/admin/profile_student.html', {'admin_user': admin_user, 'student': student})
        elif user.user_type == 'teacher':
            teacher = get_object_or_404(Teacher, user=user)
            return render(request, 'pages/admin/profile_teacher.html', {'admin_user': admin_user, 'teacher': teacher})
        elif user.user_type == 'admin':
            admin = get_object_or_404(User, username=username)
            return render(request, 'pages/admin/profile_admin.html', {'admin_user': admin_user, 'admin': admin})
        elif user.user_type == 'guest':
            guest = get_object_or_404(User, user=user)
            try:
                student = Student.objects.filter(user_id=user.id).first()
                teacher = Teacher.objects.filter(user_id = user.id).first()
                if student :
                    return render(request, 'pages/admin/profile_student.html', {'admin_user': admin_user, 'student': student})
                elif teacher:
                    return render(request, 'pages/admin/profile_teacher.html', {'admin_user': admin_user, 'teacher': teacher})
                else:
                    return render(request, 'pages/admin/profile_guest.html', {'admin_user': admin_user, 'guest': guest})

            except :

                return render(request, 'pages/admin/profile_guest.html', {'admin_user': admin_user, 'guest': guest})
        

        messages.error(request, "User not found")
        
        return render(request, 'pages/admin/profile.html', {'admin_user': user})

    def manage_student(request):
        st = Student.objects.filter(is_verified=True)
        return render(request, 'pages/admin/manage_student.html',{'students': st})

    
    def edit_student(request,id):
        classes = SchoolClass.objects.all()
        user = get_object_or_404(User, pk=id)
        student = get_object_or_404(Student,user_id=id)
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            fname = request.POST.get('fname')
            mname = request.POST.get('mname')
            age = request.POST.get('age')
            avatar = request.FILES.get('avatar')
            address = request.POST.get('address')
            gender = request.POST.get('gender')
            school_class_id = request.POST.get('school_class')
            section_id = request.POST.get('section')

            if school_class_id:
                student.school_class = get_object_or_404(SchoolClass, pk=school_class_id)
            if section_id:
                student.section = get_object_or_404(Section, pk=section_id)
            

            print(first_name, last_name, email, mobile, fname, mname)
                
            user.first_name = first_name
        
            user.last_name = last_name
        
            user.email = email
        
            user.mobile = mobile

            user.save()

        
        
            student.avatar = avatar
        
            student.name = first_name + ' ' + last_name
        
            student.mobile = mobile
            student.mobile = mobile
        
            
            student.address = address
        
            student.gender = gender
        
        
            student.age = age
    
            student.fname = fname
        
            student.mname = mname
        
            student.save()
            
            print("Student saved")

            messages.success(request, "Profile updated successfully")
            return redirect('manage_student')
            # return redirect('student_dashboard')
                
            

        return render(request, 'pages/admin/edit_student.html', {'classes': classes, 'student': student, 'user':user})

    def delete_student(request,id):
        st = get_object_or_404(User,pk=id)
        st.delete()
        return redirect('manage_student')


    def manage_teacher(request):
        te = Teacher.objects.all()
        return render(request, 'pages/admin/manage_teacher.html', {'teachers': te})

    def edit_teacher(request,id):
        user = get_object_or_404(User, pk=id)
        if user.user_type != 'teacher':
            messages.error(request, "User is not a teacher")
            return redirect('manage_teacher')
        teacher = get_object_or_404(Teacher,user=user)
        if request.method == 'POST':
            # User info
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.username = request.POST.get('username')
            user.mobile = request.POST.get('mobile')
            user.save()

            # Teacher profile info
            teacher.date_of_birth = request.POST.get('date_of_birth')
            teacher.gender = request.POST.get('gender')
            teacher.aadhar_number = request.POST.get('aadhar_number')
            teacher.address_line_1 = request.POST.get('address1')
            teacher.address_line_2 = request.POST.get('address2')
            teacher.city = request.POST.get('city')
            teacher.postal_code = request.POST.get('postal_code')
            teacher.state = request.POST.get('state')
            teacher.country = request.POST.get('country')
            teacher.qualification = request.POST.get('qualification')
            teacher.specialization = request.POST.get('specialization')
            teacher.experience_years = request.POST.get('experience')
            teacher.designation = request.POST.get('designation')

            # Optional file updates
            if request.FILES.get('image'):
                teacher.image = request.FILES.get('image')
            if request.FILES.get('aadhar_doc'):
                teacher.aadhar_imag = request.FILES.get('aadhar_doc')
            if request.FILES.get('qualification_doc'):
                teacher.qualification_doc = request.FILES.get('qualification_doc')

            teacher.save()
            messages.success(request, "Teacher profile updated successfully.")
         # Replace with the actual redirect

            return redirect('manage_teacher')
        return render(request, 'pages/admin/edit_teacher.html', {'teacher': teacher})
    def verify_teacher(request,id):
        
        teacher = get_object_or_404(User,pk=id)
         
        if teacher.is_staff:
            teacher.user_type="guest"
            teacher.is_staff = False
        else:
            employee = Employee.objects.filter(user=teacher).first()
            if not employee:
                Employee.objects.create(
                    user=teacher,
                    role=teacher.user_type
                )

            teacher.user_type="teacher"
            teacher.is_staff = True
        teacher.save()
        return redirect('manage_teacher')

    def delete_teacher(request  ,id):
        te = get_object_or_404(User,pk=id)
        te.delete()
        return redirect('manage_teacher')

    def manage_admin(request):
        # ad = Admin.objects.all()
        ad= User.objects.filter(user_type = 'admin')
        return render(request, 'pages/admin/manage_admin.html', {'admins': ad})
    def verify_admin(request,id):
        staff = get_object_or_404(User,pk=id)
        if staff.is_staff:
            staff.is_staff = False
        else:
            staff.is_staff = True
        staff.save()
        return redirect('manage_admin')
    
    def delete_admin(request,id):
        ad = get_object_or_404(User,pk=id)
        ad.delete()
        return redirect('manage_admin')



    def upload_studymaterial(request):
        classes = SchoolClass.objects.all()
        if request.method == 'POST':
            school_class_id = request.POST.get('school_class')
            section_id = request.POST.get('section')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            if is_protected == 'False':
                is_protected = False
            print(file)
            
            school_class = get_object_or_404(SchoolClass, pk=school_class_id)
        
            section = get_object_or_404(Section, pk=section_id)
        

            study_material = StudyMaterial(user=request.user,school_class=school_class, section=section, subject=subject, file_name=file_name, file=file,is_protected=is_protected)
            print(study_material)
            study_material.save()
            return redirect('upload_studymaterial')

        allStudyMaterials = StudyMaterial.objects.all()

        return render(request, 'pages/admin/upload_study.html',{'classes':classes,  'studymaterials':allStudyMaterials})

    def delete_study_material(request,id):
        
        study_material = get_object_or_404(StudyMaterial,pk=id)
        study_material.delete()
        return redirect('upload_studymaterial')

    def upload_lectures(request):

        classes = SchoolClass.objects.all()
        if request.method == 'POST':
            school_class_id = request.POST.get('school_class')
            section_id = request.POST.get('section')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            link = request.POST.get('link')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False
            school_class = get_object_or_404(SchoolClass, pk=school_class_id)
        
            section = get_object_or_404(Section, pk=section_id)
        

            lecture = Lecture(user=request.user, school_class=school_class, section=section,  subject=subject, file_name=file_name, link=link, is_protected=is_protected)
            print(lecture)
            lecture.save()
            return redirect('upload_lectures')
        allLectures = Lecture.objects.all()
        return render(request, 'pages/admin/upload_lectures.html',{'classes':classes, "lectures":allLectures})

    def delete_lecture(request,id):
        
        lecture = get_object_or_404(Lecture,pk=id)
        lecture.delete()
        return redirect('upload_lectures')

    def upload_assesments(request):
        classes = SchoolClass.objects.all()
        if request.method == 'POST':
            school_class_id = request.POST.get('school_class')
            section_id = request.POST.get('section')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False

            school_class = get_object_or_404(SchoolClass, pk=school_class_id)
        
            section = get_object_or_404(Section, pk=section_id)
        
    

            assessment = Assesment(user=request.user, school_class=school_class, section=section,  subject=subject, file_name=file_name, file=file, is_protected=is_protected)
            print(assessment)
            assessment.save()
            return redirect('upload_assesments')
        allAssessments = Assesment.objects.all()

        return render(request, 'pages/admin/upload_assesments.html',{'classes':classes, 'assessments':allAssessments})

    def delete_assessment(request,id):
        
        assessment = get_object_or_404(Assesment,pk=id)
        assessment.delete()
        return redirect('upload_assesments')

    def view_feedback(request):
        feedbacks = Feedback.objects.all()
        return render(request, 'pages/admin/view_feedback.html',{'feedbacks':feedbacks})

    def view_complaint(request):
        complaints = Complaint.objects.all()
        return render(request, 'pages/admin/view_complaint.html',{'complaints':complaints})

    def view_enquries(request):
        enquries = Enquiry.objects.all()
        return render(request, 'pages/admin/view_enquries.html',{'enquries':enquries})


    def add_notification(request):
        if request.method == 'POST':
            text = request.POST.get('text')
            link = request.POST.get('link')
            admin = Admin.objects.filter(user_id=request.user.id)
            if not admin:
                admin =None
            notification = Notification(admin=admin, text=text,link=link)
            notification.save()
            emails = User.objects.values_list('email', flat=True)
           
            send_notification_email(emails, subject=notification.text, message=notification.link)
            return redirect('add_notification')
        admin = Admin.objects.filter(user_id=request.user.id)
        print(admin)
        notifications = Notification.objects.filter()
        return render(request, 'pages/admin/add_notification.html',{'notifications':notifications})

    def delete_notification(request,id):
       
        notification = get_object_or_404(Notification,id=id)
        notification.delete()
        return redirect('add_notification')

    def add_classes(request):
        classes = SchoolClass.objects.all()
        if request.method == 'POST':
            class_name = request.POST.get('class_name')
            if class_name:
                SchoolClass.objects.create(name=class_name)
                messages.success(request, "Class added successfully")
            return redirect('add_classes')
        return render(request, 'pages/admin/add_classes.html', {'classes': classes})

    def delete_class(request, class_id):
        school_class = get_object_or_404(SchoolClass, id=class_id)
        school_class.delete()
        messages.success(request, "Class deleted successfully")
        return redirect('add_classes')

    def add_sections(request, class_id):
        sections = Section.objects.filter(school_class_id=class_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)
        if request.method == 'POST':
            section_name = request.POST.get('section_name')
            if section_name:
                Section.objects.create(school_class=school_class, name=section_name)
                messages.success(request, "Section added successfully")
            return redirect('add_sections', class_id=class_id)
        return render(request, 'pages/admin/add_sections.html', {'sections': sections, 'class': school_class})

    def delete_section(request, section_id):
        section = get_object_or_404(Section, id=section_id)
        class_id = section.school_class.id
        section.delete()
        messages.success(request, "Section deleted successfully")
        return redirect('add_sections', class_id=class_id)

    def add_fees(request, class_id, section_id):
        fees = FeesType.objects.filter(school_class_id=class_id, section_id=section_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)
        section = get_object_or_404(Section, id=section_id)
        if request.method == 'POST':
            fee_name = request.POST.get('fee_name')
            amount = request.POST.get('amount')
            if fee_name and amount:
                FeesType.objects.create(name=fee_name, amount=amount, school_class=school_class, section=section)
                messages.success(request, "Fees type added successfully")
            return redirect('add_fees', class_id=class_id, section_id=section_id)
        return render(request, 'pages/admin/add_fees.html', {'fees': fees, 'class': school_class, 'section': section})

    def delete_fees(request, fee_id):
        fee = get_object_or_404(FeesType, id=fee_id)
        class_id = fee.school_class.id
        section_id = fee.section.id
        fee.delete()
        messages.success(request, "Fees type deleted successfully")
        return redirect('add_fees', class_id=class_id, section_id=section_id)

    def add_subjects(request, class_id, section_id):
        subjects = Subject.objects.filter(school_class_id=class_id, section_id=section_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)
        section = get_object_or_404(Section, id=section_id)
        if request.method == 'POST':
            subject_name = request.POST.get('subject_name')
            subject_code = request.POST.get('subject_code')

            if subject_name and subject_code:
                Subject.objects.create(name=subject_name, subject_code=subject_code, school_class=school_class, section=section)
                messages.success(request, "Subject added successfully")
            return redirect('add_subjects', class_id=class_id, section_id=section_id)
        return render(request, 'pages/admin/add_subjects.html', {'subjects': subjects, 'class': school_class, 'section': section})

    def delete_subject(request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        class_id = subject.school_class.id
        section_id = subject.section.id
        subject.delete()
        messages.success(request, "Subject deleted successfully")
        return redirect('add_subjects', class_id=class_id, section_id=section_id)

    def add_entrance(request, class_id, section_id):
        entrances = Entrance.objects.filter(school_class_id=class_id, section_id=section_id)
        school_class = get_object_or_404(SchoolClass, id=class_id)
        section = get_object_or_404(Section, id=section_id)
        if request.method == 'POST':
            exam_name = request.POST.get('exam_name')
            date = request.POST.get('date')
            time = request.POST.get('time')
            duration = request.POST.get('duration')
            if exam_name and date and time and duration:
                Entrance.objects.create(
                    name=exam_name,
                    date=date,
                    time=time,
                    duration=duration,
                    school_class=school_class,
                    section=section
                )
                messages.success(request, "Entrance exam added successfully")
            return redirect('add_entrance', class_id=class_id, section_id=section_id)
        return render(request, 'pages/admin/add_entrance.html', {'entrances': entrances, 'class': school_class, 'section': section})

    def delete_entrance(request, entrance_id):
        entrance = get_object_or_404(Entrance, id=entrance_id)
        class_id = entrance.school_class.id
        section_id = entrance.section.id
        entrance.delete()
        messages.success(request, "Entrance exam deleted successfully")
        return redirect('add_entrance', class_id=class_id, section_id=section_id)



        

        # get total fees
        def get_total_due(student):
            expected_total = FeesType.objects.filter(year=student.year).aggregate(total=models.Sum('amount'))['total'] or 0
            paid_total = StudentFee.objects.filter(student=student).aggregate(total=models.Sum('amount_paid'))['total'] or 0
            return expected_total - paid_total
        def record_fee_payment(student, fee_type_id, amount, method, transaction_id=None):
            fee_type = get_object_or_404(FeesType,id=fee_type_id)
            StudentFee.objects.create(
                student=student,
                fee_type=fee_type,
                amount_paid=amount,
                payment_method=method,
                transaction_id=transaction_id
            )
        
        def add_gallery(request):
            user = request.user
            if request.method == 'POST':
                title = request.POST.get('title')
                image = request.FILES.get('image')
                gallery = Gallery(title=title, image=image, user=user)
                gallery.save()
                messages.success(request, "Gallery image added successfully")
                return redirect('add_gallery')
            images = Gallery.objects.all()
            return render(request, 'pages/admin/add_gallery.html', {'images': images})


 # get total fees
    def get_total_due(student):
        expected_total = FeesType.objects.filter(year=student.year).aggregate(total=models.Sum('amount'))['total'] or 0
        paid_total = StudentFee.objects.filter(student=student).aggregate(total=models.Sum('amount_paid'))['total'] or 0
        return expected_total - paid_total
    def record_fee_payment(student, fee_type_id, amount, method, transaction_id=None):
        fee_type = get_object_or_404(FeesType,id=fee_type_id)
        StudentFee.objects.create(
            student=student,
            fee_type=fee_type,
            amount_paid=amount,
            payment_method=method,
            transaction_id=transaction_id
        )
    
    def add_gallery(request):
        user = request.user
        if request.method == 'POST':
            title = request.POST.get('title')
            image = request.FILES.get('image')
            gallery = Gallery(title=title, image=image, user=user)
            gallery.save()
            messages.success(request, "Gallery image added successfully")
            return redirect('add_gallery')
        images = Gallery.objects.all()
        return render(request, 'pages/admin/add_gallery.html', {'images': images})
    
   
    def submit_student_fee(request, student_id):
        student = get_object_or_404(Student, id=student_id)
        form = StudentFeeForm(student=student)

        if request.method == 'POST':
            form = StudentFeeForm(request.POST)
            if form.is_valid():
                fee = form.save(commit=False)
                fee.student = student
                fee.paid_by = request.user
                fee.save()
                return render(request, 'pages/admin/fee_receipt.html', {'fee': fee, 'student': student})
        context = {
            'form': form,
            'student': student,
            'fee_summary': student_fee_summary(student),
        }

        return render(request, 'pages/admin/fee_submit.html', context)
    
    def edit_period(request, period_id):
        entry = Period.objects.filter(pk=period_id).first()
        periods = Period.objects.all()
        if request.method == 'POST':
            form = PeriodForm(request.POST,instance=entry)
            if form.is_valid():
                form.save()
                return redirect('add_period')  # You can change this to your actual list or dashboard
        else:
            form = PeriodForm(instance=entry)
        
        return render(request, 'pages/admin/add_period.html', {'form': form, 'periods':periods, 'period_id':period_id})
    
    def add_period(request):
        periods = Period.objects.all()
        if request.method == 'POST':
            form = PeriodForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('add_period')  # You can change this to your actual list or dashboard
        else:
            form = PeriodForm()
        
        return render(request, 'pages/admin/add_period.html', {'form': form, 'periods':periods})
    
    def generate_timetable_for_class(school_class_id, section_id):
        PERIODS = list(Period.objects.all())  # Get all defined periods
        DAYS = [choice[0] for choice in DayChoices.choices]  # e.g., ['Monday', 'Tuesday', ...]

        TimetableEntry.objects.filter(school_class_id=school_class_id, section_id=section_id).delete()

        # Fetch subjects and teacher assignments
        interests = TeacherInterest.objects.filter(school_class_id=school_class_id, section_id=section_id)
        subject_teacher_map = defaultdict(list)
        for interest in interests:
            subject_teacher_map[interest.subject].append(interest.teacher)

        # Generate all (day, period) slot combinations
        timetable_slots = [(day, period) for day in DAYS for period in PERIODS]
        random.shuffle(timetable_slots)

        subject_periods_required = {subject: 5 for subject in subject_teacher_map}  # Adjust as needed
        teacher_busy_slots = defaultdict(set)
        timetable_entries = []

        for subject, teachers in subject_teacher_map.items():
            periods_needed = subject_periods_required[subject]
            assigned = 0

            for (day, period_instance) in timetable_slots:
                if assigned >= periods_needed:
                    break

                random.shuffle(teachers)
                for teacher in teachers:
                    if (day, period_instance.id) not in teacher_busy_slots[teacher.id]:
                        timetable_entries.append(TimetableEntry(
                            school_class_id=school_class_id,
                            section_id=section_id,
                            subject=subject,
                            teacher=teacher,
                            day=day,
                            period=period_instance
                        ))
                        teacher_busy_slots[teacher.id].add((day, period_instance.id))
                        assigned += 1
                        break

        TimetableEntry.objects.bulk_create(timetable_entries)

    def generate_college_timetable(request):
        """
        View to automatically generate and save the school timetable for all sections.

        Constraints enforced:
        1. 8 periods each day (Period 5 is lunch break - no classes).
        2. Each section has one additional free period daily (aside from lunch).
        3. A teacher cannot be assigned to more than one section in the same period.
        4. Teachers only teach subjects they are interested in (TeacherInterest).
        5. Subjects are evenly distributed in each section's timetable.
        """
        with transaction.atomic():
            if request.user.user_type != 'admin':
                return
            # Clear existing timetable entries to start fresh
            TimetableEntry.objects.all().delete()
            print("Generation Started")

            # Fetch all days (e.g., Monday-Friday)
            days = [choice[0] for choice in DayChoices.choices]


            # Fetch all periods excluding period number 5 (lunch break)
            periods = list(Period.objects.exclude(name='Lunch').order_by('start_time'))

            # Pre-cache teacher interests: subject_id -> list of teacher instances
            teachers_by_subject = {}
            for ti in TeacherInterest.objects.select_related('teacher', 'subject'):
                teachers_by_subject.setdefault(ti.subject_id, []).append(ti.teacher)

            # Track teacher assignments by (day_id, period_id) to avoid conflicts
            teacher_busy = {}
            for day in days:
                for period in periods:
                    teacher_busy[(day, period.id)] = set()

            # Iterate through each section to assign its timetable
            all_sections = Section.objects.select_related('school_class').all()
            for section in all_sections:
                # Get subjects for this section (assuming SchoolClass has many-to-many 'subjects')
                try:
                    subjects_qs = section.school_class.subjects.all()
                except Exception:
                    # Fallback: use all subjects if no specific relation
                    subjects_qs = Subject.objects.all()
                subjects = list(subjects_qs)
                if not subjects:
                    continue

                # Calculate total teaching slots per week: 6 classes/day * number of days
                days_count = len(days)
                total_slots = days_count * 6  # 6 classes each day (free and lunch excluded)

                # Evenly distribute subject occurrences in this section's timetable
                num_subjects = len(subjects)
                base_count = total_slots // num_subjects
                extra = total_slots % num_subjects
                subject_slots = []
                for i, subject in enumerate(subjects):
                    count = base_count + (1 if i < extra else 0)
                    subject_slots.extend([subject] * count)
                random.shuffle(subject_slots)  # Shuffle to randomize distribution

                # Decide a random free period (aside from lunch) for each day in this section
                free_periods = {}
                available_periods = [p.id for p in periods]
                for day in days:
                    free_periods[day] = random.choice(available_periods)

                # Assign subjects to periods for each day in this section
                slot_idx = 0
                for day in days:
                    for period in periods:
                        # Skip lunch break (period number 5 is excluded already)
                        # Skip this day's free period
                        if period.id == free_periods[day]:
                            continue
                        # If we've assigned all subject slots, break
                        if slot_idx >= len(subject_slots):
                            break

                        subject = subject_slots[slot_idx]
                        slot_idx += 1

                        # Find a teacher who can teach this subject and is not busy
                        teacher_assigned = None
                        for teacher in teachers_by_subject.get(subject.id, []):
                            if teacher.id not in teacher_busy[(day, period.id)]:
                                teacher_assigned = teacher
                                break

                        # If no teacher is available for this subject at this slot, skip assigning (slot remains free)
                        if not teacher_assigned:
                            continue

                        # Mark teacher as busy for this day-period
                        teacher_busy[(day, period.id)].add(teacher_assigned.id)
                        print(day)
                        # Create the timetable entry
                        timetable=TimetableEntry.objects.create(
                            school_class=section.school_class,
                            section=section,
                            subject=subject,
                            teacher=teacher_assigned,
                            day=day,
                            period=period
                        )
                        # print(timetable)

        # return HttpResponse("Timetable generated successfully.")
        messages.success(request,"Timetable Generated...")
        return redirect("timetable_list_all")
    
    def generate_school_timetable(request):
        """
        Generates a complete timetable for all sections:
        - 6 days (Mon-Sat), 8 periods each day, skipping the 'Lunch' period.
        - Each section gets one additional free period per day (randomly chosen).
        - Subjects needed 6+ times/week are fixed to the same period each day if possible:contentReference[oaicite:5]{index=5}.
        - No teacher is double-booked in the same period across sections:contentReference[oaicite:6]{index=6}.
        - Teachers are only assigned to subjects they are interested in (via TeacherInterest).
        - Subjects are distributed evenly across available slots.
        - A teacher can teach max 6 periods every day
        """
        logger = logging.getLogger(__name__)
        logger.info("Starting generation of school timetable...")

        try:
            with transaction.atomic():
                # Clear existing timetable entries
                TimetableEntry.objects.all().delete()
                logger.info("Cleared old timetable entries.")

                # Prepare global teacher availability map: teacher_busy[teacher_id][day] = set(period_id)
                teacher_busy = {}
                teacher_load = Counter()

                # Initialize teacher_busy for all teachers
                for ti in TeacherInterest.objects.select_related('teacher').all():
                    teacher = ti.teacher
                    if teacher.id not in teacher_busy:
                        # Map each teacher to a dict of days with occupied periods
                        teacher_busy[teacher.id] = {day_choice[0]: set() for day_choice in DayChoices.choices}

                # Fetch all periods, identify lunch to skip
                lunch_period = Period.objects.filter(name__iexact='Lunch').first()
                periods = list(Period.objects.exclude(id=lunch_period.id) if lunch_period else Period.objects.all())
                periods.sort(key=lambda p: p.id)  # assume id correlates with period order

                # Prepare list of days (values from DayChoices)
                days = [choice[0] for choice in DayChoices.choices]

                # Iterate through each class and section
                for school_class in SchoolClass.objects.all():
                    for section in school_class.sections.all():
                        logger.info(f"Scheduling section {section} of class {school_class}.")
                        # Get all subjects for this class (assuming Subject has a FK to SchoolClass)
                        subjects = list(Subject.objects.filter(school_class=school_class))
                        if not subjects:
                            logger.warning(f"No subjects found for {school_class}. Skipping section {section}.")
                            continue

                        # Compute total teaching slots (6 days * (8 - 2 breaks) = 36 slots per week)
                        total_slots = 6 * (len(periods) - 1)  # subtract one for free period per day
                        # Distribute subjects evenly across total_slots
                        base_count = total_slots // len(subjects)
                        extra = total_slots % len(subjects)
                        # Assign initial counts and shuffle to randomize which subjects get the extra slot
                        random.shuffle(subjects)
                        subject_counts = {}
                        for i, subj in enumerate(subjects):
                            cnt = base_count + (1 if i < extra else 0)
                            subject_counts[subj.id] = cnt
                        subject_map = {subj.id: subj for subj in subjects}

                        # Assign one random free period per day for this section
                        free_periods = {}
                        for day in days:
                            # choose a free period from all non-lunch periods
                            free_periods[day] = random.choice(periods).id

                        # Identify subjects requiring daily coverage (>=6 slots)
                        fixed_subjects = [sid for sid, cnt in subject_counts.items() if cnt >= 6]
                        fixed_periods = {}  # map subj_id -> chosen period_id
                        occupied_fixed = set()
                        if fixed_subjects:
                            # Sort by count descending to assign largest first
                            fixed_subjects.sort(key=lambda sid: subject_counts[sid], reverse=True)
                            candidate_period_ids = [p.id for p in periods]
                            for sid in fixed_subjects:
                                # Find period candidates not used and not equal to any free period
                                candidates = [pid for pid in candidate_period_ids if pid not in occupied_fixed]
                                candidates = [
                                    pid for pid in candidates
                                    if all(pid != free_periods[day] for day in days)
                                ]
                                if not candidates:
                                    logger.warning(f"No single period available for daily subject {subject_map[sid].name}. Will distribute normally.")
                                    continue
                                chosen_pid = random.choice(candidates)
                                fixed_periods[sid] = chosen_pid
                                occupied_fixed.add(chosen_pid)
                            # Reduce counts by one per day for fixed subjects
                            for sid, pid in fixed_periods.items():
                                subject_counts[sid] -= 6

                        # Now schedule day by day
                        for day in days:
                            # Place fixed subjects first (they occupy their period each day)
                            for sid, pid in fixed_periods.items():
                                # Assign a teacher for this subject-period if not already done
                                subj = subject_map[sid]
                                # Select interested teachers who are free this day, this period
                                teacher_ids = list(TeacherInterest.objects.filter(subject=subj).values_list('teacher_id', flat=True))
                                # Filter by availability
                                available = [t for t in teacher_ids if pid not in teacher_busy.get(t, {}).get(day, set())]
                                if not available:
                                    logger.error(f"No available teacher for fixed subject {subj.name} on {day} period {pid}.")
                                    continue
                                # Choose teacher with least load to balance assignments
                                min_load = min(teacher_load[t] for t in available)
                                candidates = [t for t in available if teacher_load[t] == min_load]
                                teacher_id = random.choice(candidates)
                                # Mark teacher busy and update load
                                teacher_busy[teacher_id][day].add(pid)
                                teacher_load[teacher_id] += 1
                                # Create the timetable entry
                                period_instance=Period.objects.filter(pk=int(pid)).first()
                                subject_instance = Subject.objects.filter(pk=sid).first()
                                teacher_instance = Teacher.objects.filter(pk=teacher_id).first()

                                print("Period Instance",period_instance)
                                TimetableEntry.objects.create(
                                    school_class=section.school_class,
                                    section=section,
                                    day=day,
                                    period=period_instance,
                                    subject=subject_instance,
                                    teacher=teacher_instance
                                )

                            # Fill remaining periods
                            for period in periods:
                                pid = period.id
                                # Skip lunch and the section's free period
                                if lunch_period and pid == lunch_period.id:
                                    continue
                                if pid == free_periods[day]:
                                    continue
                                # Skip fixed subjects' reserved periods
                                if pid in fixed_periods.values():
                                    continue
                                # Find any subject with remaining count > 0
                                remaining_subjects = [sid for sid, cnt in subject_counts.items() if cnt > 0]
                                if not remaining_subjects:
                                    break  # no more subjects to schedule
                                # Try subjects in order of highest remaining count
                                remaining_subjects.sort(key=lambda sid: subject_counts[sid], reverse=True)
                                assigned = False
                                for sid in remaining_subjects:
                                    subj = subject_map[sid]
                                    # Find available teachers for this subject
                                    teacher_ids = list(TeacherInterest.objects.filter(subject=subj).values_list('teacher_id', flat=True))
                                    available = [t for t in teacher_ids if pid not in teacher_busy.get(t, {}).get(day, set())]
                                    if not available:
                                        continue  # try next subject
                                    # Pick teacher with least current load
                                    min_load = min(teacher_load[t] for t in available)
                                    candidates = [t for t in available if teacher_load[t] == min_load]
                                    teacher_id = random.choice(candidates)
                                    # Assign and update
                                    teacher_busy[teacher_id][day].add(pid)
                                    teacher_load[teacher_id] += 1
                                    subject_counts[sid] -= 1
                                    subject_instance = Subject.objects.filter(pk=sid).first()
                                    teacher_instance = Teacher.objects.filter(pk=teacher_id).first()
                                    TimetableEntry.objects.create(
                                        school_class=section.school_class,
                                        section=section,
                                        day=day,
                                        period=period,
                                        subject=subject_instance,
                                        teacher=teacher_instance
                                    )
                                    assigned = True
                                    break
                                if not assigned:
                                    logger.warning(f"Could not assign any subject to {section} on {day} period {pid} (no available teachers).")
                                    # Slot remains unfilled

                        logger.info(f"Completed scheduling for section {section}.")

                logger.info("Timetable generation completed successfully.")
                return HttpResponse("Timetable generated successfully.")
        except Exception as e:
            logger.error("Error generating timetable: %s", e)
            return HttpResponseServerError(f"Error generating timetable: {e}")
   
    def timetable_add(request):
        if request.method == 'POST':
            form = TimetableEntryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,'Timetable Entry Added')
                return redirect('timetable_list', class_id=form.cleaned_data['school_class'].id, section_id=form.cleaned_data['section'].id)
        else:
            form = TimetableEntryForm()
        
        return render(request, 'pages/admin/add_timetable.html', {'form': form, 'title': 'Add Timetable Entry'})
    
    def timetable_edit(request, entry_id):
        entry = get_object_or_404(TimetableEntry, id=entry_id)
        if request.method == 'POST':
            form = TimetableEntryForm(request.POST, instance=entry)
            if form.is_valid():
                form.save()
                return redirect('timetable_list', class_id=entry.school_class.id, section_id=entry.section.id)
        else:
            form = TimetableEntryForm(instance=entry)
        
        return render(request, 'pages/admin/add_timetable.html', {'form': form, 'title': 'Edit Timetable Entry'})
    
    def timetable_delete(request, entry_id):
        entry = get_object_or_404(TimetableEntry, id=entry_id)
        class_id = entry.school_class.id
        section_id = entry.section.id
        entry.delete()
        return redirect('timetable_list', class_id=class_id, section_id=section_id)
        
    
    def add_salary_structure(request,user_id):
        user = get_object_or_404(User, id=user_id)
        employee = get_object_or_404(Employee, user=user)

        salary_structure = SalaryStructure.objects.filter(employee=employee).first()

        
        if request.method == 'POST':

            form = SalaryStructureForm(request.POST,instance=salary_structure)
            if form.is_valid():
                structure = form.save(commit=False)
                structure.employee = employee  # ✅ Assign employee here
                structure.save()
                return redirect('manage_teacher')  # Replace with your view name
        else:
            form = SalaryStructureForm(instance=salary_structure)

        return render(request, 'pages/admin/add_salary_structure.html', {'form': form})
    
    def employee_attendance_report(request):
        employees = Employee.objects.select_related('user').all()
        

        # Get unique attendance dates
        dates = EmployeeAttendance.objects.annotate(date_only=TruncDate('date')) \
                                .values_list('date_only', flat=True) \
                                .distinct() \
                                .order_by('date_only')

        # Build dictionary of attendance data
        attendance_data = {}
        attendances = EmployeeAttendance.objects.annotate(date_only=TruncDate('date')).all()

        for attendance in attendances:
            key = (attendance.employee_id, attendance.date_only)
            attendance_data[key] = attendance.status

        return render(request, 'pages/admin/employee_attendance_report.html', {
            'employees': employees,
            'dates': dates,
            'attendance_data': attendance_data,
        })
    

    def submit_employee_attendance(request, employee_id):
        print(employee_id)
        employee = get_object_or_404(Employee,pk=employee_id)
        status = request.POST.get('status')
        print(status)
        attendance = EmployeeAttendance.objects.create(
            employee = employee,
            status=status,
        )

        return redirect('employee_attendance_report')
    

    

    def create_salary_payment(request, employee_id):
        user = get_object_or_404(User, id=employee_id)
        employee = get_object_or_404(Employee, user=user)


        # Get last salary payment date
        last_payment = SalaryPayment.objects.filter(employee=employee).aggregate(Max('date'))['date__max']
        start_date = last_payment + timedelta(days=1) if last_payment else employee.date_joined
        end_date = timezone.now().date()

        # Get attendance between dates
        attendance_qs = EmployeeAttendance.objects.filter(
            employee=employee,
            date__range=(start_date, end_date)
        )

        # Count worked and absent days
        present_days = attendance_qs.filter(status='present').count()
        half_days = attendance_qs.filter(status='halfday').count()
        absent_days = attendance_qs.filter(status='absent').count()

        # Calculate effective worked/absent
        total_worked = present_days + (half_days * 0.5)
        total_absent = absent_days + (half_days * 0.5)

        # Get employee's salary structure
        try:
            structure = SalaryStructure.objects.get(employee=employee)
        except SalaryStructure.DoesNotExist:
            messages.error(request, "Salary structure not defined for this employee.")
            return redirect('salary_payment_list')

        # Create salary payment record
        payment = SalaryPayment.objects.create(
            employee=employee,
            salary_structure=structure,
            date=end_date,
            worked_days=int(total_worked),
            absent_days=int(total_absent),
        )

        messages.success(request, f"Salary generated for {employee.user.get_full_name()} from {start_date} to {end_date}.")
        return redirect('salary_payment_list')
    
    def salary_payment_list(request):
        payments = SalaryPayment.objects.select_related('employee__user').order_by('-date')

        # Optional filters (by employee name or date)
        query = request.GET.get('q')
        if query:
            payments = payments.filter(
                Q(employee__user__first_name__icontains=query) |
                Q(employee__user__last_name__icontains=query) |
                Q(date__icontains=query)
            )

        return render(request, 'pages/admin/salary_list.html', {
            'payments': payments,
            'query': query,
        })



        




def view_fee_receipt(request, receipt_id):
    fee = get_object_or_404(StudentFee, receipt_id=receipt_id)
    return render(request, 'pages/admin/fee_receipt.html', {'fee': fee})

    


def student_fee_summary(student):
    summary = []
    fee_types = FeesType.objects.filter(
        school_class=student.school_class,
        section=student.section
    )

    for fee_type in fee_types:
        # Total paid for this fee type
        paid = StudentFee.objects.filter(student=student, fee_type=fee_type).aggregate(
            total_paid=Sum('amount_paid')
        )['total_paid'] or 0

        due = fee_type.amount - paid

        # All transactions for this fee type and student
        transactions = StudentFee.objects.filter(
            student=student,
            fee_type=fee_type
        ).order_by('-payment_date')

        

        summary.append({
            'fee_type': fee_type,
            'total_amount': fee_type.amount,
            'paid': paid,
            'due': due,
            'transactions': transactions,  # List of StudentFee instances
        })
        

    return summary

def teacher_timetable_list(request):
    teachers = Teacher.objects.select_related('user').all()
    periods = Period.objects.all().order_by('start_time')

    # Structure: {teacher: {day: {period_id: entry}}}
    teacher_timetables = {}

   
    for teacher in teachers:
        if teacher.user.is_staff ==False:
            continue
            
        print(teacher)
        timetable_entries = TimetableEntry.objects.filter(teacher=teacher).select_related(
            'subject', 'school_class', 'section', 'period'
        )

        day_period_map = defaultdict(dict)
        for entry in timetable_entries:
            day_period_map[entry.day][entry.period.id] = entry

        teacher_timetables[teacher] = dict(day_period_map)

    context = {
        'teachers': teachers,
        'periods': periods,
        'days': DayChoices.choices,
        'teacher_timetables': teacher_timetables,
    }
    return render(request, 'pages/admin/teacher_timetable_list.html', context)

def timetable_list(request, class_id, section_id):


    classes = SchoolClass.objects.all()
    school_class = get_object_or_404(SchoolClass, id=class_id)
    section = get_object_or_404(Section, id=section_id)
    timetable_entries = TimetableEntry.objects.filter(
        school_class=school_class,
        section=section
    ).select_related('subject', 'teacher', 'period')

    # Organize entries by day and period.id
    timetable = defaultdict(dict)
    for entry in timetable_entries:

        timetable[entry.day][entry.period.id] = entry
 

    context = {
        'classes':classes,
        'school_class': school_class,
        'section': section,
        'timetable': dict(timetable),
        'days': DayChoices.choices,  # E.g. [(1, "Monday"), (2, "Tuesday"), ...]
        'periods': Period.objects.all().order_by('start_time'),
    }
    return render(request, 'pages/admin/timetable_list.html', context)


def filter_timetable (request):
    if request.method == 'POST':
        class_id = request.POST.get('school_class')
        section_id = request.POST.get('section')
        return redirect('timetable_list', class_id=class_id, section_id=section_id)
    
def timetable_list_all(request):
    classes = SchoolClass.objects.prefetch_related('sections')
    periods = Period.objects.all().order_by('start_time')
    days = DayChoices.choices  # E.g. [(1, 'Monday'), (2, 'Tuesday'), ...]

    # Nested dictionary: timetable[(class_id, section_id)][day][period_id] = entry
    timetable = defaultdict(lambda: defaultdict(dict))

    entries = TimetableEntry.objects.select_related('subject', 'teacher', 'period', 'school_class', 'section')
    for entry in entries:
        key = f"{entry.school_class.id}_{entry.section.id}"
        
        timetable[key][entry.day][entry.period.id] = entry
        # print(entry.day)

        

    context = {
        'classes': classes,
        'timetable': dict(timetable),
        'days': days,
        'periods': periods,
    }
    # print(timetable)
    return render(request, 'pages/admin/timetable_list_all.html', context)