from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import generics, filters
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import Http404
from beneficiary.models import BeneficiaryUserRegistration
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
                          BeneficiaryRequestDurationLookupSerializer)
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

        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
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
        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
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
        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
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
        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
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
        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
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
    
class BeneficiarySingleChildUpdateView(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestChildCreateSerializer

    def get_object(self):
        obj = get_object_or_404(BeneficiaryRequestChild, pk=self.kwargs.get('request_pk'))

        if obj.beneficiary_request_child_processing_stage.beneficiary_request_processing_stage_name.lower() != "submitted":
            raise PermissionDenied("You can only update or delete a request in the 'submitted' stage.")

        self.check_object_permissions(self.request, obj)
        return obj
    
class BeneficiaryRequestHistoriesGetView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestHistorySerializer

    def get_queryset(self):
        # Get the 'pk' from the URL
        beneficiary_request = self.kwargs.get('request_pk')

        # Filter requests based on beneficiary
        return BeneficiaryRequestHistory.objects.filter(
            beneficiary_request=beneficiary_request
        )

class BeneficiarySingleHistoryGetView(generics.RetrieveAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestHistorySerializer

    def get_object(self):
        request_pk = self.kwargs.get('request_pk')
        return get_object_or_404(BeneficiaryRequestHistory, pk=request_pk)

class AnnouncementView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = AnnouncementSerializer
    def get_queryset(self):
        # Get the 'pk' from the URL
        beneficiary = self.kwargs.get('pk')

        # Filter requests based on beneficiary
        return CharityAnnouncementToBeneficiary.objects.filter(
            beneficiary_user_registration=beneficiary
        )

class AnnouncementRequestView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestAnnouncementSerializer

    def get_queryset(self):
        request_pk = self.kwargs.get('request_pk')

        return CharityAnnouncementForRequest.objects.filter(
            beneficiary_request=BeneficiaryRequest.objects.get(pk=request_pk)
        )

class BeneficiaryRequestTypeLayer1View(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestTypeLayer1Serializer
    queryset = BeneficiaryRequestTypeLayer1.objects.all()

class BeneficiaryRequestTypeLayer2View(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestTypeLayer2Serializer
    queryset = BeneficiaryRequestTypeLayer2.objects.all()

class BeneficiaryRequestProcessingStageView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestProcessingStageSerializer
    queryset = BeneficiaryRequestProcessingStage.objects.all()

class BeneficiaryRequestDurationLookupView(generics.ListAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryRequestDurationLookupSerializer
    queryset = BeneficiaryRequestDuration.objects.all()
