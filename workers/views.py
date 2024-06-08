from .serializers import ClientSerializer, DocumentSerializer, PaymentSerializer, RefundSerializer, DocumentFileSerializer
from rest_framework.generics import  CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from .models import Client, Document, Payment, Refund, DocumentFile
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



class CustomPageNumberPagination(PageNumberPagination):
    page_size = 30 # Измените это значение по необходимости
    page_size_query_param = 'page_size'  # Разрешаем клиентам изменять размер страницы ?page_size=100
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data # page_count =
        })

# GET
class ClientList(ListAPIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Client.objects.all().order_by('-uploaded_at')
    serializer_class = ClientSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClientFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)
        country = self.request.query_params.get('country', None)
        firstName = self.request.query_params.get('firstName', None)

        if status:
            queryset = queryset.filter(status__icontains=status)
        if country:
            queryset = queryset.filter(country__icontains=country)
        if firstName:
            queryset = queryset.filter(firstName__icontains=firstName)

        return queryset


# POST
@method_decorator(csrf_exempt, name='dispatch' )
class ClientCreate(CreateAPIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication,)
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'message': 'Анкета успешно добавлена!',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось добавить анкету!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            return Response({
                'message': 'Анкета успешно обновлена!',
                'data': response.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'message': 'Не удалось обновить анкету!',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)



# GET / UPDATE / DELETE
class ClientDetail(RetrieveUpdateDestroyAPIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'





class DocumentViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

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


    @action(detail=True, methods=['get'], url_path='files/(?P<file_id>\d+)')
    def retrieve_file_info(self, request, client_id=None, pk=None, file_id=None):
        try:
            document = self.get_object()
            file_instance = document.files.get(id=file_id)
            serializer = DocumentFileSerializer(file_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DocumentFile.DoesNotExist:
            raise Http404("File does not exist")

    @action(detail=True, methods=['get'], url_path='files/(?P<file_id>\d+)/download')
    def download_file(self, request, client_id=None, pk=None, file_id=None):
        try:
            document = self.get_object()
            file_instance = document.files.get(id=file_id)
            file_path = file_instance.file.path
            response = HttpResponse(open(file_path, 'rb').read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_instance.file.name}"'
            return response
        except DocumentFile.DoesNotExist:
            raise Http404("File does not exist")


class PaymentViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Payment.objects.filter(client__id=client_id).order_by('id')


    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        serializer.save(client_id=client_id)

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



class RefundViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = RefundSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Refund.objects.filter(client__id=client_id).order_by('id')

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        serializer.save(client_id=client_id)

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
