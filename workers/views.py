from .serializers import ( ClientSerializer, DocumentSerializer, PaymentSerializer, RefundSerializer,
                        MultipleDocumentsSerializer, DocumentFileSerializer)
from rest_framework.generics import  CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .authentication import CsrfExemptSessionAuthentication
from rest_framework.pagination import PageNumberPagination
from .models import Client, Document, Payment, Refund
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .filters import ClientFilter
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
            'results': data
        })

# GET
class ClientList(ListAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
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
            queryset = queryset.filter(firstName__icontains=country)

        return queryset


# POST
@method_decorator(csrf_exempt, name='dispatch' )
class ClientCreate(CreateAPIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication,)
    queryset = Client.objects.all()
    serializer_class = ClientSerializer



# GET / UPDATE / DELETE
class ClientDetail(RetrieveUpdateDestroyAPIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'




# class DocumentViewSet(viewsets.ModelViewSet):
#     # authentication_classes = [SessionAuthentication, BasicAuthentication]
#     # permission_classes = [IsAuthenticated]
#     serializer_class = DocumentSerializer

#     def get_queryset(self):
#         client_id = self.kwargs['client_id']
#         return Document.objects.filter(client__id=client_id).order_by('id')


#     @action(detail=False, methods=['post'], url_path='upload_documents', parser_classes=[MultiPartParser])
#     def upload_documents(self, request, *args, **kwargs):
#         client_id = self.kwargs['client_id']
#         title = request.data.get('title', 'Default Title')
#         uploaded_at = request.data.get('uploaded_at', timezone.now())


#         context = self.get_serializer_context()
#         context.update({'client_id': client_id, 'title': title, 'uploaded_at': uploaded_at})


#         serializer = MultipleDocumentsSerializer(data=request.data, context=context)
#         if serializer.is_valid():
#             doc_group = serializer.save()
#             response_serializer = DocumentSerializer(doc_group)
#             return Response(response_serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=True, methods=['post'], url_path='edit_documents')
#     def edit_documents(self, request, pk=None, *args, **kwargs):
#         try:
#             doc_group = Document.objects.get(pk=pk, is_group=True)  # Убедитесь, что это группа
#         except Document.DoesNotExist:
#             return Response({'error': 'Document group not found'}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data
#         if 'title' in data:
#             doc_group.title = data['title']
#             doc_group.save()

#         with transaction.atomic():
#             delete_uuids = data.get('delete_ids', [])
#             if delete_uuids:
#                 Document.objects.filter(uuid__in=delete_uuids, is_group=False).delete()

#             updated_documents = data.get('updated_documents', [])
#             for doc_data in updated_documents:
#                 doc_uuid = doc_data.get('uuid')
#                 document = Document.objects.get(uuid=doc_uuid, is_group=False)
#                 serializer = DocumentFileSerializer(document, data=doc_data, partial=True)
#                 if serializer.is_valid():
#                     serializer.save()

#             new_documents = data.get('new_documents', [])
#             for new_doc in new_documents:
#                 new_doc['client'] = doc_group.client.id
#                 new_doc['is_group'] = False
#                 serializer = DocumentFileSerializer(data=new_doc)
#                 if serializer.is_valid():
#                     serializer.save()

#         return Response({'message': 'Document group updated successfully'}, status=status.HTTP_200_OK)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=False, methods=['post'], url_path='upload_documents', parser_classes=[MultiPartParser])
    def upload_documents(self, request, *args, **kwargs):
        title = request.data.get('title', 'Default Title')
        uploaded_at = request.data.get('uploaded_at', timezone.now())
        client = Client.objects.get(id=request.data['client_id'])  # Адаптируйте получение клиента по необходимости

        # Создаем документ
        document = Document.objects.create(client=client, title=title, uploaded_at=uploaded_at)

        # Создаем файлы для документа
        files_serializer = DocumentFileSerializer(data=[{'file': file} for file in request.FILES.getlist('documents')], many=True)
        if files_serializer.is_valid():
            files_serializer.save(document=document)
        else:
            return Response(files_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)


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
