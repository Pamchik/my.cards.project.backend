from django.contrib.sessions.models import Session
from .models import AppUser

def username_check_by_session_key(session_key):

    try:
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        if user_id: 
            user = AppUser.objects.get(pk=user_id)
            username = user.username if user.username else 'unknown'
            return username

        return 'unknown'                
    except Session.DoesNotExist:
        return 'unknown'  
