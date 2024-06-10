from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from django.utils.timezone import now, timedelta
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.urls import reverse
from .models import Signature, Client
import base64


class SignatureCreate(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        client_id = request.data.get('client_id')
        title = request.data.get('title')
        try:
            client = Client.objects.get(id=client_id)
            signature = Signature.objects.create(client=client, title=title)
            return Response({
                'message': 'Договор успешно создан!',
                'signature_id': signature.id,
                'title': signature.title,
                'client_id': signature.client.id
            }, status=status.HTTP_201_CREATED)
        except Client.DoesNotExist:
            return Response({'error': 'Клиент не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignatureDetailView(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]


    def get(self, request, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id)
            data = {
                'title': signature.title,
                'client_id': signature.client.id,
                'signed': signature.signed,
                'signature_date': signature.signature_date,
                'image_url': signature.sign_image.url if signature.signed else None
            }
            if now() > signature.created_at + timedelta(weeks=1):
                return Response({'message': 'Срок действия для подписания договора истек!'}, status=status.HTTP_403_FORBIDDEN)

            if signature.signed:
                return Response(data, status=status.HTTP_200_OK)

            else:
                data['message'] = 'Клиент еще не поставил подпись!'
                return Response(data, status=status.HTTP_200_OK)

        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id)
            signature.title = request.data.get('title', signature.title)
            signature.save()
            return Response({'message': 'Договор обновлен'}, status=status.HTTP_200_OK)
        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id)
            signature.delete()
            return Response({'message': 'Договор удален'}, status=status.HTTP_204_NO_CONTENT)
        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Bypass CSRF check

class ClientSignatureView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [AllowAny]

    def get(self, request, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id)

            if now() > signature.created_at + timedelta(weeks=1):
                return Response({'message': 'Срок действия для подписания договора истек!'}, status=status.HTTP_403_FORBIDDEN)

            if signature.signed:
                return Response({
                    'title': signature.title,
                    'image_url': signature.sign_image.url,
                    'message': 'Вы уже поставили свою подпись!'
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    'title': signature.title,
                    'message': 'Пожалуйста, ознакомтесь с условиями договора и поставьте свою подпись!'
                }, status=status.HTTP_200_OK)

        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, signature_id):
        try:
            signature = Signature.objects.get(id=signature_id)

            if now() > signature.created_at + timedelta(weeks=1):
                return Response({'message': 'Срок действия для подписания договора истек!'}, status=status.HTTP_403_FORBIDDEN)

            if signature.signed:
                return Response({'message': 'Вы уже отправили свою подпись!'}, status=status.HTTP_403_FORBIDDEN)

            image_data = request.data.get('sign_image')
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            image_file = ContentFile(base64.b64decode(imgstr), name=f"signature_{signature_id}.{ext}")

            signature.sign_image.save(image_file.name, image_file)
            signature.signed = True
            signature.signature_date = now()
            signature.save()

            return Response({'message': 'Подпись успешно отправлена!'}, status=status.HTTP_200_OK)

        except Signature.DoesNotExist:
            return Response({'error': 'Договор не найден'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': 'Ошибка сервера: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['GET'])
# def sing_api_view(request, unique_id):
#     try:
#         signature = Signature.objects.get(unique_id=unique_id)
#         if signature.signed:
#             return Response({'message': 'Вы уже отправили свою подпись!'}, status=status.HTTP_403_FORBIDDEN)

#         if now() > signature.created_at + timedelta(weeks=1):
#             return Response({'message': 'Ссылка больше не активна!'}, status=status.HTTP_403_FORBIDDEN)

#         serializer = SignatureSerializer(signature)
#         return Response(serializer.data)

#     except Signature.DoesNotExist:
#         return Response({'error': 'Ссылка не найдена!'}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['POST'])
# def save_signature(request, signature_id):
#     try:
#         signature = Signature.objects.get(id=signature_id)
#         if signature.signed:
#             return Response({'message': 'Вы уже отправили свою подпись!'}, status=status.HTTP_403_FORBIDDEN)

#         data = request.data
#         image_data = data('image')

#         format, imgstr = image_data.split(';base64,')
#         ext = format.split('/')[-1]
#         image_file = ContentFile(base64.b64decode(imgstr), name=f"client_{uuid.uuid4()}.{ext}")

#         signature.image.save(image_file.name, image_file)
#         signature.signed = True
#         signature.signature_date = now()
#         signature.save()
#         return Response({'message': 'Подпись успешно отправлена!'}, status=status.HTTP_200_OK)

#     except Signature.DoesNotExist:
#         return Response({'error': 'Signature not found'}, status=status.HTTP_404_NOT_FOUND)

#     except KeyError:
#         return Response({'error': 'Incorrect data format'}, status=status.HTTP_400_BAD_REQUEST)

#     except Exception as e:
#         return Response({'error': 'Server error: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
