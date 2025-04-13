from django.urls import path
from .views import CharityRegistrationView

urlpatterns = [
    # Define your API endpoints here
    path('charity/register/', CharityRegistrationView.as_view(), name='charity-register'),
]