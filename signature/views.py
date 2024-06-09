from .serializers import SignatureSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, timedelta
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import status
from .models import Signature
import base64
import uuid
import json


# def drawing_view(request, unique_id):
#     signature = get_object_or_404(Signature, unique_id=unique_id)
#     if now() > signature.created_at + timedelta(weeks=1):
#         return HttpResponse("Ссылка больше не активна.", status=403)


#     return render(request, 'drawing.html', {
#         'signature': signature,
#         'title': signature.title
#     })

@api_view(['GET'])
def sing_api_view(request, unique_id):
    try:
        signature = Signature.objects.get(unique_id=unique_id)
        if signature.signed:
            return Response({'message': 'Вы уже отправили свою подпись!'}, status=status.HTTP_403_FORBIDDEN)

        if now() > signature.created_at + timedelta(weeks=1):
            return Response({'message': 'Ссылка больше не активна!'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SignatureSerializer(signature)
        return Response(serializer.data)

    except Signature.DoesNotExist:
        return Response({'error': 'Ссылка не найдена!'}, status=status.HTTP_404_NOT_FOUND)


# @csrf_exempt
# def save_signature(request, signature_id):
#     if request.method == 'POST':

#         data = json.loads(request.body)
#         image_data = data['image']

#         format, imgstr = image_data.split(';base64,')
#         ext = format.split('/')[-1]
#         image_file = ContentFile(base64.b64decode(imgstr), name=f"client_{uuid.uuid4()}.{ext}")

#         signature = Signature.objects.get(id=signature_id)
#         if signature.signed:
#             print(f"Signature {signature_id} is not active.")  # Debug print
#             return JsonResponse({'message': 'Ссылка больше не активна!'}, status=403)

#         signature.signed =True
#         signature.signature_date = now()
#         signature.image.save(image_file.name, image_file)
#         signature.save()

#         return JsonResponse({'message': 'Подпись успешно отправлена!'})
#     else:
#         return JsonResponse({'message': 'Method not allowed'}, status=405)


@api_view(['POST'])
def save_signature(request, signature_id):
    try:
        signature = Signature.objects.get(id=signature_id)
        if signature.signed:
            return Response({'message': 'Вы уже отправили свою подпись!'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        image_data = data('image')

        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f"client_{uuid.uuid4()}.{ext}")

        signature.image.save(image_file.name, image_file)
        signature.signed = True
        signature.signature_date = now()
        signature.save()
        return Response({'message': 'Подпись успешно отправлена!'}, status=status.HTTP_200_OK)

    except Signature.DoesNotExist:
        return Response({'error': 'Signature not found'}, status=status.HTTP_404_NOT_FOUND)

    except KeyError:
        return Response({'error': 'Incorrect data format'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': 'Server error: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
