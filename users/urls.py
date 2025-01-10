from django.urls import path
from django.contrib.auth import views as auth_views
from .views import request_otp_view, verify_otp_view, reset_password_view
from . import views
from core.views import home_view

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),  # Login URL
    path('', home_view, name='home'),  # Ensure you have a 'home' URL
    path('account/', include('two_factor.urls', 'two_factor')),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('agent-dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path('request-verification/<str:method>/', views.request_verification, name='request_verification'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-phone/', views.verify_phone, name='verify_phone'),
    path('request-otp/', request_otp_view, name='request_otp'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('reset-password/<phone_number>/', reset_password_view, name='reset_password'),
    path('profile/', views.profile_view, name='profile'),
    path('referral/', views.referral_view, name='referral'),
    path('admin/users/', views.admin_manage_users_view, name='admin_manage_users'),
    path('admin/users/<int:user_id>/edit/', views.admin_edit_user_view, name='admin_edit_user'),
    
    
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'),

]
