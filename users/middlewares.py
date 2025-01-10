from django.shortcuts import redirect
from .models import ActivityLog
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'role'):
            return redirect('unauthorized')  # Create an unauthorized page.
        return self.get_response(request)


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(user=user, action='login', description='User logged in.')

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    ActivityLog.objects.create(user=user, action='logout', description='User logged out.')


from django.contrib import messages

class RoleRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        role_required = view_kwargs.get('role_required')
        if role_required and request.user.is_authenticated:
            user_role = request.user.userprofile.role
            if user_role not in role_required:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('home')
