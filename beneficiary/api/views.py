from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import generics, filters
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import Http404
from beneficiary.models import (BeneficiaryUserRegistration,
                                Province,
                                City,
                                BeneficiaryUserInformation,
                                BeneficiaryUserAddress,
                                BeneficiaryUserAdditionalInfo)
from .serializers import (BeneficiaryUserSerializer,
                          BeneficiaryRequestSerializer,
                          BeneficiarySingleRequestOneTimeSerializer,
                          BeneficiarySingleRequestRecurringSerializer,
                          BeneficiaryRequestGetSerializer,
                          UpdateOnetimeSerializer,
                          UpdateRecurringSerializer,
                          BeneficiaryRequestChildGetSerializer,
                          BeneficiaryRequestChildCreateSerializer,
                          BeneficiaryRequestHistorySerializer,
                          AnnouncementSerializer,
                          BeneficiaryRequestAnnouncementSerializer,
                          BeneficiaryRequestTypeLayer1Serializer,
                          BeneficiaryRequestTypeLayer2Serializer,
                          BeneficiaryRequestProcessingStageSerializer,
                          BeneficiaryRequestDurationLookupSerializer,
                          ProvinceLookupSerializer,
                          CityLookupSerializer,
                          RequestAnnouncementSerializer,
                          BeneficiaryAnnouncementSerializer,
                          BeneficiaryInformationUpdateSerializer,
                          BeneficiaryAddressUpdateSerializer,
                          BeneficiaryAdditionalInfoUpdateSerializer,
                          UpdatingDeletingBeneficiaryUserRegistrationSerializer)
from request.models import (BeneficiaryRequestProcessingStage,
                            BeneficiaryRequest,
                            BeneficiaryRequestDurationOnetime,
                            BeneficiaryRequestDurationRecurring,
                            BeneficiaryRequestChild,
                            BeneficiaryRequestHistory,
                            CharityAnnouncementForRequest,
                            BeneficiaryRequestTypeLayer1,
                            BeneficiaryRequestTypeLayer2,
                            BeneficiaryRequestDuration,
                            )
from beneficiary.models import CharityAnnouncementToBeneficiary
from user.api.permissions import IsCertainBeneficiary
from django.db.models.functions import Coalesce
from django.db.models import F, Case, When, Value, DateTimeField
from core.cache_manager import GlobalCacheManager
from datetime import timedelta
from django.utils import timezone

class BeneficiaryAllRequestsGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date', 'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id']
    ordering = ['effective_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        page = self.request.query_params.get('page', 1)

        cache_key = GlobalCacheManager.make_paginated_key("beneficiary:request:list", page, user_id=pk)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        base_qs = BeneficiaryRequest.objects.filter(
            beneficiary_user_registration=pk
        )

        GlobalCacheManager.set(cache_key, base_qs)
        return base_qs


class BeneficiaryUserView(APIView):
    serializer_class = BeneficiaryUserSerializer  # ✅ ADD THIS
    permission_classes = [IsCertainBeneficiary]

    def get(self, request, pk, *args, **kwargs):
        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        serializer = self.serializer_class(beneficiary)
        return Response(serializer.data)

class CreateBeneficiaryInformation(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryInformationUpdateSerializer

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        # Check if the user registration exists
        try:
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=pk)
        except BeneficiaryUserRegistration.DoesNotExist:
            return Response({'detail': 'BeneficiaryUserRegistration not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if information already exists
        if BeneficiaryUserInformation.objects.filter(beneficiary_user_registration=beneficiary).exists():
            return Response({'detail': 'Beneficiary information already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create new information
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(beneficiary_user_registration=beneficiary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UpdateBeneficiaryInformationView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
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
    
class CreateAddress(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryAddressUpdateSerializer
    queryset = BeneficiaryUserAddress.objects.all()

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        # Check if the user registration exists
        try:
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=pk)
        except BeneficiaryUserRegistration.DoesNotExist:
            return Response({'detail': 'BeneficiaryUserRegistration not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if information already exists
        if BeneficiaryUserAddress.objects.filter(beneficiary_user_registration=beneficiary).exists():
            return Response({'detail': 'Beneficiary address already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create new information
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(beneficiary_user_registration=beneficiary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UpdateBeneficiaryAddressView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
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
    
class CreateAdditionalInfo(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryAdditionalInfoUpdateSerializer

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        # Check if the user registration exists
        try:
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=pk)
        except BeneficiaryUserRegistration.DoesNotExist:
            return Response({'detail': 'BeneficiaryUserRegistration not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create new information
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(beneficiary_user_registration=beneficiary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UpdateBeneficiaryAdditionalInfoView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryAdditionalInfoUpdateSerializer
    queryset = BeneficiaryUserAdditionalInfo.objects.all()
    #i want to find user_register = userregistration(pk=pk) and then find userinformation(beneficiary_user_registration=user_register) and then update it based on input or retreive or delete it
    def get_object(self):
        pk = self.kwargs.get('pk')
        info_pk = self.kwargs.get('info_pk')

        try:
            beneficiary_user = BeneficiaryUserRegistration.objects.get(pk=pk)
        except BeneficiaryUserRegistration.DoesNotExist:
            raise NotFound("BeneficiaryUserRegistration does not exist")

        try:
            user_information = BeneficiaryUserAdditionalInfo.objects.get(pk=info_pk)
        except BeneficiaryUserAdditionalInfo.DoesNotExist:
            raise NotFound("BeneficiaryUserAdditionalInfo does not exist")

        if user_information.beneficiary_user_registration != beneficiary_user:
            raise PermissionDenied("You do not have permission to access this information.")

        return user_information
        
    def perform_update(self, serializer):
        serializer.save(beneficiary_user_additional_info_is_created_by_charity=False)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
class UpdateBeneficiaryUserRegistration(generics.RetrieveUpdateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = UpdatingDeletingBeneficiaryUserRegistrationSerializer
    queryset = BeneficiaryUserRegistration.objects.all()
    lookup_field = 'pk'
    
class BeneficiaryRequestView(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
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
            
            if beneficiary_request.beneficiary_request_duration.beneficiary_request_duration_name != 'one_time':
                return Response({'error': "this request is not onetime"}, status=status.HTTP_400_BAD_REQUEST)

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
            
            if beneficiary_request.beneficiary_request_duration.beneficiary_request_duration_name != 'recurring':
                return Response({'error': "this request is not onetime"}, status=status.HTTP_400_BAD_REQUEST)
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
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date']
    ordering = ['effective_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        page = self.request.query_params.get('page', 1)

        cache_key = GlobalCacheManager.make_paginated_key("beneficiary:request:initial_stages", page, user_id=pk)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        target_stages = ['submitted', 'pending_review', 'under_evaluation']
        base_qs = BeneficiaryRequest.objects.filter(
            beneficiary_user_registration=pk,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )

        GlobalCacheManager.set(cache_key, base_qs)
        return base_qs

    
class BeneficiaryRequestInProgressGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date']
    ordering = ['effective_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        page = self.request.query_params.get('page', 1)

        cache_key = GlobalCacheManager.make_paginated_key("beneficiary:request:in_progress", page, user_id=pk)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        target_stages = ['approved', 'in_progress']
        base_qs = BeneficiaryRequest.objects.filter(
            beneficiary_user_registration=pk,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )

        GlobalCacheManager.set(cache_key, base_qs)
        return base_qs

    
class BeneficiaryRequestCompletedGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date']
    ordering = ['effective_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        page = self.request.query_params.get('page', 1)

        cache_key = GlobalCacheManager.make_paginated_key("beneficiary:request:completed", page, user_id=pk)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        target_stages = ['completed']
        base_qs = BeneficiaryRequest.objects.filter(
            beneficiary_user_registration=pk,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )

        GlobalCacheManager.set(cache_key, base_qs)
        return base_qs

    
class BeneficiaryRequestRejectedGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date']
    ordering = ['effective_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        page = self.request.query_params.get('page', 1)

        cache_key = GlobalCacheManager.make_paginated_key("beneficiary:request:rejected", page, user_id=pk)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        target_stages = ['rejected']
        base_qs = BeneficiaryRequest.objects.filter(
            beneficiary_user_registration=pk,
            beneficiary_request_processing_stage__beneficiary_request_processing_stage_name__in=target_stages
        )

        GlobalCacheManager.set(cache_key, base_qs)
        return base_qs




class BenefeciarySingleRequestGetView(generics.RetrieveAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestGetSerializer

    def get_object(self):
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        try:
            beneficiary_request = BeneficiaryRequest.objects.get(pk=request_pk)
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=pk)
            if beneficiary_request.beneficiary_user_registration != beneficiary:
                raise PermissionDenied("you can only see request belong to you")
        except BeneficiaryRequest.DoesNotExist:
            raise Http404('beneficiary request not found')
        except BeneficiaryUserRegistration.DoesNotExist:
            raise Http404('beneficiary not found') 
        return get_object_or_404(BeneficiaryRequest, pk=request_pk)

class BeneficiaryUpdateSingleRequestView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(BeneficiaryRequest, pk=self.kwargs.get('request_pk'))
        try:
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=pk)
            if obj.beneficiary_user_registration != beneficiary:
                raise PermissionDenied("you can only update requests related to you")
        except BeneficiaryUserRegistration.DoesNotExist:
            raise Http404('beneficiary not found')
        if obj.beneficiary_request_is_created_by_charity:
            raise PermissionDenied("You can only update or delete a request you created")
        if obj.beneficiary_request_processing_stage.beneficiary_request_processing_stage_name.lower() != "submitted":
            raise PermissionDenied("You can only update or delete a request in the 'submitted' stage.")

        self.check_object_permissions(self.request, obj)
        return obj


class BeneficiaryUpdateOnetimeView(generics.UpdateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = UpdateOnetimeSerializer
    queryset = BeneficiaryRequestDurationOnetime.objects.all()
    def perform_update(self, serializer):
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        try:
            beneficiary_request_onetime = BeneficiaryRequestDurationOnetime.objects.get(pk=request_pk)
            beneficiary_request = beneficiary_request_onetime.beneficiary_request
            if beneficiary_request != BeneficiaryUserRegistration.objects.get(pk=pk):
                 raise PermissionDenied("You can only update a request you created.")
        except BeneficiaryRequestDurationOnetime.DoesNotExist:
            raise Http404("BeneficiaryRequestDurationOnetime not found.")

        if beneficiary_request_onetime.beneficiary_request_duration_onetime_is_created_by_charity:
            raise PermissionDenied("You can only update a request you created.")
        # Save with validated data + beneficiary_request relation
        serializer.save()

class BeneficiaryUpdateRecurringView(generics.UpdateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = UpdateRecurringSerializer
    queryset = BeneficiaryRequestDurationRecurring.objects.all()
    def perform_update(self, serializer):
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        try:
            beneficiary_request_recurring = BeneficiaryRequestDurationOnetime.objects.get(pk=request_pk)
            beneficiary_request = beneficiary_request_recurring.beneficiary_request
            if beneficiary_request != BeneficiaryUserRegistration.objects.get(pk=pk):
                 raise PermissionDenied("You can only update a request you created.")
        except BeneficiaryRequestDurationRecurring.DoesNotExist:
            raise Http404("BeneficiaryRequestDurationRecurring not found.")

        if beneficiary_request_recurring.beneficiary_request_duration_recurring_is_created_by_charity:
            raise PermissionDenied("You can only update a request you created.")
        # Save with validated data + beneficiary_request relation
        serializer.save()

class BeneficiarySingleRequestChildsGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildGetSerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        try:
            beneficiary_request = BeneficiaryRequest.objects.get(pk=request_pk)
        except BeneficiaryRequest.DoesNotExist:
            raise Http404("BeneficiaryRequest not found.")
        beneficiary_request_child = BeneficiaryRequestChild.objects.filter(
            beneficiary_request=beneficiary_request
        )
        beneficiary = beneficiary_request.beneficiary_user_registration
        if beneficiary != BeneficiaryUserRegistration.objects.get(pk=pk):
            raise PermissionDenied("You can only see child requests for request belong to you.")
        # Filter requests based on beneficiary
        return beneficiary_request_child
    
class BeneficiarySingleChildGetView(generics.RetrieveAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildGetSerializer

    def get_object(self):
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        try:
            beneficiary_child_request = BeneficiaryRequestChild.objects.get(pk = request_pk)
            beneficiary = BeneficiaryUserRegistration.objects.get(pk=pk)
            if beneficiary_child_request.beneficiary_request.beneficiary_user_registration != beneficiary:
                raise PermissionDenied("You can only see child request belong to you.")
        except BeneficiaryRequestChild.DoesNotExist:
            raise NotFound("BeneficiaryRequestChild not found")
        except BeneficiaryUserRegistration.DoesNotExist:
            raise NotFound("beneficiary not found")

        return get_object_or_404(BeneficiaryRequestChild, pk=request_pk)

class BeneficiaryChildCreateView(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildCreateSerializer

    def perform_create(self, serializer):
        # Get the BeneficiaryRequest object or raise 404
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        beneficiary_request = get_object_or_404(BeneficiaryRequest, pk=request_pk)
        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        if beneficiary_request.beneficiary_user_registration != beneficiary:
            raise PermissionDenied("You can only create child requests for request belong to you.")
        submitted = BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='submitted')
        # Save the BeneficiaryRequest with the associated beneficiary and processing stage
        serializer.save(beneficiary_request=beneficiary_request, beneficiary_request_child_processing_stage=submitted)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class BeneficiarySingleChildUpdateView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildCreateSerializer

    def get_object(self):
        obj = get_object_or_404(BeneficiaryRequestChild, pk=self.kwargs.get('request_pk'))
        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=self.kwargs.get('pk'))
        if obj.beneficiary_request.beneficiary_user_registration != beneficiary:
            raise PermissionDenied('you can only update child request belong to you')
        if obj.beneficiary_request_child_is_created_by_charity:
            raise PermissionDenied("You can only update or delete a request you created.")

        if obj.beneficiary_request_child_processing_stage.beneficiary_request_processing_stage_name.lower() != "submitted":
            raise PermissionDenied("You can only update or delete a request in the 'submitted' stage.")

        self.check_object_permissions(self.request, obj)
        return obj
    
class BeneficiaryRequestHistoriesGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestHistorySerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        beneficiary_request = get_object_or_404(BeneficiaryRequest, pk=request_pk)
        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        if beneficiary_request.beneficiary_user_registration != beneficiary:
            raise PermissionDenied('you can only see histories related to your request')
        # Filter requests based on beneficiary
        return BeneficiaryRequestHistory.objects.filter(
            beneficiary_request=beneficiary_request
        )

class BeneficiarySingleHistoryGetView(generics.RetrieveAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestHistorySerializer

    def get_object(self):
        request_pk = self.kwargs.get('request_pk')
        pk = self.kwargs.get('pk')
        history = get_object_or_404(BeneficiaryRequestHistory, pk=request_pk)
        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        if history.beneficiary_request.beneficiary_user_registration != beneficiary:
            raise PermissionDenied('you can only see a history related to you')
        return get_object_or_404(BeneficiaryRequestHistory, pk=request_pk)

class AnnouncementView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        beneficiary = self.kwargs.get('pk')
        one_month_ago = timezone.now() - timedelta(days=30)

        return CharityAnnouncementToBeneficiary.objects.filter(
            beneficiary_user_registration=beneficiary,
            charity_announcement_to_beneficiary_created_at__gte=one_month_ago,
            charity_announcement_to_beneficiary_seen=False
        )

class AnnouncementRequestView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestAnnouncementSerializer

    def get_queryset(self):
        beneficiary = self.kwargs.get('pk')
        one_month_ago = timezone.now() - timedelta(days=30)

        request = BeneficiaryRequest.objects.filter(beneficiary_user_registration=beneficiary)

        return CharityAnnouncementForRequest.objects.filter(
            beneficiary_request_id__in = request,
            charity_announcement_for_request_created_at__gte=one_month_ago,
            charity_announcement_for_request_seen=False
        )

class RequestAnnouncementForRequestSeenView(generics.RetrieveAPIView):
    queryset = CharityAnnouncementForRequest.objects.all()
    serializer_class = RequestAnnouncementSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        announcement_pk = self.kwargs.get('announcement_pk')

        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        announcement = get_object_or_404(CharityAnnouncementForRequest, pk=announcement_pk)

        if announcement.beneficiary_request.beneficiary_user_registration != beneficiary:
            raise PermissionDenied("You can only see announcements relevant to you.")

        if not announcement.charity_announcement_for_request_seen:
            announcement.charity_announcement_for_request_seen = True
            announcement.save(update_fields=['charity_announcement_for_request_seen'])

        serializer = self.get_serializer(announcement)
        return Response(serializer.data)


# 🔹 2. For Beneficiary-specific Announcements
class BeneficiaryAnnouncementSeenView(generics.RetrieveAPIView):
    queryset = CharityAnnouncementToBeneficiary.objects.all()
    serializer_class = BeneficiaryAnnouncementSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        announcement_pk = self.kwargs.get('announcement_pk')

        beneficiary = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        announcement = get_object_or_404(CharityAnnouncementToBeneficiary, pk=announcement_pk)

        if announcement.beneficiary_user_registration != beneficiary:
            raise PermissionDenied("You can only see announcements relevant to you.")

        if not announcement.charity_announcement_to_beneficiary_seen:
            announcement.charity_announcement_to_beneficiary_seen = True
            announcement.save(update_fields=['charity_announcement_to_beneficiary_seen'])

        serializer = self.get_serializer(announcement)
        return Response(serializer.data)

class BeneficiaryRequestTypeLayer1View(generics.ListAPIView):
    serializer_class = BeneficiaryRequestTypeLayer1Serializer
    queryset = BeneficiaryRequestTypeLayer1.objects.all()
    pagination_class = None
    
class BeneficiaryRequestTypeLayer2View(generics.ListAPIView):
    serializer_class = BeneficiaryRequestTypeLayer2Serializer
    queryset = BeneficiaryRequestTypeLayer2.objects.all()
    pagination_class = None

class BeneficiaryRequestProcessingStageView(generics.ListAPIView):
    serializer_class = BeneficiaryRequestProcessingStageSerializer
    queryset = BeneficiaryRequestProcessingStage.objects.all()
    pagination_class = None

class BeneficiaryRequestDurationLookupView(generics.ListAPIView):
    serializer_class = BeneficiaryRequestDurationLookupSerializer
    queryset = BeneficiaryRequestDuration.objects.all()
    pagination_class = None

class ProvinceLookupView(generics.ListAPIView):
    serializer_class = ProvinceLookupSerializer
    queryset = Province.objects.all()
    pagination_class = None

class CityLookupView(generics.ListAPIView):
    serializer_class = CityLookupSerializer
    queryset = City.objects.all()
    pagination_class = None