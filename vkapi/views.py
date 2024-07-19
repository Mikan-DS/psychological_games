import json
import string
from datetime import datetime, timedelta

import vk_api
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from authorization.models import Settings, ConfirmationCode
from authorization.utils import generate_random_code
from vkapi.utils import generate_and_send_login_code


@csrf_exempt
def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        settings = Settings.objects.first()

        secret_key = settings.vk_secret_key

        if data['secret'] == secret_key:

            token = settings.vk_token
            vk_session = vk_api.VkApi(token=token)
            api = vk_session.get_api()

            if data['type'] == 'confirmation':
                return HttpResponse(settings.vk_confirmation_token, content_type="text/plain", status=200)
            if data['type'] == 'message_new':
                user_id = str(data['object']['user_id'])

                if data['object']['body'].startswith('!войти') or 'ref_source' in data['object']:

                    user = User.objects.filter(id=user_id)

                    if not user:
                        api.messages.send(
                            user_id=user_id,
                            message=f"Пользователь не найден, зарегистрируйтесь на сайте {settings.host_url}",
                            random_id=0)

                    else:
                        user = user.first()

                        try:
                            generate_and_send_login_code(api, user)
                        except Exception as e:

                            if settings.send_debug_messages:
                                api.messages.send(
                                    user_id=user_id,
                                    message=f"Ошибка! {repr(e)}",
                                    random_id=0)
                            else:
                                api.messages.send(
                                    user_id=user_id,
                                    message=f"Произошла ошибка!",
                                    random_id=0)
                else:
                    api.messages.send(
                        user_id=user_id,
                        message=f"Доступные комманды:\n!войти - получить код для входа",
                        random_id=0)

                if settings.send_debug_messages:
                    api.messages.send(
                        user_id=user_id,
                        message="Это тестовое сообщение для разработки, его не будет:\n\n" + str(data),
                        random_id=0)

            return HttpResponse('ok', content_type="text/plain", status=200)
        else:
            if settings.send_debug_messages:
                raise Exception("Секрет неверен" + str(data['secret']) + "\n" + str(secret_key))
            else:
                raise Exception("Секрет неверен")
    else:
        return HttpResponse('Вам тут не место!')

