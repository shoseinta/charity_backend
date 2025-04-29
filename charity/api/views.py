from rest_framework import generics,filters
from beneficiary.models import (BeneficiaryUserRegistration,
                                BeneficiaryUserInformation,
                                BeneficiaryUserAddress,
                                BeneficiaryUserAdditionalInfo,
                                CharityAnnouncementToBeneficiary,)
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
                          BeneficiaryRequestAnnouncementUpdateSerializer,
                          CharityAnnouncementToBeneficiarySerializer,
                          BeneficiaryRequestGetOnetimeSerializer,
                          BeneficiaryRequestGetRecurringSerializer)
from user.api.permissions import IsAdminOrCharity, IsCertainBeneficiary
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.filters import OrderingFilter

from django.db.models import Q
from datetime import date
from dateutil.relativedelta import relativedelta

from rest_framework import generics
from django.db.models import Q
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models import F, Case, When, Value, DateTimeField
from django.db.models.functions import Coalesce
from datetime import datetime
import meilisearch
from core.cache_manager import GlobalCacheManager
from django.db.models import Prefetch


client = meilisearch.Client("http://127.0.0.1:7700", 'search-master-key')

class MeiliSearchRequestMixin:
    def meili_filtered_queryset(self, base_queryset):
        search_query = self.request.query_params.get("search")
        if not search_query:
            return base_queryset

        try:
            results = client.index("requests").search(search_query)
            ids = [int(hit["id"]) for hit in results.get("hits", [])]
            return base_queryset.filter(pk__in=ids)
        except Exception:
            return base_queryset  # fallback on failure

client = meilisearch.Client("http://127.0.0.1:7700", "search-master-key")

class BeneficiaryListView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['beneficiary_user_information__last_name', 'beneficiary_user_information__first_name']
    ordering = ['beneficiary_user_information__last_name', 'beneficiary_user_information__first_name']

    def get_filtered_list(self, param_name):
        raw_values = self.request.query_params.getlist(param_name)
        combined = ','.join(raw_values)
        return [val.strip() for val in combined.split(',') if val.strip()]

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        page = self.request.query_params.get("page", 1)
        filters_dict = {
            'gender': ",".join(self.get_filtered_list('gender')),
            'province': ",".join(self.get_filtered_list('province')),
            'tag': ",".join(self.get_filtered_list('tag')),
            'min_age': self.request.query_params.get('min_age', ''),
            'max_age': self.request.query_params.get('max_age', ''),
        }


        base_queryset = BeneficiaryUserRegistration.objects.select_related(
            'beneficiary_user_information',
            'beneficiary_user_address__province',
            'beneficiary_user_address__city'
        ).only(
            'beneficiary_user_registration_id',
            'identification_number',
            'beneficiary_id',
            'phone_number',
            'email',
            'beneficiary_user_information__first_name',
            'beneficiary_user_information__last_name',
            'beneficiary_user_information__gender',
            'beneficiary_user_information__birth_date',
            'beneficiary_user_address__province__province_name',
            'beneficiary_user_address__city__city_name',
        ).prefetch_related(
            Prefetch(
                'beneficiary_user_additional_info',
                queryset=BeneficiaryUserAdditionalInfo.objects.only(
                    'beneficiary_user_registration',  # relation field
                    'beneficiary_user_additional_info_title'
                )
            )
        )



        if search_query:
            try:
                results = client.index("beneficiaries").search(search_query)
                matching_ids = [int(hit["id"]) for hit in results["hits"]]
                base_queryset = base_queryset.filter(beneficiary_user_registration_id__in=matching_ids)
            except Exception:
                pass

            return base_queryset

        cache_key = GlobalCacheManager.make_paginated_key("beneficiary:list", page, **filters_dict)
        cached_queryset = GlobalCacheManager.get(cache_key)
        if cached_queryset:
            return cached_queryset

        queryset = base_queryset

        genders = self.get_filtered_list('gender')
        provinces = self.get_filtered_list('province')
        tags = self.get_filtered_list('tag')
        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')

        if genders:
            queryset = queryset.filter(beneficiary_user_information__gender__in=genders)

        if provinces:
            queryset = queryset.filter(beneficiary_user_address__province__province_name__in=provinces)

        if tags:
            tag_filter = Q()
            for tag in tags:
                tag_filter |= Q(
                    beneficiary_user_additional_info__beneficiary_user_additional_info_title__icontains=tag
                )
            queryset = queryset.filter(tag_filter).distinct()

        today = date.today()
        if min_age:
            try:
                min_age = int(min_age)
                max_birth_date = today - relativedelta(years=min_age)
                queryset = queryset.filter(beneficiary_user_information__birth_date__lte=max_birth_date)
            except (ValueError, TypeError):
                pass

        if max_age:
            try:
                max_age = int(max_age)
                min_birth_date = today - relativedelta(years=max_age)
                queryset = queryset.filter(beneficiary_user_information__birth_date__gte=min_birth_date)
            except (ValueError, TypeError):
                pass

        GlobalCacheManager.set(cache_key, queryset)
        return queryset



class BeneficiaryRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = RequestCreationSerializer

    @staticmethod
    def get_queryset():
        return BeneficiaryRequest.objects.select_related(
            'beneficiary_request_type_layer1',
            'beneficiary_request_type_layer2'
        )

    def perform_create(self, serializer):
        beneficiary_pk = self.kwargs.get('pk')  # Get pk from URL
        serializer.save(beneficiary_user_registration_id=beneficiary_pk)


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
    

class BeneficiaryAllRequestsView(generics.ListAPIView, MeiliSearchRequestMixin):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]

    ordering_fields = [
        'effective_date',
        'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id'
    ]
    ordering = ['effective_date']

    def get_queryset(self):
        qs = BeneficiaryRequest.objects.all()

        # Annotate effective date
        qs = qs.annotate(
            effective_date=Coalesce(
                'beneficiary_request_date',
                'beneficiary_request_created_at',
                output_field=DateTimeField()
            )
        )

        request = self.request
        params = request.query_params

        def get_list(param):
            return [p.strip() for p in params.get(param, '').split(',') if p.strip()]

        # Filtering
        layer1_ids = get_list('layer1_id')
        if layer1_ids:
            qs = qs.filter(beneficiary_request_type_layer1__beneficiary_request_type_layer1_id__in=layer1_ids)

        layer2_ids = get_list('layer2_id')
        if layer2_ids:
            qs = qs.filter(beneficiary_request_type_layer2__beneficiary_request_type_layer2_id__in=layer2_ids)

        duration_ids = get_list('duration_id')
        if duration_ids:
            qs = qs.filter(beneficiary_request_duration__beneficiary_request_duration_id__in=duration_ids)

        processing_stage_ids = get_list('processing_stage_id')
        if processing_stage_ids:
            qs = qs.filter(beneficiary_request_processing_stage__beneficiary_request_processing_stage_id__in=processing_stage_ids)

        limits = get_list('limit')
        if limits:
            qs = qs.filter(beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit__in=limits)

        deadlines = get_list('deadline')
        if deadlines:
            try:
                deadlines = [datetime.strptime(d, '%Y-%m-%d').date() for d in deadlines]
                qs = qs.filter(beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline__in=deadlines)
            except ValueError:
                pass  # ignore invalid date formats

        # Effective date range
        min_effective_date = params.get('min_effective_date')
        max_effective_date = params.get('max_effective_date')

        if min_effective_date:
            try:
                min_date = datetime.strptime(min_effective_date, '%Y-%m-%d')
                qs = qs.filter(effective_date__gte=min_date)
            except ValueError:
                pass

        if max_effective_date:
            try:
                max_date = datetime.strptime(max_effective_date, '%Y-%m-%d')
                qs = qs.filter(effective_date__lte=max_date)
            except ValueError:
                pass
        
        qs = self.meili_filtered_queryset(qs)
        return qs

class SingleBeneficiaryAllRequestsView(generics.ListAPIView, MeiliSearchRequestMixin):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]

    ordering_fields = [
        'effective_date',
        'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id'
    ]
    ordering = ['effective_date']

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        qs = BeneficiaryRequest.objects.filter(beneficiary_user_registration = pk)

        # Annotate effective date
        qs = qs.annotate(
            effective_date=Coalesce(
                'beneficiary_request_date',
                'beneficiary_request_created_at',
                output_field=DateTimeField()
            )
        )

        request = self.request
        params = request.query_params

        def get_list(param):
            return [p.strip() for p in params.get(param, '').split(',') if p.strip()]

        # Filtering
        layer1_ids = get_list('layer1_id')
        if layer1_ids:
            qs = qs.filter(beneficiary_request_type_layer1__beneficiary_request_type_layer1_id__in=layer1_ids)

        layer2_ids = get_list('layer2_id')
        if layer2_ids:
            qs = qs.filter(beneficiary_request_type_layer2__beneficiary_request_type_layer2_id__in=layer2_ids)

        duration_ids = get_list('duration_id')
        if duration_ids:
            qs = qs.filter(beneficiary_request_duration__beneficiary_request_duration_id__in=duration_ids)

        processing_stage_ids = get_list('processing_stage_id')
        if processing_stage_ids:
            qs = qs.filter(beneficiary_request_processing_stage__beneficiary_request_processing_stage_id__in=processing_stage_ids)

        limits = get_list('limit')
        if limits:
            qs = qs.filter(beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit__in=limits)

        deadlines = get_list('deadline')
        if deadlines:
            try:
                deadlines = [datetime.strptime(d, '%Y-%m-%d').date() for d in deadlines]
                qs = qs.filter(beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline__in=deadlines)
            except ValueError:
                pass  # ignore invalid date formats

        # Effective date range
        min_effective_date = params.get('min_effective_date')
        max_effective_date = params.get('max_effective_date')

        if min_effective_date:
            try:
                min_date = datetime.strptime(min_effective_date, '%Y-%m-%d')
                qs = qs.filter(effective_date__gte=min_date)
            except ValueError:
                pass

        if max_effective_date:
            try:
                max_date = datetime.strptime(max_effective_date, '%Y-%m-%d')
                qs = qs.filter(effective_date__lte=max_date)
            except ValueError:
                pass
        
        qs = self.meili_filtered_queryset(qs)
        return qs
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

