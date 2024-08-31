from django.contrib import admin
from django.forms import inlineformset_factory
from django.urls import reverse
from django.utils.html import format_html

from .models import ProjectSummary, ProjectParameter, TestResult, TestResultParameter


class ProjectParameterInline(admin.TabularInline):
    model = ProjectParameter
    extra = 1


class TestResultInline(admin.TabularInline):
    model = TestResult
    extra = 1
    fields = ['name', 'ip', 'end_time', 'duration', 'view_test_result']
    readonly_fields = ['view_test_result']

    def view_test_result(self, instance):
        if instance.id:
            url = reverse('admin:api_testresult_change', args=[instance.id])
            return format_html('<a href="{}">Просмотр</a>', url)
        return ""
    view_test_result.short_description = "Результаты"


class ProjectSummaryAdmin(admin.ModelAdmin):
    inlines = [ProjectParameterInline, TestResultInline]
    list_display = ['name']
    search_fields = ['name']


admin.site.register(ProjectSummary, ProjectSummaryAdmin)


class TestResultParameterInline(admin.TabularInline):
    model = TestResultParameter
    extra = 1
    fields = ['name', 'value']


class TestResultAdmin(admin.ModelAdmin):
    inlines = [TestResultParameterInline]
    list_display = ['project', 'name', 'ip', 'end_time', 'duration']
    search_fields = ['project__name', 'name', 'ip']
    list_filter = ['project', 'end_time']


admin.site.register(TestResult, TestResultAdmin)
