from django.urls import path

from . import views

urlpatterns = [
    path('', views.confirmation_token, name='confirmation_token'),
]
