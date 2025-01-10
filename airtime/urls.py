from django.urls import path
from . import views

app_name = 'airtime'

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('providers/', views.providers_view, name='providers'),
    path('data-bundles/<str:provider>/', views.data_bundles_view, name='data_bundles'),
    path('purchase-airtime/', views.purchase_airtime_view, name='purchase_airtime'),
    path('purchase-data/', views.purchase_data_view, name='purchase_data'),
    path('api/data-bundles/<str:provider>/', views.api_data_bundles, name='api_data_bundles'),
    path('sentry-debug/', trigger_error),
]
