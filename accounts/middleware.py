from django.contrib import messages


class SessionExpiryMiddleware:
    """
    Detects when a user's session has expired and they were redirected
    to login, then adds an informational flash message.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add message before get_response so it renders in the login page response
        if (request.user.is_anonymous
                and request.path == '/accounts/login/'
                and 'next' in request.GET):
            messages.info(
                request,
                'Your session has expired. Please log in again.'
            )
        response = self.get_response(request)
        return response
