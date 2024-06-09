from django.urls import path
from .views import save_signature, sing_api_view

urlpatterns = [
    path('save_signature/<int:signature_id>/', save_signature, name='save_signature'),
    path('view/sign/document/<uuid:unique_id>/', sing_api_view, name='sing_api_view'),
]
