from django.shortcuts import redirect
from django.urls import path, reverse
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('<slug:game_url>', views.game, name='game'),
    path('files/<slug:game_url>/<path:file_url>', views.game_file, name='game-file'),
]
