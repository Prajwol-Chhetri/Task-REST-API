from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from authentication.serializers import UserSerializer


class RegisterUserView(generics.CreateAPIView):
    """Register a new user in the system"""
    serializer_class = UserSerializer
