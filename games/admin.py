from django.contrib import admin

from games.models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'archive')
    search_fields = ('title',)
    list_filter = ('title',)
