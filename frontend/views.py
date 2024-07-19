from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from authorization.models import Purchase


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


def pay_debug(request, order_id):
    header = "<h1>ЭТА СТРАНИЦА ЯКОБЫ ОПЛАТЫ, НАПРИМЕР enot'А</h1>"
    try:
        order = Purchase.objects.get(pk=order_id, paid=False)

        order.paid = True
        order.save()

        return HttpResponse(header + "<p>Попав на эту страницу вы автоматически \"оплатили\" заказ</p>")

    except:

        return HttpResponse(header + "<p>Этот товар уже был оплачен или его не существует</p>")
