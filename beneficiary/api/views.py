from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import generics
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from beneficiary.models import BeneficiaryUserRegistration
from .serializers import (BeneficiaryUserSerializer,
                          BeneficiaryRequestSerializer,
                          BeneficiarySingleRequestOneTimeSerializer,
                          BeneficiarySingleRequestRecurringSerializer,
                          BeneficiaryRequestGetSerializer,
                          UpdateOnetimeSerializer,
                          UpdateRecurringSerializer,
                          BeneficiaryRequestChildGetSerializer,
                          BeneficiaryRequestChildCreateSerializer)
from request.models import (BeneficiaryRequestProcessingStage,
                            BeneficiaryRequest,
                            BeneficiaryRequestDurationOnetime,
                            BeneficiaryRequestDurationRecurring,
                            BeneficiaryRequestChild,)
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

class BeneficiaryRequestOnetimeCreationView(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiarySingleRequestOneTimeSerializer

    def create(self, request, *args, **kwargs):
        # Extract the 'pk' from the URL
        beneficiary = self.kwargs.get('pk')
        beneficiary_request_pk = self.kwargs.get('request_pk')
        try:
            # Get the parent BeneficiaryRequest object
            beneficiary_request = BeneficiaryRequest.objects.get(pk=beneficiary_request_pk)
            if beneficiary_request.beneficiary_user_registration != BeneficiaryUserRegistration.objects.get(pk=beneficiary):
                return Response({"error": "This request does not belong to the specified beneficiary."}, status=status.HTTP_400_BAD_REQUEST)

        except BeneficiaryRequest.DoesNotExist:
            return Response({"error": "BeneficiaryRequest not found."}, status=status.HTTP_404_NOT_FOUND)
        if BeneficiaryRequestDurationOnetime.objects.filter(beneficiary_request=beneficiary_request).exists():
            return Response({"error": "This request already has a onetime duration."}, status=status.HTTP_400_BAD_REQUEST)
        # Initialize the serializer with the request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the object while associating the BeneficiaryRequest
        serializer.save(beneficiary_request=beneficiary_request)

        # Customize the response
        return Response(
            {
                "message": "Beneficiary request onetime created successfully!",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class BeneficiaryRequestRecurringCreationView(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiarySingleRequestRecurringSerializer

    def create(self, request, *args, **kwargs):
        # Extract the 'pk' from the URL
        beneficiary = self.kwargs.get('pk')
        beneficiary_request_pk = self.kwargs.get('request_pk')
        try:
            # Get the parent BeneficiaryRequest object
            beneficiary_request = BeneficiaryRequest.objects.get(pk=beneficiary_request_pk)
            if beneficiary_request.beneficiary_user_registration != BeneficiaryUserRegistration.objects.get(pk=beneficiary):
                return Response({"error": "This request does not belong to the specified beneficiary."}, status=status.HTTP_400_BAD_REQUEST)
        except BeneficiaryRequest.DoesNotExist:
            return Response({"error": "BeneficiaryRequest not found."}, status=status.HTTP_404_NOT_FOUND)

        if BeneficiaryRequestDurationRecurring.objects.filter(beneficiary_request=beneficiary_request).exists():
            return Response({"error": "This request already has a recurring duration."}, status=status.HTTP_400_BAD_REQUEST)
        # Initialize the serializer with the request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the object while associating the BeneficiaryRequest
        serializer.save(beneficiary_request=beneficiary_request)

        # Customize the response
        return Response(
            {
                "message": "Beneficiary request recurring created successfully!",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
class BeneficiaryRequestInitialStagesGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        beneficiary = self.kwargs.get('pk')

        # Define the target processing stage names
        target_stages = ['submitted', 'pending_review', 'under_evaluation']

        # Filter requests based on beneficiary and target processing stages
        return BeneficiaryRequest.objects.filter(
            beneficiary_user_registration__pk=beneficiary,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )
    
class BeneficiaryRequestInProgressGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        beneficiary = self.kwargs.get('pk')

        # Define the target processing stage names
        target_stages = ['approved', 'in_progress']

        # Filter requests based on beneficiary and target processing stages
        return BeneficiaryRequest.objects.filter(
            beneficiary_user_registration__pk=beneficiary,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )
    
class BeneficiaryRequestCompletedGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        beneficiary = self.kwargs.get('pk')

        # Define the target processing stage names
        target_stages = ['completed']

        # Filter requests based on beneficiary and target processing stages
        return BeneficiaryRequest.objects.filter(
            beneficiary_user_registration__pk=beneficiary,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )
    
class BeneficiaryRequestRejectedGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        beneficiary = self.kwargs.get('pk')

        # Define the target processing stage names
        target_stages = ['rejected']

        # Filter requests based on beneficiary and target processing stages
        return BeneficiaryRequest.objects.filter(
            beneficiary_user_registration__pk=beneficiary,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )


class BenefeciarySingleRequestGetView(generics.RetrieveAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer

    def get_object(self):
        request_pk = self.kwargs.get('request_pk')
        return get_object_or_404(BeneficiaryRequest, pk=request_pk)

class BeneficiaryUpdateSingleRequestView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestSerializer

    def get_object(self):
        obj = get_object_or_404(BeneficiaryRequest, pk=self.kwargs.get('request_pk'))

        if obj.beneficiary_request_processing_stage.beneficiary_request_processing_stage_name.lower() != "submitted":
            raise PermissionDenied("You can only update or delete a request in the 'submitted' stage.")

        self.check_object_permissions(self.request, obj)
        return obj
    
from rest_framework.exceptions import PermissionDenied
from django.http import Http404

class BeneficiaryUpdateOnetimeView(generics.UpdateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = UpdateOnetimeSerializer
    queryset = BeneficiaryRequestDurationOnetime.objects.all()
    def perform_update(self, serializer):
        request_pk = self.kwargs.get('request_pk')

        try:
            beneficiary_request = BeneficiaryRequestDurationOnetime.objects.get(pk=request_pk).beneficiary_request
        except BeneficiaryRequestDurationOnetime.DoesNotExist:
            raise Http404("BeneficiaryRequestDurationOnetime not found.")

        # Save with validated data + beneficiary_request relation
        serializer.save(beneficiary_request=beneficiary_request)

class BeneficiaryUpdateRecurringView(generics.UpdateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = UpdateRecurringSerializer
    queryset = BeneficiaryRequestDurationRecurring.objects.all()
    def perform_update(self, serializer):
        request_pk = self.kwargs.get('request_pk')

        try:
            beneficiary_request = BeneficiaryRequestDurationRecurring.objects.get(pk=request_pk).beneficiary_request
        except BeneficiaryRequestDurationRecurring.DoesNotExist:
            raise Http404("BeneficiaryRequestDurationRecurring not found.")

        # Save with validated data + beneficiary_request relation
        serializer.save(beneficiary_request=beneficiary_request)

class BeneficiarySingleRequestChildsGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildGetSerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        beneficiary_request = self.kwargs.get('request_pk')

        # Filter requests based on beneficiary
        return BeneficiaryRequestChild.objects.filter(
            beneficiary_request=beneficiary_request
        )
    
class BeneficiarySingleChildGetView(generics.RetrieveAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildGetSerializer

    def get_object(self):
        request_pk = self.kwargs.get('request_pk')
        return get_object_or_404(BeneficiaryRequestChild, pk=request_pk)

class BeneficiaryChildCreateView(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildCreateSerializer

    def perform_create(self, serializer):
        # Get the BeneficiaryRequest object or raise 404
        pk = self.kwargs.get('request_pk')
        beneficiary_request = get_object_or_404(BeneficiaryRequest, pk=pk)
        submitted = BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='submitted')
        # Save the BeneficiaryRequest with the associated beneficiary and processing stage
        serializer.save(beneficiary_request=beneficiary_request, beneficiary_request_child_processing_stage=submitted)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
