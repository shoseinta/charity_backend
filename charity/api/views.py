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
                            CharityAnnouncementForRequest,
                            BeneficiaryRequestTypeLayer1,
                            BeneficiaryRequestTypeLayer2,
                            BeneficiaryRequestProcessingStage)
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
                          BeneficiaryRequestTypeLayer1Serializer,
                          BeneficiaryRequestTypeLayer2Serializer,
                          BeneficiaryRequestProcessingStageSerializer,
                          BeneficiaryRequestDurationLookupSerializer)
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
        genders = self.get_filtered_list('gender')
        provinces = self.get_filtered_list('province')
        tags = self.get_filtered_list('tag')
        min_age = self.request.query_params.get('min_age')
        max_age = self.request.query_params.get('max_age')
        search_query = self.request.query_params.get("search")
        page = self.request.query_params.get("page", 1)
        filters_dict = {
            'gender': ",".join(self.get_filtered_list('gender')),
            'province': ",".join(self.get_filtered_list('province')),
            'tag': ",".join(self.get_filtered_list('tag')),
            'min_age': self.request.query_params.get('min_age', ''),
            'max_age': self.request.query_params.get('max_age', ''),
        }
        cache_key = GlobalCacheManager.make_paginated_key("beneficiary:list", page, **filters_dict)
        cached_queryset = GlobalCacheManager.get(cache_key)
        if cached_queryset:
            return cached_queryset
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
        
        if not(search_query or genders or provinces or tags or min_age or max_age):
            return base_queryset
        if search_query:
            try:
                results = client.index("beneficiaries").search(search_query)
                matching_ids = [int(hit["id"]) for hit in results["hits"]]
                base_queryset = base_queryset.filter(beneficiary_user_registration_id__in=matching_ids)
            except Exception:
                pass

            return base_queryset

        if genders:
            try:
                base_queryset = base_queryset.filter(
                    Q(beneficiary_user_information__gender__in=genders) | 
                    Q(beneficiary_user_information__isnull=True)
                )
            except:
                pass
        if provinces:
            try:
                base_queryset = base_queryset.filter(
                    Q(beneficiary_user_address__province__province_name__in=provinces) |
                    Q(beneficiary_user_address__isnull=True)
                )
            except:
                pass
        if tags:
            tag_filter = Q()
            for tag in tags:
                tag_filter |= Q(
                    beneficiary_user_additional_info__beneficiary_user_additional_info_title__icontains=tag
                )
            base_queryset = base_queryset.filter(tag_filter).distinct()

        today = date.today()
        if min_age:
            try:
                min_age = int(min_age)
                max_birth_date = today - relativedelta(years=min_age)
                base_queryset = base_queryset.filter(
                    Q(beneficiary_user_information__birth_date__lte=max_birth_date) |
                    Q(beneficiary_user_information__isnull=True)
                )
            except (ValueError, TypeError):
                pass

        if max_age:
            try:
                max_age = int(max_age)
                min_birth_date = today - relativedelta(years=max_age)
                base_queryset = base_queryset.filter(
                    Q(beneficiary_user_information__birth_date__gte=min_birth_date) |
                    Q(beneficiary_user_information__isnull=True)
                )
            except (ValueError, TypeError):
                pass

        GlobalCacheManager.set(cache_key, base_queryset)
        return base_queryset



class BeneficiaryRequestCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = RequestCreationSerializer

    def get_queryset(self):
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
    

class BeneficiaryAllRequestsView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]

    ordering_fields = [
        'effective_date',
        'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id'
    ]
    ordering = ['effective_date']

    def get_queryset(self):
        qs = BeneficiaryRequest.objects.select_related(
            'beneficiary_user_registration',
            'beneficiary_request_duration_onetime',
            'beneficiary_request_duration_recurring',
        ).prefetch_related(
            Prefetch('beneficiary_user_registration__beneficiary_user_information'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__province'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__city'),
        ).only(
            "beneficiary_request_id",
            "beneficiary_user_registration__beneficiary_user_registration_id",
            "beneficiary_user_registration__beneficiary_user_information__first_name",
            "beneficiary_user_registration__beneficiary_user_information__last_name",
            "beneficiary_user_registration__beneficiary_id",
            "beneficiary_user_registration__identification_number",
            "beneficiary_user_registration__beneficiary_user_address__province__province_name",
            "beneficiary_user_registration__beneficiary_user_address__city__city_name",
            "beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline",
            "beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit",
            "beneficiary_request_title",
            "beneficiary_request_description",
            "beneficiary_request_document",
            "beneficiary_request_date",
            "beneficiary_request_time",
            "beneficiary_request_created_at",
            "beneficiary_request_updated_at",
            "effective_date",
            "beneficiary_request_type_layer1",
            "beneficiary_request_type_layer2",
            "beneficiary_request_duration",
            "beneficiary_request_processing_stage",
        )

        # Annotate effective date
        request = self.request
        params = request.query_params
        if not params:
            return qs

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
        
        search_query = self.request.query_params.get("search")
        if not search_query:
            return qs
        if search_query:
            try:
                results = client.index("requests").search(search_query)
                ids = [int(hit["id"]) for hit in results.get("hits", [])]
                return qs.filter(pk__in=ids)
            except Exception:
                return qs
        return qs

