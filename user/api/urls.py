from django.urls import path
from .views import CharityRegistrationView, CharityLoginView

urlpatterns = [
    # Define your API endpoints here
    path('charity/register/', CharityRegistrationView.as_view(), name='charity-register'),
    path('charity/login/', CharityLoginView.as_view(), name='charity-login'),
]