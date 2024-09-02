from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class UserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Define your user type requirements here
        protected_urls = {

            'guest':'/guest/',
            'student': '/student/',
            'teacher': '/teacher/',
            'admin': '/admin/',
            'superadmin': '/superadmin/',
        }
        public_urls = ['/login/', '/signup/','/','/about/','/contact/']

        if request.user.is_authenticated:
            if request.user.is_superuser:
                # Superusers should have access to all /admin/ and /superadmin/ URLs
                if request.path.startswith('/superadmin/') or request.path.startswith('/admin/'):
                    return None
               
                for user_type, url_prefix in protected_urls.items():
                    if user_type not in ['admin', 'superadmin'] and request.path.startswith(url_prefix):
                        return redirect('admin_dashboard')
        # print(request.user.is_authenticated)
        if request.user.is_authenticated and not request.user.is_detailed and not request.user.user_type != 'guest':
            if request.user.user_type =='student' and request.path != '/student/add_student_details':
                return redirect('add_student_details')
        
        if request.path == '/student/add_student_details' and request.user.is_detailed:
            return redirect('home')

        

        if request.path in public_urls and request.user.is_authenticated:
            print("You are authenticated")
            if request.user.user_type =='guest':
                return redirect('guest_dashboard')
            if request.user.user_type =='student':
                if request.user.is_detailed:
                    print('Student is detailed')
                    return redirect('student_dashboard')
                elif not request.user.is_detailed:
                    print('Student is not detailed')
                    return redirect('add_student_details')

            if  request.user.is_superuser:
                return redirect('admin_dashboard')
            if request.user.user_type == 'admin' and request.user.is_staff:
                return redirect('admin_dashboard')
            elif not request.path.startswith('/guest/') : 
                messages.error(request, 'You do not have permission to login to admin')
                return redirect('guest_dashboard')
             
            if request.user.user_type == 'teacher' and request.user.is_staff and request.user.is_detailed:
                return redirect('teacher_dashboard')
            elif request.user.user_type == 'teacher' and not request.user.is_detailed:
                print('Teacher is not detailed')
                return redirect('add_teacher_details')
            elif not request.path.startswith('/guest/'): 
                messages.error(request, 'You do not have permission to login to teacher')
                return redirect('guest_dashboard')

            if  request.user.is_superuser:
                print("in super admin")
                return redirect('superadmin_dashboard')
        
        

        for user_type, url_prefix in protected_urls.items():
           
            if request.path.startswith(url_prefix):
                print("In protected url prefix")
                
            
                if not request.user.is_authenticated :
                    print ('Not Authenticated')
                    return redirect('login')

                
               
                elif request.user.is_authenticated and request.user.user_type != user_type :
                     # Redirect to user page or an error page
                    
                    if request.path.startswith('/guest/'):
                        return None
                    if request.user.user_type =='student':
                        if request.user.is_detailed:
                            print('Student is detailed')
                            return redirect('student_dashboard')
                        elif not request.user.is_detailed:
                            print('Student is not detailed')
                            return redirect('add_student_details')

                    

                    if request.user.user_type =='teacher' and not request.user.is_detailed:
                        return redirect('add_teacher_details')

                    if request.user.user_type == 'admin' and request.user.is_staff and request.user.is_detailed:
                        return redirect('admin_dashboard')
                    else: 
                        messages.error(request, 'You do not have permission to login to admin')
                        return redirect('guest_dashboard')
             
                    if request.user.user_type == 'teacher' and request.user.is_staff:
                        return redirect('teacher_dashboard')
                    else: 
                        messages.error(request, 'You do not have permission to login to teacher')
                        return redirect('guest_dashboard')

                    if  request.user.is_superuser:
                        print("in super admin")
                        return redirect('superadmin_dashboard')
                
                        
                else:
                    
                    return redirect('guest_dashboard')
               
        return None



# from django.shortcuts import redirect
# from .utils import get_user

# class UserTypeMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         return response

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         # Define your user type requirements here
#         protected_urls = {
#             'student': '/student_dashboard/',
#             'teacher': '/teacher_dashboard/',
#             'admin': '/admin_dashboard/',
#         }
#         public_urls = ['/login/', '/signup/']
#         user = get_user(request)
#         current_path = request.path

#         for user_type, url_prefix in protected_urls.items():
#             if user :
#                 if  and request.path.startswith(url_prefix) and user.get('is_authenticated'):
#                     # print(user_type)

#                     print (current_path)
#                     print("Current path: " + current_path)
                    


#                     if user.get('user_type') != user_type :
#                         print("I am in condition 2")
#                         if user.get('user_type') == 'student':
#                             return redirect('student_dashboard')
#                         if user.get('user_type') == 'admin':
#                             return redirect('admin_dashboard')
#                         if user.get('user_type') == 'teacher':
#                             return redirect('teacher_dashboard')

#                 elif current_path in public_urls and user.get('is_authenticated'):
#                     print("I am in else condition ")
#                     if user.get('user_type') == 'student':
#                         return redirect('student_dashboard')
#                     if user.get('user_type') == 'admin':
#                         return redirect('admin_dashboard')
#                     if user.get('user_type') == 'teacher':
#                         return redirect('teacher_dashboard')
               

                    
#         return None
