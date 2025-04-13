from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import CharityRegistrationSerializer

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