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
            user = form.save()
            username = form.cleaned_data.get('username')

            try:
                settings = Settings.objects.first()
                token = settings.vk_token
                vk_session = vk_api.VkApi(token=token)
                api = vk_session.get_api()

                user = api.users.get(user_ids=("salem_mikan"))

                if not user:
                    return HttpResponse("Пользователь ВК не найден!")
                user = user[0]
                user_id = str(user["id"])

                password = form.cleaned_data.get('password1')
                user = authenticate(username=user_id, password=password)
                # login(request, user)
                # return redirect('app')
                return redirect('https://vk.com/im?sel=-199827634&ref_source=ПолучитьКод')

            except:
                return HttpResponse("Произошла ошибка!")


    else:
        form = UserCreationForm()
    return render(request, 'authorization/register.html', {'form': form})
