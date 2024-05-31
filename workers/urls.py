from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, PaymentViewSet, RefundViewSet, ClientCreate


router = DefaultRouter()
router.register(r'client/(?P<client_id>\d+)/documents', DocumentViewSet, basename='client-documents')
router.register(r'client/(?P<client_id>\d+)/payments', PaymentViewSet, basename='client-payments')
router.register(r'client/(?P<client_id>\d+)/refunds', RefundViewSet, basename='client-refunds')

# refund_list = RefundViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })

# refund_detail = RefundViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'delete': 'destroy'
# })


urlpatterns = [
    path('', include(router.urls),  name='main_page'),
    path('main/', views.ClientList.as_view()),
    path('client_add/', ClientCreate.as_view(), name='client-add'),
    path('client/<int:id>/', views.ClientDetail.as_view()),
    # path('client/<int:client_id>/refunds/', refund_list, name='client-refund-list'),
    # path('client/<int:client_id>/refunds/<int:pk>/', refund_detail, name='client-refund-detail'),

]
