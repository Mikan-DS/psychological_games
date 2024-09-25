# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Settings, Purchase, ConsultationParameters, User, Product


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email",)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ("username", "phone", "email", "is_staff",)
    list_filter = ("username", "phone", "email", "is_staff",)
    fieldsets = (
        (None, {"fields": ("username", "phone", "first_name", "last_name", "email", "password")}),
        ("Разрешения", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )
    search_fields = ("email", "username", "phone", "email")
    ordering = ("id",)


admin.site.register(User, CustomUserAdmin)


class SettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Settings, SettingsAdmin)


class ConsultationParametersInline(admin.TabularInline):
    model = ConsultationParameters
    extra = 0


class UserInline(admin.StackedInline):
    model = User


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'cost', 'paid')
    search_fields = ('item_type', 'user__username')
    list_filter = ('paid',)
    ordering = ('-id',)

    fieldsets = (
        (None, {"fields": ("product", "cost", "paid", "yookassa_order_id")}),
    )

    inlines = [ConsultationParametersInline, UserInline]

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


class ProductAdmin(admin.ModelAdmin):
    list_display = ('verbose', 'price',)
    search_fields = ('verbose',)
    ordering = ('price',)
    fieldsets = (
        (None, {"fields": ("price",)}),
    )


admin.site.register(Product, ProductAdmin)
