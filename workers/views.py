from .serializers import ( ClientSerializer, DocumentSerializer, PaymentSerializer,
                          RefundSerializer, ClientListSerializer, PartnerClassSerializer )
from rest_framework.generics import  CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.authentication import TokenAuthentication
from .models import Client, Document, Payment, Refund, DocumentFile, PartnerClass, PaymentFile, RefundFile
from django_filters.rest_framework import DjangoFilterBackend
from .authentication import CsrfExemptSessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .filters import ClientFilter
from rest_framework import status
from django.http import FileResponse, Http404



class PartnersList(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PartnerClass.objects.all()
    serializer_class = PartnerClassSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        count = self.get_queryset().count()
        return Response({
            'count_partners': count,
            'results': response.data
        })


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'count_clients': self.page.paginator.count,
            'count_pages': total_pages,
            'results': data

        })

# GET
class ClientList(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientListSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClientFilter
    ordering_fields = ['uploaded_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', None)
        if ordering == 'old':
            queryset = queryset.order_by('uploaded_at')
        elif ordering == 'new':
            queryset = queryset.order_by('-uploaded_at')
        else:
            queryset = queryset.order_by('-uploaded_at')
        return queryset


# POST

class ClientCreate(CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'message': 'Анкета клиента успешно добавлена!',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось добавить анкету клиента!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)


# GET / UPDATE / DELETE
class ClientDetail(RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'


    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'message': 'Анкета клиента успешно обновлена!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось обновить анкету клиента!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)



    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response({
                'message': 'Анкета клиент успешно удалена!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось удалить анкету клиента!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)



class StandartSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20

    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'count_documents': self.page.paginator.count,
            'count_pages': total_pages,
            'results': data
        })


class DocumentViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    pagination_class = StandartSetPagination

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Document.objects.filter(client__id=client_id).order_by('id')


    @action(detail=False, methods=['post'], url_path='upload_documents')
    def upload_documents(self, request, client_id=None):
        client = Client.objects.get(id=client_id)
        serializer = DocumentSerializer(data=request.data, context={'client_id': client.id})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Документ успешно добавлен!','data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response({'message': 'Не удалось добавить документ!','data': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response({
                'message': 'Документ успешно удален!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось удалить документ!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'], url_path='update_documents')
    def update_documents(self, request, client_id=None, pk=None):
        instance = self.get_object()
        serializer = DocumentSerializer(instance, data=request.data, partial=True, context={'client_id': instance.client.id})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Документ успешно обновлен!', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        return Response({'message': 'Не удалось обновить документ!', 'data': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)



    @action(detail=True, methods=['get'], url_path='files/(?P<file_id>\d+)/download')
    def download_file_two(self, request, client_id=None, pk=None, file_id=None):
        try:
            document = self.get_object()
            file_instance = document.files.get(id=file_id)

            response = FileResponse(file_instance.file.open(), as_attachment=True, filename=file_instance.file.name)
            return response

        except DocumentFile.DoesNotExist:
            raise Http404("Файл не был найден")

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='files/(?P<file_id>\d+)/download')
    def download_file(self, request, client_id=None, pk=None, file_id=None):
        try:
            document = self.get_object()
            file_instance = document.files.get(id=file_id)
            file_url = request.build_absolute_uri(file_instance.file.url)

            response = FileResponse(file_instance.file.open('rb'), as_attachment=True, filename=file_instance.file.name)


            return Response({
                'message': 'Файл успешно найден!',
                'file_url': file_url
            })

        except DocumentFile.DoesNotExist:
            raise Http404("Файл не был найден")


class PaymentViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Payment.objects.filter(client__id=client_id).order_by('id')

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        serializer.save(client_id=client_id)

    @action(detail=True, methods=['get'], url_path='files/(?P<file_id>\d+)/download')
    def download_file(self, request, client_id=None, pk=None, file_id=None):
        try:
            payment = self.get_object()
            file_instance = payment.files.get(id=file_id)

            response = FileResponse(file_instance.file.open(), as_attachment=True, filename=file_instance.file.name)
            return response

        except PaymentFile.DoesNotExist:
            raise Http404("File not found")

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'message': 'Оплата успешно добавлена!',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось добавить оплату!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'message': 'Оплата успешно обновлена!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось обновить оплату!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response({
                'message': 'Оплата успешно удалена!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось удалить оплату!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)



class RefundViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Refund.objects.filter(client__id=client_id).order_by('id')

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        serializer.save(client_id=client_id)


    @action(detail=True, methods=['get'], url_path='files/(?P<file_id>\d+)/download')
    def download_file(self, request, client_id=None, pk=None, file_id=None):
        try:
            refund = self.get_object()
            file_instance = refund.files.get(id=file_id)

            response = FileResponse(file_instance.file.open(), as_attachment=True, filename=file_instance.file.name)
            return response

        except RefundFile.DoesNotExist:
            raise Http404("File not found")

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'message': 'Возврат успешно добавлен!',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось добавить возврат!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'message': 'Возврат успешно обновлен!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось обновить возврат!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            return Response({
                'message': 'Возврат успешно удален!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось удалить возврат!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
