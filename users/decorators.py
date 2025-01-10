from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.userprofile.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
        return _wrapped_view
    return decorator
