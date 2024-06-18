from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.utils.timezone import now, timedelta
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SignatureSerializer
from rest_framework import status
from django.urls import reverse
from .models import Signature, Client
from django.core.files.storage import default_storage
from django.http import FileResponse
from rest_framework import status
import base64


class SignatureCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
            signature = Signature.objects.filter(client=client).first()  # Получаем первый договор
            if signature:
                serializer = SignatureSerializer(signature)
                file_url = request.build_absolute_uri(signature.file.url) if signature.file else None
                return Response({
                    'signature_id': signature.id,
                    'client_id': signature.client.id,
                    'file': file_url,
                    'created_at': signature.created_at,
                    'signed': signature.signed,
                    'signature_date': signature.signature_date,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'signature_id': None,
                    'client_id': client_id,
                    'file': None,
                    'created_at': None,
                    'signed': None,
                    'signature_date': None,
                }, status=status.HTTP_404_NOT_FOUND)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден!'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
            existing_signature = Signature.objects.filter(client=client).first()
            if existing_signature:
                serializer = SignatureSerializer(existing_signature)
                return Response({
                    'message': 'Договор уже существует',
                    'signature_id': signature.id,
                    'client_id': signature.client.id,
                    'file': file_url,
                    'created_at': signature.created_at,
                    'signed': signature.signed,
                    'signature_date': signature.signature_date,
                }, status=status.HTTP_200_OK)

            data = request.data.copy()
            data['client'] = client_id
            serializer = SignatureSerializer(data=data, context={'request': request})

            if serializer.is_valid():
                signature = serializer.save()
                file_url = request.build_absolute_uri(signature.file.url) if signature.file else None
                return Response({
                    'message': 'Договор успешно создан!',
                    'signature_id': signature.id,
                    'client_id': signature.client.id,
                    'file': file_url,
                    'created_at': signature.created_at,
                    'signed': signature.signed,
                    'signature_date': signature.signature_date,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SignatureDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, client_id, signature_id):
        try:

            signature = Signature.objects.get(id=signature_id, client__id=client_id)
            file_url = request.build_absolute_uri(signature.file.url) if signature.file else None
            image_url = request.build_absolute_uri(signature.sign_image.url) if signature.signed and signature.sign_image else None
            data = {
                'signature_id': signature.id,
                'client_id': signature.client.id,
                'file': file_url,
                'created_at': signature.created_at,
                'signed': signature.signed,
                'signature_date': signature.signature_date,
                'image_url': image_url,
            }
            if now() > signature.created_at + timedelta(weeks=1):
                data['message'] = 'Срок действия договора для подписания истек!'
                return Response(data, status=status.HTTP_403_FORBIDDEN)

            if signature.signed:
                return Response(data, status=status.HTTP_200_OK)
            else:
                data['message'] = 'Клиент еще не поставил подпись!'
                return Response(data, status=status.HTTP_200_OK)

        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)


    def put(self, request, client_id, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id, client_id=client_id)
            serializer = SignatureSerializer(signature, data=request.data, partial=True)
            if serializer.is_valid():
                if 'file' in request.FILES:

                    if signature.file:

                        file_path = signature.file.path
                        if default_storage.exists(file_path):
                            default_storage.delete(file_path)

                serializer.save()
                file_url = request.build_absolute_uri(signature.file.url) if signature.file else None
                image_url = request.build_absolute_uri(signature.sign_image.url) if signature.signed and signature.sign_image else None
                return Response({
                    'message': 'Договор успешно обновлен!',
                    'signature_id': signature.id,
                    'client_id': signature.client.id,
                    'file': file_url,
                    'created_at': signature.created_at,
                    'signed': signature.signed,
                    'signature_date': signature.signature_date,
                    'image_url': image_url,
                    }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден!'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, client_id, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id, client_id=client_id)

            if signature.file:
                file_path = signature.file.path
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)

            if signature.sign_image:
                sign_image_path = signature.sign_image.path
                if default_storage.exists(sign_image_path):
                    default_storage.delete(sign_image_path)

            signature.delete()
            return Response({'message': 'Договор удален!'}, status=status.HTTP_204_NO_CONTENT)
        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)



class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

