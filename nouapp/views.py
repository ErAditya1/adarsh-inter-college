from django.shortcuts import render,HttpResponse,redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .models import User, Admin, Teacher,Student,Feedback,Complaint, Branch, Year, Program,Enquiry,Notification
from .models import StudyMaterial,Assesment,Lecture
from .decorators import user_type_required
from django.urls import reverse
from datetime import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
# Create your views here.
# @login_required(login_url='login')

def super_admin(request):
    return redirect('/superadmin/')

def home(request):
    return render(request, 'pages/home.html')

# Create your views here.
def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    return render(request, 'pages/contact.html')




def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
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

       

        
        user = User(username=username, email=email, first_name = first_name , last_name = last_name , mobile = mobile, user_type=user_type, password= password_hashed)
        print(user)
        user.save()

                # Prepare email content
        subject = 'Registration Confirmation'
        message = f'''
        Thank you dear {user_type} {first_name} !!
        Your Are Successfuly Register Nou Egyan Protal
        Your Username, Email and Mobile This 
        Userid: {email}
        UserName: {username}
        Mobile: {mobile}
        Please fill your detail
        Link: http://localhost:8000/student/
        '''
        from_email = 'mradityaji2@gmail.com'
        recipient_list = [email]

        # Send email
        send_mail(subject, message, from_email, recipient_list)

        # Add success message and redirect
        messages.success(request, 'Registration successful! Please check your email for confirmation.')


        login(request, user)

        collegeCode = "0375"
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day
        if user.user_type == 'guest':
            
            return redirect('guest_dashboard')
        elif user.user_type == 'teacher':

            employee_id = f"S{collegeCode}{current_year}{current_month}{current_day}{user.id}"

            teacher = Teacher.objects.create(user=user,employee_id=employee_id)
            return redirect('add_teacher_details')
            
        elif user.user_type == 'admin':
            employee_id = f"A{collegeCode}{current_year}{current_month}{current_day}{user.id}"

            admin = Admin.objects.create(user=user,employee_id=employee_id)
            return redirect('admin_dashboard')
        elif user.user_type == 'student':
            
            name = user.first_name+' '+user.last_name
            mobile = user.mobile
            
            
            EnrollmentNo = f"S{collegeCode}{current_year}{current_month}{current_day}{user.id}"
            student = Student.objects.create(user=user, name=name,mobile=mobile,rollno = EnrollmentNo )
            return redirect('add_student_details')
           

    return render(request, 'registration/signup.html')

def add_student_details(request):
    
    # user = User.objects.get(pk=id)
    user = request.user
    
    name = user.first_name+' '+user.last_name
    mobile = user.mobile

    student = Student.objects.get(user=user)
    programs = Program.objects.all()
    if request.method == 'POST':
        # rollno = request.POST.get('rollno')
        age = request.POST.get('age')
        avatar = request.POST.get('avatar')
        address = request.POST.get('address')
        fname = request.POST.get('fname')
        mname = request.POST.get('mname')
        gender = request.POST.get('gender')
        program = request.POST.get('program')
        branch = request.POST.get('branch')
        year = request.POST.get('year')
        program  = Program.objects.get(pk=program).name
        branch = Branch.objects.get(pk=branch).name
        year = Year.objects.get(pk=year).name
        
        
        # student.rollno = rollno
        student.age = age
        student.avatar = avatar
        student.address = address
        student.fname = fname
        student.mname = mname
        student.gender = gender
        student.program = program
        student.branch = branch
        student.year = year
        print(student)    
        # print(student)
        if student:
            student.save()
            
            us= User.objects.get(username=user.username)
            us.is_detailed = True
            us.save()
            return redirect('student_dashboard')
            
            messages.success(request, "Student details added successfully")
            return redirect('student_dashboard')
        
           
 
    return render (request, 'registration/studendetails.html',{"user":user,'programs':programs, "student":student})
    
