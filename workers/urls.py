from .views import DocumentViewSet, PaymentViewSet, RefundViewSet, ClientCreate, ClientList, ClientDetail
from django.urls import path, include
from signature.views import SignatureCreate, SignatureDetailView


documents_list = DocumentViewSet.as_view({
    'get': 'list',
})

documents_detail = DocumentViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

payments_list = PaymentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

payments_detail = PaymentViewSet.as_view({
    'get': 'retrieve',
    'post': 'update',
    'delete': 'destroy'
})

refunds_list = RefundViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

refunds_detail = RefundViewSet.as_view({
    'get': 'retrieve',
    'post': 'update',
    'delete': 'destroy'
})



urlpatterns = [
    path('main/', ClientList.as_view(), name='main-page'),
    path('client_add/', ClientCreate.as_view(), name='client-add'),
    path('client/<int:id>/', ClientDetail.as_view(), name='client-detail'),
    path('client/<int:client_id>/documents/', documents_list, name='client-documents-list'),
    path('client/<int:client_id>/documents/signature/', SignatureCreate.as_view(), name='signature-create'),
    path('client/<int:client_id>/documents/signature/<int:signature_id>/', SignatureDetailView.as_view(), name='signature-detail'),
    path('client/<int:client_id>/documents/upload/', DocumentViewSet.as_view({'post': 'upload_documents'}), name='upload_documents'),
    path('client/<int:client_id>/documents/<int:pk>/', documents_detail, name='client-document-detail'),
    path('client/<int:client_id>/documents/<int:pk>/update/', DocumentViewSet.as_view({'post': 'update_documents'}), name='update_documents'),
    path('client/<int:client_id>/documents/<int:pk>/files/<int:file_id>/download/', DocumentViewSet.as_view({'get': 'download_file'}), name='download_file'),
    path('client/<int:client_id>/payments/', payments_list, name='client-payment-list'),
    path('client/<int:client_id>/payments/<int:pk>/', payments_detail, name='client-payment-detail'),
    path('client/<int:client_id>/refunds/', refunds_list, name='client-refund-list'),
    path('client/<int:client_id>/refunds/<int:pk>/', refunds_detail, name='client-refund-detail'),
]
