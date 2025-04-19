from .views import (BeneficiaryUserView,
                    BeneficiaryRequestView,
                    BeneficiaryRequestOnetimeCreationView,
                    BeneficiaryRequestRecurringCreationView,)
from django.urls import path

urlpatterns = [
    path('beneficiary/<int:pk>/information/', BeneficiaryUserView.as_view(), name='beneficiary_information'),
    path('beneficiary/<int:pk>/request-create/', BeneficiaryRequestView.as_view(), name='beneficiary_request_create'),
    path('beneficiary/<int:pk>/request-create-onetime/<int:request_pk>/', BeneficiaryRequestOnetimeCreationView.as_view(), name='beneficiary_request_create_onetime'),
    path('beneficiary/<int:pk>/request-create-recurring/<int:request_pk>/', BeneficiaryRequestRecurringCreationView.as_view(), name='beneficiary_request_create_recurring'),
]