from django.contrib import admin
from django.urls import path, include  # Import include
from core.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include Django's built-in auth URLs
    path('accounts/', include('django.contrib.auth.urls')),  # This includes the login URL

    # Your other custom URLs
    path('', home_view, name='home'),  # Example home page URL
    path('offline_payments/', include('offline_payments.urls')),
]
