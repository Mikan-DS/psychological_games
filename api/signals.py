import string

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import TestResult, ProjectSummary, ProjectParameter


@receiver(post_migrate)
def update_old_variant(sender, **kwargs):

    for result in TestResult.objects.all():
        if not result.project and result.project_name:
            project, create = ProjectSummary.objects.get_or_create(name=result.project_name)
            result.project = project
            result.project_name = None
            result.save()

        if result.project:
            for parameter in result.parameters:
                if not parameter.project_parameter and parameter.name:
                    project_parameter, create = ProjectParameter.objects.get_or_create(
                        name=parameter,
                        project=result.project)
                    parameter.project_parameter = project_parameter
                    parameter.name = None

