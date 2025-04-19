from rest_framework import generics
from beneficiary.models import (BeneficiaryUserRegistration,
                                BeneficiaryUserInformation,
                                BeneficiaryUserAddress,
                                BeneficiaryUserAdditionalInfo,)
from request.models import (BeneficiaryRequest,
                            BeneficiaryRequestHistory,
                            BeneficiaryRequestChild,
                            BeneficiaryRequestDurationOnetime,
                            BeneficiaryRequestDurationRecurring,
                            BeneficiaryRequestProcessingStage,
                            BeneficiaryRequestDuration,
                            CharityAnnouncementForRequest)
from .serializers import (BeneficiaryListSerializer,
                          RequestCreationSerializer,
                          BeneficiaryListSingleSerializer,
                          SingleRequestHistorySerializer,
                          SingleRequestChildSerializer,
                          BeneficiaryGetRequestSerializer,
                          BeneficiarySingleRequestOneTimeSerializer,
                          BeneficiarySingleRequestRecurringSerializer,
                          BeneficiaryUpdateRequestSerializer,
                          BeneficiaryRequestUpdateOneTimeSerializer,
                          BeneficiaryRequestUpdateRecurringSerializer,
                          BeneficiaryRequestChangeProcessingStageSerializer,
                          BeneficiaryAdditionalInfoUpdateSerializer,
                          BeneficiaryAddressUpdateSerializer,
                          BeneficiaryInformationUpdateSerializer,
                          BeneficiaryRequestAnnouncementUpdateSerializer,)
from user.api.permissions import IsAdminOrCharity, IsCertainBeneficiary
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


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


class BeneficiaryRequestHistoryCreate(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = SingleRequestHistorySerializer

    def create(self, request, *args, **kwargs):
        # Extract the 'pk' from the URL
        beneficiary_request_pk = self.kwargs.get('pk')
        try:
            # Get the parent BeneficiaryRequest object
            beneficiary_request = BeneficiaryRequest.objects.get(pk=beneficiary_request_pk)
        except BeneficiaryRequest.DoesNotExist:
            return Response({"error": "BeneficiaryRequest not found."}, status=status.HTTP_404_NOT_FOUND)

        # Initialize the serializer with the request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the object while associating the BeneficiaryRequest
        serializer.save(beneficiary_request=beneficiary_request)

        # Customize the response
        return Response(
            {
                "message": "Beneficiary request history created successfully!",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
class BeneficiaryRequestChildCreate(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = SingleRequestChildSerializer

    def create(self, request, *args, **kwargs):
        # Extract the 'pk' from the URL
        beneficiary_request_pk = self.kwargs.get('pk')
        try:
            # Get the parent BeneficiaryRequest object
            beneficiary_request = BeneficiaryRequest.objects.get(pk=beneficiary_request_pk)
        except BeneficiaryRequest.DoesNotExist:
            return Response({"error": "BeneficiaryRequest not found."}, status=status.HTTP_404_NOT_FOUND)

        # Initialize the serializer with the request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the object while associating the BeneficiaryRequest
        serializer.save(beneficiary_request=beneficiary_request)

        # Customize the response
        return Response(
            {
                "message": "Beneficiary request child created successfully!",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
class BeneficiaryAllRequestsView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryGetRequestSerializer
    queryset = BeneficiaryRequest.objects.all()

class BeneficiaryRequestOnetimeCreationView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiarySingleRequestOneTimeSerializer

    def create(self, request, *args, **kwargs):
        # Extract the 'pk' from the URL
        beneficiary_request_pk = self.kwargs.get('pk')
        try:
            # Get the parent BeneficiaryRequest object
            beneficiary_request = BeneficiaryRequest.objects.get(pk=beneficiary_request_pk)
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
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiarySingleRequestRecurringSerializer

    def create(self, request, *args, **kwargs):
        # Extract the 'pk' from the URL
        beneficiary_request_pk = self.kwargs.get('pk')
        try:
            # Get the parent BeneficiaryRequest object
            beneficiary_request = BeneficiaryRequest.objects.get(pk=beneficiary_request_pk)
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

class BeneficiaryNewRequestGetView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    queryset = BeneficiaryRequest.objects.filter(
    beneficiary_request_processing_stage__in=[
        BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name = 'submitted'),
        BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name = 'pending_review'),
        BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name = 'under_evaluation'),
    ]
)
    
class BeneficiaryOldRequestOnetimeGetView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    queryset = BeneficiaryRequest.objects.filter(
    beneficiary_request_processing_stage__in=[
        BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name = 'approved'),
        BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name = 'in_progress'),
    ],
    beneficiary_request_duration__in=[
        BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name = 'one_time')
    ]
)
    
