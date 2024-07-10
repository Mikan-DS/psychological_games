import json

import vk
import vk_api
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from vkapi.bot_config import *

vk_session = vk_api.VkApi(token=token)
api = vk_session.get_api()

@csrf_exempt
def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data['secret'] == secret_key:
            if data['type'] == 'confirmation':
                # confirmation_token from bot_config.py
                return HttpResponse(confirmation_token, content_type="text/plain", status=200)
            if (data['type'] == 'message_new'):# if VK server send a message
                # api = vk.API(token, v=5.5)
                user_id = str(data['object']['user_id'])

                if data['object']['body'].startswith('!войти') or data['object']['ref_source']:

                    if not User.objects.filter(username=user_id):
                        # api.messages.send(user_id=user_id, message="Пользователь не найден, создается новый.", random_id=0)
                        # User.objects.create_user(user_id, )
                        api.messages.send(
                            user_id=user_id,
                            message="Пользователь не найден, зарегистрируйтесь на сайте [ССЫЛКА НА САЙТ, КОТОРОГО НЕТ]",
                            random_id=0)

                    else:
                        pass

                # token from bot_config.py
                api.messages.send(user_id=user_id, message="Это тестовое сообщение для разработки, его не будет:\n"+str(data), random_id=0)
                return HttpResponse('ok', content_type="text/plain", status=200)
    else:
        return HttpResponse('see you :)')

