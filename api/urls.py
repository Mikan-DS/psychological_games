from django.urls import path

from . import views

urlpatterns = [
    path('add-result', views.add_result, name='add_result'),
    path('update-db', views.update_from_old_type_database, name='update_db')
]
