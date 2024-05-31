import django_filters
from .models import Client

class ClientFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains', required=False)
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains', required=False)
    firstName = django_filters.CharFilter(field_name='firstName', lookup_expr='icontains', required=False)

    class Meta:
        model = Client
        fields = ['status', 'country', 'firstName']
