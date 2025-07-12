from django.shortcuts import redirect,HttpResponse
from django.urls import reverse
from django.contrib import messages


# >>>>>># Middleware to handle user type-based access control
# >>>>>># This middleware checks the user type and redirects accordingly


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
        public_urls = ['/login/', '/register/','/','/about/','/contact/']

        if request.user.is_authenticated:
            if request.user.is_superuser:
                # Superusers should have access to all /admin/ and /superadmin/ URLs
                if request.path.startswith('/superadmin/') or request.path.startswith('/admin/'):
                    return None
               
                for user_type, url_prefix in protected_urls.items():
                    if user_type not in ['admin', 'superadmin'] and request.path.startswith(url_prefix):
                        return redirect('admin_dashboard')
      
      

        

        if request.path in public_urls and request.user.is_authenticated:
            print("You are in Public urls")
            if request.user.user_type =='guest':
                return redirect('guest_dashboard')
                print("In guest vfid   1")

            if request.user.user_type =='student':
                
                return redirect('student_dashboard')
                

            if  request.user.is_superuser:
                print("in super admin")
                # return redirect('superadmin_dashboard')
                return redirect('admin_dashboard')
            if request.user.user_type == 'admin' :
                return redirect('admin_dashboard')
            # elif not request.path.startswith('/guest/' ) and not request.user.is_staff  :
            #     print("In Guest 2   admin dashboard") 
            #     messages.error(request, 'You do not have permission to login to admin')
            #     return HttpResponse( "You are not verified")
             
            if request.user.user_type == 'teacher' and  request.user.is_staff  :
                
                return redirect('teacher_dashboard')
            elif  not request.user.is_staff  :
                print('Teacher is not staff')
                return HttpResponse("You are not verified")
                
                

          
        
        

        for user_type, url_prefix in protected_urls.items():
           
            if request.path.startswith(url_prefix):

                print("In protected url prefix")
                
            
                if not request.user.is_authenticated:
                    print ('Not Authenticated')
                    messages.error(request,"Please Login")
                    return redirect('login')

                
               
                if request.user.is_authenticated and request.user.user_type != user_type :
                     # Redirect to user page or an error page

                    if request.user.user_type == 'guest':
                        print('Guest is not admin')
                        return redirect('guest_dashboard')
                    elif request.user.user_type =='student':
                        
                        print('Student is detailed')
                        return redirect('student_dashboard')
                    elif request.user.user_type == 'teacher' and request.user.is_staff :
                        
                        print('Teacher is staff')
                        return redirect('teacher_dashboard')
                    elif  not request.user.is_staff :
                        print('Teacher is not staff')
                        return HttpResponse('You are not verified teacher')
                    

                    elif request.user.user_type == 'admin' and  request.user.is_staff:
                        # if request.user.is_staff:
                        print('Admin is staff')
                        return redirect('admin_dashboard')
                    elif not request.user.is_staff:
                        print('Admin is not staff')
                        return HttpResponse('You are not verified teacher')
                
                    if  request.user.is_superuser:
                        print("in super admin")
                        return redirect('admin_dashboard')
                
                        
                    else: 
                        return None
            elif request.user.is_authenticated and request.user.user_type == user_type :
                if request.user.user_type == 'teacher' or request.user.user_type == 'admin':
                    if not request.user.is_staff:
                        print("in unverified teacher")
                        return HttpResponse('You are not verified teacher')
                   
               
        return None



