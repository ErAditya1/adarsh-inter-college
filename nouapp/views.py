from django.shortcuts import render,HttpResponse,redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from .models import *
from .decorators import user_type_required

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



# Create your views here.
# @login_required(login_url='login')

def super_admin(request):
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
        
        # student = get_object_or_404(Student,user_id=user.id)
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


   




# Admin Dashboard and views --------------------------------------------------------
# @user_type_required('admin')
class AdminViews():

    def verify_user(request,id):
        user = get_object_or_404(User,pk=id)
        if user.is_verified:
            user.is_verified = False
        else:
            user.is_verified = True
        user.save()
        return redirect('manage_user')

    def verify_admin(request,id):
        staff = get_object_or_404(User,pk=id)
        if staff.is_staff:
            staff.is_staff = False
        else:
            staff.is_staff = True
        staff.save()
        return redirect('manage_admin')
    
    def verify_teacher(request,id):
        
        teacher = get_object_or_404(User,pk=id)
         
        if teacher.is_staff:
            teacher.user_type="guest"
            teacher.is_staff = False
        else:
            teacher.user_type="teacher"
            teacher.is_staff = True
        teacher.save()
        return redirect('manage_teacher')

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

    
    
    def manage_student(request):
        st = Student.objects.filter(is_verified=True)
        return render(request, 'pages/admin/manage_student.html',{'students': st})

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
                    school_class_id=school_class_id,
                    section_id=section_id,
                    previous_school=previous_school,
                    last_qualification=last_qualification,
                    year_of_passing=2024,
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
            dob = request.POST.get('dob')
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
                messages.success(request, f"Teacher {first_name} registered successfully.")
                send_admin_teacher_registration_email(user_email=email, user_name=f"{first_name} {last_name}", username=username, password=password, login_url=None)
                return redirect('register_teacher')  # Replace with your actual view
            except Exception as e:
                messages.error(request, f"Error occurred: {e}")


        return render(request, "pages/admin/register_teacher.html")

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
                
            

        return render(request, 'pages/student/update_profile.html', {'classes': classes, 'student': student, 'user':user})


    def manage_teacher(request):
        te = Teacher.objects.all()
        return render(request, 'pages/admin/manage_teacher.html', {'teachers': te})

    def edit_teacher(request,id):
        te = get_object_or_404(Teacher,pk=id)
        if request.method == 'POST':
            te.first_name = request.POST.get('first_name')
            te.last_name = request.POST.get('last_name')
            te.email = request.POST.get('email')
            te.mobile = request.POST.get('mobile')
            te.save()
            return redirect('manage_teacher')
        return render(request, 'pages/admin/edit_teacher.html', {'teacher': te})

    def manage_admin(request):
        ad = Admin.objects.all()
        return render(request, 'pages/admin/manage_admin.html', {'admins': ad})

    def delete_user(request,id):
        u = get_object_or_404(User,pk=id)
        u.delete()
        return redirect('manage_user')

    def delete_student(request,id):
        st = get_object_or_404(User,pk=id)
        st.delete()
        return redirect('manage_student')

    def delete_teacher(request  ,id):
        te = get_object_or_404(User,pk=id)
        te.delete()
        return redirect('manage_teacher')

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