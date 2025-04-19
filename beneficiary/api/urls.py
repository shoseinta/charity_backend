from .views import BeneficiaryUserView
from django.urls import path

urlpatterns = [
    path('beneficiary/<int:pk>/information/', BeneficiaryUserView.as_view(), name='beneficiary_information'),
]