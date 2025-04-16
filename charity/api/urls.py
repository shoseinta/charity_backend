from django.urls import path
from .views import (BeneficiaryListView,
                    BeneficiaryRequestCreateView,
                    BeneficiaryDetailView,
                    BeneficiaryRequestHistoryCreate)

urlpatterns = [
    path('beneficiaries/list/', BeneficiaryListView.as_view(), name='beneficiary-list'),
    path('beneficiaries/request-create/', BeneficiaryRequestCreateView.as_view(), name='beneficiary-request-create'),
    path('beneficiaries/<int:pk>/get/', BeneficiaryDetailView.as_view(), name='beneficiary-detail'),
    path('requests/<int:pk>/create/', BeneficiaryRequestHistoryCreate.as_view(), name='beneficiary-request-history-create'),
]