from .views import (BeneficiaryUserView,
                    BeneficiaryRequestView,
                    BeneficiaryRequestOnetimeCreationView,
                    BeneficiaryRequestRecurringCreationView,
                    BeneficiaryRequestInitialStagesGetView,
                    BeneficiaryRequestInProgressGetView,
                    BeneficiaryRequestCompletedGetView,
                    BeneficiaryRequestRejectedGetView,
                    BenefeciarySingleRequestGetView,)
from django.urls import path

urlpatterns = [
    path('beneficiary/<int:pk>/information/', BeneficiaryUserView.as_view(), name='beneficiary_information'),
    path('beneficiary/<int:pk>/request-create/', BeneficiaryRequestView.as_view(), name='beneficiary_request_create'),
    path('beneficiary/<int:pk>/request-create-onetime/<int:request_pk>/', BeneficiaryRequestOnetimeCreationView.as_view(), name='beneficiary_request_create_onetime'),
    path('beneficiary/<int:pk>/request-create-recurring/<int:request_pk>/', BeneficiaryRequestRecurringCreationView.as_view(), name='beneficiary_request_create_recurring'),
    path('beneficiary/<int:pk>/request-initial-stages-get/', BeneficiaryRequestInitialStagesGetView.as_view(), name='beneficiary_request_initial_stages_get'),
    path('beneficiary/<int:pk>/request-in-progress-get/', BeneficiaryRequestInProgressGetView.as_view(), name='beneficiary_request_in_progress_get'),
    path('beneficiary/<int:pk>/request-completed-get/', BeneficiaryRequestCompletedGetView.as_view(), name='beneficiary_request_completed_get'),
    path('beneficiary/<int:pk>/request-rejected-get/', BeneficiaryRequestRejectedGetView.as_view(), name='beneficiary_request_rejected_get'),
    path('beneficiary/<int:pk>/request-single-get/<int:request_pk>/', BenefeciarySingleRequestGetView.as_view(), name='beneficiary_single_request_get'),
]