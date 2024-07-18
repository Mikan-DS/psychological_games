# admin.py
from django.contrib import admin
from .models import Settings, Purchase, ConsultationParameters


class SettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Settings, SettingsAdmin)


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('item_type', 'user', 'cost', 'paid')
    search_fields = ('item_type', 'user__username')
    list_filter = ('paid',)
    ordering = ('-id',)


class ConsultationParametersAdmin(admin.ModelAdmin):
    list_display = ('question', 'age', 'gender', 'contact_way', 'purchase')
    search_fields = ('question', 'age__value', 'contact_way__method', 'purchase__item_type')
    list_filter = ('gender', 'age', 'contact_way')
    ordering = ('-id',)


admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(ConsultationParameters, ConsultationParametersAdmin)
