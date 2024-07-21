"""
URL configuration for psychological_games project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = ([
    path('', include('frontend.urls')),
    path('admin/', admin.site.urls),
    path('vk_callback/', include('vkapi.urls')),
    path('auth/', include('authorization.urls')),
    path('games/', include('games.urls')),
    path('bild190cjvveb', RedirectView.as_view(url="/games/bild190cjvveb")),
    path('Cooljungle-1.60-web', RedirectView.as_view(url="/games/cooljungle-160-web")),
    path('cooljungle160gp', RedirectView.as_view(url="/games/cooljungle-160-gp")),
    path('test3archetypes2', RedirectView.as_view(url="/games/test3archetypes2")),
    path('tik/posobie-android', RedirectView.as_view(url="/games/posobie-android")),
    path('tik/posobie-pk', RedirectView.as_view(url="/games/posobie-pk")),
    path('tik/relax', RedirectView.as_view(url="/games/relax")),
    path('tik/situations1', RedirectView.as_view(url="/games/situations1")),
    path('tik/situations2', RedirectView.as_view(url="/games/situations2")),
])

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
