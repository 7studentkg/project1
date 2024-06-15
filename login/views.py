from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, TokenAuthentication, SessionAuthentication
from rest_framework.views import APIView
from .serializer import LoginSerializer
from rest_framework import status
from django.middleware.csrf import get_token




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
                csrf_token = get_token(request)
                return Response({
                            "message": "Успешный вход в систему",
                            "token": token.key,
                            "csrf_token": csrf_token
                            }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Неправильные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            token = Token.objects.get(user=request.user)
            token.delete()
            logout(request)

            response = Response({"message": "Успешный выход из системы"}, status=status.HTTP_200_OK)
            response.delete_cookie("csrftoken")

            return response
        except Token.DoesNotExist:
            return Response({"error": "Не получилось выйти!"}, status=status.HTTP_400_BAD_REQUEST)