def add_teacher_details(request):
    user = request.user
    teacher = Teacher.objects.get(user=user)
    print(teacher)
    if request.method == 'POST':
        
        specialization = request.POST.get('specialization')

        
        print(specialization)
        print(teacher)
        teacher.specialization = specialization
        teacher.save()
        if teacher :
            user.is_detailed = True
            user.save()
            messages.success(request, "Teacher details added successfully")
            return redirect('teacher_dashboard')
    return render (request, 'registration/teacher.html',{"employee_id":teacher.employee_id})
    


   

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
       
        
        subject = 'Registration Confirmation'
        message = f'''
        Thank you dear Aditya !!
        Your Are Successfuly Register Nou Egyan Protal
        Your Username, Email and Mobile This 
        
        UserName: {username}
        
        Please fill your detail
        Link: http://localhost:8000/student/
        '''
        from_email = 'mradityaji2@gmail.com'
        recipient_list = ["tempxtemp2@gmail.com"]

        # Send email
        send_mail(
            'Subject here',
            'Here is the message.',
            'mradityaji2@gmail.com',
            ['tempxtemp2@gmail.com'],
            fail_silently=False,
        )

        # Add success message and redirect
        messages.success(request, 'Registration successful! Please check your email for confirmation.')


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
            
            if user.user_type == 'admin' or user.is_superuser:
                return redirect('admin_dashboard')
            if user.user_type == 'teacher':
                return redirect('teacher_dashboard')
        else:
            return HttpResponse ("Username or Password is incorrect!!!") 
        

    else:
        messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')


def load_branches(request):
    print("Loading branches...")
    program_id = request.GET.get('program_id')
    print("Program ID:", program_id)
    branches = Branch.objects.filter(program_id=program_id).all()
    return JsonResponse(list(branches.values('id', 'name')), safe=False)

def load_years(request):
    branch_id = request.GET.get('branch_id')
    years = Year.objects.filter(branch_id=branch_id).all()
    return JsonResponse(list(years.values('id', 'name')), safe=False)

def save_enquiry(request):
    
    name = request.POST.get('name')
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
    return redirect('contact')



# Student Dashboard ----------------------------------------------------------------



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
        student = Student.objects.get(user_id=request.user.id)
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

            program  = Program.objects.get(pk=program).name
            branch = Branch.objects.get(pk=branch).name
            year = Year.objects.get(pk=year).name

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
            return redirect('student-profile')
            # return redirect('student_dashboard')
                
            

        return render(request, 'pages/student/update_profile.html', {'programs': programs, 'student': student, 'user':user})

    # def save_profile(request):
        programs = Program.objects.all()
        user = request.user
        student = Student.objects.get(user_id=request.user.id)
       
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



    def study_material(request):

        studymaterials = StudyMaterial.objects.all()

        return render(request, 'pages/student/study_material.html',{'studymaterials':studymaterials})

    def assesments(request):
        assesments = Assesment.objects.all()
        return render(request, 'pages/student/assignments.html',{'assesments': assesments})


    def lectures(request):
        lectures = Lecture.objects.all()
        return render(request, 'pages/student/lectures.html',{'lectures':lectures})

    def doubt_session(request):
        return render(request, 'pages/student/doubts_session.html')


    def register_complaint(request):
        if request.method == 'POST':
            subject = request.POST.get('subject')
            comp = request.POST.get('comp')
            student = get_object_or_404(Student,user_id=request.user.id)
            complain = Complaint(student=student, subject=subject, comp=comp)
            complain.save()
            
            messages.success(request, "Complaints submitted successfully")
            return redirect('register_complaint')
        return render(request, 'pages/student/register_complaint.html')


    def feedbacks(request):
        if request.method == 'POST':
            subject = request.POST.get('subject')
            feed = request.POST.get('feed')
            student = get_object_or_404(Student,user_id=request.user.id)
            feedback = Feedback(student=student, subject=subject, feed=feed)
            feedback.save()
            
            messages.success(request, "Feedback submitted successfully")
            return redirect('feedbacks')
        return render(request, 'pages/student/feedbacks.html')

    def read_notifications(request):
        notifications = Notification.objects.all()
        return render(request, 'pages/student/notifications.html', {'notifications': notifications})
   




# Guest Dash board ------------------------------------------------------------

class GuestViews():

    def dashboard(request):
        print("username:",request.user.username)
        
        return render(request, 'pages/guest/home.html')




    
    def profile(request):
        
        user = request.user  
        
        return render(request, 'pages/guest/profile.html', {'user': user})
       


    def update_profile(request):

        return render(request, 'pages/guest/update_profile.html')


    
    def study_material(request):
        return render(request, 'pages/guest/study_material.html')

   

    def feedbacks(request):
        if request.method == 'POST':
            subject = request.POST.get('subject')
            feed = request.POST.get('feed')
            student = Student.objects.get(user_id=request.user.id)
            feedback = Feedback(student=student, subject=subject, feed=feed)
            feedback.save()
            print(feedback)
            messages.success(request, "Feedback submitted successfully")
            return redirect('feedbacks')
        return render(request, 'pages/guest/feedbacks.html')

    
    
    
    def lectures(request):
        return render(request, 'pages/guest/lectures.html')




