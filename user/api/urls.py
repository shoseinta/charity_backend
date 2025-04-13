from django.urls import path
from .views import (CharityRegistrationView, 
                    CharityLoginView, 
                    BeneficiaryRegisterView, 
                    BeneficiaryLoginView,
                    BeneficiaryUserRegistrationInfoView)

urlpatterns = [
    # Define your API endpoints here

    #login register paths
    path('charity/register/', CharityRegistrationView.as_view(), name='charity-register'),
    path('charity/login/', CharityLoginView.as_view(), name='charity-login'),
    path('beneficiary/register/',BeneficiaryRegisterView.as_view(), name='beneficiary-register'),
    path('beneficiary/login/', BeneficiaryLoginView.as_view(), name='beneficiary-login'),

    #additional info paths
    path('beneficiary/<int:pk>/register-info/', BeneficiaryUserRegistrationInfoView.as_view(), name='beneficiary-register-info'),

]