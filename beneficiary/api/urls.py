from .views import (BeneficiaryUserView,
                    BeneficiaryRequestView)
from django.urls import path

urlpatterns = [
    path('beneficiary/<int:pk>/information/', BeneficiaryUserView.as_view(), name='beneficiary_information'),
    path('beneficiary/<int:pk>/request-create/', BeneficiaryRequestView.as_view(), name='beneficiary_request_create'),
]