class SingleBeneficiaryAllRequestsView(generics.ListAPIView):
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
        search_query = self.request.query_params('search')
        if not search_query:
            return qs
        if search_query:
            try:
                results = client.index("requests").search(search_query)
                ids = [int(hit["id"]) for hit in results.get("hits", [])]
                return qs.filter(pk__in=ids)
            except Exception:
                return qs
        
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

class BeneficiaryNewRequestGetView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date', 'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id']
    ordering = ['effective_date']
    _processing_stage_ids = None
    
    @classmethod
    def get_processing_stage_ids(cls):
        if cls._processing_stage_ids is None:
            stage_names = ['submitted', 'pending_review', 'under_evaluation']
            cls._processing_stage_ids = list(
                BeneficiaryRequestProcessingStage.objects.filter(
                    beneficiary_request_processing_stage_name__in=stage_names
                ).values_list('pk', flat=True)
            )
        return cls._processing_stage_ids

    def get_queryset(self):
        qs = BeneficiaryRequest.objects.select_related(
            'beneficiary_user_registration',
            'beneficiary_request_duration_onetime',
            'beneficiary_request_duration_recurring',
        ).prefetch_related(
            Prefetch('beneficiary_user_registration__beneficiary_user_information'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__province'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__city'),
        ).only(
            "beneficiary_request_id",
            "beneficiary_user_registration__beneficiary_user_registration_id",
            "beneficiary_user_registration__beneficiary_user_information__first_name",
            "beneficiary_user_registration__beneficiary_user_information__last_name",
            "beneficiary_user_registration__beneficiary_id",
            "beneficiary_user_registration__identification_number",
            "beneficiary_user_registration__beneficiary_user_address__province__province_name",
            "beneficiary_user_registration__beneficiary_user_address__city__city_name",
            "beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline",
            "beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit",
            "beneficiary_request_title",
            "beneficiary_request_description",
            "beneficiary_request_document",
            "beneficiary_request_date",
            "beneficiary_request_time",
            "beneficiary_request_created_at",
            "beneficiary_request_updated_at",
            "effective_date",
            "beneficiary_request_type_layer1",
            "beneficiary_request_type_layer2",
            "beneficiary_request_duration",
            "beneficiary_request_processing_stage",
        ).filter(
            beneficiary_request_processing_stage__in = self.get_processing_stage_ids()
        )

        # Annotate effective date
        request = self.request
        params = request.query_params
        if not params:
            return qs

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
        
        search_query = self.request.query_params.get("search")
        if not search_query:
            return qs
        if search_query:
            try:
                results = client.index("requests").search(search_query)
                ids = [int(hit["id"]) for hit in results.get("hits", [])]
                return qs.filter(pk__in=ids)
            except Exception:
                return qs
        return qs

class BeneficiaryOldRequestOnetimeGetView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date', 'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id']
    ordering = ['effective_date']
    _processing_stage_ids = None
    _duration_ids = None
    
    @classmethod
    def get_processing_stage_ids(cls):
        if cls._processing_stage_ids is None:
            stage_names = ['approved', 'in_progress']
            cls._processing_stage_ids = list(
                BeneficiaryRequestProcessingStage.objects.filter(
                    beneficiary_request_processing_stage_name__in=stage_names
                ).values_list('pk', flat=True)
            )
        return cls._processing_stage_ids
    def get_queryset(self):
        qs = BeneficiaryRequest.objects.select_related(
            'beneficiary_user_registration',
            'beneficiary_request_duration_onetime',
            'beneficiary_request_duration_recurring',
        ).prefetch_related(
            Prefetch('beneficiary_user_registration__beneficiary_user_information'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__province'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__city'),
        ).only(
            "beneficiary_request_id",
            "beneficiary_user_registration__beneficiary_user_registration_id",
            "beneficiary_user_registration__beneficiary_user_information__first_name",
            "beneficiary_user_registration__beneficiary_user_information__last_name",
            "beneficiary_user_registration__beneficiary_id",
            "beneficiary_user_registration__identification_number",
            "beneficiary_user_registration__beneficiary_user_address__province__province_name",
            "beneficiary_user_registration__beneficiary_user_address__city__city_name",
            "beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline",
            "beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit",
            "beneficiary_request_title",
            "beneficiary_request_description",
            "beneficiary_request_document",
            "beneficiary_request_date",
            "beneficiary_request_time",
            "beneficiary_request_created_at",
            "beneficiary_request_updated_at",
            "effective_date",
            "beneficiary_request_type_layer1",
            "beneficiary_request_type_layer2",
            "beneficiary_request_duration",
            "beneficiary_request_processing_stage",
        ).filter(
            beneficiary_request_processing_stage__in = self.get_processing_stage_ids(),
            beneficiary_request_duration = 1
        )

        # Annotate effective date
        request = self.request
        params = request.query_params
        if not params:
            return qs

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
        
        search_query = self.request.query_params.get("search")
        if not search_query:
            return qs
        if search_query:
            try:
                results = client.index("requests").search(search_query)
                ids = [int(hit["id"]) for hit in results.get("hits", [])]
                return qs.filter(pk__in=ids)
            except Exception:
                return qs
        return qs    
    
