import json

import vk_api
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from authorization.models import Settings, ConfirmationCode, Age, ContactWay, ConsultationParameters, Purchase, User, \
    Product
from vkapi.utils import generate_and_send_login_code

from yookassa import Configuration, Payment


def logoutView(request):
    try:
        logout(request)
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False})


@csrf_exempt
def pay_init(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            email = data.get('email')
            name = data.get('name')
            buy_type = data.get('buy_type')
            consultation_parameters = data.get('consultation_parameters', None)

            if not phone or not name or not buy_type:
                return JsonResponse({'error': 'Phone, buy_type and name are required'}, status=400)

            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'username': "without_vk_" + phone,
                    'email': email,
                    "password": User.objects.make_random_password(
                        20,
                        "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789@#&%$"
                    ),
                    'first_name': name
                }
            )

            if Purchase.objects.filter(user=user, paid=True).exists():
                return JsonResponse({'error': "Уже куплено"}, status=500)

            product = Product.objects.get(article=buy_type)

            purchase = Purchase.objects.create(
                product=product,
                user=user,
                cost=1,#3750 if buy_type == 'game' else 7900,
                paid=False
            )

            if buy_type == "game_consultation" and consultation_parameters:
                age = Age.objects.get(value=consultation_parameters['age'])
                contact_way = ContactWay.objects.get(method=consultation_parameters['contact_way'])
                ConsultationParameters.objects.create(
                    question=consultation_parameters['custom_question'],
                    age=age,
                    gender=consultation_parameters['gender'],
                    contact_way=contact_way,
                    purchase=purchase
                )

            settings = Settings.objects.first()

            Configuration.account_id = settings.yookassa_account_id
            Configuration.secret_key = settings.yookassa_secret_key

            # YOOKASSA
            payment = Payment.create({
                "amount": {
                    "value": f"{purchase.cost}.00",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"{settings.pay_url}pay/{purchase.id}"
                },
                "capture": True,
                "description": "Игра" if buy_type == 'game' else "Игра и консультация",
                "metadata": {
                    "order_id": str(purchase.id)
                }
            })

            purchase.yookassa_order_id = payment["id"]
            purchase.save()

            return JsonResponse(
                {'message': 'Purchase created successfully', "url": payment["confirmation"]["confirmation_url"]}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def login_init(request, phone):
    phone = phone.replace(" ", "")
    try:
        user = User.objects.get(phone=phone)

        login(request, user)
        return JsonResponse({
            "result": "auto"
        })

        settings = Settings.objects.first()

        if not Purchase.objects.filter(user=user, paid=True).exists():
            orders = Purchase.objects.filter(user=user, paid=False)

            for order in orders:
                payment = Payment.find_one(order.yookassa_order_id)
                if payment["paid"]:
                    order.paid = True
                    order.save()

        if "without_vk" in user.username:
            return JsonResponse({
                'result': True,
                "message": "Получите временный код для входа и следуйте инструкциям в",
                "bot_url": settings.vk_chat_url})

        try:

            token = settings.vk_token
            vk_session = vk_api.VkApi(token=token)
            api = vk_session.get_api()

            generate_and_send_login_code(api, user)
        except Exception as e:
            print(e)

        return JsonResponse({'result': True,
                             'message': "Получите временный код для входа в",
                             "bot_url": settings.vk_chat_url})

    except Exception as e:
        pass
    return JsonResponse({'result': False, "message": "Неверный логин"})


def login_code(request, phone, code):
    try:
        user = User.objects.get(phone=phone)

        confirmation_code = ConfirmationCode.objects.get(code=code, user=user, is_used=False)

        assert confirmation_code.is_active

        confirmation_code.is_used = True
        confirmation_code.delete()

        login(request, user)

        return redirect("/")

    except Exception as e:

        return redirect(f"/?login={phone}&code={code}")
