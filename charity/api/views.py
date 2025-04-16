from rest_framework import generics
from beneficiary.models import BeneficiaryUserRegistration
from request.models import BeneficiaryRequest
from .serializers import (BeneficiaryListSerializer,
                          RequestCreationSerializer,
                          BeneficiaryListSingleSerializer)
from user.api.permissions import IsAdminOrCharity, IsCertainBeneficiary

class BeneficiaryListView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    queryset = BeneficiaryUserRegistration.objects.all()
    serializer_class = BeneficiaryListSerializer

class BeneficiaryRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    queryset = BeneficiaryRequest.objects.all()
    serializer_class = RequestCreationSerializer

class BeneficiaryDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminOrCharity]
    queryset = BeneficiaryUserRegistration.objects.all()
    serializer_class = BeneficiaryListSingleSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        return self.queryset.get(pk=pk)