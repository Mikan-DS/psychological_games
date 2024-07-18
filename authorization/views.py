import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import vk_api
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt

from authorization.models import Settings, ConfirmationCode, Age, ContactWay, ConsultationParameters, Purchase


#
# def login_view(request):
#     if request.method == 'POST':
#         code_input = request.POST.get('code')
#         try:
#             confirmation_code = ConfirmationCode.objects.get(code=code_input, is_used=False)
#             if confirmation_code.is_active:
#                 confirmation_code.is_used = True
#                 confirmation_code.save()
#                 login(request, confirmation_code.user)
#                 return redirect('app')  # Redirect to your app's main view
#             else:
#                 return render(request, 'authorization/login.html', {'error': 'Код неверен или истёк.'})
#         except ConfirmationCode.DoesNotExist:
#             return render(request, 'authorization/login.html', {'error': 'Код неверен или истёк.'})
#     return render(request, 'authorization/login.html')
#
# def login_with_code(request, user_id, code):
#     try:
#         user = User.objects.get(username=user_id)
#         confirmation_code = ConfirmationCode.objects.get(code=code, user=user, is_used=False)
#         if confirmation_code.is_active:
#             confirmation_code.is_used = True
#             confirmation_code.save()
#             login(request, confirmation_code.user)
#             return redirect('app')  # Redirect to your app's main view
#         else:
#             return render(request, 'authorization/login.html', {'error': 'Код неверен или истёк.', "user": user.first_name or "Имени нет"})
#     except ConfirmationCode.DoesNotExist:
#         return render(request, 'authorization/login.html', {'error': 'Код неверен или истёк.', "user": "Unknown"})
#
#
#
# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             try:
#                 settings = Settings.objects.first()
#                 token = settings.vk_token
#                 vk_session = vk_api.VkApi(token=token)
#                 api = vk_session.get_api()
#
#                 username = form.cleaned_data.get('username')
#                 vk_user = api.users.get(user_ids=(username,))
#
#                 if not vk_user:
#                     return HttpResponse("Пользователь ВК не найден!")
#                 vk_user = vk_user[0]
#                 user_id = str(vk_user["id"])
#
#                 # Проверка наличия пользователя с таким же user_id
#                 if User.objects.filter(username=user_id).exists():
#                     return HttpResponse("Пользователь с таким VK ID уже существует!")
#
#                 # Создание нового пользователя с user_id в качестве имени пользователя
#                 user = form.save(commit=False)
#                 user.username = user_id
#                 user.save()
#
#                 password = form.cleaned_data.get('password1')
#                 user = authenticate(username=user_id, password=password)
#                 return redirect('https://vk.com/im?sel=-199827634&ref_source=ПолучитьКод')
#
#             except:
#                 return HttpResponse("Произошла ошибка!")
#
#     else:
#         form = UserCreationForm()
#     return render(request, 'authorization/register.html', {'form': form})
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
            buy_type = data.get('buy_type')
            consultation_parameters = data.get('consultation_parameters', None)
            cost = data.get('cost', 0.0)

            if not phone or not email:
                return JsonResponse({'error': 'Phone and email are required'}, status=400)

            user, created = User.objects.get_or_create(
                id=phone,
                defaults={
                    'username': "without_vk_" + phone,
                    'email': email,
                    "password": User.objects.make_random_password(
                        20,
                        "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789@#&%$"
                    )
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
                age = Age.objects.get(id=consultation_parameters['age_id'])
                contact_way = ContactWay.objects.get(id=consultation_parameters['contact_way_id'])
                ConsultationParameters.objects.create(
                    question=consultation_parameters['custom_question'],
                    age=age,
                    gender=consultation_parameters['gender'],
                    contact_way=contact_way,
                    purchase=purchase
                )

            return JsonResponse({'message': 'Purchase created successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

