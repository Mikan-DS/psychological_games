# admin.py
from django.contrib import admin

from .models import Settings, Purchase, ConsultationParameters


class SettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Settings, SettingsAdmin)

class ConsultationParametersInline(admin.TabularInline):
    model = ConsultationParameters
    extra = 1

class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_type', 'cost', 'paid')
    search_fields = ('item_type', 'user__username')
    list_filter = ('paid',)
    ordering = ('-id',)

    inlines = [ConsultationParametersInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.item_type == 'game_consultation' and not ConsultationParameters.objects.filter(purchase=obj):
            ConsultationParameters.objects.create(purchase=obj, age_id=1, contact_way_id=1)
        else:
            ConsultationParameters.objects.filter(purchase=obj).delete()


class ConsultationParametersAdmin(admin.ModelAdmin):
    list_display = ('question', 'age', 'gender', 'contact_way', 'purchase')
    search_fields = ('question', 'age__value', 'contact_way__method', 'purchase__item_type')
    list_filter = ('gender', 'age', 'contact_way')
    ordering = ('-id',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(purchase__item_type='game_consultation')

admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(ConsultationParameters, ConsultationParametersAdmin)