class BeneficiaryOldRequestOngoingGetView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryGetRequestSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['effective_date', 'beneficiary_request_processing_stage__beneficiary_request_processing_stage_id']
    ordering = ['effective_date']
    _processing_stage_ids = None
    _duration_ids = None
    
    @classmethod
    def get_processing_stage_ids(cls):
        if cls._processing_stage_ids is None:
            stage_names = ['approved', 'in_progress']
            cls._processing_stage_ids = list(
                BeneficiaryRequestProcessingStage.objects.filter(
                    beneficiary_request_processing_stage_name__in=stage_names
                ).values_list('pk', flat=True)
            )
        return cls._processing_stage_ids
    def get_queryset(self):
        qs = BeneficiaryRequest.objects.select_related(
            'beneficiary_user_registration',
            'beneficiary_request_duration_onetime',
            'beneficiary_request_duration_recurring',
        ).prefetch_related(
            Prefetch('beneficiary_user_registration__beneficiary_user_information'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__province'),
            Prefetch('beneficiary_user_registration__beneficiary_user_address__city'),
        ).only(
            "beneficiary_request_id",
            "beneficiary_user_registration__beneficiary_user_registration_id",
            "beneficiary_user_registration__beneficiary_user_information__first_name",
            "beneficiary_user_registration__beneficiary_user_information__last_name",
            "beneficiary_user_registration__beneficiary_id",
            "beneficiary_user_registration__identification_number",
            "beneficiary_user_registration__beneficiary_user_address__province__province_name",
            "beneficiary_user_registration__beneficiary_user_address__city__city_name",
            "beneficiary_request_duration_onetime__beneficiary_request_duration_onetime_deadline",
            "beneficiary_request_duration_recurring__beneficiary_request_duration_recurring_limit",
            "beneficiary_request_title",
            "beneficiary_request_description",
            "beneficiary_request_document",
            "beneficiary_request_date",
            "beneficiary_request_time",
            "beneficiary_request_created_at",
            "beneficiary_request_updated_at",
            "effective_date",
            "beneficiary_request_type_layer1",
            "beneficiary_request_type_layer2",
            "beneficiary_request_duration",
            "beneficiary_request_processing_stage",
        ).filter(
            beneficiary_request_processing_stage__in = self.get_processing_stage_ids(),
            beneficiary_request_duration__in = [2,3],
        )

        # Annotate effective date
        request = self.request
        params = request.query_params
        if not params:
            return qs

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
        
        search_query = self.request.query_params.get("search")
        if not search_query:
            return qs
        if search_query:
            try:
                results = client.index("requests").search(search_query)
                ids = [int(hit["id"]) for hit in results.get("hits", [])]
                return qs.filter(pk__in=ids)
            except Exception:
                return qs
        return qs

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

class BeneficiaryRequestTypeLayer1View(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestTypeLayer1Serializer
    queryset = BeneficiaryRequestTypeLayer1.objects.all()

class BeneficiaryRequestTypeLayer2View(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestTypeLayer2Serializer
    queryset = BeneficiaryRequestTypeLayer2.objects.all()

class BeneficiaryRequestProcessingStageView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestProcessingStageSerializer
    queryset = BeneficiaryRequestProcessingStage.objects.all()

class BeneficiaryRequestDurationLookupView(generics.ListAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = BeneficiaryRequestDurationLookupSerializer
    queryset = BeneficiaryRequestDuration.objects.all()