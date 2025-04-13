from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .serializers import CharityRegistrationSerializer, CharityLoginSerializer

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