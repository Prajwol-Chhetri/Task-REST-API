# from django.http import response
from rest_framework import generics
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

from authentication.serializers import UserSerializer


class RegisterUserView(generics.CreateAPIView):
    """Register a new user in the system"""
    serializer_class = UserSerializer


# class HelloView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         content = {'message': 'Hello World'}
#         return Response(content)