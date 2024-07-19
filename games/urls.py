from django.urls import path

from . import views

urlpatterns = [
    path('<slug:game_url>', views.game, name='game'),
]
