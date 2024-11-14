from user_api.functions import username_check_by_session_key

class SessionKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.headers.get('Sec-Fetch-Site') == 'same-origin':
            session_key = request.session.session_key
            host = request.headers.get('Host')
        else:
            authorization_header = request.headers.get('Authorization')
            session_key = authorization_header.split('=')[1].strip() if authorization_header else None           
            host = request.headers.get('Origin')

        request.username = 'unknown' if not session_key else username_check_by_session_key(session_key)
        request.host = 'unknown' if not host else host
        response = self.get_response(request)
 
        return response