class BeneficiaryOldRequestOngoingGetView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    queryset = BeneficiaryRequest.objects.filter(
    beneficiary_request_processing_stage__in=[
        BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name = 'approved'),
        BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name = 'in_progress'),
    ],
    beneficiary_request_duration__in=[
        BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name = 'recurring'),
        BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name = 'permanent')
    ]
)
    
class SingleRequestGetView(generics.RetrieveAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    queryset = BeneficiaryRequest.objects.all()
    lookup_field = 'pk'

class BeneficiaryUpdateRequestView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryUpdateRequestSerializer
    queryset = BeneficiaryRequest.objects.all()
    lookup_field = 'pk' 

class SingleHistoryUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = SingleRequestHistorySerializer
    queryset = BeneficiaryRequestHistory.objects.all()
    lookup_field = 'pk'

class SingleChildUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = SingleRequestChildSerializer
    queryset = BeneficiaryRequestChild.objects.all()
    lookup_field = 'pk'


class SingleOnetimeUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestUpdateOneTimeSerializer
    queryset = BeneficiaryRequestDurationOnetime.objects.all()
    lookup_field = 'pk'

class SingleRecurringUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestUpdateRecurringSerializer
    queryset = BeneficiaryRequestDurationRecurring.objects.all()
    lookup_field = 'pk'

class ChangeRequestProcessingStageView(generics.UpdateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestChangeProcessingStageSerializer
    queryset = BeneficiaryRequest.objects.all()
    lookup_field = 'pk'

class UpdateBeneficiaryAddressView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryAddressUpdateSerializer
    queryset = BeneficiaryUserAddress.objects.all()
    #i want to find user_register = userregistration(pk=pk) and then find userinformation(beneficiary_user_registration=user_register) and then update it based on input or retreive or delete it
    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            user_register = BeneficiaryUserRegistration.objects.get(pk=pk)
            user_information = BeneficiaryUserAddress.objects.get(beneficiary_user_registration=user_register)
            return user_information
        except BeneficiaryUserRegistration.DoesNotExist:
            raise Http404("BeneficiaryUserRegistration does not exist")
        except BeneficiaryUserAddress.DoesNotExist:
            raise Http404("BeneficiaryUserAddress does not exist")
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class UpdateBeneficiaryInformationView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryInformationUpdateSerializer
    queryset = BeneficiaryUserInformation.objects.all()
    #i want to find user_register = userregistration(pk=pk) and then find userinformation(beneficiary_user_registration=user_register) and then update it based on input or retreive or delete it
    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            user_register = BeneficiaryUserRegistration.objects.get(pk=pk)
            user_information = BeneficiaryUserInformation.objects.get(beneficiary_user_registration=user_register)
            return user_information
        except BeneficiaryUserRegistration.DoesNotExist:
            raise Http404("BeneficiaryUserRegistration does not exist")
        except BeneficiaryUserInformation.DoesNotExist:
            raise Http404("BeneficiaryUserInformation does not exist")
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class UpdateBeneficiaryAdditionalInfoView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryAdditionalInfoUpdateSerializer
    queryset = BeneficiaryUserAdditionalInfo.objects.all()
    #i want to find user_register = userregistration(pk=pk) and then find userinformation(beneficiary_user_registration=user_register) and then update it based on input or retreive or delete it
    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            user_register = BeneficiaryUserRegistration.objects.get(pk=pk)
            user_information = BeneficiaryUserAdditionalInfo.objects.get(beneficiary_user_registration=user_register)
            return user_information
        except BeneficiaryUserRegistration.DoesNotExist:
            raise Http404("BeneficiaryUserRegistration does not exist")
        except BeneficiaryUserAdditionalInfo.DoesNotExist:
            raise Http404("BeneficiaryUserInformation does not exist")
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
class BeneficiaryRequestAnnouncementListView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestAnnouncementUpdateSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            single_request = BeneficiaryRequest.objects.get(pk=pk)
            return CharityAnnouncementForRequest.objects.filter(beneficiary_request=single_request)
        except BeneficiaryRequest.DoesNotExist:
            raise Http404("BeneficiaryRequest does not exist")

class BeneficiaryRequestAnnouncementCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestAnnouncementUpdateSerializer

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        try:
            single_request = BeneficiaryRequest.objects.get(pk=pk)
            serializer.save(beneficiary_request=single_request)
        except BeneficiaryRequest.DoesNotExist:
            raise Http404("BeneficiaryRequest does not exist")
        
class BeneficiaryRequestAnnouncementUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestAnnouncementUpdateSerializer
    queryset = CharityAnnouncementForRequest.objects.all()
    lookup_field = 'pk'