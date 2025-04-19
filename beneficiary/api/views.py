from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import generics
from rest_framework import status
from django.shortcuts import get_object_or_404
from beneficiary.models import BeneficiaryUserRegistration
from .serializers import (BeneficiaryUserSerializer,
                          BeneficiaryRequestSerializer)
from request.models import BeneficiaryRequestProcessingStage
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

class BeneficiaryRequestView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BeneficiaryRequestSerializer

    def perform_create(self, serializer):
        # Get the BeneficiaryUserRegistration object or raise 404
        pk = self.kwargs.get('pk')
        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        processing_stage = BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='submitted')
        # Save the BeneficiaryRequest with the associated beneficiary and processing stage
        serializer.save(beneficiary_user_registration=beneficiary, beneficiary_request_processing_stage=processing_stage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)