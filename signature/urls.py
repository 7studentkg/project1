from django.urls import path
from .views import ClientSignatureView


urlpatterns = [
    path('view/sign/document/<int:signature_id>/', ClientSignatureView.as_view(), name='client-signature'),
]
