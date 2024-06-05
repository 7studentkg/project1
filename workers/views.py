from .serializers import ( ClientSerializer, DocumentSerializer, PaymentSerializer, RefundSerializer,)
from rest_framework.generics import  CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .authentication import CsrfExemptSessionAuthentication
from rest_framework.pagination import PageNumberPagination
from .models import Client, Document, Payment, Refund
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .filters import ClientFilter



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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
