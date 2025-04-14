from django.urls import path
from .views import (CharityRegistrationView, 
                    CharityLoginView, 
                    BeneficiaryRegisterView, 
                    BeneficiaryLoginView,
                    BeneficiaryUserRegistrationInfoView,
                    BeneficiaryInformationCreateView,
                    BeneficiaryInformationSingleCreateView)

urlpatterns = [
    # Define your API endpoints here

    #login register paths
    path('charity/register/', CharityRegistrationView.as_view(), name='charity-register'),
    path('charity/login/', CharityLoginView.as_view(), name='charity-login'),
    path('beneficiary/register/',BeneficiaryRegisterView.as_view(), name='beneficiary-register'),
    path('beneficiary/login/', BeneficiaryLoginView.as_view(), name='beneficiary-login'),

    #additional info paths
    path('beneficiary/<int:pk>/register-info/', BeneficiaryUserRegistrationInfoView.as_view(), name='beneficiary-register-info'),
    path('beneficiary/information/', BeneficiaryInformationCreateView.as_view(), name='beneficiary-information-create'),
    path(
        'beneficiary/<int:beneficiary_user_registration_id>/information/',
        BeneficiaryInformationSingleCreateView.as_view(),
        name='beneficiary-information-single-create'
    ),

]