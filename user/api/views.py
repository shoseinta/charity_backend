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
                        BeneficiaryInformationSingleSerializer
                        )
from django.contrib.auth.models import User
from beneficiary.models import (BeneficiaryUserRegistration,
                                BeneficiaryUserInformation)

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
    
class BeneficiaryUserRegistrationInfoView(generics.UpdateAPIView):
    queryset = BeneficiaryUserRegistration.objects.all()
    serializer_class = BeneficiaryUserRegistrationInfoSerializer
    lookup_field = 'pk'

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
    queryset = BeneficiaryUserInformation.objects.all()
    serializer_class = BeneficiaryInformationSerializer


class BeneficiaryInformationSingleCreateView(generics.CreateAPIView):
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