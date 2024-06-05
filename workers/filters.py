from django.db.models import Q
from .models import Client
import django_filters


class ClientFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains', required=False)
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains', required=False)
    name = django_filters.CharFilter(method='filter_by_name', required=False)

    class Meta:
        model = Client
        fields = ['status', 'country', 'name']

    def filter_by_name(self, queryset, name, value):
        if not value:
            return queryset

        filtered_queryset = queryset.filter(
            Q(firstName__istartswith=value) | Q(currentLastName__istartswith=value)
        )

        if not filtered_queryset.exists() and value:
            value_with_capital = value.capitalize()
            filtered_queryset = queryset.filter(
                Q(firstName__istartswith=value_with_capital) | Q(currentLastName__istartswith=value_with_capital)
            )

        return filtered_queryset
