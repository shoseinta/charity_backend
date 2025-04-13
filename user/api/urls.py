from django.urls import path
from .views import CharityRegistrationView, CharityLoginView, BeneficiaryRegisterView, BeneficiaryLoginView

urlpatterns = [
    # Define your API endpoints here
    path('charity/register/', CharityRegistrationView.as_view(), name='charity-register'),
    path('charity/login/', CharityLoginView.as_view(), name='charity-login'),
    path('beneficiary/register/',BeneficiaryRegisterView.as_view(), name='beneficiary-register'),
    path('beneficiary/login/', BeneficiaryLoginView.as_view(), name='beneficiary-login'),
]