import json

import vk_api
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from authorization.models import Settings
from vkapi.utils import generate_and_send_login_code, write_message


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
                by_ref_source = False
                user = None
                if 'ref_source' in data['object']:
                    user = User.objects.filter(id=data['object']["ref_source"])
                    if user:
                        by_ref_source = True
                        user = user.first()

                in_cause_phone = (data['object']['body']
                                  .replace('+', '')
                                  .replace("(", "")
                                  .replace(")", "")
                                  .replace(" ", "")
                                  .replace("-", "")
                                  )

                if data['object']['body'].startswith('+') and in_cause_phone.isdigit():
                    user = User.objects.filter(id=in_cause_phone)
                    if user:
                        user = user.first()

                        if user and "without_vk" in user.username:
                            by_ref_source = True
                        else:
                            write_message(
                                api,
                                user_id,
                                f"Номер телефона уже привязан к другому аккаунту. "
                                f"Если вы действительно оплачивали игру и указывали этот "
                                f"номер телефона при регистрации - обратитесь в поддержку."
                            )


                if by_ref_source and "without_vk" in user.username:
                    user.username = user_id
                    user.save()
                    write_message(
                        api,
                        user_id,
                        f"Вы привязали этот вк к своему аккаунту на сайте {settings.host_url}!"
                    )

                if data['object']['body'].startswith('!войти') and not user:
                    write_message(
                        api,
                        user_id,
                        f"Ваш профиль вк не привязан к сайту {settings.host_url}, отправьте свой номер который вы указывали при регистрации в формате +8-ххх-ххх-хх-хх для продолжения."
                    )
                elif data['object']['body'].startswith('!войти') or by_ref_source:

                    user = User.objects.filter(id=user_id)

                    if not user:
                        write_message(
                            api,
                            user_id,
                            f"Пользователь не найден, зарегистрируйтесь на сайте {settings.host_url}"
                        )

                    else:
                        user = user.first()

                        try:
                            generate_and_send_login_code(api, user)
                        except Exception as e:

                            if settings.send_debug_messages:
                                write_message(
                                    api,
                                    user_id,
                                    f"Ошибка! {repr(e)}"
                                )
                            else:
                                write_message(
                                    api,
                                    user_id,
                                    f"Произошла ошибка!"
                                )
                else:
                    write_message(
                        api,
                        user_id,
                        f"Доступные комманды:\n!войти - получить код для входа"
                    )

                if settings.send_debug_messages:
                    write_message(
                        api,
                        user_id,
                        "Это тестовое сообщение для разработки, его не будет:\n\n" + str(data)
                    )

            return HttpResponse('ok', content_type="text/plain", status=200)
        else:
            if settings.send_debug_messages:
                raise Exception("Секрет неверен" + str(data['secret']) + "\n" + str(secret_key))
            else:
                raise Exception("Секрет неверен")
    else:
        return HttpResponse('Вам тут не место!')
