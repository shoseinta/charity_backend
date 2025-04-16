from rest_framework import generics
from beneficiary.models import BeneficiaryUserRegistration
from .serializers import BeneficiaryListSerializer

class BeneficiaryListView(generics.ListAPIView):
    queryset = BeneficiaryUserRegistration.objects.all()
    serializer_class = BeneficiaryListSerializer