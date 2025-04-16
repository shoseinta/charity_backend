from rest_framework import generics
from beneficiary.models import BeneficiaryUserRegistration
from request.models import (BeneficiaryRequest,
                            BeneficiaryRequestHistory,
                            BeneficiaryRequestChild)
from .serializers import (BeneficiaryListSerializer,
                          RequestCreationSerializer,
                          BeneficiaryListSingleSerializer,
                          SingleRequestHistorySerializer)
from user.api.permissions import IsAdminOrCharity, IsCertainBeneficiary
from rest_framework.response import Response
from rest_framework import status


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
