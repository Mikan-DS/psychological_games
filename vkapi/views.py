import json
import string
from datetime import datetime, timedelta

import vk
import vk_api
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from authorization.models import Settings, ConfirmationCode
from authorization.utils import generate_random_code


# from vkapi.bot_config import *



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
                # confirmation_token from bot_config.py
                return HttpResponse(settings.vk_confirmation_token, content_type="text/plain", status=200)
            if (data['type'] == 'message_new'):# if VK server send a message
                # api = vk.API(token, v=5.5)
                user_id = str(data['object']['user_id'])

                if data['object']['body'].startswith('!войти') or 'ref_source' in data['object']:

                    user = User.objects.filter(username=user_id)

                    if not user:
                        # api.messages.send(user_id=user_id, message="Пользователь не найден, создается новый.", random_id=0)
                        # User.objects.create_user(user_id, )
                        api.messages.send(
                            user_id=user_id,
                            message=f"Пользователь не найден, зарегистрируйтесь на сайте {settings.host_url}",
                            random_id=0)

                    else:

                        try:
                            user = user[0]

                            expiry_duration = settings.confirmation_code_expiry if settings else timedelta(days=1)
                            expires_at = datetime.now() + expiry_duration
                            code = generate_random_code(4, string.digits)
                            confirmation_code = ConfirmationCode(user=user, code=code, expires_at=expires_at)
                            confirmation_code.save()

                            api.messages.send(
                                user_id=user_id,
                                message=f"Ваш код для входа: {confirmation_code.code}\nТак-же вы можете зайти по ссылке"
                                        f"{settings.host_url}/login/{confirmation_code.code}",
                                random_id=0)
                        except Exception as e:

                            api.messages.send(
                                user_id=user_id,
                                message=f"Ошибка! {repr(e)}",
                                random_id=0)



                # token from bot_config.py
                api.messages.send(user_id=user_id, message="Это тестовое сообщение для разработки, его не будет:\n"+str(data), random_id=0)
            return HttpResponse('ok', content_type="text/plain", status=200)
        else:
            raise Exception("Секрет неверен" + str(data['secret']) + "\n" + str(secret_key))
    else:
        return HttpResponse('see you :)')

