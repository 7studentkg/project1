from django.contrib import admin
from .models import Client, Document, DocumentFile, Payment, Refund, Contact, Mother, Father, Child
from django.db.models import Sum
from django.db.models import Q
from signature.models import Signature

class DocumentFileInline(admin.TabularInline):
    model = DocumentFile
    extra = 1

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

class RefundInline(admin.TabularInline):
    model = Refund
    extra = 1

class MotherInline(admin.TabularInline):
    model = Mother
    extra = 0

class FatherInline(admin.TabularInline):
    model = Father
    extra = 0

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0

class ChildInline(admin.TabularInline):
    model = Child
    extra = 1



class SignatureInline(admin.TabularInline):
    model = Signature
    extra = 0
    exclude = ('last_accessed', 'signature_date', 'signed',)


class ClientAdmin(admin.ModelAdmin):
    inlines = [
        DocumentInline, PaymentInline, RefundInline,
        MotherInline, FatherInline, ContactInline, ChildInline, SignatureInline
    ]
    list_display = [ '__str__', 'total_payments', 'total_refunds', 'documents_count_admin', 'children_count_admin', 'id']
    search_fields = ['firstName', 'currentLastName']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            search_terms = search_term.split()
            queries = Q()
            for term in search_terms:
                queries |= Q(firstName__icontains=term) | Q(currentLastName__icontains=term)
            queryset = queryset.filter(queries)
        return queryset, use_distinct


    def documents_count_admin(self, obj):
        return obj.documents.count()
    documents_count_admin.short_description = 'Количество документов'

    def children_count_admin(self, obj):
        return obj.children.count()
    children_count_admin.short_description = 'Количество детей'

    def total_payments(self, obj):
        return obj.payment.aggregate(Sum('amount'))['amount__sum'] or 0
    total_payments.short_description = 'Сумма оплат'

    def total_refunds(self, obj):
        return obj.refund.aggregate(Sum('amount'))['amount__sum'] or 0
    total_refunds.short_description = 'Сумма возвратов'

admin.site.register(Client, ClientAdmin)


class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'file']

admin.site.register(DocumentFile, DocumentFileAdmin)

# admin.site.register(Status)
# admin.site.register(Country)
