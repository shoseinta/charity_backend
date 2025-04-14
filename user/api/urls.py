from django.urls import path
from .views import (CharityRegistrationView, 
                    CharityLoginView, 
                    BeneficiaryRegisterView, 
                    BeneficiaryLoginView,
                    BeneficiaryUserRegistrationInfoView,
                    BeneficiaryInformationCreateView,
                    BeneficiaryInformationSingleCreateView,
                    LogoutView,
                    CharityUsernameUpdateView,
                    CharityPasswordUpdateView,
                    BeneficiaryPasswordUpdateView,
                    BeneficiaryUserRegistrationInfoUpdateView
                    )

urlpatterns = [
    # Define your API endpoints here

    #login register paths
    path('charity/register/', CharityRegistrationView.as_view(), name='charity-register'),
    path('charity/login/', CharityLoginView.as_view(), name='charity-login'),
    path('beneficiary/register/',BeneficiaryRegisterView.as_view(), name='beneficiary-register'),
    path('beneficiary/login/', BeneficiaryLoginView.as_view(), name='beneficiary-login'),

    #additional info paths
    path('beneficiary/<int:beneficiary_user_registration_id>/register-info/', BeneficiaryUserRegistrationInfoView.as_view(), name='beneficiary-register-info'),
    path('beneficiary/information/', BeneficiaryInformationCreateView.as_view(), name='beneficiary-information-create'),
    path(
        'beneficiary/<int:beneficiary_user_registration_id>/information/',
        BeneficiaryInformationSingleCreateView.as_view(),
        name='beneficiary-information-single-create'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('charity/<int:pk>/username-update/', CharityUsernameUpdateView.as_view(), name='charity-username-update'),
    path('charity/<int:pk>/password-update/', CharityPasswordUpdateView.as_view(), name='charity-password-update'),
    path('beneficiary/<int:pk>/password-update/', BeneficiaryPasswordUpdateView.as_view(), name='beneficiary-password-update'),
    path('beneficiary/<int:beneficiary_user_registration_id>/update-register-info/', BeneficiaryUserRegistrationInfoUpdateView.as_view(), name='beneficiary-update-register-info'),
    
]