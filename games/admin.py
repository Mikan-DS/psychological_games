from django.contrib import admin

from games.models import PostGame


@admin.register(PostGame)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'folder', 'url')
    search_fields = ('title',)
    list_filter = ('title',)
