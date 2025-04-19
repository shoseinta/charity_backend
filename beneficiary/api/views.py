from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from beneficiary.models import BeneficiaryUserRegistration
from .serializers import BeneficiaryUserSerializer
from user.api.permissions import IsCertainBeneficiary

class BeneficiaryUserView(APIView):
    permission_classes = [IsCertainBeneficiary]

    def get(self, request, pk, *args, **kwargs):
        try:
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=pk)
        except BeneficiaryUserRegistration.DoesNotExist:
            raise NotFound("Beneficiary not found.")
        
        serializer = BeneficiaryUserSerializer(beneficiary)
        return Response(serializer.data)