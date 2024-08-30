import typing
from datetime import timedelta

from django.db import models
from django.utils.datetime_safe import datetime


class TestResult(models.Model):
    project_name = models.CharField(max_length=80)
    name = models.CharField(max_length=80)
    ip = models.CharField(max_length=80)
    end_time = models.DateTimeField(default=datetime.utcnow)
    duration = models.IntegerField()

    def __init__(self, *args, **kwargs):
        result_parameters = kwargs.pop('result_parameters', None)
        super().__init__(*args, **kwargs)
        if result_parameters:
            self.parameters: typing.Collection[TestResultParameter] = self.create_parameters(result_parameters)

    def create_parameters(self, result_parameters):
        parameters = []
        pairs = result_parameters.split(',')
        for pair in pairs:
            pair = pair.strip()
            if not pair:
                continue
            name, value = pair.split(':')
            parameter = TestResultParameter(test_result=self, name=name.strip(), value=value.strip())
            parameters.append(parameter)
        return parameters

    def __str__(self):
        return f'&lt;TestResult {self.project_name}&gt;'

    def as_dict(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'name': self.name,
            'ip': self.ip,
            'end_time': self.end_time,
            'duration': str(timedelta(seconds=self.duration)),
            'result_parameters': {
                parameter.name: parameter.value for parameter in self.parameters.all()
            }
        }

class TestResultParameter(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete=models.CASCADE, related_name='parameters')
    name = models.CharField(max_length=80)
    value = models.CharField(max_length=500)

    def __str__(self):
        return f'<TestResultParameter {self.name}>'