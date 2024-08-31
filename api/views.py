import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.datetime_safe import datetime
from django.views.decorators.csrf import csrf_exempt

from api.models import TestResult, ProjectSummary, TestResultParameter, ProjectParameter


@csrf_exempt
def add_result(request):

    try:
        try:
            data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            data = request.GET or request.POST

        project = get_object_or_404(ProjectSummary, name=data.get("project_name"))

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        ts = TestResult.objects.create(
            name=data.get("name", ""),
            ip=request.META.get('REMOTE_ADDR', ""),
            duration=int(data.get("duration", 0)),
            end_time=datetime.utcnow(),
            project=project,
            user=user
        )

        test_results = {}
        test_results_list = data.get("result_parameters", "").split(",")
        for test_result in test_results_list:
            test_result = test_result.split(":", 2)
            test_results[test_result[0]] = test_result[1]

        for k, v in test_results.items():

            if v == "None":
                continue
            param = ProjectParameter.objects.filter(name=k, project=ts.project)
            if param.count() > 0:
                param = param.first()
            else:
                continue
            TestResultParameter.objects.create(
                test_result=ts,
                value=v,
                project_parameter=param
            )
        return JsonResponse({"message": "success"}, status=200)
    except Exception as e:
        return HttpResponse(f"Exception: {repr(e)}", status=500)

    #     if set(param.name for param in ts.parameters) != set(project.expected_parameters):
    #         return JsonResponse({'error': 'Invalid test results'}, status=400)
    #
    #     ts.save()
    #     return JsonResponse(ts.as_dict())
    #
    # except Exception as e:
    #     import traceback
    #     return JsonResponse({'error': 'Invalid test result'}, status=400)