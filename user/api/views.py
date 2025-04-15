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
                        BeneficiaryAddressInfoSerializer
                        )
from django.contrib.auth.models import User
from beneficiary.models import (BeneficiaryUserRegistration,
                                BeneficiaryUserInformation,
                                BeneficiaryUserAddress)
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
    
class CharityLoginView(APIView):
    def post(self, request):
        serializer = CharityLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
        }, status=status.HTTP_200_OK)
    
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
    
class BeneficiaryLoginView(APIView):
    def post(self, request):
        serializer = BeneficiaryLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
        }, status=status.HTTP_200_OK)
    
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


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's authentication token
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=200)
    
class CharityUsernameUpdateView(APIView):
    permission_classes = [IsAdminOrCharity]

    def patch(self, request, pk):
        # Fetch the Charity instance
        try:
            charity_instance = Charity.objects.get(pk=pk)
        except Charity.DoesNotExist:
            return Response({"error": "Charity not found"}, status=404)

        # Get the new username from the request
        new_username = request.data.get('charity_username')  # Use 'charity_username' instead of 'username'

        if not new_username:
            return Response({"error": "Charity username is required"}, status=400)

        # Update the Charity model using the serializer
        serializer = CharityUsernameUpdate(instance=charity_instance, data={'charity_username': new_username}, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update the username in the User model
            user = request.user
            user.username = new_username
            user.save()

            return Response({"message": "Charity username updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CharityPasswordUpdateView(APIView):
    permission_classes = [IsAdminOrCharity]

    def patch(self, request, pk):
        # Fetch the Charity instance
        try:
            charity_instance = Charity.objects.get(pk=pk)
        except Charity.DoesNotExist:
            return Response({"error": "Charity not found"}, status=404)

        # Get the new password from the request
        new_password = request.data.get('charity_password')  # Use 'charity_password' instead of 'password'

        if not new_password:
            return Response({"error": "Charity password is required"}, status=400)

        # Update the Charity model using the serializer
        serializer = CharityPasswordUpdateSerializer(instance=charity_instance, data={'charity_password': new_password}, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update the password in the User model
            user = request.user
            user.set_password(new_password)
            user.save()

            return Response({"message": "Charity password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BeneficiaryPasswordUpdateView(APIView):
    permission_classes = [IsCertainBeneficiary]

    def patch(self, request, pk):
        # Fetch the Charity instance
        try:
            charity_instance = BeneficiaryUserRegistration.objects.get(pk=pk)
        except BeneficiaryUserRegistration.DoesNotExist:
            return Response({"error": "Charity not found"}, status=404)

        # Get the new password from the request
        new_password = request.data.get('password')  # Use 'charity_password' instead of 'password'

        if not new_password:
            return Response({"error": "password is required"}, status=400)

        # Update the Charity model using the serializer
        serializer = BeneficiaryPasswordUpdate(instance=charity_instance, data={'password': new_password}, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update the password in the User model
            user = request.user
            user.set_password(new_password)
            user.save()

            return Response({"message": "Beneficiary password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
