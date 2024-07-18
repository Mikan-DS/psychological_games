from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
def app(request, project_id=None):
    return render(request, "frontend/app.html")


def get_user(request):
    if request.user.is_authenticated:
        user = request.user
        return JsonResponse({
            "username": user.username,
            'name': user.first_name or user.username,
            'email': user.email,
            'id': user.id,
            "authenticated": True
        })
    else:
        return JsonResponse({
            "username": None,
            "authenticated": False
        })


def checknumber(request, phone):

    try:
        if User.objects.get(pk=int(phone.replace(" ", ""))):
            return JsonResponse({"result": False})
    except:
        pass
    return JsonResponse({"result": True})