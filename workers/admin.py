from django.contrib import admin
from .models import Client, Document, DocumentFile, Payment, Refund, Contact, Mother, Father, Child
from django.db.models import Sum

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

class ClientAdmin(admin.ModelAdmin):
    inlines = [
        DocumentInline, PaymentInline, RefundInline,
        MotherInline, FatherInline, ContactInline, ChildInline
    ]
    list_display = [ '__str__', 'total_payments', 'total_refunds', 'documents_count_admin', 'children_count_admin', 'id']

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

# class DocumentAdmin(admin.ModelAdmin):
#     inlines = [DocumentFileInline]
#     list_display = ['id', 'title', 'client', 'uploaded_at']

# admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentFile, DocumentFileAdmin)

# admin.site.register(Status)
# admin.site.register(Country)
