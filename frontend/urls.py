from django.urls import path

from . import views

urlpatterns = [
    path('', views.app, name='app'),
    path('web/utils/get_user', views.get_user, name='get_user'),
    path('web/utils/checknumber/<str:phone>', views.checknumber, name='get_user'),
    path('pay/<str:order_id>', views.pay_debug, name='pay_debug'),
]
