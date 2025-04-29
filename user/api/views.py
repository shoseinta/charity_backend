from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .serializers import (CharityRegistrationSerializer,
                        CharityLoginSerializer,
                        BeneficiaryRegistrationSerializer, 
                        BeneficiaryLoginSerializer,
                        BeneficiaryUserRegistrationInfoSerializer,
                        BeneficiaryInformationSerializer,
                        BeneficiaryInformationSingleSerializer,
                        CharityUsernameUpdate,
                        CharityPasswordUpdateSerializer,
                        BeneficiaryPasswordUpdate,
                        BeneficiaryAddressInfoSerializer,
                        BeneficiaryAdditionalInfoSerializer,
                        CharityWorkFieldSerializer,
                        )
from django.contrib.auth.models import User
from beneficiary.models import (BeneficiaryUserRegistration,
                                BeneficiaryUserInformation,
                                BeneficiaryUserAddress,
                                BeneficiaryUserAdditionalInfo)
from request.models import CharityWorkfield
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrCharity, IsCertainBeneficiary
from charity.models import Charity


class CharityRegistrationView(generics.CreateAPIView):
    serializer_class = CharityRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to register
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # You can add email verification logic here if needed
        
        return Response({
            "user": serializer.data,
            "message": "User created successfully.",
        }, status=status.HTTP_201_CREATED)
    
class BeneficiaryRegisterView(generics.CreateAPIView):
    serializer_class = BeneficiaryRegistrationSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'status': 'success',
            'data': {
                'user_id': user.id,
                'beneficiary_id': user.username,
                'charity_id': user.beneficiaryuserregistration.charity.charity_id,
                'message': 'Beneficiary registered successfully'
            }
        }, status=status.HTTP_201_CREATED)
    
    
class BeneficiaryUserRegistrationInfoView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsCertainBeneficiary]
    queryset = BeneficiaryUserRegistration.objects.all()
    serializer_class = BeneficiaryUserRegistrationInfoSerializer
    lookup_field = 'beneficiary_user_registration_id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Only update fields that were provided
        if 'phone_number' in serializer.validated_data:
            instance.phone_number = serializer.validated_data['phone_number'] or None
        if 'email' in serializer.validated_data:
            instance.email = serializer.validated_data['email'] or None
        
        instance.save()
        
        return Response({
            'status': 'success',
            'data': {
                'phone_number': instance.phone_number,
                'email': instance.email,
                'beneficiary_id': instance.beneficiary_id
            }
        }, status=status.HTTP_200_OK)
    
class BeneficiaryInformationCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    queryset = BeneficiaryUserInformation.objects.all()
    serializer_class = BeneficiaryInformationSerializer


class BeneficiaryInformationSingleCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BeneficiaryInformationSingleSerializer
    
    def create(self, request, beneficiary_user_registration_id):
        try:
            # Get the user registration from URL parameter
            user_registration = BeneficiaryUserRegistration.objects.get(pk=beneficiary_user_registration_id)
            
            # Check for existing information
            if BeneficiaryUserInformation.objects.filter(
                beneficiary_user_registration=user_registration
            ).exists():
                return Response(
                    {"detail": "User information already exists for this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate and save with the URL-determined relationship
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Create the instance with the enforced relationship
            beneficiary_info = BeneficiaryUserInformation.objects.create(
                beneficiary_user_registration=user_registration,
                **serializer.validated_data
            )
            
            return Response(
                BeneficiaryInformationSingleSerializer(beneficiary_info).data,
                status=status.HTTP_201_CREATED
            )
            
        except BeneficiaryUserRegistration.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
    

class BeneficiaryAddressInfoView(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryAddressInfoSerializer
    
    def create(self, request, pk):
        try:
            # Get the user registration from URL parameter
            user_registration = BeneficiaryUserRegistration.objects.get(pk=pk)
            
            # Check for existing information
            if BeneficiaryUserAddress.objects.filter(
                beneficiary_user_registration=user_registration
            ).exists():
                return Response(
                    {"detail": "User address information already exists for this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate and save with the URL-determined relationship
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Create the instance with the enforced relationship
            beneficiary_info = BeneficiaryUserAddress.objects.create(
                beneficiary_user_registration=user_registration,
                **serializer.validated_data
            )
            
            return Response(
                BeneficiaryAddressInfoSerializer(beneficiary_info).data,
                status=status.HTTP_201_CREATED
            )
            
        except BeneficiaryUserRegistration.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class BeneficiaryAdditionalInfoView(generics.CreateAPIView):
    permission_classes = [IsCertainBeneficiary]
    serializer_class = BeneficiaryAdditionalInfoSerializer
    
    def create(self, request, pk):
        try:
            # Get the user registration from URL parameter
            user_registration = BeneficiaryUserRegistration.objects.get(pk=pk)
            # Validate and save with the URL-determined relationship
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Create the instance with the enforced relationship
            beneficiary_info = BeneficiaryUserAdditionalInfo.objects.create(
                beneficiary_user_registration=user_registration,
                **serializer.validated_data
            )
            
            return Response(
                BeneficiaryAdditionalInfoSerializer(beneficiary_info).data,
                status=status.HTTP_201_CREATED
            )
            
        except BeneficiaryUserRegistration.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class CharityWorkFieldView(generics.CreateAPIView):
    permission_classes = [IsAdminOrCharity]
    serializer_class = CharityWorkFieldSerializer
    
    def create(self, request, pk):
        try:
            # Validate and save with the URL-determined relationship
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_registration = Charity.objects.get(pk=pk)
            # Create the instance with the enforced relationship
            beneficiary_info = CharityWorkfield.objects.create(
                charity=user_registration,
                **serializer.validated_data
            )
            
            return Response(
                CharityWorkFieldSerializer(beneficiary_info).data,
                status=status.HTTP_201_CREATED
            )
            
        except Charity.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

# Corrected and Fully Implemented Views

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import (
    CharityLoginSerializer,
    BeneficiaryLoginSerializer,
    CharityUsernameUpdate,
    CharityPasswordUpdateSerializer,
    BeneficiaryPasswordUpdate,
)
from django.shortcuts import get_object_or_404
from charity.models import Charity
from beneficiary.models import BeneficiaryUserRegistration
from .permissions import IsAdminOrCharity, IsCertainBeneficiary
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

class CharityLoginView(APIView):
    serializer_class = CharityLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.pk,
            'username': user.username,
        }, status=status.HTTP_200_OK)


class BeneficiaryLoginView(APIView):
    serializer_class = BeneficiaryLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.pk,
            'username': user.username,
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# --- CharityUsernameUpdateView ---
class CharityUsernameUpdateView(APIView):
    serializer_class = CharityUsernameUpdate
    permission_classes = [IsAdminOrCharity]

    def patch(self, request, pk):
        charity_instance = get_object_or_404(Charity, pk=pk)
        new_username = request.data.get('charity_username')

        if not new_username:
            return Response({"error": "Charity username is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance=charity_instance, data={'charity_username': new_username}, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update related user model username too
            charity_instance.charity_user_id.username = new_username
            charity_instance.charity_user_id.save()

            return Response({"message": "Charity username updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- CharityPasswordUpdateView ---
class CharityPasswordUpdateView(APIView):
    serializer_class = CharityPasswordUpdateSerializer
    permission_classes = [IsAdminOrCharity]

    def patch(self, request, pk):
        charity_instance = get_object_or_404(Charity, pk=pk)
        new_password = request.data.get('charity_password')

        if not new_password:
            return Response({"error": "Charity password is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance=charity_instance, data={'charity_password': new_password}, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update related user model password too
            charity_instance.charity_user_id.set_password(new_password)
            charity_instance.charity_user_id.save()

            return Response({"message": "Charity password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- BeneficiaryPasswordUpdateView ---
class BeneficiaryPasswordUpdateView(APIView):
    serializer_class = BeneficiaryPasswordUpdate
    permission_classes = [IsCertainBeneficiary]

    def patch(self, request, pk):
        beneficiary_instance = get_object_or_404(BeneficiaryUserRegistration, pk=pk)
        new_password = request.data.get('password')

        if not new_password:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance=beneficiary_instance, data={'password': new_password}, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update related user model password too
            beneficiary_instance.benficiary_user_id.set_password(new_password)
            beneficiary_instance.benficiary_user_id.save()

            return Response({"message": "Beneficiary password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
