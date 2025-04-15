
from .models import User
def site_info(request):
    user = request.user
  
    return {
        'user': user,
        'user_ip': request.META.get('REMOTE_ADDR')
    }