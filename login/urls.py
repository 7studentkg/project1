from django.urls import path, include
from . import views



urlpatterns = [
    path('user/', views.LoginAPIView.as_view()),

]
#