class BeneficiaryRequestFilterMixin:
    def apply_filters(self, queryset):
        params = self.request.query_params

        def get_list(param):
            return [p.strip() for p in params.get(param, '').split(',') if p.strip()]

        from datetime import datetime

        # Filtering for ID fields
        layer1_ids = get_list('layer1_id')
        if layer1_ids:
            queryset = queryset.filter(
                beneficiary_request_type_layer1__beneficiary_request_type_layer1_id__in=layer1_ids
            )

        layer2_ids = get_list('layer2_id')
        if layer2_ids:
            queryset = queryset.filter(
                beneficiary_request_type_layer2__beneficiary_request_type_layer2_id__in=layer2_ids
            )

        duration_ids = get_list('duration_id')
        if duration_ids:
            queryset = queryset.filter(
                beneficiary_request_duration__beneficiary_request_duration_id__in=duration_ids
            )

        processing_stage_ids = get_list('processing_stage_id')
        if processing_stage_ids:
            queryset = queryset.filter(
                beneficiary_request_processing_stage__beneficiary_request_processing_stage_id__in=processing_stage_ids
            )

        # Range filtering for recurring limit
        limit_min = params.get('limit_min')
        limit_max = params.get('limit_max')
        if limit_min:
            try:
                queryset = queryset.filter(
                    beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit__gte=int(limit_min)
                )
            except ValueError:
                pass
        if limit_max:
            try:
                queryset = queryset.filter(
                    beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit__lte=int(limit_max)
                )
            except ValueError:
                pass

        # Range filtering for onetime deadline
        deadline_min = params.get('deadline_min')
        deadline_max = params.get('deadline_max')
        if deadline_min:
            try:
                min_date = datetime.strptime(deadline_min, '%Y-%m-%d').date()
                queryset = queryset.filter(
                    beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline__gte=min_date
                )
            except ValueError:
                pass

        if deadline_max:
            try:
                max_date = datetime.strptime(deadline_max, '%Y-%m-%d').date()
                queryset = queryset.filter(
                    beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline__lte=max_date
                )
            except ValueError:
                pass

        # Range filtering for effective date
        min_effective_date = params.get('min_effective_date')
        max_effective_date = params.get('max_effective_date')
        if min_effective_date:
            try:
                min_date = datetime.strptime(min_effective_date, '%Y-%m-%d')
                queryset = queryset.filter(effective_date__gte=min_date)
            except ValueError:
                pass

        if max_effective_date:
            try:
                max_date = datetime.strptime(max_effective_date, '%Y-%m-%d')
                queryset = queryset.filter(effective_date__lte=max_date)
            except ValueError:
                pass

        return queryset



class BeneficiaryNewRequestGetView(BeneficiaryRequestFilterMixin, MeiliSearchRequestMixin, generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date', 'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id']
    ordering = ['effective_date']

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        page = self.request.query_params.get("page", 1)

        if search_query:
            # If search is active, do not cache, return real-time queryset
            base_qs = BeneficiaryRequest.objects.annotate(
                effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
            ).filter(
                beneficiary_request_processing_stage__in=[
                    BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='submitted'),
                    BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='pending_review'),
                    BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='under_evaluation'),
                ]
            )
            base_qs = self.meili_filtered_queryset(base_qs)
            return self.apply_filters(base_qs)

        # No search → apply caching
        filters_dict = {
            'stage': 'new'
        }
        cache_key = GlobalCacheManager.make_paginated_key("request:list:new", page, **filters_dict)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        # Generate queryset
        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
            beneficiary_request_processing_stage__in=[
                BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='submitted'),
                BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='pending_review'),
                BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='under_evaluation'),
            ]
        )

        base_qs = self.meili_filtered_queryset(base_qs)
        filtered_qs = self.apply_filters(base_qs)

        GlobalCacheManager.set(cache_key, filtered_qs)

        return filtered_qs

    
