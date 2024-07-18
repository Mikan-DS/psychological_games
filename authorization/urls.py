from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login_view'),
    path('login/<str:user_id>/<str:code>/', views.login_with_code, name='login_with_code'),
    path('register/', views.register, name='register'),
]