# Teachers dash views ------------------------------------------------------------


class TeacherViews():

    def dashboard(request):
    
        return render(request, 'pages/teacher/home.html')





# Admin Dashboard and views --------------------------------------------------------

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


    def manage_user(request):
        users = User.objects.all()
        return render(request, 'pages/admin/manage_user.html', {'users': users})


    def edit_user(request,id):
        u = User.objects.get_object_or_404(pk=id)
        if request.method == 'POST':
            u.first_name = request.POST.get('first_name')
            u.last_name = request.POST.get('last_name')
            u.email = request.POST.get('email')
            u.mobile = request.POST.get('mobile')
            u.save()
            return redirect('manage_user')
        return render(request, 'pages/admin/edit_user.html', {'user': u})


    def manage_student(request):
        st = Student.objects.all()
        return render(request, 'pages/admin/manage_student.html',{'students': st})

    def edit_student(request,id):
        st = Student.objects.get_object_or_404(pk=id)
        if request.method == 'POST':
            st.first_name = request.POST.get('first_name')
            st.last_name = request.POST.get('last_name')
            st.email = request.POST.get('email')
            st.mobile = request.POST.get('mobile')
            st.save()
            return redirect('manage_student')
        return render(request, 'pages/admin/edit_student.html', {'student': st})

    def manage_teacher(request):
        te = Teacher.objects.all()
        return render(request, 'pages/admin/manage_teacher.html', {'teachers': te})

    def edit_teacher(request,id):
        te = Teacher.objects.get_object_or_404(pk=id)
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
            else:
                is_protected =False
            print(file)
            program  = Program.objects.get(pk=program).name
            branch = Branch.objects.get(pk=branch).name
            year = Year.objects.get(pk=year).name

            study_material = StudyMaterial(user=request.user,program=program, branch=branch, year=year, subject=subject, file_name=file_name, file=file,is_protected=is_protected)
            print(study_material)
            study_material.save()
            return redirect('upload_studymaterial')

        allStudyMaterials = StudyMaterial.objects.all()

        return render(request, 'pages/admin/upload_study.html',{'programs':programs,  'allStudyMaterials':allStudyMaterials})

    def upload_lectures(request):
        programs = Program.objects.all()
        if request.method == 'POST':
            program = request.POST.get('program')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            subject = request.POST.get('subject')
            file_name = request.POST.get('file_name')
            link = request.POST.get('link')
            if is_protected == 'True':
                is_protected =True
            else:
                is_protected =False
            program  = Program.objects.get(pk=program).name
            branch = Branch.objects.get(pk=branch).name
            year = Year.objects.get(pk=year).name

            lecture = Lecture(user=request.user, program=program, branch=branch, year=year, subject=subject, file_name=file_name, link=link, is_protected=is_protected)
            print(lecture)
            lecture.save()
            return redirect('upload_lectures')
        allLectures = Lecture.objects.all()
        return render(request, 'pages/admin/upload_lectures.html',{'programs':programs, "allLectures":allLectures})

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

            program  = Program.objects.get(pk=program).name
            branch = Branch.objects.get(pk=branch).name
            year = Year.objects.get(pk=year).name

            assessment = Assesment(user=request.user, program=program, branch=branch, year=year, subject=subject, file_name=file_name, file=file, is_protected=is_protected)
            print(assessment)
            assessment.save()
            return redirect('upload_assesments')
        allAssessments = Assesment.objects.all()

        return render(request, 'pages/admin/upload_assesments.html',{'programs':programs, 'allAssessments':allAssessments})

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
            return redirect('add_notification')
        return render(request, 'pages/admin/add_notification.html')


    def show_programs(request):
        programs = Program.objects.all()
        return render(request, 'pages/admin/show_programs.html', {'programs': programs})

    

    def add_program(request):
        print('Adding programq ')
        program_name = request.POST.get('program_name')
        if program_name:
            Program.objects.create(name=program_name)
            return redirect('show_programs')  # Redirect after POST
      


    def add_branch(request):
       
        program_id = request.POST.get('program')
        branch_name = request.POST.get('branch_name')
        if program_id and branch_name:
            program = Program.objects.get(id=program_id)
            Branch.objects.create(program=program, name=branch_name)
            return redirect('show_programs')  # Redirect after POST
        


    def add_year(request):
        
        branch_id = request.POST.get('branch')
        year_name = request.POST.get('year_name')
        if branch_id and year_name:
            branch = Branch.objects.get(id=branch_id)
            Year.objects.create(branch=branch, name=year_name)
            return redirect('show_programs') 
       
