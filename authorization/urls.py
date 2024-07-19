from django.urls import path

from . import views

urlpatterns = [
    # path('login/', views.login_view, name='login_view'),
    # path('login/<str:user_id>/<str:code>/', views.login_with_code, name='login_with_code'),
    # path('register/', views.register, name='register'),
    path('logout', views.logoutView, name='logout'),
    path('pay/init', views.pay_init, name='pay_init'),
    path('login/init/<str:phone>', views.login_init, name='login_init'),
]

