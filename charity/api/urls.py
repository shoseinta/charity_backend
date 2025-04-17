from django.urls import path
from .views import (BeneficiaryListView,
                    BeneficiaryRequestCreateView,
                    BeneficiaryDetailView,
                    BeneficiaryRequestHistoryCreate,
                    BeneficiaryRequestChildCreate,
                    BeneficiaryAllRequestsView,
                    BeneficiaryRequestOnetimeCreationView,
                    BeneficiaryRequestRecurringCreationView,)

urlpatterns = [
    path('beneficiaries/list/', BeneficiaryListView.as_view(), name='beneficiary-list'),
    path('beneficiaries/request-create/', BeneficiaryRequestCreateView.as_view(), name='beneficiary-request-create'),
    path('beneficiaries/<int:pk>/get/', BeneficiaryDetailView.as_view(), name='beneficiary-detail'),
    path('requests/<int:pk>/create-history/', BeneficiaryRequestHistoryCreate.as_view(), name='beneficiary-request-history-create'),
    path('requests/<int:pk>/create-child/', BeneficiaryRequestChildCreate.as_view(), name='beneficiary-request-child-create'),
    path('requests/list/', BeneficiaryAllRequestsView.as_view(), name='beneficiary-all-requests'),
    path('requests/<int:pk>/create-onetime/', BeneficiaryRequestOnetimeCreationView.as_view(), name='beneficiary-request-onetime-create'),
    path('requests/<int:pk>/create-recurring/', BeneficiaryRequestRecurringCreationView.as_view(), name='beneficiary-request-recurring-create'),
]