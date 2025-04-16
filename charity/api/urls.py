from django.urls import path
from .views import BeneficiaryListView

urlpatterns = [
    path('beneficiaries/list/', BeneficiaryListView.as_view(), name='beneficiary-list'),
]