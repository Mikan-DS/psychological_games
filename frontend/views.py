from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from yookassa import Payment

from authorization.models import Purchase, Settings


# Create your views here.
def app(request, project_id=None):

    settings = Settings.objects.first()

    return render(request, "frontend/app.html", context={"enot": settings.enot_code, "enot_code": settings.enot_code})


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
        user = User.objects.get(pk=int(phone.replace(" ", "")))
        if user and Purchase.objects.filter(user=user, paid=True).exists():
            return JsonResponse({"result": False})
    except:
        pass
    return JsonResponse({"result": True})


def pay_debug(request, order_id):
    try:
        order = Purchase.objects.get(pk=order_id, paid=False)

        payment = Payment.find_one(order.yookassa_order_id)
        if payment["paid"]:
            order.paid = True
            order.save()
        return HttpResponseRedirect("app")
    except Exception as e:
        return HttpResponseRedirect("app")