class BeneficiaryOldRequestOnetimeGetView(BeneficiaryRequestFilterMixin, MeiliSearchRequestMixin, generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date', 'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id']
    ordering = ['effective_date']

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        page = self.request.query_params.get("page", 1)

        if search_query:
            # If searching, don't cache
            base_qs = BeneficiaryRequest.objects.annotate(
                effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
            ).filter(
                beneficiary_request_processing_stage__in=[
                    BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='approved'),
                    BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='in_progress'),
                ],
                beneficiary_request_duration__in=[
                    BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='one_time')
                ]
            )
            base_qs = self.meili_filtered_queryset(base_qs)
            return self.apply_filters(base_qs)

        # No search: use cache
        filters_dict = {
            'stage': 'old_onetime'
        }
        cache_key = GlobalCacheManager.make_paginated_key("request:list:old_onetime", page, **filters_dict)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
            beneficiary_request_processing_stage__in=[
                BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='approved'),
                BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='in_progress'),
            ],
            beneficiary_request_duration__in=[
                BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='one_time')
            ]
        )

        base_qs = self.meili_filtered_queryset(base_qs)
        filtered_qs = self.apply_filters(base_qs)

        GlobalCacheManager.set(cache_key, filtered_qs)

        return filtered_qs


    
class BeneficiaryOldRequestOngoingGetView(BeneficiaryRequestFilterMixin, MeiliSearchRequestMixin, generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date', 'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id']
    ordering = ['effective_date']

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        page = self.request.query_params.get("page", 1)

        if search_query:
            # If searching, no cache
            base_qs = BeneficiaryRequest.objects.annotate(
                effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
            ).filter(
                beneficiary_request_processing_stage__in=[
                    BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='approved'),
                    BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='in_progress'),
                ],
                beneficiary_request_duration__in=[
                    BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='recurring'),
                    BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='permanent'),
                ]
            )
            base_qs = self.meili_filtered_queryset(base_qs)
            return self.apply_filters(base_qs)

        # No search: cache based on page
        filters_dict = {
            'stage': 'old_ongoing'
        }
        cache_key = GlobalCacheManager.make_paginated_key("request:list:old_ongoing", page, **filters_dict)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        base_qs = BeneficiaryRequest.objects.annotate(
            effective_date=Coalesce('beneficiary_request_date', 'beneficiary_request_created_at', output_field=DateTimeField())
        ).filter(
            beneficiary_request_processing_stage__in=[
                BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='approved'),
                BeneficiaryRequestProcessingStage.objects.get(beneficiary_request_processing_stage_name='in_progress'),
            ],
            beneficiary_request_duration__in=[
                BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='recurring'),
                BeneficiaryRequestDuration.objects.get(beneficiary_request_duration_name='permanent'),
            ]
        )

        base_qs = self.meili_filtered_queryset(base_qs)
        filtered_qs = self.apply_filters(base_qs)

        GlobalCacheManager.set(cache_key, filtered_qs)

        return filtered_qs


    
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

class BeneficiaryAnnouncementListView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = CharityAnnouncementToBeneficiarySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        cache_key = GlobalCacheManager.make_key("beneficiary", "announcement:list", pk)

        queryset = GlobalCacheManager.get(cache_key)
        if queryset:
            return queryset

        try:
            single_user = BeneficiaryUserRegistration.objects.get(pk=pk)
            queryset = CharityAnnouncementToBeneficiary.objects.filter(
                beneficiary_user_registration=single_user
            )
            GlobalCacheManager.set(cache_key, queryset)
            return queryset

        except BeneficiaryUserRegistration.DoesNotExist:
            raise Http404("BeneficiaryUserRegistration does not exist")


class BeneficiaryAnnouncementCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = CharityAnnouncementToBeneficiarySerializer

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        try:
            single_user = BeneficiaryUserRegistration.objects.get(pk=pk)
            serializer.save(beneficiary_user_registration=single_user)
        except BeneficiaryUserRegistration.DoesNotExist:
            raise Http404("BeneficiaryUserRegistration does not exist")
        
class BeneficiaryAnnouncementUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = CharityAnnouncementToBeneficiarySerializer
    queryset = CharityAnnouncementToBeneficiary.objects.all()
    lookup_field = 'pk'

class SingleRequestHistoriesView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = SingleRequestHistorySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            single_request = BeneficiaryRequest.objects.get(pk=pk)
            return BeneficiaryRequestHistory.objects.filter(beneficiary_request=single_request)
        except BeneficiaryRequest.DoesNotExist:
            raise Http404("BeneficiaryRequest does not exist")
        
class SingleRequestChildsView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = SingleRequestChildSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            single_request = BeneficiaryRequest.objects.get(pk=pk)
            return BeneficiaryRequestChild.objects.filter(beneficiary_request=single_request)
        except BeneficiaryRequest.DoesNotExist:
            raise Http404("BeneficiaryRequest does not exist")

class AllRequestChildsView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = SingleRequestChildSerializer
    queryset = BeneficiaryRequestChild.objects.all()
