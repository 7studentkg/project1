from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Client, Document, Payment, Refund
from rest_framework.generics import  CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from .serializers import ClientSerializer, DocumentSerializer, PaymentSerializer, RefundSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .authentication import CsrfExemptSessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ClientFilter


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 2 # Измените это значение по необходимости
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





# import logging

# logger = logging.getLogger(__name__)



# class SearchClientByCountryView(ListAPIView):
#     queryset = Client.objects.all()
#     serializer_class = ClientSerializer
#     pagination_class = LargePagePagination
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = ClientFilteCountry



# class SearchClientByStatusView(ListAPIView):
#     queryset = Client.objects.all()
#     serializer_class = ClientSerializer
#     pagination_class = LargePagePagination
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = ClientFilteStatus


# POST
@method_decorator(csrf_exempt, name='dispatch' )
class ClientCreate(CreateAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    queryset = Client.objects.all()
    serializer_class = ClientSerializer



# GET / UPDATE / DELETE
class ClientDetail(RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'id'


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Document.objects.filter(client__id=client_id).order_by('id')

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        serializer.save(client_id=client_id)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Payment.objects.filter(client__id=client_id).order_by('id')


    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        serializer.save(client_id=client_id)


class RefundViewSet(viewsets.ModelViewSet):
    serializer_class = RefundSerializer

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Refund.objects.filter(client__id=client_id).order_by('id')

    def perform_create(self, serializer):
        client_id = self.kwargs['client_id']
        serializer.save(client_id=client_id)


class ClientSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if query:
            clients = Client.objects.filter(
                Q(surname__istartswith=query) | Q(firstname__istartswith=query)
            )
        else:
            clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)