class ClientSignatureView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [AllowAny]

    def get(self, request, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id)
            # file_url = request.build_absolute_uri(signature.file.url) if signature.file else None
            # image_url = request.build_absolute_uri(signature.sign_image.url) if signature.signed and signature.sign_image else None

            serializer = SignatureSerializer(signature, context={'request': request})
            data = serializer.data

            if now() > signature.created_at + timedelta(weeks=1):
                return Response({'message': 'Срок действия договора для подписания истек!'}, status=status.HTTP_403_FORBIDDEN)

            if signature.signed:
                return Response({
                    'file':  data.get('file_url'),
                    'image_url': data.get('sign_image_url'),
                    'dowload_file': data.get('file_url'),
                    'message': 'Вы уже поставили свою подпись!'
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    'file': data.get('file_url'),
                    'message': 'Пожалуйста, ознакомтесь с условиями договора и поставьте свою подпись!'
                }, status=status.HTTP_200_OK)

        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id)
            # file_url = request.build_absolute_uri(signature.file.url) if signature.file else None
            # image_url = request.build_absolute_uri(signature.sign_image.url) if signature.signed and signature.sign_image else None

            serializer = SignatureSerializer(signature, context={'request': request})
            data = serializer.data

            if now() > signature.created_at + timedelta(weeks=1):
                return Response({'message': 'Срок действия договора для подписания истек!'}, status=status.HTTP_403_FORBIDDEN)

            if signature.signed:
                return Response({
                    'file':  data.get('file_url'),
                    'image_url': data.get('sign_image_url'),
                    'dowload_file': data.get('file_url'),
                    'message': 'Вы уже поставили свою подпись!'
                }, status=status.HTTP_403_FORBIDDEN)


            image_file = request.FILES.get('sign_image')
            if not image_file:
                return Response({'error': 'Файл изображения не предоставлен'}, status=status.HTTP_400_BAD_REQUEST)


            signature.sign_image = image_file
            signature.signed = True
            signature.signature_date = now()
            signature.save()

            return Response({'message': 'Подпись успешно отправлена!'}, status=status.HTTP_200_OK)

        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





    # def post(self, request, signature_id):
    #     try:
    #         signature = Signature.objects.get(id=signature_id)
    #         if signature.signed:
    #             return Response({'message': 'Вы уже отправили свою подпись!'}, status=status.HTTP_403_FORBIDDEN)

    #         image_file = request.FILES.get('sign_image')
    #         if image_file:
    #             # Обработка загруженного файла
    #             signature.sign_image.save(f"signature_{signature_id}.png", image_file)
    #         else:
    #             # Обработка строки base64
    #             image_data = request.data.get('sign_image')
    #             if not image_data:
    #                 return Response({'error': 'Отсутствуют данные изображения'}, status=status.HTTP_400_BAD_REQUEST)
    #             format, imgstr = image_data.split(';base64,')
    #             image = base64.b64decode(imgstr)
    #             signature.sign_image.save(f"signature_{signature_id}.png", ContentFile(image))

    #         signature.signed = True
    #         signature.signature_date = now()
    #         signature.save()
    #         return Response({'message': 'Подпись успешно отправлена!'}, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




    # def post(self, request, signature_id):
    #     try:
    #         signature = Signature.objects.get(id=signature_id)
    #         if now() > signature.created_at + timedelta(weeks=1):
    #             return Response({'message': 'Срок действия для подписания договора истек!'}, status=status.HTTP_403_FORBIDDEN)

    #         if signature.signed:
    #             return Response({'message': 'Вы уже отправили свою подпись!'}, status=status.HTTP_403_FORBIDDEN)

    #         image_data = request.data.get('sign_image')
    #         if not image_data:
    #             return Response({'error': 'Отсутствуют данные изображения'}, status=status.HTTP_400_BAD_REQUEST)

    #         try:
    #             format, imgstr = image_data.split(';base64,')
    #             ext = format.split('/')[-1]
    #         except ValueError:
    #             return Response({'error': 'Некорректные данные изображения'}, status=status.HTTP_400_BAD_REQUEST)

    #         try:
    #             image_file = ContentFile(base64.b64decode(imgstr), name=f"signature_{signature_id}.{ext}")
    #         except TypeError:
    #             return Response({'error': 'Ошибка при декодировании изображения'}, status=status.HTTP_400_BAD_REQUEST)

    #         signature.sign_image.save(image_file.name, image_file)
    #         signature.signed = True
    #         signature.signature_date = now()
    #         signature.save()

    #         return Response({'message': 'Подпись успешно отправлена!'}, status=status.HTTP_200_OK)

    #     except Signature.DoesNotExist:
    #         return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
