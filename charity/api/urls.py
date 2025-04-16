from django.urls import path
from .views import (BeneficiaryListView,
                    BeneficiaryRequestCreateView,
                    BeneficiaryDetailView)

urlpatterns = [
    path('beneficiaries/list/', BeneficiaryListView.as_view(), name='beneficiary-list'),
    path('beneficiaries/request-create/', BeneficiaryRequestCreateView.as_view(), name='beneficiary-request-create'),
    path('beneficiaries/<int:pk>/', BeneficiaryDetailView.as_view(), name='beneficiary-detail'),
]