
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from yookassa import Payment, Configuration

from authorization.models import Purchase, Settings, User


# Create your views here.
def app(request):

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
        in_cause_phone = phone.replace(" ", "")
        user = User.objects.filter(phone__in=(int("7" + in_cause_phone[1:]), int("8" + in_cause_phone[1:]))).first()
        if user and Purchase.objects.filter(user=user, paid=True).exists():
            return JsonResponse({"result": False})
    except:
        pass
    return JsonResponse({"result": True})


def pay_debug(request, order_id):
    try:
        order = Purchase.objects.get(pk=order_id, paid=False)

        settings = Settings.objects.first()

        Configuration.account_id = settings.yookassa_account_id
        Configuration.secret_key = settings.yookassa_secret_key

        payment = Payment.find_one(order.yookassa_order_id)
        if payment["paid"]:
            order.paid = True
            order.save()
        return redirect(f"/?login={order.user.phone}")
    except Exception as e:
        return HttpResponseRedirect("/")
