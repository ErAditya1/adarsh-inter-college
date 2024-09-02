
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
# Create your models here.

class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('guest', 'Guest'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    email = models.EmailField(max_length=254)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_detailed = models.BooleanField(default=False)

    # Fixing the clashes with related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Change related_name here
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Change related_name here
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
   

    def __str__(self):
        return self.username

class Student(models.Model):
    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    PROGRAMS = (
        ('bt', 'BTech'),
        ('mtech', 'MTech'),
        ('phd', 'PhD'),
        ('diploma', 'Diploma'),
        ('bca', 'BCA'),
        ('mca', 'MCA')
    )
    YEAR =(
        ('first', 'First Year'),
        ('second', 'Second Year'),
        ('third', 'Third Year'),
        ('fourth', 'Fourth Year'),
        
    )
    user = models.OneToOneField(User , on_delete=models.CASCADE,  related_name='student' )
    rollno = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=50)
    age = models.CharField( max_length=4)
    fname = models.CharField(max_length=50)
    mname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices= GENDER)
    address = models.CharField(max_length=255)
    program = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    year = models.CharField( max_length=50)
    mobile = models.CharField(max_length=14)
    # email = models.EmailField( max_length=254)
    avatar = models.ImageField(upload_to='students')
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='teacher')
    employee_id = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='admin')
    employee_id = models.CharField(max_length=20)
    office = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
 
class StudyMaterial(models.Model):               # upload study material
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_materials')
    program = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    year = models.CharField( max_length=50)
    subject = models.CharField( max_length=500)
    file_name = models.CharField( max_length=200)
    file = models.FileField(upload_to='myimage')
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject

class Assesment(models.Model):  #Upload Asignment
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, null = True, on_delete=models.CASCADE, related_name='assesments')

    program = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    year = models.CharField( max_length=50)
    subject = models.CharField( max_length=500)
    file_name = models.CharField( max_length=200)
    file = models.FileField(upload_to='myimage')
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject


class Lecture(models.Model):  # Upload Lectures
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, null = True, on_delete=models.CASCADE, related_name='lectures')

    program = models.CharField(max_length=200)
    branch = models.CharField(max_length=50)
    year = models.CharField( max_length=50)
    subject = models.CharField( max_length=50)
    file_name = models.CharField( max_length=200)
    link = models.CharField( max_length=500)
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self): 
        return self.subject

class Complaint(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    student = models.ForeignKey(Student,null = True, on_delete=models.CASCADE, related_name='complaints')
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_complaints')
    # admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admin_complaints')
    subject = models.CharField(max_length=200)
    comp = models.TextField(max_length = 1000)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject

class Feedback(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    student = models.ForeignKey(Student,null = True, on_delete=models.CASCADE, related_name='feedbacks')
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_feedback')
    # admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admin_feedback')
    subject = models.CharField(max_length=200)
    feed = models.TextField(max_length = 1000)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subject

class Enquiry(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ENQUIRY',null=True)
    name = models.CharField( max_length=50)
    gender = models.CharField( max_length=50)
    address = models.CharField( max_length=300)
    mobile = models.CharField( max_length=15)
    email = models.EmailField( max_length=254)
    text = models.CharField( max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='notifications', null=True)
    text = models.CharField(max_length=500)
    link = models.CharField( max_length=350)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class Program(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Branch(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Year(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='years')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


