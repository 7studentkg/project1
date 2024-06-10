from django.contrib import admin
from .models import Signature
from django.utils.html import format_html
from django.utils.timezone import now, timedelta

@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ['client', 'created_at', 'signature_link', 'signature_date', 'signed_status']
    list_filter = ['created_at', 'signed']
    search_fields = ['client__name']
    fields = ['client', 'title', 'sign_image']

    def signature_link(self, obj):
        try:
            link = obj.get_absolute_url()
        except AttributeError:
            return "No URL method defined"

        active = now() <= obj.created_at + timedelta(weeks=1)
        color = '#00FF00' if active else 'red'
        font_weight = 'bold'
        return format_html('<a href="{}" target="_blank" style="color: {}; font-weight: {};">View/Sign Document</a>', link, color, font_weight)

    signature_link.short_description = 'Signature Link'

    def signed_status(self, obj):
        color = '#00FF00' if obj.signed else 'red'
        font_weight = 'bold'
        status_text = "Signed" if obj.signed else "Not Signed"
        return format_html('<span style="color: {}; font-weight: {};">{}</span>', color, font_weight, status_text)

    signed_status.short_description = 'Signed Status'
