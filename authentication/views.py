from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from authentication.serializers import UserSerializer


class RegisterUserView(generics.CreateAPIView):
    """Register a new user in the system"""
    serializer_class = UserSerializer


class UpdateUserView(generics.RetrieveUpdateAPIView):
    """Update the details of user in the system"""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Retreive and return authenticated user"""
        return self.request.user
