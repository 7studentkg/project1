from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .serializer import LoginSerializer
from rest_framework.authtoken.models import Token

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({"token": token.key, "message": "Успешный вход в систему"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Неправильные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
