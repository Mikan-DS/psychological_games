import csv

from django.contrib import admin
from django.forms import inlineformset_factory
from django.http import HttpResponse
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


def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test_results.csv"'

    writer = csv.writer(response)
    writer.writerow(['Project', 'Name', 'IP', 'End Time', 'Duration'] +
                    [param.name for param in ProjectParameter.objects.all()])

    for obj in queryset:
        row = [obj.project, obj.name, obj.ip, obj.end_time, obj.duration]
        parameters = {param.name: param.value for param in obj.parameters.all()}
        for param in ProjectParameter.objects.all():
            row.append(parameters.get(param.name, ''))
        writer.writerow(row)

    return response


export_to_csv.short_description = "Экспорт в CSV"

class TestResultParameterInline(admin.TabularInline):
    model = TestResultParameter
    extra = 1
    fields = ['name', 'value']


class TestResultAdmin(admin.ModelAdmin):
    inlines = [TestResultParameterInline]
    list_display = ['project', 'name', 'ip', 'end_time', 'duration']
    search_fields = ['project__name', 'name', 'ip']
    list_filter = ['project', 'end_time']

    actions = [export_to_csv]


admin.site.register(TestResult, TestResultAdmin)
