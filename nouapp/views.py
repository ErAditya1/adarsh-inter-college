from django.shortcuts import render,HttpResponse,redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .models import *
from .decorators import user_type_required

from datetime import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .utils import send_registration_success_email, send_password_reset_email ,send_notification_email
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



def load_branches(request):
    print("Loading branches...")
    program_id = request.GET.get('program_id')
    
    print("Program ID:", program_id)
    branches = Branch.objects.filter(program_id=program_id).all()
    print(branches)
    return JsonResponse(list(branches.values('id', 'name')), safe=False)

def load_years(request):
    branch_id = request.GET.get('branch_id')
    years = Year.objects.filter(branch_id=branch_id).all()
    return JsonResponse(list(years.values('id', 'name')), safe=False)

def load_subjects(request):
    year_id = request.GET.get('year_id')
    subjects = Subject.objects.filter(year_id=year_id).all()
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

def generate_roll_number(pg, br, yr):
    current_year = datetime.now().year

    program = get_object_or_404(Program, pk=pg)
    branch = get_object_or_404(Branch, pk=br)
    year = get_object_or_404(Year, pk=yr)

    # Filter existing students in the same Program + Branch + Year
    existing_students = Student.objects.filter(
        program=program,
        branch=branch,
        year=year
    )

    student_number = existing_students.count() + 1

    # Make sure student_number is 3-digits (e.g., 001, 042, 105)
    formatted_number = f"{student_number:03d}"

    rollno = f"S{current_year}{branch.branch_code}{year.id}{formatted_number}"

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
        programs = Program.objects.all()
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
            program = request.POST.get('program')
            branch = request.POST.get('branch')
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

            if program:
                student.program = get_object_or_404(Program, pk=program)
            if branch:
                student.branch = get_object_or_404(Branch, pk=branch)
            if year:
                student.year = get_object_or_404(Year, pk=year)

            student.save()

            messages.success(request, "Profile updated successfully")
            return redirect('student-profile')

        return render(request, 'pages/student/update_profile.html', {
            'programs': programs,
            'student': student,
            'user': user
        })



    def study_material(request):

        student = get_object_or_404(Student, user_id=request.user.id)
        studymaterials = StudyMaterial.objects.filter(program=student.program, branch=student.branch, year=student.year)

        return render(request, 'pages/student/study_material.html',{'studymaterials':studymaterials})

    def assesments(request):
        student = get_object_or_404(Student, user_id=request.user.id)
        assesments = Assesment.objects.filter(program=student.program, branch=student.branch, year=student.year)

        return render(request, 'pages/student/assignments.html',{'assesments': assesments})


    def lectures(request):
        student = get_object_or_404(Student, user_id=request.user.id)
        lectures = Lecture.objects.filter(program=student.program, branch=student.branch, year=student.year)

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
            programs = Program.objects.all()
            # If no student is found, redirect to a different template or page
            return render(request, 'pages/guest/home.html',{'programs': programs})



    
    def profile(request):
        
        user = request.user  
        
        return render(request, 'pages/guest/profile.html', {'user': user})
       
    def admission_apply(request):
        user = request.user
        programs = Program.objects.all()
        try:
            student = get_logged_in_student(request)
            if student:
                messages.info(request, 'You are already applied for admission')
                return redirect('guest_dashboard')
            else:
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
                    
                    pg = request.POST.get('program')
                    br = request.POST.get('branch')
                    yr = request.POST.get('year')

                    previous_school = request.POST.get('previous_school')
                    last_qualification = request.POST.get('last_qualification')
                    year_of_passing = request.POST.get('year_of_passing')
                    grade = request.POST.get('grade')



                    image = request.FILES.get('image')
                    aadhar_image = request.FILES.get('aadhar_image')


                    branch = get_object_or_404(Branch, pk=br)
                    year = get_object_or_404(Year, pk=yr)
                    program = get_object_or_404(Program, pk=pg)

                
                
                    rollnumber = generate_roll_number(pg, br, yr)



                    admission = Student(user=user,rollno = rollnumber,date_of_birth=date_of_birth,fname=fname,mname=mname,gender=gender,   program=program, branch=branch, year=year,aadhar_number=aadhar_number, previous_school=previous_school, last_qualification=last_qualification, year_of_passing=year_of_passing, grade=grade, city=city, state=state, country=country, postal_code=postal_code,address_line_1=address_line_1, address_line_2=address_line_2,  image=image, aadhar_imag=aadhar_image)
                    admission.save()
                    messages.success(request, "Admission application submitted successfully")
                    return redirect('admission_apply')
                return render(request, 'pages/guest/admission_apply.html',{"programs":programs})
        
        except Student.DoesNotExist:
            print ("Student does not exist")
        
            
            
    
    def drop_admission(request):
        user = request.user
        student = get_object_or_404(Student, user=user)
        
        student.delete()
           
        messages.success(request, "Admission dropped successfully")
        return redirect('guest_dashboard')
        
    def teaching_apply(request):

        if request.method == 'POST':
            user = request.user
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

            # Check if teacher already registered
            if Teacher.objects.filter(user=user).exists():
                messages.warning(request, "Teacher profile already exists.")
                return redirect('guest_dashboard')  # or render same page with context

            # Save teacher record
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
            return redirect('guest_dashboard')  # change to wherever you want after success

        return render(request, 'pages/guest/teaching_apply.html')
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
            pg = request.POST.get('program')
            br = request.POST.get('branch')
            yr = request.POST.get('year')
            sub = request.POST.get('subject')

            

            subject = get_object_or_404(Subject,pk=sub)
            year = get_object_or_404(Year, pk=yr)
            branch = get_object_or_404(Branch, pk=br)
            program = get_object_or_404(Program, pk=pg)

            TeacherInterest.objects.create(
                teacher=teacher,
                subject=subject,
                year=year,
                branch=branch,
                program=program
            )
            messages.success(request, "Teacher subject added successfully")
            return redirect('add_intrested_subjects')
        programs = Program.objects.all()
        
        subjects = teacher.interests.all()
        
        return render(request, 'pages/teacher/add_intrested_subjects.html',{'programs':programs,"subjects":subjects})
      
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
        programs = Program.objects.all()
        if request.method == 'POST':
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            if is_protected == 'False':
                is_protected = False
            print(file)
            if program:
                program = get_object_or_404(Program, pk=program)
            if branch:
                branch = get_object_or_404(Branch, pk=branch)
            if year:
                year = get_object_or_404(Year, pk=year)

            study_material = StudyMaterial(user=request.user,program=program, branch=branch, year=year, subject=subject, file_name=file_name, file=file,is_protected=is_protected)
            print(study_material)
            study_material.save()
            return redirect('upload_studymaterial')

        allStudyMaterials = StudyMaterial.objects.all()

        return render(request, 'pages/teacher/upload_study.html',{'programs':programs,  'studymaterials':allStudyMaterials})

    def delete_study_material(request,id):
        
        study_material = get_object_or_404(StudyMaterial,pk=id)
        study_material.delete()
        return redirect('upload_studymaterial')

    def upload_lectures(request):
        programs = Program.objects.all()
        if request.method == 'POST':
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            link = request.POST.get('link')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False
            if program:
                program = get_object_or_404(Program, pk=program)
            if branch:
                branch = get_object_or_404(Branch, pk=branch)
            if year:
                year = get_object_or_404(Year, pk=year)

            lecture = Lecture(user=request.user, program=program, branch=branch, year=year, subject=subject, file_name=file_name, link=link, is_protected=is_protected)
            print(lecture)
            lecture.save()
            return redirect('upload_lectures')
        allLectures = Lecture.objects.all()
        return render(request, 'pages/teacher/upload_lectures.html',{'programs':programs, "lectures":allLectures})

    def delete_lecture(request,id):
        
        lecture = get_object_or_404(Lecture,pk=id)
        lecture.delete()
        return redirect('upload_lectures')

    def upload_assesments(request):
        programs = Program.objects.all()
        if request.method == 'POST':
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False

            if program:
                program = get_object_or_404(Program, pk=program)
            if branch:
                branch = get_object_or_404(Branch, pk=branch)
            if year:
                year = get_object_or_404(Year, pk=year)

            assessment = Assesment(user=request.user, program=program, branch=branch, year=year, subject=subject, file_name=file_name, file=file, is_protected=is_protected)
            print(assessment)
            assessment.save()
            return redirect('upload_assesments')
        allAssessments = Assesment.objects.all()

        return render(request, 'pages/teacher/upload_assesments.html',{'programs':programs, 'assessments':allAssessments})

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
        programs = Program.objects.all()
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
                
            

        return render(request, 'pages/teacher/updateprofile.html', {'programs': programs,  'user':user})

    def save_profile(request):
        programs = Program.objects.all()
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
        program = request.POST.get('program')
        branch = request.POST.get('branch')
        year = request.POST.get('year')
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
        if program:
            student.program = program
        if age :
            student.age = age
        if fname:
            student.fname = fname
        if mname:
            student.mname = mname
        if branch:
            student.branch = branch
        if year:
            student.year = year
        student.save()
        print("Student saved")

        messages.success(request, "Profile updated successfully")
        # return redirect('student_profile')
        return render(request, 'pages/student/update_profile.html', {'programs': programs, 'user':user})
        # return redirect('student_dashboard')
            
            

        # return render(request, 'pages/student/update_profile.html', {'programs': programs, 'student': student, 'user':user})

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
        programs = Program.objects.all()
        students = Student.objects.select_related('user').filter(admission_status='approved')
        is_filtered = False
        if request.method == 'GET':
            program = request.GET.get('program')
            branch = request.GET.get('branch')
            year = request.GET.get('year')
            subject = request.GET.get('subject')
            
            if program:
                students = students.filter(program=program)
            if branch:
                students = students.filter(branch=branch)
            if year:
                is_filtered = True
                students = students.filter(year=year)
            if subject:
                students = students.filter(subject=subject)

        if request.method == 'POST':
        # getting values from form
            student_ids = request.POST.getlist('student_ids')   # list of student IDs
            program_id = request.GET.get('program')
            branch_id = request.GET.get('branch')
            year_id = request.GET.get('year')

            if not student_ids or not program_id or not branch_id or not year_id:
                messages.error(request, "Please select students and class details")
                return redirect('attendance')
            
            program = get_object_or_404(Program, pk=program_id)
            branch = get_object_or_404(Branch, pk=branch_id)
            year = get_object_or_404(Year, pk=year_id)
            

            for student_id in student_ids:

                status = request.POST.get(f'status_{student_id}') == 'present'  # status_present / status_absent
                is_attendance_exists = Attendance.objects.filter(student_id=student_id, program=program, branch=branch, year=year).exists()
                if is_attendance_exists:
                    attendance = Attendance.objects.get(student_id=student_id, program=program, branch=branch, year=year, date__date=datetime.now().date())
                    attendance.status = status
                    attendance.submitted_by = request.user
                    attendance.save()
                else:
                    Attendance.objects.create(
                        student_id=student_id,
                        program=program,
                        branch=branch,
                        year=year,
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
            'programs': programs,
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
        teacher.user_type="teacher" 
        if teacher.is_staff:
            teacher.is_staff = False
        else:
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
                student.user.role = 'guest'
            else:
                student.user.role = 'student'
                student.is_verified = True
            student.save()
            
            messages.success(request, "Admission status updated successfully")
            return redirect('students_admission_verification')
        
        

    def edit_student(request,id):
        programs = Program.objects.all()
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
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')

            if program:
                student.program = get_object_or_404(Program, pk=program)
            if branch:
                student.branch = get_object_or_404(Branch, pk=branch)
            if year:
                student.year = get_object_or_404(Year, pk=year)

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
        
            student.program = program
        
            student.age = age
    
            student.fname = fname
        
            student.mname = mname
        
            student.branch = branch
        
            student.year = year
            student.save()
            
            print("Student saved")

            messages.success(request, "Profile updated successfully")
            return redirect('manage_student')
            # return redirect('student_dashboard')
                
            

        return render(request, 'pages/student/update_profile.html', {'programs': programs, 'student': student, 'user':user})


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
        programs = Program.objects.all()
        if request.method == 'POST':
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            if is_protected == 'False':
                is_protected = False
            print(file)
            
            program = get_object_or_404(Program, pk=program)
        
            branch = get_object_or_404(Branch, pk=branch)
        
            year = get_object_or_404(Year, pk=year)

            study_material = StudyMaterial(user=request.user,program=program, branch=branch, year=year, subject=subject, file_name=file_name, file=file,is_protected=is_protected)
            print(study_material)
            study_material.save()
            return redirect('upload_studymaterial')

        allStudyMaterials = StudyMaterial.objects.all()

        return render(request, 'pages/admin/upload_study.html',{'programs':programs,  'studymaterials':allStudyMaterials})

    def delete_study_material(request,id):
        
        study_material = get_object_or_404(StudyMaterial,pk=id)
        study_material.delete()
        return redirect('upload_studymaterial')

    def upload_lectures(request):
        programs = Program.objects.all()
        if request.method == 'POST':
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            link = request.POST.get('link')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False
            program = get_object_or_404(Program, pk=program)
        
            branch = get_object_or_404(Branch, pk=branch)
        
            year = get_object_or_404(Year, pk=year)

            lecture = Lecture(user=request.user, program=program, branch=branch, year=year, subject=subject, file_name=file_name, link=link, is_protected=is_protected)
            print(lecture)
            lecture.save()
            return redirect('upload_lectures')
        allLectures = Lecture.objects.all()
        return render(request, 'pages/admin/upload_lectures.html',{'programs':programs, "lectures":allLectures})

    def delete_lecture(request,id):
        
        lecture = get_object_or_404(Lecture,pk=id)
        lecture.delete()
        return redirect('upload_lectures')

    def upload_assesments(request):
        programs = Program.objects.all()
        if request.method == 'POST':
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            file = request.FILES.get('file')
            is_protected = request.POST.get('is_protected')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False

            program = get_object_or_404(Program, pk=program)
        
            branch = get_object_or_404(Branch, pk=branch)
        
            year = get_object_or_404(Year, pk=year)

            assessment = Assesment(user=request.user, program=program, branch=branch, year=year, subject=subject, file_name=file_name, file=file, is_protected=is_protected)
            print(assessment)
            assessment.save()
            return redirect('upload_assesments')
        allAssessments = Assesment.objects.all()

        return render(request, 'pages/admin/upload_assesments.html',{'programs':programs, 'assessments':allAssessments})

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

    def add_programs(request):
        programs = Program.objects.all()
        if request.method == 'POST':
            program_name = request.POST.get('program_name')
            print(program_name)
            if program_name:
                Program.objects.create(name=program_name)
                messages.success(request, "Program added successfully")
            return redirect('add_programs')
        return render(request, 'pages/admin/add_programs.html', {'programs': programs})
    
    def delete_program(request,program_id):
        program = get_object_or_404(Program,id=program_id)
        program.delete()
        messages.success(request, "Program deleted successfully")
        return redirect('add_programs')
    
    
    def add_branches(request,program_id):
        branches = Branch.objects.filter(program_id=program_id).all()
        program = get_object_or_404(Program,id=program_id)
        if request.method == 'POST':
            branch_name = request.POST.get('branch_name')
            branch_code = request.POST.get('branch_code')
            if program_id and branch_name and branch_code:
                program = get_object_or_404(Program,id=program_id)
                Branch.objects.create(program=program, name=branch_name, branch_code=branch_code)
                messages.success(request, "Branch added successfully")
            return redirect('add_branches', program_id=program_id)
        return render(request, 'pages/admin/add_branches.html', {'branches': branches, 'program': program})
    
    def delete_branch(request,branch_id):
        print(branch_id)
        branch = get_object_or_404(Branch,id=branch_id)
        branch.delete()
        messages.success(request, "Branch deleted successfully")
        return redirect('add_branches',program_id=branch.program.id)
    

    def add_years(request,program_id, branch_id):

        
        years = Year.objects.filter(branch_id=branch_id).all()
        branch = get_object_or_404(Branch,id=branch_id)
        program = get_object_or_404(Program,id=program_id)
        if request.method == 'POST':
            year_name = request.POST.get('year_name')
            # fees = request.POST.get('fees')

            if branch_id and year_name :
                branch = get_object_or_404(Branch,id=branch_id)
                Year.objects.create(branch=branch, name=year_name)
                messages.success(request, "Year added successfully")
            return redirect('add_years', program_id=program_id, branch_id=branch_id)
        return render(request, 'pages/admin/add_years.html', {'years': years, 'branch': branch, 'program': program})
    def delete_year(request,year_id):
        year = get_object_or_404(Year,id=year_id)
        year.delete()
        messages.success(request, "Year deleted successfully")
        return redirect('add_years', program_id=year.branch.program.id, branch_id=year.branch.id)
    
    def add_fees(request, program_id, branch_id, year_id):
        fees = FeesType.objects.filter(year_id=year_id).all()
        year = get_object_or_404(Year,id=year_id)
        branch = get_object_or_404(Branch,id=branch_id)
        program = get_object_or_404(Program,id=program_id)
        if request.method == 'POST':
            fee_name = request.POST.get('fee_name')
            amount = request.POST.get('amount')
            if year_id and fee_name and amount:
                FeesType.objects.create(year=year, name=fee_name, amount=amount, program=program, branch=branch)
                messages.success(request, "Fees type added successfully")
            return redirect('add_fees', program_id=program_id, branch_id=branch_id, year_id=year_id)
        return render(request, 'pages/admin/add_fees.html', {'fees': fees, 'year': year, 'branch': branch, 'program': program})
    def delete_fees(request, fee_id):
        fee = get_object_or_404(FeesType,id=fee_id)
        fee.delete()
        messages.success(request, "Fees type deleted successfully")
        return redirect('add_fees', program_id=fee.year.branch.program.id, branch_id=fee.year.branch.id, year_id=fee.year.id)
    
    def add_entrance(request, program_id, branch_id, year_id):
        entrances = Entrance.objects.filter(year_id=year_id).all()
        
        year = get_object_or_404(Year,id=year_id)
        branch = get_object_or_404(Branch,id=branch_id)
        program = get_object_or_404(Program,id=program_id)
        if request.method == 'POST':
            entrance_name = request.POST.get('exam_name')
            date = request.POST.get('date')
            time = request.POST.get('time')
            duration = request.POST.get('duration')
            if year_id and entrance_name and date and time and duration:
               
                Entrance.objects.create(year=year, name=entrance_name, date=date, time=time, duration=duration,program=program, branch=branch)
                messages.success(request, "Entrance exam added successfully")
            return redirect('add_entrance', program_id=program_id, branch_id=branch_id, year_id=year_id)
        return render(request, 'pages/admin/add_entrance.html', {'entrances': entrances, 'year': year, 'branch': branch, 'program': program})
    def delete_entrance(request, entrance_id):
        entrance = get_object_or_404(Entrance,id=entrance_id)
        entrance.delete()
        messages.success(request, "Entrance exam deleted successfully")
        return redirect('add_Entrance', program_id=entrance.year.branch.program.id, branch_id=entrance.year.branch.id, year_id=entrance.year.id)
    
    def add_subjects(request, program_id, branch_id, year_id):
        subjects = Subject.objects.filter(year_id=year_id).all()
        year = get_object_or_404(Year,id=year_id)
        branch = get_object_or_404(Branch,id=branch_id)
        program = get_object_or_404(Program,id=program_id)
        if request.method == 'POST':
            subject_name = request.POST.get('subject_name')
            subject_code = request.POST.get('subject_code')
            if year_id and subject_name and subject_code:
               
                Subject.objects.create(year=year, name=subject_name, subject_code=subject_code,program=program, branch=branch)
                messages.success(request, "Subject added successfully")
            return redirect('add_subjects', program_id=program_id, branch_id=branch_id, year_id=year_id)
        return render(request, 'pages/admin/add_subjects.html', {'subjects': subjects, 'year': year, 'branch': branch, 'program': program})
    def delete_subject(request,subject_id):
        subject = get_object_or_404(Subject,id=subject_id)
        subject.delete()
        messages.success(request, "Subject deleted successfully")
        return redirect('add_subjects', program_id=subject.year.branch.program.id, branch_id=subject.year.branch.id, year_id=subject.year.id)
        


    

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


