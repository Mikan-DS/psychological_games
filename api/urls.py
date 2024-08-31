from django.urls import path

from . import views

urlpatterns = [
    path('add-result', views.add_result, name='add_result'),
]
