from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
import vk_api

from authorization.models import Settings


# Create your views here.

def confirmation_token(request):
    return HttpResponse('see you :)')


from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                settings = Settings.objects.first()
                token = settings.vk_token
                vk_session = vk_api.VkApi(token=token)
                api = vk_session.get_api()

                username = form.cleaned_data.get('username')
                vk_user = api.users.get(user_ids=(username,))

                if not vk_user:
                    return HttpResponse("Пользователь ВК не найден!")
                vk_user = vk_user[0]
                user_id = str(vk_user["id"])

                # Проверка наличия пользователя с таким же user_id
                if User.objects.filter(username=user_id).exists():
                    return HttpResponse("Пользователь с таким VK ID уже существует!")

                # Создание нового пользователя с user_id в качестве имени пользователя
                user = form.save(commit=False)
                user.username = user_id
                user.save()

                password = form.cleaned_data.get('password1')
                user = authenticate(username=user_id, password=password)
                return redirect('https://vk.com/im?sel=-199827634&ref_source=ПолучитьКод')

            except:
                return HttpResponse("Произошла ошибка!")

    else:
        form = UserCreationForm()
    return render(request, 'authorization/register.html', {'form': form})
